# Getting Started

This guide walks you through setting up and running the Italy Startups scraping, database initialization, and visualization application.

## Prerequisites

- **Python**: 3.9 or higher (with `venv` support)
- **Node.js & npm**: Recommended LTS version (e.g., v18 or newer)
- **Gemini API Key**: Required only if you want to use the LLM-based scraper. Get an API key from [Google AI Studio](https://aistudio.google.com/).

---

## 1. Backend Setup

First, configure your Python environment and dependencies:

1. **Create and Activate Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install Python Dependencies**:
   ```bash
   pip install requests beautifulsoup4 geopy google-genai pydantic python-dotenv
   ```

3. **Configure Environment Variables**:
   Create a `.env` file in the root directory and add your Gemini API Key:
   ```env
   GEMINI_API_KEY="your_gemini_api_key_here"
   ```

---

## 2. Scraping and Initializing the Database

To crawl the data, resolve locations, and prepare the database:

1. **Scrape Data (LLM Scraper)**:
   This uses Gemini to parse details from EU-Startups articles and saves them to `italy_startups_llm.csv`.
   ```bash
   python scraper_llm.py
   ```

2. **Scrape Data (Heuristic Scraper - Alternative)**:
   If you don't have an API key, you can run the rule-based heuristic scraper:
   ```bash
   python scraper.py
   ```

3. **Geocode and Build Database**:
   This reads `italy_startups_llm.csv` (or edit the script to read `italy_startups.csv`), geocodes the cities via the Nominatim API (with a 1.1s rate-limiting delay per request to be polite to the server), saves them to the SQLite database `startups.db`, and outputs `frontend/public/startups.json`.
   ```bash
   python init_db.py
   ```

---

## 3. Frontend Setup & Run

The visualization frontend is built using React, Vite, and Leaflet.

1. **Navigate to the frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install frontend dependencies**:
   ```bash
   npm install
   ```

3. **Start the local development server**:
   ```bash
   npm run dev
   ```

4. **Access the application**:
   Open [http://localhost:5173/](http://localhost:5173/) in your web browser.
