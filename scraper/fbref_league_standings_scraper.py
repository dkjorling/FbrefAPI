from scraper.fbref_scraper import FbrefScraper

class FbrefLeagueStandingsScraper(FbrefScraper):
    """
    FbrefLeagueStandingsScraper scrapes and cleans football reference standings data for a given league-season.

    Standings data varies based on both league type (league or cup) and whether or not the league has advanced stats available on football reference.

    Main Functionality Methods
    -------
    scrape_clean_data(self, league_id, season_id=None):
        Scrapes and cleans football reference standings data for a specified football reference league id and season id

    clean_data(self, league_standings_data_dict):
        Cleans raw league-standings data scraped by the scrape_league_standings_data method
        
    scrape_league_standings_data(self, league_id, season_id=None):
        Scrapes football reference standings data for a specified football reference league id and season id

    Notes
    -------
    ** If season id is not provided, data is scraped for most recent season id for the specified league id **

    Data when available, includes:

        1) rk - int; team standings rank
        2) team_name - str; team name
        3) team_id - str; team football reference id
        4) mp - int; number of matches played
        5) w - int; number of wins
        6) d - int; number of draws
        7) l - int; number of losses
        8) gf - int; goals scored
        9) ga - int; goals scored against
        10) gd - str; goal differential (gf - ga)
        11) pts - int; points won during season; most leagues award 3 points for a win, 1 for a draw, 0 for a loss
        12) xg - float; total expected goals
        13) xga - float; total expected goals against
        14) xgd - str; expected goals diff (xg - xga)
        15) xgd/90 - str; expected goal difference per 90 minutes
    
    """
    # Initialization Methods
    def __init__(self):
        # Call parent class (FbrefScraper) initialization
        super().__init__()
    
    # Main Functionality Methods
    def scrape_clean_data(self, league_id, season_id=None):
        """
        Scrapes and cleans football reference standings data for a specified football reference league id and season id

        Parameters
        ----------
        league_id : int
            Integer representing a league's football reference id
        season_id : str, optional
            Football reference season id. If not provided, defaults to None.
        
        Returns
        -------
        dict
            A dictionary containing the cleaned standings data for a specified league-season
        """
        # Scrape data
        league_standings_data_dict = self.scrape_league_standings_data(league_id, season_id=season_id)
        # Clean data
        league_standings_data_dict_clean = self.clean_data(league_standings_data_dict)
        return league_standings_data_dict_clean
    
    def clean_data(self, league_standings_data_dict):
        """
        Cleans raw league-standings data scraped by the scrape_league_standings_data method

        Parameters
        ----------
        league_standings_data_dict : dict
            Dictionary containing raw data fetched by the scrape_league_standings_data method.

        Returns
        -------
        dict
            A dictionary containing the cleaned standings data for a specified league-season
           
        Notes
        -------
        This method calls sub-class specific cleaning method, clean_league_standings
        """
        # Call sub-class specific cleaning method
        league_standings_data_dict_clean = self.clean_league_standings(league_standings_data_dict)
        return league_standings_data_dict_clean

    def scrape_league_standings_data(self, league_id, season_id=None):
        """
        Scrapes football reference standings data for a specified football reference league id and season id

        Parameters
        ----------
        league_id : int
            Integer representing a league's football reference id
        season_id : str, optional
            Football reference season id. If not provided, defaults to None.
        
        Returns
        -------
        dict
            A dictionary containing the raw standings data for a specified league-season
        """
        if season_id == None:
            url = f"https://fbref.com/en/comps/{league_id}/"
        else:
            url = f"https://fbref.com/en/comps/{league_id}/{season_id}/"
        soup = self.scrape_data_requests(url)
        all_tables = self.get_all_tables(soup)
        standings_tables = self.get_standings_tables_from_caption(all_tables)
        
        league_standings_data_dict = {}
        for table in standings_tables:
            table_name = self.get_table_name(table, remove_table=False)
            if table_name not in league_standings_data_dict.keys():
                sub_dict = self.parse_table_data(table)
                team_id_patterns = [r"squads/(\w{8})/"]
                sub_dict['team_id'] = self.get_all_items_from_table_urls(table, team_id_patterns)
                league_standings_data_dict[table_name] = sub_dict
            else:
                continue
        return league_standings_data_dict
    
    # Helper Methods
    def clean_league_standings(self, league_standings_data_dict):
        """
        Cleans raw league-standings data scraped by the scrape_league_standings_data method

        Parameters
        ----------
        league_standings_data_dict : dict
            Dictionary containing raw data fetched by the scrape_league_standings_data method.

        Returns
        -------
        dict
            A dictionary containing the cleaned standings data for a specified league-season
        """
        league_standings_data_dict_clean = {}
        league_standings_data_dict_clean['data'] = []
        # Iterate through each standings table (For example regular season/playoffs)
        for key in league_standings_data_dict.keys():
            # Create dictionary which will be appended to 'data' in final clean dictionary
            sub_standings_dict = {}
            # Standings type key is simply the name of the specific standings table
            sub_standings_dict['standings_type'] = key
            sub_dict = league_standings_data_dict[key]
            sub_dict = self.convert_standings_dict_dtypes(sub_dict)
            # Check and clean certain keys:
            if 'notes' in sub_dict.keys():
                sub_dict.pop('notes')
            if 'squad' in sub_dict.keys():  # rename squad key to team_name to stay consistent
                self.rename_dict_key(sub_dict, 'squad', 'team_name')
            sub_dict['team_name'] = [self.clean_team_name(x) for x in sub_dict['team_name']]
            # Reorder subdict keys
            sub_dict = self.reorder_standings_dict_keys(sub_dict)
            # Change orientation
            standings_list = self.change_league_standings_dict_orientation(sub_dict)
            # Clean top team scorer
            for d in standings_list:
                if 'top_team_scorer' in d.keys():
                    d = self.clean_top_scorer(d)
            sub_standings_dict['standings'] = standings_list
            league_standings_data_dict_clean['data'].append(sub_standings_dict)

        return league_standings_data_dict_clean
    
    def change_league_standings_dict_orientation(self, league_standings_sub_data_dict):
        """
        This function converts the league-standings data dict from column format to row format, with league id used as unique row identifier.

        Parameters
        ----------
        league_standings_data_dict : dict
            Partially cleaned league-standings data dict with keys representing standings types

        Returns
        -------
        list
            List to be appended to subdictionary
        
        Notes
        -------
        This is a helper function used in the clean_league_standings
        """
        output_list = []
        num_teams = len(league_standings_sub_data_dict['rk'])
        for i in range(num_teams):
            team_dict = {}
            for key in league_standings_sub_data_dict.keys():
                team_dict[key] = league_standings_sub_data_dict[key][i]
            output_list.append(team_dict)
        return output_list

    def clean_top_scorer(self, league_standings_data_dict):
        """
        Takes data dict containing top_scorer data in the form of a list, and converts it to a dictionary with two keys:

            player : list of str; of player(s) who scored the most goals for a given team in the league-season standings
            goals_scored : int; number goals scored by highest scrorer(s) on the given team in the league-season standings

        Parameters
        ----------
        league_standings_data_dict : dict
            Dictionary containing raw or partially cleaned data fetched by the scrape_league_standings_data method.
        
        Returns
        -------
        dict
            League-Standings data dict with clean top scorers dict in place of raw top scorers list
        """
        # Create new temporary key to store original value
        league_standings_data_dict['raw_top_scorer'] = [league_standings_data_dict.pop('top_team_scorer')]
        # Re-define original key as a dictionary instead of a list, adding players and goals_scored as keys which will have list values
        league_standings_data_dict['top_team_scorer'] = {}
        league_standings_data_dict['top_team_scorer']['player'] = []
        league_standings_data_dict['top_team_scorer']['goals_scored'] = []
        # Iterate through each raw top scorer in the data dict
        for scorer in league_standings_data_dict['raw_top_scorer']:
            # Split players from goals while keeping players with hyphonated names in tact and append to new dictionary
            p_n = scorer.split('-')
            if len(' '.join(p_n[:-1]).split(',')) > 1:
                league_standings_data_dict['top_team_scorer']['player'].append(' '.join(p_n[:-1]).split(','))
            else:
                league_standings_data_dict['top_team_scorer']['player'].append(' '.join(p_n[:-1]))
            league_standings_data_dict['top_team_scorer']['goals_scored'].append(int(p_n[-1]))
        # Delete the temporary key
        league_standings_data_dict.pop('raw_top_scorer')
        # Convet goals scored from a list to a single number if list length is one
        if len(league_standings_data_dict['top_team_scorer']['goals_scored']) == 1:
            league_standings_data_dict['top_team_scorer']['goals_scored'] = league_standings_data_dict['top_team_scorer']['goals_scored'][0]
        return league_standings_data_dict
    
    def reorder_standings_dict_keys(self, league_standings_data_dict):
        """
        Re-order keys in league-standings data dictionary

        Parameters
        ----------
        league_standings_data_dict : dict
            Dictionary containing raw or partially cleaned data fetched by the scrape_league_standings_data method.

        Returns
        -------
        dict
            League-Standings data dict with keys in order specified within function

        Notes
        -----
        This function is a specialization of the generic reorder_dict_keys method in the base class
        """
        new_key_order = [
            'rk', 'team_name', 'team_id', 'mp', 'w', 'd', 'l', 'gf', 'ga', 'gd', 'pts',
            'pts/mp', 'xg', 'xga', 'xgd', 'xgd/90', 'attendance', 'goalkeeper', 'top_team_scorer']
        league_standings_data_dict = self.reorder_dict_keys(league_standings_data_dict, new_key_order)
        return league_standings_data_dict
        
    def convert_standings_dict_dtypes(self, league_standings_data_dict):
        """
        Convert specific field's data types from str to either int or float

        Parameters
        ----------
        league_standings_data_dict : dict
            Dictionary containing raw or partially cleaned data fetched by the scrape_league_standings_data method

        Returns
        -------
        dict
            League-standings data dict with converted data types
            
        Notes
        -----
        This function is a specialization of the generic convert_list_from_str method in the base class
        """
        int_keys = ['rk', 'mp', 'w', 'd', 'l', 'gf', 'ga', 'pts']
        float_keys = ['pts/mp', 'xg', 'xga',]
        for k in league_standings_data_dict.keys():
            if k in int_keys:
                league_standings_data_dict[k] = self.convert_list_from_str(league_standings_data_dict[k])
            elif k in float_keys:
                league_standings_data_dict[k] = self.convert_list_from_str(league_standings_data_dict[k], convert_to='float')
        return league_standings_data_dict
    
    def get_standings_tables_from_caption(self, all_tables):
        """
        Given a list of BeautifulSoup tables, identify and return tables containing league-standings data.

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
        patterns = [
            r"Group\s.+", r"Regular\sseason", r"Matchup\s.+", r"Ranking\sof", r"Conference", r"Relegation",
            r"Championship\sround", r"play-offs", r"Championship\sgroup", r"Apertura\s"
            ]
        standings_tables = self.get_tables_from_caption(all_tables, patterns) # find standings tables
        return standings_tables
    