import nflgame
import numpy as np
import pandas as pd



def main():

	df = pd.read_csv('player_appended.csv')
	df.loc[df['home_away'] == 'home', 'home_away'] = 0
	df.loc[df['home_away'] == 'away', 'home_away'] = 1

	#### temp modifications
	#df = df[df['position'].isin(['QB', 'RB', 'TE', 'LWR', 'RWR'])]
	####

	feature_list = ['playerid', 'name', 'year', 'week', 'position', 'depth', 'team', 'opp', 'home_away', 'career_games', 'STD_games', 'win_perc_home', 'win_perc_away', 'opp_win_perc_home', 'opp_win_perc_away']

	for span in ['PG', 'P3G', 'STD', 'CTD', 'PGopp', 'P3Gopp']:
		for stat in ['passingYds', 'INT', 'passingAtt', 'completions', 'passingTDs', 'carries', 'rushingYds', 'rushingTDs', 'receptions', 'targets', 'receivingYDs', 'receivingTDs', 'fumbles']:
			feature_list.append(span + '_' + stat)

	feature_list.append('PG_win_perc')
	feature_list.append('P3G_win_perc')
	feature_list.append('STD_win_perc')
	feature_list.append('PGopp_win_perc')

	feature_list.append('opp_PG_win_perc')
	feature_list.append('opp_P3G_win_perc')
	feature_list.append('opp_STD_win_perc')

	for span in ['PG', 'P3G', 'STD']:
		for stat in ['opp_first_downs_allowed', 'opp_passing_yds_allowed', 'opp_rushing_yds_allowed', 'opp_points_allowed']:
			feature_list.append(stat + '_' + span)

	feature_list.append('fant_halfppr')		

	df_train = df[feature_list]

	df_A = df_train.sample(n = 10000, replace = True).reset_index()
	df_A = df_A.rename(columns={'index': 'instance'})
	df_B = df_train.sample(n = 10000, replace = True).reset_index()
	df_B = df_B.rename(columns={'index': 'instance'})

	
	

		 

	#df_train.to_csv('training_AvsB_examples.csv')	


if __name__ == "__main__":
	main()


