from whalrus.scorer.Scorer import Scorer
from whalrus.scorer.ScorerBorda import ScorerBorda
from whalrus.rule.RuleScore import RuleScore
from whalrus.converter_ballot.ConverterBallotToOrder import ConverterBallotToOrder
from whalrus.priority.Priority import Priority
from whalrus.utils.Utils import cached_property, NiceDict
from whalrus.converter_ballot.ConverterBallot import ConverterBallot
from whalrus.profile.Profile import Profile
from typing import Union


class RuleBucklin(RuleScore):
    """
    Bucklin's rule

    :param converter: the default is :class:`ConverterBallotToOrder`.
    :param scorer: a :class:`Scorer`. Default: ``ScorerBorda(absent_give_points=True,
        absent_receive_points=None, unordered_give_points=True, unordered_receive_points=False)``.
    :param default_median: the default median of a candidate when it receives no score whatsoever.

    >>> rule = RuleBucklin(ballots=['a > b > c', 'b > a > c', 'c > a > b'])
    >>> rule.scores_
    {'a': (1.0, 3), 'b': (1.0, 2), 'c': (0.0, 3)}
    >>> rule.winner_
    'a'

    For each candidate, its median Borda score is computed. Let ``support`` be the number of voters who assign a
    Borda score that is greater or equal to the median. Then the candidate's score is ``(median, support)``.
    Finally, scores are compared lexicographically.

    When preferences are strict orders, it is equivalent to say that:

        * The candidate with the lowest median rank is declared the winner,
        * If several candidates have the lowest median rank, this tie is broken by examining how many voters rank
          each of them with this rank or lower.
    """

    def __init__(self, ballots: Union[list, Profile] = None, weights: list = None, voters: list = None,
                 candidates: set = None,
                 tie_break: Priority = Priority.UNAMBIGUOUS, converter: ConverterBallot = None,
                 scorer: Scorer = None, default_median: object = 0.):
        # Default value
        if converter is None:
            converter = ConverterBallotToOrder()
        if scorer is None:
            scorer = ScorerBorda(absent_give_points=True, absent_receive_points=None,
                                 unordered_give_points=True, unordered_receive_points=False)
        # Parameters
        self.scorer = scorer
        self.default_median = default_median
        super().__init__(
            ballots=ballots, weights=weights, voters=voters, candidates=candidates,
            tie_break=tie_break, converter=converter
        )

    @cached_property
    def scores_(self) -> NiceDict:
        levels_ = NiceDict({c: [] for c in self.candidates_})
        weights_ = NiceDict({c: [] for c in self.candidates_})
        for ballot, weight, voter in self.profile_converted_.items():
            for c, level in self.scorer(ballot=ballot, voter=voter, candidates=self.candidates_).scores_.items():
                levels_[c].append(level)
                weights_[c].append(weight)
        scores_ = NiceDict()
        for c in self.candidates_:
            if not levels_[c]:
                scores_[c] = (self.default_median, 0)
                continue
            indexes = self.scorer.scale.argsort(levels_[c])
            levels_[c] = [levels_[c][i] for i in indexes]
            weights_[c] = [weights_[c][i] for i in indexes]
            total_weight = sum(weights_[c])
            half_total_weight = total_weight / 2
            cumulative_weight = 0
            median = None
            for i, weight in enumerate(weights_[c]):
                cumulative_weight += weight
                if cumulative_weight >= half_total_weight:
                    median = levels_[c][i]
                    break
            support = sum([weights_[c][i] for i, level in enumerate(levels_[c]) if self.scorer.scale.ge(level, median)])
            scores_[c] = (median, support)
        return scores_

    def compare_scores(self, one: tuple, another: tuple) -> int:
        if one == another:
            return 0
        if self.scorer.scale.lt(one[0], another[0]):
            return -1
        if self.scorer.scale.gt(one[0], another[0]):
            return 1
        return -1 if one[1] < another[1] else 1
