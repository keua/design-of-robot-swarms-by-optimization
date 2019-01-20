import statistics as stats
import scipy.stats as scistats
import collections as coll
import math

Criterion = coll.namedtuple(
    'Criterion', ['type', 'best_outcome', 'perturb_outcome', 'acceptance']
)


def mean(best_cntrl_scores, perturb_cntrl_scores):
    """
    """
    perturb_out = stats.mean(perturb_cntrl_scores)
    best_out = stats.mean(best_cntrl_scores)
    # < for max
    return Criterion('Mean', best_out, perturb_out, best_out < perturb_out)


def median(best_cntrl_scores, perturb_cntrl_scores):
    """
    """
    perturb_out = stats.median(perturb_cntrl_scores)
    best_out = stats.median(best_cntrl_scores)
    # < for max
    return Criterion('Median', best_out, perturb_out, best_out < perturb_out)


def mode(best_cntrl_scores, perturb_cntrl_scores):
    """
    """
    perturb_out = stats.mode(perturb_cntrl_scores)
    best_out = stats.mode(best_cntrl_scores)
    # < for max
    return Criterion('Mode', best_out, perturb_out, best_out < perturb_out)


def sumc(best_cntrl_scores, perturb_cntrl_scores):
    """
    """
    perturb_out = sum(perturb_cntrl_scores)
    best_out = sum(best_cntrl_scores)
    # < for max
    return Criterion('Sum', best_out, perturb_out, best_out < perturb_out)


def maxc(best_cntrl_scores, perturb_cntrl_scores):
    """
    """
    perturb_out = sum(perturb_cntrl_scores)
    best_out = sum(best_cntrl_scores)
    # < for max
    return Criterion('Max', best_out, perturb_out, best_out < perturb_out)


def minc(best_cntrl_scores, perturb_cntrl_scores):
    """
    """
    perturb_out = min(perturb_cntrl_scores)
    best_out = min(best_cntrl_scores)
    # < for max
    return Criterion('Min', best_out, perturb_out, best_out < perturb_out)


def tstudent_test(best_cntrl_scores, perturb_cntrl_scores, confidence=0.05):
    """
    """
    _, p = scistats.ttest_ind(best_cntrl_scores, perturb_cntrl_scores)
    perturb_out = stats.mean(perturb_cntrl_scores)
    best_out = stats.mean(best_cntrl_scores)
    # < for max
    return Criterion(
        'TStudent', best_out, perturb_out,
        best_out < perturb_out and p < confidence
    )


def wilcoxon_test(best_cntrl_scores, perturb_cntrl_scores, confidence=0.05):
    """
    """
    _, p = scistats.wilcoxon(best_cntrl_scores, perturb_cntrl_scores)
    perturb_out = stats.mean(perturb_cntrl_scores)
    best_out = stats.mean(best_cntrl_scores)
    # < for max
    return Criterion(
        'Wilcoxon', best_out, perturb_out,
        best_out < perturb_out and p < confidence
    )


def metropolis_condition(best_cntrl_scores, perturb_cntrl_scores, t, random_gen,
                         criterion=mean):
    """
    """
    c = criterion(best_cntrl_scores, perturb_cntrl_scores)
    delta = c.perturb_outcome - c.best_outcome
    # While ∆ ≥ 0 or Random (0, 1) < e^(∆/t), do ω ← ω';
    return Criterion(
        'metropolis', c.best_outcome, c.perturb_outcome,
        delta >= 0 or random_gen.random() < math.exp((delta / t))
    )
