## Disclaimer

## Tested QRs

| QR Content                                    | Blockstream Jade |
| --------------------------------------------- | ---------------- |
| Bytes Entropy (Compact SeedQR)                | ✅                |
| BIP39 Seedphrase                              |                  |
| BIP39 Seedphrase Shorted (4 letters per word) |                  |
| BIP39 Decimal Indexes                         |                  |
| BIP39 Binary Indexes                          |                  |
| BIP39 Seed                                    |                  |
| Hexadecimal Entropy                           |                  |
| Decimal Integer Entropy                       |                  |
| Master Private Key (xprv)                     |                  |
| Binary String without checksum                |                  |



# BIP85
Usage:

This will generate the first {qty} child bip85 seedphrases for the indexes in qty argument:
```
> python -m seedqr bip85 "some mnemonic twelve words long seed phrase for bip39 is fine right" --qty 10
```

This will generate a specific bip85 child index.
```
> python -m seedqr bip85 "some mnemonic twelve words long seed phrase for bip39 is fine right" --index 6
```