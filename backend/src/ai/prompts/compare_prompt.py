from langchain_core.prompts import PromptTemplate

COMPARE_SYSTEM_PROMPT = """You are an expert AI Support Engineer.

Your task is to compare two documents/knowledge items and generate a structured comparison highlighting key similarities, differences, and recommendations.

DOCUMENT A:
{doc_a}

DOCUMENT B:
{doc_b}

COMPARISON ANALYSIS:
"""

compare_prompt_template = PromptTemplate(
    input_variables=["doc_a", "doc_b"],
    template=COMPARE_SYSTEM_PROMPT,
)
