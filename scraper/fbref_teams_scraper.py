import re
from scraper.fbref_scraper import FbrefScraper

class FbrefTeamsScraper(FbrefScraper):
    """
    FbrefTeamsScraper scrapes and cleans football reference team data for a given team and, optionally, season.

    Team data is grouped into two categories:

    1) team_roster
        Contains meta-data for all players who participated for the specified team and season
    
    2) team_schedule
        Contains meta-data for all matches played by specified team and season

    Main Functionality Methods
    -------
    scrape_clean_data(self, team_id, season_id=None):
        Scrapes and cleans football reference teams data for a specified football reference team id and season id

    clean_data(self, team_tables):
        Cleans raw teams data scraped by the scrape_team_data method
        
    scrape_team_data(self, team_id, season_id=None):
        Scrapes football reference standings data for a specified football reference league id and season id

    Notes
    -------   
    Team Roster meta-data, when available includes:

    1) player - str; name of player
    2) player_id - str; 8-character football reference player id string
    3) nationality - str; three-latter football reference country_code to which player belongs
    4) position - str or list of str; position(s) played by player over course of season
    5) age - int; age at start of season
    6) mp - int; number of matches played
    7) starts - int; number of matches started

    Team Schedule meta-data when available includes:

    1) date - str; date of match in %Y-%m-%d format
    2) time - str; time of match (GMT) in %H:%M format
    3) match_id - str; 8-character football reference match id string 
    4) league_name - str; name of league that match was played in
    5) league_id - int; football reference league id number
    6) opponent - str; name of match opponent
    7) opponent_id - str; 8-character football reference opponent team id string
    8) home_away - str; whether game was played home, away or neutral
    9) result - str; result of game from specified team's perspective
    10) gf - int; goals scored by team in match
    11) ga - int; goals scored by opponent in match
    12) attendance - str; number of people who attended match
    13) captain - str; name of team captain in match
    14) formation - str; formation played by team at start of match
    15) referee - str; name of match referee

    """
    # Initialization Methods
    def __init__(self):
        # Call parent class (FbrefEntity) initialization
        super().__init__()
    
    # Main Functionality MEthods
    def scrape_clean_data(self, team_id, season_id=None):
        """
        Scrapes and cleans football reference team data for a specified football reference team id and season id

        Parameters
        ----------
        team_id : str
            8-character string representing a teams's football reference id
        season_id : str, optional
            Football reference season id. If not provided, defaults to None.
        
        Returns
        -------
        dict
            A dictionary containing the cleaned team data for a specified team and season

        Notes
        -------
        ** If no season_id is provided to scrape_clean_data method, data scrape defaults to the most recent season available for specified team **

        """
        # Scrape teams data
        team_tables = self.scrape_team_data(team_id=team_id, season_id=season_id)
        # Clean teams data
        team_data_dict_clean = self.clean_data(team_tables)
        return team_data_dict_clean
    
    def clean_data(self, team_tables):
        """
        Parameters
        ----------
        team_tables : list of BeautifulSoup
            List of BeautifulSoup objects representing team data tables.

            team_tables[0] represents the roster data
            team_tables[1] represents the schedule data
        
        Returns
        -------
        dict
            A dictionary containing the cleaned teams data for a specified team-season
           
        Notes
        -------
        This method calls sub-class specific cleaning method, clean_teams
        """
        # Call sub-class specific cleaning method
        team_data_dict_clean = self.clean_teams(team_tables)
        return team_data_dict_clean

    def scrape_team_data(self, team_id, season_id=None):
        """
        Scrapes raw football reference teams data for a specified football reference team id and season id

        Parameters
        ----------
        team_id : str
            8-digit string representing a teams's football reference id
        season_id : str, optional
            Football reference season id. If not provided, defaults to None.
        
        Returns
        -------
        list of BeautifulSoup
            List of BeautifulSoup objects representing team data tables.

            team_tables[0] represents the roster data
            team_tables[1] represents the schedule data
        
        Notes
        -------
        ** If no season_id is provided to scrape_clean_data method, data scrape defaults to the most recent season available for specified team **

        """
        # Specify url based on parameters passed
        if season_id == None:
            url = f"https://fbref.com/en/squads/{team_id}/"
        else:
            url = f"https://fbref.com/en/squads/{team_id}/{season_id}/"
        # Get data
        soup = self.scrape_data_requests(url)
        all_tables = self.get_all_tables(soup)
        # Identify and return team tables
        team_tables = self.get_team_tables_from_caption(all_tables)
        return team_tables
    
    # Helper Methods
    def clean_teams(self, team_tables):
        """
        Parameters
        ----------
        team_tables : list of BeautifulSoup
            List of BeautifulSoup objects representing team data tables.

            team_tables[0] represents the roster data
            team_tables[1] represents the schedule data
        
        Returns
        -------
        dict
            A dictionary containing the cleaned teams data for a specified team-season
           
        Notes
        -------
        This method calls sub-class specific cleaning method, clean_teams
        """
        # Store data in larger dictionary
        team_data_dict_clean = {}
        # Clean Team Roster data
        team_data_dict_clean['team_roster'] = self.clean_team_roster_table(team_tables[0])
        # Clean Team Schedule data
        team_data_dict_clean['team_schedule'] = self.clean_team_schedule_table(team_tables[1])
        return team_data_dict_clean
    
    def clean_team_roster_table(self, team_roster_table):
        """
        Parameters
        ----------
        team_schedule_table : BeautifulSoup
            BeautifulSoup object representing team schedule table.
        
        Returns
        -------
        dict
            A dictionary containing the cleaned team scehdule dat
        """
        # Transform BeautifulSoup object into dictionary
        roster_data_dict = self.parse_table_data(team_roster_table, skip_row=True)
        # Parse player ids
        player_id_patterns = [r"players/(\w{8})/"]
        roster_data_dict['player_id'] = self.get_all_items_from_table_urls(team_roster_table, player_id_patterns)
        # Clean nationality and age
        roster_data_dict['nationality'] = [self.clean_team_name(x) for x in roster_data_dict['nation']]
        roster_data_dict['age'] = [re.findall(r"(^\d{2}).*", x)[0] if len(re.findall(r"(^\d{2}).*", x)) > 0 else None for x in roster_data_dict['age']]
        # Since only want meta-data, want to delete most statistical data
        delete_keys = [
            'min', '90s', 'gls', 'ast', 'g+a', 'g-pk', 'pk', 'pkatt', 'crdy', 'crdr', 'xg', 'npxg',
            'xag', 'npxg+xag', 'prgc', 'prgp', 'prgr', 'g+a-pk', 'xg+xag', 'matches', 'nation'
            ]
        roster_data_dict = self.delete_dict_keys(roster_data_dict, delete_keys)
        # Rename position key
        roster_data_dict = self.rename_dict_key(roster_data_dict, 'pos', 'position')
        # Convert data types
        roster_data_dict = self.convert_teams_dict_dtypes(roster_data_dict)
        # Reorder keys
        new_order = ['player', 'player_id', 'nationality', 'position', 'age', 'mp', 'starts']
        roster_data_dict = self.reorder_dict_keys(roster_data_dict, new_order)
        # Add nas to player_id for totals so can reorient
        totals_rows = 0 # store for late
        for player in roster_data_dict['player']:
            if "Total" in player:
                roster_data_dict['player_id'].append(None)
                totals_rows += 1
        # Reorient dict
        roster_data_dict = self.change_dict_orientation(roster_data_dict, id_key='player')
        # Delete totals row
        roster_data_dict['data'] = roster_data_dict['data'][:-totals_rows] 
        return roster_data_dict

    def clean_team_schedule_table(self, team_schedule_table):
        """
        Parameters
        ----------
        team_schedule_table : BeautifulSoup
            BeautifulSoup object representing team schedule table.
        
        Returns
        -------
        dict
            A dictionary containing the cleaned team scehdule dat
        """
        # Convert BeautifulSoup table to dict
        schedule_data_dict = self.parse_table_data(team_schedule_table)
        # Get match, league and opponent team ids
        match_id_patterns = [r"matches/(\w{8})/"]
        schedule_data_dict['match_id'] = self.get_all_items_from_table_urls(team_schedule_table, match_id_patterns)
        league_id_patterns = [r"comps/(\d+)/"]
        schedule_data_dict['league_id'] = self.get_all_items_from_table_urls(team_schedule_table, league_id_patterns)
        opponent_id_patterns = [r"squads/(\w{8})/"]
        schedule_data_dict['opponent_id'] = self.get_all_items_from_table_urls(team_schedule_table, opponent_id_patterns)
        schedule_data_dict['opponent'] = [self.clean_team_name(x) for x in schedule_data_dict['opponent']]
        # Clean goals for and goals against data
        schedule_data_dict['gf'] = [self.clean_gf_ga(x) for x in schedule_data_dict['gf']]
        schedule_data_dict['ga'] = [self.clean_gf_ga(x) for x in schedule_data_dict['ga']]
        # Rename keys
        schedule_data_dict = self.rename_dict_key(schedule_data_dict, 'venue', 'home_away')
        schedule_data_dict = self.rename_dict_key(schedule_data_dict, 'comp', 'league_name')
        # Delete unwanted keys
        delete_keys = [
            'xg', 'xga', 'poss', 'match_report', 'notes', 'day'
            ]
        schedule_data_dict = self.delete_dict_keys(schedule_data_dict, delete_keys)
        # Convert data types
        schedule_data_dict = self.convert_teams_dict_dtypes(schedule_data_dict)
        # Reorder keys
        new_order = [
            'date', 'time', 'match_id', 'league_name', 'league_id', 'rounds', 'opponent', 'opponent_id',
            'home_away', 'result', 'gf', 'ga', 'attendance', 'captain', 'formation', 'referee']
        schedule_data_dict = self.reorder_dict_keys(schedule_data_dict, new_order)
        # Some matches havent occured yet and have no match id. Add match ids/league ids so can convert orientation
        no_match_ids = len(schedule_data_dict['date']) - len(schedule_data_dict['match_id'])
        for _ in range(no_match_ids):
            schedule_data_dict['match_id'].append(None)
            schedule_data_dict['league_id'].append(None)
        schedule_data_dict = self.change_dict_orientation(schedule_data_dict, id_key='date')
        return schedule_data_dict
    
    def convert_teams_dict_dtypes(self, team_data_dict):
        """
        Convert specific field's data types from str to either int or float

        Parameters
        ----------
        team_data_dict : dict
            Dictionary containing raw or partially cleaned data fetched by the scrape_team_data method

        Returns
        -------
        dict
            Team data dict with converted data types
            
        Notes
        -----
        This function is a specialization of the generic convert_list_from_str method in the base class
        """
        # Specify integer and float keys
        int_keys = ['age', 'mp', 'starts', 'gf', 'ga', 'league_id']
        float_keys = []
        # Convert keys
        for k in team_data_dict.keys():
            if k in int_keys:
                team_data_dict[k] = self.convert_list_from_str(team_data_dict[k])
            elif k in float_keys:
                team_data_dict[k] = self.convert_list_from_str(team_data_dict[k], convert_to='float')
        return team_data_dict

    def get_team_tables_from_caption(self, all_tables):
        """
        Given a list of BeautifulSoup tables, identify and return tables containing team roster and schedule data.

        Parameters
        ----------
        all_tables : list of BeautifulSoup
            List of BeautifulSoup objects representing tables that were scraped from league-season URL html content
        
        Returns
        -------
        list of BeautifulSoup
            List of BeautifulSoup objects representing tables that contain league-season-details meta-data
            
        Notes
        -----
        This function is a specialization of the generic get_tables_from_caption method in the base class
        """
        # Define patterns and locate/return tables
        patterns = [r"^Scores\s&\sFixtures", r"^Standard\sStats"]
        team_tables = self.get_tables_from_caption(all_tables, patterns) 
        return team_tables
    
    
        
        
        
            
            
        