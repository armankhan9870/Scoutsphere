# ADR-003: Resume Parsing Approach - Hybrid Rule-Based + LLM Extraction

## Context & Problem Statement
Resume documents come in diverse formats (PDFs, multi-column layouts, table-based layouts, scanned text). ScoutSphere needs to extract clean structured JSON profiles (skills, experience, education, contact info) and generate vector embeddings.

Pure LLM extraction (sending raw PDF bytes or messy text directly to LLM) can hit API rate limits, suffer from high latency, or hallucinate non-existent experience. Pure rule-based parsing (regex/heuristics) breaks on non-standard layouts.

## Decision Drivers
- High structural accuracy for skill, experience, and project extraction.
- Resilience against free-tier LLM rate-limits (429 errors).
- Native multimodal capability (Gemini Flash free tier supports inline PDF document parsing).
- Fast, local pre-processing fallback.

## Considered Options
1. **Pure Heuristic / Rule-Based Parser (pdfplumber + Regex)**
2. **Pure LLM Extraction (Raw PDF $\rightarrow$ Gemini Flash / LLMClient)**
3. **Hybrid Strategy (Local Rule-Based Pre-processing & Sectioning + LLM Structural Extraction & Normalization)**

## Decision Outcome
Chosen Option: **Option 3 - Hybrid Strategy**.

### Justification:
- **Phase 1 (Local Layout Extraction)**: `pdfplumber` / `pypdf` extracts raw text, detects bounding boxes, and partitions document into candidate sections (Work Experience, Skills, Education, Projects).
- **Phase 2 (LLM Structural Extraction)**: Section text chunks are passed to `LLMClient` (Gemini Flash as primary, Groq/Ollama as fallback) with a strict Pydantic JSON schema to parse exact fields.
- **Multimodal Advantage**: When Gemini Flash API is available, raw PDF bytes are passed directly into Gemini's native document parser for visual layout understanding (e.g. multi-column resumes), falling back to `pdfplumber` + Groq/Ollama text parsing when rate-limited.

## Status
Accepted.

## Consequences
- **Positive**: Resilient against rate-limits, handles multi-column visual layouts via Gemini Flash, fallback stability via local text extraction.
- **Negative**: Requires maintaining both PDF text extraction helpers and structured LLM Pydantic schemas.
