# FoxWallet Token List

```
type Token = {
    address: string;
    name: string;
    symbol: string;
    decimals: number;
    logoURI: string;
    display?: string;
    tag?: "recommend" | "skip_coinmarket" | string;
    coingeckoID?: string;
}
```