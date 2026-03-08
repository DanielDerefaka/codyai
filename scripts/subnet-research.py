#!/usr/bin/env python3
"""
Bittensor Subnet Intelligence Pipeline
Pulls data from Taostats API, Desearch (X/Twitter + Web), and GitHub
to produce comprehensive subnet research reports.

Usage:
  python3 subnet-research.py report <netuid>    # Full intelligence report
  python3 subnet-research.py scan               # Quick scan all subnets
  python3 subnet-research.py top [N]            # Top N most profitable (default 10)

Requires: TAOSTATS_API_KEY, DESEARCH_API_KEY in .env or environment
"""

import json
import os
import re
import sys
import time
import urllib.request
import urllib.parse
from datetime import datetime, timedelta

# ── Config ──────────────────────────────────────────────────────────────────

# Load .env from multiple locations
for env_path in [".env", os.path.expanduser("~/.openclaw/.env")]:
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, val = line.split('=', 1)
                    os.environ.setdefault(key.strip(), val.strip())

TAOSTATS_API_KEY = os.environ.get("TAOSTATS_API_KEY", "")
DESEARCH_API_KEY = os.environ.get("DESEARCH_API_KEY", "")

# Post-halving constants (Dec 12, 2025)
BLOCK_REWARD_TAO = 0.5
BLOCKS_PER_DAY = 7200
DAILY_NETWORK_EMISSION = BLOCK_REWARD_TAO * BLOCKS_PER_DAY  # 3,600 TAO

# ── Taostats API ────────────────────────────────────────────────────────────

TAOSTATS_BASE = "https://api.taostats.io"

def taostats_get(path, params=None):
    """Call Taostats API endpoint. Returns parsed JSON or None on error."""
    url = f"{TAOSTATS_BASE}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={
        "Authorization": TAOSTATS_API_KEY,
        "Accept": "application/json"
    })
    for attempt in range(3):
        try:
            fresh_req = urllib.request.Request(url, headers={
                "Authorization": TAOSTATS_API_KEY,
                "Accept": "application/json",
                "User-Agent": "Mozilla/5.0 (compatible; SubnetResearch/1.0)"
            })
            with urllib.request.urlopen(fresh_req, timeout=20) as resp:
                data = json.loads(resp.read().decode())
                time.sleep(2)  # Rate limit: ~0.5 req/sec to avoid 429
                return data
        except urllib.error.HTTPError as e:
            if e.code in (403, 429) and attempt < 2:
                wait = (attempt + 1) * 5
                print(f"  [taostats] {path} rate limited, waiting {wait}s...", file=sys.stderr)
                time.sleep(wait)
                continue
            print(f"  [taostats] {path} error: {e}", file=sys.stderr)
            return None
        except Exception as e:
            print(f"  [taostats] {path} error: {e}", file=sys.stderr)
            return None
    return None

def get_subnet_identity(netuid):
    """Get subnet name, website, GitHub, Discord, description, Twitter."""
    resp = taostats_get("/api/subnet/identity/v1", {"netuid": netuid})
    if resp and resp.get("data"):
        d = resp["data"][0]
        return {
            "subnet_name": d.get("subnet_name", ""),
            "description": d.get("description", ""),
            "summary": d.get("summary", ""),
            "website": d.get("subnet_url", "").strip(),
            "github_repo": d.get("github_repo", "").strip(),
            "discord": d.get("discord", "").strip(),
            "twitter": d.get("twitter", "").strip(),
            "contact": d.get("subnet_contact", "").strip(),
            "tags": d.get("tags", []),
        }
    return None

def get_subnet_emission(netuid):
    """Get emission data from Taostats (already accounts for halving)."""
    resp = taostats_get("/api/dtao/subnet_emission/v1", {"netuid": netuid, "per_page": 1})
    if resp and resp.get("data"):
        d = resp["data"][0]
        return {
            "block_number": d.get("block_number"),
            "timestamp": d.get("timestamp"),
            "tao_in_pool": d.get("tao_in_pool"),
            "alpha_in_pool": d.get("alpha_in_pool"),
            "alpha_rewards": d.get("alpha_rewards"),
            "symbol": d.get("symbol", ""),
        }
    return None

