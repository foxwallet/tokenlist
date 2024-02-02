import requests
import json
from typing import Mapping, List

CHAIN_ID_MAP = {
    "1": "ethereum",
    "10": "optimism",
    "56": "bnb",
    "137": "polygon",
    "169": "manta-pacific",
    "314": "filecoin-evm",
    "324": "zksync-era",
    "7000": "zeta-evm",
    "42161": "arbitrum",
    "42766": "zkfair",
    "80085": "bera-artio",
}

NATIVE_COIN_MAP = {
    "ethereum": "ETH",
    "optimism": "ETH",
    "bnb": "BNB",
    "polygon": "MATIC",
    "zksync-era": "ETH",
    "zeta-evm": "ZETA",
    "arbitrum": "ETH",
    "zkfair": "USDC",
    "bera-artio": "BERA",
}

def update_tokens(new_tokens: Mapping[str, List]):
    for chain, tokens in new_tokens.items():
        origin_tokens = []
        origin_addrs = set()
        try:
            with open(f"{chain}.json", "r") as reader:
                origin_tokens = json.load(reader)
            for t in origin_tokens:
                origin_addrs.add(t["address"].lower())
            new_tokens = origin_tokens
            for t in tokens:
                if t["address"].lower() in origin_addrs:
                    continue
                new_tokens.append(t)
            new_tokens = list(filter(lambda t: t.get("symbol", None) != NATIVE_COIN_MAP.get(chain, ""), new_tokens))
            with open(f"{chain}.json", "w") as writer:
                json.dump(new_tokens, writer, indent=2)
        except BaseException as e:
            print(chain, e)
            continue        

def izumi():
    data = requests.get("https://raw.githubusercontent.com/izumiFinance/izumi-tokenList/main/build/tokenList.json").json()
    result = {}
    for item in data:
        name = item["name"]
        symbol = item["symbol"]
        logoURI = item["icon"]
        contracts = item.get("contracts", {})
        for chain_id, v in contracts.items():
            chain = CHAIN_ID_MAP.get(chain_id, None)
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
    update_tokens(result)


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
    update_tokens(result)

def coreum():
    data = requests.get("https://raw.githubusercontent.com/CoreumFoundation/token-registry/master/mainnet/assets.json").json()
    
    metadatas = requests.get("https://full-node.mainnet-1.coreum.dev:1317/cosmos/bank/v1beta1/denoms_metadata").json()
    metadata_map = {}
    for item in metadatas["metadatas"]:
        metadata_map[item["base"]] = item

    result = {
        "coreum": []
    }
    for item in data.get("assets", []):
        address = item["denom"]
        meta = metadata_map.get(address)
        ibc = item.get("ibc_info")
        if not meta and ibc.get("display_name") is None:
            continue
        if address == "ucore":
            continue
        token = {
            "address": address,
            "logoURI": item["logo_URIs"]["png"],
            "name": meta["name"] if meta else ibc["display_name"],
            "symbol": meta["symbol"] if meta else ibc["display_name"],
            "decimals": meta["denom_units"][-1]["exponent"] if meta else ibc["precision"],
        }
        result["coreum"].append(token)    
    update_tokens(result)

def one_inch():
    result = {}
    for chain_id in ["1", "10", "56", "137", "42161"]:
        chain = CHAIN_ID_MAP.get(chain_id)
        if not chain:
            continue
        data = requests.get(f"https://tokens.1inch.io/v1.2/{chain_id}").json()
        for address, item in data.items():
            logoURI = item.get("logoURI")
            if not logoURI:
                continue
            token = {
                "address": address,
                "name": item["name"],
                "symbol": item["symbol"],
                "decimals": item["decimals"],
                "logoURI": logoURI,
            }
            if not chain in result:
                result[chain] = []
            result[chain].append(token)
    update_tokens(result)

def sushiswap():
    chain_map = {
        "filecoin": "filecoin-evm"
    }
    result = {}
    for c in ["filecoin", ]:
        chain = chain_map.get(c)
        if not chain:
            continue
        data = requests.get(f"https://raw.githubusercontent.com/sushiswap/list/master/lists/token-lists/default-token-list/tokens/{c}.json").json()
        for item in data:
            token = {
                "address": item["address"],
                "name": item["name"],
                "symbol": item["symbol"],
                "decimals": item["decimals"],
                "logoURI": item["logoURI"],
            }
            if chain not in result:
                result[chain] = []
            result[chain].append(token)
    update_tokens(result)

if __name__ == "__main__":
    sushiswap()