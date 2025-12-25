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

# Distribution Licence

<a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/"><img alt="Creative Commons Licence" style="border-width:0" src="https://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png" /></a><br /><span xmlns:dct="http://purl.org/dc/terms/" href="http://purl.org/dc/dcmitype/Text" property="dct:title" rel="dct:type">BibleMate AI Verse Commentary</span> by <a xmlns:cc="http://creativecommons.org/ns#" href="https://www.bibletools.app" property="cc:attributionName" rel="cc:attributionURL">Eliran Wong</a> is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/">Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License</a>.<br />Based on a work at <a xmlns:dct="http://purl.org/dc/terms/" href="https://github.com/eliranwong/AI_Commentary" rel="dct:source">https://github.com/eliranwong/AI_Commentary</a>.<br />Permissions beyond the scope of this license may be available at <a xmlns:cc="http://creativecommons.org/ns#" href="https://marvel.bible/contact/contactform.php" rel="cc:morePermissions">https://marvel.bible/contact/contactform.php</a>.

# Published at:

* English

https://biblemate.gospelchurch.uk/?tool=commentary&tq=AIC:::

Traditional Chinese

https://biblemate.gospelchurch.uk/?tool=commentary&tq=AICTC:::

Simplified Chinese

https://biblemate.gospelchurch.uk/?tool=commentary&tq=AICSC:::

# Related Projects

This resource is built for BibleMate AI:

https://github.com/eliranwong/biblemate

https://github.com/eliranwong/biblemategui

Analysis of Every Single Book in the Bible

https://github.com/eliranwong/BibleBookStudies

Summary of Every Single Chapter in the Bible

https://github.com/eliranwong/BibleChapterSummaries

Commentary of Every Single Verse in the Bible

https://github.com/eliranwong/AI_Commentary
