import requests
import json
from typing import Mapping, List
import os

EVM_CHAIN_ID_MAP = {
    "1": "ethereum",
    "10": "optimism",
    "56": "bnb",
    "100": "gnosis",
    "137": "polygon",
    "169": "manta-pacific",
    "196": "xlayer",
    "250": "fantom",
    "314": "filecoin-evm",
    "324": "zksync-era",
    "463": "areon",
    "698": "matchain",
    "1100": "dym",
    "1329": "sei-evm",
    "2818": "morph",
    "4200": "merlin",
    "5165": "bahamut",
    "7000": "zeta-evm",
    "8217": "klay",
    "8453": "base",
    "42161": "arbitrum",
    "43114": "avax",
    "42766": "zkfair",
    "48900": "zircuit",
    "59144": "linea",
    "72888": "caga",
    "80085": "bera-artio",
    "81457": "blast",
    "96370": "lumoz",
    "98865": "plume",
    "168168": "zchains",
    "167000": "taiko",
    "200901": "bitlayer",
    "534352": "scroll",
}


NATIVE_COIN_MAP = {
    "arbitrum": "ETH",
    "avax": "AVAX",
    "areon": "AREA",
    "base": "ETH",
    "bnb": "BNB",
    "blast": "ETH",
    "bera-artio": "BERA",
    "coreum": "COREUM",
    "dym": "DYM",
    "ethereum": "ETH",
    "filecoin-evm": "FIL",
    "fantom": "FTM",
    "gnosis": "xDAI",
    "klay": "KLAY",
    "linea": "ETH",
    "manta-pacific": "ETH",
    "merlin": "BTC",
    "optimism": "ETH",
    "polygon": "MATIC",
    "scroll": "ETH",
    "solana": "SOL",
    "taiko": "ETH",
    "xlayer": "OKB",
    "zeta-evm": "ZETA",
    "zkfair": "USDC",
    "zklink": "ETH",
    "zksync-era": "ETH",
    "bahamut": "FTN",
    "qtum": "QTUM",
    "zchains": "ZCD",
    "ton": "TON",
    "tron": "TRX",
    "sei-evm": "SEI",
    "sei": "SEI",
    "zircuit": "ETH",
    "sui": "SUI",
    "bitlayer": "BTC",
    "aptos": "APT",
    "morph": "ETH",
    "polkadot": "DOT",
    "plume": "ETH",
    "ironfish": "IRON",
    "lumoz": "MOZ",
    "cage": "CAGA",
    "matchain": "BNB",
}

proxies = {
    "http": "http://127.0.0.1:7897",
    "https": "http://127.0.0.1:7897"
}

skip_addrs = set()
with open("./skiplist.txt", "r") as skipReader:
    for addr in skipReader:
        skip_addrs.add(addr.strip().lower())


def update_tokens(new_tokens: Mapping[str, List]):
    for chain, tokens in new_tokens.items():
        origin_tokens = []
        origin_addrs = set()
        try:
            if os.path.exists(f"{chain}.json"):
                with open(f"{chain}.json", "r") as reader:
                    origin_tokens = json.load(reader)
            else:
                origin_tokens = []
            for t in origin_tokens:
                origin_addrs.add(t["address"].lower())
            new_tokens = origin_tokens
            for t in tokens:
                if t["address"].lower() in origin_addrs:
                    continue
                if len(t["symbol"]) >= 10:
                    continue
                if t["address"].lower() in skip_addrs:
                    continue
                if not t["logoURI"]:
                    continue
                new_tokens.append(t)
            new_tokens = list(filter(lambda t: t.get("symbol", None) != NATIVE_COIN_MAP.get(chain, ""), new_tokens))
            with open(f"{chain}.json", "w+") as writer:
                json.dump(new_tokens, writer, indent=2)
        except BaseException as e:
            print(chain, e)
            continue        


def one_inch():
    print("start 1inch")
    result = {}
    for chain_id in ["1", "10", "56", "100", "137", "250", "324", "8217", "8453", "42161", "43114"]:
        chain = EVM_CHAIN_ID_MAP.get(chain_id)
        if not chain:
            continue
        print("getting chainId", chain_id)
        data = requests.get(f"https://wallet.foxnb.net/public/wrap_swap/{chain_id}/tokens", proxies=proxies, timeout=25).json()
        data = data.get("data", {}).get("tokens", {})
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


