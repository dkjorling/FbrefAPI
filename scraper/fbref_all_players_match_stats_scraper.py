import re
from scraper.fbref_stats_scraper import FbrefStatsScraper

class FbrefAllPlayersMatchStatsScraper(FbrefStatsScraper):
    """
    FbrefAllPlayersMatchStatsScraper scrapes and cleans match-level player statistical data for both teams for a specified match id

    Main Functionality Methods
    -------
    scrape_clean_stats(self, match_id):
        Scrapes and cleans match-level player statistical data for both teams for a specified match id

    clean_stats(self, all_players_match_stats_dict):
        Cleans match-level player statistical data for both teams for a specified match id
        
    scrape_all_players_match_stats(self, match_id):
        Scrapes match-level player statistical data for both teams for a specified match id

    Notes
    -------   
    This class provides both meta-data related to each player, and match-level player statistics covering various statistical categories.

    Player meta-data when available includes:

    1) player_id - str; 8-character football reference player id  
    2) player_name - str; name of player
    3) player_country_code - str; 3 letter abbreviation of player country
    4) player_number - str; number of player
    5) age - str; 

    Advanced Statistical Player Categories:

    1) summary - general team stats such as goals and goals against
    2) passing - statistics related to passing performance
    3) passing_types - statistics related to passing types completed
    4) defense - statistics related to defense
    5) possession - statistics related to possession
    6) misc - miscellaneous stats including cards and penalties
    7) keeper - basic and advanced keeper stats
    
    Non-Advanced Statistical Categories:

    1) summary
    2) keeper - basic keeper stats
    
    ** Detailed statistic descriptions can be found in the API Documentation **
    """
    # Initialization Methods
    def __init__(self):
        # Call parent class (FbrefScraper) initialization
        super().__init__(name='all_players_match_stats')

    # Main Functionality Methods
    def scrape_clean_stats(self, match_id):
        """
        Scrapes and cleans match-level player statistical data for both teams for a specified match id

        Parameters
        ----------
        match_id : str
            8-character string representing football reference match id
        
        Returns
        -------
        dict
            A dictionary containing the cleaned player-match statistical data for both teams in a specified match
        """
        # Scrape Data
        all_players_match_stats_dict = self.scrape_all_players_match_stats(match_id)
        # Clean Data
        all_players_match_stats_dict_clean = self.clean_stats(all_players_match_stats_dict)
        return all_players_match_stats_dict_clean
    
    def clean_stats(self, all_players_match_stats_dict):
        """
        Cleans match-level player statistical data for both teams for a specified match id

        Parameters
        ----------
        all_players_match_stats_dict : dict
            Dictionary object containing scraped player-match data from scrape_all_players_match_stats method
           
        Returns
        -------
        dict
            A dictionary containing the cleaned player-match statistical data for both teams in a specified match
        
        Notes
        -------
        This method calls sub-class specific cleaning method, clean_player_match_stats
        """
        # Call class-specified cleaning method
        all_players_match_stats_dict_clean = self.clean_all_players_match_stats(all_players_match_stats_dict)
        return all_players_match_stats_dict_clean

    def scrape_all_players_match_stats(self, match_id):
        """
        Scrapes and cleans match-level player statistical data for both teams for a specified match id

        Parameters
        ----------
        match_id : str
            8-character string representing football reference match id
        
        Returns
        -------
        dict
            A dictionary containing the raw player-match statistical data for both teams in a specified match
        """
        # Specify URL and scrape data
        url = f"https://fbref.com/en/matches/{match_id}/"
        soup = self.scrape_data_requests(url)
        all_match_tables = self.get_all_tables(soup)
        # Get other data from BeautifulSoup object and convert to dict
        raw_stats_tables_dict = self.get_home_away_player_stat_tables(all_match_tables)
        for team in raw_stats_tables_dict.keys():
            for key in raw_stats_tables_dict[team]['stat_tables']:
                table = raw_stats_tables_dict[team]['stat_tables'][key]
                # Drop rows for all stat but keeper
                if key == 'keeper':
                    drop_rows = 0
                else:
                    drop_rows = 1
                stat_dict = self.parse_stat_table_data(table, skip_row=True, drop_rows=drop_rows) # skip row for all
                # get player ids
                player_id_patterns = [r"players/(\w{8})/"]
                stat_dict['player_id'] = self.get_all_items_from_stat_table_urls(table, player_id_patterns, skip_row=True)
                # get player country
                country_patterns = [r"country/([A-Z]{3})/"]
                stat_dict['player_country_code'] = self.get_all_items_from_stat_table_urls(table, country_patterns, skip_row=True)
                raw_stats_tables_dict[team]['stat_tables'][key] = stat_dict
        return raw_stats_tables_dict

    # Helper Methods
    def clean_all_players_match_stats(self, all_players_match_stats_dict):
        """
        Cleans match-level player statistical data for both teams for a specified match id

        Parameters
        ----------
        all_players_match_stats_dict : dict
            Dictionary object containing scraped player-match data from scrape_all_players_match_stats method
           
        Returns
        -------
        dict
            A dictionary containing the cleaned player-match statistical data for both teams in a specified match
        """
        # Get correct column map
        t = list(all_players_match_stats_dict.keys())[0]
        cmap = self.get_adv_or_nadv_cmap(all_players_match_stats_dict[t]['stat_tables'], threshold=2)
        # Iterate through keys
        for team in all_players_match_stats_dict.keys():
            for key in all_players_match_stats_dict[team]['stat_tables'].keys():
                sub_stat_dict = all_players_match_stats_dict[team]['stat_tables'][key] # create subdict for clarity
                sub_stat_dict = self.delete_rename_order_convert_sub_stat_dict(sub_stat_dict, key, cmap)
                sub_stat_dict = self.clean_stat_dict_columns(sub_stat_dict) # clean columns
                all_players_match_stats_dict[team]['stat_tables'][key] = sub_stat_dict # reconvert
        # Reorient:
        all_players_match_stats_dict_clean = self.change_stat_dict_orientation(all_players_match_stats_dict)
        return all_players_match_stats_dict_clean
    
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
        This method calls sub-class specific cleaning method, change_apms_dict_orientation
        """
        # Call subclass-specific reorientation method
        output_dict = self.change_apms_dict_orientation(input_dict)
        return output_dict
    
    def change_apms_dict_orientation(self, all_players_match_stats_dict_clean):
        """
        Change dictionary orientation  of all player-seasons stat dictionary

        Parameters
        ----------
        all_players_match_stats_dict_clean : dict
            Dictionary object containing clean or partially clean player match stats data
           
        Returns
        -------
        dict
            A dictionary with desired orientation
        
        Notes
        -------
        This method specifies the unit of observation of this class as player-match
        """
        # Create empty output dict
        output_dict = {}
        output_dict['data'] = []
        meta_data = self.column_map['advanced']['meta_data']
        # Iterate through both teams, creating player and keeper dictioanaries for each
        for team in all_players_match_stats_dict_clean.keys():
            sub_dict = all_players_match_stats_dict_clean[team]
            team_dict = {}
            team_dict['team_name'] = team
            team_dict['home_away'] = sub_dict['home_away']
            team_dict['players'] = []
            team_dict['keepers'] = []
            players_dict = sub_dict['stat_tables']
            keepers_dict = players_dict.pop('keeper')
            
            # Iterate through players
            num_players = len(players_dict['summary']['player_id'])
            for i in range(num_players):
                used_cols = []
                player_dict = {}
                player_dict['meta_data'] = {}
                player_dict['stats'] = {}
                for stat_id in players_dict:
                    player_dict['stats'][stat_id] = {}
                    for stat in players_dict[stat_id].keys():
                        if stat in meta_data:
                            try:
                                player_dict['meta_data'][stat]= players_dict[stat_id][stat][i]
                            except:
                                player_dict['meta_data'][stat] = None
                        elif stat in used_cols:
                            continue
                        else:
                            try:
                                player_dict['stats'][stat_id][stat]= players_dict[stat_id][stat][i]
                                used_cols.append(stat)
                            except:
                                player_dict['stats'][stat_id][stat] = None
                team_dict['players'].append(player_dict)
                        
            # Iterate through keepers
            for j, _ in enumerate(keepers_dict['player_id']):
                keeper_dict = {}
                for key in keepers_dict.keys():
                    try:
                        keeper_dict[key] = keepers_dict[key][j]
                    except:
                        keeper_dict[key] = None
                team_dict['keepers'].append(keeper_dict)
            output_dict['data'].append(team_dict)
        return output_dict

    def get_home_away_player_stat_tables(self, all_match_tables):
        """
        Identify all player-match data table and attribute to either home or away team

        Parameters
        ----------
        all_match_tables : list of BeautifulSoup
            list of BeautifulSoup objects representing player-match table data
        
        Returns
        -------
        dict
            Dict containing raw player match stats for both teams
        """
        # Define empty dict for storing
        raw_stats_tables_dict = {}
        adv_stat_ids = ['summary', 'passing', 'passing_types', 'defense', 'possession', 'misc']
        for i, table in enumerate(all_match_tables):
            num_teams = len(raw_stats_tables_dict.keys())
            if table.caption:
                # Find player and goalkeeper tables
                team_name = re.findall(r"(.*)\s(?:Player|Goalkeeper)\sStats\sTable", table.caption.text)
                if len(team_name) > 0:
                    if num_teams == 0:
                        raw_stats_tables_dict[team_name[0]] = {}
                        raw_stats_tables_dict[team_name[0]]['home_away'] = 'home'
                        raw_stats_tables_dict[team_name[0]]['stat_tables'] = {}
                    elif (team_name[0] not in raw_stats_tables_dict.keys()) & (num_teams == 1):
                        raw_stats_tables_dict[team_name[0]] = {}
                        raw_stats_tables_dict[team_name[0]]['home_away'] = 'away'
                        raw_stats_tables_dict[team_name[0]]['stat_tables'] = {}
                    if len(re.findall(r"Goalkeeper\sStats\sTable", table.caption.text)) > 0:
                        raw_stats_tables_dict[team_name[0]]['stat_tables']['keeper'] = table
                    elif len(raw_stats_tables_dict[team_name[0]]['stat_tables'].keys()) == 0:
                        raw_stats_tables_dict[team_name[0]]['stat_tables']['summary'] = table
                    else:
                        num_stats = len(raw_stats_tables_dict[team_name[0]]['stat_tables'].keys())
                        raw_stats_tables_dict[team_name[0]]['stat_tables'][adv_stat_ids[num_stats]] = table
        return raw_stats_tables_dict
                    

        

            