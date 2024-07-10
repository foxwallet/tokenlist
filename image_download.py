import os
import json
import requests
import re
from urllib.parse import urlparse
from os.path import basename, splitext
from PIL import Image


def run():
    proxies = {
        "http": "http://127.0.0.1:7890",
        "https": "http://127.0.0.1:7890"
    }

    replace_list = [
        r"^https://pbs\.twimg\.com", 
        r"^https://assets\.coingecko\.com", 
        r"^https://s2\.coinmarketcap\.com",
        r"^https://silkswap\.me",
        r"^https://minerva\.digital",
        r"^https://basescan\.org",
        r"^https://img\.cryptorank.io",
        r"^https://img\.cryptorank.io",
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
                    if re.search(patten, logoURI):
                        need_replace = True
                        break
                if not need_replace:
                    continue
                if "assets.coingecko.com" in logoURI:
                    logoURI = logoURI.replace("/standard/", "/large/")
                _, suffix = splitext(basename(urlparse(logoURI).path))
                if suffix not in [".jpg", ".png", ".jpeg", ".webp"]:
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