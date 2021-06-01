# pyscheduler/scripts/pb.py

import itertools

import numpy as np
import pulp
from styleframe import StyleFrame, Styler, utils

from pyscheduler import pyscheduler


def run():
    print('Starting lineup generator')

    s = {'Mark P': 4.17,
        'Bev': 3.75,
        'Lefty Mike': 4.08,
        'Eric T': 4.51,
        'Peter W': 4.23,
        'Kimber': 3.8,
        'Charlie': 4.35,
        'Rick': 3.81,
        'Andy': 4.55,
        'Christian': 3.7,
        'Josh W': 4.1,
        'Jeff P': 3.7,
        'Erik P': 4.4,
        'Scott': 3.35,
        'Stu': 3.41,
        'Dave': 3.68,
        'George': 3.62,
        'Casey': 3.54,
        'Mike Ka': 3.66,
        'Vic': 3.51,
        'Guy': 3.17,
        'Pink Floyd': 3.31,
        'Dani': 3.05,
        'Megan': 3.01
    }
    
    # add some noise
    noise = np.random.rand(len(list(s.keys()))) / 100
    for k, n in zip(s, noise):
        s[k] = s[k] + s[k] * n

    thresh = .25
    n_games = 7

    team_combos = list(pulp.combination(s.keys(), 2))
    print('created team combos')
    game_combos = pyscheduler._game_combos(team_combos, n_games)
    print(f'created {len(game_combos)} game combos')
    game_scores = pyscheduler._game_scores(game_combos, s)
    print('created game scores')
    
    # filter invalid games
    valid_game_scores = {k: v for k,v in game_scores.items() if v <= thresh}
    valid_game_combos = [(item[0][0], item[0][1], item[1])
                         for item in itertools.product(valid_game_scores.keys(), np.arange(n_games) + 1)]
    valid_team_combos = set([gc[0][0] for gc in valid_game_combos] + [gc[0][1] for gc in valid_game_combos])
    print(f'filters {len(game_combos)} game combos to {len(valid_game_combos)}')

    solver = pulp.get_solver('PULP_CBC_CMD', gapAbs=1, timeLimit=120)
    prob, gcvars = pyscheduler._optimize(valid_team_combos, valid_game_combos, valid_game_scores, list(s.keys()), n_games, solver)
    df = pyscheduler._solution(gcvars, s)
    print(df)
    print(pyscheduler._solution_grid(df, list(s.keys()), 'partner'))


def style_output(df, savefn, style_params=None):
    """Styles and saves dataframe as excel file"""

    base_params = {
      'font_size': 12,
      'font_family': utils.fonts.arial
      'header_style': {'bold': True, 'font_size': 18},
      'column_width': 30,
      'row_height': 40,
      'shade_color': utils.colors.grey
    }

    p = base_params if not style_params else dict(**base_params, **style_params)
 
    # applies fonts
    default_style = Styler(font=p['font_family'], font_size=p['font_size'])
    sf = StyleFrame(df, styler_obj=default_style)

    # header row
    header_style = Styler(**p['header_style'])
    sf.apply_headers_style(styler_obj=header_style)

    # these work reasonably well without autofitting
    sf.set_column_width(columns=sf.columns, width=p['column_width'])
    sf.set_row_height(rows=sf.row_indexes, height=p['row_height'])

    # shades the even rounds
    sf.apply_style_by_indexes(indexes_to_style=sf[sf['Round#'] % 2 == 0],
                            cols_to_style=list(df.columns),
                            styler_obj=Styler(bg_color=p['shade_color']))

    # save to disk
    sf.to_excel(savefn).save()


if __name__ == '__main__':
    run()

