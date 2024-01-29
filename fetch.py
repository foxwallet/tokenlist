import requests
import json

CHAIN_ID_MAP = {
    "1": "ethereum",
    "10": "optimism",
    "56": "bnb",
    "137": "polygon",
    "169": "manta-pacific",
    "324": "zksync-era",
    "42161": "arbitrum",
    "42766": "zkfair",
    "80085": "bera-artio",
}

def izumi():
    data = requests.get("https://raw.githubusercontent.com/izumiFinance/izumi-tokenList/main/build/tokenList.json").json()
    result = {}
    for item in data:
        name = item["name"]
        symbol = item["symbol"]
        logoURI = item["icon"]
        contracts = item.get("contracts", {})
        for k, v in contracts.items():
            chain = CHAIN_ID_MAP.get(k, None)
            if chain is None:
                continue
            address = v["address"]
            decimals = v["decimal"]
            token = {
                "address": address,
                "name": name,
                "symbol": symbol,
                "decimals": decimals,
                "logoURI": logoURI,
            }
            if not chain in result:
                result[chain] = []
            result[chain].append(token)

    for chain, tokens in result.items():
        origin_tokens = []
        origin_addrs = set()
        with open(f"{chain}.json", "r") as reader:
            origin_tokens = json.load(reader)
        for t in origin_tokens:
            origin_addrs.add(t["address"].lower())
        new_tokens = origin_tokens
        for t in tokens:
            if t["address"].lower() in origin_addrs:
                continue
            new_tokens.append(t)
        with open(f"{chain}.json", "w") as writer:
            json.dump(new_tokens, writer, indent=2)


def bera_artio():
    data = requests.get("https://raw.githubusercontent.com/berachain/default-token-list/main/src/tokens/testnet/defaultTokenList.json").json()
    result = {
        "bera-artio": []
    }
    for item in data.get("tokens", []):
        token = {
            "address": item["address"],
            "name": item["name"],
            "symbol": item["symbol"],
            "decimals": item["decimals"],
            "logoURI": item["logoURI"],
        }
        result["bera-artio"].append(token)    
    
    for chain, tokens in result.items():
        origin_tokens = []
        origin_addrs = set()
        with open(f"{chain}.json", "r") as reader:
            origin_tokens = json.load(reader)
        for t in origin_tokens:
            origin_addrs.add(t["address"].lower())
        new_tokens = origin_tokens
        for t in tokens:
            if t["address"].lower() in origin_addrs:
                continue
            new_tokens.append(t)
        with open(f"{chain}.json", "w") as writer:
            json.dump(new_tokens, writer, indent=2)


if __name__ == "__main__":
    bera_artio()