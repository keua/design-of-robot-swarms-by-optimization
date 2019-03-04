import argparse
import csv
import logging
import os
import subprocess

import numpy as np
import pandas

home = "/home/kubedaar/"
path_scenario = home + "masterthesis/localsearch/scenarios/kubedaar/vanilla/"
agg_methods = {
    "MEAN" : np.mean,
    "MEDIAN": np.median,
    "WILCOXON": np.median
}
automode = {
    "BT": home + "AutoMoDe-BT/bin/automode_main_bt",
    "FSM": home + "AutoMoDe-FSM/bin/automode_main"
}
scenarios = {
    "foraging": {
        "BT": path_scenario + "foraging_bt.argos",
        "FSM": path_scenario + "foraging.argos"
    },
    "aggregation": {
        "BT": path_scenario + "aggregation_bt.argos",
        "FSM": path_scenario + "aggregation.argos"
    },
    "sca": {
        "BT": path_scenario + "sca_bt.argos",
        "FSM": path_scenario + "sca_fsm.argos"
    },
    "aac": {
        "BT": path_scenario + "aac_bt.argos",
        "FSM": path_scenario + "aac_fsm.argos"
    },
}
seeds = [845250, 895992, 965205, 238419, 968623,
         345192, 757616, 3185512, 9216842, 9516551]
cmd_base = "{} --seed {} -n -c {} {}"


def get_folders(rootdir, scenario, budget, architecture, acceptance):
    folders = [os.path.join(root, name)
               for root, dirs, files in os.walk(rootdir + scenario + budget)
               for name in dirs
               if architecture in name and acceptance in name]
    return sorted(folders)


def get_controllers(bud, arch, accept, scenario, folders, rootdir):
    controllers = []
    auto = automode[arch]
    scenario_file = scenarios[scenario][arch]
    out = open("%s%s/%s_%s_%s.res" %
               (rootdir, scenario, bud, arch, accept), "w")
    for fold in folders:
        best_controller = "%s/best_controller.txt" % fold
        file = open(best_controller, "r")
        controller = file.read()
        for seed in seeds:
            cmd = cmd_base.format(auto, seed, scenario_file, controller)
            out.write("%s\n" % cmd)
            controllers.append((auto, str(seed), scenario_file, controller))
        file.close()
    out.close()
    return controllers


def evaluate_controllers(controllers, workers):
    import mpi4py.futures
    results = []
    pool = mpi4py.futures.MPIPoolExecutor(max_workers=workers)
    for controller in controllers:
        results.append(pool.submit(execute_controller, *controller))
    pool.shutdown(wait=True)
    return results


def execute_controller(auto, seed, scenario_file, controller):
    args = [auto, "--seed", seed, "-n", "-c", scenario_file]
    args.extend(controller.split(" "))
    p = subprocess.Popen(args, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    (stdout, stderr) = p.communicate()
    # Analyse result
    output = stdout.decode('utf-8')
    lines = output.splitlines()
    try:
        logging.debug(lines[len(lines) - 1])
        score = float(lines[len(lines) - 1].split(" ")[1])
    except:
        score = -1  # Just to be sure
        logging.error("arguments: {}".format(controller))
        logging.error("stderr: {}".format(stderr.decode('utf-8')))
        logging.error("stdout: {}".format(stdout.decode('utf-8')))
        raise
    logging.debug("returned score: {}".format(score))
    return score


def initialize():
    # Reading conf and args
    ap = argparse.ArgumentParser(description='Process results')
    ap.add_argument(
        "-s", "--scenario", required=False, help="results from scenario",
        nargs='?', const=str, type=str, default="foraging", dest="scenario"
    )
    ap.add_argument(
        "-rd", "--rootdir", required=False, help="Folder that contains tests",
        nargs='?', const=str, type=str,
        default='/home/kubedaar/masterthesis/result/', dest="rootdir"
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
        "-sm", "--sample", required=False, help="experiment sample",
        nargs='?', const=int, type=int, default=10, dest="sample"
    )
    args = ap.parse_args()
    return args


if __name__ == "__main__":
    # Read execution configuration
    args = initialize()
    # Set execution values
    rootdir = args.rootdir
    print(rootdir)
    budgets = ["budget_%s" % budget for budget in args.budgets]
    acceptances = args.acceptances
    architectures = args.architectures
    sample = args.sample
    workers = len(acceptances) * sample * len(seeds)
    # Read best controllers and generate commands to execute
    controllers = []
    print(budgets)
    print(architectures)
    print(acceptances)
    for bud in budgets:
        for arch in architectures:
            for accept in acceptances:
                print(bud, arch, accept)
                folders = get_folders(
                    rootdir, "%s/" % args.scenario, bud, arch, accept)
                controllers.extend(get_controllers(
                    bud, arch, accept, args.scenario, folders, rootdir))

    print(len(controllers))
    # Evaluate controller in simulations
    results = evaluate_controllers(controllers, workers)
    # Read results of evaluation
    d = {}
    i = 0
    for bud in budgets:
        for arch in architectures:
            for accept in acceptances:
                agg = agg_methods[accept]
                row = []
                for s in range(sample):
                    agg_scores = []
                    for seed in seeds:
                        if results[i].exception() is not None:
                            raise results[i].exception()
                        agg_scores.append(results[i].result())
                        i += 1
                    row.append(agg(agg_scores))
                d["%s_%s_%s" % (bud, arch, accept)] = row
    # Pandas dataframe
    df = pandas.DataFrame(data=d)
    df.to_excel("data/summary_%s.xlsx" % args.scenario,  encoding='utf-8')