def uniswap():
    print("start uniswap")
    chain_map = {
        "arbitrum": "arbitrum",
        "mainnet": "ethereum",
        "optimism": "optimism",
        "bnb": "bnb",
        "base": "base",
        "blast": "blast",
        "polygon": "polygon",
    }
    result = {}
    for chain, unique_id in chain_map.items():
        print(chain)
        url = f"https://raw.githubusercontent.com/Uniswap/default-token-list/main/src/tokens/{chain}.json"
        data = requests.get(url, proxies=proxies, timeout=5).json()
        if unique_id not in result:
            result[unique_id] = []
        for token in data:
            del token["chainId"]
            if "extensions" in token:
                del token["extensions"]
            result[unique_id].append(token)
    update_tokens(result)


def sushiswap():
    print("start sushi")
    chain_map = {
        "filecoin": "filecoin-evm"
    }
    result = {}
    for c in ["filecoin", ]:
        chain = chain_map.get(c)
        if not chain:
            continue
        data = requests.get(f"https://raw.githubusercontent.com/sushiswap/list/master/lists/token-lists/default-token-list/tokens/{c}.json", proxies=proxies, timeout=5).json()
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


def izumi():
    print("start izumi")
    data = requests.get("https://raw.githubusercontent.com/izumiFinance/izumi-tokenList/main/build/tokenList.json", proxies=proxies, timeout=5).json()
    result = {}
    for item in data:
        name = item["name"]
        symbol = item["symbol"]
        logoURI = item["icon"]
        contracts = item.get("contracts", {})
        for chain_id, v in contracts.items():
            chain = EVM_CHAIN_ID_MAP.get(chain_id, None)
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


def xlayer():
    print("start xlayer")
    unique_id = "xlayer"
    result = {
       unique_id : []
    }
    url = "https://rpc.xlayer.tech/priapi/v1/ob/bridge/main-coins/3"
    data = requests.get(url, proxies=proxies, timeout=5).json()
    for item in data.get("data", []):
        if not item["address"]:
            continue
        chainId = item["chainId"]
        if chainId != "196":
            continue
        token = {
            "address": item["address"],
            "name": item["name"],
            "symbol": item["symbol"],
            "decimals": int(item["decimals"]),
            "logoURI": item["logoLink"],
        }
        result[unique_id].append(token)
    update_tokens(result)


def coreum():
    print("start coreum")
    data = requests.get("https://raw.githubusercontent.com/CoreumFoundation/token-registry/master/mainnet/assets.json", proxies=proxies).json()
    metadatas = requests.get("https://full-node.mainnet-1.coreum.dev:1317/cosmos/bank/v1beta1/denoms_metadata", proxies=proxies).json()
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

def silkswap():
    print("start silkswap")
    result = {
        "bahamut": []
    }
    data = requests.get("https://raw.githubusercontent.com/blockstars-tech/silk-swap/main/token-list.json", proxies=proxies).json()
    for item in data.get("tokens", []):
        if item["chainId"] != 5165 or "logoURI" not in item:
            continue
        token = {
            "address": item["address"],
            "name": item["name"],
            "symbol": item["symbol"],
            "decimals": item["decimals"],
            "logoURI": item["logoURI"],
        }
        result["bahamut"].append(token)
    update_tokens(result)

