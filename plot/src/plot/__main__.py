import argparse
import os
import sys
import glob

import matplotlib.pyplot as plt
from parsy import ParseError

from miss_rate_curve import MissRateCurve


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


def plot_client_timeline(args, client_files):
    try:
        X = []
        Y = []

        prev_mrc = None
        for path in client_files:
            with open(path) as mrc_file:
                mrc = MissRateCurve.parse_miss_rate_curve(mrc_file.readlines())
                if prev_mrc == None:
                    prev_mrc = mrc
                    continue
                mae = mrc.mean_absolute_error(prev_mrc)
                prev_mrc = mrc
                ts = int(os.path.basename(path).split("_")[1].split(".")[0])
                X.append(ts)
                Y.append(mae)
        X,Y = zip(*sorted(zip(X,Y), key=lambda x: x[0]))

        plt.plot(X, Y)
        plt.show()

    except IsADirectoryError:
        print(f"{path}: unexpected subdirectory in miss rate curve directory")
    except ParseError as err:
        print(f"{path}: parse error: {err}")



def get_client_files(args):
    clients = []
    for path in os.listdir(args.mrc):
        client = os.path.basename(path).split("_")[0]
        if not client in clients:
            clients.append(client)

    client_files = []

    for client in clients:
        files = glob.glob(os.path.join(args.mrc, f"{client}_*.txt"))
        client_files.append(files)

    return client_files

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mrc")
    args = parser.parse_args()

    # print_all_mrc(args)
    client_files = get_client_files(args)
    for client in client_files:
        plot_client_timeline(args, client)

if __name__ == "__main__":
    main()
