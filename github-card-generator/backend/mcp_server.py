import os
import json
import httpx
from fastmcp import FastMCP
from google import genai
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("GitHubDevCard")

# Initialize Gemini Client
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=GOOGLE_API_KEY) if GOOGLE_API_KEY else None

@mcp.tool()
async def scrape_github(username: str) -> dict:
    """
    Calls the GitHub REST API to fetch public profile data.
    """
    headers = {"Accept": "application/vnd.github.v3+json"}
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    async with httpx.AsyncClient() as http_client:
        # Fetch user profile
        user_url = f"https://api.github.com/users/{username}"
        user_resp = await http_client.get(user_url, headers=headers)
        if user_resp.status_code != 200:
            return {"error": f"User {username} not found"}
        user_data = user_resp.json()

        # Fetch repos
        repos_url = f"https://api.github.com/users/{username}/repos?sort=stars&per_page=100"
        repos_resp = await http_client.get(repos_url, headers=headers)
        repos_data = repos_resp.json() if repos_resp.status_code == 200 else []

        # Aggregate languages
        languages = {}
        for repo in repos_data:
            lang = repo.get("language")
            if lang:
                languages[lang] = languages.get(lang, 0) + 1
        
        sorted_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)

        # Top 6 repos
        top_repos = []
        for repo in sorted(repos_data, key=lambda x: x.get("stargazers_count", 0), reverse=True)[:6]:
            top_repos.append({
                "name": repo.get("name"),
                "stars": repo.get("stargazers_count"),
                "language": repo.get("language"),
                "description": repo.get("description")
            })

        return {
            "name": user_data.get("name") or username,
            "bio": user_data.get("bio"),
            "location": user_data.get("location"),
            "avatar_url": user_data.get("avatar_url"),
            "public_repos": user_data.get("public_repos"),
            "followers": user_data.get("followers"),
            "top_6_repos": top_repos,
            "languages": [l[0] for l in sorted_langs[:5]]
        }

@mcp.tool()
async def analyze_profile(github_data: dict) -> dict:
    """
    Uses Gemini to analyze GitHub data and extract developer personality.
    """
    if not client:
        return {"error": "Gemini API key not configured"}

    prompt = f"""
    Analyze this GitHub profile data and return a JSON object with:
    - developer_vibe: 1 sentence personality.
    - top_skills: list of 3 skills.
    - fun_fact: something clever inferred from their repos.
    - card_theme: one of ["hacker", "builder", "researcher", "designer", "open-source-hero"].

    Data: {json.dumps(github_data)}
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json"
        }
    )
    return json.loads(response.text)

@mcp.tool()
async def generate_card_html(username: str, github_data: dict, analysis: dict) -> str:
    """
    Generates a self-contained HTML string for a beautiful dev card.
    """
    theme = analysis.get("card_theme", "builder")
    
    # Simple theme mapping
    bg_color = {
        "hacker": "#0f0", "builder": "#007bff", "researcher": "#6c757d",
        "designer": "#e83e8c", "open-source-hero": "#28a745"
    }.get(theme, "#333")
    
    html = f"""
    <div style="font-family: sans-serif; max-width: 400px; border: 2px solid {bg_color}; border-radius: 15px; padding: 20px; background: #1a1a1a; color: white; box-shadow: 0 4px 15px rgba(0,0,0,0.5);">
        <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 15px;">
            <img src="{github_data.get('avatar_url')}" style="width: 80px; height: 80px; border-radius: 50%; border: 3px solid {bg_color};">
            <div>
                <h2 style="margin: 0;">{github_data.get('name')}</h2>
                <p style="margin: 5px 0 0; color: {bg_color}; font-weight: bold;">@{username}</p>
            </div>
        </div>
        <p style="font-style: italic; font-size: 0.9em; margin-bottom: 15px;">"{analysis.get('developer_vibe')}"</p>
        <div style="margin-bottom: 15px;">
            {' '.join([f'<span style="background: {bg_color}; padding: 3px 8px; border-radius: 10px; font-size: 0.8em; margin-right: 5px;">{s}</span>' for s in analysis.get('top_skills', [])])}
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 0.85em; border-top: 1px solid #333; padding-top: 10px; margin-bottom: 15px;">
            <span>📦 <b>{github_data.get('public_repos')}</b> Repos</span>
            <span>👥 <b>{github_data.get('followers')}</b> Followers</span>
        </div>
        <div>
            <h4 style="margin: 0 0 10px; border-bottom: 1px solid #333;">Top Projects</h4>
            {''.join([f'<div style="margin-bottom: 5px; font-size: 0.85em;">⭐ {r["name"]} <span style="color: #888;">({r["language"]})</span></div>' for r in github_data.get('top_6_repos', [])[:3]])}
        </div>
        <div style="margin-top: 15px; font-size: 0.75em; color: #888; text-align: center;">
            💡 {analysis.get('fun_fact')}
        </div>
    </div>
    """
    return html

@mcp.tool()
async def save_card(username: str, html: str) -> str:
    """
    Saves the HTML to static/cards/{username}.html.
    """
    output_dir = Path("static/cards")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = output_dir / f"{username}.html"
    file_path.write_text(html, encoding="utf-8")
    
    return f"/static/cards/{username}.html"

if __name__ == "__main__":
    mcp.run()
