import nflgame
import numpy as np
import pandas as pd


def append_career_games(index, row, df, df_prior):
	'''
	Purpose: for a given row, append the career game number

	Inputs
		index: index of the row we're appending career game number too
		row: specific row we're appending career game number too
		df: dataframe containing all the rows for all the players
	Outputs
		df: df with career games appended for that row
	'''
	
	if df_prior.empty:
		if row['year'] == 2009 and row['week'] == 1:
			df.loc[index, 'career_games'] = 3
		else:	
			df.loc[index, 'career_games'] = 1
	else:
		career_games = df_prior.iloc[-1]['career_games'] + 1
		df.loc[index, 'career_games'] = career_games
	
	return df

def league_mean(player_df, career_games, position, stat):
	'''
	Purpose: to calculate the career game mean value for the league for a given stat 

	'''
	proxy_df = player_df[(player_df['career_games'] == career_games) & (player_df['position'] == position)]
	value = proxy_df[stat].mean()

	if np.isnan(value):
		proxy_df = player_df[player_df['position'] == position]
		value = proxy_df[stat].mean()	

	return value


def append_PG(index, row, player_df, player_df_prior, player_opp_df, stat):
	'''
	Purpose: for a given row, append stats for the previous game for that player and the opponent

	Inputs
		index: index of the row we're appending stats from previous game
		row: specific row we're appending career game number too
		player_df: dataframe containing all the rows for all the players
		player_df_prior: the subset of the df that contains all the rows just for that player
		team_df: df containing all the defensive stats for opponent
	Outputs
		df: df with values appended
	'''
	
	if player_df_prior.empty:
		value = league_mean(player_df, 1, row['position'], stat)
	else:
		value = player_df_prior[stat].iloc[-1]
	
	player_df.loc[index, 'PG_' + stat] = value

	if player_opp_df.empty:
		proxy_df = player_df[(player_df['opp'] == row['opp']) & (player_df['position'] == row['position']) & (player_df.index < index)]
		if proxy_df.empty:
			value = player_df[(player_df['opp'] == row['opp']) & (player_df['position'] == row['position'])][stat].mean()
		else:
			value = proxy_df.tail(5)[stat].mean()
	else:
		value = player_opp_df[stat].iloc[-1]

	player_df.loc[index, 'PGopp_' + stat] = value

	if np.isnan(value):
		print('nan value: append_PG')
	
	return player_df

def append_P3G(index, row, player_df, player_df_prior, player_opp_df, stat):
	'''
	Purpose: for a given row, append stats for the previous 3 games for that player and the opponent

	Inputs
		index: index of the row we're appending stats from previous game
		row: specific row we're appending career game number too
		player_df: dataframe containing all the rows for all the players
		player_df_prior: the subset of the df that contains all the rows just for that player
		team_df: df containing all the defensive stats for opponent
	Outputs
		df: df with values appended
	'''
	
	if player_df_prior.empty:
		value = league_mean(player_df, 1, row['position'], stat)
	elif len(player_df_prior) == 1:
		value = 0.5*league_mean(player_df, 2, row['position'], stat) + 0.5*player_df_prior[stat].iloc[-1]
	elif len(player_df_prior) == 2:
		value = 0.33*league_mean(player_df, 3, row['position'], stat) + 0.33*player_df_prior[stat].iloc[-1] + 0.33*player_df_prior[stat].iloc[-2]
	elif len(player_df_prior) > 2:
		value = player_df_prior[stat].iloc[[-1, -2, -3]].mean()
	else:
		print('error in append_P3G')
		exit()
	
	player_df.loc[index, 'P3G_' + stat] = value	

	if len(player_opp_df) < 3:
		proxy_df = player_df[(player_df['opp'] == row['opp']) & (player_df['position'] == row['position']) & (player_df.index < index)]
		if proxy_df.empty:
			value = player_df[(player_df['opp'] == row['opp']) & (player_df['position'] == row['position'])][stat].mean()
		else:
			value = proxy_df.tail(5)[stat].mean()
	else:
		value = player_opp_df[stat].iloc[[-1, -2, -3]].mean()

	player_df.loc[index, 'P3Gopp_' + stat] = value
	
	if np.isnan(value):
		print('nan value: append_P3G')

	return player_df

