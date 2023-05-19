import nflgame
import numpy as np
import pandas as pd


def main():

	#########
	#Pull in raw depth chart data, fix ARZ to ARI team name, and make names lower case. 
	#Then, sort such that the lowest depth chart position of a player in a given week is at the top for each player and drop duplicates to remove times when one player is in one week's depth chart multiple times
	#Make a csv to check if all this worked
	#Then creat 
	#########
	depth_df = pd.read_csv('depth_league.csv')
	depth_df.loc[depth_df['team'] == 'ARZ', 'team'] = 'ARI'   #change ARZ to ARI
	depth_df['name'] = depth_df['name'].str.lower()  #lower case player names to prevent joining errors
	depth_df = depth_df.sort_values(by=['year', 'week', 'team', 'name', 'depth'])
	depth_df = depth_df.drop_duplicates(['year', 'week', 'team', 'name'])

	depth_df.to_csv('depth_league_mod.csv')

	print('01 depth_df processed')	


	########
	#Pull in raw player performance data
	#Fix a bunch of incorrect team names by changing them all to the most recent version
	#######
	player_df = pd.read_csv('players.csv')
	problem_ids = ['XX-0000001', '00-0032523', '00-0033675']
	player_df = player_df[~player_df['playerid'].isin(problem_ids)]

	for team in ['team', 'opp']:
		player_df.loc[player_df[team] == 'JAC', team] = 'JAX' #change JAC to JAX
		player_df.loc[player_df[team] == 'OAK', team] = 'LV' #change OAK to LV
		player_df.loc[player_df[team] == 'SD', team] = 'LAC' #change SD to LAC
		player_df.loc[player_df[team] == 'STL', team] = 'LAR' #change STL to LAR
		player_df.loc[player_df[team] == 'LA', team] = 'LAR' #change STL to LAR
	
	player_df['name'] = player_df['name'].str.lower() #lower case all names

	print('02 players.csv processed')	

	########
	#create a join list for the first merge. the first merge appends the position and depth number for the cases where a depth_df entry is present for a player entry. the depth_df has been filtered for WR, QB, RB, and TE positions so a bunch of the defensive players in the players_df will not get a position and depth appended (by design). furthermore, if a play came back from injury, he may not be in the depth chart since the depth chart only updated once a month. therefore, those rows in the player_df will also be missing position and depth (will be appended later)
	########
	join_list = ['name', 'team', 'year', 'week']

	player_master_df = player_df.merge(depth_df, how='left', on=join_list)

	player_master_df.to_csv('player_master.csv')

	#appends fantasy points to each row of player dataframe from calc_fantasy_points method
	player_fant_df = calc_fantasy_points(player_master_df)

	print('03 position, depth, and fantasy points appended')

	print('Unique players: ', len(player_fant_df['playerid'].drop_duplicates()))
	print('Total rows: ', len(player_fant_df))	


	########
	#now we have to eliminate the players that aren't in our depth chart (which has been filtered for the relevant positions) from our players_df. to do this, we create temporary simplified player and depth df which only contain team, name, and year for both, but player_temp also has player id. we make a new df that is the intersection of these two temp dfs and this new df contains all the playerids we care about. we then take a subset of the player_fant_df onthe condition that the playerid is in our above intersected df.
	########
	player_temp = player_fant_df[['playerid', 'team', 'name', 'year']]
	depth_temp = depth_df[['team', 'name', 'year']]

	playerids = pd.merge(player_temp, depth_temp, how='inner', on=['team', 'name', 'year'])

	player_fant_df = player_fant_df[player_fant_df['playerid'].isin(playerids['playerid'])]

	player_fant_df.to_csv('player_fant.csv')

	print('04 players not ever in depth chart eliminated')
	print('Unique players: ', len(player_fant_df['playerid'].drop_duplicates()))
	print('Total rows: ', len(player_fant_df))

	########
	#now, we need to append position and depth to the players that were missing from the depth chart, but are still in the player df because they at some point had a position and depth (essentially, the players that aren't in the depth chart because they came from injury before the depth chart was updated)
	########
	player_fant_null_df = player_fant_df[player_fant_df['position'].isnull()]

	for index, row in player_fant_null_df.iterrows():
		#print(index, row['name'], row['playerid'], row['year'])
		
		player_subset_df = player_fant_df[player_fant_df['playerid'] == row['playerid']]
		
		pos = player_subset_df['position'].mode()
		depth = player_subset_df['depth'].mode()
		if len(pos) == 0:
			depth_subset_df = depth_df[(depth_df['name'] == row['name']) & (depth_df['team'] == row['team'])]
			pos = depth_subset_df['position'].mode()
			depth = depth_subset_df['depth'].mode()

		player_fant_df.loc[index, 'position'] = pos.iloc[0]
		player_fant_df.loc[index, 'depth'] = depth.iloc[0]
		
	player_fant_df.to_csv('player_fant.csv')

	print('05 Pos and depth blanks filled in')
	print('Unique players: ', len(player_fant_df['playerid'].drop_duplicates()))
	print('Total rows: ', len(player_fant_df))

	#########
	#filter the dataset to remove players who have played fewer than 3 games, 
	#########

	counts = player_fant_df['playerid'].value_counts()
	games_played_keep = counts[counts > 3].index
	player_filter_df = player_fant_df[player_fant_df['playerid'].isin(games_played_keep)]

	print('06 filtered players played <3 games')
	print('Unique players: ', len(player_filter_df['playerid'].drop_duplicates()))
	print('Total rows: ', len(player_filter_df))

	#########
	#filter the dataset to remove players who have avg < 3 halfppr points, 
	#########

	player_id_list = player_filter_df['playerid'].drop_duplicates()
	halfppr_drop = []

	for index, value in player_id_list.items():
		#about to iterate on playerid and find the mean fantasy points
		playerid = value
		avg_halfppr = player_filter_df[player_filter_df['playerid'] == playerid]['fant_halfppr'].mean()
		if avg_halfppr < 1:
			halfppr_drop.append(playerid)

	player_filter_df = player_filter_df[~player_filter_df['playerid'].isin(halfppr_drop)]

	player_filter_df.to_csv('player_filter.csv')

	print('07 filtered players avg <1 halfppr')
	print('Unique players: ', len(player_filter_df['playerid'].drop_duplicates()))
	print('Total rows: ', len(player_filter_df))

	



		

		
	



def calc_fantasy_points(df):
	'''
	Purpose: to add 3 fantasy points columns to each row of player_master_df, one col for standard points, one for half ppr, one for full ppr

	Inputs
		df: dataframe with all the necessary columns for calculating points
	Outputs
		df: same df with fantasy points columns
	'''
	
	df['fant_stand'] = 0

	df['fant_stand'] += df['passingYds']/25    #passingyds, 1 point per 25 yds
	df['fant_stand'] -= df['INT']*2            #interceptions, 2 points per INT
	df['fant_stand'] += df['passingTDs']*4     #4 pts per passing TD
	df['fant_stand'] += df['rushingYds']/10    #1 point per 10 rushing yds
	df['fant_stand'] += df['rushingTDs']*6     #6 points per rushing TD
	df['fant_stand'] += df['receivingYDs']/10  #1 point per 10 receiving yds
	df['fant_stand'] += df['receivingTDs']*6   #6 points per receiving td
	df['fant_stand'] -= df['fumbles']*2        #-2 points per fumble

	df['fant_halfppr'] = df['fant_stand'] + df['receptions']*0.5
	df['fant_fullppr'] = df['fant_stand'] + df['receptions']

	return df


if __name__ == "__main__":
	main()


