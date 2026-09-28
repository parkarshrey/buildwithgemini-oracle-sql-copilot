"""SQL parsing, formatting, and static analysis tools."""

import sqlparse


def parse_and_lint_sql(sql_query: str) -> dict:
    """Parses, formats, and lints an Oracle SQL query using static AST analysis.

    Args:
        sql_query: The SQL query string to parse and lint.

    Returns:
        A dictionary containing formatted SQL, complexity score, statement type, join count, and lint issues.
    """
    if not sql_query or not sql_query.strip():
        return {"error": "Empty SQL query provided"}

    formatted = sqlparse.format(
        sql_query,
        reindent=True,
        keyword_case="upper",
        strip_comments=False,
    )

    parsed = sqlparse.parse(sql_query)
    stmt_type = "UNKNOWN"
    if parsed:
        stmt_type = parsed[0].get_type()

    upper_query = sql_query.upper()
    join_count = upper_query.count("JOIN")
    subquery_count = upper_query.count("SELECT") - 1 if upper_query.count("SELECT") > 1 else 0
    where_count = upper_query.count("WHERE")
    group_by = "GROUP BY" in upper_query
    window_funcs = any(kw in upper_query for kw in ["OVER (", "ROW_NUMBER()", "DENSE_RANK()", "RANK()"])

    # Complexity score calculation (scale of 10 to 100)
    score = 10 + (join_count * 15) + (subquery_count * 20) + (15 if window_funcs else 0) + (10 if group_by else 0)
    score = min(100, max(10, score))

    lint_issues = []
    if not sql_query.strip().endswith(";"):
        lint_issues.append("Query statement does not terminate with a semicolon ';'.")
    if "SELECT *" in upper_query:
        lint_issues.append("Avoid 'SELECT *' in production Oracle queries; explicitly select required columns.")
    if "LIKE '%" in upper_query:
        lint_issues.append("Leading wildcard 'LIKE %...' prevents B-Tree index lookup; consider Oracle Text / CONTEXT index.")

    return {
        "formatted_sql": formatted,
        "statement_type": stmt_type,
        "complexity_score": score,
        "join_count": join_count,
        "subquery_count": subquery_count,
        "has_window_functions": window_funcs,
        "lint_issues": lint_issues if lint_issues else ["No lint warnings found."],
    }
