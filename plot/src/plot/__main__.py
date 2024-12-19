import argparse
import json
import os
import sys
import random

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.ticker import LogFormatter
from parsy import ParseError

from miss_rate_curve import MissRateCurve


def plot_mrc(client_data, client_name):
    fig, axs = plt.subplots()
    prev = 0
    last = int(client_data["last_ts"])
    first = int(client_data["first_ts"])

    for timestamp, mrc_lines in client_data["mrcs"].items():
        ts = int(timestamp)
        if ts - prev < 3*3600 or ts < 12*3600:
            continue
        prev = ts
        mrc = MissRateCurve.parse_miss_rate_curve(mrc_lines)
        if not mrc:
            continue

        # Earlier timestamps are more blue, later and more red
        red = max(min((ts - first) / (last - first), 1), 0)
        blue = max(min((last - ts + first) / (last - first), 1), 0)

        mrc.plot(axs, color=(red,0,blue,1))

    plt.title(f"Client {client_name} MRC Curves")
    plt.xlabel("Cache Size (keys)")
    plt.ylabel("Miss Rate")
    axs.set_xscale('log', base=2)
    axs.set_yscale('linear')
    axs.xaxis.set_major_formatter(LogFormatter(base=2.0))
    plt.show()


def plot_client_timeline(axs: Axes, client_name: str, client_data: dict):
    try:
        xs: list[float] = []
        ys: list[float] = []
        prev_mrc = None
        mrcs = client_data["mrcs"]
        prev = 0

        it = iter(mrcs.items())
        first = next(it)
        second = next(it)
        time_delta_seconds = int(second[0]) - int(first[0])

        for timestamp, mrc_lines in mrcs.items():
            ts = int(timestamp)
            if ts - prev < 3 * 3600 or ts < 12 * 3600:
                continue
            prev = ts

            mrc = MissRateCurve.parse_miss_rate_curve(mrc_lines)
            if prev_mrc is None:
                prev_mrc = mrc
                continue
            mae_percent = mrc.mean_absolute_error(prev_mrc) * 100 / time_delta_seconds
            prev_mrc = mrc
            xs.append(float(ts))
            ys.append(mae_percent)
        xs, ys = zip(*sorted(zip(xs, ys), key=lambda x: x[0]))

        plt.plot(xs, ys)
        plt.title(f"Client {client_name} MAE Curve")
        plt.xlabel("Timestamp")
        plt.ylabel("MAE (%/s)")
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("plot", choices=["firstlast", "lifetimedist", "mae", "mrc"])
    parser.add_argument("--sample-size", type=int)
    parser.add_argument("--hist-bins", type=int, default=25)
    parser.add_argument("mrc")
    args = parser.parse_args()

    client_file_paths = {
        filepath: os.path.join(args.mrc, filepath) for filepath in os.listdir(args.mrc)
    }
    client_datas = {}
    if args.sample_size:
        client_file_paths = dict(
            random.sample(list(client_file_paths.items()), k=args.sample_size)
        )

    for client, client_file_path in client_file_paths.items():
        with open(client_file_path) as client_file:
            client_datas[client] = json.load(client_file)

    fig, axs = plt.subplots()
    if args.plot == "firstlast":
        if not args.sample_size:
            print("need a sample size with firstlast plot")
            return 1

        start_ends = sorted(
            ((d["first_ts"], d["last_ts"]) for d in client_datas.values()),
            key=lambda x: int(x[0]),
        )
        for n, (first, last) in enumerate(start_ends):
            plot_first_last(axs, int(first), int(last), n)

        plt.show()
        return 0

    elif args.plot == "lifetimedist":
        plot_lifetimes_distribution(axs, client_datas, args.hist_bins)
        plt.show()

    elif args.plot == "mrc":
        for client_name, client_data in client_datas.items():
            plot_mrc(client_data, client_name)

    else:
        for client_name, client_data in client_datas.items():
            print(f'plotting {client_name}')
            plot_client_timeline(axs, client_name, client_data)


if __name__ == "__main__":
    main()
