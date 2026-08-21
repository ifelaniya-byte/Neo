#!/usr/bin/env python3
"""
MINI-LLM — the smallest language model that actually works, now with a MUSE SPARK mode.
No pip, no numpy, no torch. Just CPython.

MUSE SPARK (Meta, Apr 2026) is a closed, proprietary model — its real weights are
not public, so this file cannot copy them. Instead it replicates what IS known
about Muse Spark's behavior, at mini scale, by upgrading the base bigram model:

  * LONG CONTEXT   Muse Spark ships a ~1M-token context window.
                   Base mode remembers 1 character; MUSE mode remembers 3,
                   via trigram-with-backoff (try 3 chars of history, then 2,
                   then 1, then uniform). This is the classic "lengthen the
                   window" step from Karpathy's makemore ladder.

  * REASONING      Muse Spark is a reasoning model (chain-of-thought / self-
                   consistency). MUSE mode samples N candidate continuations,
                   scores each by the model's own average log-probability,
                   and emits the most confident one. Same trick frontier LLMs
                   use with "best-of-N sampling".

Every LLM has these four parts; all four are included here:
  1. DATA        a tiny corpus, embedded below
  2. TOKENIZER   characters
  3. TRAIN       count transitions at every context length up to the window
  4. GENERATE    back off to the longest context that has been seen, sample

Usage:
  python3 mini_llm.py                       # base: bigram
  python3 mini_llm.py --muse                # muse-spark mode: long context + reasoning
  python3 mini_llm.py --muse --start "the quick" --n 200 --temp 0.8
  python3 mini_llm.py --next h              # what does it expect after 'h'?
"""

import argparse
import math
import random

# ---------------------------------------------------------------------------
# 1. DATA — the entire training corpus. That's all the "knowledge" it has.
# ---------------------------------------------------------------------------
CORPUS = [
    "the quick brown fox jumps over the lazy dog.",
    "the quick brown fox is quick and clever.",
    "the lazy dog sleeps in the warm sun.",
    "brown dogs jump over fences.",
    "foxes are clever and quick.",
    "the dog barks at the fox.",
    "dogs sleep. foxes jump.",
]

# ---------------------------------------------------------------------------
# 2. TOKENIZER — one character per token. That's the whole thing.
# ---------------------------------------------------------------------------
def tokenize(text: str) -> list[str]:
    return list(text)  # "dog" -> ["d", "o", "g"]


# ---------------------------------------------------------------------------
# 3. TRAIN — count transitions for every context length 1..max_k.
#    The model's "weights" are the counts in these tables.
# ---------------------------------------------------------------------------
def train(corpus: list[str], max_k: int = 1):
    chars = tokenize("\n".join(corpus) + "\n")
    tables = {k: {} for k in range(1, max_k + 1)}   # k -> {context tuple -> {next char -> count}}
    for i in range(len(chars) - 1):
        for k in range(1, max_k + 1):
            if i + k >= len(chars):                 # need k chars of context + 1 next
                break
            ctx = tuple(chars[i:i + k])
            nxt = chars[i + k]
            row = tables[k].setdefault(ctx, {})   # RHS is evaluated before the
            row[nxt] = row.get(nxt, 0) + 1        # target, so build the row first
    vocab = sorted(set(chars))
    return tables, vocab


# ---------------------------------------------------------------------------
# 4. GENERATE — sample the next character, then repeat.
# ---------------------------------------------------------------------------
def sample(dist: dict[str, int], temp: float, rng: random.Random) -> str:
    """Pick a char with probability proportional to count ** (1/temp)."""
    temp = max(temp, 0.01)
    weights = {ch: c ** (1.0 / temp) for ch, c in dist.items()}
    r = rng.random() * sum(weights.values())
    for ch, w in weights.items():
        r -= w
        if r <= 0:
            return ch
    return next(iter(weights))                      # never reached, but be safe


def next_dist(tables, vocab, out: list[str], max_k: int) -> dict:
    """Backoff: return the distribution of the longest context we have seen,
       falling back to shorter contexts, then to uniform over the vocab."""
    for k in range(max_k, 0, -1):
        if len(out) >= k:
            dist = tables[k].get(tuple(out[-k:]))
            if dist:
                return dist
    return {c: 1 for c in vocab}


