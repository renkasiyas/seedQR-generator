import argparse
import os
from pprint import pprint as pp

from dotenv import load_dotenv
from rich import pretty, print

from seedqr.helpers import (from_binary_indexes_to_mnemonic,
                            from_decimal_index_to_mnemonic,
                            from_mnemonic_to_bip85, from_mnemonic_to_entropy,
                            from_short_to_mnemonic, generate_mnemonic, make_qr,
                            process_entropy)

pretty.install()

VALID_LENGTHS = [12, 15, 18, 21, 24]


def shared_bip_args(parser):
    parser.add_argument("--qty", default=0, type=int, help="Generate batch quantity.")
    parser.add_argument(
        "--length",
        type=int,
        default=12,
        help="Select from [12, 15, 18, 21, 24] words length.",
        choices=VALID_LENGTHS,
    )


def env_argument(parser):
    parser.add_argument(
        "--env", action="store_true", help="Load USER_INPUT from .env file."
    )


def shared_arguments(parser):
    parser.add_argument("--no-info", action="store_true")
    parser.add_argument("--hide-qr", action="store_true")
    parser.add_argument("--save", action="store_true")
    parser.add_argument("--filename")


parser = argparse.ArgumentParser(description="Scripts for Seed Phrases.")
subparsers = parser.add_subparsers(help="Command help", dest="command")

bip39_parser = subparsers.add_parser("bip39")
bip39_parser.add_argument("--hints", type=str, default="")
bip39_parser.add_argument("--places", type=str, default="")
shared_bip_args(bip39_parser)
shared_arguments(bip39_parser)

bip85_parser = subparsers.add_parser("bip85")
bip85_parser.add_argument("--master", default=None, type=str)
bip85_parser.add_argument("--passphrase", type=str, default="")
bip85_parser.add_argument(
    "--index", type=int, help="Generate a specific index.", default=-1
)
# bip85_parser.add_argument("--start", type=int, help="Generate a specific index.")
# bip85_parser.add_argument("--end", type=int, help="Generate a specific index.")
shared_bip_args(bip85_parser)
shared_arguments(bip85_parser)
env_argument(bip85_parser)

seedQR_parser = subparsers.add_parser("seedQR")
seedQR_parser.add_argument("--input", default=None, type=str)
seedQR_parser.add_argument("--mnemonic", action="store_true")
seedQR_parser.add_argument("--entropy", action="store_true")
seedQR_parser.add_argument("--short", action="store_true")
seedQR_parser.add_argument(
    "--decimal-index", action="store_true", help="Decimal indexes start at 0"
)
seedQR_parser.add_argument("--binary-index", action="store_true")
shared_arguments(seedQR_parser)
env_argument(seedQR_parser)


args = parser.parse_args()


def print_data(data):
    print(
        f"""
[bold]Bytes Entropy:[/bold]

    {data['bytes']}

[bold]Hex Entropy:[/bold]

    {data['entropy']}

[bold]Binary Index:[/bold]

    {data['index']['binary']}

    String: {"".join(data['index']['binary'])}

[bold]Decimal Index:[/bold]

    {data['index']['decimal']}
    String: {"".join(data['index']['decimal'])}

[bold]Mnemonic:[/bold]

    [bold yellow]{data['mnemonic']}[/bold yellow]

[bold]Shorted Mnemonic:[/bold]

    {data['short']}

    """
    )


def post_process(args, data, index):
    filename = False
    if args.save:
        if args.filename:
            filename = args.filename
        else:
            filename = f"seedQR-{index:04}"
    if not args.no_info:
        print_data(data)
    if not args.hide_qr:
        print("[bold]Compact SeedQR:[/bold]\n")
    make_qr(data["bytes"], hide=args.hide_qr, save=filename)


def seed_has_hints(args, mnemonic):
    mnemonic = mnemonic.split()
    template_mn = [None] * 12
    for i in range(len(args.hints)):
        template_mn[args.places[i] - 1] = args.hints[i]
    in_place = []
    if all(list(map(lambda word: word in set(mnemonic), args.hints))):
        for i in range(len(args.hints)):
            in_place.append(mnemonic[args.places[i] - 1] == args.hints[i])
        return all(in_place)


