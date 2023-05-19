from bs4 import BeautifulSoup
import requests
from datetime import datetime
import pandas as pd


def get_depth_rows(date_num, team, pos_inventory):
	'''
		Purpose: To get rows of the position and depth chart table with name, year, week, team, position, and depth chart placement for all the players on a team for a months worth of games
	
		Inputs
			date_num: string number going into URL to get specific month
			team: string going into URL to get team

		Returns
			depth_dict_rows: array of rows where each row is a dictionary with name, year, week, team, positino, and depth for a single player in a single week 
	'''


	#assume number in url will correspond to month 9,10,11,12
	page = requests.get('https://www.ourlads.com/nfldepthcharts/archive/' + date_num + '/' + team)
	soup = BeautifulSoup(page.content, 'html.parser')

	#date year and month on that page
	date = soup.find('h1').get_text().split('(')[1].split(')')[0]
	year = date.split('/')[2]
	month = date.split('/')[0]
	
	#if statements creating the weeks that month's depth chart positions will be assigned to
	if month == '09':
		weeks = [1, 2, 3, 4]
	elif month == '10':
		weeks = [5, 6, 7, 8]
	elif month == '11':
		weeks = [9, 10, 11, 12]
	elif month == '12':
		weeks = [13, 14, 15, 16, 17]
	else:
		print('number in url giving date with month not 9, 10, 11, or 12')
		exit()

	#all the rows on ourlads that correspond to positions (LWR, RWR,...)
	html_table = soup.find_all('tr', class_=['row-dc-wht', 'row-dc-grey'])

	counter = {}

	counter['WR'] = 1
	counter['LWR'] = 1
	counter['RWR'] = 1
	counter['SWR'] = 1
	counter['TE'] = 1
	counter['QB'] = 1
	counter['RB'] = 1
	counter['RB2'] = 1
	

	depth_dict_rows = []
		

	for row in range(0,len(html_table)):    #iterate through table by rows
	
		html_row = html_table[row].find_all('td') #parse out contents of individual row
	
		pos = html_row[0].get_text() #that row's positions (eg LWR)

		if pos in ['TE/H-', 'TE/HB', 'TE/FB', 'FB/TE']: #converging position name variations
			pos = 'TE'
		if pos == 'RB2':
			pos = 'RB'
		
		if pos in counter.keys():
			for col in [2, 4, 6, 8, 10]:    #iterate through players in row
				name = html_row[col].get_text()
				
				if name != '':    #ignores cells with no players
					if ' , ' in name:
						last_name = name.split(' , ')[0]
						first_name = name.split(' ')[2]
					elif ', ' in name:
						last_name = name.split(', ')[0]
						first_name = name.split(' ')[1]	
					elif ',' not in name:
						last_name = name.split(' ')[0]
						first_name = name.split(' ')[1]
					else:
						print('name is funky on this page')
						exit()

					for week in weeks:       
						depth_dict_row = {}
						depth_dict_row['name'] = first_name[0] + '.' + last_name
						depth_dict_row['year'] = int(year)
						depth_dict_row['week'] = week
						depth_dict_row['team'] = team
						depth_dict_row['position'] = pos
						depth_dict_row['depth'] = counter[pos]
						
						depth_dict_rows.append(depth_dict_row)

					counter[pos] += 1

	return depth_dict_rows, pos_inventory

def main():
	'''
	
	date_nums = ['40',  '41',  '42',  '102', '111', '112', '113', '114','123', '124', '125', '126', '135', '136', '137', '138', '150', '151', '152', '153', '162', '164', '165', '166', '175', '176', '177', '178', '187', '188', '189', '190', '199', '200', '202', '203', '212', '213', '214', '215', '224', '225', '226', '227']  
	
	date_nums = ['111', '112']
	'''
	
	#			 Sep    Oct    Nov    Dec
	date_nums = ['40',  '41',  '42',  '102',  #2009
				 '111', '112', '113', '114',  #2010
				 '123', '124', '125', '126',  #2011
				 '135', '136', '137', '138',  #2012
				 '150', '151', '152', '153',  #2013
				 '162', '164', '165', '166',  #2014
				 '175', '176', '177', '178',  #2015
				 '187', '188', '189', '190',  #2016
				 '199', '200', '202', '203',  #2017
				 '212', '213', '214', '215',  #2018
				 '224', '225', '226', '227'   #2019
				 ] 
		
	
	teams = ['BUF', 'MIA', 'NE', 'NYJ',   #AFC East 
			 'DEN', 'KC', 'LV', 'LAC',    #AFC West
			 'BAL', 'CIN', 'CLE', 'PIT',  #AFC North
			 'HOU', 'IND', 'JAX', 'TEN',  #AFC South
			 'DAL', 'NYG', 'PHI', 'WAS',  #NFC East
			 'ARZ', 'LAR', 'SF', 'SEA',   #NFC West
			 'CHI', 'DET', 'GB', 'MIN',   #NFC North
			 'ATL', 'CAR', 'NO', 'TB'     #NFC South
			 ]
	
	
	#date_nums = ['199']
	#teams = ['ATL']

	depth_dict_all_rows = []
	pos_inventory = []
	for team in teams:
		print(team)
		for date_num in date_nums:
			#print(date_num) 
			depth_dict_rows, pos_inventory = get_depth_rows(date_num, team, pos_inventory)
			depth_dict_all_rows.extend(depth_dict_rows)
			

	depth_df_SF = pd.DataFrame(depth_dict_all_rows)
	depth_df_SF.to_csv('depth_league.csv')

	


if __name__ == "__main__":
	main()
