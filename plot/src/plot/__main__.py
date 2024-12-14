import argparse
import os
import sys
import glob

import matplotlib.pyplot as plt
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


def plot_client_timeline(client: str, client_files: list[str]):
    """Plot a timeline for some client"""
    try:
        X = []
        Y = []
        prev_mrc = None
        for path in client_files:
            with open(path) as mrc_file:
                mrc = MissRateCurve.parse_miss_rate_curve_file(mrc_file)
                if prev_mrc is None:
                    prev_mrc = mrc
                    continue
                mae_percent = mrc.mean_absolute_error(prev_mrc) * 100
                prev_mrc = mrc
                ts = int(os.path.basename(path))
                X.append(ts)
                Y.append(mae_percent)
        if not (X and Y):
            return
        X, Y = zip(*sorted(zip(X, Y), key=lambda x: x[0]))

        plt.plot(X, Y)
        plt.title(f"Client {client} MAE Curve")
        plt.xlabel("Timestamp")
        plt.ylabel("MAE (%)")
        ax = plt.gca()
        ax.set_ylim(0, 3)
        plt.show()

    except IsADirectoryError:
        print(f"{path}: unexpected subdirectory in miss rate curve directory")
    except ParseError as err:
        print(f"{path}: parse error: {err}")


def get_client_files(mrc_dir: str) -> dict[str, list[str]]:
    client_files: dict[str, list[str]] = {}
    for root, dirs, files in os.walk(mrc_dir):
        if root == mrc_dir:
            continue
        client = os.path.basename(root)
        client_files[client] = []
        for filename in files:
            client_files[client].append(os.path.join(root, filename))
    return client_files


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mrc")
    args = parser.parse_args()

    # print_all_mrc(args)
    client_files = get_client_files(args.mrc)
    for client, client_files in client_files.items():
        plot_client_timeline(client, client_files)


if __name__ == "__main__":
    main()
