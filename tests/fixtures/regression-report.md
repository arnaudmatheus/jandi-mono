# Jandí Mono: regression check

Each family against its baseline. Fails if a confusable pair is more than 0.01 worse (similarity; lower is easier to tell apart).

| Family | Confusability 12 / 15 / 20 px | Spacing CV | Sharpness 12 px | Pairs worse |
|---|---|---|---|---|
| Test | 0.868 → 0.881 / 0.868 → 0.868 / 0.868 → 0.868 | 0.2 → 0.2 | 0.16 → 0.16 | `t/r` 12 px +0.025 |
| New | no baseline (new family) | | | skipped |

**Result: FAIL**, 1 pair(s) worse.
