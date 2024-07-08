import os
import json
import requests
from urllib.parse import urlparse
from os.path import basename, splitext
from PIL import Image


def run():
    proxies = {
        "http": "http://127.0.0.1:7890",
        "https": "http://127.0.0.1:7890"
    }

    replace_list = [
        "https://pbs.twimg.com/", 
        "https://assets.coingecko.com", 
        "https://s2.coinmarketcap.com",
        "https://silkswap.me",
        "https://minerva.digital",
        "https://basescan.org/"
    ]

    for f in os.listdir("."):
        if not f.endswith(".json"):
            continue
        need_update = False
        with open(f, "r") as reader:
            tokens = json.load(reader)
            for index, token in enumerate(tokens):
                symbol: str = token.get("display", token["symbol"])
                symbol = symbol.replace(" ", "_")
                logoURI: str = token["logoURI"]
                need_replace = False
                for patten in replace_list:
                    if logoURI.startswith(patten):
                        need_replace = True
                        break
                if not need_replace:
                    continue
                _, suffix = splitext(basename(urlparse(logoURI).path))
                if suffix not in [".jpg", ".png", ".jpeg", ".svg"]:
                    continue
                filename = f"./img/{symbol}{suffix}"
                webpname = f"./img/{symbol}.webp"
                if not os.path.exists(webpname):
                    try:
                        print("donwloading", logoURI, "to", filename)
                        resp = requests.get(logoURI, proxies=proxies, timeout=10)
                        if resp.status_code != 200:
                            raise Exception(f"request failed {resp.status_code}")
                        with open(filename, "wb+") as writer:
                            writer.write(resp.content)
                        im = Image.open(filename)
                        im.save(webpname, "WEBP")
                        os.remove(filename)
                    except BaseException as e:
                        print(f"cannot download image for {token['address']} due to {e}")  
                        continue  
                tokens[index]["logoURI"] = f"https://raw.githubusercontent.com/foxwallet/tokenlist/main/img/{symbol}.webp"
                need_update = True
        if need_update:
            with open(f, "w") as writer:
                json.dump(tokens, writer, indent=2) 
            print("updated", f)

if __name__ == "__main__":
    run()