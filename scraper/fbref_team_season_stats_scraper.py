import time
from scraper.fbref_stats_scraper import FbrefStatsScraper

class FbrefTeamSeasonStatsScraper(FbrefStatsScraper):
    """
    FbrefTeamSeasonStatsScraper scrapes and cleans season-level team statistical data for a specified league and season.

    Statistics are aggregate, average, or per 90 statistics over the course of a single season.

    Main Functionality Methods
    -------
    scrape_clean_stats(self, league_id, season_id=None):
        Scrapes and cleans football reference team-season statistics for a specified league and season

    clean_stats(self, team_season_stats_dict):
        Cleans football reference team-season statistics for a specified league and season
        
    scrape_team_season_stats(self, league_id, season_id=None):
        Scrapes football reference team-season statistics for a specified league and season

    Notes
    -------   
    Advanced Statistical Categories:

    1) stats - general team stats such as goals and goals against
    2) keepers - general goalkeeping statistics
    3) keepersadv - advanced goalkeeping statistics
    4) shooting - statistics related to shot taking
    5) passing - statistics related to passing performance
    6) passing_types - statistics related to passing types completed
    7) gca - statistics related to goal- and shot-creating actions
    8) defense - statistics related to defense
    9) possession - statistics related to possession
    10) playingtime - statistics related to roster playing time
    11) misc - miscellaneous stats including cards and penalties

    Non-Advanced Statistical Categories:

    1) stats
    2) keepers
    3) shooting
    4) playtingtime
    5) misc

    ** Detailed statistic descriptions can be found in the API Documentation **
    """
    # Initialization Methods
    def __init__(self):
        # Call parent class (FbrefStatsScraper) initialization
        super().__init__(name='team_season_stats')

    # Main Functionality Methods
    def scrape_clean_stats(self, league_id, season_id=None):
        """
        Scrapes and cleans football reference season-level team statistics for a specified league and season

        Parameters
        ----------
        league_id : int
           Integer representing a league's football reference id. 
        season_id : str, optional
            Football reference season id. If not provided, defaults to None.
        
        Returns
        -------
        dict
            A dictionary containing the cleaned team-season statistical data for a specified league and season
        """
        # Scrape Data
        team_season_stats_dict = self.scrape_team_season_stats(league_id, season_id)
        # Clean Data
        team_season_stats_dict_clean = self.clean_stats(team_season_stats_dict)
        return team_season_stats_dict_clean
    
    def clean_stats(self, team_season_stats_dict):
        """
        Cleans football reference season-level team statistics for a specified league and season

        Parameters
        ----------
        team_season_stats_dict : dict
            Dictionary object containing scraped team-season data from scrape_team_season_stats method
           
        Returns
        -------
        dict
            A dictionary containing the cleaned team-season statistical data for a specified league and season
        
        Notes
        -------
        This method calls sub-class specific cleaning method, clean_team_season_stats
        """
        # Call class-specified cleaning method
        team_season_stats_dict_clean = self.clean_team_season_stats(team_season_stats_dict)
        return team_season_stats_dict_clean
    
    def scrape_team_season_stats(self, league_id, season_id=None):
        """
        Scrapes football reference season-level team statistics for a specified league and season

        Parameters
        ----------
        league_id : int
           Integer representing a league's football reference id. 
        season_id : str, optional
            Football reference season id. If not provided, defaults to None.
        
        Returns
        -------
        dict
            A dictionary containing the raw team-season statistical data for a specified league and season
        
        Notes
        -------
        This method uses a different scraping method depending on whether the competition is a league or a cup.
        """
        _, league_type = self.get_league_type_adv(league_id)
        if league_type == 'league':
            team_season_stats_dict = self.scrape_stats_from_league(league_id, season_id=season_id)
        elif league_type == 'cup':
            team_season_stats_dict = self.scrape_stats_from_cup(league_id, season_id=season_id)
        else:
            return None
        return team_season_stats_dict
    
    # Helper Methods
    def clean_team_season_stats(self, team_season_stats_dict):
        """
        Cleans football reference team-season statistics for a specified league and season

        Parameters
        ----------
        team_season_stats_dict : dict
            Dictionary object containing scraped team-season data from scrape_team_season_stats method
           
        Returns
        -------
        dict
            A dictionary containing the cleaned team-season statistical data for a specified league and season
        """
        # Get column map
        cmap = self.get_adv_or_nadv_cmap(team_season_stats_dict, threshold=5)
        # Iterate through stat_id keys
        for key in team_season_stats_dict.keys():
            sub_stat_dict = team_season_stats_dict[key]
            sub_stat_dict = self.clean_stat_dict_columns(sub_stat_dict)
            team_season_stats_dict[key] = self.delete_rename_order_convert_sub_stat_dict(sub_stat_dict, key, cmap)
            # Reorient
            team_season_stats_dict_clean = self.change_stat_dict_orientation(team_season_stats_dict)
        return team_season_stats_dict_clean
    
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
        This method calls sub-class specific cleaning method, change_tss_dict_orientation
        """
        # Call subclass-specific reorientation method
        output_dict = self.change_tss_dict_orientation(input_dict)
        return output_dict
        
    def change_tss_dict_orientation(self, team_season_stats_dict_clean):
        """
        Change dictionary orientation of team season stat dictionary

        Parameters
        ----------
        team_season_stats_dict_clean : dict
            Dictionary object containing clean or partially clean team season stats data
           
        Returns
        -------
        dict
            A dictionary with desired orientation
        
        Notes
        -------
        This method specifies the unit of observation of this class as team-league-season
        """
        # Create empty output dict
        output_dict = {}
        output_dict['data'] = []
        meta_data = self.column_map['advanced']['meta_data']
        # Determine number of team-season units in dictioanry
        num_teams = len(team_season_stats_dict_clean['stats']['team_id'])
        # Iterate through each team and append to data
        for i in range(num_teams):
            # For each team define dict and create dictionaries for meta-data and stats
            used_cols = []
            team_dict = {}
            team_dict['meta_data'] = {}
            team_dict['stats'] = {}
            for stat_id in team_season_stats_dict_clean.keys():
                team_dict['stats'][stat_id] = {}
                for stat in team_season_stats_dict_clean[stat_id].keys():
                    if stat in meta_data:
                        try:
                            team_dict['meta_data'][stat]= team_season_stats_dict_clean[stat_id][stat][i]
                        except:
                            team_dict['meta_data'][stat] = None
                    elif stat in used_cols:
                        # Do not repeat stats
                        continue
                    else:
                        try:
                            team_dict['stats'][stat_id][stat]= team_season_stats_dict_clean[stat_id][stat][i]
                            used_cols.append(stat)
                        except:
                            team_dict['stats'][stat_id][stat] = None
            output_dict['data'].append(team_dict)
        return output_dict

    def scrape_stats_from_cup(self, league_id, season_id=None):
        """
        Scrapes football reference team-season statistics for a specified league and season if league type is 'cup'

        Parameters
        ----------
        league_id : int
           Integer representing a player's football reference id. 
        season_id : str, optional
            Football reference season id. If not provided, defaults to None.
        
        Returns
        -------
        dict
            A dictionary containing the raw team-season statistical data for a specified league and season with league type 'cup'
        """
        # Set base url
        if season_id:
            base_url = f"https://fbref.com/en/comps/{league_id}/{season_id}/"
        else:
            base_url = f"https://fbref.com/en/comps/{league_id}/"
        # Determine if the season has advanced stats or not
        has_adv_stats, _ = self.get_league_type_adv(league_id)
        stat_ids = self.get_stat_ids(has_adv_stats)
        stats_dict = {}
        # Iterate through stat_id types
        for stat in stat_ids:
            print(stat)
            try:
                url = base_url + f"{stat}/"
                soup = self.scrape_data_requests(url)
                stat_table = self.get_all_tables(soup)[0]
                stat_dict = self.parse_stat_table_data(stat_table, skip_row=True)
                team_id_patterns = [r"squads/(\w{8})/"]
                stat_dict['team_id'] = self.get_all_items_from_stat_table_urls(stat_table, team_id_patterns, skip_row=True)
                stats_dict[stat] = stat_dict
            except:
                stats_dict[stat] = None
            time.sleep(3) # fbref scraping restriction
        return stats_dict

    def scrape_stats_from_league(self, league_id, season_id=None):
        """
        Scrapes football reference team-season statistics for a specified league and season if league type is 'league'

        Parameters
        ----------
        league_id : int
           Integer representing a player's football reference id. 
        season_id : str, optional
            Football reference season id. If not provided, defaults to None.
        
        Returns
        -------
        dict
            A dictionary containing the raw team-season statistical data for a specified league and season with league type 'league'
        """
        # Set base url
        if season_id:
            url = f"https://fbref.com/en/comps/{league_id}/{season_id}/"
        else:
            url = f"https://fbref.com/en/comps/{league_id}/"
        # Determine if the season has advanced stats or not
        has_adv_stats, _ = self.get_league_type_adv(league_id)
        stat_ids = self.get_stat_ids(has_adv_stats) # use for formatting dict
        stat_patterns = self.get_league_stat_patterns(has_adv_stats) # use for finding stat tables
        soup = self.scrape_data_requests(url)
        all_tables = self.get_all_tables(soup)
        all_stat_tables = self.get_tables_from_caption(all_tables, stat_patterns)
        # Check special case where shooting may or may not be in non advanced stats:
        if (has_adv_stats == 'no') & (len(all_stat_tables)==4):
            stat_ids.remove('passing')
        stats_dict = {}
        # Iterate through stat_id types
        for i, stat_table in enumerate(all_stat_tables):
            stat_dict = self.parse_stat_table_data(stat_table, skip_row=True)
            team_id_patterns = [r"squads/(\w{8})/"]
            stat_dict['team_id'] = self.get_all_items_from_stat_table_urls(stat_table, team_id_patterns, skip_row=True)
            stats_dict[stat_ids[i]] = stat_dict
        return stats_dict

    def get_stat_ids(self, has_adv_stats):
        """
        Determine which statistical id categories are available based on advanced stat designation

        Parameters
        ----------
        has_adv_stats : str
            'yes' or 'no' indicating whether a league-season has advanced statistical data available
        
        Returns
        -------
        list of str
            list containing names of available stat ids
        """
        if has_adv_stats == 'yes':
            stat_ids = [
                'stats', 'keepers', 'keepersadv', 'shooting', 'passing', 'passing_types',
                'gca', 'defense', 'possession', 'playingtime', 'misc'
                ]
        elif has_adv_stats == 'no':
            stat_ids = ['stats', 'keepers', 'shooting', 'playingtime', 'misc']
        else:
            raise ValueError("has_adv_stats argument must be either 'yes' or'no' ")
        return stat_ids
    
    def get_league_stat_patterns(self, has_adv_stats):
        """
        Parameters
        ----------
        has_adv_stats : str
            'yes' or 'no' indicating whether a league-season has advanced statistical data available
        
        Returns
        -------
        list of str
            list containing regex patterns that will be used to identify team-season statistical tables
        
        Notes
        -------
        This method is only called for leagues with type 'league'
        """
        if has_adv_stats == 'yes':
            stat_patterns = [
                r'^Squad\sStandard', r'^Squad\sGoalkeeping', r'^Squad\sAdvanced\sGoalkeeping', r'^Squad\sShooting',
                r'^Squad\sPassing', r'^Squad\sPass\sTypes', r'^Squad\sGoal\sand\sShot\sCreation',
                r'^Squad\sDefensive\sActions', r'^Squad\sPossession', r'^Squad\sPlaying\sTime', r'^Squad\sMiscellaneous'
            ]
        elif has_adv_stats == 'no':
            stat_patterns = [
                r'^Squad\sStandard', r'^Squad\sGoalkeeping',r'^Squad\sShooting', r'^Squad\sPlaying\sTime', r'^Squad\sMiscellaneous'
            ]
        else:
            raise ValueError("has_adv_stats argument must be either 'yes' or'no' ")
        return stat_patterns
    


    