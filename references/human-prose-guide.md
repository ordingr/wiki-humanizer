# How pre-2022 human Wikipedia prose behaves

This is the "imitate" side of the skill. `ai-patterns.md` lists what to remove;
this file lists what careful human writers did instead, measured on the
corpus in `human-corpus/` (18 articles, ~131k words, every revision saved
September to October 2022, before ChatGPT launched on 30 Nov 2022).

Run `python scripts/ai_tell_lint.py --stats <draft>` to compare a draft with
these numbers.

## Measured on the corpus (2026-10-28)

| Measure | Corpus value | What it means for a draft |
|---|---|---|
| AI-tell score | 0.2 per 100 words | Aim under 1. Above 3, rewrite. |
| Mean sentence length | 22.7 words | Medium-long sentences are normal; no need to chop. |
| Sentence length spread (SD) | 11.4 words | Lengths vary a lot. Uniform 15-word sentences read as machine. |
| Em/en dashes | 0.07 per 1,000 words | Roughly one dash per 14,000 words. Use none. |
| Numbers | 2.1 per 100 words | About one figure every 50 words. |
| is/are/was/has/had | 3.5 per 100 words | Plain verbs carry most sentences. |
| Lead sentence "X is a/an/the ..." | 18 of 18 articles | Open by saying what the thing is. |
| "in YEAR" | 498 uses | Facts are pinned to dates. |
| "according to" | 50 uses | Claims are pinned to a named source. |

## Re-measured after adding security, engineering and Featured articles (2026-10-29)

The corpus grew to 53 articles and about 332k words, adding 10 security
articles, 10 software engineering articles and 13 Featured articles (Wikipedia's
top quality grade). Every revision is still dated before 1 Nov 2022. The shape
held steady, which suggests these numbers describe human encyclopedic prose in
general rather than the first 18 topics:

| Measure | 18 articles | 53 articles |
|---|---|---|
| AI-tell score | 0.2 | 0.2 |
| Mean sentence length | 22.7 | 23.0 |
| Sentence length SD | 11.4 | 11.7 |
| Dashes per 1,000 words | 0.07 | 0.1 |
| Numbers per 100 words | 2.1 | 2.1 |
| is/are/was/has/had per 100 words | 3.5 | 3.6 |

For security and engineering writing, calibrate against `Computer_security.txt`,
`Transport_Layer_Security.txt`, `Software_engineering.txt`, `DevOps.txt` and
`Kubernetes.txt`. For prose at its best, read any Featured article
(`Elephant.txt`, `Apollo_8.txt`, `Charles_Darwin.txt`, `Sea.txt`).

## The habits behind the numbers

1. **Say what it is, first.** The first sentence defines the subject with a
   plain verb ("A warehouse is a building for storing goods."). No run-up,
   no framing of why it matters.
2. **Numbers instead of adjectives.** Where AI text says "significant growth",
   the human text gives the figure, the unit and the year. If you lack the
   number, write a plainer sentence rather than an inflated one.
3. **Attribution is specific.** "According to the 2019 census" or a named
   historian, never "experts say". If no one is named, the claim stands on
   its own or goes.
4. **Paragraphs end on a fact.** The last sentence of a paragraph is usually
   another piece of information, not a summary of the paragraph or a lesson.
5. **Plain verbs.** *is, has, was, built, sold, moved*. Not *serves as,
   boasts, stands as, plays a pivotal role in*.
6. **Lists stay in prose until they really are lists.** Three or more items
   run inline with commas; bullets appear only for genuinely parallel,
   reference-style content.
7. **Uneven rhythm.** A 40-word sentence with two clauses sits next to an
   8-word one. Writers did not balance them on purpose.
8. **Hedges are local and sourced.** "about", "approximately" (123 uses
   together) qualify a number; they are not stacked on an opinion.
9. **No commentary on the text itself.** No "this section explains", no
   closing paragraph about the future, no "in conclusion".
10. **Dull is allowed.** Encyclopedic text accepts a flat sentence when the
    fact is flat. It does not decorate to keep the reader engaged.

## Using the corpus as reference

Before rewriting in the encyclopedic register, open one or two corpus files
on a related subject (`Supply_chain_management.txt`, `Warehouse.txt`,
`Cloud_computing.txt`, `SQL.txt`, `Microsoft_Excel.txt` for business and tech
work) and read a few paragraphs. Match the shape: sentence length, how facts
are dated, how sources are named. Do not copy sentences; the corpus is
CC BY-SA and is there to calibrate the ear, not to be quoted.

Add more articles any time:

    python scripts/fetch_human_corpus.py "Inventory" "Logistics"

`manifest.json` records the revision ID and a permanent link for every file.
