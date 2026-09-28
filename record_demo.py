"""Record a demo video of the Oracle SQL Copilot & Advisor web frontend optimizing a complex UNION query and invoking tools."""

import os
import time
from playwright.sync_api import sync_playwright

def record_demo():
    video_dir = os.path.abspath("demo_video")
    os.makedirs(video_dir, exist_ok=True)
    
    target_url = "https://oracle-sql-copilot-frontend-701008191527.us-east1.run.app"
    print(f"Starting browser recording for {target_url}...")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-gpu"]
        )
        context = browser.new_context(
            record_video_dir=video_dir,
            record_video_size={"width": 1280, "height": 720},
            viewport={"width": 1280, "height": 720}
        )
        page = context.new_page()

        print("Navigating to frontend...")
        page.goto(target_url, wait_until="networkidle")
        time.sleep(2)

        # Prompt 1: Complex UNION Query Optimization with WITH clause
        prompt_1_text = (
            "Optimize this complex Oracle SQL query with multiple UNION ALLs using a WITH clause (CTE) "
            "for the repeated active_regions subquery: \n\n"
            "SELECT 'Q1' AS quarter, region_id, SUM(amount) AS total_sales FROM sales_q1 WHERE status = 'COMPLETED' "
            "AND region_id IN (SELECT id FROM active_regions WHERE is_enabled = 1) GROUP BY region_id "
            "UNION ALL SELECT 'Q2' AS quarter, region_id, SUM(amount) AS total_sales FROM sales_q2 WHERE status = 'COMPLETED' "
            "AND region_id IN (SELECT id FROM active_regions WHERE is_enabled = 1) GROUP BY region_id "
            "UNION ALL SELECT 'Q3' AS quarter, region_id, SUM(amount) AS total_sales FROM sales_q3 WHERE status = 'COMPLETED' "
            "AND region_id IN (SELECT id FROM active_regions WHERE is_enabled = 1) GROUP BY region_id "
            "UNION ALL SELECT 'Q4' AS quarter, region_id, SUM(amount) AS total_sales FROM sales_q4 WHERE status = 'COMPLETED' "
            "AND region_id IN (SELECT id FROM active_regions WHERE is_enabled = 1) GROUP BY region_id;"
        )
        print("Executing Prompt 1: Complex UNION Query Optimization with WITH Clause...")
        page.fill("#input", prompt_1_text)
        time.sleep(1)
        page.click("button[type='submit']")

        # Wait for agent response
        print("Waiting for Prompt 1 response...")
        page.wait_for_selector("#log .msg.agent", timeout=60000)
        time.sleep(6)  # Pause to showcase optimization result & WITH clause

        # Prompt 2: Richer prompt showing tool call & generated ERD diagram image
        prompt_2_text = "Generate an ERD visual diagram for an e-commerce database with customers, orders, products, and payments tables"
        print(f"Executing Prompt 2: {prompt_2_text}...")
        page.fill("#input", prompt_2_text)
        time.sleep(1)
        page.click("button[type='submit']")

        # Wait for agent response containing the generated diagram
        print("Waiting for Prompt 2 response...")
        page.wait_for_selector("#log .msg.agent:nth-of-type(4)", timeout=60000)
        time.sleep(8)  # Pause to showcase ERD diagram

        context.close()
        browser.close()
        print("Recording finished successfully. Video saved in demo_video/ directory.")

if __name__ == "__main__":
    record_demo()
