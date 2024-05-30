from scraper.fbref_stats_scraper import FbrefStatsScraper

class FbrefPlayerSeasonStatsScraper(FbrefStatsScraper):
    """
    FbrefPlayerSeasonStatsScraper scrapes and cleans season-level player statistical data for a specified team, league and season.

    Statistics are aggregate, average, or per 90 statistics over the course of a single season.

    Methods
    -------
    set_stat_patterns(self):
        Set stat_patterns attribute used to identify player season statistical tables


    Main Functionality Methods
    -------
    scrape_clean_stats(self, team_id, league_id=None, season_id=None):
        Scrapes and cleans football reference player-season statistics for a specified league and season

    clean_stats(self, team_season_stats_dict):
        Cleans football reference player-season statistics for a specified league and season
        
    scrape_team_season_stats(self, league_id, season_id=None):
        Scrapes football reference player-season statistics for a specified league and season

    Notes
    -------   
    Advanced Player Statistical Categories:

    1) stats - general team stats such as goals and goals against
    2) shooting - statistics related to shot taking
    3) passing - statistics related to passing performance
    4) passing_types - statistics related to passing types completed
    5) gca - statistics related to goal- and shot-creating actions
    6) defense - statistics related to defense
    7) possession - statistics related to possession
    8) playingtime - statistics related to roster playing time
    9) misc - miscellaneous stats including cards and penalties
    
    Advanced Keeper Statistical Categories:

    1) keepers - general goalkeeping statistics
    2) keepersadv - advanced goalkeeping statistics

    Non-Advanced Statistical Categories:

    1) stats
    2) keepers
    3) shooting
    4) playingtime
    5) misc

    Advanced Keeper Statistical Categories:

    1) keepers

    This class provides both meta-data related to each player and team statistics in covering various statistical categories.

    Player meta-data when available includes:

    1) player_id - str; 8-character football reference player identification 
    2) player_name - str; name of player
    3) player_country_code - str; 3-digit country code attributed to player
    4) age - int; integer age of player at start of season

    ** Detailed statistic descriptions can be found in the API Documentation **
    """
    def __init__(self):
        # Call parent class (FbrefScraper) initialization
        super().__init__(name='player_season_stats')
        self.set_stat_patterns()

    # Initialization Methods
    def set_stat_patterns(self):
        """
        Set stat_patterns attribute used to identify player season statistical tables
        """
        self.stat_patterns = [
                r'^Standard\sStats', r'^Goalkeeping', r'^Advanced\sGoalkeeping', r'^Shooting',
                r'^Passing', r'^Pass\sTypes', r'^Goal\sand\sShot\sCreation',
                r'^Defensive\sActions', r'^Possession', r'^Playing\sTime', r'^Miscellaneous'
            ]

    # Main Functionality Methods
    def scrape_clean_stats(self, team_id, league_id=None, season_id=None):
        """
        Scrapes and cleans football reference season-level player statistics for a specified team, league and season

        Parameters
        ----------
        team_id : str
            8-character string representing football reference team id
        league_id : int
           Integer representing a league's football reference id. If not provided, defaults to None
        season_id : str, optional
            Football reference season id. If not provided, defaults to None.
        
        Returns
        -------
        dict
            A dictionary containing the cleaned player-season statistical data for a specified team, league and season
        """
        # Scrape player-season stat data
        player_season_stats_dict = self.scrape_player_season_stats(team_id, season_id, league_id)
        # Clean  player-season stat data
        player_season_stats_dict_clean = self.clean_stats(player_season_stats_dict)
        return player_season_stats_dict_clean
    
    def clean_stats(self, player_season_stats_dict):
        """
        Cleans football reference season-level player statistics for a specified team, league and season

        Parameters
        ----------
        player_season_stats_dict : dict
            Dictionary object containing scraped player-season data from scrape_team_season_stats method
           
        Returns
        -------
        dict
            A dictionary containing the cleaned player-season statistical data for a specified league and season
        
        Notes
        -------
        This method calls sub-class specific cleaning method, clean_player_season_stats
        """
        # Call class-specified cleaning method
        player_season_stats_dict_clean = self.clean_player_season_stats(player_season_stats_dict)
        return player_season_stats_dict_clean
    
    def scrape_player_season_stats(self, team_id, season_id=None, league_id=None):
        """
        Scrapes football reference season-level player statistics for a specified team, league and season

        Parameters
        ----------
        team_id : str
            8-character string representing football reference team id
        league_id : int
           Integer representing a league's football reference id. If not provided, defaults to None
        season_id : str, optional
            Football reference season id. If not provided, defaults to None.
        
        Returns
        -------
        dict
            A dictionary containing the raw player-season statistical data for a specified team, league and season
        """
        # Define url
        url = self.get_player_season_stats_url(team_id, season_id, league_id)
        # Get data
        soup = self.scrape_data_requests(url)
        all_tables = self.get_all_tables(soup)
        all_stat_tables = self.get_tables_from_caption(all_tables, self.stat_patterns)
        # Set stat ids
        if len(all_stat_tables) > 5:
            stat_ids = [
                'stats', 'keepers', 'keepersadv', 'shooting', 'passing', 'passing_types',
                'gca', 'defense', 'possession', 'playingtime', 'misc'
                ]
        else:
            stat_ids = ['stats', 'keepers', 'shooting', 'playingtime', 'misc']
        # Iterate through each stat id
        stats_dict = {}
        for i, stat_table in enumerate(all_stat_tables):
            stat_dict = self.parse_stat_table_data(stat_table, skip_row=True, exclude_totals=True)
            # get player ids
            player_id_patterns = [r"players/(\w{8})/"]
            stat_dict['player_id'] = self.get_all_items_from_stat_table_urls(stat_table, player_id_patterns, skip_row=True)
            # get player country
            country_patterns = [r"country/([A-Z]{3})/"]
            stat_dict['player_country_code'] = self.get_all_items_from_stat_table_urls(stat_table, country_patterns, skip_row=True)
            stats_dict[stat_ids[i]] = stat_dict
        return stats_dict

    # Helper Methods
    def clean_player_season_stats(self, player_season_stats_dict):
        """
        Cleans football reference season-level player statistics for a specified team, league and season

        Parameters
        ----------
        player_season_stats_dict : dict
            Dictionary object containing scraped player-season data from scrape_team_season_stats method
           
        Returns
        -------
        dict
            A dictionary containing the cleaned player-season statistical data for a specified league and season
        """
        # Set cmap based on advanced stat availability
        cmap = self.get_adv_or_nadv_cmap(player_season_stats_dict, threshold=5)
        # Clean each subdictionary
        for key in player_season_stats_dict.keys():
            sub_stat_dict = player_season_stats_dict[key]
            sub_stat_dict = self.clean_stat_dict_columns(sub_stat_dict)
            player_season_stats_dict[key] = self.delete_rename_order_convert_sub_stat_dict(sub_stat_dict, key, cmap)
        # Reorient
        player_season_stats_dict_clean = self.change_stat_dict_orientation(player_season_stats_dict)
        return player_season_stats_dict_clean

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
        This method calls sub-class specific cleaning method, change_pss_dict_orientation
        """
        # Call subclass-specific reorientation method
        output_dict = self.change_pss_dict_orientation(input_dict)
        return output_dict
    
    def change_pss_dict_orientation(self, player_season_stats_dict_clean):
        """
        Change dictionary orientation  of player-season stat dictionary

        Parameters
        ----------
        team_season_stats_dict_clean : dict
            Dictionary object containing clean or partially clean player season stats data
           
        Returns
        -------
        dict
            A dictionary with desired orientation
        
        Notes
        -------
        This method specifies the unit of observation of this class as player-team-league-season
        """
        # Create empty output dict
        output_dict = {}
        output_dict['players'] = []
        output_dict['keepers'] = []
        meta_data = self.column_map['advanced']['meta_data']
        meta_data = self.column_map['advanced']['meta_data']

        # Get keepers dict to iterate separately
        keeper_season_stats_dict = {}
        nadv_keepers = player_season_stats_dict_clean.pop('keepers')
        keeper_season_stats_dict['keepers'] = nadv_keepers
        if 'keepersadv' in player_season_stats_dict_clean.keys():
            adv_keepers = player_season_stats_dict_clean.pop('keepersadv')
            keeper_season_stats_dict['keepersadv'] = adv_keepers

        # Define data dict of dicts to iterate through
        data = {
            'players': player_season_stats_dict_clean,
            'keepers': keeper_season_stats_dict
        }
        
        # Iterate through data
        for d in list(data.keys()):
            first_key = list(data[d].keys())[0]
            num_players = len(data[d][first_key]['player_id'])
            for i in range(num_players):
                # For each player define dict and create dictionaries for meta-data and stats
                player_dict = {}
                used_cols = []
                player_dict['meta_data'] = {}
                player_dict['stats'] = {}
                # Iterate through each stat id type
                for stat_id in data[d].keys():
                    player_dict['stats'][stat_id] = {}
                    for stat in data[d][stat_id].keys():
                        if stat in meta_data:
                            try:
                                player_dict['meta_data'][stat]= data[d][stat_id][stat][i]
                            except:
                                player_dict['meta_data'][stat] = None
                        elif stat in used_cols:
                            # Do not repeat stats
                            continue
                        else:
                            try:
                                player_dict['stats'][stat_id][stat]= data[d][stat_id][stat][i]
                                used_cols.append(stat)
                            except:
                                player_dict['stats'][stat_id][stat]= None
                # Reorder meta data
                player_dict['meta_data'] = self.reorder_dict_keys(player_dict['meta_data'], list(self.column_map['advanced']['meta_data']))
                output_dict[d].append(player_dict)
        return output_dict

    def get_player_season_stats_url(self, team_id, season_id=None, league_id=None):
        """
        Get appropriate url to scrape from based on parameters passed

         Parameters
        ----------
        team_id : str
            8-character string representing football reference team id
        league_id : int
           Integer representing a league's football reference id. If not provided, defaults to None
        season_id : str, optional
            Football reference season id. If not provided, defaults to None.
        
        Returns
        -------
        str
            URL from which to scrape data from 
        """
        url = f"https://fbref.com/en/squads/{team_id}/"
        if season_id:
            url = url + f"{season_id}/"
        if league_id:
            url = url + f"c{league_id}/"
        else:
            url = url + "all_comps/"
        return url
    
   
    
