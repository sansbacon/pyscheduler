import itertools
import os

from flask import Flask
import numpy as np
import pandas as pd
import pulp
from sheetfu import SpreadsheetApp


app = Flask(__name__)
THRESH = .25
N_GAMES = 5
ssid = '1pviG2swzT_N_DyiMmBH22D0oCQ3bNuliE7-XqF3CY7s'


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
    # no game scores > 1
    for gc in game_combos:
        prob += gcvars[gc] * game_scores[(gc[0], gc[1])] <= 1

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
    for player, pplayer in itertools.combinations(p, 2):
        prob += pulp.lpSum([v for k, v in gcvars.items()
                            if (player in k[0] and pplayer in k[0]) or
                            (player in k[1] and pplayer in k[1])]) <= 2
        prob += pulp.lpSum([v for k, v in gcvars.items()
                            if (player in k[0] and pplayer in k[1]) or
                            (player in k[1] and pplayer in k[0])]) <= 3

    # solve the problem
    if not solver:
        solver = pulp.getSolver('PULP_CBC_CMD', timeLimit=600, gapAbs=2)
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


def _ss_to_df(ws):
    """Creates dataframe from spreadsheet"""
    data = wks.get_all_values()
    headers = data.pop(0)
    return pd.DataFrame(data, columns=headers)


def clear_sheet(s, keep_headers=False):
    """Clears all values in worksheet
    
    Args:
        s (worksheet): sheetfu worksheet object
        keep_headers (bool): keep worksheet headers

    Returns:
        None

    """
    if keep_headers:
        max_row = s.get_max_rows()
        max_column = s.get_max_columns()
        rng = s.get_range(row=2, column=1, number_of_row=max_row - 1, number_of_column=max_column)
    else:
        try:
            rng = s.get_data_range()
        except (ValueError, NoDataRangeError):
            rng = s.get_range(row=1, column=1, number_of_row=500, number_of_column=25)
    rng.set_value('')


def df_to_values(df, include_headers=True):
    """Converts DataFrame to list of tuples to use for sheet values
    
    Args:
        df (DataFrame): the dataframe to convert
        include_headers (bool): include headers in values

    Returns:
        list[tuple]

    """
    if include_headers:
        return [tuple(df.columns)] + list(df.itertuples(index=False, name=None))
    return list(df.itertuples(index=False, name=None))


def get_df_rng(ws, df, start_row=1, start_col=1, include_headers=True):
    """Gets a range that matches size of dataframe"""
    nrow = len(df) + 1 if include_headers else len(df) 
    ncol = len(df.columns)
    return ws.get_range(row=start_row, 
                        column=start_col, 
                        number_of_row=nrow, 
                        number_of_column=ncol)


def df_to_sheet(s, df, include_headers=True):
    """Replaces all values in ws with dataframe values)"""
    # step one: clear existing values
    clear_sheet(s)
    rng = get_df_rng(s, df, include_headers=include_headers)
    vals = df_to_values(df, include_headers=include_headers)
    rng.set_values(vals)
    return True  


def sheet_to_df(s, include_headers=True):
    """Reads a worksheet into a pandas dataframe"""
    rng = s.get_data_range() 
    vals = rng.get_values()
    if include_headers:
        headers = vals.pop(0)
        return (
            pd.DataFrame(data=vals, columns=headers)
        )
    return pd.DataFrame(data=vals)


@app.route('/')
def hello_world():
    #sa = SpreadsheetApp('/content/drive/MyDrive/pickleball-315623-72469838c4d6.json')
    sa = SpreadsheetApp(from_env=True)
    spreadsheet = sa.open_by_id(ssid)
    
    # get player ratings from spreadsheet
    # only uses players marked active
    player_sheet = spreadsheet.get_sheet_by_name('players')
    playerdf = sheet_to_df(player_sheet)
    playerdf.columns = playerdf.columns.str.strip()
    playerdf['Rating'] = playerdf['Rating'].astype(float) 
    playerdf = playerdf.loc[playerdf['Active'] == 'Yes', :]
    s = dict(zip(playerdf['Player'], playerdf['Rating']))

    # create team combos
    team_combos = list(pulp.combination(s.keys(), 2))
    game_combos = _game_combos(team_combos, N_GAMES)
    game_scores = _game_scores(game_combos, s)

    # filter invalid games
    valid_game_scores = {k: v for k,v in game_scores.items() if v <= THRESH}
    valid_game_combos = [(item[0][0], item[0][1], item[1])
                          for item in itertools.product(valid_game_scores.keys(), np.arange(N_GAMES) + 1)]
    valid_team_combos = set([gc[0][0] for gc in valid_game_combos] + [gc[0][1] for gc in valid_game_combos])
    solver = pulp.get_solver('PULP_CBC_CMD', gapAbs=1, timeLimit=300)
    prob, gcvars = _optimize(valid_team_combos, valid_game_combos, valid_game_scores, list(s.keys()), N_GAMES, solver)
    df = _solution(gcvars, s)
    df['Matchup'] = df.apply(lambda x: ' and '.join([p for p in x.Team1]) + '\n' + ' and '.join([p for p in x.Team2]), axis=1)
    df['Court'] = df.groupby('Round#').cumcount() + 1
    pdf = df.pivot(index='Round#', columns='Court', values='Matchup')
    pdf.columns = [f'Court {c}' for c in pdf.columns]
    pdf = pdf.reset_index()
    
    schedule_sheet = spreadsheet.get_sheet_by_name('schedule')
    
    # save to disk
    df_to_sheet(schedule_sheet, pdf)
    
    # clear existing formatting and
    # add alternating formatting to 
    # header and cells with data
    try:
        # clear existing formatting
        cells = schedule_sheet.get_range_from_a1('A1:M13')
        blank_backgrounds = [[''] * 13 for _ in range(13)]
        cells.set_backgrounds(blank_backgrounds)

        # add formatting to schedule
        data_range = schedule_sheet.get_data_range()
        backgrounds = data_range.get_backgrounds()
        new_backgrounds = []
        for idx, row in enumerate(backgrounds):
            n_columns = len(row)
            fmt = ''
            if idx == 0:
                fmt = '#bdbdbd'
            elif idx % 2 == 1:
                fmt = '#f3f3f3'
            new_backgrounds.append([fmt] * n_columns)    
        data_range.set_backgrounds(new_backgrounds)
    except:
        pass
        
    # autosize rows and columns
    try:
        sheetid = 1017411366
        request = {
            "autoResizeDimensions": {
                "dimensions": {
                  "sheetId": sheetid,
                  "dimension": "COLUMNS",
                  "startIndex": 0,
                  "endIndex": 20
                }
            }
        }

        body = {'requests': [request]}
        sa.sheet_service.spreadsheets().batchUpdate(spreadsheetId=ssid, body=body).execute()

        request = {
            "autoResizeDimensions": {
                "dimensions": {
                  "sheetId": sheetid,
                  "dimension": "ROWS",
                  "startIndex": 0,
                  "endIndex": 20
                }
            }
        }

        body = {'requests': [request]}
        sa.sheet_service.spreadsheets().batchUpdate(spreadsheetId=ssid, body=body).execute()
    except:
        pass
    
    try:    
        return pdf.to_html()
    except:
        return 'Hello world!!!'
        
        
if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=int(os.environ.get('PORT', 8080)))
