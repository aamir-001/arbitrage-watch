import os
import json
import itertools

# Paths to withdrawal fee files
FEE_FILE_PATHS = {
    "BinanceUS": "static-data/binanceus-wth-fees.json",
    "OKX": "static-data/okx-wth-fees.json",
    "Gate.io": "static-data/gateio-wth-fees.json",
    "Bitget": "static-data/bitget-wth-fees.json",
    "MEXC": "static-data/mexc-wth-fees.json"
}

# Load all fee data
fee_data = {}

for ex_name, path in FEE_FILE_PATHS.items():
    if os.path.exists(path):
        with open(path, 'r') as f:
            data = json.load(f)
            fee_data[ex_name] = data.get(ex_name, {})
    else:
        print(f"⚠️ File missing: {path}")

# Step 1: Build token → exchange → {network: fee} map
token_network_map = {}

for ex_name, tokens in fee_data.items():
    for token, networks in tokens.items():
        if token not in token_network_map:
            token_network_map[token] = {}
        token_network_map[token][ex_name] = {
            net: (
                0.0 if fee.strip().lower() == "free"
                else float(fee.strip().split()[0])
            )
            for net, fee in networks.items()
            if fee.strip().lower() not in ["n/a", ""]
        }

# Step 2: Compare every exchange pair per token
output = {}

exchanges = list(FEE_FILE_PATHS.keys())

for exA, exB in itertools.combinations(exchanges, 2):
    ex_pair_key = "-".join(sorted([exA, exB]))

    for token, ex_data in token_network_map.items():
        if exA in ex_data and exB in ex_data:
            networksA = ex_data[exA]
            networksB = ex_data[exB]

            shared_networks = set(networksA.keys()) & set(networksB.keys())
            if not shared_networks:
                continue

            # Find cheapest network based on withdrawal fee from exA
            cheapest_network = min(shared_networks, key=lambda n: networksA[n])
            cheapest_fee = networksA[cheapest_network]

            if ex_pair_key not in output:
                output[ex_pair_key] = {}
            output[ex_pair_key][token] = {
                "network": cheapest_network,
                "fee": str(cheapest_fee)
            }

# Save output
os.makedirs("static-data", exist_ok=True)
output_path = "static-data/common-token-networks.json"

with open(output_path, "w") as f:
    json.dump(output, f, indent=2)

print(f"\n✅ Common token networks saved to: {output_path}")
