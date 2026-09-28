#!/usr/bin/env python3
"""Seed script for populating the initial Oracle SQL queries in Firestore."""

import datetime
from google.cloud import firestore

# Hardcode GCP Project ID directly as required (do NOT use google.auth.default() or GOOGLE_CLOUD_PROJECT)
FIRESTORE_PROJECT_ID = "qwiklabs-gcp-02-56893539409e"

SEEDED_QUERIES = [
    {
        "query_id": "oracle_top_salaries_01",
        "title": "Top 3 Salaries Per Department",
        "sql_text": (
            "SELECT dept_id, emp_id, salary, "
            "DENSE_RANK() OVER (PARTITION BY dept_id ORDER BY salary DESC) as rank "
            "FROM employees WHERE status = 'ACTIVE' FETCH FIRST 100 ROWS ONLY;"
        ),
        "dialect": "Oracle",
        "category": "Analytic Functions",
        "complexity_score": 45,
        "explanation": "Uses DENSE_RANK() window function to partition employees by department and rank them by salary.",
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
    },
    {
        "query_id": "oracle_hierarchy_02",
        "title": "Employee Org Chart Hierarchy",
        "sql_text": (
            "SELECT emp_id, last_name, manager_id, LEVEL, "
            "SYS_CONNECT_BY_PATH(last_name, '/') AS path "
            "FROM employees START WITH manager_id IS NULL "
            "CONNECT BY PRIOR emp_id = manager_id;"
        ),
        "dialect": "Oracle",
        "category": "Hierarchical",
        "complexity_score": 65,
        "explanation": "Uses Oracle CONNECT BY PRIOR and SYS_CONNECT_BY_PATH to build an organizational reporting hierarchy.",
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
    },
    {
        "query_id": "oracle_index_hint_03",
        "title": "Optimized Order Detail Search",
        "sql_text": (
            "SELECT /*+ INDEX(o idx_orders_cust_date) */ o.order_id, o.order_date, "
            "c.customer_name, i.item_name, i.price "
            "FROM orders o "
            "JOIN customers c ON o.customer_id = c.customer_id "
            "JOIN order_items i ON o.order_id = i.order_id "
            "WHERE o.order_date >= TRUNC(SYSDATE) - 30;"
        ),
        "dialect": "Oracle",
        "category": "Optimization",
        "complexity_score": 55,
        "explanation": "Uses Oracle TRUNC date arithmetic and optimizer hint /*+ INDEX(...) */ to accelerate 30-day order lookups.",
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
]

def seed():
    print(f"Connecting to Firestore for project: {FIRESTORE_PROJECT_ID}...")
    db = firestore.Client(project=FIRESTORE_PROJECT_ID)
    collection_ref = db.collection("saved_queries")

    for item in SEEDED_QUERIES:
        doc_ref = collection_ref.document(item["query_id"])
        doc_ref.set(item)
        print(f"Seeded document: {item['query_id']} - {item['title']}")

    print("Firestore seeding completed successfully!")

if __name__ == "__main__":
    seed()