def get_subnet_pools(netuid):
    """Get pool data — TAO pool, alpha pool, rates."""
    resp = taostats_get("/api/dtao/subnet_emission/v1", {"netuid": netuid, "per_page": 3})
    if resp and resp.get("data") and len(resp["data"]) >= 2:
        latest = resp["data"][0]
        prev = resp["data"][1]
        tao_now = int(latest.get("tao_in_pool", 0))
        tao_prev = int(prev.get("tao_in_pool", 0))
        return {
            "tao_pool": tao_now,
            "tao_pool_tao": round(tao_now / 1e9, 2),
            "alpha_pool": int(latest.get("alpha_in_pool", 0)),
            "tao_flow": "inflow" if tao_now > tao_prev else "outflow",
            "tao_change": round((tao_now - tao_prev) / 1e9, 4),
        }
    return None

def get_subnet_info(netuid):
    """Get subnet info from subnet/latest — active miners, validators, reg cost, etc."""
    resp = taostats_get("/api/subnet/latest/v1", {"netuid": netuid})
    if resp and resp.get("data"):
        d = resp["data"][0]
        neuron_reg_rao = int(d.get("neuron_registration_cost", 0))
        return {
            "active_miners": d.get("active_miners", 0),
            "active_validators": d.get("active_validators", 0),
            "active_keys": d.get("active_keys", 0),
            "max_neurons": d.get("max_neurons", 256),
            "tempo": d.get("tempo", 360),
            "registration_cost_tao": round(neuron_reg_rao / 1e9, 6),
            "incentive_burn": d.get("incentive_burn"),
            "emission": d.get("emission"),
            "projected_emission": d.get("projected_emission"),
            "registration_allowed": d.get("registration_allowed", False),
            "pow_registration_allowed": d.get("pow_registration_allowed", False),
        }
    return None

def get_tao_price():
    """Get current TAO price in USD."""
    resp = taostats_get("/api/price/latest/v1", {"asset": "tao"})
    if resp and resp.get("data"):
        d = resp["data"][0]
        return {
            "price_usd": float(d.get("close", d.get("price", 0))),
            "market_cap": d.get("market_cap"),
            "circulating_supply": d.get("circulating_supply"),
        }
    return None

def get_metagraph_summary(netuid):
    """Get metagraph summary — miner/validator counts, emission distribution.

    Classification: incentive > 0 = miner, dividends > 0 = validator.
    Emission: uses daily_mining_alpha_as_tao / daily_validating_alpha_as_tao
    (alpha emissions only, NOT staking rewards from root network).
    """
    resp = taostats_get("/api/metagraph/latest/v1", {"netuid": netuid, "per_page": 1024})
    if not resp or not resp.get("data"):
        return None

    neurons = resp["data"]

    # Classify by incentive/dividends (NOT validator_permit — miners can have it)
    miners = [n for n in neurons if float(n.get("incentive") or 0) > 0]
    validators = [n for n in neurons if float(n.get("dividends") or 0) > 0]

    # Daily alpha emissions (subnet emission, not staking rewards)
    miner_daily_tao = []
    for m in miners:
        daily = int(m.get("daily_mining_alpha_as_tao") or 0)
        if daily > 0:
            miner_daily_tao.append(daily / 1e9)

    val_daily_tao = []
    for v in validators:
        daily = int(v.get("daily_validating_alpha_as_tao") or 0)
        if daily > 0:
            val_daily_tao.append(daily / 1e9)

    # Owner emission
    owner_daily_tao = sum(int(n.get("daily_owner_alpha_as_tao") or 0) for n in neurons) / 1e9

    # Total subnet emission = miner alpha + validator alpha + owner alpha
    total_emission = sum(miner_daily_tao) + sum(val_daily_tao) + owner_daily_tao

    result = {
        "total_neurons": len(neurons),
        "miners": len(miners),
        "validators": len(validators),
        "earning_miners": len(miner_daily_tao),
        "earning_validators": len(val_daily_tao),
        "daily_emission_tao": round(total_emission, 4),
        "miner_daily_emission_tao": round(sum(miner_daily_tao), 4),
        "validator_daily_emission_tao": round(sum(val_daily_tao), 4),
        "owner_daily_emission_tao": round(owner_daily_tao, 4),
    }

    if miner_daily_tao:
        result["avg_miner_daily_tao"] = round(sum(miner_daily_tao) / len(miner_daily_tao), 6)
        result["top_miner_daily_tao"] = round(max(miner_daily_tao), 6)
        result["bottom_miner_daily_tao"] = round(min(miner_daily_tao), 6)

    if val_daily_tao:
        result["avg_validator_daily_tao"] = round(sum(val_daily_tao) / len(val_daily_tao), 6)

    # Top 3 miners by daily earnings
    miner_earnings = []
    for m in miners:
        daily = int(m.get("daily_mining_alpha_as_tao") or 0)
        if daily > 0:
            miner_earnings.append({
                "uid": m.get("uid"),
                "daily_tao": round(daily / 1e9, 6),
                "incentive": round(float(m.get("incentive") or 0), 6),
                "hotkey": m.get("hotkey", {}).get("ss58", "")[:12] + "...",
            })
    miner_earnings.sort(key=lambda x: x["daily_tao"], reverse=True)
    result["top_3_miners"] = miner_earnings[:3]

    return result

