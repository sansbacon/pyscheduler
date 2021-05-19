# -*- coding: utf-8 -*-
# tests/test_pyscheduler.py
import numpy as np
from numpy.random import default_rng
import pulp
import pytest

from pyscheduler import pyscheduler

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
def team_combos():
    """"Generates team combos"""
    random_keys = RNG.choice(list(DATA.keys()), N_GAMES + 1)
    random_d = {k: DATA[k] for k in random_keys}
    return list(pulp.combination(random_keys, 2))


@pytest.fixture
def game_combos(team_combos):
    """Generates game combos"""
    return pyscheduler._game_combos(team_combos, N_GAMES)


def test_game_combos(team_combos):
    gc = pyscheduler._game_combos(team_combos, N_GAMES)
    assert isinstance(gc, list)
    assert isinstance(gc[0], tuple)
    assert isinstance(gc[0][0], tuple)
    assert isinstance(gc[0][0][0], str)


def test_game_scores(game_combos):
    """Tests game_scores"""
    gs = pyscheduler._game_scores(game_combos, DATA)
    assert isinstance(gs, dict)
    keys = list(gs.keys())
    random_key = keys[RNG.choice(np.arange(len(keys)))]
    assert isinstance(random_key, tuple)
    value = gs[random_key]
    assert isinstance(value, float)