def generate_bip39(args):
    print("Generating BIP39 Seedphrase")
    if args.hints and args.places:
        args.hints = args.hints.split()
        args.places = [int(x) for x in args.places.split()]
        print(args.hints, args.places)
        if len(args.hints) == len(args.places):
            for i in range(1000000000):
                seed_number = i + 1
                strength = int(args.length * 32 / 3)
                mnemonic = generate_mnemonic(strength)
                if i % 5000000 == 0:
                    print(f"#{seed_number}")
                if seed_has_hints(args, mnemonic):
                    print(f"#{seed_number}: {mnemonic}")
        else:
            raise ValueError("Hints and places should have same length.")
    elif args.qty > 0:
        if args.qty <= 100:
            for i in range(args.qty):
                seed_number = i + 1
                strength = int(args.length * 32 / 3)
                mnemonic = generate_mnemonic(strength)
                print(f"BIP39 Seed #{seed_number}: {mnemonic}")
                entropy = from_mnemonic_to_entropy(mnemonic)
                data = process_entropy(entropy)
                post_process(args, data, seed_number)
        else:
            raise ValueError("--qty max value: 100.")


def make_child_seed(args, index):
    child_mnemonic = from_mnemonic_to_bip85(
        args.master, args.length, index, args.passphrase
    )
    print(f"Child Mnemonic #{index}: [bold yellow]{child_mnemonic}[/bold yellow]")
    entropy = from_mnemonic_to_entropy(child_mnemonic)
    data = process_entropy(entropy)
    post_process(args, data, index)


def generate_bip85(args):
    if args.master and args.env:
        raise ValueError(
            "Using manual --master and --env flag could lead to costly mistakes. Please use just one <input> or --env."
        )
    elif args.env:
        if load_dotenv():
            args.master = os.environ["USER_INPUT"]
        else:
            raise ValueError(".env file not found.")
    if args.master:
        print(
            f"Generating BIP85 Child Mnemonic Seed from master seedphrase:\n[bold orange]{args.master}[/bold orange]"
        )
        if args.qty:
            if args.qty <= 100:
                for index in range(args.qty):
                    make_child_seed(args, index)
            else:
                raise ValueError("--qty max value: 100.")
        elif args.index >= 0:
            make_child_seed(args, args.index)
        else:
            raise ValueError("No --qty or --index provided.")
    else:
        raise ValueError("No user input provided, please use --master or --env.")


def generate_seedqr(args):
    print("Generating SeedQR from input")
    if args.input and args.env:
        raise ValueError(
            "Using manual --input and --env flag could lead to costly mistakes. Please use just one <input> or --env."
        )
    elif args.env:
        if load_dotenv():
            user_input = os.environ["USER_INPUT"]
        else:
            raise ValueError(".env file not found.")
    elif args.input:
        user_input = args.input
    else:
        raise ValueError("No user input provided, please use --input or --env.")

    print(f"\nUser input: [red]{user_input}[/red]")

    if args.entropy:
        entropy = user_input
    else:
        if args.mnemonic:
            print("Using full mnemonic seed phrase")
            mnemonic = user_input
        elif args.short:
            print("Using shorted mnemonic seed phrase")
            mnemonic = from_short_to_mnemonic(user_input)
        elif args.decimal_index:
            print(f"Using decimal_index array starting at {args.decimal_index}")
            mnemonic = from_decimal_index_to_mnemonic(user_input)
        elif args.binary_index:
            print("Using binary indexes.")
            mnemonic = from_binary_indexes_to_mnemonic(user_input)
        else:
            raise ValueError(
                "No type of input provided. Please use --mnemonic, --entropy, --decimal-index, etc."
            )
        entropy = from_mnemonic_to_entropy(mnemonic)
    data = process_entropy(entropy)
    post_process(args, data, 0)


if __name__ == "__main__":
    # print(args)
    if args.command == "bip39":
        generate_bip39(args)
    elif args.command == "bip85":
        generate_bip85(args)
    elif args.command == "seedQR":
        generate_seedqr(args)
    else:
        print("No valid command selected")
