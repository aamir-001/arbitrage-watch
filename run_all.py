import subprocess

scripts = [
    "fetch-top-tokens-by-volume.py",
    "binanceus-wth-fees.py",
    "bitget-wth-fees.py",
    "gateio-wth-fees.py",
    "mexc-wth-fees.py",
    "okx-wth-fees.py",
    "generate_available_pairs.py",
    "generate_common_token_networks.py",
]

print("🚀 Starting pipeline...")

for script in scripts:
    print(f"\n▶️ Running: {script}")
    result = subprocess.run(["python", f"scrappers/{script}" if "wth-fees" in script or "fetch-top" in script else script])
    if result.returncode != 0:
        print(f"❌ Failed at: {script}")
        break

print("\n✅ All scripts executed (if no errors above). You can now run detect_arbitrage.py.")
