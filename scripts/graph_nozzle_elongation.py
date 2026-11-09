#!/usr/bin/env python3
# Graph nozzle thermal elongation from Z_THERMAL_ADJUST_CALIBRATE output
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import optparse

import matplotlib
import numpy as np


def parse_log(logname):
    data = np.loadtxt(logname, delimiter=",", skiprows=1)
    return data[:, 0], data[:, 1]


def plot_elongation(temps, z_vals):
    a = np.vstack([temps, np.ones(len(temps))]).T
    slope, intercept = np.linalg.lstsq(a, z_vals, rcond=None)[0]
    z_min = z_vals.min()
    fig, ax = matplotlib.pyplot.subplots()
    ax.set_title("Nozzle Elongation Coefficient")
    ax.set_xlabel("Temperature °C")
    ax.set_ylabel("Nozzle Elongation mm")
    ax.scatter(temps, z_vals - z_min, label="measurements")
    line_x = np.array([temps.min(), temps.max()])
    ax.plot(
        line_x,
        slope * line_x + (intercept - z_min),
        color="tab:red",
        label="temp_coeff=%.8f" % (-slope,),
    )
    ax.legend()
    ax.grid(True)
    fig.tight_layout()
    return fig


def setup_matplotlib(output_to_file):
    global matplotlib
    if output_to_file:
        matplotlib.rcParams.update({"figure.autolayout": True})
        matplotlib.use("Agg")
    import matplotlib.pyplot


def main():
    usage = "%prog [options] <csv file>"
    opts = optparse.OptionParser(usage)
    opts.add_option(
        "-o",
        "--output",
        type="string",
        dest="output",
        default=None,
        help="filename of output graph",
    )
    options, args = opts.parse_args()
    if len(args) != 1:
        opts.error("Incorrect number of arguments")

    temps, z_vals = parse_log(args[0])
    setup_matplotlib(options.output is not None)
    fig = plot_elongation(temps, z_vals)
    if options.output is None:
        matplotlib.pyplot.show()
    else:
        fig.set_size_inches(8, 6)
        fig.savefig(options.output)


if __name__ == "__main__":
    main()
