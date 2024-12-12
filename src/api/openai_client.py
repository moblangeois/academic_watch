# src/api/openai_client.py

from openai import OpenAI
from ..models.schemas import ArticleSummary, Article, LitteratureReview
import logging
import os

class OpenAIClient:
    def __init__(self, api_key: str, model: str):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def _format_article_text(self, article: Article) -> str:
        """Convertit un article en texte formaté pour l'analyse."""
        return f"""
Title: {article.title}
DOI: {article.doi if article.doi else 'N/A'}
Authors: {', '.join(article.authors)}
Source: {article.source}
Publication Date: {article.publication_date}
DOI: {article.doi if article.doi else 'N/A'}
Abstract: {article.abstract if article.abstract else 'N/A'}
"""

    def summarize_article(self, article: Article, ThesisSubject) -> ArticleSummary:
        try:
            completion = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": f"""Vous êtes un assistant de recherche académique. Analysez l'article suivant et fournissez en langue française :
                        1. Points clés (maximum 5 points)
                        2. Score de pertinence (1-10) au regard du sujet de thèse de l'utilisateur
                        3. Méthodologie utilisée (le cas échéant)
                        4. Cadre théorique (le cas échéant)
                        
                        Sujet de thèse : {ThesisSubject}

                        Rédigez une histoire originale en français pour l'utilisateur, puis fournissez une analyse détaillée en français pour chaque article. Veuillez inclure tous les articles dans votre réponse.
                        
                        Formatez votre réponse comme un JSON structuré correspondant au schéma spécifié."""
                    },
                    {
                        "role": "user",
                        "content": self._format_article_text(article)
                    }
                ],
                response_format=ArticleSummary,
                temperature=0
            )
            # Parse la réponse JSON en ArticleSummary
            return ArticleSummary.parse_raw(completion.choices[0].message.content)
            
        except Exception as e:
            logging.error(f"OpenAI API error: {str(e)}")
            raise

    def generate_literature_review(self, articles_text: str) -> str:
        try:
            completion = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """Vous êtes un assistant de recherche académique. Analysez les articles suivants et fournissez une revue de la littérature en langue française :
                        1. Synthèse des points clés
                        2. Importance et pertinence des études
                        3. Méthodologies utilisées
                        4. Cadres théoriques abordés
                        
                        Formatez votre réponse comme un texte narratif structuré et bien formatté en citant en format APA7.
                        Citez en inline URL les auteurs et l'année de publication pour chaque article. Exemple : [(Doe et al., 2021)](DOI pour l'article (doi.org/(doi))).
                        """
                    },
                    {
                        "role": "user",
                        "content": articles_text
                    }
                ],
                response_format=LitteratureReview,
                temperature=0
            )
            return completion.choices[0].message.content
            
        except Exception as e:
            logging.error(f"OpenAI API error: {str(e)}")
            raise