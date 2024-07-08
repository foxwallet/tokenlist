# FoxWallet Token List

```
type Token = {
    address: string;
    name: string;
    symbol: string;
    decimals: number;
    logoURI: string;
    display?: string;
    tag?: "recommend" | "skip_coinmarket" | "default";
    coingeckoID?: string;
    cmcID?: string;
    type?: "ERC20"(default) | "SPL" | "BRC20" | "QBRC20"
}
```