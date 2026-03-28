import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import re
from datetime import datetime

from database.db import save_result, fetch_results, fetch_recent_results, is_database_connected
from utils.predictor import predict_news
from utils.verifier import verify_news
from utils.explain import explain_news
from utils.preprocess import highlight_suspicious_words

st.set_page_config(
    page_title="🔍 Fake News Detection & Verification",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
/* Main Background - Dark Gradient */
.stApp {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    color: #ffffff;
}

/* Remove default top padding */
.st-emotion-cache-1y4p8pa {
    padding-top: 0;
}

/* Header Styling */
.header-title {
    text-align: center;
    background: linear-gradient(90deg, #00d4ff, #7b2ff7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-size: 3em;
    font-weight: 900;
    margin-bottom: 10px;
    letter-spacing: 1.5px;
}

.header-subtitle {
    text-align: center;
    color: #b0bec5;
    font-size: 1.2em;
    margin-bottom: 30px;
    font-weight: 300;
}

/* Glassmorphism Cards */
.card-container {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    padding: 24px;
    border-radius: 16px;
    margin: 15px 0;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    transition: all 0.3s ease;
}

.card-container:hover {
    background: rgba(255, 255, 255, 0.08);
    border-color: rgba(255, 255, 255, 0.2);
    transform: translateY(-2px);
}

/* Result Cards */
.result-fake {
    background: linear-gradient(135deg, rgba(255, 65, 108, 0.15), rgba(255, 107, 107, 0.1));
    border-left: 5px solid #ff416c;
}

.result-real {
    background: linear-gradient(135deg, rgba(0, 201, 255, 0.15), rgba(0, 150, 255, 0.1));
    border-left: 5px solid #00c9ff;
}

.result-error {
    background: linear-gradient(135deg, rgba(255, 193, 7, 0.15), rgba(255, 152, 0, 0.1));
    border-left: 5px solid #ffc107;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(90deg, #00d4ff, #7b2ff7);
    color: white;
    border: none;
    border-radius: 10px;
    height: 3.2em;
    width: 100%;
    font-size: 16px;
    font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(0, 212, 255, 0.3);
    letter-spacing: 1px;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0, 212, 255, 0.5);
}

/* Text Area */
.stTextArea > div > div > textarea {
    background: rgba(255, 255, 255, 0.05);
    color: white;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    font-size: 15px;
}

.stTextArea > div > div > textarea:focus {
    border-color: #00d4ff;
    box-shadow: 0 0 10px rgba(0, 212, 255, 0.3);
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 10px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.stTabs [data-baseweb="tab"] {
    color: #b0bec5;
    border-radius: 8px;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(90deg, #00d4ff, #7b2ff7);
    color: white;
}

/* Progress Bar */
.stProgress > div > div > div > span {
    background: linear-gradient(90deg, #00d4ff, #7b2ff7);
}

/* Metrics */
.metric-card {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    padding: 20px;
    border-radius: 12px;
    text-align: center;
}

/* Highlighted Text - Suspicious Words */
.suspicious-word {
    color: #ff4b4b;
    font-weight: bold;
    background: rgba(255, 75, 75, 0.1);
    padding: 2px 6px;
    border-radius: 4px;
}

/* Feature List */
.feature-list {
    list-style: none;
    padding: 0;
}

.feature-list li {
    padding: 8px 0;
    color: #b0bec5;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.feature-list li::before {
    content: "✓ ";
    color: #00c9ff;
    font-weight: bold;
    margin-right: 8px;
}

/* Sidebar */
.stSidebar {
    background: linear-gradient(180deg, rgba(15, 12, 41, 0.8), rgba(48, 43, 99, 0.8));
}

/* Alert Messages */
.stAlert {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 10px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

</style>
""", unsafe_allow_html=True)


with st.sidebar:
    st.markdown("""
    <div class="card-container" style="text-align: center;">
        <h2>⚙️ Settings</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")

    db_status = is_database_connected()
    if db_status:
        st.success("✅ Database Connected")
    else:
        st.warning("⚠️ Database disconnected - Results won't be saved", icon="⚠")
    
    st.markdown("---")
    
    st.markdown("""
    <div class="card-container">
        <h3>📊 Quick Stats</h3>
    </div>
    """, unsafe_allow_html=True)
    
    results = fetch_results()
    if results:
        total_analyses = sum([row[1] for row in results])
        fake_count = next((row[1] for row in results if row[0].lower() == "fake"), 0)
        real_count = next((row[1] for row in results if row[0].lower() == "real"), 0)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total", total_analyses)
        with col2:
            st.metric("Fake", fake_count)
        with col3:
            st.metric("Real", real_count)
    else:
        st.info("No analyses yet")
    
    st.markdown("---")
    
    st.markdown("""
    <div class="card-container">
        <h4>📚 How It Works</h4>
        <ul class="feature-list">
            <li>NLP Sentiment Analysis</li>
            <li>Keyword Detection</li>
            <li>Credibility Scoring</li>
            <li>Source Verification</li>
            <li>Database Storage</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("""
    <div class="header-title">🔍 FAKE NEWS DETECTION AND VERIFICATION TOOL</div>
    <div class="header-subtitle">AI-Powered Truth Verification Engine</div>
    """, unsafe_allow_html=True)

st.markdown("---")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    <div class="card-container">
        <h3>📝 Analyze News Statement</h3>
    </div>
    """, unsafe_allow_html=True)
    
    news_text = st.text_area(
        "Enter the news text or statement to analyze:",
        height=180,
        placeholder="Paste your news text here... (minimum 10 characters)",
        label_visibility="collapsed"
    )

with col2:
    st.markdown("""
    <div class="card-container">
        <h3>⚡ Features</h3>
        <ul class="feature-list">
            <li>Sentiment Analysis</li>
            <li>Credibility Score</li>
            <li>Source Lookup</li>
            <li>Detailed Insights</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

col_button = st.columns([1, 4, 1])[1]

with col_button:
    analyze_button = st.button(
        "🚀 ANALYZE NEWS",
        use_container_width=True,
        key="analyze_btn"
    )

if analyze_button:
    
    if news_text.strip() == "":
        st.warning("⚠️ Please enter news text to analyze", icon="⚠️")
        st.stop()
    
    if len(news_text.strip()) < 10:
        st.warning("⚠️ Please enter at least 10 characters", icon="⚠️")
        st.stop()
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    status_text.write("🤖 Running AI analysis...")
    progress_bar.progress(25)
    
    label, confidence = predict_news(news_text)
    
    progress_bar.progress(50)
    status_text.write("💾 Saving to database...")
    
    if db_status:
        save_result(news_text, label, confidence)

    progress_bar.progress(75)
    status_text.write("📖 Generating explanation...")
    
    reasons = explain_news(news_text)

    status_text.write("🔍 Verifying sources...")
    progress_bar.progress(90)
    
    verification_status, articles = verify_news(news_text[:100])
    
    progress_bar.progress(100)
    status_text.write("✅ Analysis complete!")

    import time
    time.sleep(0.5)
    progress_bar.empty()
    status_text.empty()
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if label.lower() == "fake":
            st.markdown(f"""
            <div class="card-container result-fake">
                <h2>🚨 FAKE NEWS</h2>
                <p style="font-size: 2em; color: #ff416c; margin: 10px 0;">
                    {confidence*100:.1f}%
                </p>
                <p style="color: #b0bec5; font-size: 0.9em;">Confidence Score</p>
            </div>
            """, unsafe_allow_html=True)
        elif label.lower() == "real":
            st.markdown(f"""
            <div class="card-container result-real">
                <h2>✅ REAL NEWS</h2>
                <p style="font-size: 2em; color: #00c9ff; margin: 10px 0;">
                    {confidence*100:.1f}%
                </p>
                <p style="color: #b0bec5; font-size: 0.9em;">Confidence Score</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="card-container result-error">
                <h2>⚠️ UNABLE TO ANALYZE</h2>
                <p style="color: #ffc107;">{label}</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
      
        score = int(confidence * 100)
        
        st.markdown("<h3>📊 Credibility Score</h3>", unsafe_allow_html=True)
        st.progress(score / 100)
        
        if score >= 75:
            status_badge = "🟢 Highly Credible"
            status_color = "#00c966"
        elif score >= 50:
            status_badge = "🟡 Moderately Credible"
            status_color = "#ffc107"
        elif score >= 25:
            status_badge = "🟠 Low Credibility"
            status_color = "#ff9800"
        else:
            status_badge = "🔴 Very Low Credibility"
            status_color = "#f44336"
        
        st.markdown(f"""
        <div style="text-align: center; color: {status_color}; font-weight: bold; margin-top: 10px;">
            {status_badge}
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        word_count = len(news_text.split())
        char_count = len(news_text)
        
        st.markdown("<h3>📈 Text Statistics</h3>", unsafe_allow_html=True)
        
        col_stat1, col_stat2 = st.columns(2)
        with col_stat1:
            st.metric("Word Count", word_count)
        with col_stat2:
            st.metric("Characters", char_count)
    
    st.markdown("---")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "🧠 Explanation",
        "🔗 Sources",
        "📈 Analysis",
        "📋 History"
    ])
    

    with tab1:
        st.markdown("<h3>Why did we get this result?</h3>", unsafe_allow_html=True)
        
        if reasons:
            for i, reason in enumerate(reasons, 1):
                st.markdown(f"""
                <div class="card-container">
                    <strong>{reason}</strong>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No specific indicators detected in this text")
        
        st.markdown("<h4>🔴 Suspicious Words Found:</h4>", unsafe_allow_html=True)
        suspicious_words = highlight_suspicious_words(news_text)
        
        if suspicious_words:
            suspicious_text = ", ".join([f"<strong class='suspicious-word'>{w}</strong>" for w in suspicious_words])
            st.markdown(suspicious_text, unsafe_allow_html=True)
        else:
            st.success("✅ No suspicious words detected")

    with tab2:
        st.markdown("<h3>Related News Sources</h3>", unsafe_allow_html=True)
        
        st.info(verification_status, icon="ℹ️")
        
        if articles:
            for idx, article in enumerate(articles, 1):
                st.markdown(f"""
                <div class="card-container">
                    <h4><a href="{article['url']}" target="_blank" style="color: #00d4ff; text-decoration: none;">
                        {idx}. {article['title']}
                    </a></h4>
                    <p style="color: #b0bec5; margin: 10px 0; font-size: 0.9em;">
                        <strong>Source:</strong> {article['source']}
                    </p>
                    <p style="color: #90a4ae; font-size: 0.85em; margin: 5px 0;">
                        {article['description'][:150]}...
                    </p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ No related articles found or API not configured")
    
    # TAB 3: ANALYSIS
    with tab3:
        st.markdown("<h3>Confidence Analysis</h3>", unsafe_allow_html=True)
        
        # Donut chart
        fig = go.Figure(data=[go.Pie(
            values=[confidence, 1-confidence],
            labels=["Confidence", "Uncertainty"],
            hole=0.4,
            marker=dict(
                colors=['#00d4ff', '#ff416c'],
                line=dict(color='rgba(0,0,0,0)', width=0)
            ),
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>%{value:.2%}<extra></extra>'
        )])
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white', size=12),
            showlegend=True,
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Interpretation
        st.markdown("<h4>📊 Interpretation</h4>", unsafe_allow_html=True)
        
        if label.lower() == "fake":
            interpretation = f"""
            The AI model is **{confidence*100:.1f}% confident** this is **fake news** based on sentiment analysis.
            Negative sentiment indicators suggest potential misinformation patterns.
            """
        else:
            interpretation = f"""
            The AI model is **{confidence*100:.1f}% confident** this is **real news** based on sentiment analysis.
            Positive/neutral sentiment suggests factual and credible language patterns.
            """
        
        st.markdown(interpretation)
    
    # TAB 4: HISTORY
    with tab4:
        st.markdown("<h3>Recent Analyses</h3>", unsafe_allow_html=True)
        
        recent = fetch_recent_results(limit=5)
        
        if recent:
            for item in recent:
                id_val, text, label_val, confidence_val, created_at = item
                
                label_color = "#00c9ff" if label_val.lower() == "real" else "#ff416c"
                
                st.markdown(f"""
                <div class="card-container">
                    <p style="color: #90a4ae; font-size: 0.85em; margin-bottom: 8px;">
                        {created_at}
                    </p>
                    <p style="margin-bottom: 10px;">
                        {text[:80]}...
                    </p>
                    <p style="color: {label_color}; font-weight: bold;">
                        {label_val.upper()} - {confidence_val*100:.1f}% confidence
                    </p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No history yet - analyze some news to get started!")


st.markdown("---")
st.markdown("<h2>📊 Overall Analytics Dashboard</h2>", unsafe_allow_html=True)

try:
    results = fetch_results()
    
    if results and len(results) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            # Bar Chart: Fake vs Real
            labels = [row[0] for row in results]
            values = [row[1] for row in results]
            
            colors = ['#ff416c' if label.lower() == "fake" else '#00c9ff' for label in labels]
            
            fig_bar = go.Figure(data=[go.Bar(
                x=labels,
                y=values,
                marker=dict(color=colors, line=dict(width=0)),
                text=values,
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
            )])
            
            fig_bar.update_layout(
                title="Fake vs Real News Count",
                xaxis_title="Classification",
                yaxis_title="Count",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white', size=12),
                hovermode='x',
                height=400
            )
            
            st.plotly_chart(fig_bar, use_container_width=True)
        
        with col2:
            # Summary Stats
            total = sum(values)
            fake_pct = (values[0] / total * 100) if labels[0].lower() == "fake" else (values[1] / total * 100)
            real_pct = 100 - fake_pct
            
            st.markdown(f"""
            <div class="card-container">
                <h3>📈 Summary Statistics</h3>
                <div style="margin-top: 20px;">
                    <div style="margin: 15px 0; padding: 15px; background: rgba(0,201,255,0.1); border-left: 4px solid #00c9ff; border-radius: 8px;">
                        <h4 style="margin: 0; color: #00c9ff;">Total Analyses</h4>
                        <h2 style="margin: 10px 0; color: white;">{total}</h2>
                    </div>
                    <div style="margin: 15px 0; padding: 15px; background: rgba(0,201,255,0.1); border-left: 4px solid #00c9ff; border-radius: 8px;">
                        <h4 style="margin: 0; color: #00c9ff;">Real News</h4>
                        <h2 style="margin: 10px 0; color: white;">{real_pct:.1f}%</h2>
                    </div>
                    <div style="margin: 15px 0; padding: 15px; background: rgba(255,65,108,0.1); border-left: 4px solid #ff416c; border-radius: 8px;">
                        <h4 style="margin: 0; color: #ff416c;">Fake News</h4>
                        <h2 style="margin: 10px 0; color: white;">{fake_pct:.1f}%</h2>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("🔍 No analysis data yet. Start by analyzing some news!")

except Exception as e:
    st.warning("📊 Unable to load analytics data")

st.markdown("---")

st.markdown("""
<div style="text-align: center; color: #90a4ae; padding: 20px; font-size: 0.85em;">
    <p>🔐 <strong>Privacy & Security:</strong> All your data is stored securely in our MySQL database.</p>
    <p>⚙️ <strong>Technology Stack:</strong> Streamlit | Transformers | News API | MySQL</p>
    <p style="margin-top: 15px; color: #616161;">© 2026 Fake News Detection System | Built with AI</p>
</div>
""", unsafe_allow_html=True)