def ton_diamonds():
    print("start ton.diamonds")
    result = {
        "ton": []
    }
    # url = "https://ton.diamonds/api/v1/dex/jettons/v3?currentPage=1&open_in_browser=true"
    # headers = {
    #     "accept": "application/json, text/plain, */*",
    #     "referer": "https://ton.diamonds/dex/swap?open_in_browser=true",
    #     "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    # }
    # resp = requests.get(url, headers=headers, proxies=proxies)
    # data = resp.json()
    data = json.loads("""{"ok":true,"data":{"items":[{"jettonAddress":"EQCxE6mUtQJKFnGfaROTKOt1lZbDiiX1kCixRv7Nw2Id_sDs","name":"Tether USD","symbol":"USD₮","description":"Tether Token for Tether USD","image":"https://tether.to/images/logoCircle.png","decimals":6,"imageData":null,"totalSupply":"10000002000000","mintable":true,"adminAddress":"EQBkQP48aUEDg5Y5RRc8SxFHm_C5tNcJDlh3e9pYHC-ZmG2M","createdAt":"2024-04-19T09:06:40.953Z","verified":true,"usdPrice":"1001587306","isDefault":true,"isScam":false,"isCashback":false,"isMultihop":false,"holdersCount":596766,"tonLiquidity":"43532227546821659","volume24":"0","priceChange24":-0.00006},{"jettonAddress":"EQBlqsm144Dq6SjbPI4jjZvA1hqTIP3CvHovbIfW_t-SCALE","name":"Scaleton","symbol":"SCALE","description":null,"image":"ipfs://QmSMiXsZYMefwrTQ3P6HnDQaCpecS4EWLpgKK5EX1G8iA8","decimals":9,"imageData":null,"totalSupply":"16686615203894199","mintable":false,"adminAddress":"EQDIhshKpDtDt-uTawnlGIq-cNijBgB7jyYprczoAOXTWLwf","createdAt":"2023-10-05T13:21:42.148Z","verified":true,"usdPrice":"5354898021","isDefault":true,"isScam":false,"isCashback":true,"isMultihop":true,"holdersCount":15777,"tonLiquidity":"382434570111145","volume24":"0","priceChange24":0.03535},{"jettonAddress":"EQA2kCVNwVsil2EM2mB0SkXytxCqQjS4mttjDpnXmwG9T6bO","name":"STON","symbol":"STON","description":"STON is the utility token of the STON.fi DEX integrated into the core protocol mechanics. STON allows participation in protocol governance through long-term staking.","image":"https://static.ston.fi/logo/ston_symbol.png","decimals":9,"imageData":null,"totalSupply":"99999999876550000","mintable":true,"adminAddress":null,"createdAt":"2023-10-05T13:21:42.148Z","verified":true,"usdPrice":"11747125544","isDefault":true,"isScam":false,"isCashback":true,"isMultihop":true,"holdersCount":46249,"tonLiquidity":"326244440049532","volume24":"0","priceChange24":0.013434},{"jettonAddress":"EQDv-yr41_CZ2urg2gfegVfa44PDPjIK9F-MilEDKDUIhlwZ","name":"ANON","symbol":"ANON","description":null,"image":"https://i.ibb.co/0MZg87z/IMG-8399.png","decimals":9,"imageData":null,"totalSupply":"888888888000000000","mintable":true,"adminAddress":"EQBxeJmFSy425pf4ccxI4aa1JwqBWvDBCtRL5ZqzVdJ_MNTT","createdAt":"2024-04-04T00:00:42.091Z","verified":true,"usdPrice":"6986675","isDefault":true,"isScam":false,"isCashback":false,"isMultihop":true,"holdersCount":34668,"tonLiquidity":"216860127613189","volume24":"0","priceChange24":0.005161},{"jettonAddress":"EQCdpz6QhJtDtm2s9-krV2ygl45Pwl-KJJCV1-XrP-Xuuxoq","name":"$PUNK","symbol":"PUNK","description":"Legendary token on legendary blockchain","image":"https://punk-metaverse.fra1.digitaloceanspaces.com/logo/punk.png","decimals":9,"imageData":null,"totalSupply":"49991540499820000","mintable":true,"adminAddress":"EQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM9c","createdAt":"2023-10-05T13:21:38.259Z","verified":true,"usdPrice":"1136187676","isDefault":true,"isScam":false,"isCashback":true,"isMultihop":true,"holdersCount":39283,"tonLiquidity":"126149647821974","volume24":"0","priceChange24":0.02446},{"jettonAddress":"EQC47093oX5Xhb0xuk2lCr2RhS8rj-vul61u4W2UH5ORmG_O","name":"Gram","symbol":"GRAM","description":"The first-ever PoW jetton on TON Blockchain.","image":"https://gramcoin.org/img/icon.png","decimals":9,"imageData":null,"totalSupply":"5000000000000000000","mintable":true,"adminAddress":"EQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM9c","createdAt":"2024-01-30T02:34:44.029Z","verified":true,"usdPrice":"5714175","isDefault":true,"isScam":false,"isCashback":true,"isMultihop":true,"holdersCount":92254,"tonLiquidity":"44403626760038","volume24":"0","priceChange24":0.086423},{"jettonAddress":"EQDCJL0iQHofcBBvFBHdVG233Ri2V4kCNFgfRT-gqAd3Oc86","name":"Fanzee Token","symbol":"FNZ","description":"fanz.ee is a web3 fan engagement platform designed to help sports and entertainment organisations meaningfully connect with their fans through immersive gamification experiences","image":"https://media.fanz.ee/images/91ee938a92934656a01131c569b377b6.png","decimals":9,"imageData":null,"totalSupply":"2099999987876525259","mintable":true,"adminAddress":"EQCG5PhzGSNcphDuFb_SvB-D-Ry-aP06jQw4NATQCM_ztW3l","createdAt":"2023-10-05T13:21:38.259Z","verified":true,"usdPrice":"2970198","isDefault":true,"isScam":false,"isCashback":true,"isMultihop":true,"holdersCount":20565,"tonLiquidity":"26897510579168","volume24":"0","priceChange24":0.005675},{"jettonAddress":"EQBynBO23ywHy_CgarY9NK9FTz0yDsG82PtcbSTQgGoXwiuA","name":"Tether USD","symbol":"jUSDT","description":"Tether USD transferred from Ethereum via bridge.ton.org. Token address in Ethereum: 0xdac17f958d2ee523a2206206994597c13d831ec7.","image":"https://bridge.ton.org/token/1/0xdac17f958d2ee523a2206206994597c13d831ec7.png","decimals":6,"imageData":null,"totalSupply":"1894513665389","mintable":true,"adminAddress":null,"createdAt":"2023-10-05T13:21:38.259Z","verified":true,"usdPrice":"1005122419","isDefault":true,"isScam":false,"isCashback":true,"isMultihop":true,"holdersCount":20028,"tonLiquidity":"26458385874177","volume24":"0","priceChange24":0.00393},{"jettonAddress":"EQCBdxpECfEPH2wUxi1a6QiOkSf-5qDjUWqLCUuKtD-GLINT","name":"Glint Coin","symbol":"GLINT","description":"Glint Coin is a utility token from TON Diamonds, an NFT Marketplace on TON Blockchain. Visit ton.diamonds to learn more about all utilities of $GLINT.","image":"https://nft.ton.diamonds/glint_meta.png","decimals":9,"imageData":null,"totalSupply":"22000000000000000","mintable":true,"adminAddress":"EQDmrX8umof6ClCCoRIr5MlJfoUBSCnWj3BQkjMPIewe9wbk","createdAt":"2023-10-05T16:08:26.469Z","verified":true,"usdPrice":"124959198","isDefault":true,"isScam":false,"isCashback":true,"isMultihop":true,"holdersCount":4619,"tonLiquidity":"24765059191145","volume24":"0","priceChange24":0.024837},{"jettonAddress":"EQCIXQn940RNcOk6GzSorRSiA9WZC9xUz-6lyhl6Ap6na2sh","name":"Shards of Notcoin NFT bond","symbol":"wNOT","description":"Token 1:1 backed by Notcoin through NFT bonds locked in Shardify.app smart contract","image":"https://shardify.app/tokens/notcoin/image.png","decimals":9,"imageData":null,"totalSupply":"20000000000000000","mintable":true,"adminAddress":"EQCpjRqFu3P3ltbS3M7rusJNrtt3YJkcqB_pTVpRt5pHzY7G","createdAt":"2024-03-27T18:13:14.944Z","verified":true,"usdPrice":"13487","isDefault":true,"isScam":false,"isCashback":false,"isMultihop":true,"holdersCount":10405,"tonLiquidity":"2215820283014","volume24":"0","priceChange24":0.000816},{"jettonAddress":"EQCcLAW537KnRg_aSPrnQJoyYjOZkzqYp6FVmRUvN1crSazV","name":"Ambra","symbol":"AMBR","description":"The Whales Club Token","image":"ipfs://bafybeicsvozntp5iatwad32qgvisjxshop62erwohaqnajgsmkl77b6uh4","decimals":9,"imageData":null,"totalSupply":"9999999998364045100","mintable":true,"adminAddress":"EQCMVd9ya3yvhyhOWckBUmrHsle3eLqb_em8npZEmbbR-NOe","createdAt":"2023-10-05T13:23:20.345Z","verified":true,"usdPrice":"536210523","isDefault":true,"isScam":false,"isCashback":true,"isMultihop":true,"holdersCount":2024,"tonLiquidity":"1546865985577","volume24":"0","priceChange24":0.036812},{"jettonAddress":"EQCM3B12QK1e4yZSf8GtBRT0aLMNyEsBc_DhVfRRtOEffLez","name":"Proxy TON","symbol":"pTON","description":"Proxy contract for TON","image":"https://static.ston.fi/logo/ton_symbol.png","decimals":9,"imageData":null,"totalSupply":"0","mintable":true,"adminAddress":null,"createdAt":"2023-10-05T13:21:38.259Z","verified":true,"usdPrice":"6764300000","isDefault":true,"isScam":false,"isCashback":true,"isMultihop":true,"holdersCount":45,"tonLiquidity":"0","volume24":"0","priceChange24":0},{"jettonAddress":"EQAvlWFDxGF2lXm67y4yzC17wYKD9A0guwPkMs1gOsM__NOT","name":"Notcoin","symbol":"NOT","description":"Probably nothing","image":"https://cdn.joincommunity.xyz/clicker/not_logo.png","decimals":9,"imageData":null,"totalSupply":"102719221714000000000","mintable":true,"adminAddress":"EQAQQTyWQnLTmerS0GWQYrFYtLogGuXAW_kG5gw-50RVpJXb","createdAt":"2024-05-16T05:39:48.991Z","verified":true,"usdPrice":"13915354","isDefault":false,"isScam":false,"isCashback":false,"isMultihop":false,"holdersCount":2411216,"tonLiquidity":"705647084087769","volume24":"0","priceChange24":0.019085},{"jettonAddress":"EQAQXlWJvGbbFfE8F3oS8s87lIgdovS455IsWFaRdmJetTon","name":"JetTon","symbol":"JETTON","description":"JetTon.Games Platform Token","image":"https://raw.githubusercontent.com/JetTon-Bot/JetTon/main/jetton-256.png","decimals":9,"imageData":null,"totalSupply":"100000000000000000","mintable":false,"adminAddress":"EQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM9c","createdAt":"2023-10-05T13:22:08.943Z","verified":true,"usdPrice":"1937126836","isDefault":false,"isScam":false,"isCashback":true,"isMultihop":true,"holdersCount":56210,"tonLiquidity":"355009567314226","volume24":"0","priceChange24":0.00853},{"jettonAddress":"EQCJbp0kBpPwPoBG-U5C-cWfP_jnksvotGfArPF50Q9Qiv9h","name":"Ton Raffles Token","symbol":"RAFF","description":"$RAFF is a unique utility token, the centerpiece of tonraffles.app ecosystem.","image":"https://tonraffles.store/raffjetton/jetton.svg","decimals":9,"imageData":null,"totalSupply":"20000000000000000","mintable":true,"adminAddress":"EQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM9c","createdAt":"2023-12-12T16:40:46.538Z","verified":true,"usdPrice":"365290803","isDefault":false,"isScam":false,"isCashback":true,"isMultihop":true,"holdersCount":148578,"tonLiquidity":"168456209525544","volume24":"0","priceChange24":0.023602}],"pinned":[],"total":29734,"currentPage":1,"lastPage":1983}}""")
    for item in data.get("data", {}).get("items", []):
        if not item["verified"]:
            continue
        token = {
            "address": item["jettonAddress"],
            "name": item["name"],
            "symbol": item["symbol"],
            "decimals": item["decimals"],
            "logoURI": item["image"],
            "type": "JETTON"
        }
        result["ton"].append(token)
    update_tokens(result)    


