# FoxWallet Token List

```
type Token = {
    address: string;
    name: string;
    symbol: string;
    decimals: number;
    logoURI: string;
    display?: string; 
    tag?: "recommend" | "default";
    type?: "ERC20"(default) | "SPL" | "BRC20" | "QRC20" | "QBRC20" | "JETTON" | "TRC20" | "SUICoin";
    priceSource?: "static:{value}"  | "cmc:{ID}" | "coingecko" | "1inch" | "lifi";
}
```