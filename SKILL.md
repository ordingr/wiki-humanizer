---
name: wiki-humanizer
description: |
  Make writing read as human-written, using Wikipedia as the source of truth in
  two directions: Wikipedia's "Signs of AI writing" for what to remove (via the
  Humanizer skill's 26 patterns) and pre-ChatGPT Wikipedia revisions as measured
  examples of human prose to imitate. Use when the user asks to humanize, de-AI,
  or make text sound less like ChatGPT/Claude, when reviewing a draft for AI
  tells, or when writing a report, doc, email, post, README, PR description or
  client deliverable that should not read as machine-written.
license: MIT (vendored Humanizer patterns); corpus text CC BY-SA 3.0 from Wikipedia
metadata:
  version: "1.0.0"
---

# wiki-humanizer

Text saved to Wikipedia before 30 November 2022 was written by people. This
skill uses that fact twice:

- **Avoid:** `references/ai-patterns.md` is Humanizer v3.1.0 by Siqi Chen
  (github.com/blader/humanizer, MIT), built from Wikipedia's "Signs of AI
  writing". 26 patterns, strongest first.
- **Imitate:** `references/human-prose-guide.md` describes how human
  Wikipedia prose behaves, measured on `references/human-corpus/` (18
  articles as they stood in Sep to Oct 2022).

## 1. Pick the register

| Text | Register | Voice source |
|---|---|---|
| Reports, docs, READMEs, specs, client deliverables, summaries | Encyclopedic | `human-prose-guide.md` + a related corpus file |
| Emails, chat replies, posts, personal notes | The user's own | `voice-sample.md` if it has real text; otherwise plain and direct, no corporate tone |
| PR descriptions, commit messages | Plain technical | Encyclopedic rules, but short |
| Fiction | Out of scope for the corpus | Use `ai-patterns.md` only |

If `voice-sample.md` still says "no sample yet", say so once when writing in
the user's voice, and suggest they fill it.

## 2. Work

1. Read `references/ai-patterns.md` (the full method is there: mark, draft,
   check, final). Follow its rules on not adding facts.
2. For the encyclopedic register, read `references/human-prose-guide.md` and
   skim a few paragraphs of the closest corpus file to calibrate.
3. Write or rewrite.
4. Check by observation, not by feel:

       python <skill-dir>/scripts/ai_tell_lint.py --stats draft.md

   Aim for a score under 1 per 100 words (the human corpus scores 0.2) and
   zero dashes. Fix every w3 hit. Treat w1 hits as prompts to look, since
   the regex can't read meaning. If the stats show uniform sentence
   lengths (SD well under 8), vary them.
5. Return what `ai-patterns.md` says to return for the mode (pasted text,
   file, or embedded).

When writing your own output (not rewriting the user's text), apply steps 3
and 4 silently and return only the final text.

## 3. Grow the corpus

    python <skill-dir>/scripts/fetch_human_corpus.py "Title one" "Title two"
    python <skill-dir>/scripts/fetch_human_corpus.py --date 2020-01-01 "Title"

The script refuses any date on or after 2022-11-30. It backs off when
Wikipedia rate-limits (HTTP 429). Each file's header and `manifest.json`
carry the revision ID and a permanent link.

## Limits

Removing tells doesn't make text accurate or good. Testers of Humanizer found
it can make prose more casual and less precise, so for technical text keep
the exact terms, numbers and names even when they sound stiff. Wikipedia's
own guidance warns that the hardest AI text to spot is polished on the
surface, and no tell list catches that.
