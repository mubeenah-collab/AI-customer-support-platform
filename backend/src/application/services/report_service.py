import logging
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.ai.llm.gemini_llm import GeminiLLMService
from backend.src.ai.rag.rag_pipeline import RAGPipeline
from backend.src.domain.entities.report import Report
from backend.src.domain.exceptions.document_exceptions import DocumentNotFoundError
from backend.src.domain.exceptions.report_exceptions import ReportGenerationError, ReportNotFoundError
from backend.src.infrastructure.repositories.document_repository import SQLAlchemyDocumentRepository
from backend.src.infrastructure.repositories.message_repository import SQLAlchemyMessageRepository
from backend.src.infrastructure.repositories.report_repository import SQLAlchemyReportRepository
from backend.src.presentation.schemas.ai_schemas import SummaryResponseSchema
from backend.src.presentation.schemas.report_schemas import DocumentSummaryResponse

logger = logging.getLogger("report_service")


class ReportService:
    """Application service for generating document summaries and customer support analytics reports."""

    def __init__(
        self,
        session: AsyncSession,
        llm_service: GeminiLLMService,
        rag_pipeline: RAGPipeline,
    ):
        self.session = session
        self.report_repo = SQLAlchemyReportRepository(session)
        self.doc_repo = SQLAlchemyDocumentRepository(session)
        self.msg_repo = SQLAlchemyMessageRepository(session)
        self.llm_service = llm_service
        self.rag_pipeline = rag_pipeline

    async def generate_document_summary(
        self,
        user_id: str,
        document_id: str,
    ) -> DocumentSummaryResponse:
        """Generate structured summary of a processed document using Gemini LLM."""
        doc = await self.doc_repo.get_by_id(document_id)
        if not doc or doc.user_id != user_id:
            raise DocumentNotFoundError(document_id)

        # Retrieve knowledge chunks for document via RAG filter
        rag_res = self.rag_pipeline.run_retrieval(
            query=f"Overview summary of {doc.filename}",
            top_k=5,
            filter_metadata={"document_id": document_id},
        )

        doc_text = rag_res.context if rag_res.has_sufficient_context else f"Document Filename: {doc.filename}"

        try:
            summary_schema: SummaryResponseSchema = self.llm_service.summarize_text(doc_text)
            return DocumentSummaryResponse(
                document_id=doc.id,
                document_name=doc.filename,
                summary=summary_schema.summary,
                key_points=summary_schema.key_points or [],
                title=summary_schema.title or f"Summary: {doc.filename}",
            )
        except Exception as e:
            logger.error(f"ReportService document summary generation failure: {str(e)}")
            raise ReportGenerationError(f"Failed to generate document summary: {str(e)}") from e

    async def generate_support_report(
        self,
        user_id: str,
        topic: str,
        conversation_id: Optional[str] = None,
    ) -> Report:
        """Generate and save structured customer support report in DB."""
        if not topic or not topic.strip():
            raise ReportGenerationError("Report topic cannot be empty.")

        # 1. Retrieve knowledge base context for report topic
        rag_res = self.rag_pipeline.run_retrieval(query=topic.strip(), top_k=5)
        context_str = rag_res.context

        # 2. Retrieve conversation history context if conversation_id provided
        history_str = "None"
        if conversation_id:
            messages = await self.msg_repo.get_by_conversation_id(conversation_id)
            history_str = "\n".join([f"{m.sender_type}: {m.content}" for m in messages[-6:]])

        # 3. Generate report content via Gemini LLM
        try:
            report_text = self.llm_service.generate_report(
                topic=topic.strip(),
                context=context_str,
                chat_history=history_str,
            )
        except Exception as e:
            logger.error(f"ReportService report generation failure: {str(e)}")
            raise ReportGenerationError(f"Failed to generate report: {str(e)}") from e

        # 4. Save Report Entity in DB
        report_entity = Report(
            user_id=user_id,
            title=f"Support Report: {topic[:40]}",
            report_type="support_analytics",
            content=report_text,
        )
        return await self.report_repo.create(report_entity)

    async def list_user_reports(self, user_id: str) -> List[Report]:
        return await self.report_repo.get_by_user_id(user_id)

    async def get_report_by_id(self, user_id: str, report_id: str) -> Report:
        report = await self.report_repo.get_by_id(report_id)
        if not report or report.user_id != user_id:
            raise ReportNotFoundError(report_id)
        return report

    async def export_report_pdf(self, user_id: str, report_id: str) -> bytes:
        """Generate PDF binary stream export for executive support analytics report."""
        from backend.src.application.services.pdf_generator import SimplePDFGenerator

        report = await self.get_report_by_id(user_id, report_id)
        return SimplePDFGenerator.generate_pdf(
            title=report.title,
            content=report.content,
        )
