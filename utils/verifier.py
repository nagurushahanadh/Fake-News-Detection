import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("NEWS_API_KEY", "")

def verify_news(query):
    """
    Verify news by finding similar articles from trusted sources using News API.
    
    Args:
        query (str): Search query (news text or keywords)
    
    Returns:
        tuple: (status_message, articles_list)
    """
    
    if not API_KEY:
        return "⚠️ News API key not configured", []
    
    try:
        search_query = query[:100] if query else "news"
        
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": search_query,
            "apiKey": API_KEY,
            "language": "en",
            "sortBy": "relevancy",
            "pageSize": 5
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if data.get("status") != "ok":
            error_msg = data.get("message", "Unknown API error")
            return f"⚠️ API Error: {error_msg}", []
        
        articles = data.get("articles", [])
        
        if len(articles) == 0:
            return "ℹ️ No related news sources found", []
     
        formatted_articles = []
        for article in articles[:5]:
            formatted_articles.append({
                "title": article.get("title", "No title"),
                "url": article.get("url", "#"),
                "source": article.get("source", {}).get("name", "Unknown"),
                "description": article.get("description", "No description"),
                "image": article.get("urlToImage", "")
            })
        
        return "✅ Found similar news in trusted sources", formatted_articles
        
    except requests.exceptions.Timeout:
        return "⚠️ API request timeout", []
    except requests.exceptions.RequestException as e:
        return f"⚠️ Network error: {str(e)}", []
    except Exception as e:
        print(f"❌ Verification Error: {e}")
        return "⚠️ Verification service unavailable", []
