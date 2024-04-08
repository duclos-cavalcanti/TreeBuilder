import argparse
import deploy

def parse():
    arg_def = argparse.ArgumentParser(
        description='Main script to several tasks.',
        epilog='Example: main.py --mode/-m run'
    )

    arg_def.add_argument(
        "-m", "--module",
        type=str,
        required=True,
        choices=["deploy", "analysis"],
        dest="module",
    )

    return arg_def.parse_known_args()


def main():
    args, rem = parse()

    match args.module:
        case "deploy":
            deploy.run(rem)

        case _:
            raise NotImplementedError(f"Mode {args.module} doesn't have a corresponding function!")

    return


if __name__ == "__main__":
    main()
