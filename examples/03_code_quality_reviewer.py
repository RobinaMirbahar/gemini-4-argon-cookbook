"""Example 03: Autonomous Code Quality & Architecture Reviewer with Gemini 4 Argon."""
from google import genai
from pydantic import BaseModel, Field

class RefactorSuggestion(BaseModel):
    line_number: int = Field(description="Line number where readability or performance can be improved")
    category: str = Field(description="Category such as readability, type-annotations, or algorithmic-complexity")
    explanation: str = Field(description="Clear explanation of the maintainability improvement")
    refactored_snippet: str = Field(description="Clean, idiomatic Python replacement code")

class CodeQualityReport(BaseModel):
    summary: str
    maintainability_score: int
    suggestions: list[RefactorSuggestion]

def review_python_module(source_code: str) -> CodeQualityReport:
    client = genai.Client()
    interaction = client.interactions.create(
        model="gemini-4-argon",
        input=f"Review the following Python module for PEP 8 readability, type annotations, and algorithmic efficiency:\n\n```python\n{source_code}\n```",
        generation_config={
            "thinking_level": "high",
            "response_mime_type": "application/json",
            "response_schema": CodeQualityReport,
        },
    )
    return CodeQualityReport.model_validate_json(interaction.output_text)

if __name__ == "__main__":
    print("Ready to review Python modules for maintainability and performance with Gemini 4 Argon.")
