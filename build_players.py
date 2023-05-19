import nflgame
import numpy as np
import pandas as pd


def get_team_stats(game, location):
	'''
	Purpose: To get a row of the team table which will be used to calculate team and opponent records as well as defensive ranks
	
	Inputs
		game: nflgame object representing a single game
		location: either 'home' or 'away'

	Returns
		team_dict: dictionary of various defensive performance stats 
	'''
	
	team_dict = {}

	if location == 'home':
		team_dict['team'] = game.home
		team_dict['opp'] = game.away
		team_dict['points_allowed'] = game.score_away
		game_stats = game.stats_away
	elif location == 'away':
		team_dict['team'] = game.away
		team_dict['opp'] = game.home
		team_dict['points_allowed'] = game.score_home
		game_stats = game.stats_home
	else:
		print('location invalid, must be home or away')
		exit()

	team_dict['home_away'] = location
	team_dict['rushing_yds_allowed'] = game_stats.rushing_yds
	team_dict['passing_yds_allowed'] = game_stats.passing_yds
	team_dict['first_downs_allowed'] = game_stats.first_downs
	
	#in the case of a tie, both teams are assigned as 'loser'
	if team_dict['team'] == game.winner:
		team_dict['win_lose'] = 'win'
	else:
		team_dict['win_lose'] = 'lose'

	return team_dict


def get_player_stats(player, game):
	'''
	Purpose: To get a row of the player table with all the relevant offensive stats of a player from a single game
	
	Inputs
		player: nflgame object representing a single player from a single game

	Returns
		player_dict: dictionary of various individual player offensive performance stats 
	'''


	player_dict = {}
	
	#player_dict['first_name'] = player.player.first_name
	#player_dict['last_name'] = player.player.last_name
	
	player_dict['name'] = player.name
	player_dict['playerid'] = player.playerid
	#player_dict['position'] = player.player.position
	player_dict['team'] = player.team
	
	if player.home == True:
		player_dict['home_away'] = 'home'
		player_dict['opp'] = game.away	
	else:
		player_dict['home_away'] = 'away'
		player_dict['opp'] = game.home	

	player_dict['passingYds'] = player.passing_yds
	player_dict['INT'] = player.passing_int
	player_dict['passingAtt'] = player.passing_att
	player_dict['completions'] = player.passing_cmp
	player_dict['passingTDs'] = player.passing_tds
	player_dict['carries'] = player.rushing_att
	player_dict['rushingYds'] = player.rushing_yds
	player_dict['rushingTDs'] = player.rushing_tds
	player_dict['receptions'] = player.receiving_rec
	player_dict['targets'] = player.receiving_tar
	player_dict['receivingYDs'] = player.receiving_yds
	player_dict['receivingTDs'] = player.receiving_tds
	player_dict['fumbles'] = player.fumbles_tot

	### To be implemented in the future ###
	#weather = 
	#depth chart placement - use link in doc

	return player_dict

def main():

	#defining years and weeks
	#years = np.arange(2009, 2020)
	#weeks = np.arange(1, 18)

	years = [2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019]
	weeks = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
	
	#years = [2015]
	#weeks = [17]

	def_positions = ['CB', 'DT', 'DE', 'SS', 'DB', 'P', 'LB', 'OLB', 'OT', 'ILB', 'FS', 'C', 'OG', 'DL', 'K']

	team_dict_rows = []
	player_dict_rows = []

	for year in years:
		print(year)
		for week in weeks:
			print(week)
			#creates games and players object for my functions
			games = nflgame.games(year, week)
			#print(games.scores)
			for game in games:

				print(game)
				team_dict_row = get_team_stats(game, 'home')
				team_dict_row['year'] = year
				team_dict_row['week'] = week	
				team_dict_rows.append(team_dict_row)
				team_dict_row = get_team_stats(game, 'away')
				team_dict_row['year'] = year
				team_dict_row['week'] = week	
				team_dict_rows.append(team_dict_row)

				if year == 2016 and week == 1 and game.home == 'JAC':
					gam = nflgame.games(year, week, 'JAX', 'GB')
				else:
					gam = nflgame.games(year, week, game.home, game.away)
				
				players = nflgame.combine(gam, plays=True)
				#player = players.name('T.Brady')
				for player in players:
					#print(player.name)
					player_dict_row	= get_player_stats(player, game)

					player_dict_row['year'] = year 
					player_dict_row['week'] = week

					player_dict_rows.append(player_dict_row)

	team_df = pd.DataFrame(team_dict_rows)

	for team in ['team', 'opp']:	
		#fixing team names
		team_df.loc[team_df[team] == 'JAC', team] = 'JAX' #change JAC to JAX
		team_df.loc[team_df[team] == 'OAK', team] = 'LV' #change OAK to LV
		team_df.loc[team_df[team] == 'SD', team] = 'LAC' #change SD to LAC
		team_df.loc[team_df[team] == 'STL', team] = 'LAR' #change STL to LAR
		team_df.loc[team_df[team] == 'LA', team] = 'LAR' #change STL to LAR

	team_df.to_csv('team.csv')
	players_df = pd.DataFrame(player_dict_rows)
	players_df.to_csv('players.csv')			


if __name__ == "__main__":
	main()


