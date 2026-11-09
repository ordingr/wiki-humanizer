#!/usr/bin/env python3
"""Score text for AI-writing tells and list them with line numbers.

Usage:
    python ai_tell_lint.py draft.md
    echo "some text" | python ai_tell_lint.py -
    python ai_tell_lint.py --stats references/human-corpus/*.txt

Score = weighted tells per 100 words. Weights follow references/ai-patterns.md:
3 = acts on one sighting (§1-5, §22-23), 2 = usual tell, 1 = weak alone.
Human pre-2022 Wikipedia text scores near 0; treat anything above ~3 as
worth a rewrite. A regex can't read meaning, so the list is a prompt to
look, not a verdict.
"""
import argparse
import re
import sys
from pathlib import Path

W = r"\b"
PATTERNS = [
    # (section, weight, label, regex)
    ("§1", 3, "not X but Y", r"\bnot (?:just|only|merely|simply)\b[^.]{0,80}\bbut\b|\bit'?s not\b[^.]{0,60}[,;—-]\s*it'?s\b|\bthis does(?:n'?t| not) mean\b"),
    ("§2", 3, "dramatic closer", r"^\s*(?:that|this) (?:is|was) the (?:real )?(?:win|point|key|difference|lesson)\.\s*$|\blet that sink in\b|\bread that again\b|\bthat distinction matters\b|\bthe message was clear\b"),
    ("§3", 3, "deep-sounding saying", r"\bthe real question is\b|\bat its core\b|\bwhat really matters\b|\bthe heart of the matter\b|\bthe deeper issue\b|\bfundamentally,"),
    ("§4", 3, "staged run-up", r"\blet'?s (?:dive|delve|explore|break (?:this|it) down)\b|\bhere'?s (?:what you need to know|the thing)\b|\bwithout further ado\b|^\s*(?:honestly\?|look,|real talk)|\blet'?s be honest\b"),
    ("§5", 3, "arguing with no one", r"\bto be clear\b|\bdon'?t get me wrong\b|\bthis is not to say\b|\bi'?m not saying\b|\bone might be tempted\b|\ba tempting approach\b"),
    ("§6", 1, "triad (check it)", r"\b\w+, \w+,? and \w+\b(?=[^.]{0,20}\.)"),
    ("§8", 2, "dash", r"\s?[—–]\s?|\s--\s"),
    ("§9", 1, "stacked qualifier", r"\bcould potentially\b|\bmight arguably\b|\bit'?s also possible\b|\bpotentially possibly\b"),
    ("§12", 2, "AI word", W + r"(?:additionally|bolster(?:ed|s)?|crucial|deep dive|delv(?:e|es|ing)|enduring|enhanc(?:e|es|ing)|garner(?:ed|s)?|interplay|intricac(?:y|ies)|intricate|landscape|meticulous(?:ly)?|pivotal|quietly|showcas(?:e|es|ing)|tapestry|testament|underscor(?:e|es|ing)|vibrant|seamless(?:ly)?|leverag(?:e|es|ing))" + W),
    ("§13", 2, "inflated significance", r"\bstands as a\b|\bplays? a (?:key|crucial|pivotal|vital) role\b|\bmarking a (?:pivotal|significant|key)\b|\bsetting the stage\b|\bindelible mark\b|\bevolving landscape\b|\bthe future looks bright\b|\bexciting times\b|\bcontinues to thrive\b|\breflects a broader\b"),
    ("§14", 1, "vague association", r"\bin (?:association|connection) with\b|\bassociated with\b"),
    ("§15", 2, "-ing rider", r",\s+(?:highlighting|underscoring|emphasizing|reflecting|symbolizing|showcasing|fostering|cultivating|ensuring)\b"),
    ("§16", 2, "sales language", r"\bnestled\b|\bin the heart of\b|\bbreathtaking\b|\bmust-visit\b|\bstunning\b|\brich (?:cultural|history|heritage|tradition)\b|\bdiverse array\b|\brenowned\b|\bgroundbreaking\b"),
    ("§17", 2, "borrowed authority", r"\bexperts (?:argue|believe|say|agree)\b|\bobservers have\b|\bindustry reports\b|\bsome critics\b"),
    ("§18", 1, "avoids is/has", r"\bserves as\b|\bfunctions as\b|\bboasts\b"),
    ("§19", 1, "bold label", r"^\s*[-*]\s+\*\*[^*]+:\*\*|\*\*[^*]+\*\*:"),
    ("§20", 1, "emoji/arrow decoration", "[→\U0001F300-\U0001FAFF✅✨]"),
    ("§22", 3, "chatbot residue", r"\bi hope this helps\b|\bgreat question\b|\bcertainly!|\bof course!|\byou'?re absolutely right\b|\blet me know if\b|\bwould you like me to\b|\bwant me to\b"),
    ("§23", 3, "knowledge-limit hedge", r"\bas of my (?:last|latest)\b|\btraining (?:data|cutoff)\b|\bnot (?:widely|extensively|publicly) (?:documented|available)\b|\bbased on available information\b|\bmaintains a low profile\b"),
]
COMPILED = [(s, w, l, re.compile(p, re.I)) for s, w, l, p in PATTERNS]


def strip_code(text):
    """Blank out fenced and inline code so commands and paths don't count."""
    text = re.sub(r"```.*?```", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.S)
    return re.sub(r"`[^`\n]+`", "", text)


def lint(text):
    text = strip_code(text)
    hits = []
    for n, line in enumerate(text.splitlines(), 1):
        for sec, w, label, rx in COMPILED:
            for m in rx.finditer(line):
                hits.append((n, sec, w, label, m.group(0).strip()))
    words = max(len(re.findall(r"\b\w+\b", text)), 1)
    return hits, words, round(100 * sum(h[2] for h in hits) / words, 1)


def stats(text):
    """Shape numbers for comparing a draft with the human corpus."""
    body = "\n".join(l for l in strip_code(text).splitlines() if not l.startswith("#"))
    sents = [s for s in re.split(r"(?<=[.!?])\s+", body) if len(s.split()) > 2]
    lens = [len(s.split()) for s in sents] or [0]
    words = max(len(body.split()), 1)
    mean = sum(lens) / len(lens)
    sd = (sum((x - mean) ** 2 for x in lens) / len(lens)) ** 0.5
    return {
        "words": words,
        "sentences": len(sents),
        "mean_sentence_words": round(mean, 1),
        "sentence_length_sd": round(sd, 1),
        "dashes_per_1k": round(1000 * len(re.findall(r"[—–]", body)) / words, 2),
        "numbers_per_100": round(100 * len(re.findall(r"\b\d[\d,.]*\b", body)) / words, 1),
        "is_are_was_has_per_100": round(100 * len(re.findall(r"\b(?:is|are|was|were|has|have|had)\b", body, re.I)) / words, 1),
    }


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Score text for AI-writing tells.")
    ap.add_argument("files", nargs="+", help="files to check, or - for stdin")
    ap.add_argument("--stats", action="store_true", help="print sentence-shape stats too")
    args = ap.parse_args()
    for f in args.files:
        text = sys.stdin.read() if f == "-" else Path(f).read_text("utf-8")
        hits, words, score = lint(text)
        print(f"{f}: {words} words, {len(hits)} tells, score {score} per 100 words")
        for n, sec, w, label, match in hits[:60]:
            print(f"  line {n:>4}  {sec:<4} w{w}  {label}: {match!r}")
        if len(hits) > 60:
            print(f"  ... {len(hits) - 60} more")
        if args.stats:
            for k, v in stats(text).items():
                print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
