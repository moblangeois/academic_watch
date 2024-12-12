from pydantic import BaseModel, Field
from typing import List, Optional

class Article(BaseModel):
    title: str
    authors: List[str]
    abstract: str
    doi: Optional[str]
    publication_date: str
    source: str

class ArticleSummary(BaseModel):
    title: str
    authors: List[str]
    doi: str
    key_points: List[str]
    relevance_score: int
    methodology: Optional[str] = None
    theoretical_framework: Optional[str] = None

class DailyDigest(BaseModel):
    date: str
    summaries: List[ArticleSummary]
    total_articles: int

class LitteratureReview(BaseModel):
    review: str