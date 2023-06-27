"""
- All indexes start on zero.
"""
import hashlib
import re
import unicodedata
from textwrap import wrap
from typing import Any, Union

import qrcode
from bip85 import app as bip85
from mnemonic import Mnemonic
from pycoin.symbols.btc import network as BTC

language = "english"
mn = Mnemonic(language)


def _bip32_master_seed_to_xprv(bip32_master_seed: bytes):
    if len(bip32_master_seed) < 16 or len(bip32_master_seed) > 64:
        raise ValueError("BIP32 master seed must be between 128 and 512 bits")
    xprv = BTC.keys.bip32_seed(bip32_master_seed).hwif(as_private=True)
    return xprv


def generate_mnemonic(strenght: int):
    return mn.generate(strength=strenght)


def from_binary_indexes_to_mnemonic(indexes: str):
    list_bin = wrap(indexes, 11)
    mnemonic = " ".join([mn.wordlist[int(index, 2)] for index in list_bin])
    return mnemonic


def from_decimal_index_to_mnemonic(indexes: str, init: int = 0):
    list_ndxs = wrap(indexes, 4)
    mnemonic = " ".join([mn.wordlist[int(index) + init] for index in list_ndxs])
    return mnemonic


def from_short_to_mnemonic(short: str) -> str:
    full = mn.expand(short)
    if mn.check(full):
        return full
    else:
        raise ValueError("Something's wrong with your shorted seedphrase")


def from_mnemonic_to_short(mnemonic: str):
    return " ".join([word[0:4] for word in mnemonic.split()])


def from_mnemonic_to_index(mnemonic: str, binary: bool = False) -> list:
    wordlist = mn.wordlist
    mnemonic_list = mnemonic.split()
    indexes = [wordlist.index(word) for word in mnemonic_list]
    if binary:
        indexes = [f"{int(bin(index)[2:]):011}" for index in indexes]
    else:
        indexes = [f"{i:04}" for i in indexes]
    return indexes


def from_mnemonic_to_entropy(mnemonic: str):
    entropy = mn.to_entropy(mnemonic)
    return entropy.hex()


def from_entropy_to_bytes(entropy: str):
    return bytes.fromhex(entropy)


def from_entropy_to_mnemonic(entropy: str):
    entropy = from_entropy_to_bytes(entropy)
    return mn.to_mnemonic(entropy)


def process_entropy(entropy):
    mnemonic = from_entropy_to_mnemonic(entropy)
    return {
        "bytes": from_entropy_to_bytes(entropy),
        "entropy": entropy,
        "index": {
            "decimal": from_mnemonic_to_index(mnemonic),
            "binary": from_mnemonic_to_index(mnemonic, binary=True),
        },
        "mnemonic": mnemonic,
        "short": from_mnemonic_to_short(mnemonic),
    }


def from_mnemonic_to_bip85(mnemonic, length, index, passphrase=""):
    xprv = _bip32_master_seed_to_xprv(mn.to_seed(mnemonic, passphrase=passphrase))
    return bip85.bip39(xprv, language, length, index)


def make_qr(data: Any, hide: bool = False, save: Union[bool, str] = False) -> None:
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        border=8,
    )
    qr.add_data(data)
    qr.make()
    if not hide:
        qr.print_tty(out=None)
    if save:
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(f"output/{save}.png")


# DEPRECATED. Left for near future reference.
def manual_process_entropy(entropy: str) -> dict:
    entropy_bits = len(entropy) * 4
    entropy_bytes = bytes.fromhex(entropy)
    entropy_int = int.from_bytes(entropy_bytes, byteorder="big")
    sha256_entropy_bytes = hashlib.sha256(entropy_bytes).digest()
    sha256_entropy_int = int.from_bytes(sha256_entropy_bytes, "big")
    checksum_bit_length = int(entropy_bits / 32)
    checksum = bin(sha256_entropy_int)[2:].zfill(256)[:checksum_bit_length]
    entropy_checksum = bin(entropy_int)[2:] + checksum
    entropy_checksum = entropy_checksum.zfill(entropy_bits + checksum_bit_length)
    bin_indexes = re.findall("." * 11, entropy_checksum)
    bin_string = "".join([i for i in bin_indexes])
    bitstream_wo_checksum = bin_string[: (len(bin_string) // 32) * -1]
    indexes = [int(index, 2) for index in bin_indexes]
    zero_padded_indexes = "".join([f"{index:04}" for index in indexes])
    mnemonic_list = [mn.wordlist[index] for index in indexes]
    mnemonic_sentence = unicodedata.normalize("NFKD", " ".join(mnemonic_list))
    short_mnemonic = " ".join([n[0:4] for n in mnemonic_list])
    return {}