def dragonswap():
    print("start dragonswap")
    result = {
        "sei-evm": []
    }
    url = "https://raw.githubusercontent.com/dragonswap-app/assets/main/tokenlist-sei-mainnet.json"
    resp = requests.get(url, proxies=proxies)
    data = resp.json()
    for item in data.get("tokens", []):
        token = {
            "address": item["address"],
            "name": item["name"],
            "symbol": item["symbol"],
            "decimals": item["decimals"],
            "logoURI": f"https://raw.githubusercontent.com/dragonswap-app/assets/main/logos/{item['address']}/logo.png",
        }
        result["sei-evm"].append(token)
    update_tokens(result)    

def sui_cetus():
    print("start sui_cetus")
    unique_id = "sui"
    result = {
       unique_id : []
    }
    url = "https://api-sui.cetus.zone/v2/sui/coins_info"
    data = requests.get(url, proxies=proxies, timeout=5).json()
    for item in data.get("data", {}).get("list", []):
        if not item["is_trusted"]:
            continue
        token = {
            "address": item["coin_type"],
            "name": item["name"],
            "symbol": item["symbol"],
            "decimals": int(item["decimals"]),
            "logoURI": item["logo_url"],
            "type": "SUICoin",
        }
        result[unique_id].append(token)
    update_tokens(result)
    

