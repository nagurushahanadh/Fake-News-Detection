
from __future__ import annotations

from datetime import datetime
from typing import Iterable, Optional, Tuple

from sqlalchemy.orm import Session

from . import models
from .config import settings
from .utils import hash_password, verify_password


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, name: str, email: str, password: str, role: str = "user") -> models.User:
    user = models.User(
        name=name,
        email=email,
        password_hash=hash_password(password),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> Optional[models.User]:
    user = get_user_by_email(db, email=email)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def upsert_system_metrics(db: Session) -> models.SystemMetric:
    metric = db.query(models.SystemMetric).first()
    if not metric:
        metric = models.SystemMetric()
        db.add(metric)
        db.commit()
        db.refresh(metric)
    return metric


def increment_metrics(
    db: Session,
    fake: bool,
    real: bool,
    active_users: Optional[int] = None,
    uptime_seconds: Optional[float] = None,
) -> models.SystemMetric:
    metric = upsert_system_metrics(db)
    metric.articles_analyzed += 1
    if fake:
        metric.fake_news_detected += 1
    if real:
        metric.real_news_detected += 1

    # Compute accuracy as percent of correct labels if ground truth is provided.
    # For this demo, we treat all predictions as "correct" since we do not have ground truth.
    # Users can update this value manually in the database or extend the model to store labels.
    total = metric.fake_news_detected + metric.real_news_detected
    if total > 0:
        metric.model_accuracy = 100.0 * (total - metric.fake_news_detected) / total

    if active_users is not None:
        metric.active_users = active_users
    if uptime_seconds is not None:
        metric.system_uptime = uptime_seconds

    metric.last_updated = datetime.utcnow()
    db.add(metric)
    db.commit()
    db.refresh(metric)
    return metric


def get_trusted_sources(db: Session, only_active: bool = True) -> list[models.TrustedSource]:
    query = db.query(models.TrustedSource)
    if only_active:
        query = query.filter(models.TrustedSource.status == "Active")
    return query.order_by(models.TrustedSource.source_name).all()


def add_trusted_source(
    db: Session,
    source_name: str,
    website_url: str,
    added_by: Optional[int] = None,
    status: str = "Active",
) -> models.TrustedSource:
    source = models.TrustedSource(
        source_name=source_name,
        website_url=website_url,
        status=status,
        added_by=added_by,
    )
    db.add(source)
    db.commit()
    db.refresh(source)
    return source


def deactivate_trusted_source(db: Session, source_id: int) -> Optional[models.TrustedSource]:
    source = db.query(models.TrustedSource).filter(models.TrustedSource.source_id == source_id).first()
    if not source:
        return None
    source.status = "Inactive"
    db.add(source)
    db.commit()
    db.refresh(source)
    return source


def create_article_with_prediction(
    db: Session,
    title: str,
    content: str,
    url: Optional[str],
    submitted_by: Optional[int],
    prediction_result: str,
    confidence_score: float,
    explanation: str,
    suspicious_phrases: list[str],
) -> Tuple[models.NewsArticle, models.Prediction]:
    article = models.NewsArticle(
        title=title,
        content=content,
        url=url,
        submitted_by=submitted_by,
    )
    db.add(article)
    db.commit()
    db.refresh(article)

    explanation_full = explanation
    if suspicious_phrases:
        explanation_full += "\nSuspicious phrases: " + ", ".join(suspicious_phrases)

    prediction = models.Prediction(
        article_id=article.article_id,
        prediction_result=prediction_result,
        confidence_score=float(confidence_score),
        explanation=explanation_full,
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)

    return article, prediction


def list_articles(db: Session, limit: int = 50) -> list[models.NewsArticle]:
    return db.query(models.NewsArticle).order_by(models.NewsArticle.submission_date.desc()).limit(limit).all()
