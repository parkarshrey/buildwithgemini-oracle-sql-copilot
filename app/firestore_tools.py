"""Firestore function tools for reading and writing saved SQL queries."""

import datetime

from google.cloud import firestore

# Hardcoded GCP Project ID directly as required (do NOT use google.auth.default() or GOOGLE_CLOUD_PROJECT)
FIRESTORE_PROJECT_ID = "qwiklabs-gcp-02-56893539409e"


def _get_db_client() -> firestore.Client:
    return firestore.Client(project=FIRESTORE_PROJECT_ID)


def save_sql_query(
    title: str,
    sql_text: str,
    category: str = "General",
    explanation: str = "",
    complexity_score: int = 50,
) -> str:
    """Saves a SQL query into the Firestore catalog for future reference.

    Args:
        title: Short descriptive title for the SQL query.
        sql_text: The complete SQL query statement.
        category: Category/tag (e.g. Analytic, Hierarchical, Optimization, General).
        explanation: Explanation of what the query does.
        complexity_score: Estimated query complexity score (1-100).

    Returns:
        A string confirming the save operation with the query ID.
    """
    try:
        db = _get_db_client()
        query_id = f"query_{int(datetime.datetime.now(datetime.timezone.utc).timestamp())}"
        doc_ref = db.collection("saved_queries").document(query_id)

        data = {
            "query_id": query_id,
            "title": title,
            "sql_text": sql_text,
            "dialect": "Oracle",
            "category": category,
            "complexity_score": complexity_score,
            "explanation": explanation,
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
        doc_ref.set(data)
        return f"Successfully saved query '{title}' to Firestore catalog with ID: {query_id}"
    except Exception as e:
        return f"Error saving query to Firestore: {str(e)}"


def list_saved_queries(category: str = "") -> str:
    """Lists saved SQL queries from the Firestore catalog.

    Args:
        category: Optional category filter (e.g. Analytic, Optimization). If empty, returns all queries.

    Returns:
        A formatted string listing the saved queries with their IDs, titles, and categories.
    """
    try:
        db = _get_db_client()
        col_ref = db.collection("saved_queries")

        if category:
            docs = col_ref.where("category", "==", category).stream()
        else:
            docs = col_ref.stream()

        results = []
        for doc in docs:
            item = doc.to_dict()
            results.append(
                f"- ID: {item.get('query_id')} | Title: {item.get('title')} | "
                f"Category: {item.get('category')} | Complexity: {item.get('complexity_score')}\n"
                f"  SQL: {item.get('sql_text')[:80]}..."
            )

        if not results:
            return "No saved queries found in Firestore catalog."

        return "Saved SQL Queries in Firestore Catalog:\n" + "\n".join(results)
    except Exception as e:
        return f"Error fetching saved queries from Firestore: {str(e)}"


def get_saved_query_by_id(query_id: str) -> str:
    """Retrieves full details and SQL text of a specific saved query by its ID.

    Args:
        query_id: The unique document ID of the query (e.g. oracle_top_salaries_01).

    Returns:
        A detailed string formatted with full query attributes and SQL text.
    """
    try:
        db = _get_db_client()
        doc_ref = db.collection("saved_queries").document(query_id)
        doc = doc_ref.get()

        if not doc.exists:
            return f"Query with ID '{query_id}' was not found in Firestore."

        item = doc.to_dict()
        return (
            f"=== Saved Query: {item.get('title')} ===\n"
            f"ID: {item.get('query_id')}\n"
            f"Dialect: {item.get('dialect')}\n"
            f"Category: {item.get('category')}\n"
            f"Complexity Score: {item.get('complexity_score')}\n"
            f"Explanation: {item.get('explanation')}\n\n"
            f"SQL Code:\n{item.get('sql_text')}"
        )
    except Exception as e:
        return f"Error retrieving query '{query_id}' from Firestore: {str(e)}"
