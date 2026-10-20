import requests
from bs4 import BeautifulSoup


def fetch_github_trending(since: str = "weekly") -> list[dict]:
    url = f"https://github.com/trending?since={since}"
    headers = {"User-Agent": "Mozilla/5.0 (compatible; AI-Digest/1.0)"}
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
    except Exception as e:
        print(f"  ⚠ GitHub trending fetch error: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    repos = []

    for i, item in enumerate(soup.select("article.Box-row")[:10], 1):
        h2 = item.select_one("h2 a")
        if not h2:
            continue
        path = h2.get("href", "").strip("/")
        parts = path.split("/")
        owner = parts[0] if parts else ""
        repo_name = parts[1] if len(parts) > 1 else path
        repo_url = f"https://github.com/{path}"

        desc_el = item.select_one("p")
        description = desc_el.get_text(strip=True) if desc_el else ""

        lang_el = item.select_one("[itemprop='programmingLanguage']")
        language = lang_el.get_text(strip=True) if lang_el else ""

        star_links = item.select("a.Link--muted")
        total_stars = star_links[0].get_text(strip=True) if star_links else "?"
        forks = star_links[1].get_text(strip=True) if len(star_links) > 1 else "?"

        weekly_el = item.select_one("span.d-inline-block.float-sm-right")
        weekly_stars = weekly_el.get_text(strip=True) if weekly_el else ""

        repos.append({
            "rank": i,
            "name": f"{owner}/{repo_name}",
            "owner": owner,
            "repo": repo_name,
            "url": repo_url,
            "description": description,
            "language": language,
            "total_stars": total_stars.strip(),
            "weekly_stars": weekly_stars.strip(),
            "forks": forks.strip(),
        })
        print(f"  #{i} {owner}/{repo_name} ({language}) ⭐{total_stars.strip()}")

    return repos
