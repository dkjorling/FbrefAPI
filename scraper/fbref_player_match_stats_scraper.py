import time
from scraper.fbref_stats_scraper import FbrefStatsScraper

class FbrefPlayerMatchStatsScraper(FbrefStatsScraper):
    """
    FbrefPlayerMatchStatsScraper scrapes and cleans match-level player statistical data for a specified player, league and season.

    Main Functionality Methods
    -------
    scrape_clean_stats(self, team_id, league_id, season_id):
        Scrapes and cleans match-level player statistical data for a specified team, league and season.

    clean_stats(self, team_season_stats_dict):
        Cleans match-level player statistical data for a specified team, league and season.
        
    scrape_all_player_match_stats(self, player_id, season_id, league_id):
        Scrapes match-level team statistical data for a specified team, league and season.

    Notes
    -------   
    ** IMPORTANT **
    
    For players where advanced stats are available, stat id types must be pulled one at a time.
    Football Reference has a scraping restriction of one every 3 seconds. 

    ** Therefore the main class functionality will take over 24 seconds to run each time **

    This class provides both meta-data related to each match and player statistics in covering various statistical categories.

    Match meta-data when available includes:

    1) match_id - str; 8-character football reference match id  
    2) date - str; date of match in %Y-%m-%d format
    3) round - str; name of round or matchweek number
    4) home_away - str; whether match was played 'Home' or 'Away' or 'Neutral'
    5) team_name - str; name of team that player played for
    6) team_id str; 8-character football reference team id for team player played for
    7) opponent - str; name of opposing team
    8) opponent_id str; 8-character football reference team id of opponent 

    Advanced Statistical Player Categories:

    1) summary - general team stats such as goals and goals against
    2) passing - statistics related to passing performance
    3) passing_types - statistics related to passing types completed
    4) gca - statistics related to goal- and shot-creating actions
    5) defense - statistics related to defense
    6) possession - statistics related to possession
    7) misc - miscellaneous stats including cards and penalties

    Non-Advanced Statistical Categories:

    1) summary

    ** Detailed statistic descriptions can be found in the API Documentation **
    """
    # Initialization Methods
    def __init__(self):
        # Call parent class (FbrefScraper) initialization
        super().__init__(name='player_match_stats')

    # Main Functionality Methods
    def scrape_clean_stats(self, player_id, league_id, season_id):
        """
        Scrapes and cleans match-level player statistical data for a specified team, league and season.

        Parameters
        ----------
        player_id : str
            8-character string representing football reference player id
        league_id : int
           Integer representing a league's football reference id.
        season_id : str, optional
            Football reference season id.
        
        Returns
        -------
        dict
            A dictionary containing the cleaned player-match statistical data for a specified team, league and season
        """
        # Scrape player-match data
        player_match_stats_dict = self.scrape_all_player_match_stats(player_id, league_id, season_id)
        # Clean player0-match data
        player_match_stats_dict_clean = self.clean_stats(player_match_stats_dict)
        return player_match_stats_dict_clean
    
    def clean_stats(self, player_match_stats_dict):
        """
        Cleans match-level player statistical data for a specified team, league and season.

        Parameters
        ----------
        player_match_stats_dict : dict
            Dictionary object containing scraped player-match data from scrape_team_season_stats method
           
        Returns
        -------
        dict
            A dictionary containing the cleaned player-season statistical data for a specified league and season
        
        Notes
        -------
        This method calls sub-class specific cleaning method, clean_player_match_stats
        """
        # Call class-specified cleaning method
        player_match_stats_dict_clean = self.clean_player_match_stats(player_match_stats_dict)
        return player_match_stats_dict_clean
    
    def scrape_all_player_match_stats(self, player_id, league_id, season_id):
        """
        Scrapes match-level player statistical data for a specified team, league and season.

        Parameters
        ----------
        player_id : str
            8-character string representing football reference player id
        league_id : int
           Integer representing a league's football reference id.
        season_id : str, optional
            Football reference season id.
        
        Returns
        -------
        dict
            A dictionary containing the raw player-match statistical data for a specified team, league and season

        Notes
        -------
        This method utilizies the scrape_player_match_stats method to scrape data for each stat id
        """
        # Get stat ids 
        has_adv_stats, _ = self.get_league_type_adv(league_id)
        if has_adv_stats == 'yes':
            stat_ids = [
                'summary', 'passing', 'passing_types', 'gca', 'defense', 'possession', 'misc',
                ]
        else:
            stat_ids = [
                'summary'
            ]
        # Scrape for each stat id and create dictionary to store all
        all_stats_dict = {}
        for stat_id in stat_ids:
            print(stat_id)
            stat_dict = self.scrape_player_match_stats(player_id, league_id, season_id, stat_id)
            all_stats_dict[stat_id] = stat_dict
            time.sleep(3) # Sleep for three seconds between each scrape for football reference scraping rules
        return all_stats_dict

    # Helper Methods
    def clean_player_match_stats(self, player_match_stats_dict):
        """
        Cleans match-level player statistical data for a specified team, league and season.

        Parameters
        ----------
        player_match_stats_dict : dict
            Dictionary object containing scraped player-match data from scrape_team_season_stats method
           
        Returns
        -------
        dict
            A dictionary containing the cleaned player-season statistical data for a specified league and season
        """
        cmap = self.get_adv_or_nadv_cmap(player_match_stats_dict, threshold=1)
        for key in player_match_stats_dict.keys():
            sub_stat_dict = player_match_stats_dict[key]
            sub_stat_dict = self.clean_stat_dict_columns(sub_stat_dict)
            player_match_stats_dict[key] = self.delete_rename_order_convert_sub_stat_dict(sub_stat_dict, key, cmap)
        # reorient dict
        player_match_stats_dict_clean = self.change_stat_dict_orientation(player_match_stats_dict)
        return player_match_stats_dict_clean
    
    def change_stat_dict_orientation(self, input_dict):
        """
        Change dictionary orientation 

        Parameters
        ----------
        input_dict : dict
            Dictionary object to be reoriented
           
        Returns
        -------
        dict
            A dictionary with desired orientation

        Notes
        -------
        This method calls sub-class specific cleaning method, change_pms_dict_orientation
        """
        # Call subclass-specific reorientation method
        output_dict = self.change_pms_dict_orientation(input_dict)
        return output_dict
    
    def change_pms_dict_orientation(self, player_match_stats_dict_clean):
        """
        Change dictionary orientation  of player-season stat dictionary

        Parameters
        ----------
        player_match_stats_dict_clean : dict
            Dictionary object containing clean or partially clean player match stats data
           
        Returns
        -------
        dict
            A dictionary with desired orientation
        
        Notes
        -------
        This method specifies the unit of observation of this class as player-league-season
        """
        # Create empty output dict
        output_dict = {}
        output_dict['data'] = []
        meta_data = self.column_map['advanced']['meta_data']
        # Get number of matches in dictionary
        num_matches = len(player_match_stats_dict_clean['summary']['match_id'])
        for i in range(num_matches):
            match_dict = {}
            used_cols = []
            match_dict['meta_data'] = {}
            match_dict['stats'] = {}
            for stat_id in player_match_stats_dict_clean.keys():
                match_dict['stats'][stat_id] = {}
                for stat in player_match_stats_dict_clean[stat_id].keys():
                    if stat in meta_data:
                        try:
                            match_dict['meta_data'][stat]= player_match_stats_dict_clean[stat_id][stat][i]
                        except:
                            match_dict['meta_data'][stat] = None
                    elif stat in used_cols:
                        continue
                    else:
                        try:
                            match_dict['stats'][stat_id][stat]= player_match_stats_dict_clean[stat_id][stat][i]
                            used_cols.append(stat)
                        except:
                            match_dict['stats'][stat_id][stat] = None
            output_dict['data'].append(match_dict)
        return output_dict

    def scrape_player_match_stats(self, player_id, league_id, season_id, stat_id):
        """
        Scrapes match-level player statistical data for a specified team, league and season.

        Parameters
        ----------
        player_id : str
            8-character string representing football reference player id
        league_id : int
           Integer representing a league's football reference id.
        season_id : str
            Football reference season id.
        stat_id : str
            String referencing stat id to scrape. 
        
        Returns
        -------
        dict
            A dictionary containing the raw player-match statistical data for a specified team, league and season
        """
        # Specify URL to scrape
        url = f"https://fbref.com/en/players/{player_id}/matchlogs/{season_id}/c{league_id}/{stat_id}/"
        # Get data
        soup = self.scrape_data_requests(url)
        stat_table = self.get_all_tables(soup)[0]
        # Set rows to drop
        skip_row=True
        drop_rows = 1
        stat_dict = self.parse_stat_table_data(stat_table, skip_row=skip_row, drop_rows=drop_rows) # skip pre-header and drop totals row
        # Get matches
        match_id_patterns = [r"matches/(\w{8})/"]
        stat_dict['match_id']  = self.get_all_items_from_stat_table_urls(stat_table, match_id_patterns, skip_row=skip_row)
        # Team id and opponent team id:
        team_ids, opponent_ids = self.get_team_and_opponent_ids(stat_table, skip_row=skip_row,drop_rows=drop_rows)
        stat_dict['team_id'] = team_ids
        stat_dict['opponent_id'] = opponent_ids
        return stat_dict
    
    def parse_player_match_stat_table_data(self, table, skip_row=False, drop_rows=0, exclude_totals=False):
        """
        Special form of parse_table_data that skips rows where a player did not participate

        Parameters
        ----------
        table : BeautifulSoup
            BeautifulSoup object representing player-match table data
        skip_row : bool
            Determines whether to skip the top row of table or not. If not provided, defaults to False.
        drop_rows : int
            Determines how many rows from bottom of table to ignore. If not provided, defaults to 0
        exclude_totals : bool
            Determines whether or not to exclude the totals row in the table

        Returns
        -------
        dict
            Data dict that was parsed using logic specific to the player-match stats class
        
        """
        clean_rows = self.parse_table_rows(table)
        all_row_data = self.parse_all_row_data(clean_rows)
        # skip_row if passed
        if skip_row == True:
            all_row_data = all_row_data[1:]
        # exclude totals rows if True...this overwrites passed drop_rows
        if exclude_totals == True:
            totals_rows = self.detect_totals_rows(all_row_data)
            drop_rows = totals_rows
        # drop rows if > 0
        if drop_rows > 0:
            all_row_data = all_row_data[:(-drop_rows)]
        # check row length
        header_len = len(all_row_data[0])
        drop = []
        for i,row in enumerate(all_row_data):
            if len(row) != header_len:
                drop.append(i)
        all_row_data = [x for j, x in enumerate(all_row_data) if j not in drop]
        data_dict = self.convert_row_data_to_dict(all_row_data)
        return data_dict

    def get_team_and_opponent_ids(self, stat_table, skip_row=True, drop_rows=1):
        """
        Get team and opponent football reference ids

        Parameters
        ----------
        stat_table : BeautifulSoup
            BeautifulSoup object representing player-match table data
        skip_row : bool
            Determines whether to skip the top row of table or not. If not provided, defaults to True.
        drop_rows : int
            Determines how many rows from bottom of table to ignore. If not provided, defaults to 1
        
        Returns
        -------
        tuple
            Tuple of strings containing team fbref id and opponent fbref id
        """
        # Get team data
        team_id_patterns = [r"squads/(\w{8})/"]
        cleaner_rows = self.parse_stat_table_rows(stat_table, skip_row=skip_row)
        team = []
        opponent = []
        for row in cleaner_rows[1:-drop_rows]:
            hrefs = [a.get('href') for a in row.find_all('a') if a.get('href')]
            home_away = [] # store team and opponent ids
            for href in hrefs:
                ha = self.parse_pattern_from_url(team_id_patterns, href)
                if (ha != None) & (ha not in home_away):
                    home_away.append(ha)
            try:
                team.append(home_away[0])
                opponent.append(home_away[1])
            except:
                team.append(None)
                opponent.append(None)
        return team, opponent
    
     