def jupiter():
    print("start jupiter")
    unique_id = "solana"
    result = {
       unique_id : []
    }
    url = "https://tokens.jup.ag/tokens?tags=verified"
    data = requests.get(url, proxies=proxies, timeout=5).json()
    for item in data:
        if not item["extensions"]:
            continue
        token = {
            "address": item["address"],
            "name": item["name"],
            "symbol": item["symbol"],
            "decimals": int(item["decimals"]),
            "logoURI": item["logoURI"],
            "type": "SPL",
        }
        result[unique_id].append(token)
    update_tokens(result)
    
def panro():
    print("start panro")
    unique_id = "aptos"
    result = {
       unique_id : []
    }
    url = "https://raw.githubusercontent.com/PanoraExchange/Aptos-Tokens/refs/heads/main/token-list.json"
    data = requests.get(url, proxies=proxies, timeout=5).json()
    for item in data:
        if item["chainId"] != 1:
            continue
        tags = item.get("panoraTags", [])
        if "Verified" not in tags:
            continue
        v1Addr = item.get("tokenAddress", "")
        if v1Addr and len(v1Addr) > 10:
            token = {
                "address": v1Addr,
                "name": item["name"],
                "symbol": item["symbol"],
                "decimals": int(item["decimals"]),
                "logoURI": item["logoUrl"],
                "type": "AptosCoin",
            }
            result[unique_id].append(token)
        v2Addr = item.get("faAddress", "")
        if v2Addr and len(v2Addr) > 10:
            token = {
                "address": v2Addr,
                "name": item["name"],
                "symbol": item["symbol"],
                "decimals": int(item["decimals"]),
                "logoURI": item["logoUrl"],
                "type": "AptosFA",
            }
            result[unique_id].append(token)
    update_tokens(result)


