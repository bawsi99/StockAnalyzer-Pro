# StockAnalyzer-Pro 📈

A state-of-the-art, enterprise-grade stock analysis platform that combines advanced technical indicators, AI-powered pattern recognition, multi-timeframe analysis, and real-time market data streaming to provide comprehensive stock market insights and trading recommendations.


This repo also contains a pitchdeck, accepted into video interview stage for a16z speedrun SR006.


## Monorepo structure (Git submodules)

This repository is a monorepo that pulls the backend and frontend as Git submodules. Work primarily happens inside those sub-repos.

- Backend (FastAPI services): backend — https://github.com/bawsi99/stockanalyzerpro_backend
- Frontend (React/TypeScript/Vite): frontend — https://github.com/bawsi99/stockanalyzerpro_frontend

Top-level files only provide orchestration and docs for the two sub-repos.

### Repo layout
```
.
├── backend/   # Git submodule: FastAPI services (data, analysis, database)
├── frontend/  # Git submodule: Vite + React app
├── .gitmodules
├── LICENSE
└── README.md (this file)
```

## 📘 Product overview (from pitch deck)

- What we do: Autonomous AI trading analysis and asset management platform delivering actionable, risk-aware insights in real time.
- Who it's for: Active traders, quant researchers, funds/desks, brokers/fintechs integrating decision support.
- Core value: Multi-agent LLM analysis, multi-timeframe alignment, sector context, pattern/risk synthesis, live data stream.
- Differentiation: Agentic orchestration with prefetch reuse, in-memory charting, unified cache, and production-grade FastAPI services.
- Go-to-market: Tiered subscriptions (Individual/Pro/Enterprise), API licensing, and white-label partnerships.
- Roadmap highlights: Broker/execution integrations, automated strategies API, alerting, mobile, and model marketplace.
- Call to action: For access, private review, partnerships, funding or investment, contact the owner (see Owner & Contact).

## ❗ Problem

- Human bottleneck: Expensive analyst teams cover only 20–30 stocks/day, making exchange-wide coverage impractical.
- Fragmented workflow: Research, trading, and portfolio management are split across people/tools, causing delays, inconsistency, and missed opportunities.
- High cost, low access: Institutional-grade research and portfolio tools are out of reach for small funds and individuals.

## ✅ Solution

An autonomous AI trading analysis and asset management platform that automates the entire investment workflow via a coordinated multi-agent system, scaling to analyze entire exchanges in real time.

See architecture below for the full agent suite and data flow.

## 🧠 System architecture: multi-agent orchestration

- Orchestrator coordinates independent agents in parallel with a shared in-process prefetch cache (correlation_id-based reuse) and Redis for persistence.
- System agents (top-level):
  - Technical Analysis Agent (LIVE – Proof of Concept on NSE (India))
  - Fundamental Analysis Agent
  - Market Intelligence Agent
  - Autonomous Trading Agent
  - Portfolio Management Agent
- Data flow (high level): data snapshot → indicators → parallel agents → cache/compose → final decision → persist → UI/WS updates.

## 🔬 Technical Analysis Agent (overview)

Status: LIVE — Proof of Concept on equity market for NSE (India)

- Purpose: Provide fast, robust technical features and a curated indicator summary for downstream agents and UI.
- Inputs: symbol, exchange, timeframe/interval, period/window; optional indicator set and parameters.
- Capabilities:
  - 25+ indicators (RSI, MACD, Bollinger, ADX, Stoch, OBV, Ichimoku, VWAP, pivots, Fibonacci, volatility/volume metrics)
  - Minimal-data fallbacks and input validation; feature normalizations where applicable
  - Indicator Summary LLM that converts curated metrics to markdown + structured JSON
  - Designed to interoperate with MTF Agent for cross-timeframe alignment
- Outputs: indicator values, derived signals (trend/momentum/volatility/liquidity), curated summary for LLM/UI, metadata (coverage, data windows)
- Performance & caching: in-process prefetch reuse plus Redis-backed cache; charts generated in-memory and returned as base64
- Extensibility: add indicator functions to a central registry; typed schemas for responses

Sub-agents (TA internal architecture):
- Indicator Agent — analyses different indicators
- Pattern Agent — analyses different patterns and charts
- Machine learning–based pattern success scoring agent — predicts success probability of a pattern, supports Pattern Agent
- Sector Agent — sector benchmarking and correlation
- Market Index Agent — market index benchmarking
- Multi-Time frame Agent — analyses multiple time frames for more context to support decision making
- Risk scoring — risk scoring, scenario analysis, and stress testing
- Machine learning–based quant scoring Agent — supports price predictions
- FINAL Decision Agent — receives information from all of the above agents and gives final decision

## 📌 Current status (from pitch deck and codebase)

- Implemented: Technical Analysis agent: multi-agent orchestration (MTF, pattern, volume suite, sector, risk, final decision); in-memory charting; Redis caching; real-time data streaming; Supabase-backed persistence interfaces.
- Submodule structure: this repo hosts frontend and backend as Git submodules; active development primarily occurs within those sub-repos.
- Target users: active traders, quant teams, funds/desks, and fintech/broker partners.
- Roadmap highlights: broker/execution integrations, automated strategies API, alerting, mobile apps, model marketplace.
- Media: see demo video and pitch materials below for a visual walkthrough and business overview.

## 📄 Setup & docs

For setup, environment configuration, and deployment guides, see:
- backend/README.md (backend services)
- frontend/README.md (frontend app)


## 📹 Media & Demos

- **Product Demo**: `StockAnalyzer Pro demo.mov` - Interactive platform walkthrough
- **Pitch Video**: `StockAnalyzerPro_pitch_video.mp4` - Complete business presentation
- **Pitch Deck**: `stockanalyzerpro_pitchdeck.pdf` - Business overview and strategy

## 👤 Owner & Contact

- Owner: Aaryan Manawat
- Email: aaryanmanawat99@gmail.com
- Phone: +91 9321536130
- For additional access, private review, demos, partnerships, funding, or investment discussions, please contact the owner.

## ⚠️ Usage Notice

- Code is open-source under GPLv3 (see License below).
- Media and brand assets (demo video, pitch video, pitch deck, logos) are proprietary; copying or distribution requires explicit permission.
- For commercial licensing or private deployments, contact the owner.


## 🔒 Security & performance (high level)

- JWT/Supabase auth, CORS, and rate limiting where applicable
- Async FastAPI services; Redis caching; token usage tracking for LLMs
- In-memory charting; resource caps via env

## 📝 License

Licensed under the GNU General Public License v3.0. See `LICENSE` for details.

---

Disclaimer: This tool is for educational and research purposes only and does not constitute financial advice. Trading involves risk. 
