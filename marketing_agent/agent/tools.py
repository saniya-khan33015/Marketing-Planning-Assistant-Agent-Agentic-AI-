# Tool execution log (basic, in-memory for now)
tool_execution_log = []

# Mock tool implementations for the agent

def get_competitors():
    return ["BrandA", "BrandB", "BrandC"]

def fetch_ads_data():
    return [{"brand": "BrandA", "ads": 12}, {"brand": "BrandB", "ads": 8}]

def analyze_trends():
    return {"trend": "Video ads increasing", "platform": "Instagram"}

def generate_report():
    return "Report generated: Competitor ad strategies summarized."

# Real data demo tool: fetch marketing news headlines
def fetch_marketing_news():
    """
    Fetches latest marketing news headlines from NewsAPI (requires API key in .env as NEWSAPI_KEY).
    Logs execution result and errors.
    """
    import requests
    import os
    api_key = os.getenv("NEWSAPI_KEY", "demo")
    url = f"https://newsapi.org/v2/top-headlines?category=business&q=marketing&apiKey={api_key}"
    result = None
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            articles = resp.json().get("articles", [])
            result = [a["title"] for a in articles[:5]] or ["No news found."]
        else:
            result = [f"Failed to fetch news. Status: {resp.status_code}"]
    except Exception as e:
        result = [f"Error fetching news: {e}"]
    tool_execution_log.append({
        "tool": "fetch_marketing_news",
        "output": result
    })
    return result

# Real data demo tool: fetch Google Trends
def fetch_google_trends(keyword, geo='US'):
    """
    Fetches Google Trends data for a given keyword and region.
    """
    from pytrends.request import TrendReq
    pytrends = TrendReq()
    try:
        pytrends.build_payload([keyword], geo=geo)
        data = pytrends.interest_over_time()
        if not data.empty:
            trend = data[keyword].tolist()
            return f"Trend for '{keyword}' in {geo}: {trend[-5:]} (last 5 points)"
        else:
            return f"No trend data found for '{keyword}' in {geo}."
    except Exception as e:
        return f"Error fetching Google Trends: {e}"

# Tool registry for validation and calling
TOOL_REGISTRY = {
    "get_competitors": get_competitors,
    "fetch_ads_data": fetch_ads_data,
    "analyze_trends": analyze_trends,
    "generate_report": generate_report,
    "fetch_marketing_news": fetch_marketing_news,
    "fetch_google_trends": fetch_google_trends
}
