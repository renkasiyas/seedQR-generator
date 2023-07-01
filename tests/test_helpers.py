from datatest import bip39_12words, bip39_24words, bip85, bip85_indexes

from seedqr.helpers import (from_binary_indexes_to_mnemonic,
                            from_entropy_to_mnemonic, from_mnemonic_to_bip85,
                            from_mnemonic_to_entropy, from_mnemonic_to_short,
                            from_short_to_mnemonic, generate_mnemonic, mn)


def test_generate_mnemonic():
    for s in [128, 160, 192, 224, 256]:
        assert type(generate_mnemonic(s)) == str
        assert len(generate_mnemonic(s).split()) == s / 32 * 3
        assert mn.check(generate_mnemonic(s))


def test_from_binary_indexes_to_mnemonic():
    for i in bip39_12words:
        assert from_binary_indexes_to_mnemonic(i["binary"]) == i["mnemonic"]
    for i in bip39_24words:
        assert from_binary_indexes_to_mnemonic(i["binary"]) == i["mnemonic"]


def test_from_short_to_mnemonic():
    for i in bip39_12words:
        assert from_short_to_mnemonic(i["short"]) == i["mnemonic"]
    for i in bip39_24words:
        assert from_short_to_mnemonic(i["short"]) == i["mnemonic"]


def test_from_mnemonic_to_short():
    for i in bip39_12words:
        assert from_mnemonic_to_short(i["mnemonic"]) == i["short"]
    for i in bip39_24words:
        assert from_mnemonic_to_short(i["mnemonic"]) == i["short"]


def test_from_mnemonic_to_entropy():
    for i in bip39_12words:
        assert from_mnemonic_to_entropy(i["mnemonic"]) == i["entropy"]
    for i in bip39_24words:
        assert from_mnemonic_to_entropy(i["mnemonic"]) == i["entropy"]


def test_from_entropy_to_mnemonic():
    for i in bip39_12words:
        assert from_entropy_to_mnemonic(i["entropy"]) == i["mnemonic"]
    for i in bip39_24words:
        assert from_entropy_to_mnemonic(i["entropy"]) == i["mnemonic"]


def test_from_mnemonic_to_bip85():
    for i in bip85:
        if i.get("passphrase"):
            passphrase = i["passphrase"]
        else:
            passphrase = ""
        for length in [12, 24]:
            for index in bip85_indexes:
                assert (
                    from_mnemonic_to_bip85(
                        i["master seed"],
                        passphrase=passphrase,
                        length=length,
                        index=index,
                    )
                    == i[length][index]
                )
