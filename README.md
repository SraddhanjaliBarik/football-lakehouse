# football-lakehouse
Football Streaming Lakehouse

An end-to-end data and AI project on Databricks Free Edition: football match events are streamed into a medallion lakehouse (bronze → silver → gold), visualised in a live dashboard, and queried through a guarded agentic AI analyst that answers questions in plain English.

Built with Python, SQL, Databricks (Unity Catalog, Auto Loader, Jobs, AI/BI Dashboards), and an LLM agent with tool calling.

What it does
Replays a real match event by event (StatsBomb open data) from a Python producer, simulating a live feed.
Ingests the feed with Auto Loader into Delta tables governed by Unity Catalog.
Transforms raw JSON into clean, de-duplicated events, then into analytics views (xG, shot map, player form).
Visualises the match in a Databricks AI/BI dashboard (xG race, shot map, top players).
Answers questions through an AI agent that can only run read-only queries on the gold layer.
Automates the pipeline with a Databricks Job (bronze → silver).



Tech stack

Python · SQL · PySpark Structured Streaming · Databricks Free Edition (serverless) · Unity Catalog · Delta Lake · Auto Loader · Databricks Jobs · AI/BI Dashboards · LLM tool calling (Databricks model serving endpoint) · Git/GitHub

Repository structure
football-lakehouse/
├── README.md
├── .env.example          # settings template, no secrets
├── .gitignore
├── producer/
│   ├── replay_to_volume.py   # replays a match, uploads batches to the Volume
│   └── list_matches.py       # lists match IDs for a competition/season
└── notebooks/
    ├── 01_bronze_stream.py   # Auto Loader → bronze
    ├── 02_silver_stream.py   # parse, validate, de-duplicate → silver
    ├── 03_gold.py            # gold SQL views
    └── 04_agent.py           # AI analyst with SQL guard and tests
Setup

Prerequisites: a Databricks Free Edition workspace, Python 3.11+, and a Databricks personal access token.

Create the catalog objects (Databricks SQL editor):
sql
   CREATE CATALOG IF NOT EXISTS football;
   CREATE SCHEMA  IF NOT EXISTS football.bronze;
   CREATE SCHEMA  IF NOT EXISTS football.silver;
   CREATE SCHEMA  IF NOT EXISTS football.gold;
   CREATE VOLUME  IF NOT EXISTS football.bronze.landing;
   CREATE VOLUME  IF NOT EXISTS football.bronze.chk;
Configure the producer on your machine:
bash
   python -m venv .venv && source .venv/bin/activate
   pip install databricks-sdk requests python-dotenv
   cp .env.example .env      # then fill in your host and token
Import the notebooks from notebooks/ into your workspace.
Create the job football_pipeline with two serverless notebook tasks: bronze (01_bronze_stream) then silver (02_silver_stream, depends on bronze).
Run the producer, then run the job:
bash
   python producer/replay_to_volume.py            # default match
   python producer/replay_to_volume.py <match_id> # any other StatsBomb match
Run 03_gold once to create the views, then build the dashboard on football.gold.*.

Agentic AI analyst

The agent (notebooks/04_agent.py) uses an LLM with two tools: describe_gold (list views and columns) and query_gold (run a SELECT). It plans, queries, and explains in plain English, for example:

Spain created better chances than England, with a total xG of 1.79 compared to England's 0.73, a difference of 1.06 xG.
