# src/api/openai_client.py

from openai import OpenAI
from ..models.schemas import ArticleSummary, Article
import logging

class OpenAIClient:
    def __init__(self, api_key: str, model: str):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def _format_article_text(self, article: Article) -> str:
        """Convertit un article en texte formaté pour l'analyse."""
        return f"""
Title: {article.title}
Authors: {', '.join(article.authors)}
Source: {article.source}
Publication Date: {article.publication_date}
DOI: {article.doi if article.doi else 'N/A'}
Abstract: {article.abstract if article.abstract else 'N/A'}
"""

    def summarize_article(self, article: Article) -> ArticleSummary:
        try:
            completion = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are an academic research assistant. Analyze the following article and provide:
                        1. Key points (maximum 5 bullet points)
                        2. Relevance score (1-10)
                        3. Methodology used (if applicable)
                        4. Theoretical framework (if applicable)
                        
                        Format your response as a structured JSON matching the specified schema."""
                    },
                    {
                        "role": "user",
                        "content": self._format_article_text(article)
                    }
                ],
                response_format=ArticleSummary,
            )
            # Parse la réponse JSON en ArticleSummary
            return ArticleSummary.parse_raw(completion.choices[0].message.content)
            
        except Exception as e:
            logging.error(f"OpenAI API error: {str(e)}")
            raise