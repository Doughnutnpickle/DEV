import requests
import time
from datetime import datetime, timezone

seen = set()

def get_solana_pairs():
    url = "https://api.dexscreener.com/latest/dex/search/?q=solana"
    try:
        response = requests.get(url)
        data = response.json()
        return data.get("pairs", [])
    except Exception as e:
        print("Error fetching Dexscreener data:", e)
        return []

def monitor_moonshots():
    print("Tracking relaxed Solana moonshots (≥ $500 liquidity, +50% 1h price change, launched < 30 mins)...\n")
    while True:
        pairs = get_solana_pairs()
        new_moonshots = []

        for token in pairs:
            name = token.get("baseToken", {}).get("name", "Unknown")
            symbol = token.get("baseToken", {}).get("symbol", "")
            url = token.get("url", "")
            liquidity = float(token.get("liquidity", {}).get("usd", 0))
            price_change = float(token.get("priceChange", {}).get("h1", 0))
            created_at = token.get("pairCreatedAt")

            unique_id = f"{name}-{symbol}"
            if not created_at or unique_id in seen:
                continue

            launch_time = datetime.fromtimestamp(created_at / 1000, tz=timezone.utc)
            now = datetime.now(timezone.utc)
            age = (now - launch_time).total_seconds()

            # Relaxed filters
            if liquidity >= 500 and price_change >= 50 and age < 1800:
                seen.add(unique_id)
                new_moonshots.append({
                    "name": name,
                    "symbol": symbol,
                    "liquidity": liquidity,
                    "price_change": price_change,
                    "url": url,
                    "age": int(age)
                })

        if new_moonshots:
            print(f"\n>>> New relaxed moonshots found!\n")
            for shot in new_moonshots:
                print(f"Name: {shot['name']} ({shot['symbol']})")
                print(f"Age: {shot['age']}s")
                print(f"Liquidity: ${shot['liquidity']}")
                print(f"1h Pump: +{shot['price_change']}%")
                print(f"Link: {shot['url']}\n")
        else:
            print("No relaxed moonshots...")

        time.sleep(5)

monitor_moonshots()