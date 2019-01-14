import statistics
import collections

import scipy.stats as scistats

Criterion = collections.namedtuple(
    'Criterion', ['type', 'best_outcome', 'perturb_outcome', 'accepted']
)


def mean(best_cntrl_scores, perturb_cntrl_scores):
    perturb_out = statistics.mean(perturb_cntrl_scores)
    best_out = statistics.mean(best_cntrl_scores)
    # < for max
    return Criterion('Mean', best_out, perturb_out, best_out < perturb_out)


def median(best_cntrl_scores, perturb_cntrl_scores):
    perturb_out = statistics.median(perturb_cntrl_scores)
    best_out = statistics.median(best_cntrl_scores)
    # < for max
    return Criterion('Median', best_out, perturb_out, best_out < perturb_out)


def mode(best_cntrl_scores, perturb_cntrl_scores):
    perturb_out = statistics.mode(perturb_cntrl_scores)
    best_out = statistics.mode(best_cntrl_scores)
    # < for max
    return Criterion('Mode', best_out, perturb_out, best_out < perturb_out)


def sumc(best_cntrl_scores, perturb_cntrl_scores):
    perturb_out = sum(perturb_cntrl_scores)
    best_out = sum(best_cntrl_scores)
    # < for max
    return Criterion('Sum', best_out, perturb_out, best_out < perturb_out)


def maxc(best_cntrl_scores, perturb_cntrl_scores):
    perturb_out = sum(perturb_cntrl_scores)
    best_out = sum(best_cntrl_scores)
    # < for max
    return Criterion('Max', best_out, perturb_out, best_out < perturb_out)


def minc(best_cntrl_scores, perturb_cntrl_scores):
    perturb_out = min(perturb_cntrl_scores)
    best_out = min(best_cntrl_scores)
    # < for max
    return Criterion('Min', best_out, perturb_out, best_out < perturb_out)


def tstudent_test(best_cntrl_scores, perturb_cntrl_scores, confidence=0.05):
    _, p = scistats.ttest_ind(best_cntrl_scores, perturb_cntrl_scores)
    perturb_out = statistics.mean(perturb_cntrl_scores)
    best_out = statistics.mean(best_cntrl_scores)
    # < for max
    return Criterion(
        'TStudent', best_out, perturb_out, best_out < perturb_out and p < confidence
    )


def wilcoxon_test(best_cntrl_scores, perturb_cntrl_scores, confidence=0.05):
    _, p = scistats.wilcoxon(best_cntrl_scores, perturb_cntrl_scores)
    perturb_out = statistics.mean(perturb_cntrl_scores)
    best_out = statistics.mean(best_cntrl_scores)
    # < for max
    return Criterion(
        'Wilcoxon', best_out, perturb_out, best_out < perturb_out and p < confidence
    )