def get_all_subnet_identities():
    """Get identities for all subnets in one call."""
    resp = taostats_get("/api/subnet/identity/v1", {"per_page": 256})
    if resp and resp.get("data"):
        return {d["netuid"]: d for d in resp["data"]}
    return {}

def get_all_subnet_emissions():
    """Get latest emission data for all subnets."""
    # Get emissions for each subnet — Taostats returns time series per netuid
    # For scan mode, we query all at once
    resp = taostats_get("/api/dtao/subnet_emission/v1", {"per_page": 256})
    if resp and resp.get("data"):
        # Group by netuid, take latest per subnet
        by_netuid = {}
        for d in resp["data"]:
            nid = d["netuid"]
            if nid not in by_netuid:
                by_netuid[nid] = d
        return by_netuid
    return {}


# ── Desearch API (X/Twitter + Web) ─────────────────────────────────────────

def desearch_x_search(query, count=15):
    """Search X/Twitter for recent posts about a subnet."""
    if not DESEARCH_API_KEY:
        return {"error": "DESEARCH_API_KEY not set"}
    try:
        from desearch_py import Desearch
        client = Desearch(api_key=DESEARCH_API_KEY)
        results = client.basic_twitter_search(
            query=query,
            sort="Latest",
            count=count
        )
        # Normalize results
        tweets = []
        if isinstance(results, list):
            for t in results:
                tweet = t if isinstance(t, dict) else (t.dict() if hasattr(t, 'dict') else t.__dict__)
                tweets.append({
                    "text": tweet.get("text", "")[:280],
                    "user": tweet.get("user", {}).get("username", "") if isinstance(tweet.get("user"), dict) else "",
                    "likes": tweet.get("like_count", 0),
                    "retweets": tweet.get("retweet_count", 0),
                    "views": tweet.get("view_count", 0),
                    "url": tweet.get("url", ""),
                    "date": tweet.get("created_at", ""),
                })
        return {"tweets": tweets, "count": len(tweets)}
    except Exception as e:
        return {"error": str(e)}

def desearch_web_search(query):
    """Web search for project info, guides, articles."""
    if not DESEARCH_API_KEY:
        return {"error": "DESEARCH_API_KEY not set"}
    try:
        from desearch_py import Desearch
        client = Desearch(api_key=DESEARCH_API_KEY)
        results = client.basic_web_search(query=query, num=10, start=0)

        def safe_dump(obj):
            if hasattr(obj, 'model_dump'):
                return obj.model_dump()
            elif hasattr(obj, 'dict'):
                return obj.dict()
            elif isinstance(obj, list):
                return [safe_dump(x) for x in obj]
            return obj

        return json.loads(json.dumps(safe_dump(results), default=str))
    except Exception as e:
        return {"error": str(e)}

def desearch_web_crawl(url):
    """Crawl a project website for content."""
    if not DESEARCH_API_KEY or not url:
        return None
    try:
        from desearch_py import Desearch
        client = Desearch(api_key=DESEARCH_API_KEY)
        content = client.web_crawl(url=url)
        if isinstance(content, str):
            return content[:5000]
        return str(content)[:5000]
    except Exception as e:
        return f"Error crawling {url}: {e}"


# ── GitHub API ──────────────────────────────────────────────────────────────

