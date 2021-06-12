"""
pyscheduler2.py
pure python implementation of scheduler

TODO: 
  passes basic tests but need to inspect output
  need to test gap implementation
  
"""
from collections import defaultdict
import itertools
import logging
from typing import Dict, List, Union


class PyScheduler2:

    def __init__(self, n_games: int, players: Dict[Union[str, int], float], method: str = 'diff'):
        """Creates new instance

        Args:
            n_games (int): number of games to schedule
            players (dict[Union[str, int], float]): dict of player and score
            method (str, optional): default 'diff', measures relative gap between teams
                                    'gap' measures gap b/w best and worst player

        Returns:
            PyScheduler2

        """
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self.n_games = n_games
        self.method = method
        self.players = players
        self._game_combos = None
        self._game_scores = None
        self._team_combos = None

    @property
    def games(self):
        return range(1, self.n_games + 1)

    @property
    def player_names(self):
        return list(self.players.keys())

    @property
    def player_scores(self):
        return list(self.players.values())

    @property
    def game_combos(self) -> List[tuple]:
        """Creates game combinations from team combinations

        Args:
            None

        Returns:
            list[tuple]

        """
        # calculate game combinations
        # each item is a 3-tuple of tuple(team1), tuple(team2), game_number
        # the set intersection ensures no common elements between teams
        if not self._game_combos:
            legal_games = [(t[0], t[1]) for t in itertools.combinations(self.team_combos, 2) 
                           if not set(t[0]) & set(t[1])]
            self._game_combos = [(t1, t2, gn) for gn in self.games for t1, t2 in legal_games]
        return self._game_combos

    def _gs_diff(self)-> Dict[tuple, float]:
        """Diff method to calculate game_scores
        
        Args:
            None

        Returns:
            dict[tuple, float]

        """
        unique_game_scores = {}
        unique_game_combos = set([(gc[0], gc[1]) for gc in self.game_combos])
        s = self.players
        for gc in unique_game_combos:
            p1, p2 = gc[0]
            p3, p4 = gc[1]
            unique_game_scores[(gc[0], gc[1])] = abs((s[p1] + s[p2]) - (s[p3] + s[p4]))
        return unique_game_scores

    def _gs_gap(self)-> Dict[tuple, float]:
        """Gap method to calculate game_scores
        
        Args:
            None

        Returns:
            dict[tuple, float]

        """
        unique_game_scores = {}
        unique_game_combos = set([(gc[0], gc[1]) for gc in self.game_combos])
        for gc in unique_game_combos:
            scores = [s[p] for p in itertools.chain.from_iterable(gc)]           
            unique_game_scores[(gc[0], gc[1])] = max(scores) - min(scores)
        return unique_game_scores

    @property
    def game_scores(self) -> Dict[tuple, float]:
        """Creates game scores from mapping

        Args:
            None

        Returns:
            dict[tuple, float]

        """
        if not self._game_scores:
            # calculate game score differential
            if self.method == 'diff':
                unique_game_scores = self._gs_diff()
            elif self.method == 'gap':
                unique_game_scores = self._gs_gap()
            else:
                raise ValueError(f'Invalid game_scores method: {method}')
            self._game_scores = {(k[0], k[1], g): v for g in self.games 
                                 for k, v in unique_game_scores.items()}
        return self._game_scores

    @property
    def team_combos(self) -> List[tuple]:
        """Creates team combinations

        Args:
            None

        Returns:
            list[tuple]

        """
        if not self._team_combos:
            self._team_combos = list(itertools.combinations(self.player_names, 2))
        return self._team_combos


if '__name__' == '__main__':
    pass
