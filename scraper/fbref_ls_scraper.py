from scraper.fbref_scraper import FbrefScraper

class FbrefLeagueSeasonsScraper(FbrefScraper):
    """
    FbrefLeagueSeasonsScraper scrapes and cleans meta data for all season ids tracked by football reference, given a football reference league id.

    Main Functionality Methods
    -------
    scrape_clean_data(self, lg_id):
        Scrapes and cleans meta data for all season ids tracked by football reference, given a football reference league id

    clean_data(self, ls_data_dict):
        Cleans raw league-seaons data scraped by the scrape_league_seasons method.

    scrape_league_seasons_data(self, lg_id):
        Scrapes meta data for all season ids tracked by football reference, given a football reference league id

    Notes
    -------
    Meta-data, when available, includes:

    1) season_id - str; football reference season that is either in "%Y"  or "%Y-%Y" format, depending on the league
    2) competition_name - str; name of league; typically consistent across seasons although it does change on rare occassion
    3) #_squads - int; number of teams that competed in the league-season
    4) champion - str; name of team that won the competition for specified league-season
    5) top_scorer - dict; dictionary containing player(s) name (str) and number of goals scored (int) by top scorer for specified league-season
    """
    # Initialization Methods
    def __init__(self):
        # Call parent class (FbrefScraper) initialization
        super().__init__()
    
    # Main Functionality Methods
    def scrape_clean_data(self, league_id):
        """
        Scrapes and cleans meta data for all season ids tracked by football reference, given a football reference league id

        Parameters
        ----------
        league_id : int
            Integer representing a league's football reference id
        
        Returns
        -------
        dict
            A dictionary containing the cleaned meta-data for all league-seasons for the given league id
        """
        # Scrape data
        ls_data_dict = self.scrape_league_seasons_data(league_id)
        # Clean data
        ls_data_dict_clean = self.clean_data(ls_data_dict)
        return ls_data_dict_clean
    
    def clean_data(self, ls_data_dict):
        """
        Cleans raw league-seasons data scraped by the scrape_league_seasons_data method.

        Parameters
        ----------
        ls_data_dict : dict
            Dictionary containing raw data fetched by the scrape_league_seasons_data method.

        Returns
        -------
        dict
            A dictionary containing the cleaned meta-data for all league-seasons.
        
        Notes
        -------
        This method calls sub-class specific cleaning method, clean_league_seasons
        """
        # Clean raw data dict
        ls_data_dict_clean = self.clean_league_seasons(ls_data_dict)
        return ls_data_dict_clean

    def scrape_league_seasons_data(self, league_id):
        """
        Scrapes and meta data for all season ids tracked by football reference, given a football reference league id

        Parameters
        ----------
        lg_id : int
            Integer representing a league's football reference id
        
        Returns
        -------
        dict
            A dictionary containing the raw meta-data for all league-seasons for the given league id
        """
        # Get html content
        url = f"https://fbref.com/en/comps/{str(league_id)}/history/"
        soup = self.scrape_data_requests(url)
        all_tables = self.get_all_tables(soup)
        # Identify league seasons table and return as dictionary
        league_seasons_tables = self.get_ls_tables_from_caption(all_tables)
        ls_data_dict = self.parse_table_data(league_seasons_tables[0])
        return ls_data_dict
    
    # Helper Methods
    def clean_league_seasons(self, ls_data_dict):
        """
        Cleans raw league-seasons data scraped by the scrape_league_seasons_data method.

        Parameters
        ----------
        ls_data_dict : dict
            Dictionary containing raw data fetched by the scrape_league_seasons_data method.

        Returns
        -------
        dict
            A dictionary containing the cleaned meta-data for all league-seasons.
        """
        if 'top_scorer' in ls_data_dict.keys():
            ls_data_dict = self.clean_top_overall_scorer(ls_data_dict)
        if 'final' in ls_data_dict.keys():
            ls_data_dict.pop('final')
        for key in ['champion', 'runner-up']:
            if key in ls_data_dict.keys():
                ls_data_dict[key] = [self.clean_team_name(x) for x in ls_data_dict[key]]
        for key in ['season', 'year']:
            if key in ls_data_dict.keys():
                ls_data_dict = self.rename_dict_key(ls_data_dict, key, 'season_id')
        ls_data_dict = self.convert_ls_dict_dtypes(ls_data_dict)
        ls_data_dict = self.reorder_ls_dict_keys(ls_data_dict)
        ls_data_dict_clean = self.change_dict_orientation(ls_data_dict, id_key='season_id')
        return ls_data_dict_clean
    
    def convert_ls_dict_dtypes(self, ls_data_dict):
        """
        Convert specific field's data types from str to either int or float

        Parameters
        ----------
        leagues_data_dict : dict
            Dictionary containing raw or partially cleaned data fetched by the scrape_league_seasons_data method.

        Returns
        -------
        dict
            Leagues data dict with converted data types
            
        Notes
        -----
        This function is a specialization of the generic convert_list_from_str method in the base class
        """
        # Define int and float keys and convert data
        int_keys = ['#_squads']
        float_keys = []
        for k in ls_data_dict.keys():
            if k in int_keys:
                ls_data_dict[k] = self.convert_list_from_str(ls_data_dict[k])
            elif k in float_keys:
                ls_data_dict[k] = self.convert_list_from_str(ls_data_dict[k], convert_to='float')
        return ls_data_dict
    
    def reorder_ls_dict_keys(self, ls_data_dict):
        """
        Re-order keys in league-seasons data dictionary

        Parameters
        ----------
        ls_data_dict : dict
            Dictionary containing raw or partially cleaned data fetched by the scrape_league_seasons_data method.

        Returns
        -------
        dict
            League-Seasons data dict with keys in order specified within function

        Notes
        -----
        This function is a specialization of the generic reorder_dict_keys method in the base class
        """
        new_key_order = [
            'season_id', 'competition_name', 'host_country', '#_squads', 'champion', 'runner-up', 'top_scorer'
            ]
        ls_data_dict = self.reorder_dict_keys(ls_data_dict, new_key_order)
        return ls_data_dict
    
    def get_ls_tables_from_caption(self, all_tables):
        """
        Identify 

        Parameters
        ----------
        all_tables : list of BeautifulSoup
            List of BeautifulSoup objects representing tables that were scraped from league URL html content
        
        Returns
        -------
        list of BeautifulSoup
            List of BeautifulSoup objects representing tables that contain league-season meta-data
            
        Notes
        -----
        This function is a specialization of the generic get_tables_from_caption method in the base class
        """
        # Define regex patterns pertaining to league-seasons meta-data
        patterns = [r"Seasons", r"Tournaments"]
        # Find league-seasons tables
        league_seasons_tables = self.get_tables_from_caption(all_tables, patterns) 
        return league_seasons_tables
    
    def clean_top_overall_scorer(self, ls_data_dict):
        """
        Takes data dict containing top_scorer data in the form of a list, and converts it to a dictionary with two keys:
            player : list of str; of player(s) who scored the most goals in a given league-season
            goals_scored : int; number goals scored by highest scrorer(s)

        Parameters
        ----------
        ls_data_dict : dict
            Dictionary containing raw or partially cleaned data fetched by the scrape_league_seasons_data method.
        
        Returns
        -------
        dict
            League-Seasons data dict with clean top scorers dict in place of raw top scorers list
        """
        ls_data_dict['raw_top_scorer'] = ls_data_dict.pop('top_scorer')
        ls_data_dict['top_scorer'] = {}
        ls_data_dict['top_scorer']['player'] = []
        ls_data_dict['top_scorer']['goals_scored'] = []
        for scorer in ls_data_dict['raw_top_scorer']:
            if scorer == '':
                ls_data_dict['top_scorer']['player'].append('')
                ls_data_dict['top_scorer']['goals_scored'].append(None)
            else:
                p_n = scorer.split('-')
                if len(' '.join(p_n[:-1]).split(',')) > 1:
                    ls_data_dict['top_scorer']['player'].append(' '.join(p_n[:-1]).split(','))
                else:
                    ls_data_dict['top_scorer']['player'].append(' '.join(p_n[:-1]))
                ls_data_dict['top_scorer']['goals_scored'].append(int(p_n[-1]))
        ls_data_dict.pop('raw_top_scorer')
        return ls_data_dict
    
        
    
        
            
            
            
        
        

    
