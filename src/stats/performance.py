import os


def prepare_score_files():
    if not os.path.isdir("scores"):
        os.mkdir("scores")
    with open("scores/history.csv", "w") as file:
        file.write("best, perturbed, operator \n")
    with open("scores/scores.csv", "w") as file:
        file.write("best_scores; perturbed_scores \n")


def save_results(best_controller, perturbed_controller):
    with open("scores/history.csv", "a") as file:
        file.write("{}, {}, {} \n".format(best_controller.agg_score[1], perturbed_controller.agg_score[1],
                                          perturbed_controller.perturb_history[
                                              len(perturbed_controller.perturb_history) - 1].__name__))
    with open("scores/scores.csv", "a") as file:
        file.write("{}; {} \n".format(best_controller.scores, perturbed_controller.scores))