def analyze_github(repo_url):
    """Analyze a GitHub repo — stars, commits, contributors, language."""
    if not repo_url:
        return None

    # Extract owner/repo from various URL formats
    match = re.search(r'github\.com/([^/]+)/([^/\s]+)', repo_url)
    if not match:
        return {"error": f"Cannot parse GitHub URL: {repo_url}"}

    owner = match.group(1)
    repo = match.group(2).rstrip('/')
    # Remove /tree/main etc
    repo = repo.split('/')[0]

    base = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": "subnet-research"}

    result = {"owner": owner, "repo": repo, "url": f"https://github.com/{owner}/{repo}"}

    # Repo info
    try:
        req = urllib.request.Request(base, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            result["stars"] = data.get("stargazers_count", 0)
            result["forks"] = data.get("forks_count", 0)
            result["open_issues"] = data.get("open_issues_count", 0)
            result["language"] = data.get("language", "")
            result["updated_at"] = data.get("updated_at", "")
            result["created_at"] = data.get("created_at", "")
            result["description"] = data.get("description", "")
    except Exception as e:
        result["repo_error"] = str(e)

    # Recent commits
    try:
        req = urllib.request.Request(f"{base}/commits?per_page=5", headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            commits = json.loads(resp.read().decode())
            result["recent_commits"] = [
                {
                    "message": c.get("commit", {}).get("message", "").split('\n')[0][:100],
                    "date": c.get("commit", {}).get("committer", {}).get("date", ""),
                    "author": c.get("commit", {}).get("author", {}).get("name", ""),
                }
                for c in commits[:5]
            ]
            if commits:
                last_date = commits[0].get("commit", {}).get("committer", {}).get("date", "")
                if last_date:
                    result["last_commit"] = last_date
                    try:
                        last_dt = datetime.fromisoformat(last_date.replace('Z', '+00:00'))
                        days_ago = (datetime.now(last_dt.tzinfo) - last_dt).days
                        result["days_since_last_commit"] = days_ago
                    except:
                        pass
    except Exception as e:
        result["commits_error"] = str(e)

    # Contributors count
    try:
        req = urllib.request.Request(f"{base}/contributors?per_page=1&anon=true", headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            # Check Link header for total count
            link = resp.headers.get('Link', '')
            if 'last' in link:
                m = re.search(r'page=(\d+)>; rel="last"', link)
                if m:
                    result["contributors"] = int(m.group(1))
            else:
                contributors = json.loads(resp.read().decode())
                result["contributors"] = len(contributors)
    except Exception as e:
        result["contributors_error"] = str(e)

    # README — the key to understanding how to mine
    try:
        readme_url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/README.md"
        req = urllib.request.Request(readme_url, headers={"User-Agent": "subnet-research"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            readme = resp.read().decode('utf-8', errors='ignore')
            # Keep first 8000 chars — enough for setup instructions
            result["readme"] = readme[:8000]
    except:
        # Try master branch
        try:
            readme_url = f"https://raw.githubusercontent.com/{owner}/{repo}/master/README.md"
            req = urllib.request.Request(readme_url, headers={"User-Agent": "subnet-research"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                readme = resp.read().decode('utf-8', errors='ignore')
                result["readme"] = readme[:8000]
        except:
            pass

    return result


# ── Profitability Calculator ────────────────────────────────────────────────

def calculate_profitability(metagraph, tao_price_usd, reg_cost_tao, subnet_info=None):
    """Calculate mining profitability from metagraph data."""
    if not metagraph:
        return None

    result = {}
    avg_daily = metagraph.get("avg_miner_daily_tao", 0)
    earning = metagraph.get("earning_miners", 0)
    # Use subnet_info for active counts (most accurate), fall back to metagraph
    active = subnet_info.get("active_miners", 0) if subnet_info else metagraph.get("miners", 0)

    result["earning_miners"] = earning
    result["active_miners"] = active
    result["avg_daily_tao_per_miner"] = avg_daily
    result["avg_daily_usd_per_miner"] = round(avg_daily * tao_price_usd, 2) if tao_price_usd else 0
    result["top_daily_tao"] = metagraph.get("top_miner_daily_tao", 0)
    result["top_daily_usd"] = round(metagraph.get("top_miner_daily_tao", 0) * tao_price_usd, 2) if tao_price_usd else 0

    if reg_cost_tao and avg_daily > 0:
        result["reg_cost_tao"] = reg_cost_tao
        result["days_to_roi"] = round(reg_cost_tao / avg_daily, 1)

    # Competition score: lower is better (fewer miners competing for emission)
    total_emission = metagraph.get("miner_daily_emission_tao", 0)
    if active > 0 and total_emission > 0:
        result["competition_ratio"] = round(active / total_emission, 2)

    return result


# ── Report Commands ─────────────────────────────────────────────────────────

def cmd_report(netuid):
    """Full intelligence report for a single subnet."""
    print(f"Generating intelligence report for Subnet {netuid}...\n", file=sys.stderr)

    report = {"netuid": netuid, "generated_at": datetime.utcnow().isoformat() + "Z"}

    # 1. Identity
    print("  [1/8] Fetching identity...", file=sys.stderr)
    identity = get_subnet_identity(netuid)
    if identity:
        report["identity"] = identity

    subnet_name = identity.get("subnet_name", "") if identity else ""
    github_url = identity.get("github_repo", "") if identity else ""
    website_url = identity.get("website", "") if identity else ""
    twitter_handle = identity.get("twitter", "") if identity else ""

    # 2. Emission + Pools
    print("  [2/8] Fetching emission data...", file=sys.stderr)
    emission = get_subnet_emission(netuid)
    if emission:
        report["emission"] = emission

    pools = get_subnet_pools(netuid)
    if pools:
        report["pools"] = pools

    # 3. Subnet info (active miners/validators, reg cost, etc.)
    print("  [3/8] Fetching subnet info...", file=sys.stderr)
    subnet_info = get_subnet_info(netuid)
    if subnet_info:
        report["subnet_info"] = subnet_info
    reg_cost = subnet_info.get("registration_cost_tao", 0) if subnet_info else 0

    # 4. TAO price
    print("  [4/8] Fetching TAO price...", file=sys.stderr)
    price_data = get_tao_price()
    tao_price = 0
    if price_data:
        tao_price = price_data.get("price_usd", 0)
        report["tao_price_usd"] = tao_price

    # 5. Metagraph
    print("  [5/8] Fetching metagraph...", file=sys.stderr)
    metagraph = get_metagraph_summary(netuid)
    if metagraph:
        report["metagraph"] = metagraph

    # 6. Profitability
    profitability = calculate_profitability(metagraph, tao_price, reg_cost, subnet_info)
    if profitability:
        report["profitability"] = profitability

    # 7. GitHub
    print("  [6/8] Analyzing GitHub...", file=sys.stderr)
    if github_url:
        gh = analyze_github(github_url)
        if gh:
            report["github"] = gh

    # 8. X/Twitter sentiment — search for the project name specifically
    print("  [7/9] Searching X/Twitter...", file=sys.stderr)
    # Primary search: project name + subnet number
    if subnet_name:
        x_query = f"{subnet_name} bittensor"
    else:
        x_query = f"bittensor subnet {netuid}"
    x_data = desearch_x_search(x_query, count=20)
    if x_data:
        report["x_sentiment"] = x_data

    # Also get the project's own tweets if they have a Twitter handle
    if twitter_handle and twitter_handle.strip():
        print("  [7b/9] Fetching project's own tweets...", file=sys.stderr)
        try:
            from desearch_py import Desearch
            client = Desearch(api_key=DESEARCH_API_KEY)
            handle = twitter_handle.lstrip('@')
            own_tweets = client.tweets_by_user(user=handle, count=10)
            if isinstance(own_tweets, list):
                report["project_tweets"] = [
                    {
                        "text": (t.get("text", "") if isinstance(t, dict) else getattr(t, "text", ""))[:280],
                        "date": t.get("created_at", "") if isinstance(t, dict) else getattr(t, "created_at", ""),
                        "likes": t.get("like_count", 0) if isinstance(t, dict) else getattr(t, "like_count", 0),
                        "views": t.get("view_count", 0) if isinstance(t, dict) else getattr(t, "view_count", 0),
                    }
                    for t in own_tweets[:10]
                ]
        except Exception as e:
            print(f"  [desearch] project tweets error: {e}", file=sys.stderr)

    # 9. Web search — mining guides, setup instructions, reviews
    print("  [8/9] Running web search...", file=sys.stderr)
    web_query = f"bittensor {subnet_name} subnet {netuid} mining guide setup requirements"
    web_data = desearch_web_search(web_query)
    if web_data:
        report["web_research"] = web_data

    # 10. Crawl project website
    if website_url and website_url.startswith("http"):
        print("  [9/9] Crawling project website...", file=sys.stderr)
        site_content = desearch_web_crawl(website_url)
        if site_content and len(site_content.strip()) > 50:
            report["website_content"] = site_content[:5000]

    print(f"\nReport complete for SN {netuid} ({subnet_name})", file=sys.stderr)
    return report


def cmd_scan():
    """Quick scan of all subnets with identity + emission data."""
    print("Scanning all subnets via Taostats API...\n", file=sys.stderr)

    identities = get_all_subnet_identities()
    emissions = get_all_subnet_emissions()
    price_data = get_tao_price()
    tao_price = price_data.get("price_usd", 0) if price_data else 0

    subnets = []
    for netuid, ident in sorted(identities.items()):
        entry = {
            "netuid": netuid,
            "name": ident.get("subnet_name", ""),
            "description": ident.get("description", "")[:100],
            "website": ident.get("subnet_url", "").strip(),
            "github": ident.get("github_repo", "").strip(),
            "twitter": ident.get("twitter", "").strip(),
        }

        em = emissions.get(netuid)
        if em:
            entry["tao_pool"] = round(int(em.get("tao_in_pool", 0)) / 1e9, 2)
            entry["alpha_rewards"] = em.get("alpha_rewards")

        subnets.append(entry)

    print(f"Scanned {len(subnets)} subnets", file=sys.stderr)
    return {"subnets": subnets, "tao_price_usd": tao_price, "total_subnets": len(subnets)}


def cmd_top(n=10):
    """Find top N most profitable subnets to mine."""
    print(f"Finding top {n} most profitable subnets...\n", file=sys.stderr)

    identities = get_all_subnet_identities()
    price_data = get_tao_price()
    tao_price = price_data.get("price_usd", 0) if price_data else 0

    results = []
    netuids = sorted(identities.keys())

    for i, netuid in enumerate(netuids):
        if netuid == 0:
            continue  # Skip root subnet
        print(f"  [{i+1}/{len(netuids)}] Checking SN {netuid}...", file=sys.stderr)

        metagraph = get_metagraph_summary(netuid)
        if not metagraph:
            continue

        subnet_info = get_subnet_info(netuid)
        reg_cost = subnet_info.get("registration_cost_tao", 0) if subnet_info else 0
        profit = calculate_profitability(metagraph, tao_price, reg_cost, subnet_info)
        if not profit:
            continue

        ident = identities[netuid]
        entry = {
            "netuid": netuid,
            "name": ident.get("subnet_name", ""),
            "active_miners": profit.get("active_miners", 0),
            "earning_miners": profit.get("earning_miners", 0),
            "avg_daily_tao": profit.get("avg_daily_tao_per_miner", 0),
            "avg_daily_usd": profit.get("avg_daily_usd_per_miner", 0),
            "top_daily_tao": profit.get("top_daily_tao", 0),
            "top_daily_usd": profit.get("top_daily_usd", 0),
            "reg_cost_tao": reg_cost,
            "days_to_roi": profit.get("days_to_roi"),
            "total_miner_emission_tao": metagraph.get("miner_daily_emission_tao", 0),
        }
        results.append(entry)

    # Sort by avg daily TAO per miner (descending)
    results.sort(key=lambda x: x.get("avg_daily_tao", 0), reverse=True)

    top = results[:n]
    print(f"\nTop {n} subnets by avg daily TAO per miner:", file=sys.stderr)
    for i, s in enumerate(top):
        print(f"  {i+1}. SN {s['netuid']} ({s['name']}) — {s['avg_daily_tao']:.4f} TAO/day (${s['avg_daily_usd']:.2f})", file=sys.stderr)

    return {
        "top_subnets": top,
        "tao_price_usd": tao_price,
        "total_evaluated": len(results),
        "note": "Post-halving: network emits ~3,600 TAO/day (0.5 TAO/block). All figures from Taostats API."
    }


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "report" and len(sys.argv) > 2:
        netuid = int(sys.argv[2])
        result = cmd_report(netuid)
        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))

    elif cmd == "scan":
        result = cmd_scan()
        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))

    elif cmd == "top":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        result = cmd_top(n)
        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))

    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
