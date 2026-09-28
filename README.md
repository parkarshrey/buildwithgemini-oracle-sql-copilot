# Oracle SQL Copilot & Advisor

An AI-powered assistant built with the **Google Agent Development Kit (ADK)** and deployed on **Agent Runtime (A2A Protocol)**. **Oracle SQL Copilot & Advisor** helps data engineers and database developers generate, parse, lint, optimize, and visualize Oracle SQL queries, search real Oracle developer community solutions, and persist query catalogs across sessions.

![Oracle SQL Copilot & Advisor Demo](demo.gif)

---

## 🚀 Key Features & Capabilities

All features below are implemented directly in `app/` and registered with the core agent:

* **⚡ Oracle SQL Analysis & CTE Optimization** ([`app/sql_tools.py`](file:///config/Desktop/Session1/oracle-sql-copilot/app/sql_tools.py))
  * Parses Oracle SQL queries using `sqlparse`.
  * Computes statement complexity scores (0–100) and detects subquery redundancy.
  * Refactors complex, multi-branch queries (such as repeated `UNION ALL` subqueries) into clean Common Table Expressions (CTEs) using `WITH` clauses.

* **🧠 Cross-Session Long-Term Memory** ([`app/agent.py`](file:///config/Desktop/Session1/oracle-sql-copilot/app/agent.py))
  * Integrates **Vertex AI Memory Bank** (`VertexAiMemoryBankService`) targeting the Agent Engine Memory Bank.
  * Automatically stores user preferences, database schemas, and developer context across separate conversation sessions via `PreloadMemoryTool` and post-turn callbacks.

* **📦 Firestore Query Catalog** ([`app/firestore_tools.py`](file:///config/Desktop/Session1/oracle-sql-copilot/app/firestore_tools.py))
  * Saves, tags, searches, and retrieves SQL query snippets in **Google Cloud Firestore** under the `saved_sql_queries` collection.

* **🔍 Oracle Community Knowledge Base** ([`app/community_tools.py`](file:///config/Desktop/Session1/oracle-sql-copilot/app/community_tools.py))
  * Searches curated Oracle community solutions and discussions for common database errors (e.g. `ORA-00942`, `ORA-01555`, `ORA-00054`, `ORA-01427`).

* **🎨 Visual ERD & Architecture Diagram Generation** ([`app/image_tools.py`](file:///config/Desktop/Session1/oracle-sql-copilot/app/image_tools.py))
  * Uses Google's `gemini-3.1-flash-lite-image` model in the `global` region to generate technical database ERD diagrams and system architecture flows.
  * Saves artifacts to the ADK Artifacts panel and uploads public images directly to Google Cloud Storage.

* **🎬 3D Animated Concept Video Generation** ([`app/video_tools.py`](file:///config/Desktop/Session1/oracle-sql-copilot/app/video_tools.py))
  * Uses Google's Omni model (`gemini-omni-flash-preview`) in the `global` region to create 3D animated motion graphics depicting database concepts (e.g. table joins, execution plans).
  * Saves artifacts to ADK Playground and publishes public MP4 videos to Google Cloud Storage.

* **🔒 Secure Python Code Sandbox** ([`app/agent.py`](file:///config/Desktop/Session1/oracle-sql-copilot/app/agent.py))
  * Uses `AgentEngineSandboxCodeExecutor` to safely execute Python calculation and validation code inside Google Cloud Agent Engine.

* **📍 Google Maps Integration** ([`app/maps_tools.py`](file:///config/Desktop/Session1/oracle-sql-copilot/app/maps_tools.py))
  * Geocodes addresses and searches nearby locations via Google Maps Platform API.

* **📱 A2UI Native Card Interface** ([`app/a2ui_utils.py`](file:///config/Desktop/Session1/oracle-sql-copilot/app/a2ui_utils.py), [`frontend/`](file:///config/Desktop/Session1/oracle-sql-copilot/frontend/))
  * Emits A2UI v0.8 cards (Cards, Columns, Rows, Text, Images) rendered natively in the FastAPI chat proxy and web interface.

---

## 🔮 Roadmap (Planned, Not Yet Implemented)

* **Live Database Execution**: Direct connection to live Oracle Database instances (`cx_Oracle` / `oracledb`) to run `EXPLAIN PLAN` and fetch real execution statistics.

---

## 🛠️ Project Structure

```
.
├── app/                        # Agent backend application
│   ├── agent.py                # Core ADK Agent, Memory Bank, & A2UI setup
│   ├── sql_tools.py            # Oracle SQL parser, linter, & complexity analyzer
│   ├── firestore_tools.py      # Firestore query catalog integration
│   ├── community_tools.py      # Oracle community search tools
│   ├── image_tools.py          # Diagram generation via gemini-3.1-flash-lite-image
│   ├── video_tools.py          # 3D video generation via gemini-omni-flash-preview
│   └── maps_tools.py           # Google Maps geocoding & places lookups
├── frontend/                   # Web frontend & A2A FastAPI proxy
│   ├── main.py                 # FastAPI proxy forwarding browser requests over A2A
│   └── static/                 # Chat web interface (index.html, A2UI renderer)
├── agents-cli-manifest.yaml    # Deployment manifest for agents-cli 1.1.0
├── demo.gif                    # Animated walkthrough demonstration
└── record_demo.py              # Automated Playwright recording script
```

---

## 💻 Local Setup & Execution Instructions

### 1. Prerequisites

* Python 3.11+
* `agents-cli` 1.1.0+
* Google Cloud SDK (`gcloud`) authenticated with Application Default Credentials:

```bash
gcloud auth login
gcloud auth application-default login
```

### 2. Install Backend & Agent Dependencies

```bash
uv pip install -r requirements.txt
```

### 3. Run Agent Locally with ADK Web

```bash
adk web app
```

### 4. Run Frontend Proxy Locally

Navigate to the `frontend` folder, set the required environment variables, and run the FastAPI server:

```bash
cd frontend
pip install -r requirements.txt
export AGENT_ENGINE_RESOURCE_NAME="projects/<PROJECT_NUMBER>/locations/<LOCATION>/reasoningEngines/<ENGINE_ID>"
export AGENT_DIRECTORY="app"
python main.py
```

---

## 🚀 Deployment Instructions

### Deploy Agent to Agent Runtime

```bash
agents-cli deploy --project <PROJECT_ID> --no-confirm-project
```

### Deploy Frontend Proxy to Cloud Run

```bash
gcloud run deploy oracle-sql-copilot-frontend \
  --source ./frontend \
  --region us-east1 \
  --allow-unauthenticated \
  --set-env-vars AGENT_ENGINE_RESOURCE_NAME="projects/<PROJECT_NUMBER>/locations/<LOCATION>/reasoningEngines/<ENGINE_ID>",AGENT_DIRECTORY="app"
```
