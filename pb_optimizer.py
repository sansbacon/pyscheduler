#!/usr/bin/env python
# coding: utf-8

# # Using PuLP to Optimize Weekly Schedule

# In[13]:


import itertools

import pandas as pd
import pulp


# In[3]:


players = np.array(['Kumar', 'Peter S.', 'Peter W.', 'Eric',
                    'Rich', 'Matt', 'Calvin', 'Mark',
                    'Natalie', 'Bev', 'Charlie', 'Kimber',
                    'Kevin', 'Josh', 'Jeff', 'Rachel'])


# In[4]:


ranks = np.array([4.7, 5.2, 4.1, 4.5, 4.3, 4.5, 4.3, 4.2, 4.2, 3.9, 4.2, 3.9, 4.3, 4.1, 3.7, 5.0])


# In[56]:


n_courts = 4
n_rounds = 7
rng_courts = np.arange(n_courts) + 1
rng_rounds = np.arange(n_rounds) + 1
court_teams = ('A', 'B')
combos = itertools.product(rng_rounds, rng_courts, court_teams, players)


# In[57]:


# setup problem
# maximize ranks on each court
prob = pulp.LpProblem('PBOpt', pulp.LpMinimize)


# In[58]:


# create variables
# the schedule has 4 parts:
# the round number (here, 1-7)
# the court number (here, 1-4)
# the team (here 'A' or 'B')
# the player
player_schedule_vars = pulp.LpVariable.dicts("player_schedule",
                                        ((round_num, court_num, team, player) 
                                          for round_num, court_num, team, player 
                                          in combos),
                                        cat='Binary')

player_vars = pulp.LpVariable.dicts("players", players, cat="Binary")


# In[59]:


# NOT SURE HOW TO PHRASE OBJECTIVE FUNCTION
# prob += pulp.lpSum([player_vars[player] for player in players])


# In[60]:


# Add constraints
#for slot in range(slots):
#    for role in roles:
#        # In every time slot, each role is assigned to exactly one person
#        problem += pulp.lpSum(assignments[slot, person, role] for person in people) == 1
#
#    for person in people:
#        # Nobody is assigned multiple roles in the same time slot
#        problem += pulp.lpSum(assignments[slot, person, role] for role in roles) <= 1


# In[61]:


# every court side has 2 players
for round_num in rng_rounds:
    for court_num in rng_courts:
        for team in court_teams:
            prob += pulp.lpSum([player_schedule_vars[(round_num, court_num, team, player)] 
                                for player in players]) == 2


# In[64]:


# player can only appear one court per round
for round_num in rng_rounds:
    for player in players:
        prob += pulp.lpSum([player_schedule_vars[(round_num, court_num, team, player)] 
                            for court_num, team in itertools.product(rng_courts, court_teams)]) == 1


# In[65]:


# player can only be partnered with same player once
# struggling with how to express this constraint
#for p1, p2 in itertools.combinations(players, 2):
#    prob += pulp.lpSum([player_schedule_vars[round_num, court_num, team, player])

# conceptually, want to loop through each combination and then
# ensure that the p1 var + p2 var == 1
for p1, p2 in itertools.combinations(players, 2):
    # find all of the matches
    
    
    
    #prob += pulp.lpSum([]) <= 1


# In[ ]:





# In[38]:


# constraint: lineup must have 9 players
prob += pulp.lpSum(player_vars.values()) == 9


# Let's take a look at the problem again. We now see SUBJECT TO _C2, which is a linear equation for the number of players. The sum of the chosen player variables (1) must be = 9.

# In[39]:


prob


# Now we are going to add the positional constraints. You can accomodate the FLEX by setting minimum and maximum counts for the flex-eligible positions. So, here, the constraint is that a lineup must have 2 or more RBs and 3 or less RBs, which meets the minimum requirement of 2 and also allows a lineup to use a third RB in the flex. The same logic applies to the constraints for WR and TE.

# In[40]:


# add positional constraints
prob += pulp.lpSum([v for v, pos in zip(player_vars.values(), df.pos) 
                    if pos == 'QB']) == 1
