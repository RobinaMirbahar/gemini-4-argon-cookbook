"""Example 03: Automated Code Quality & Maintainability Reviewer with Gemini 2.5 Pro."""
from google import genai
from google.genai import types
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
    response = client.models.generate_content(
        model="gemini-2.5-pro",
        contents=f"Review the following Python module for PEP 8 readability, type annotations, and algorithmic efficiency:\n\n```python\n{source_code}\n```",
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=CodeQualityReport,
            temperature=0.1,
        ),
    )
    return CodeQualityReport.model_validate_json(response.text)

if __name__ == "__main__":
    sample = "def calc(items):\n    res = []\n    for i in range(len(items)):\n        if items[i] > 0:\n            res.append(items[i] * 2)\n    return res\n"
    print("Ready to review Python modules for maintainability and performance with Gemini 2.5 Pro.")
