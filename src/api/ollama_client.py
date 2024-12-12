import ollama
from ..models.schemas import ArticleSummary
import logging

class OllamaClient:
    def __init__(self, model: str):
        self.model = model

    def summarize_article(self, article_text: str) -> ArticleSummary:
        try:
            response = ollama.chat(
                model=self.model,
                messages=[{'role': 'user', 'content': article_text}],
                format=ArticleSummary.model_json_schema()
            )
            return ArticleSummary.parse_raw(response.message.content)
        except Exception as e:
            logging.error(f"Ollama error: {str(e)}")
            raise