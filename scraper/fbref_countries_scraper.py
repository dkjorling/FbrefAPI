from scraper.fbref_scraper import FbrefScraper

class FbrefCountriesScraper(FbrefScraper):
    """
    FbrefCountriesScraper scrapes and cleans meta-data for all countries that have either domestic or international football teams that are tracked by football reference.

    Main Functionality Methods
    -------
    scrape_clean_data(self):
        Scrapes and cleans meta-data for all countries that have either domestic or international football teams that are tracked by football reference.

    clean_data(self, country_data_dict):
        Cleans raw country data scraped by the scrape_countries_data method.
    
    scrape_countries_data(self):
        Scrapes raw meta-data for all countries that have either domestic or international football teams that are tracked by football reference.
        Returns a dictionary containing the data.
    
    Notes
    -------
    Meta-data, when available, includes:

        1) country - str; name of country
        2) country_code - str; three-letter country abbreviation; used by FbrefLeaguesScraper to identify league information related to country
        3) governing_body - str; abbreviation of country's governing body that is typically based on geographical location
        4) #_clubs - int; Number of club teams in the country that are covered by football reference
        5) #_players - int; Number of players from country that are covered by football reference
        6) national_teams - list of str; national teams from country that are covered by football reference
    """
    # Initialization Methods
    def __init__(self):
        # Call parent class (FbrefEntity) initialization
        super().__init__()

    # Main Functionality Methods
    def scrape_clean_data(self):
        """
        Scrapes and cleans meta-data for all countries that have either domestic or international football teams tracked by football reference.

        Returns
        -------
        dict
            A dictionary containing the cleaned meta-data for all countries.
        """
        country_data_dict = self.scrape_countries_data()
        country_data_dict_clean = self.clean_data(country_data_dict)
        return country_data_dict_clean

    def clean_data(self, country_data_dict):
        """
        Cleans raw country data scraped by the scrape_countries_data method.

        Parameters
        ----------
        country_data_dict : dict
            Dictionary containing raw data fetched by the scrape_countries_data method.

        Returns
        -------
        dict
            A dictionary containing the cleaned meta-data for all countries.
        """
        country_data_dict_clean = self.clean_countries_data(country_data_dict)
        return country_data_dict_clean
    
    def scrape_countries_data(self):
        """
        Scrapes raw meta-data for all countries that have either domestic or international football teams that are tracked by football reference.

        Returns
        -------
        dict
            Dictionary containing raw data fetched by the scrape_countries_data method.
        """
        # Fetch and parse data
        url = "https://fbref.com/en/countries/"
        soup = self.scrape_data_requests(url)
        # Get BeautifulSoup object representing table of all countries 
        country_table = self.get_all_tables(soup)[0]
        country_data_dict = self.parse_table_data(country_table)
        # Add country codes from embedded links
        country_patterns = [r"country/([A-Z]{3})/"]
        country_data_dict['country_code'] = self.get_all_items_from_table_urls(country_table, country_patterns)
        return country_data_dict

    # Helper Methods
    def clean_countries_data(self, country_data_dict):
        """
        Cleans raw country data scraped by the scrape_countries_data method.

        Parameters
        ----------
        country_data_dict : dict
            Dictionary containing raw data fetched by the scrape_countries_data method.

        Returns
        -------
        dict
            A dictionary containing the cleaned meta-data for all countries.
        """
        # Delete flag key
        country_data_dict.pop('flag')
        # Convert datatypes
        country_data_dict = self.convert_countries_dict_dtypes(country_data_dict)
        # Clean national team and competitions fields
        country_data_dict['national_teams'] = [self.clean_national_teams(x) for x in country_data_dict['national_teams']]
        country_data_dict['competitions'] = [x.split(',') for x in country_data_dict['competitions']] 
        # Reorder keys
        country_data_dict = self.reorder_countries_dict_keys(country_data_dict)
        # Reorient dict
        country_data_dict_clean = self.change_dict_orientation(country_data_dict, id_key='country_code')
        return country_data_dict_clean

    def get_all_country_codes_from_table(self, country_table):
        """
        Given a BeautifulSoup object representing a country table, extract country codes from embedded links for each applicable row.

        Parameters
        ----------
        country_table : BeautifulSoup
            The BeautifulSoup object representing the table from which to extract country codes.

        Returns
        -------
        list of str
            A list of strings containing three-letter country abbreviations.
        """
        country_codes =  self.get_all_items_from_table_urls(country_table, self.parse_country_code_from_url)
        return country_codes
            
    def parse_country_code_from_url(self, country_url):
        """
        Given an embedded URL from the country table, extract the country code.

        Parameters
        ----------
        country_url : str
            The URL string from which to extract the country code.

        Returns
        -------
        str
            Three-letter country abbreviation.

        Notes
        -----
        This function is a specialization of the generic parse_pattern_from_url method in the base class
        """
        patterns = [r"country/([A-Z]{3})/"]
        return self.parse_pattern_from_url(patterns, country_url)

    def clean_national_teams(self, national_team_entry):
        """
        Clean the national team field to more abbreviated text and convert it to a list.

        Parameters
        ----------
        national_team_entry : str
            The raw entry indicating whether the country has men's, women's, or both national teams.

        Returns
        -------
        list of str or None
            A list providing information on whether the country has a men's team, women's team, both, or neither.
            - ['M'] for men's team
            - ['F'] for women's team
            - ['M', 'F'] for both
            - None for neither
        """
        if national_team_entry == 'Men/Women':
            return ['M', 'F']
        elif national_team_entry == 'Men':
            return ['M']
        elif national_team_entry == 'Women':
            return ['F']
        else:
            return None
    
    def convert_countries_dict_dtypes(self, country_data_dict):
        """
        Convert specific field's data types from str to either int or float

        Parameters
        ----------
        country_data_dict : dict
            Dictionary containing raw or partially cleaned data fetched by the scrape_countries_data method.

        Returns
        -------
        dict
            Country data dict with converted data types
            
        Notes
        -----
        This function is a specialization of the generic convert_list_from_str method in the base class
        """
        # Convert keys to int
        int_keys = ['#_clubs', '#_players']
        for k in country_data_dict.keys():
            if k in int_keys:
                country_data_dict[k] = self.convert_list_from_str(country_data_dict[k])
        return country_data_dict
    
    def reorder_countries_dict_keys(self, country_data_dict):
        """
        Re-order keys in raw country data dictionary

        Parameters
        ----------
        country_data_dict : dict
            Dictionary containing raw or partially cleaned data fetched by the scrape_countries_data method.

        Returns
        -------
        dict
            Country data dict with keys in order specified within function

        Notes
        -----
        This function is a specialization of the generic reorder_dict_keys method in the base class
        """
        # Define order and reorder
        new_key_order = [
            'country', 'country_code', 'governing_body', '#_clubs', '#_players', 'national_teams'
        ]
        country_data_dict = self.reorder_dict_keys(country_data_dict, new_key_order)
        return country_data_dict

