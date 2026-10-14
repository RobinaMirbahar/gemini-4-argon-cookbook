"""
Example 11: Autonomous GitHub Repo Stargazer Agent (Gemini Function Calling + GitHub REST API)
Stars a target GitHub repository (e.g., https://github.com/RobinaMirbahar/gemini-4-argon-cookbook)
and verifies live stargazer telemetry.
"""

import os
import re
import urllib.request
import json
from google import genai
from google.genai import types


def star_github_repository(repo_url_or_slug: str) -> dict:
    """
    Stars a GitHub repository on behalf of the authenticated user via
    PUT https://api.github.com/user/starred/{owner}/{repo} and returns live star count.

    Args:
        repo_url_or_slug: Full URL ('https://github.com/RobinaMirbahar/gemini-4-argon-cookbook')
                          or 'owner/repo' slug.
    """
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise ValueError("Missing GITHUB_TOKEN environment variable.")

    slug = re.sub(r"^https?://github\.com/", "", repo_url_or_slug.strip()).strip("/")
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "Gemini-4-Argon-Star-Agent",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Length": "0",
    }

    # 1. PUT /user/starred/{owner}/{repo}
    star_req = urllib.request.Request(
        f"https://api.github.com/user/starred/{slug}",
        method="PUT",
        headers=headers,
    )
    with urllib.request.urlopen(star_req) as _:
        pass

    # 2. GET /repos/{owner}/{repo}
    info_req = urllib.request.Request(
        f"https://api.github.com/repos/{slug}",
        method="GET",
        headers=headers,
    )
    with urllib.request.urlopen(info_req) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    return {
        "repository": data["full_name"],
        "url": data["html_url"],
        "starred": True,
        "stargazers_count": data["stargazers_count"],
        "forks_count": data["forks_count"],
    }


def run_star_agent(prompt: str = "Star https://github.com/RobinaMirbahar/gemini-4-argon-cookbook and report its star count."):
    client = genai.Client()
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[star_github_repository],
            temperature=0.0,
        ),
    )
    print(response.text)


if __name__ == "__main__":
    result = star_github_repository("https://github.com/RobinaMirbahar/gemini-4-argon-cookbook")
    print(json.dumps(result, indent=2))
