import random
import argparse
import subprocess
import logging
import statistics


def evaluate_controller(path_to_AutoMoDe_executable, scenario_file, controller_config_constant, controller):

    # TODO: Handle seed window better?
    seed_window = []
    scores = []
    for i in range(0, 10):
        seed_window.append(random.randint(0, 2147483647))
    for seed in seed_window:
        args = [path_to_AutoMoDe_executable, "-n", "-c", scenario_file, "--seed", str(seed), controller_config_constant]
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
            logging.error("Args: " + str(args))
            logging.error("Stderr: " + stderr.decode('utf-8'))
            logging.error("Stdout: " + stdout.decode('utf-8'))
            raise
        scores.append(score)
    # print(scores)
    return scores


def evaluate_all_controllers(controller_file, automode, scenario, architecture="BT", output_file=""):

    if architecture == "BT":
        controller_config_constant = "--bt-config"
    elif architecture == "FSM":
        controller_config_constant = "--fsm-config"
    else:
        print("Unknown architecture {}".format(architecture))
    if output_file:
        with open(output_file, "w") as output:
            with open(controller_file) as file:
                controllers = file.readlines()
                for controller in controllers:
                    controller = controller.strip()
                    # print(controller)
                    scores = evaluate_controller(automode, scenario, controller_config_constant, controller)
                    # print(statistics.mean(scores))
                    output.write(str(statistics.mean(scores)) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--architecture', dest="architecture", required=True,
                        help="The type of controller used (FSM or BT)."
                             " (REQUIRED)")
    parser.add_argument('-cf', '--controller_file', dest="controller_file", required=True,
                        help="The file that contains the controllers to be evaluated. One controller per line."
                             " (REQUIRED)")
    parser.add_argument('-s', '--scenario_file', dest="scenario_file", required=True,
                        help="The scenario file for the improvement. (REQUIRED)")
    parser.add_argument('-exe', '--executable', dest="executable", required=True,
                        help="The path to the automode executable (REQUIRED)")
    parser.add_argument('-o', '--output', dest="output", required=False, default="",
                        help="An optional argument to write the output to.")
    input_args = parser.parse_args()
    evaluate_all_controllers(input_args.controller_file, input_args.executable, input_args.scenario_file,
                             input_args.architecture, input_args.output)
