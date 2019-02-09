import argparse
import socket


def get_args():
    parser = argparse.ArgumentParser()
    add_args(parser)
    args = parser.parse_args()

    # Kvuli nekompatibilnimu zadavani argumentu s argparse nutno odstranit prefixy "name="
    if args.api_key.startswith("api_key=") and args.city.startswith("city="):
        args.api_key = args.api_key[len("api_key="):]
        args.city = args.city[len("city="):]
    else:
        raise Exception("Bad structure of input args. Type --help for help")

    return args


def add_args(parser):
    parser.add_argument(dest="api_key", help="api_key")
    parser.add_argument(dest="city", help="Specifies in which city you want to display weather")


get_args()