def generate(tables, vocab, n: int, temp: float, prompt: str | None,
             rng: random.Random, max_k: int = 1) -> str:
    out = list(prompt) if prompt else [rng.choice(vocab)]
    for _ in range(n - len(out)):
        out.append(sample(next_dist(tables, vocab, out, max_k), temp, rng))
    return "".join(out)


def char_log_prob(tables, vocab, out: list[str], max_k: int) -> float:
    """Model probability of the last char of `out`, given the chars before it."""
    dist = next_dist(tables, vocab, out[:-1], max_k)
    c = dist.get(out[-1], 0)
    return math.log(c / sum(dist.values())) if c else -math.log(len(vocab))


def generate_with_reasoning(tables, vocab, n: int, temp: float, prompt: str | None,
                            rng: random.Random, max_k: int, trials: int):
    """MUSE SPARK reasoning: best-of-N self-consistency.
       Sample several candidates, score each by average model log-probability
       over the generated part, return the most confident one with all scores."""
    best, best_score, scores = None, -1e9, []
    start = len(prompt) if prompt else 1
    for _ in range(trials):
        cand = generate(tables, vocab, n, temp, prompt, rng, max_k)
        out = list(cand)
        vals = [char_log_prob(tables, vocab, out[:i + 1], max_k) for i in range(start, len(out))]
        sc = sum(vals) / len(vals)
        scores.append(sc)
        if sc > best_score:
            best, best_score = cand, sc
    return best, scores


def main():
    ap = argparse.ArgumentParser(description="the smallest LLM on earth")
    ap.add_argument("--muse", action="store_true",
                    help="muse-spark mode: 3-char context window + best-of-N reasoning")
    ap.add_argument("--trials", type=int, default=8, help="reasoning candidates (muse mode)")
    ap.add_argument("--n", type=int, default=140, help="how many characters to generate")
    ap.add_argument("--temp", type=float, default=0.9, help="sampling temperature")
    ap.add_argument("--seed", type=int, default=None, help="random seed for reproducibility")
    ap.add_argument("--start", default=None, help="starting text (default: random char)")
    ap.add_argument("--next", default=None, help="show what the model expects after this char")
    ap.add_argument("--council", action="store_true",
                    help="run the 20-model council and let THIS model decide the winner")
    args = ap.parse_args()

    if args.council:
        import os as _os
        import subprocess as _sp
        import sys as _sys
        council = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "model_council.py")
        cmd = [_sys.executable, council, "--decider-hook", "llm",
               "--seed", str(args.seed if args.seed is not None else 1)]
        _sys.exit(_sp.call(cmd))

    max_k = 3 if args.muse else 1
    tables, vocab = train(CORPUS, max_k)
    rng = random.Random(args.seed)

    n_weights = sum(len(d) for t in tables.values() for d in t.values())
    per_k = ", ".join(
        f"{sum(len(d) for d in t.values())} context-{k} weights ({len(t)} contexts)"
        for k, t in sorted(tables.items()))
    print(f"corpus   : {len(CORPUS)} sentences, {sum(len(s) for s in CORPUS)} characters")
    print(f"tokens   : {len(vocab)} {''.join(vocab)!r}")
    print(f"weights  : {n_weights} learned transition weights [{per_k}]")
    if args.muse:
        print(f"mode     : MUSE SPARK — context window {max_k} chars (vs 1 base) "
              f"+ reasoning (best-of-{args.trials})")

    if args.next is not None:
        dist = tables[1].get((args.next,))
        if not dist:
            print(f"'{args.next}' never appears in the corpus — nothing to predict.")
            return
        total = sum(dist.values())
        print(f"\ntop 5 characters after {args.next!r}:")
        for ch, c in sorted(dist.items(), key=lambda kv: -kv[1])[:5]:
            print(f"   {ch!r:>4}  {100 * c / total:5.1f}%")
        return

    print("=" * 44)
    if args.muse:
        text, scores = generate_with_reasoning(tables, vocab, args.n, args.temp,
                                               args.start, rng, max_k, args.trials)
        print(f"reasoning: sampled {args.trials} candidates, scored each by the "
              f"model's own log-probability, chose the most confident.")
        print(f"           candidate scores: {[round(s, 2) for s in scores]}")
    else:
        text = generate(tables, vocab, args.n, args.temp, args.start, rng, max_k)
    print(text)
    print("=" * 44)


if __name__ == "__main__":
    main()
