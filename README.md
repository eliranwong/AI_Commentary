# AI verse-by-verse commentary generator

A small set of scripts that automatically generate verse-level AI commentaries (English and Traditional Chinese), enrich them with interlinear and morphological data, and store the results in an SQLite database for later conversion to static HTML. The pipeline assembles prompts with source text + interlinear + morphology, calls the LLM via the agentmake wrapper, post-processes the output with the project parser, and saves or updates commentary rows in ai_commentary.db.

Quick start (example)
- Ensure AGENTMAKE_CONFIG is configured and the UniqueBible data files exist under ~/UniqueBible.
- Run the English pipeline:
  - python3 create_ai_commentary.py
- Convert markdown to HTML (example):
  - python3 md2html/convert.py

How it works (high level)
- Source verses: fetch NET (English) or CUV (Chinese) verse tables.
- Enrich: look up interlinear text and per-word morphological data.
- Prompt + LLM: assemble prompt and call agentmake (system role: biblemate/commentary).
- Post-process: parse and format LLM output using BibleVerseParser, then insert/update SQLite.
- Logs & refine: runtime issues written to errors.txt; refine.py helps merge or import commentary rows.

Key files
- create_ai_commentary.py — English pipeline, DB helpers, LLM calls
- create_ai_commentary_zh.py — Traditional Chinese pipeline
- refine.py — utilities for merging/importing commentary
- md2html/convert.py — markdown → HTML example
- verse_alignment/CUV_verse_alignment.md — manual Chinese alignments
- errors.txt — runtime error log

# Published at:

* English

https://biblemate.gospelchurch.uk/?tool=commentary&tq=AIC:::

Traditional Chinese

https://biblemate.gospelchurch.uk/?tool=commentary&tq=AICTC:::

# Related Projects

Analysis of Every Single Book in the Bible

https://github.com/eliranwong/BibleBookStudies

Summary of Every Single Chapter in the Bible

https://github.com/eliranwong/BibleChapterSummaries

Commentary of Every Single Verse in the Bible

https://github.com/eliranwong/AI_Commentary
