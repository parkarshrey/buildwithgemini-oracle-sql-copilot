"""External public API integration tool for searching StackOverflow Oracle SQL solutions."""

import os
import requests


def search_oracle_community_solutions(query: str) -> str:
    """Searches StackOverflow for real developer solutions, ORA-error workarounds, and Oracle SQL examples.

    Args:
        query: Search keywords or error codes (e.g., 'ORA-00918', 'Oracle DENSE_RANK', 'optimizing inner join').

    Returns:
        A formatted string listing relevant StackOverflow questions, accepted answers, view counts, and links.
    """
    if not query or not query.strip():
        return "Please provide a valid query or ORA error code to search."

    url = "https://api.stackexchange.com/2.3/search/advanced"
    params = {
        "order": "desc",
        "sort": "relevance",
        "q": query,
        "site": "stackoverflow",
        "pagesize": 3,
    }

    # Optional API key from environment variable if provided for higher rate limits
    api_key = os.getenv("STACKEXCHANGE_API_KEY")
    if api_key:
        params["key"] = api_key

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        items = data.get("items", [])
        if not items:
            return f"No community solutions found on StackOverflow for query: '{query}'."

        results = []
        for idx, item in enumerate(items, 1):
            title = item.get("title", "")
            link = item.get("link", "")
            views = item.get("view_count", 0)
            answers = item.get("answer_count", 0)
            is_answered = item.get("is_answered", False)
            tags = ", ".join(item.get("tags", []))

            status = "Answered" if is_answered else "Unanswered"
            results.append(
                f"{idx}. {title}\n"
                f"   Status: {status} ({answers} answers, {views:,} views)\n"
                f"   Tags: [{tags}]\n"
                f"   Link: {link}"
            )

        return f"Found StackOverflow Community Solutions for '{query}':\n\n" + "\n\n".join(results)

    except Exception as e:
        return f"Error fetching community solutions: {str(e)}"
