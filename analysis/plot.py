import argparse

import matplotlib.pyplot as plt
import numpy as np
import pandas
import seaborn as sns
from IPython.display import display


def initialize():
    """
    Reading conf and args
    """
    ap = argparse.ArgumentParser(description='Process results')
    ap.add_argument(
        "-s", "--scenario", required=False, help="results from scenario",
        nargs='?', const=str, type=str, default="foraging", dest="scenario"
    )
    ap.add_argument(
        "-b", "--budgets", required=False, help="Budgets to analyse",
        nargs='+', type=str, default=["5k", "20k", "50k"], dest="budgets"
    )
    ap.add_argument(
        "-a", "--acceptances", required=False, help="acceptances to analyse",
        nargs='+', type=str, default=["MEAN", "MEDIAN", "WILCOXON"],
        dest="acceptances"
    )
    ap.add_argument(
        "-ar", "--architectures", required=False,
        help="architectures to analyse", nargs='+', type=str,
        default=["FSM", "BT"], dest="architectures"
    )
    ap.add_argument(
        "-p", "--plot", required=False,
        help="Type of plot to plot", nargs='+', type=str,
        default=["boxplot"], dest="plots"
    )
    return ap.parse_args()

def boxplot(args):
    """
    Plot boxplots
    """
    df = pandas.read_excel('data/summary_%s.xlsx' % args.scenario, index_col=0)
    # Generate columns per budget and architecture
    columns, labels = ([] for _ in range(2))
    for budget in args.budgets:
        for arch in args.architectures:
            column = []
            for acceptance in args.acceptances:
                column.append("budget_%s_%s_%s" % (budget, arch, acceptance))
                labels.append("%s_%s" % (arch, acceptance))
            columns.append(column)

    # Separate data frame in columns per budget and architecture
    dfs = [df[c] for c in columns]

    # Set plot configuration
    sns.set_context("notebook")
    sns.set_style("whitegrid")
    sns.set_palette("Greys")

    # Define plot structure
    cols = len(args.architectures)
    rows = len(args.budgets)
    fig, axs = plt.subplots(ncols=cols, nrows=rows, sharey=True, sharex=True)

    # Plot boxplots per each architecture and budget
    for i, df in enumerate(dfs):
        sns.boxplot(data=df, ax=axs[int(i / rows), i % cols])
    # Set legend per each budget
    for i, budget in enumerate(args.budgets):
        for j, arch in enumerate(args.architectures):
            axs[i, j].legend([budget], loc="lower right")
    # Set x (acceptance) label per each architecture
    for i in range(0, cols):
        axs[rows - 1,
            i].set_xticklabels(args.acceptances, rotation=30, fontsize=7)
    # Set titles per each architecture
    for i, arch in enumerate(args.architectures):
        axs[0, i].set_title(arch, fontsize=14)
    # Set y (objective function) label per each budget
    for i in range(0, rows):
        axs[i, 0].set_ylabel('Objective function', fontsize=7)
    # Show boxplots
    plt.show()
    # Display Dataframes in Jupyter notebook per budget
    for i in range(0, rows + 1, 2):
        display(pandas.concat([dfs[i], dfs[i + 1]], axis=1))
    # Save boxplot for future uses
    fig.savefig("plots/summary_%s.pdf" % args.scenario)

def main():
    args = initialize()
    for plot in args.plots:
        f = globals()[plot]
        f(args)



if __name__ == "__main__":
    main()
