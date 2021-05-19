"""
pyscheduler.py

Example:

p = np.array(['Joe', 'Tom', 'Sam', 'Bill', 'Fred', 'John', 'Wex', 'Chip',
            'Mike', 'Jeff', 'Steve', 'Kumar', 'Connor', 'Matt', 'Peter', 'Cindy'])
r = np.array([5.0, 4.2, 4.3, 5.1, 4.4, 3.7, 3.8, 4.6, 3.2, 3.6, 3.8, 4.7, 4.3, 4.6, 4.2, 3.4])
s = dict(zip(p, r))

n_rounds = 7

# calculate team combinations
team_combos = list(pulp.combination(p, 2))

# calculate game combinations / scores
game_combos = _game_combos(team_combos)
game_scores = _game_scores(game_combos, s)

# optimize lineup
prob, gcvars = _optimize(game_combos, game_scores, p, n_rounds)

# inspect solution
_solution(gcvars)

"""

import itertools
import numpy as np
import pandas as pd
import pulp


def _game_combos(team_combos, n_games):
    """Creates game combinations from team combinations

    Args:
        team_combos (list[tuple]): the team combinations
        n_games (int): number of games to schedule

    Returns:
        list[tuple]

    """
    game_combos = []
    for t in team_combos:
        for tt in team_combos:
            if t[0] in tt or t[1] in tt:
                continue
            for round_number in np.arange(n_rounds) + 1:
                game_combos.append((t, tt, round_number))
    return game_combos


def _game_scores(game_combos, s):
    """Creates game scores from mapping

    Args:
        game_combos (list[tuple]): the game combos
        s (dict[str, float]): the game scores

    Returns:
        dict[tuple, float]

    """
    # calculate game score differential
    game_scores = {}
    for gc in game_combos:
        p1, p2 = gc[0]
        p3, p4 = gc[1]
        game_scores[(gc[0], gc[1])] = np.abs((s[p1] + s[p2]) - (s[p3] + s[p4]))
    return game_scores


def _optimize(game_combos, game_scores, p, n_rounds):
    """Creates game scores from mapping

    Args:
        game_combos (list[tuple]): the game combos
        game_scores (dict[tuple, float]): the game scores

    Returns:
        pulp.LpProblem

    """
    # decision variables
    gcvars = pulp.LpVariable.dicts('gc_decvar', game_combos, cat=pulp.LpBinary)

    # create problem
    # minimize game scores subject to constraints
    prob = pulp.LpProblem("PBOpt", pulp.LpMinimize)

    # objective function
    # minimize difference between team scores
    prob += pulp.lpSum([gcvars[gc] * game_scores[(gc[0], gc[1])] for gc in game_combos])

    # constraints
    # each player must have n_rounds games
    for player in p:
        prob += pulp.lpSum([v for k, v in gcvars.items()
                        if (player in k[0] or player in k[1])]) == n_rounds

    # each player has 1 game per round
    for player in p:
        for round_number in np.arange(1, n_rounds + 1):
            prob += pulp.lpSum([v for k, v in gcvars.items()
                                if (player in k[0] or player in k[1]) and
                                k[2] == round_number]) == 1

    # do not play with a player more than twice
    # do not play against a player more than thrice
    for player in p:
        for pplayer in p:
            if player == pplayer:
                continue
            prob += pulp.lpSum([v for k, v in gcvars.items()
                                if (player in k[0] and pplayer in k[0]) or
                                (player in k[1] and pplayer in k[1])]) <= 1
            prob += pulp.lpSum([v for k, v in gcvars.items()
                                if (player in k[0] and pplayer in k[1]) or
                                (player in k[1] and pplayer in k[0])]) <= 3

    # solve the problem
    prob.solve()

    return prob, gcvars


def _solution(gcvars):
    """Inspects solution

    Args:
        gcvars (dict[str, LpVariable]): the decision variables

    Returns:
        DataFrame

    """
    # look at solution
    return pd.DataFrame(data=[k for k, v in gcvars.items() if v.varValue == 1], 
                        columns=['Team1', 'Team2', 'Round#'])


if '__name__' == '__main__':
    pass

