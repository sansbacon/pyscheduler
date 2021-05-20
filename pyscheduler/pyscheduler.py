"""
pyscheduler.py

Example:

import pulp
from pyscheduler import pyscheduler


s = {'Mark': 4.2,
     'Bev': 3.9,
     'Jeff': 3.7,
     'Peter S': 5.0,
     'Kimber': 3.9,
     'Eric': 4.5,
     'Erik': 4.4,
     'Charlie': 4.3,
     'Paul': 4.3,
     'Rich': 4.4,
     'Ricky': 3.9,
     'Calvin': 4.3,
     'Josh': 4.1,
     'Peter W.': 4.2,
     'Natalie': 4.2,
     'Matt': 4.6
}

n_games = 7

team_combos = list(pulp.combination(s.keys(), 2))
game_combos = pyscheduler._game_combos(team_combos, n_games)
game_scores = pyscheduler._game_scores(game_combos, s)

solver = pulp.get_solver('PULP_CBC_CMD', gapAbs=.8, timeLimit=60)
prob, gcvars = pyscheduler._optimize(team_combos, game_combos, game_scores, list(s.keys()), n_games, solver)
df = pyscheduler._solution(gcvars, s)
try:
    display(df)
except NameError:
    df
pyscheduler._solution_grid(df, list(s.keys()), 'partner')

"""
from collections import defaultdict
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
    # calculate game combinations
    # each item is a 3-tuple of tuple(team1), tuple(team2), game_number
    # the set intersection ensures no common elements between teams
    legal_games = [(t[0], t[1]) for t in pulp.combination(team_combos, 2) 
                   if not set(t[0]) & set(t[1])]
    return [(t1, t2, game_number)
            for game_number in np.arange(n_games) + 1
            for t1, t2 in legal_games]


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


def _opp_report(df, player_names):
    """Generates opponent report"""
    opp = {player: {'partner': defaultdict(int), 'opponent': defaultdict(int)}
           for player in player_names}
    for row in df.itertuples():
        p1, p2 = row.Team1
        p3, p4 = row.Team2
        opp[p1]['partner'][p2] += 1
        opp[p2]['partner'][p1] += 1
        opp[p3]['partner'][p4] += 1
        opp[p4]['partner'][p3] += 1
        opp[p1]['opponent'][p3] += 1
        opp[p1]['opponent'][p4] += 1
        opp[p2]['opponent'][p3] += 1
        opp[p2]['opponent'][p4] += 1
        opp[p3]['opponent'][p1] += 1
        opp[p4]['opponent'][p1] += 1
        opp[p3]['opponent'][p2] += 1
        opp[p4]['opponent'][p2] += 1
    return opp


def _optimize(team_combos, game_combos, game_scores, p, n_games, solver=None):
    """Creates game scores from mapping

    Args:
        team_combos (list[tuple]): the team combos
        game_combos (list[tuple]): the game combos
        game_scores (dict[tuple, float]): the game scores
        p (list[str]): player names
        n_games (int): number of games
        solver (pulp.apis.core.LpSolver): optional solver

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
    # each player must have n_games games
    for player in p:
        prob += pulp.lpSum([v for k, v in gcvars.items()
                        if (player in k[0] or player in k[1])]) == n_games

    # each player has 1 game per game_number
    for player in p:
        for game_number in np.arange(1, n_games + 1):
            prob += pulp.lpSum([v for k, v in gcvars.items()
                                if (player in k[0] or player in k[1]) and
                                k[2] == game_number]) == 1

    # do not play with a player more than once
    # do not play against a player more than twice
    for player in p:
        for pplayer in p:
            if player == pplayer:
                continue
            prob += pulp.lpSum([v for k, v in gcvars.items()
                                if (player in k[0] and pplayer in k[0]) or
                                (player in k[1] and pplayer in k[1])]) <= 1
            prob += pulp.lpSum([v for k, v in gcvars.items()
                                if (player in k[0] and pplayer in k[1]) or
                                (player in k[1] and pplayer in k[0])]) <= 2

    # solve the problem
    if not solver:
        solver = pulp.getSolver('PULP_CBC_CMD', timeLimit=60, gapRel=.05)
    prob.solve(solver)

    return prob, gcvars


def _solution(gcvars, s):
    """Inspects solution

    Args:
        gcvars (dict[str, LpVariable]): the decision variables

    Returns:
        DataFrame

    """
    # look at solution
    df = pd.DataFrame(data=[k for k, v in gcvars.items() if v.varValue == 1], 
                        columns=['Team1', 'Team2', 'Round#'])
    df = df.sort_values('Round#')
    df['Team1_score'] = df['Team1'].apply(lambda x: sum(s.get(i) for i in x))
    df['Team2_score'] = df['Team2'].apply(lambda x: sum(s.get(i) for i in x))
    df = df.assign(Combined_score=lambda x: x['Team1_score'] + x['Team2_score'])
    df = df.assign(Score_diff=lambda x: (np.abs(x['Team1_score'] - x['Team2_score']).round(2)))
    return df


def _solution_grid(df, player_names, grid_type):
    """Generates solution pivot table showing partner or opponent

    Args:
        df (DataFrame): the solution dataframe
        grid_type (str): either 'partner' or 'opponent'

    Returns:
        DataFrame with index player name, columns player name

    """
    orpt = _opp_report(df, player_names)

    # orpt has values for partner and opponent
    # this filters to the correct one
    # key is player name, value is dict of partner/opponent and counts
    d = {k: v[grid_type] for k, v in orpt.items()}
    l = []
    for k, v in d.items():
        for k2, v2 in v.items():
            l.append((k, k2, v2))
    
    return (
        pd.DataFrame(data=l, columns=['player', grid_type, 'n'])
        .pivot(index='player', columns=grid_type, values='n')
        .fillna(0)
        .astype(int)
        .astype(str)
        .replace('0', '')
    )


if '__name__' == '__main__':
    pass
