#!/usr/bin/env python3
"""
MINI-LFM — the smallest "Large Fact Model" that actually works, now with a MUSE SPARK mode.
No pip, no numpy, no torch. Just CPython.

MUSE SPARK (Meta, Apr 2026) is a closed, proprietary model — its real weights are
not public, so this file cannot copy them. Instead it replicates what IS known
about Muse Spark's behavior, at mini scale, on top of the base fact recaller:

  * REASONING      Muse Spark is a reasoning model. MUSE mode shows its work:
                   a visible chain-of-thought over the whole fact database
                   (top candidates, matched words, probabilities), then a
                   self-consistency check (several sampled reasoning passes;
                   the answer that wins the vote is the one it commits to).

  * ABSTENTION     Reasoning models decline when unsure. Base mode always
                   guesses (remember "tallest mountain" -> paris 11%?).
                   MUSE mode refuses to answer below a confidence threshold.

  * LONG CONTEXT   Base mode matches exact words. MUSE mode also matches word
                   stems ("planets" ~ "planet"), like a bigger retriever.

Built the same way as mini_llm.py, four parts, all included:
  1. DATA        a tiny fact database, embedded below
  2. TOKENIZER   words (lowercased, punctuation stripped)
  3. TRAIN       count question-word -> fact co-occurrences
  4. ANSWER      score every stored fact against the question (naive Bayes),
                 reason over the scores, pick (or abstain)

Usage:
  python3 mini_lfm.py                     # base: run the built-in demo
  python3 mini_lfm.py --muse              # muse-spark mode: reasoning + abstention
  python3 mini_lfm.py --muse --q "capital of japan"
  python3 mini_lfm.py --q "Capital of France?" --verbose
"""

import argparse
import math
import random
import re

# ---------------------------------------------------------------------------
# 1. DATA — the entire fact database. That's all the "knowledge" it has.
# ---------------------------------------------------------------------------
FACTS = [
    ("what is the capital of france", "paris"),
    ("what is the capital of japan", "tokyo"),
    ("what is the capital of the usa", "washington dc"),
    ("what is the largest planet", "jupiter"),
    ("what is the closest planet to the sun", "mercury"),
    ("how many planets are in the solar system", "eight"),
    ("how many legs does a spider have", "eight"),
    ("what is two plus two", "four"),
    ("what is the square root of 144", "twelve"),
    ("what do bees make", "honey"),
    ("what is the largest ocean", "the pacific ocean"),
    ("what color is the sky", "blue"),
    ("who painted the mona lisa", "leonardo da vinci"),
    ("what is the boiling point of water in celsius", "one hundred"),
]

DEMO_QUESTIONS = [
    "what is the capital of france",
    "capital of japan",
    "what color is the sky",
    "how many legs does a spider have",
    "who painted the mona lisa",
    "what is the tallest mountain on earth",  # not memorized -> should abstain in muse mode
    "please recite shakespeare",              # no overlap at all -> honest failure
]

# ---------------------------------------------------------------------------
# 2. TOKENIZER — words, lowercased, punctuation stripped. Plus a tiny stemmer.
# ---------------------------------------------------------------------------
def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())  # "Washington DC" -> ["washington", "dc"]


def stem(w: str) -> str:
    """Weak lemmatizer: "planets" -> "planet". Enough for a toy retriever."""
    return w[:-1] if w.endswith("s") and len(w) > 3 else w


# ---------------------------------------------------------------------------
# 3. TRAIN — count question-word -> fact co-occurrences (full words + stems).
# ---------------------------------------------------------------------------
def train(facts: list[tuple[str, str]]):
    word_fact: dict[str, dict[int, int]] = {}   # word -> {fact id -> count}
    questions = [q for q, _ in facts]
    answers = [a for _, a in facts]
    for i, (q, _) in enumerate(facts):
        for w in set(tokenize(q)):              # each word counts once per fact
            for key in {w, stem(w)}:
                row = word_fact.setdefault(key, {})   # build the row first:
                row[i] = row.get(i, 0) + 1            # RHS runs before the target
    return word_fact, questions, answers


# ---------------------------------------------------------------------------
# 4. ANSWER — score every stored fact, then reason (or just guess).
# ---------------------------------------------------------------------------
def score(word_fact, answers, question, temp):
    """Naive Bayes: p(fact | words) proportional to product of p(word | fact),
       uniform prior, in log space, softened by temperature (the same knob
       mini_llm.py uses when sampling). Returns probabilities and the set of
       question words that matched anything."""
    n = len(answers)
    logs = [0.0] * n
    hits: dict[int, set[str]] = {i: set() for i in range(n)}
    matched = set()
    for w in set(tokenize(question)):
        for key in {w, stem(w)}:
            row = word_fact.get(key)
            if row is None:
                continue
            matched.add(w)
            total = sum(row.values())
            for i in range(n):                 # +1 smoothing keeps unknowns possible
                c = row.get(i, 0)
                if c:
                    hits[i].add(w)
                logs[i] += math.log((c + 1) / (total + n))
    m = max(logs)
    temp = max(temp, 0.05)
    probs = [math.exp((l - m) / temp) for l in logs]
    s = sum(probs)
    return [p / s for p in probs], matched, hits


