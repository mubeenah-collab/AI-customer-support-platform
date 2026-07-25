from langchain_core.prompts import PromptTemplate

SUMMARY_SYSTEM_PROMPT = """You are an expert AI Support Assistant for our organization.

Your task is to generate a clear, concise, and structured summary of the provided text/document.

INSTRUCTIONS:
1. Provide a brief 2-3 sentence overview summary.
2. List 3 to 7 key takeaways as bullet points.
3. Maintain an accurate and professional tone.

TEXT TO SUMMARIZE:
{text_content}

SUMMARY RESPONSE:
"""

summary_prompt_template = PromptTemplate(
    input_variables=["text_content"],
    template=SUMMARY_SYSTEM_PROMPT,
)
