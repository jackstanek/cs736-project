import argparse

import matplotlib.pyplot as plt

from plot.miss_rate_curve import MissRateCurve


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mrc", type=argparse.FileType(mode="r"))
    args = parser.parse_args()

    with args.mrc:
        mrc = MissRateCurve.parse_miss_rate_curve(args.mrc.readlines())
        fig, axs = plt.subplots()
        mrc.plot(axs)
        plt.show()


if __name__ == "__main__":
    main()