def append_CTD(index, row, player_df, player_df_prior, stat):
	'''
	Purpose: for a given row, append stats for the CTD games for that player and the opponent

	Inputs
		index: index of the row we're appending stats from previous game
		row: specific row we're appending career game number too
		player_df: dataframe containing all the rows for all the players
		player_df_prior: the subset of the df that contains all the rows just for that player
		team_df: df containing all the defensive stats for opponent
	Outputs
		df: df with values appended
	'''

	if player_df_prior.empty:
		value = league_mean(player_df, 1, row['position'], stat)
		ifstat = 'empty'
	else:
		value = player_df_prior[stat].mean()
		ifstat = 'not empty'
	
	player_df.loc[index, 'CTD_' + stat] = value	
	
	if np.isnan(value):
		print('nan value: append_CTD', stat, row['name'], row['year'], row['week'], ifstat)

	return player_df

def append_STD(index, row, player_df, player_df_prior, stat):
	'''
	Purpose: for a given row, append stats for the STD games for that player and the opponent

	Inputs
		index: index of the row we're appending stats from previous game
		row: specific row we're appending career game number too
		player_df: dataframe containing all the rows for all the players
		player_df_prior: the subset of the df that contains all the rows just for that player
		team_df: df containing all the defensive stats for opponent
	Outputs
		df: df with values appended
	'''
	player_df_season = player_df_prior[player_df_prior['year'] == row['year']]
	player_df.loc[index, 'STD_games'] = len(player_df_season)

	if player_df_season.empty and player_df_prior.empty:
		value = league_mean(player_df, 1, row['position'], stat)
	elif player_df_season.empty:
		value = player_df_prior[stat].mean()
	else:
		value = player_df_season[stat].mean()
	
	player_df.loc[index, 'STD_' + stat] = value

	if np.isnan(value):
		print('nan value: append_STD', stat, row['name'], row['year'], row['week'])	
	
	return player_df

def append_win_perc(index, row, player_df, team_df):
	'''
	Purpose: for a given row, append stats for the previous game for that player and the opponent

	Inputs
		index: index of the row we're appending stats from previous game
		row: specific row we're appending career game number too
		player_df: dataframe containing all the rows for all the players
		player_df_prior: the subset of the df that contains all the rows just for that player
		team_df: df containing all the defensive stats for opponent
	Outputs
		df: df with values appended
	'''
	#home team win percentages
	team_prior_df = team_df[(team_df['team'] == row['team']) & (team_df['year'] == row['year']) & (team_df['week'] < row['week'])]

	if team_prior_df.empty == False:
		win_perc_PG = team_prior_df['win_lose'].iloc[-1]
		win_perc_P3G = team_prior_df['win_lose'].tail(3).mean()
		win_perc_STD = team_prior_df['win_lose'].mean()
		win_perc_PGopp = team_prior_df[team_prior_df['opp'] == row['opp']]['win_lose'].tail(3).sum()/len(team_prior_df[team_prior_df['opp'] == row['opp']]['win_lose'].tail(3))
		if np.isnan(win_perc_PGopp):
			win_perc_PGopp = 0.5
	else:
		win_perc_PG = 0.5
		win_perc_P3G = 0.5
		win_perc_STD = 0.5
		win_perc_PGopp = 0.5

	team_home_df = team_df[(team_df['team'] == row['team']) & (team_df['home_away'] == 'home')]
	team_away_df = team_df[(team_df['team'] == row['team']) & (team_df['home_away'] == 'away')]

	win_perc_home = team_home_df['win_lose'].mean()
	win_perc_away = team_away_df['win_lose'].mean()

	player_df.loc[index, 'PG_win_perc'] = win_perc_PG
	player_df.loc[index, 'P3G_win_perc'] = win_perc_P3G
	player_df.loc[index, 'STD_win_perc'] = win_perc_STD
	player_df.loc[index, 'PGopp_win_perc'] = win_perc_PGopp
	player_df.loc[index, 'win_perc_home'] = win_perc_home
	player_df.loc[index, 'win_perc_away'] = win_perc_away


	#opp team win percentages
	opp_prior_df = team_df[(team_df['team'] == row['opp']) & (team_df['year'] == row['year']) & (team_df['week'] < row['week'])]

	if opp_prior_df.empty == False:
		opp_win_perc_PG = opp_prior_df['win_lose'].iloc[-1]
		opp_win_perc_P3G = opp_prior_df['win_lose'].tail(3).mean()
		opp_win_perc_STD = opp_prior_df['win_lose'].mean()
	else:
		opp_win_perc_PG = 0.5
		opp_win_perc_P3G = 0.5
		opp_win_perc_STD = 0.5

	opp_home_df = team_df[(team_df['team'] == row['opp']) & (team_df['home_away'] == 'home')]
	opp_away_df = team_df[(team_df['team'] == row['opp']) & (team_df['home_away'] == 'away')]

	opp_win_perc_home = opp_home_df['win_lose'].mean()
	opp_win_perc_away = opp_away_df['win_lose'].mean()

	player_df.loc[index, 'opp_PG_win_perc'] = opp_win_perc_PG
	player_df.loc[index, 'opp_P3G_win_perc'] = opp_win_perc_P3G
	player_df.loc[index, 'opp_STD_win_perc'] = opp_win_perc_STD
	player_df.loc[index, 'opp_win_perc_home'] = opp_win_perc_home
	player_df.loc[index, 'opp_win_perc_away'] = opp_win_perc_away

	return player_df


