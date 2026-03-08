---
name: bittensor-research
description: Deep Bittensor subnet research — pulls live data from Taostats, Desearch, and GitHub
user-invocable: true
---

# Bittensor Subnet Research

When Dx asks about Bittensor subnets, mining, staking, or TAO:

## Tools

Run the subnet research script at `~/.openclaw/workspace/scripts/subnet-research.py`:

- **Full report on a subnet**: `python3 ~/.openclaw/workspace/scripts/subnet-research.py report <netuid>`
- **Quick scan all subnets**: `python3 ~/.openclaw/workspace/scripts/subnet-research.py scan`
- **Top N most profitable**: `python3 ~/.openclaw/workspace/scripts/subnet-research.py top <N>`

Also read `~/.openclaw/workspace/reference/BITTENSOR.md` for the knowledge base and analysis framework.

## How to Present Data

The script outputs JSON. You MUST use the actual values from the JSON — never calculate your own numbers. Here are the correct fields:

### Key metrics to show (from `subnet_info`):
- `active_miners` — the REAL active miner count. DO NOT use `total_neurons`, `active_keys`, or `max_neurons`
- `active_validators` — real active validator count
- `registration_cost_tao` — miner registration (burn) cost
- `max_neurons` — total UID slots

### Key metrics to show (from `metagraph`):
- `daily_emission_tao` — total subnet emission per day in TAO
- `miner_daily_emission_tao` — total miner emission per day
- `avg_miner_daily_tao` — average per-miner daily earnings
- `top_3_miners` — top 3 miners with their UID, daily_tao earnings, and incentive score

### From `profitability`:
- `avg_daily_tao_per_miner` and `avg_daily_usd_per_miner`
- `top_daily_tao` and `top_daily_usd`
- `days_to_roi` (if registration costs anything)

### DO NOT show these (not useful to Dx):
- `emission` per block (raw number, confusing)
- `projected_emission` (internal fraction)
- EMA TAO inflow (too technical, not actionable)
- `tao_pool` raw rao values
- `alpha_pool`, `alpha_rewards`

## Report Structure

When presenting a subnet report, use this structure:

1. **What They Do** — plain English, what the subnet rewards miners for
2. **How Mining Works** — step-by-step from the GitHub README (the script fetches it)
3. **Live Stats Table** — use ONLY these fields:

| Metric | Value |
|--------|-------|
| Active Miners | `subnet_info.active_miners` |
| Active Validators | `subnet_info.active_validators` |
| Daily Emission | `metagraph.daily_emission_tao` TAO |
| Miner Emission/Day | `metagraph.miner_daily_emission_tao` TAO |
| Avg Miner/Day | `metagraph.avg_miner_daily_tao` TAO ($X) |
| Reg Cost | `subnet_info.registration_cost_tao` TAO |
| TAO Price | from `tao_price_usd` |

4. **Top 3 Miners** — show from `metagraph.top_3_miners`:

| Rank | UID | Daily TAO | Incentive |
|------|-----|-----------|-----------|
| 1 | uid | daily_tao | incentive |

5. **Is It Profitable?** — honest assessment using real numbers
6. **What People Say** — from X/Twitter data and Discord
7. **Cody's Take** — specific recommendation for Dx

## Important Rules

- NEVER make up numbers. Every metric must come from the script JSON output
- The `active_miners` from `subnet_info` is the ONLY correct active miner count
- Do NOT confuse `max_neurons` (256) or `active_keys` (256) with active miners
- Post-halving: network emits ~3,600 TAO/day total (0.5 TAO/block since Dec 12 2025)
- Always show TAO amounts AND USD equivalent using `tao_price_usd`
