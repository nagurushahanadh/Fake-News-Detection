
from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Text,
    ForeignKey,
    Float,
    Boolean,
)
from sqlalchemy.orm import relationship

from .database import Base


# NOTE: User model is kept for historical purposes but is not used in the current UI.
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    email = Column(String(256), unique=True, nullable=False, index=True)
    password_hash = Column(String(256), nullable=False)
    role = Column(String(32), nullable=False, default="user")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    submissions = relationship("NewsArticle", back_populates="submitted_by_user")
    sources_added = relationship("TrustedSource", back_populates="added_by_user")


class NewsArticle(Base):
    __tablename__ = "news_articles"

    article_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(1024), nullable=False)
    content = Column(Text, nullable=False)
    url = Column(String(1024), nullable=True)
    submitted_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    submission_date = Column(DateTime, default=datetime.utcnow, nullable=False)

    submitted_by_user = relationship("User", back_populates="submissions")
    prediction = relationship("Prediction", back_populates="article", uselist=False)


class Prediction(Base):
    __tablename__ = "predictions"

    prediction_id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("news_articles.article_id"), nullable=False)
    prediction_result = Column(String(32), nullable=False)
    confidence_score = Column(Float, nullable=False)
    explanation = Column(Text, nullable=True)
    analyzed_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    article = relationship("NewsArticle", back_populates="prediction")


class TrustedSource(Base):
    __tablename__ = "trusted_sources"

    source_id = Column(Integer, primary_key=True, index=True)
    source_name = Column(String(256), nullable=False)
    website_url = Column(String(1024), nullable=False)
    status = Column(String(32), default="Active", nullable=False)
    added_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    added_date = Column(DateTime, default=datetime.utcnow, nullable=False)

    added_by_user = relationship("User", back_populates="sources_added")


class SystemMetric(Base):
    __tablename__ = "system_metrics"

    metric_id = Column(Integer, primary_key=True, index=True)
    articles_analyzed = Column(Integer, default=0, nullable=False)
    fake_news_detected = Column(Integer, default=0, nullable=False)
    real_news_detected = Column(Integer, default=0, nullable=False)
    model_accuracy = Column(Float, default=0.0, nullable=False)
    active_users = Column(Integer, default=0, nullable=False)
    system_uptime = Column(Float, default=0.0, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow, nullable=False)
