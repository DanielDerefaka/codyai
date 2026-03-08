# Bittensor Knowledge Base

## ⚠️ CRITICAL: Live Data Requirement

**BEFORE writing ANY subnet stats (active miners, emissions, reg cost, validators), you MUST run:**

```
python3 ~/.codyai/workspace/scripts/subnet-research.py report <netuid>
```

**The script returns accurate live data from Taostats API. Use ONLY the JSON output for numbers.**

Key fields from the script output:
- `subnet_info.active_miners` = real active miner count (NOT max_neurons, NOT active_keys)
- `subnet_info.active_validators` = real validator count
- `subnet_info.registration_cost_tao` = miner burn cost
- `metagraph.daily_emission_tao` = subnet daily emission in TAO
- `metagraph.miner_daily_emission_tao` = miner share of emission
- `metagraph.avg_miner_daily_tao` = average per-miner daily TAO
- `metagraph.top_3_miners` = top 3 miners with UID, daily_tao, incentive
- `tao_price_usd` = current TAO price

**NEVER guess, estimate, or calculate these numbers yourself. NEVER use numbers from the GitHub README or docs — they are outdated. Run the script and use its output.**

---

## How Bittensor Works (High Level)
- Bittensor is a decentralized AI network. TAO is the native token.
- The network has 64+ subnets, each running a different AI/compute task.
- Each subnet has two roles: **validators** (score work) and **miners** (do work and earn TAO).
- Validators stake TAO to gain voting weight. They send tasks to miners, score responses, and set weights.
- Miners register a hotkey on a subnet, run the subnet's specific software, and compete to produce the best output.
- Better performance = higher incentive score = more TAO emissions.
- TAO emissions are split: ~41% to miners, ~41% to validators, ~18% to subnet owners.

## Registration & Entry
- To mine, you register a hotkey on the subnet. This costs TAO (the "registration cost" or "burn cost").
- Registration cost is dynamic — it goes up when many people register, down when few do.
- Check live costs: PATH=$HOME/.local/bin:$PATH btcli subnet list --network finney (look at "Price" column)
- Each subnet has max slots (usually 256 or 360). If all slots are full, new miners must outperform existing ones or wait for deregistration.
- New miners get an "immunity period" — they can't be deregistered during this time even if they score poorly.

## How Mining Actually Works
1. **Pick a subnet** — research what it does, hardware needs, and competition level
2. **Set up a server** — VPS or local machine with the right specs
3. **Create a wallet** — coldkey (secure, offline) + hotkey (on the server)
   - btcli wallet new_coldkey --wallet.name mywallet
   - btcli wallet new_hotkey --wallet.name mywallet --hotkey.name myhotkey
4. **Fund the wallet** — transfer TAO to cover registration cost
5. **Register on the subnet** — btcli subnet register --netuid [N] --wallet.name mywallet --hotkey.name myhotkey
6. **Clone the subnet repo** — each subnet has a GitHub repo with miner code
7. **Install dependencies** — usually Python, PyTorch, sometimes specific models
8. **Run the miner** — typically: python neurons/miner.py --netuid [N] --wallet.name mywallet --hotkey.name myhotkey --subtensor.network finney
9. **Monitor performance** — check your incentive score, adjust as needed

## Hardware Requirements by Subnet Type

### GPU-Required Subnets (need NVIDIA GPU)
These subnets run neural network inference or training. Minimum: RTX 3090 / A10 (24GB VRAM). Ideal: A100 / H100.

| Type | Examples | Min GPU | Notes |
|------|----------|---------|-------|
| LLM Inference | SN1, SN4, SN64 | RTX 3090 (24GB) | Larger models need A100 (80GB) |
| Image Generation | SN5 | RTX 3090 (24GB) | Stable Diffusion, FLUX models |
| Fine-tuning | SN37 | RTX 3090+ | Training runs need VRAM |
| ML Compute | SN19 | A10+ | General ML inference |
| Audio/Speech | SN16 | RTX 3060+ | Whisper, TTS models |
| Video | SN17 | A100 | Very VRAM intensive |

**GPU VPS Providers (for mining):**
- RunPod — cheapest for A100/H100, pay per hour ($1-3/hr for A100)
- Vast.ai — marketplace model, variable pricing, often cheapest
- Lambda Cloud — A100/H100, $1.10/hr for A100
- AWS p3/p4 instances — expensive but reliable
- Hetzner — budget dedicated GPU servers in EU
- OVH — budget dedicated in EU

### CPU-Friendly Subnets (no GPU needed)
These subnets run data tasks, API calls, scraping, or lightweight compute. Can run on standard VPS.

| Type | Examples | Min Specs | Notes |
|------|----------|-----------|-------|
| Data scraping | SN13, SN3 | 4 vCPU, 8GB RAM | Network I/O heavy |
| Search/indexing | SN22 | 4 vCPU, 16GB RAM | Needs fast storage |
| Blockchain data | SN15 | 2 vCPU, 4GB RAM | Light compute |
| VPN/Networking | SN65 | 2 vCPU, 2GB RAM | Bandwidth matters |
| Storage | SN21 | 2 vCPU, 8GB RAM + disk | Storage heavy |
| Oracle/Data feeds | Various newer SNs | 2 vCPU, 4GB RAM | API-based |

