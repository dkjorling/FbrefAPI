from scraper.fbref_scraper import FbrefScraper

class FbrefLeagueSeasonDetailsScraper(FbrefScraper):
    """
    FbrefLeagueSeasonsScraper scrapes and cleans meta-data for a specific league id and season id

    This class provides different and potentially more useful data than the FbrefLeagueSeasonsScraper class

    Main Functionality Methods
    -------
    scrape_clean_data(self, lg_id, season_id=None):
        Scrapes and cleans meta data for a specific league id and season id

    clean_data(self, ls_details_data_dict, lg_id, season_id=None):
        Cleans raw league-seaons data scraped by the scrape_league_seasons method.

    scrape_league_season_details_data(self, lg_id, season_id=None):
        Scrapes meta data for a specific league id and season id

    Notes
    -------
    ** If season id is not provided, data is scraped for most recent season id for the specified league id **

    Meta-data, when available, includes:

    1) league_start - str; string date in '%Y-%m-%d' format representing first match date for given league-season
    2) league_start - str; string date in '%Y-%m-%d' format representing last match date for given league-season
        ** Note ** If season has round format and still in progress, the actual last match date may be inaccurate due to currently unknown final match date
    3) league_type - str; either 'cup' or 'league'
    4) has_adv_stats - str; either 'yes' or 'no'; identifies whether advanced stats are available for specific league-season
    5) rounds - list of str; list of names of rounds if a league has a multiple round format
    """
    # Initialization Methods
    def __init__(self):
        # Call parent class (FbrefScraper) initialization
        super().__init__()
    
    # Main Functionality Methods
    def scrape_clean_data(self, league_id, season_id=None):
        """
        Scrapes and cleans meta-data for a specific league id and season id.

        Parameters
        ----------
        league_id : int
            Football reference league id.
        season_id : str, optional
            Football reference season id. If not provided, defaults to None.

        Returns
        -------
        dict
            A dictionary containing the cleaned meta-data for a league-season for the specified league id and season id.
        """
        # Scrape raw league-season-details data
        ls_details_data_dict = self.scrape_league_season_details_data(league_id, season_id=season_id)
        # Clean league-season-details data
        ls_details_data_dict_clean = self.clean_data(ls_details_data_dict, league_id, season_id=season_id)
        return ls_details_data_dict_clean
    
    def clean_data(self, ls_details_data_dict, league_id, season_id=None):
        """
        Cleans raw league-season-details data scraped by the scrape_league_season_details_data method.

        Parameters
        ----------
        ls_details_data_dict : dict
            Dictionary containing raw data fetched by the scrape_league_season_details_data method.
        league_id : int
            Football reference league id.
        season_id : str, optional
            Football reference season id. If not provided, defaults to None.

        Returns
        -------
        dict
            A dictionary containing the cleaned meta-data for a league-season for the specified league id and season id.
        
        Notes
        -------
        This method calls sub-class specific cleaning method, clean_league_season_details
        """
        # Call class-specified cleaning method
        ls_details_data_dict_clean = self.clean_league_season_details(ls_details_data_dict, league_id, season_id)
        return ls_details_data_dict_clean

    def scrape_league_season_details_data(self, league_id, season_id=None):
        """
        Scrapes meta data for a specific league id and season id

        Parameters
        ----------
        lg_id : int
            Football reference league id.
        season_id : str, optional
            Football reference season id. If not provided, defaults to None.

        Returns
        -------
        dict
            A dictionary containing the raw meta-data for the league-seasons for the given league id and season id

        """
        # specify url based on parameters passed
        if season_id == None:
            url = f"https://fbref.com/en/comps/{str(league_id)}/schedule/"
        else:
            url = f"https://fbref.com/en/comps/{str(league_id)}/{season_id}/schedule/"
        # get data
        soup = self.scrape_data_requests(url)
        all_tables = self.get_all_tables(soup)
        ls_details_table = self.get_ls_details_tables_from_caption(all_tables)[0]
        ls_details_data_dict = self.parse_table_data(ls_details_table)
        return ls_details_data_dict
    
    # Helper Methods
    def clean_league_season_details(self, ls_details_data_dict, league_id, season_id=None):
        """
        Cleans raw league-season-details data scraped by the scrape_league_season_details_data method.

        Parameters
        ----------
        ls_details_data_dict : dict
            Dictionary containing raw data fetched by the scrape_league_season_details_data method.
        league_id : int
            Football reference league id.
        season_id : str, optional
            Football reference season id. If not provided, defaults to None.

        Returns
        -------
        dict
            A dictionary containing the cleaned meta-data for a league-season for the specified league id and season id.
        """
        # Create ls details data dict
        ls_details_data_dict_clean = {}
        ls_details_data_dict_clean['data'] = {}
        ls_details_data_dict_clean['data']['lg_id'] = int(league_id)
        if season_id == None:
            ls_details_data_dict_clean['data']['season_id'] = 'most_recent_season'
        else:
            ls_details_data_dict_clean['data']['season_id'] = season_id
        # League start and end:
        ls_details_data_dict_clean['data']['league_start'] = min(ls_details_data_dict['date'])
        ls_details_data_dict_clean['data']['league_end'] = max(ls_details_data_dict['date'])
        # League_type and adv stats
        has_adv_stats, league_type = self.get_league_type_adv(league_id)
        ls_details_data_dict_clean['data']['league_type'] = league_type
        # Adv stats
        ls_details_data_dict_clean['data']['has_adv_stats'] = has_adv_stats
        # Rounds
        ls_details_data_dict_clean['data']['rounds'] = self.check_rounds(ls_details_data_dict)
        if 'Round' in ls_details_data_dict_clean['data']['rounds']:
            ls_details_data_dict_clean['data']['rounds'].remove('Round')
        
        return ls_details_data_dict_clean

    def get_ls_details_tables_from_caption(self, all_tables):
        """
        Given a list of BeautifulSoup tables, identify and return tables containing league-season-details data.

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
        # Define regex patterns pertaining to league-season-details meta-data
        patterns = [r"^Scores\s"]
        # Find league-season-details tables
        ls_details_tables = self.get_tables_from_caption(all_tables, patterns) # find league seasons tables
        return ls_details_tables
    
    def check_rounds(self, ls_details_data_dict):
        """
        Get list of unique rounds for a league if the league has a rounds format
        
        Parameters
        ----------
        ls_details_data_dict : dict
            Dictionary containing raw or partially cleaned league-season-details data
        
        Returns
        -------
        list of str
            List of round names
        """
        # Check if league-season has rounds and fetch set of rounds if so
        if 'round' in ls_details_data_dict.keys():
            rounds = list(set(ls_details_data_dict['round']))
        else:
            rounds = None
        return rounds
