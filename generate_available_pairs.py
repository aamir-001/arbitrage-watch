# generate_available_pairs.py

import ccxt
import json
import os

# Constants
BASE_TOKENS = ["USDT", "USDC", "BTC", "ETH", "BNB", "SOL"]
EXCHANGE_CLASSES = {
    "BinanceUS": ccxt.binanceus(),
    "OKX": ccxt.okx(),
    "Gate.io": ccxt.gateio(),
    "Bitget": ccxt.bitget(),
    "MEXC": ccxt.mexc(),
}

# Load token list from JSON file
with open('static-data/top-tokens-by-volume.json', 'r') as f:
    top_tokens = json.load(f)
    token_symbols = [t['symbol'].upper() for t in top_tokens]  # Make sure all are uppercase

# Prepare output
available_pairs = {}

# Process each exchange
for name, exchange in EXCHANGE_CLASSES.items():
    print(f"\n🔍 Loading markets for {name}...")
    try:
        exchange.load_markets()
    except Exception as e:
        print(f"❌ Failed to load markets for {name}: {e}")
        continue

    pairs = []

    for token in token_symbols:
        for base in BASE_TOKENS:
            symbol = f"{token}/{base}"
            if symbol in exchange.markets:
                pairs.append(symbol)

    available_pairs[name] = pairs
    print(f"✅ {name}: {len(pairs)} valid pairs found")

# Save to JSON
os.makedirs("static-data", exist_ok=True)
with open("static-data/available-token-pairs.json", "w") as f:
    json.dump(available_pairs, f, indent=2)

print("\n✅ All done! Pairs saved to static-data/available-token-pairs.json")