**CPU VPS Providers:**
- Hetzner — best value in EU (CX31: 4 vCPU/8GB for ~$8/mo)
- Contabo — very cheap, decent specs
- DigitalOcean — reliable, $12-24/mo
- Vultr — good global coverage
- AWS Lightsail — cheap entry

### Hybrid (GPU helps but not required)
- Some subnets let you mine with CPU but you score lower
- SN22 (search) can run CPU but GPU helps with embedding models
- Check each subnet's docs — they usually specify minimum requirements

## What Makes a Subnet "Mineable" (Analysis Framework)
When Dx asks about mineable subnets, analyze these 7 factors:

1. **Registration Cost** — Lower is better for entry
   - Cheap: < 0.1 TAO
   - Moderate: 0.1 - 1 TAO
   - Expensive: > 1 TAO
   - Very expensive: > 10 TAO (top subnets)

2. **Miner Slots (k/n)** — The k/n column in btcli
   - Open: k/n < 50% (easy to get in)
   - Competitive: k/n 50-80%
   - Saturated: k/n > 90% (hard to stay, get deregistered if you score low)

3. **Emission Rate** — How much TAO flows into the subnet
   - High emission + few miners = good opportunity
   - Low emission + many miners = bad opportunity
   - Calculate: emission / number_of_miners = rough TAO per miner

4. **Hardware Cost** — What you need to run vs what you earn
   - CPU subnet on $10/mo VPS earning 0.5 TAO/day = great ROI
   - GPU subnet on $3/hr A100 earning 0.1 TAO/day = probably losing money

5. **Incentive Distribution** — Are rewards spread evenly or concentrated?
   - Run btcli subnet metagraph --netuid [N] to see per-miner incentives
   - If top 5 miners get 80% of rewards, hard to compete as newcomer
   - If rewards are spread relatively evenly, easier to earn

6. **Code Quality & Documentation** — Can you actually set up a miner?
   - Check the subnet's GitHub repo
   - Look for: clear README, miner setup guide, active commits, open issues being addressed
   - No docs / dead repo = avoid

7. **Community Activity** — Are people actually mining and getting paid?
   - Check subnet's Discord channel
   - Look for active validators, miner discussions, troubleshooting
   - Dead community = risky

## How to Research a Specific Subnet
1. Run: bash ~/.codyai/workspace/scripts/subnet-scanner.sh [netuid] — get live metagraph
2. Use Brave Search: "[subnet name] bittensor mining setup guide"
3. Find the GitHub repo: search "bittensor subnet [netuid]" or check docs.bittensor.com
4. Check incentive distribution in metagraph — are rewards concentrated or spread?
5. Calculate rough ROI: (estimated daily TAO earnings * TAO price) vs hardware cost
6. Check Discord for community activity

## Dx's Current Mining Setup
- Currently mines SN37 (fine-tuning subnet)
- Has Bittensor coldkey + hotkey configured
- VPS already running on AWS (13.63.129.188) — this is for Cody, not mining
- Dx has experience with Rust, Python, TypeScript
- Dx's hardware situation: [Ask Dx what GPUs/servers he has access to]

## Mining Profitability Quick Math
```
Daily TAO per miner ≈ (subnet_daily_emission * your_incentive_share)
Daily USD = daily_TAO * TAO_price
Daily cost = server_cost_per_day
Profit = Daily USD - Daily cost

Example:
- Subnet emits 100 TAO/day, you have 1% incentive share = 1 TAO/day
- TAO price = $400 → $400/day revenue
- A100 on RunPod = $72/day
- Profit = $328/day

But if you have 0.01% share = 0.01 TAO/day = $4/day vs $72/day cost = losing $68/day
```

## btcli Command Reference
```bash
# Always prefix with PATH=$HOME/.local/bin:$PATH

# List all subnets with key metrics
btcli subnet list --network finney

# Show specific subnet metagraph (all miners, validators, scores)
btcli subnet metagraph --netuid [N] --network finney

# Check wallet balance
btcli wallet balance --wallet.name default --network finney

# Register on a subnet
btcli subnet register --netuid [N] --wallet.name [name] --hotkey.name [name] --network finney

# Check registration cost for a subnet
btcli subnet list --network finney  # look at Price column

# Subnet info
btcli subnet info --netuid [N] --network finney
```

## Common Mining Problems & Solutions
- **"Not registered"** — Registration failed or you got deregistered. Re-register.
- **Zero incentive** — Your miner is running but scoring poorly. Check logs, update code, check if your responses match what validators expect.
- **Deregistered quickly** — You're scoring below the threshold. Improve miner performance or try a less competitive subnet.
- **High registration cost** — Wait for it to drop (costs fluctuate) or try a different subnet.
- **Miner crashes** — Check Python version, dependencies, VRAM usage. Most issues are dependency conflicts.
- **Can't connect to subtensor** — Network issue. Try: --subtensor.network finney or use a specific endpoint.

## Staking (Passive TAO Income)
If Dx doesn't want to actively mine, he can stake TAO to validators:
- Stake TAO to a validator on any subnet
- Earn a share of the validator's rewards (proportional to stake)
- Lower risk than mining (no hardware costs)
- Lower reward than mining (passive vs active)
- btcli stake add --wallet.name [name] --hotkey.name [validator_hotkey] --amount [TAO]
