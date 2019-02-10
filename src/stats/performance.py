import os


best_score = 0


def reset():
    global best_score
    best_score = 0


def prepare_score_files(filename=""):
    if not os.path.isdir("scores"):
        os.mkdir("scores")
    with open("scores/%s_history.csv" % filename, "w") as file:
        file.write("best, perturbed, operator \n")
    with open("scores/%s_scores.csv" % filename, "w") as file:
        file.write("best_scores; perturbed_scores \n")


def save_results(best_controller, perturbed_controller, filename=""):
    with open("scores/%s_history.csv" % filename, "a") as file:
        file.write("{}, {}, {} \n".format(
            best_controller.agg_score[1], perturbed_controller.agg_score[1],
            perturbed_controller.perturb_history[-1].__name__))
    with open("scores/%s_scores.csv" % filename, "a") as file:
        file.write("{}; {} \n".format(
            best_controller.scores, perturbed_controller.scores))


def set_final_score(score):
    global best_score
    best_score = score