def stellaswap():
    print("start stellaswap")
    result = {
        "polkadot": []
    }
    url = "https://raw.githubusercontent.com/stellaswap/assets/refs/heads/main/tokenlist.json"
    resp = requests.get(url, proxies=proxies)
    data = resp.json()
    for item in data.get("tokens", []):
        token = {
            "address": item["address"],
            "name": item["name"],
            "symbol": item["symbol"],
            "decimals": item["decimals"],
            "logoURI": f"https://raw.githubusercontent.com/stellaswap/assets/main/tokenlist/{item['address']}/logo.png",
        }
        result["polkadot"].append(token)
    update_tokens(result)    

def ironfish():
    print("start ironfish")
    result = {
        "ironfish": []
    }
    url = "https://raw.githubusercontent.com/iron-fish/verified-assets/refs/heads/main/mainnet.json"
    resp = requests.get(url, proxies=proxies)
    data = resp.json()
    for item in data.get("assets", []):
        token = {
            "address": item["identifier"],
            "name": item["symbol"],
            "symbol": item["symbol"],
            "decimals": item["decimals"],
            "logoURI": item["logoURI"],
        }
        result["ironfish"].append(token)
    update_tokens(result)    

if __name__ == "__main__":
    # one_inch()
    # uniswap()
    # sushiswap()
    # izumi()
    # xlayer()
    # coreum()
    # silkswap()
    # ton_diamonds()
    # dragonswap()
    # sui_cetus()
    jupiter()
    panro()
    stellaswap()
    ironfish()