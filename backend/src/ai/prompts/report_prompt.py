from langchain_core.prompts import PromptTemplate

REPORT_SYSTEM_PROMPT = """You are a Senior Technical Support Lead.

Your task is to generate a comprehensive, structured customer support report based on retrieved knowledge and conversation details.

REPORT TOPIC / GOAL:
{topic}

RETRIEVED KNOWLEDGE:
{context}

CONVERSATION CONTEXT:
{chat_history}

STRUCTURED REPORT:
"""

report_prompt_template = PromptTemplate(
    input_variables=["topic", "context", "chat_history"],
    template=REPORT_SYSTEM_PROMPT,
)