def answer_base(word_fact, questions, answers, question, temp, verbose, rng, do_sample):
    probs, matched, _ = score(word_fact, answers, question, temp)
    order = sorted(range(len(answers)), key=lambda i: -probs[i])
    choice = rng.choices(range(len(answers)), weights=probs)[0] if do_sample else order[0]
    print(f"Q: {question}")
    if not matched:
        print("A: (i don't know — no word matched anything I memorized)")
    else:
        print(f"A: {answers[choice]}")
    print(f"   confidence {probs[choice] * 100:5.1f}%  "
          f"({len(matched)} matched word{'s' if len(matched) != 1 else ''})")
    if verbose:
        for i in order[1:4]:
            print(f"   runner-up: {answers[i]!r}  {probs[i] * 100:5.1f}%")
    print()


def answer_muse(word_fact, questions, answers, question, temp, rng, trials, threshold):
    """MUSE SPARK mode: show the chain-of-thought, vote with self-consistency,
       abstain if even the winner isn't confident enough."""
    probs, matched, hits = score(word_fact, answers, question, temp)
    order = sorted(range(len(answers)), key=lambda i: -probs[i])

    print(f"Q: {question}")
    if not matched:
        print("reasoning : nothing matched anything I memorized (0 words).")
        print("spark > I don't know.")
        print()
        return

    print(f"reasoning : I checked all {len(answers)} memorized facts "
          f"({len(matched)} question words matched):")
    for i in order[:3]:
        words = sorted(hits[i])[:10]
        q = questions[i] if len(questions[i]) <= 36 else questions[i][:33] + "..."
        print(f"           cand {answers[i]!r:>18}  p={probs[i]:5.2f}  [{q}]")
        print(f"               matched {words}")

    votes = [rng.choices(range(len(answers)), weights=probs)[0] for _ in range(trials)]
    winner = max(set(votes), key=votes.count)
    agree = votes.count(winner)
    print(f"           self-consistency: {trials} reasoning passes -> "
          f"{answers[winner]!r} {agree}/{trials}")

    if probs[winner] < threshold:
        print(f"spark > I'm not sure. Best candidate is only "
              f"{probs[winner] * 100:.0f}% confidence — refusing to guess.")
    else:
        print(f"spark > {answers[winner]}  (confidence {probs[winner] * 100:.0f}%)")
    print()


def main():
    ap = argparse.ArgumentParser(description="the smallest LFM on earth")
    ap.add_argument("--muse", action="store_true",
                    help="muse-spark mode: reasoning trace + abstention")
    ap.add_argument("--trials", type=int, default=5, help="reasoning passes (muse mode)")
    ap.add_argument("--threshold", type=float, default=0.3,
                    help="below this confidence, muse mode refuses to answer")
    ap.add_argument("--q", default=None, help="ask one question")
    ap.add_argument("--temp", type=float, default=0.15,
                    help="temperature (1 = plain Bayes, lower = sharper)")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--verbose", action="store_true", help="show runner-up facts")
    ap.add_argument("--sample", action="store_true",
                    help="sample the answer instead of always taking the best")
    ap.add_argument("--council", action="store_true",
                    help="run the 20-model council and let THIS model decide the winner")
    args = ap.parse_args()

    if args.council:
        import os as _os
        import subprocess as _sp
        import sys as _sys
        council = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "model_council.py")
        cmd = [_sys.executable, council, "--decider-hook", "lfm",
               "--seed", str(args.seed if args.seed is not None else 1)]
        _sys.exit(_sp.call(cmd))

    word_fact, questions, answers = train(FACTS)
    rng = random.Random(args.seed)

    print(f"fact db  : {len(FACTS)} memorized facts")
    print(f"vocab    : {len(word_fact)} distinct words (incl. stems)")
    print(f"weights  : {sum(len(row) for row in word_fact.values())} learned word->fact counts")
    if args.muse:
        print(f"mode     : MUSE SPARK — reasoning over all facts, "
              f"{args.trials} self-consistency passes, abstain below "
              f"{args.threshold * 100:.0f}% confidence")
    print("=" * 44)

    queries = [args.q] if args.q else DEMO_QUESTIONS
    for q in queries:
        if args.muse:
            answer_muse(word_fact, questions, answers, q, args.temp, rng,
                        args.trials, args.threshold)
        else:
            answer_base(word_fact, questions, answers, q, args.temp,
                        args.verbose, rng, args.sample)


if __name__ == "__main__":
    main()
