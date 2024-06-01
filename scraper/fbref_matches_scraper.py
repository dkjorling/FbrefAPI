from scraper.fbref_scraper import FbrefScraper

class FbrefMatchesScraper(FbrefScraper):
    """
    FbrefMatchesScraper scrapes and cleans match meta-data from Football Reference.

    There are two distinct match data returned by this class: 

    1) Team match data - When a team id is passed, this signals to the class to retrieve match meta-data for a specific team

    2) League match data - When a team id is not passed but a league id is, this indicates to the class to retrieve match meta-data for a specific league

    Main Functionality Methods
    -------
    scrape_clean_data(self, team_id=None, league_id=None, season_id=None):
        Scrapes and cleans football reference match data for specified team or league

    clean_data(self, matches_table, url):
        Cleans raw players data scraped by the scrape_player_data method
        
    scrape_matches(self, team_id=None, league_id=None, season_id=None):
        Scrapes football reference standings data for a specified football reference league id and season id

    Notes
    -------   
    Team match meta-data when available includes:

        1. match_id - str; 8-character football reference match identification
        2. date - str; date of match in %Y-%m-%d format
        3. time - str; time in %H-%M format
        4. round - str; name of round or matchweek number
        5. league_id - int; football reference league identification that match was played under
        6. home_away - str; whether team played the match at home, neutral or away
        7. opponent - str; name of opposing team
        8. opponent_id - str; 8-character football reference identification of opposing team
        9. result - str; result of match (W = win, L = loss, D = draw)
        10. gf - int; number of goals scored by team in match
        11. ga - int; number of goals conceded by team in match
        12. formation - str; formation played by team
        13. attendance - str; number of people in attedance
        14. captain - str; name of team captain for match
        15. referee - str; name of referee for match
    
    League match meta-data when available includes:
        
        1. match_id - str; 8-character football reference match identification
        2. date - str; date of match in %Y-%m-%d format
        3. time - str; time in %H-%M format
        4. wk - str; name of matchweek if applicable
        5. round - str; name of round if applicable
        6. home - str; name of home team
        7. home_team_id - str; 8-character football reference identification of home team
        8. away - str; name of away team
        9. away_team_id - str; 8-character football reference identification of away team
        10. home_team_score - int; number of goals scored by home team in match
        11. away_team_score - int; number of goals scored by away team in match
        12. venue - str; name of venue played at
        13. attendance - str; number of people in attedance
        14. referee - str; name of referee for match

    """
    # Initialization Methods
    def __init__(self):
        # Call parent class (FbrefScraper) initialization
        super().__init__()
    
    # Main Functionality Methods
    def scrape_clean_data(self, team_id=None, league_id=None, season_id=None):
        """
        Scrapes and cleans football reference match data for specified team or league

        Parameters
        ----------
        team_id : str, optional
            8-character string representing a teams's football reference id. If not provided, defaults to None.
        league_id : int, optional
           Integer representing a player's football reference id. If not provided, defaults to None.
        season_id : str, optional
            Football reference season id. If not provided, defaults to None.
        
        Returns
        -------
        dict
            A dictionary containing the cleaned matches data for a specified league or team
        """
        # Scrape data
        matches_table, url = self.scrape_matches(team_id=team_id,league_id=league_id, season_id=season_id)
        # Clean data
        matches_data_dict_clean = self.clean_data(matches_table, url)
        return matches_data_dict_clean

    def clean_data(self, matches_table, url):
        """
        Cleans football reference match data for specified team or league

        Parameters
        ----------
        matches_table : BeautifulSoup
            BeautifulSoup object representing table with matches data
        url : str
            url which is used to determine whether matches data is for a single team or entire league
        
        Returns
        -------
        dict
            A dictionary containing the cleaned matches data for a specified league or team
        
        Notes
        -------
        This method calls sub-class specific cleaning method, clean_matches
        """
        # Call class-specified cleaning method
        matches_data_dict_clean = self.clean_matches(matches_table, url)
        return matches_data_dict_clean
        
    def scrape_matches(self, team_id=None, league_id=None, season_id=None):
        """
        Scrapes football reference match data for specified team or league

        Parameters
        ----------
        team_id : str, optional
            8-character string representing a teams's football reference id. If not provided, defaults to None.
        league_id : int, optional
           Integer representing a player's football reference id. If not provided, defaults to None.
        season_id : str, optional
            Football reference season id. If not provided, defaults to None.
        
        Returns
        -------
        BeautifulSoup
            A BeautifulSoup object representing a table containing matches data
        """
        # Get proper url
        url = self.get_matches_url(team_id, league_id, season_id)
        # Get data
        soup = self.scrape_data_requests(url)
        all_tables = self.get_all_tables(soup)
        # Get matches table
        matches_table = self.get_matches_table_from_caption(all_tables)
        # Return url to determine matches data type for cleaning step
        return matches_table, url
    
    # Helper methods
    def clean_matches(self, matches_table, url):
        """
        Cleans football reference matches data for specified team or league

        Parameters
        ----------
        matches_table : BeautifulSoup
            BeautifulSoup object representing table with matches data
        url : str
            url which is used to determine whether matches data is for a single team or entire league
        
        Returns
        -------
        dict
            A dictionary containing the cleaned matches data for a specified league or team
        
        """
        # Use url type to determine proper cleaning funciton
        if "comps" in url:
            matches_data_dict = self.clean_league_matches_table(matches_table)
        else:
            matches_data_dict = self.clean_team_matches_table(matches_table)
        # Make sure match ids and league ids have same length as other columns
        no_match_ids = len(matches_data_dict['date']) - len(matches_data_dict['match_id'])
        for _ in range(no_match_ids):
            matches_data_dict['match_id'].append(None)
        if 'league_id' in matches_data_dict.keys():
            no_match_ids = len(matches_data_dict['date']) - len(matches_data_dict['league_id'])
            for _ in range(no_match_ids):
                matches_data_dict['league_id'].append(None)
        # clean team names:
        for key in ['home', 'away', 'opponent']:
            if key in matches_data_dict.keys():
                matches_data_dict[key] = [self.clean_team_name(x) for x in matches_data_dict[key]]
        # delete unwanted keys
        delete_keys = [
            'day', 'xg', 'score', 'match_report', 'notes', 'xga', 'poss'
            ]
        matches_data_dict = self.delete_dict_keys(matches_data_dict, delete_keys)
        # change dtypes
        matches_data_dict = self.convert_matches_dict_dtypes(matches_data_dict)
        # reorder
        new_order = [
            'match_id', 'date', 'time', 'round', 'wk', 'league_id', 'home', 'home_team_id', 'away',
            'away_team_id', 'home_team_score', 'away_team_score', 'home_away', 'opponent',
            'opponent_id', 'result', 'gf', 'ga', 'formation', 'venue', 'attendance', 'captain',
            'referee', 
        ]
        matches_data_dict_clean = self.reorder_dict_keys(matches_data_dict, new_order)
        # reorient dict and return
        matches_data_dict_clean = self.change_dict_orientation(matches_data_dict_clean, id_key='date')
        return matches_data_dict_clean

    def clean_league_matches_table(self, league_matches_table):
        """
        Intermediate cleaning function that takes a league matches table and returns a dictionary

        Parameters
        ----------
        league_matches_table : BeautifulSoup
            BeautifulSoup object representing table with league matches data
        
        Returns
        -------
        dict
            A dictionary containing matches data for a specified league
        
        """
        # Turn table into dict
        league_matches_data_dict = self.parse_table_data(league_matches_table)
        # Get match ids 
        match_ids, _ = self.get_match_id_and_lg_id(league_matches_table)
        league_matches_data_dict['match_id'] = match_ids
        # Get home/away ids and score
        home, away = self.get_home_and_away_ids(league_matches_table)
        league_matches_data_dict['home_team_id'] = home
        league_matches_data_dict['away_team_id'] = away
        league_matches_data_dict['home_team_score'] = [self.clean_score(x)[0] for x in league_matches_data_dict['score']]
        league_matches_data_dict['away_team_score'] = [self.clean_score(x)[0] for x in league_matches_data_dict['score']]
        return league_matches_data_dict

    def clean_team_matches_table(self, team_matches_table):
        """
        Intermediate cleaning function that takes a league matches table and returns a dictionary

        Parameters
        ----------
        team_matches_table : BeautifulSoup
            BeautifulSoup object representing table with team matches data
        
        Returns
        -------
        dict
            A dictionary containing matches data for a specified team
        """
        # Turn table into dict
        team_matches_data_dict = self.parse_table_data(team_matches_table)
        # Get match, league, opponent ids
        match_ids, league_ids = self.get_match_id_and_lg_id(team_matches_table)
        team_matches_data_dict['match_id'] = match_ids
        team_matches_data_dict['league_id'] = league_ids
        opponent_id_patterns = [r"squads/(\w{8})/"]
        team_matches_data_dict['opponent_id'] = self.get_all_items_from_table_urls(team_matches_table, opponent_id_patterns)
        # Rename venue to home_away
        team_matches_data_dict = self.rename_dict_key(team_matches_data_dict, old_key='venue', new_key='home_away')
        # Clean gf ga
        team_matches_data_dict['gf'] = [self.clean_gf_ga(x) for x in team_matches_data_dict['gf']]
        team_matches_data_dict['ga'] = [self.clean_gf_ga(x) for x in team_matches_data_dict['ga']]
        return team_matches_data_dict
    
    def get_match_id_and_lg_id(self, matches_table):
        """
        Get match and league ids from matches table

        Parameters
        ----------
        matches_table : BeautifulSoup
            BeautifulSoup object representing table with matches data
        
        Returns
        -------
        tuple of lists
            A tuple containing a list of match ids and a list of league ids

        """
        match_id_patterns = [r"matches/(\w{8})/"]
        league_id_patterns = [r"comps/(\d+)/"]
        match_ids = self.get_all_items_from_table_urls(matches_table, match_id_patterns)
        league_ids = self.get_all_items_from_table_urls(matches_table, league_id_patterns)
        return match_ids, league_ids
    
    def get_matches_table_from_caption(self, all_tables):
        """
        Given a list of BeautifulSoup tables, identify and return table containing match data.

        Parameters
        ----------
        all_tables : list of BeautifulSoup
            List of BeautifulSoup objects representing tables that were scraped from league-season URL html content
        
        Returns
        -------
        BeautifulSoup
            BeautifulSoup object representing table that contains matches meta-data
            
        Notes
        -----
        This function is a specialization of the generic get_tables_from_caption method in the base class
        """
        patterns = [r"^Scores\s&\sFixtures"]
        matches_table = self.get_tables_from_caption(all_tables, patterns)[0] # find team tables
        return matches_table
    
    def get_home_and_away_ids(self, matches_table):
        """
        Get football reference team ids for home and away teams playing in match.
    
        Parameters
        ----------
        matches_table : BeautifulSoup
            BeautifulSoup object representing table that contains matches meta-data
        
        Returns
        -------
        tuple
            tuple representing hoome and away football reference team ids

        Notes
        -----
        Home and away teams only exist in league matches data therefore this function is specific to league match data.
        """
        # Identify patterns
        team_id_patterns = [r"squads/(\w{8})/"]
        clean_rows = self.parse_table_rows(matches_table)
        home = []
        away = []
        for row in clean_rows[1:]:
            hrefs = [a.get('href') for a in row.find_all('a') if a.get('href')]
            home_away = [] # store home and away ids
            for href in hrefs:
                ha = self.parse_pattern_from_url(team_id_patterns, href)
                if (ha != None) & (ha not in home_away):
                    home_away.append(ha)
            try:
                home.append(home_away[0])
                away.append(home_away[1])
            except:
                home.append(None)
                away.append(None)
        return home, away
    
    def convert_matches_dict_dtypes(self, matches_data_dict):
        """
        Convert specific field's data types from str to either int or float

        Parameters
        ----------
        matches_data_dict : dict
            Dictionary containing raw or partially cleaned data fetched by the scrape_matches_data method

        Returns
        -------
        dict
            Matches data dict with converted data types
            
        Notes
        -----
        This function is a specialization of the generic convert_list_from_str method in the base class
        """
        int_keys = ['home_team_score', 'away_team_score', 'gf', 'ga', 'league_id']
        float_keys = []
        for k in matches_data_dict.keys():
            if k in int_keys:
                matches_data_dict[k] = self.convert_list_from_str(matches_data_dict[k])
            elif k in float_keys:
                matches_data_dict[k] = self.convert_list_from_str(matches_data_dict[k], convert_to='float')
        return matches_data_dict
    
    def clean_score(self, score_raw):
        """
        If data has a score column instead of goals for and goals against, extract home goals and away goals and return

        Parameters
        ----------
        score_raw : str
            Raw goal scored OR goals conceded string
        
        Returns
        -------
        tuple
            home team goals and away team goals
        
        Notes
        -----
        This function should be applied individually to raw gf and ga fields
        """
        split_score = score_raw.split('-')
        if len(split_score) > 1:
            home_team_goals = split_score[0]
            away_team_goals = split_score[1]
        else:
            home_team_goals = None
            away_team_goals = None
        return home_team_goals, away_team_goals
    
    def get_matches_url(self, team_id=None, league_id=None, season_id=None):
        """
        Determine url based on parameters passed

        Parameters
        ----------
        team_id : str, optional
            8-character string representing a teams's football reference id. If not provided, defaults to None.
        league_id : int, optional
           Integer representing a player's football reference id. If not provided, defaults to None.
        season_id : str, optional
            Football reference season id. If not provided, defaults to None.
        
        Returns
        -------
        str
            URL used to scrape data
        """
        # Determine season string 
        if season_id != None:
            season_string = f"{season_id}/"
        else:
            season_string = ""
        try:
            if team_id != None:
                if league_id != None:
                    url = f"https://fbref.com/en/squads/{team_id}/{season_string}matchlogs/c{league_id}/schedule/"
                else:
                    url = f"https://fbref.com/en/squads/{team_id}/{season_string}matchlogs/schedule/"
            elif (team_id == None) & (league_id != None):
                url = f"https://fbref.com/en/comps/{league_id}/{season_string}schedule/"
            return url
        except:
            raise ValueError("Invalid combination of parameters! See class documentation for details.")
    