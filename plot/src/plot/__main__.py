import argparse
import json
import os
import sys
import random

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from parsy import ParseError

from plot.miss_rate_curve import MissRateCurve


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


def plot_client_timeline(client_name: str, client_data: dict):
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
        xs, ys = zip(*sorted(zip(xs, ys), key=lambda x: x[0]))

        plt.plot(xs, ys)
        plt.title(f"Client {client_name} MAE Curve")
        plt.xlabel("Timestamp")
        plt.ylabel("MAE (%)")
        ax = plt.gca()
        ax.set_ylim(0, 3)
        plt.show()

    except ParseError as err:
        print(f"{client_name}: parse error: {err}")


def plot_start_end(axs: Axes, start: int, end: int, n: int):
    ys = [n, n]
    xs = [start, end]
    axs.plot(xs, ys)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mrc")
    parser.add_argument("--start-end", action="store_true")
    args = parser.parse_args()

    # print_all_mrc(args)
    client_file_paths = {
        filepath: os.path.join(args.mrc, filepath) for filepath in os.listdir(args.mrc)
    }

    if args.start_end:
        fig, axs = plt.subplots()
        client_datas = []
        for _, client_file_path in client_file_paths.items():
            with open(client_file_path) as client_file:
                client_datas.append(json.load(client_file))

        start_ends = random.sample(
            sorted(
                ((d["first_ts"], d["last_ts"]) for d in client_datas),
                key=lambda x: int(x[0]),
            ),
            k=25,
        )
        for n, (start, end) in enumerate(start_ends):
            plot_start_end(axs, int(start), int(end), n)

        plt.show()
        return 0

    for client_name, client_file_path in client_file_paths.items():
        with open(client_file_path) as client_file:
            client_data = json.load(client_file)
        plot_client_timeline(client_name, client_data)


if __name__ == "__main__":
    main()
