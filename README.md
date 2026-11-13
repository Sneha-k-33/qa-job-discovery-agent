# Automated QA Job Discovery & Telegram Alert Agent

An automated, self-hosted job discovery pipeline built with **FastAPI**, **SQLAlchemy**, **APScheduler**, and the **Telegram Bot API**. Designed to continuously aggregate global remote Quality Assurance (QA) and SDET opportunities, deduplicate listings in SQLite, display them on a live web dashboard, and push instant notifications to Telegram.

---

## System Architecture & Key Features

* **Multi-Source API Aggregation (`app/services/discovery.py`)**: Fetches live remote tech job feeds from public JSON endpoints (**Himalayas** and **RemoteOK**) and filters roles by QA-specific keywords (`QA`, `Quality Assurance`, `Test`, `SDET`).
* **Database Deduplication (`SQLite` + `SQLAlchemy`)**: Enforces composite unique constraints (`source` + `source_job_id`) in `JobListing` to ensure zero duplicate alerts and track discovery run audit logs (`DiscoveryRun`).
* **Instant Telegram Bot Alerts**: Pushes formatted Markdown notifications with direct application links via the Telegram Bot API (`sendMessage`) the moment a new role is discovered.
* **Automated Background Scheduling (`APScheduler`)**: Uses FastAPI's `lifespan` context manager to run a background discovery worker automatically every **3 hours**.
* **Interactive Web Dashboard & REST API (`static/index.html`)**: Provides a responsive Bootstrap UI and REST endpoints (`/api/jobs`, `/api/discover`) to browse listings, inspect metadata, and trigger on-demand scans.

---

## Tech Stack

* **Backend**: Python 3.11+, FastAPI, Uvicorn
* **Database & ORM**: SQLite, SQLAlchemy 2.0
* **HTTP & Automation**: HTTPX (async requests), APScheduler
* **Notifications**: Telegram Bot API
* **Frontend**: HTML5, Vanilla JavaScript (Fetch API), Bootstrap 5

---

## Local Setup & Installation

### 1. Clone the repository & create a virtual environment
```powershell
git clone [https://github.com/](https://github.com/)<your-username>/qa-job-discovery-agent.git
cd qa-job-discovery-agent
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt