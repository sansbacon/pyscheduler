# -*- coding: utf-8 -*-
# tests/test_pyscheduler.py
from copy import deepcopy
import numpy as np
from numpy.random import default_rng
import pulp
import pytest

from pyscheduler import pyscheduler2


RNG = default_rng()
N_GAMES = 5
DATA = {
    'Mark': 4.2,
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

@pytest.fixture
def o():
    """Generates object"""
    return pyscheduler2.PyScheduler2(N_GAMES, DATA)

@pytest.fixture
def team_combos():
    """"Generates team combos"""
    random_keys = RNG.choice(list(DATA.keys()), N_GAMES + 1)
    random_d = {k: DATA[k] for k in random_keys}
    return list(pulp.combination(random_keys, 2))


@pytest.fixture
def game_combos(o, team_combos):
    """Generates game combos"""
    o2 = deepcopy(o)
    o2._team_combos = team_combos
    return o2.game_combos


def test_game_combos(game_combos):
    assert isinstance(game_combos, list)
    assert isinstance(game_combos[0], tuple)
    assert isinstance(game_combos[0][0], tuple)
    assert isinstance(game_combos[0][0][0], str)


def test_game_scores(o, game_combos):
    """Tests game_scores"""
    o2 = deepcopy(o)
    o2._game_combos = game_combos
    gs = o2.game_scores
    assert isinstance(gs, dict)
    keys = list(gs.keys())
    random_key = keys[RNG.choice(np.arange(len(keys)))]
    assert isinstance(random_key, tuple)
    value = gs[random_key]
    assert isinstance(value, float)