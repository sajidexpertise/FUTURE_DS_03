# Marketing Funnel & Conversion Performance — analysis

**Data:** deterministic simulation for training. Figures describe the synthetic dataset, not real customers or verified campaign results.

April 2024: **110,364** impressions → **33,855** clicks → **12,789** leads → **1,868** qualified leads → **716** customers. Overall conversion: **0.65%**.

## Stage losses

| From → To | Lost | Drop-off |
|---|---:|---:|
| Impressions → Clicks | 76,509 | 69.3% |
| Clicks → Leads | 21,066 | 62.2% |
| Leads → Qualified Leads | 10,921 | 85.4% |
| Qualified Leads → Customers | 1,152 | 61.7% |

Largest absolute loss: **Impressions → Clicks**, losing **76,509**. This is a volume comparison; examine the rates as well.

## Channel performance

| Source | Impressions | Customers | Conversion |
|---|---:|---:|---:|
| Paid Search | 32,110 | 302 | 0.94% |
| Organic Search | 22,889 | 156 | 0.68% |
| Email | 9,753 | 140 | 1.44% |
| Paid Social | 27,315 | 81 | 0.30% |
| Display | 18,297 | 37 | 0.20% |

## Suggested follow-up experiments

1. Test alternative creative and audience segments at the first stage; compare click-through rate and downstream customers before increasing spend.
2. Audit landing page speed, message and lead-form friction with an A/B test; compare qualified leads and customers, not clicks alone.
3. Test follow-up timing and lead qualification rules, while checking whether any changes affect lead quality.

**Caution:** These are hypotheses to test. Observed funnel counts cannot establish that a specific intervention caused a change. No revenue or ROI claims are made.
