import statistics as stats
import collections as coll

Criterion = coll.namedtuple(
    'Criterion', ['type', 'best_outcome', 'mut_outcome', 'acceptance']
)


def mean(best_cntrl_scores, mut_cntrl_scores):
    mut_out = stats.mean(mut_cntrl_scores)
    best_out = stats.mean(best_cntrl_scores)
    # < for max
    return Criterion('Mean', best_out, mut_out, best_out < mut_out)