def opp_def_stats(index, row, player_df, opp_df, opp_prior_df, stat):

	if opp_prior_df.empty == False:
		PG = opp_prior_df[stat].iloc[-1]
		P3G = opp_prior_df[stat].tail(3).mean()
		STD = opp_prior_df[stat].mean()
	else:
		PG = opp_df[stat].mean()
		P3G = opp_df[stat].mean()
		STD = opp_df[stat].mean()

	player_df.loc[index, 'opp_' + stat + '_PG'] = PG
	player_df.loc[index, 'opp_' + stat + '_P3G'] = P3G
	player_df.loc[index, 'opp_' + stat + '_STD'] = STD

	return player_df



def main():

	player_df = pd.read_csv('player_filter.csv')
	team_df = pd.read_csv('team.csv')
	team_df.loc[team_df['win_lose'] == 'win', 'win_lose'] = 1
	team_df.loc[team_df['win_lose'] == 'lose', 'win_lose'] = 0

	#player_df = player_df[player_df['year'].isin([2009, 2010])]
	#player_df = player_df[(player_df['year'].isin([2009])) & (player_df['name'] == 'b.roethlisberger')]

	#initialize columns to append
	player_df['career_games'] = 0
	player_df['STD_games'] = 0
	time_spans1 = ['PG', 'P3G', 'STD', 'CTD', 'PGopp', 'P3Gopp']
	stats1 = ['passingYds', 'INT', 'passingAtt', 'completions', 'passingTDs', 'carries', 'rushingYds', 'rushingTDs', 'receptions', 'targets', 'receivingYDs', 'receivingTDs', 'fumbles']
	
	stats2 = ['win_perc', 'win_perc_home', 'win_perc_away', 'opp_win_perc', 'opp_win_perc_home', 'opp_win_perc_away']
	stats3 = ['points_allowed', 'rushing_yds_allowed', 'passing_yds_allowed', 'first_downs_allowed']

	for span in time_spans1:
		for stat in stats1:
			player_df[span + '_' + stat] = 0
	

	
	#filling in career_games column
	for index, row in player_df.iterrows():
		player_df_prior = player_df[(player_df['playerid'] == row['playerid']) & (player_df.index < index)]
		player_df = append_career_games(index, row, player_df, player_df_prior)
	print('finished appending career games')

	year = 2009
	week = 1
	print('Year:', year, 'Week:', week)

	#filling in other columns
	for index, row in player_df.iterrows():
		
		player_df_prior = player_df[(player_df['playerid'] == row['playerid']) & (player_df.index < index)]
		player_opp_df = player_df_prior[player_df_prior['opp'] == row['opp']]
		
		for stat in stats1:

			player_df = append_PG(index, row, player_df, player_df_prior, player_opp_df, stat)
			player_df = append_P3G(index, row, player_df, player_df_prior, player_opp_df, stat)
			player_df = append_CTD(index, row, player_df, player_df_prior, stat)
			player_df = append_STD(index, row, player_df, player_df_prior, stat)

		
		player_df = append_win_perc(index, row, player_df, team_df)

		opp_df = team_df[team_df['team'] == row['opp']]
		opp_prior_df = team_df[(team_df['team'] == row['opp']) & (team_df['year'] == row['year']) & (team_df['week'] < row['week'])]

		for stat in stats3:
			player_df = opp_def_stats(index, row, player_df, opp_df, opp_prior_df, stat)


		if row['week'] != week:
			week = row['week']
			year = row['year']
			print('Year:', year, 'Week:', week)



	player_df.to_csv('player_appended.csv')



	



		

		
	






if __name__ == "__main__":
	main()


