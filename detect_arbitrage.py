import json
import asyncio
import ccxt.async_support as ccxt
import time

EXCHANGES = {
    'BinanceUS': ccxt.binanceus(),
    'OKX': ccxt.okx(),
    'Gate.io': ccxt.gateio(),
    'Bitget': ccxt.bitget(),
    'MEXC': ccxt.mexc()
}

BASE_TOKENS = ["USDT", "USDC", "BTC", "ETH", "BNB", "SOL"]

with open("static-data/common-token-networks.json") as f:
    common_token_networks = json.load(f)

async def fetch_price(exchange, symbol):
    try:
        ticker = await exchange.fetch_ticker(symbol)
        return symbol, ticker['ask'], ticker['bid']
    except Exception:
        return symbol, None, None

async def process_exchange_pair(ex1_name, ex2_name, token_data, results):
    ex1 = EXCHANGES[ex1_name]
    ex2 = EXCHANGES[ex2_name]

    for token, info in token_data.items():
        base = info.get("base", "USDT")  # optional: allow base override
        symbol = f"{token}/{base}"
        try:
            # Fetch prices concurrently
            s1, s2 = await asyncio.gather(
                fetch_price(ex1, symbol),
                fetch_price(ex2, symbol)
            )
            _, ask, _ = s1 if ex1_name < ex2_name else s2
            _, _, bid = s2 if ex1_name < ex2_name else s1

            if ask is None or bid is None:
                continue

            fee = float(info["fee"])
            net_cost = ask + fee
            if net_cost < bid:
                results.append({
                    "token": token,
                    "base": base,
                    "buy_from": ex1_name,
                    "sell_to": ex2_name,
                    "buy_price": ask,
                    "sell_price": bid,
                    "network": info["network"],
                    "withdraw_fee": fee,
                    "profit": round(bid - net_cost, 6),
                    "roi": round((bid - net_cost) / ask * 100, 3)
                })

        except Exception:
            continue

async def main():
    start = time.time()
    results = []

    tasks = []
    for pair, token_map in common_token_networks.items():
        ex1_name, ex2_name = pair.split("-")
        tasks.append(process_exchange_pair(ex1_name, ex2_name, token_map, results))

    await asyncio.gather(*tasks)

    for r in results:
        print(f"\n💰 Arbitrage found for {r['token']}/{r['base']}")
        print(f"  Buy from {r['buy_from']} at {r['buy_price']}")
        print(f"  Sell to   {r['sell_to']} at {r['sell_price']}")
        print(f"  Network: {r['network']}, Withdrawal fee: {r['withdraw_fee']}")
        print(f"  ➤ Profit per unit: {r['profit']}")
        print(f"\n  ROI: {r['roi']}%")
        print("-" * 60)

    print(f"\n⏱️ Total detection time: {round(time.time() - start, 2)} seconds")

    # Close exchange connections
    await asyncio.gather(*[ex.close() for ex in EXCHANGES.values()])

if __name__ == "__main__":
    asyncio.run(main())
