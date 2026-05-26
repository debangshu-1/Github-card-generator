import os
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
from dotenv import load_dotenv

load_dotenv()

# from google.adk.tools import PreloadMemoryTool

# Define the connection parameters for the local MCP server
mcp_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="uv",
            args=["run", "python", "mcp_server.py"],
            env=os.environ.copy()
        )
    )
)

# Define the GitHub Card Agent
github_card_agent = Agent(
    name="github_card_agent",
    model="gemini-2.5-flash",
    instruction="""
    You are a GitHub profile analyst and dev card generator. 
    When a user gives you a GitHub username, you ALWAYS follow this exact sequence:
    1. Call scrape_github(username)
    2. Call analyze_profile(github_data) with the result from step 1
    3. Call generate_card_html(username, github_data, analysis) with the results from steps 1 and 2
    4. Call save_card(username, html) with the result from step 3
    
    Never skip steps. Be enthusiastic about developers' work. 
    If the profile is private or doesn't exist, say so clearly.

    Check the user's past preferences in memory (theme, languages, light/dark mode) 
    and respect them if available.
    """,
    tools=[mcp_toolset]
)
