import re
from scraper.fbref_scraper import FbrefScraper

class FbrefLeaguesScraper(FbrefScraper):
    """
    FbrefLeaguesScraper scrapes and cleans meta-data for all unique leagues associated with a specified country.

    Data is retrieved based on a country's three-letter country code used as identification within football reference. 

    Leagues are classified as one of the following:

    1) domestic_leagues - club-level league competitions occurring only within the specified country
    2) domestic_cups - club-level cup competitions occuring only within the specified country
    3) international_competitions - club-level competitions occuring between teams in specified coutnry and teams from other countries
    4) national_team_competitions - national team-level competitions where specified country's national team participated in

    Main Functionality Methods
    -------
    scrape_clean_data(self, country_code):
        Scrapes and cleans meta-data for all leagues associated with a specified country
        Country is specified by the country's three-letter football reference country code.
    
    clean_data(self, leagues_data_dict):
        Cleans raw leagues data scraped by the scrape_leagues_data method.

    scrape_leagues_data(self, country_code):
        Scrapes raw meta-data for all leagues associated with a specified country and returns as a dictionary.

    Notes
    -------
    Meta-data, when available, includes:

    1) league_id - int; fotball reference league id number
    2) competition_name - str; name of league
    3) gender - str; 'M' if male or 'F' if female
    4) first_season - str; season id for earliest season that league is tracked in football reference
    5) last_season - str; season id for latest season that league is tracked in football reference
    6) tier - str; determines level on country's football pyramid in which competition belongs
    """
    # Initialization Methods
    def __init__(self):
        # Call parent class (FbrefScraper) initialization
        super().__init__()
    
    # Main Functionality Methods
    def scrape_clean_data(self, country_code):
        """
        Scrapes and cleans meta-data for all unique leagues associated with a specified country
        Country is specified by the country's three-letter football reference country code.

        Parameters
        ----------
        country_code : str
            Three-letter code used by football reference to identify specific country

        Returns
        -------
        dict
            A dictionary containing the cleaned meta-data for all leagues from the given country.
        """
        # Scrape data
        leagues_data_dict = self.scrape_leagues_data(country_code)
        # Clean data
        leagues_data_dict_clean = self.clean_data(leagues_data_dict)
        # Check for all nulls
        all_null_values = all(value is None for value in leagues_data_dict_clean.values())
        if all_null_values:
            raise ValueError("Country code is either invalid or has no leagues or competitions being tracked by football reference.") 
        else:
            return leagues_data_dict_clean
    
    def clean_data(self, leagues_data_dict):
        """
        Cleans raw leagues data scraped by the scrape_leagues_data method.

        Parameters
        ----------
        leagues_data_dict : dict
            Dictionary containing raw data fetched by the scrape_leagues_data method.

        Returns
        -------
        dict
            A dictionary containing the cleaned meta-data for all leagues.
        
        Notes
        -------
        This method calls sub-class specific cleaning method, clean_leagues_data
        """
        leagues_data_dict_clean = self.clean_leagues_data(leagues_data_dict)
        return leagues_data_dict_clean


    def scrape_leagues_data(self, country_code):
        """
        Scrapes raw meta-data for all leagues associated with a specified country and returns as a dictionary.

        Parameters
        ----------
        country_code : str
            Three-letter code used by football reference to identify specific country
        
        Returns
        -------
        dict
            A dictionary containing the raw meta-data for all leagues.

        """
        # Fetch and parse html content
        url = f"https://fbref.com/en/country/{country_code}/"
        soup = self.scrape_data_requests(url)
        # Get all tables from soup object
        all_tables = self.get_all_tables(soup)
        # Scrape data and store in larger data dictionary
        leagues_data_dict = {}
        leagues_data_dict['domestic_leagues'] = self.scrape_domestic_leagues_table(all_tables)
        leagues_data_dict['domestic_cups'] = self.scrape_domestic_cups_table(all_tables)
        leagues_data_dict['international_competitions'] = self.scrape_international_cups_table(all_tables)
        leagues_data_dict['national_team_competitions'] = self.scrape_national_team_competitions(all_tables)
        return leagues_data_dict
    
    # Helper Methods
    def clean_leagues_data(self, leagues_data_dict):
        """
        Cleans raw leagues data scraped by the scrape_leagues_data method.

        Parameters
        ----------
        leagues_data_dict : dict
            Dictionary containing raw data fetched by the scrape_leagues_data method.

        Returns
        -------
        dict
            A dictionary containing the cleaned meta-data for all leagues.
        """
        leagues_data_dict_clean = {}
        for key in leagues_data_dict:
            if leagues_data_dict[key] is not None:
                # Create sub dict for readability
                leagues_sub_dict = leagues_data_dict[key]
                # Convert datatypes
                leagues_sub_dict = self.convert_leagues_dict_dtypes(leagues_sub_dict)
                # Reorder keys
                leagues_sub_dict = self.reorder_leagues_dict_keys(leagues_sub_dict)
                leagues_data_dict_clean[key] = leagues_sub_dict
        # Reorient entire dictionary
        leagues_data_dict_clean = self.change_league_dict_orientation(leagues_data_dict_clean)
        return leagues_data_dict_clean

    def scrape_domestic_leagues_table(self, all_tables):
        """
        Identify and parse data related to domestic leagues given a list of tables scraped from a country code URL.

        Parameters
        ----------
        all_tables : list of BeautifulSoup
            List of BeautifulSoup objects representing tables that were scraped from a country code URL html content

        Returns
        -------
        dict
            A dictionary representing table columns for domestic league meta-data.
        """
        # Identify tables containing data pertaining to domestic leagues
        domestic_leagues_tables = self.get_tables_from_caption(all_tables, [r"Domestic\sLeagues"])
        # Format data into dictionary
        if domestic_leagues_tables:
            domestic_leagues_table = domestic_leagues_tables[0]
            dl_data_dict = self.format_league_tables(domestic_leagues_table)
            return dl_data_dict
        else:
            return None

    def scrape_domestic_cups_table(self, all_tables):
        """
        Identify and parse data related to domestic cups given a list of tables scraped from a country code URL.

        Parameters
        ----------
        all_tables : list of BeautifulSoup
            List of BeautifulSoup objects representing tables that were scraped from a country code URL html content

        Returns
        -------
        dict
            A dictionary representing table columns for domestic cups meta-data.
        """
        # Identify tables containing data pertaining to domestic cups
        domestic_cups_tables = self.get_tables_from_caption(all_tables, [r"Domestic\sCups"])
        # Format data into dictionary
        if domestic_cups_tables:
            domestic_cups_table = domestic_cups_tables[0]
            dc_data_dict = self.format_league_tables(domestic_cups_table)
            return dc_data_dict
        else:
            return None

    def scrape_international_cups_table(self, all_tables):
        """
        Identify and parse data related to international cups given a list of tables scraped from a country code URL.

        Parameters
        ----------
        all_tables : list of BeautifulSoup
            List of BeautifulSoup objects representing tables that were scraped from a country code URL html content

        Returns
        -------
        dict
            A dictionary representing table columns for international cups meta-data.
        """
        # Identify tables containing data pertaining to international cups
        international_cups_tables = []
        for table in all_tables:
            if 'Qualifiers' in self.get_table_name(table):
                ic_data_dict = self.format_league_tables(table, get_names=True)
                international_cups_tables.append(ic_data_dict)
        if international_cups_tables:
            # Format data into dictionary
            league_names = []
            league_ids = []
            gender = []
            for data_dict in international_cups_tables:
                for i, league_name in enumerate(data_dict['competition_name']):
                    if league_name not in league_names:
                        league_names.append(league_name)
                        league_ids.append(data_dict['league_id'][i])
                        gender.append(data_dict['gender'][i])
            international_cups_dict = {}
            international_cups_dict['competition_name'] = league_names
            international_cups_dict['league_id'] = league_ids
            international_cups_dict['gender'] = gender
            return international_cups_dict
        else:
            return None
    
    def scrape_national_team_competitions(self, all_tables):
        """
        Identify and parse data related to national team competitions given a list of tables scraped from a country code URL.

        Parameters
        ----------
        all_tables : list of BeautifulSoup
            List of BeautifulSoup objects representing tables that were scraped from a country code URL html content

        Returns
        -------
        dict
            A dictionary representing table columns for national team competitions meta-data.
        
        Notes
        -------
        This function grabs data from multiple tables representing men's and women's national team competition meta-data and concatenates intoa  single dict.
        """
        # Get mens team tables
        mens_national_tables = self.get_tables_from_caption(all_tables, [r"\smen's\snational\steam"])
        if mens_national_tables:
            mens_national_table = mens_national_tables[0]
            mn_data_dict = self.format_league_tables(mens_national_table, get_names=True)
        else:
            mn_data_dict = None
        # Get womens team tables
        womens_national_tables = self.get_tables_from_caption(all_tables, [r"\swomen's\snational\steam"])
        if womens_national_tables:
            womens_national_table = womens_national_tables[0]
            wmn_data_dict = self.format_league_tables(womens_national_table, get_names=True)
        else:
            wmn_data_dict = None
        # Concatenate data and format as dict 
        league_names = []
        league_ids = []
        gender = []
        for i, data_dict in enumerate([mn_data_dict, wmn_data_dict]):
            if data_dict:
                for j, league_name in enumerate(data_dict['competition_name']):
                    if league_name not in league_names:
                        league_names.append(league_name)
                        league_ids.append(data_dict['league_id'][j])
                        if i == 0:
                            gender.append('M')
                        else:
                            gender.append('F')
        if len(league_names) == 0:
            return None
        else:
            national_comps_dict = {}
            national_comps_dict['competition_name'] = league_names
            national_comps_dict['league_id'] = league_ids
            national_comps_dict['gender'] = gender
            return national_comps_dict
    
    def change_league_dict_orientation(self, league_dict):
        """
        This function converts the league data dict from column format to row format, with league id used as unique row identifier.

        Parameters
        ----------
        league_dict : dict
            Partially cleaned league data dict with keys representing league types

        Returns
        -------
        dict
            Dict with new orientation
        """
        output_dict = {}
        output_dict['data'] = []
        for key in league_dict.keys():
            if league_dict[key] is not None:
                league_sub_dict = {}
                league_sub_dict['league_type'] = key
                league_sub_dict['leagues'] = []
                num_leagues = len(league_dict[key]['league_id'])
                for i in range(num_leagues):
                    league_sub_sub_dict = {}
                    for key2 in league_dict[key].keys():
                        league_sub_sub_dict[key2] = league_dict[key][key2][i]
                    league_sub_dict['leagues'].append(league_sub_sub_dict)
                output_dict['data'].append(league_sub_dict)
        return output_dict
                
    def format_league_tables(self, league_table, get_names=False):
        """
        Given a BeautifulSoup object representing a table with , parse table data and return data dictionary.

        This function also adds football reference league id data and competition name where aplicable

        Parameters
        ----------
            league_table : BeautifulSoup
                Beautiful Soup object representing a table containing league data
            get_names : bool
                Determines whether or not to scrape competition name from embedded url.
                This is a necessary paramater because the method to retrieve competition name varies based on league_type
        Returns
        -------
        dict
            Dictionary formatted with league id field and cleaned competition name if needed
        """
        league_data_dict = self.parse_table_data(league_table)
        league_id_patterns = [r"comps/(\d+)/"]
        league_data_dict['league_id'] = self.get_all_items_from_table_urls(league_table, league_id_patterns)
        if get_names == True:
            league_patterns = [r"\d{4}-([a-zA-Z-]+)-Stats", r"comps/\d{1,3}/([a-zA-Z-]+)-Stats"]
            league_data_dict['competition_name'] = self.get_all_items_from_table_urls(league_table, league_patterns)
            # Clean competition name
            league_data_dict['competition_name'] = [x.replace('-',' ') for x in league_data_dict['competition_name']]
            league_data_dict['competition_name'] = [re.sub(r'\s+', ' ', x) for x in league_data_dict['competition_name']]
        return league_data_dict
    
    def convert_leagues_dict_dtypes(self, leagues_data_dict):
        """
        Convert specific field's data types from str to either int or float

        Parameters
        ----------
        leagues_data_dict : dict
            Dictionary containing raw or partially cleaned data fetched by the scrape_countries_data method.

        Returns
        -------
        dict
            Leagues data dict with converted data types
            
        Notes
        -----
        This function is a specialization of the generic convert_list_from_str method in the base class
        """
        # Define int and float keys and convert data
        int_keys = ['league_id']
        float_keys = []
        for k in leagues_data_dict.keys():
            if k in int_keys:
                leagues_data_dict[k] = self.convert_list_from_str(leagues_data_dict[k])
            elif k in float_keys:
                leagues_data_dict[k] = self.convert_list_from_str(leagues_data_dict[k], convert_to='float')
        return leagues_data_dict
    
    def reorder_leagues_dict_keys(self, leagues_data_dict):
        """
        Re-order keys in leagues data dictionary

        Parameters
        ----------
        leagues_data_dict : dict
            Dictionary containing raw or partially cleaned data fetched by the scrape_leagues_data method.

        Returns
        -------
        dict
            Leagues data dict with keys in order specified within function

        Notes
        -----
        This function is a specialization of the generic reorder_dict_keys method in the base class
        """
        # Define order and reorder
        new_key_order = [
            'league_id', 'competition_name', 'gender', 'first_season', 'last_season', 'tier'
        ]
        leagues_data_dict = self.reorder_dict_keys(leagues_data_dict, new_key_order)
        return leagues_data_dict




    

                

        