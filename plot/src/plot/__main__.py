import argparse
import json
import os
import sys
import random

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from parsy import ParseError

from plot.miss_rate_curve import MissRateCurve
from plot.json import parse_fast


def plot_all_mrc(args):
    if os.path.isdir(args.mrc):
        paths = [os.path.join(args.mrc, path) for path in os.listdir(args.mrc)]
    elif os.path.isfile(args.mrc):
        paths = [args.mrc]
    else:
        print(f"{args.mrc}: no such file or directory")
        sys.exit(1)

    plotted = 0
    fig, axs = plt.subplots()
    for path in paths:
        try:
            with open(path) as mrc_file:
                mrc = MissRateCurve.parse_miss_rate_curve(mrc_file.readlines())
                if not mrc:
                    continue

                mrc.plot(axs)
                plotted += 1

        except IsADirectoryError:
            print(f"{path}: unexpected subdirectory in miss rate curve directory")
            sys.exit(1)
        except ParseError as err:
            print(f"{path}: parse error: {err}")
            sys.exit(1)

    if plotted:
        plt.show()
    else:
        print(f"{args.mrc}: no miss rate curve information found in directory")


def plot_client_timeline(axs: Axes, client_name: str, client_data: dict):
    try:
        xs: list[float] = []
        ys: list[float] = []
        prev_mrc = None
        mrcs = client_data["mrcs"]
        for ts, mrc_lines in mrcs.items():
            mrc = MissRateCurve.parse_miss_rate_curve(mrc_lines)
            if prev_mrc is None:
                prev_mrc = mrc
                continue
            mae_percent = mrc.mean_absolute_error(prev_mrc) * 100
            prev_mrc = mrc
            xs.append(float(ts))
            ys.append(mae_percent)
        xs, ys = tuple(list(z) for z in zip(*sorted(zip(xs, ys), key=lambda x: x[0])))

        plt.plot(xs, ys)
        plt.title(f"Client {client_name} MAE Curve")
        plt.xlabel("Timestamp")
        plt.ylabel("MAE (%)")
        # ax = plt.gca()
        # ax.set_ylim(0, 3)
        plt.show()

    except ParseError as err:
        print(f"{client_name}: parse error: {err}")


def plot_first_last(axs: Axes, first: int, last: int, n: int):
    ys = [n, n]
    xs = [first / (60 * 60), last / (60 * 60)]
    axs.set_xlabel("Time (hrs)")
    axs.set_ylabel("Client")
    axs.plot(xs, ys)


def plot_lifetimes_distribution(axs: Axes, client_data: dict, bins: int):
    """Plot a histogram of the lifetimes of each client"""
    lifetimes = [
        (int(d["last_ts"]) - int(d["first_ts"])) / (60 * 60)
        for d in client_data.values()
    ]
    axs.set_xlabel("Lifetime of cache client (hrs)")
    axs.set_ylabel("Count")
    axs.hist(lifetimes, bins=bins)


def get_all_mrcs(client_file_paths: dict[str, str]) -> dict:
    client_datas = {}
    for client, client_file_path in client_file_paths.items():
        with open(client_file_path) as client_file:
            client_datas[client] = json.load(client_file)
    return client_datas


def get_all_first_last(client_file_paths: dict[str, str]) -> dict:
    client_datas = {}
    for client, client_file_path in client_file_paths.items():
        with open(client_file_path) as client_file:
            client_datas[client] = parse_fast(client_file)
    return client_datas


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("plot", choices=["firstlast", "lifetimedist", "mae"])
    parser.add_argument("--sample-size", type=int)
    parser.add_argument("--hist-bins", type=int, default=25)
    parser.add_argument("mrc")
    args = parser.parse_args()

    # print_all_mrc(args)
    client_file_paths = {
        filepath: os.path.join(args.mrc, filepath) for filepath in os.listdir(args.mrc)
    }
    if args.sample_size:
        client_file_paths = dict(
            random.sample(list(client_file_paths.items()), k=args.sample_size)
        )


    fig, axs = plt.subplots()
    if args.plot == "firstlast":
        client_datas = get_all_first_last(client_file_paths)
        if not args.sample_size:
            print("need a sample size with firstlast plot")
            return 1

        start_ends = sorted(
            ((d["first_ts"], d["last_ts"]) for d in client_datas.values()),
        )
        for n, (first, last) in enumerate(start_ends):
            plot_first_last(axs, int(first), int(last), n)

        plt.show()
        return 0

    elif args.plot == "lifetimedist":
        plot_lifetimes_distribution(axs, client_datas, args.hist_bins)
        plt.show()

    else:
        for client_name, client_data in client_datas.items():
            print(f"plotting {client_name}")
            plot_client_timeline(axs, client_name, client_data)


if __name__ == "__main__":
    main()
