# Scraper Approaches Comparison

This project contains two distinct approaches for extracting information from EU-Startups articles: a **Heuristic-based approach** and a **Generative LLM-based approach**. 

---

## 1. Heuristic-Based Scraper (`scraper.py`)

This approach extracts fields using custom string analysis and regular expressions.

### Pros
- **Fast and cost-efficient**: Runs locally in parallel without requiring network calls to an external AI model. No API costs.
- **Deterministic**: Given the same HTML input, it will always output the exact same parsed values.
- **Zero Dependencies**: Does not require any external LLM keys or advanced SDKs.

### Cons
- **Brittle**: Extremely dependent on specific title formatting patterns (e.g. looking specifically for terms like `" raises "`, `" secures "`, or `" acquires "`). Any change in formatting by editors will break the extraction.
- **Inaccurate/Limited**: High rate of `"N/A"` fields. Identifying founders and exact startup names from varied natural language contexts via regex is notoriously difficult and error-prone.
- **Hard to Maintain**: Requires adding more regex edge cases continuously as new articles use different phrasing.

---

## 2. LLM-Based Scraper (`scraper_llm.py`)

This approach leverages Google's **Gemini 2.5 Flash** model with structured outputs (`response_schema` utilizing Pydantic).

### Pros
- **Highly Accurate**: LLMs understand the context of the article, meaning they can correctly extract founders and startup names regardless of the phrasing.
- **Structured Output**: Uses Gemini's JSON schema feature (`response_mime_type="application/json"`), ensuring the output always conforms exactly to the expected Pydantic model (`StartupInfo`).
- **Resilient**: Will not break if the editorial style of the website changes slightly.

### Cons
- **API Dependency & Costs**: Requires an active `GEMINI_API_KEY` and incurs usage costs (though extremely cost-effective with Flash models).
- **Rate Limits**: Subject to API rate limits (resolved by utilizing a smaller worker pool of `max_workers=3` during parallel execution).
- **Non-deterministic**: Rarely, LLMs might output slightly different variations of names or locations across runs.

---

## Field Extraction Comparison

| Field | Heuristic Method (`scraper.py`) | LLM Method (`scraper_llm.py`) |
| :--- | :--- | :--- |
| **Startup Name** | Extract token preceding `" raises "` / `" secures "` in the title. | Semantic analysis of the whole article + title. |
| **Location** | Matches pattern `([A-Z][a-zA-Z\s,]+)-based`. | Understood from the context of where the startup operates. |
| **Founders** | Regex for `founded ... by [Name]` or `[Name], co-founder`. | Extracted from natural text references to founders. |
| **Website** | Grabs the first external URL not matching social networks. | Identifies and extracts the official company URL. |