prob += pulp.lpSum([v for v, pos in zip(player_vars.values(), df.pos) 
                    if pos == 'RB']) >= 2
prob += pulp.lpSum([v for v, pos in zip(player_vars.values(), df.pos) 
                    if pos == 'RB']) <= 3
prob += pulp.lpSum([v for v, pos in zip(player_vars.values(), df.pos) 
                    if pos == 'WR']) >= 3
prob += pulp.lpSum([v for v, pos in zip(player_vars.values(), df.pos) 
                    if pos == 'WR']) <= 4
prob += pulp.lpSum([v for v, pos in zip(player_vars.values(), df.pos) 
                    if pos == 'TE']) >= 1
prob += pulp.lpSum([v for v, pos in zip(player_vars.values(), df.pos) 
                    if pos == 'TE']) <= 2
prob += pulp.lpSum([v for v, pos in zip(player_vars.values(), df.pos) 
                    if pos == 'DST']) == 1

"""
Flexible version

position_slots = (
  ('QB', 'eq', 1),
  ('RB', 'gte', 2),
  ('RB', 'lte', 3),
  ('WR', 'gte', 3),
  ('WR', 'lte', 4),
  ('TE', 'gte', 1),
  ('TE', 'lte', 2),
  ('DST', 'eq', 1),
)

for pos, direction, n in position_slots:
    constraint = pulp.lpSum([v for v, p in zip(player_vars.values(), df.pos) if p == pos])  
    if direction == 'eq':
        prob += constraint == n
    elif direction == 'gte':
        prob += constraint >= n
    elif direction == 'lte':
        prob += constraint <= n
"""
    


# Let's take a look at prob again. We can see that the problem is growing in complexity as we add more constraints. This latest round takes us all the way up to _C10.

# In[41]:


prob


# ## Optional Constraints

# It can be desirable for a lineup to include a QB and a WR from the same team. As explained above, if projections are accurate, then stacking requirements will likely result in a suboptimal lineup. However, projecting the future is fraught with error, so these rules may be a useful way to account for projection error when choosing a lineup because they nudge the solution towards a pairing that empirically tends to do well together (such as QB + WR, QB + WR + Opp WR1, etc.)

# In[26]:


# stacking QB and receiver
for row in df.loc[df.pos == 'QB', :].itertuples(index=False):
    prob += pulp.lpSum([v for k,v in player_vars.items() if
        df.loc[df.full_name == k, 'team'].values[0] == row.team and
                  df.loc[df.full_name == k, 'pos'].values[0] == 'WR'] +
                  [-1 * player_vars[row.full_name]]) >= 0  


# Adding stacking constraints increases the complexity of the problem. With a QB + WR stack, you have to create a new constraint for every QB in your player pool. You can reduce the performance hit from doing so by removing low-scoring (or projected to be low-scoring) QBs from the pool.

# In[ ]:


prob


# In[11]:


# stacking QB and two other players
for row in df.loc[df.pos == 'QB', :].itertuples(index=False):
    prob += pulp.lpSum([v for k,v in player_vars.items() if
                        df.loc[df.full_name == k, 'team'].values[0] == row.team and
                        df.loc[df.full_name == k, 'pos'].values[0] in ('WR', 'TE', 'RB')] +
                        [-2 * player_vars[row.full_name]]) >= 0  


# In[ ]:


# include a bringback
for row in df.loc[df.pos == 'QB', :].itertuples(index=False):
    prob += pulp.lpSum([v for k,v in player_vars.items() if
        df.loc[df.full_name == k, 'team'].values[0] == row.opp and
                  df.loc[df.full_name == k, 'pos'].values[0] == 'WR'] +
                  [-1 * player_vars[row.full_name]]) >= 0


# ## Solve Problem

# In[13]:


# solve problem and print solution
prob.solve()
chosen = [v.name for v in prob.variables() if v.varValue == 1]
solution = df.loc[df.full_name.isin([c.replace('Player_', '') for c in chosen]), list(df.columns)[0:-1]]
print(solution)
print(f'\n{solution.fppg.sum()}')


# In[ ]:




