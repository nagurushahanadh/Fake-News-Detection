from __future__ import annotations
import time
from datetime import datetime
from typing import Optional

import streamlit as st

from fake_news import crud, database, ml
from fake_news.config import settings


def init_app() -> None:
    """Initialize the database and system metrics."""
    database.init_db()
    with database.SessionLocal() as db:
        crud.upsert_system_metrics(db)


def get_trusted_domains(db) -> list[str]:
    sources = crud.get_trusted_sources(db, only_active=True)
    domains = []
    for s in sources:
        # Basic extraction of domain from URL
        if s.website_url:
            url = s.website_url.strip()
            if url.startswith("http"):
                # remove schema
                try:
                    domain = url.split("//", 1)[1].split("/")[0]
                except Exception:
                    domain = url
            else:
                domain = url.split("/")[0]
            domains.append(domain)
    return domains


def show_analysis() -> None:
    st.title("📰 Fake News Detection & Verification")
    st.write(
        "Paste the full article text below to analyze whether it is likely Real or Fake."  # noqa: E501
    )

    with st.form("analysis_form"):
        content = st.text_area("Full article text", height=260)
        submitted = st.form_submit_button("Analyze")

    if submitted:
        if not content:
            st.warning("Please enter the article text to analyze.")
            return

        with database.SessionLocal() as db:
            trusted_domains = get_trusted_domains(db)
            result = ml.classify_article(
                title="",
                content=content,
                url=None,
                trusted_domains=trusted_domains,
            )

        # Persist results anonymously
        crud.create_article_with_prediction(
            db=db,
            title="(Content only)",
            content=content or "",
            url=None,
            submitted_by=None,
            prediction_result=result.prediction,
            confidence_score=result.confidence * 100.0,
            explanation=result.explanation,
            suspicious_phrases=result.suspicious_phrases,
        )

        st.markdown("---")
        st.subheader("Prediction")
        st.write(f"**{result.prediction}**")
        st.write(f"Confidence Score: **{result.confidence*100:.1f}%**")

        st.subheader("Explanation")
        st.write(result.explanation)

        if result.suspicious_phrases:
            st.subheader("Suspicious claims detected")
            for phrase in result.suspicious_phrases:
                st.write(f"- {phrase}")

        if result.top_features:
            st.subheader("Top contributing terms")
            for term, score in result.top_features:
                st.write(f"- {term}: {score:.3f}")

        st.success("Analysis complete! The result has been stored in the system.")




def main() -> None:
    st.set_page_config(page_title="Fake News Detector", layout="wide")

    if "start_time" not in st.session_state:
        st.session_state["start_time"] = time.time()

    init_app()

    show_analysis()


if __name__ == "__main__":
    main()
