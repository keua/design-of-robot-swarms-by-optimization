import statistics as stats
import scipy.stats as scistats
import collections as coll

Criterion = coll.namedtuple(
    'Criterion', ['type', 'best_outcome', 'mut_outcome', 'acceptance']
)


def mean(best_cntrl_scores, mut_cntrl_scores):
    mut_out = stats.mean(mut_cntrl_scores)
    best_out = stats.mean(best_cntrl_scores)
    # < for max
    return Criterion('Mean', best_out, mut_out, best_out < mut_out)


def median(best_cntrl_scores, mut_cntrl_scores):
    mut_out = stats.median(mut_cntrl_scores)
    best_out = stats.median(best_cntrl_scores)
    # < for max
    return Criterion('Median', best_out, mut_out, best_out < mut_out)


def mode(best_cntrl_scores, mut_cntrl_scores):
    mut_out = stats.mode(mut_cntrl_scores)
    best_out = stats.mode(best_cntrl_scores)
    # < for max
    return Criterion('Mode', best_out, mut_out, best_out < mut_out)


def sumc(best_cntrl_scores, mut_cntrl_scores):
    mut_out = sum(mut_cntrl_scores)
    best_out = sum(best_cntrl_scores)
    # < for max
    return Criterion('Sum', best_out, mut_out, best_out < mut_out)


def maxc(best_cntrl_scores, mut_cntrl_scores):
    mut_out = sum(mut_cntrl_scores)
    best_out = sum(best_cntrl_scores)
    # < for max
    return Criterion('Max', best_out, mut_out, best_out < mut_out)


def minc(best_cntrl_scores, mut_cntrl_scores):
    mut_out = min(mut_cntrl_scores)
    best_out = min(best_cntrl_scores)
    # < for max
    return Criterion('Min', best_out, mut_out, best_out < mut_out)


def tstudent_test(best_cntrl_scores, mut_cntrl_scores, confidence=0.05):
    _, p = scistats.ttest_ind(best_cntrl_scores, mut_cntrl_scores)
    mut_out = stats.mean(mut_cntrl_scores)
    best_out = stats.mean(best_cntrl_scores)
    # < for max
    return Criterion(
        'TStudent', best_out, mut_out, best_out < mut_out and p < confidence
    )


def wilcoxon_test(best_cntrl_scores, mut_cntrl_scores, confidence=0.05):
    _, p = scistats.wilcoxon(best_cntrl_scores, mut_cntrl_scores)
    mut_out = stats.mean(mut_cntrl_scores)
    best_out = stats.mean(best_cntrl_scores)
    # < for max
    return Criterion(
        'Wilcoxon', best_out, mut_out, best_out < mut_out and p < confidence
    )
