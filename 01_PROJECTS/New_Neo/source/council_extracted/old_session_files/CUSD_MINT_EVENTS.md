# CUSD mint trail (why 120 became 136)

Council USD points are **simulated**, not redeemable dollars.

Canonical source: `usd_ledger.json` `events` where `kind=mint`.

| Session | Places paid | Session total | Running global |
|---:|---|---:|---:|
| 3–8 | early 1-USD-era / mixed | 6 | 6 |
| 9–15 | 10+5+1 each | 7×16 = 112 | 118? wait computed live |

Live invariant (verified in tests):

```
sum(event.usd for mint events) == global_minted == people_minted_sum
```

As of session 18: **36 mint events, sum 136, global_minted 136**.

The jump 120 → 136 is **one council session** paying prize table 10+5+1 = 16 points (session 18).  
120 was session 17 after the same 16-point mint on top of 104.

Every mint event has `t`, `session`, `key`, `usd`, `item`, `place`.
