import argparse
import os
import sys

import matplotlib.pyplot as plt
from parsy import ParseError

from plot.miss_rate_curve import MissRateCurve


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mrc")
    args = parser.parse_args()

    if os.path.isdir(args.mrc):
        paths = [os.path.join(args.mrc, path) for path in os.listdir(args.mrc)]
    elif os.path.isfile(args.mrc):
        paths = [args.mrc]
    else:
        print(f"{args.mrc}: no such file or directory")
        sys.exit(1)

    plotted = False
    for path in paths:
        try:
            with open(path) as mrc_file:
                mrc = MissRateCurve.parse_miss_rate_curve(mrc_file.readlines())
                if not mrc:
                    continue

                fig, axs = plt.subplots()
                mrc.plot(axs)
                plotted = True

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

if __name__ == "__main__":
    main()
