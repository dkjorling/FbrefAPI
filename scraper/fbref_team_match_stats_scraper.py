import time
from scraper.fbref_stats_scraper import FbrefStatsScraper

class FbrefTeamMatchStatsScraper(FbrefStatsScraper):
    """
    FbrefTeamMatchStatsScraper scrapes and cleans match-level team statistical data for a specified team, league and season.

    Main Functionality Methods
    -------
    scrape_clean_stats(self, team_id, league_id, season_id):
        Scrapes and cleans match-level team statistical data for a specified team, league and season.

    clean_stats(self, team_season_stats_dict):
        Cleans match-level team statistical data for a specified team, league and season.
        
    scrape_all_team_match_stats(self, team_id, season_id, league_id):
        Scrapes match-level team statistical data for a specified team, league and season.

    Notes
    -------   
    This class provides both meta-data related to each match and team statistics in covering various statistical categories.

    Match meta-data when available includes:

    1) match_id - str; 8-character football reference match id  
    2) date - str; date of match in %Y-%m-%d format
    3) round - str; name of round or matchweek number
    4) home_away - str; whether match was played 'Home' or 'Away' or 'Neutral'
    5) opponent - str; name of opposing team
    6) opponent_id str; 8-character football reference team id of opponent 

    Advanced Statistical Categories:

    1) schedule - general team stats such as goals and goals against
    2) keeper - all goalkeeping related stats
    3) shooting - statistics related to team shot taking
    4) passing - statistics related to passing performance
    5) passing_types - statistics related to passing types completed
    6) gca - statistics related to goal- and shot-creating actions
    7) defense - statistics related to defense
    8) possession - statistics related to possession
    9) misc - miscellaneous stats including cards and penalties

    Non-Advanced Statistical Categories:

    1) schedule
    2) keeper
    3) shooting
    4) misc

    ** Detailed statistic descriptions can be found in the API Documentation **
    """
    # Initialization Methods
    def __init__(self):
        # Call parent class (FbrefScraper) initialization
        super().__init__(name='team_match_stats')
    
    # Main Functionality Methods
    def scrape_clean_stats(self, team_id, league_id, season_id):
        """
        Scrapes and cleans football reference match-level team statistics for a specified team, league and season

        Parameters
        ----------
        team_id : str
            8-character string representing football reference team id
        league_id : int
           Integer representing a league's football reference id. 
        season_id : str
            Football reference season id
        
        Returns
        -------
        dict
            A dictionary containing the cleaned match-level team statistical data for a specified team, league and season
        """
        # Scrape Data
        team_match_stats_dict = self.scrape_all_team_match_stats(team_id, league_id, season_id)
        # Clean Data
        team_match_stats_dict_clean = self.clean_stats(team_match_stats_dict)
        return team_match_stats_dict_clean
    
    def clean_stats(self, team_match_stats_dict):
        """
        Cleans football reference match-level team statistics for a specified league and season

        Parameters
        ----------
        team_match_stats_dict : dict
            Dictionary object containing scraped match-level team data from scrape_team_season_stats method
           
        Returns
        -------
        dict
            A dictionary containing the cleaned match-level team statistical data for a specified league and season
        
        Notes
        -------
        This method calls sub-class specific cleaning method, clean_team_match_stats
        """
        # Call class-specified cleaning method
        team_match_stats_dict_clean = self.clean_team_match_stats(team_match_stats_dict)
        return team_match_stats_dict_clean
    
    def scrape_all_team_match_stats(self, team_id, league_id, season_id):
        """
        Scrapes football reference match-level team statistics for a specified team, league and season

        Parameters
        ----------
        team_id : str
            8-character string representing football reference team id
        league_id : int
           Integer representing a league's football reference id. 
        season_id : str
            Football reference season id
        
        Returns
        -------
        dict
            A dictionary containing the raw match-level team statistical data for a specified team, league and season
        
        Notes
        -------
        This method iterates through each stat_id type, calling scrape_team_match_stats method each time
        """
        # Determine whether league has advanced stats and set stat_ids
        has_adv_stats, _ = self.get_league_type_adv(league_id)
        if has_adv_stats == 'yes':
            stat_ids = [
                'schedule', 'keeper', 'shooting', 'passing', 'passing_types', 'gca', 'defense', 'possession', 'misc'
                ]
        else:
            stat_ids = [
                'schedule', 'keeper', 'shooting', 'misc'
            ]
        all_stats_dict = {}
        # Iterate through each stat_id and scrape data
        for stat_id in stat_ids:
            print(stat_id)
            stat_dict = self.scrape_team_match_stats(team_id, season_id, league_id, stat_id)
            all_stats_dict[stat_id] = stat_dict
            time.sleep(3)
        return all_stats_dict
    
    # Helper Methods
    def clean_team_match_stats(self, team_match_stats_dict):
        """
        Cleans football reference match-level team statistics for a specified league and season

        Parameters
        ----------
        team_match_stats_dict : dict
            Dictionary object containing scraped match-level team data from scrape_team_season_stats method
           
        Returns
        -------
        dict
            A dictionary containing the cleaned match-level team statistical data for a specified league and season
        """
        cmap = self.get_adv_or_nadv_cmap(team_match_stats_dict, threshold=5)
        for key in team_match_stats_dict.keys():
            sub_stat_dict = team_match_stats_dict[key]
            sub_stat_dict = self.clean_stat_dict_columns(sub_stat_dict)
            team_match_stats_dict[key] = self.delete_rename_order_convert_sub_stat_dict(sub_stat_dict, key, cmap)
        # reorient
        team_match_stats_dict_clean = self.change_stat_dict_orientation(team_match_stats_dict)
        return team_match_stats_dict_clean
    
    def scrape_team_match_stats(self, team_id, season_id, league_id, stat_id):
        """
        Scrapes football reference match-level team statistics for a specified team, league, season and stat_id

        Parameters
        ----------
        team_id : str
            8-character string representing football reference team id
        league_id : int
           Integer representing a league's football reference id. 
        season_id : str
            Football reference season id
        stat_id : str
            String specifiying the statistical category to scrape
        
        Returns
        -------
        dict
            A dictionary containing the raw match-level team statistical data for a specified team, league, season, and stat id
        """
        url = f"https://fbref.com/en/squads/{team_id}/{season_id}/matchlogs/c{league_id}/{stat_id}"
        soup = self.scrape_data_requests(url)
        stat_table = self.get_all_tables(soup)[0]
        # set skip_row to True for schedule stat id
        if stat_id != 'schedule':
            skip_row = True
            drop_rows = 1
        else:
            skip_row = False
            drop_rows = 0
        stat_dict = self.parse_stat_table_data(stat_table, drop_rows=drop_rows, skip_row=skip_row)
        # get matches
        match_id_patterns = [r"matches/(\w{8})/"]
        stat_dict['match_id']  = self.get_all_items_from_stat_table_urls(stat_table, match_id_patterns, skip_row=skip_row)
        # get opponent id
        opponent_id_patterns = [r"squads/(\w{8})/"]
        stat_dict['opponent_id'] = self.get_all_items_from_stat_table_urls(stat_table, opponent_id_patterns, skip_row=skip_row)
        return stat_dict
    
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
        This method calls sub-class specific cleaning method, change_tms_dict_orientation
        """
        # Call sub-class specified reorientation method
        output_dict = self.change_tms_dict_orientation(input_dict)
        return output_dict
    
    def change_tms_dict_orientation(self, team_match_stats_dict_clean):
        """
        Change dictionary orientation 

        Parameters
        ----------
        team_match_stats_dict_clean : dict
            Dictionary object containing clean or partially clean team-match stats data
           
        Returns
        -------
        dict
            A dictionary with desired orientation
        
         Notes
        -------
        This function specifies the unit of observation of this class as team-league-season-match
        """
        # Create empty output dict
        output_dict = {}
        output_dict['data'] = []
        meta_data = self.column_map['advanced']['meta_data']
        # Determine number of team-match units in dictioanry
        num_matches = len(team_match_stats_dict_clean['schedule']['match_id'])
        # Iterate through each match and append to data
        for i in range(num_matches):
            match_dict = {}
            used_cols = []
            match_dict['meta_data'] = {}
            match_dict['stats'] = {}
            for stat_id in team_match_stats_dict_clean.keys():
                match_dict['stats'][stat_id] = {}
                for stat in team_match_stats_dict_clean[stat_id].keys():
                    if stat in meta_data:
                        try:
                            match_dict['meta_data'][stat]= team_match_stats_dict_clean[stat_id][stat][i]
                        except:
                            match_dict['meta_data'][stat] = None
                    elif stat in used_cols:
                        continue
                    else:
                        try:
                            match_dict['stats'][stat_id][stat]= team_match_stats_dict_clean[stat_id][stat][i]
                            used_cols.append(stat)
                        except:
                            match_dict['stats'][stat_id][stat] = None
            output_dict['data'].append(match_dict)
        return output_dict
    
    
        
    
    
    

        


    