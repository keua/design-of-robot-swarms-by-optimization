import os
import subprocess
import logging
import csv
import numpy as np

home = "/home/kubedaar/"
path_scenario = home + "masterthesis/localsearch/scenarios/kubedaar/vanilla/"
rootdir = '/home/kubedaar/masterthesis/result/'
budgets = ["budget_5k","budget_20k","budget_50k"]
architectures = ["FSM", "BT"]
acceptances = ["MEAN", "MEDIAN", "WILCOXON"]
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
}
seeds = [845250, 895992, 965205, 238419, 968623,
         345192, 757616, 3185512, 9216842, 9516551]
sample = 10
workers = len(acceptances) * sample * len(seeds)
cmd_base = "{} --seed {} -n -c {} {}"


def get_folders(budget, architecture, acceptance):
    folders = [os.path.join(root, name)
               for root, dirs, files in os.walk(rootdir + budget)
               for name in dirs
               if architecture in name and acceptance in name]
    return sorted(folders)


def get_controllers(bud, arch, accept, scenario, folders):
    controllers = []
    auto = automode[arch]
    scenario = scenarios[scenario][arch]
    out = open(bud + "_" + arch + "_" + accept + ".res", "w")
    for fold in folders:
        best_controller = fold + "/best_controller.txt"
        file = open(best_controller, "r")
        controller = file.read()
        for seed in seeds:
            cmd = cmd_base.format(auto, seed, scenario, controller)
            out.write(cmd + "\n")
            controllers.append((auto, str(seed), scenario, controller))
        file.close()
    out.close()
    return controllers


def evaluate_controllers(controllers):
    import mpi4py.futures
    results = []
    pool = mpi4py.futures.MPIPoolExecutor(max_workers=workers)
    for controller in controllers:
        results.append(pool.submit(execute_controller, *controller))
    pool.shutdown(wait=True)
    return results


def execute_controller(auto, seed, scenario, controller):
    args = [auto, "--seed", seed, "-n", "-c", scenario]
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


if __name__ == "__main__":
    controllers = []
    for bud in budgets:
        for arch in architectures:
            for accept in acceptances:
                print(bud, arch, accept)
                folders = get_folders(bud, arch, accept)
                controllers.extend(get_controllers(
                    bud, arch, accept, "foraging", folders))

    print(len(controllers))
    results = evaluate_controllers(controllers)
    i = 0
    for bud in budgets:
        with open('summary_'+bud+'.csv', 'w') as writeFile:
            writer = csv.writer(writeFile)
            for arch in architectures:
                for accept in acceptances:
                    agg = np.mean if accept is "MEAN" else np.median
                    writer.writerow([bud, arch, accept])
                    row = []
                    scores = []
                    for s in range(sample):
                        agg_scores = []
                        for seed in seeds:
                            if results[i].exception() is not None:
                                raise results[i].exception()
                            agg_scores.append(results[i].result())
                            i += 1
                        row.append(agg(agg_scores))
                        scores.extend(agg_scores)
                    writer.writerow(scores)
                    writer.writerow(row)
