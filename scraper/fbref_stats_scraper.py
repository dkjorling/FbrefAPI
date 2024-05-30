import json
from scraper.fbref_scraper import FbrefScraper

class FbrefStatsScraper(FbrefScraper):
    """
    FbrefStatsScraper is the foundational class for scraping and cleaning statistical data from football reference. 
    
    This class provides basic functionalities to:
    - Fetch and parse football reference data related to match or season stats
    - Clean data and return as a dictionary object

    Subclasses should override the scrape_clean_stats and clean_stats methods.

    Attributes
    -------
    name:
        Determines class name which is used to reference the proper column mapping.

    column_map:
        This dictionary contains information to help clean stat data. 

    Main Functionality Methods
    -------
    scrape_clean_stats(self,*args, **kwargs):
        Performs common scraping and cleaning operations and delegates to subclass-specific scraping and cleaning methods.

    clean_stats(self, *args, **kwargs):
        Performs common cleaning operations and delegates to subclass-specific cleaning methods.

    parse_stat_table_rows(self, soup):
        Converts BeautifulSoup object representing a stat table into a dictionary with keys as column headers and lists of data as values

    Notes
    -------
    This class serves as the base for more specialized classes:

        FbrefTeamSeasonStatsScraper: Scrape team season stats for all teams for specified fbref league id and season id
        FbrefTeamMatchStatsScraper: Scrape team match stats for a specified fbref team id, league id and season id
        FbrefPlayerSeasonStatsScraper: Scrape all player season stats for a specified fbref team id, league id, and season id
        FbrefPlayerMatchStatsScraper: Scrape player match stats for a specified fbref player id, league id and season id
        FbrefAllPlayersMatchStatsScraper: Scrape all player stats for a specified fbref match id
    """
        
    # Initialization Methods
    def __init__(self, name=None):
        # Call parent class (FbrefScraper) initialization
        super().__init__()
        self.name = name # set name
        self.set_column_map()

    def set_column_map(self):
        """
        Set column_map attribute by loading json file
        """
        with open("data/column_map_final.json", "r") as f:
            column_map = json.load(f)
        if self.name:
            self.column_map = column_map[self.name]
        else:
            self.column_map = column_map
    
    # Main Functionality Methods
    def scrape_clean_stats(self,*args, **kwargs):
        """
        This method is a placeholder for scraping and cleaning football reference statistics.

        Subclasses must implement this method to provide specific functionality for scraping and cleaning stats data.
    
        Parameters
        ----------
        *args : tuple
            Variable-length positional arguments. These arguments can be used to pass any additional parameters as required by subclasses.

        **kwargs : dict
            Arbitrary keyword arguments. These arguments can be used to pass any additional keyword parameters as required by subclasses.

        Raises
        ------
        NotImplementedError
            This method is not implemented in the base class and must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement scrape_clean_stats")

    def clean_stats(self, *args, **kwargs):
        """
        This method is a placeholder for cleaning football reference statistics.

        Subclasses must implement this method to provide specific functionality for cleaning stats data.

        Parameters
        ----------
        *args : tuple
            Variable-length positional arguments. These arguments can be used to pass any additional parameters as required by subclasses.

        **kwargs : dict
            Arbitrary keyword arguments. These arguments can be used to pass any additional keyword parameters as required by subclasses.

        Raises
        ------
        NotImplementedError
            This method is not implemented in the base class and must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement clean_stats")
    
    def parse_stat_table_data(self, stat_table, skip_row=False, drop_rows=0, exclude_totals=False):
        """
        Given a BeautifulSoup stats table, parse data and return a dictionary with headers as keys and lists of values as data.

        This is a special form of parse_table_data that skips rows where a player did not participate

        Parameters
        ----------
        stat_table : BeautifulSoup
            The BeautifulSoup object representing the table containing statistics from which to parse the data.
        skip_row : bool, optional
            Whether to skip the first row of the table. Default is False.
        drop_rows : int, optional
            The number of rows to drop from the end of the table. Default is 0.
        exclude_totals : bool, optional
            Whether to exclude rows labeled as totals. If True, this overwrites the drop_rows parameter. Default is False.

        Returns
        -------
        dict
            A dictionary where each key represents a header and the corresponding value is a list of data extracted from rows.

        Notes
        -----
        This function first parses the table rows and then processes them to skip or drop rows as specified.
        It also provides an option to exclude rows labeled as totals.
        The parsed data is stored in a dictionary with headers as keys and lists of values as data.
        """
        cleaner_rows = self.parse_stat_table_rows(stat_table, skip_row=skip_row)
        all_row_data = self.parse_all_row_data(cleaner_rows)
        # exclude totals rows if True...this overwrites passed drop_rows
        if exclude_totals == True:
            totals_rows = self.detect_totals_rows(all_row_data)
            drop_rows = totals_rows
        # drop rows if > 0
        if drop_rows > 0:
            all_row_data = all_row_data[:(-drop_rows)]
        # check row length
        header_len = len(all_row_data[0])
        drop = []
        for i,row in enumerate(all_row_data):
            if len(row) != header_len:
                drop.append(i)
        all_row_data = [x for j, x in enumerate(all_row_data) if j not in drop]
        data_dict = self.convert_row_data_to_dict(all_row_data)
        return data_dict
    
    # Helper Methods
    def parse_stat_table_rows(self, stat_table, skip_row=False):
        """
        An extension of the parse_table_rows method which, given a BeautifulSoup table, parses data and returns a dictionary with
        headers as keys and lists of values as data.

        For some player stats, if a player did not enter a game or record any playing time, data fields will not exist for that player.
        This function ensures that these player rows are removed.

        Parameters
        ----------
        stat_table : BeautifulSoup
            BeautifulSoup object representing a table containing statistical data.
        skip_row : bool, optional
            Whether to skip the first row of the table. Default is False.

        Returns
        -------
        dict
            A dictionary with headers as keys and lists of values as data, excluding rows where players did not record any playing time.
        """
        clean_rows = self.parse_table_rows(stat_table)
        if skip_row == True:
            header_row = clean_rows[1]
            data_rows = clean_rows[2:]
        else:
            header_row = clean_rows[0]
            data_rows = clean_rows[1:]
        num_headers = len(header_row.find_all(['th', 'td']))
        cleaner_rows = []
        cleaner_rows.append(header_row)
        for row in data_rows:
            row_length = len(row.find_all(['th', 'td']))
            if row_length == num_headers:
                cleaner_rows.append(row)
        return cleaner_rows
    
    def get_all_items_from_stat_table_urls(self, stat_table, patterns, skip_row=False):
        """
        Extracts string items from URLs embedded in a football reference statistical table.

        Parameters
        ----------
        stat_table : BeautifulSoup
            The BeautifulSoup object representing the statistical table from which to extract items.
        patterns : list of str
            A list of regex patterns to match against the URLs.
        skip_row : bool, optional
            Whether to skip the first row of the table. Default is False.

        Returns
        -------
        list of str
            A list of string items extracted from the embedded URLs in the statistical table based on the provided regex patterns.

        """
        cleaner_rows = self.parse_stat_table_rows(stat_table, skip_row=skip_row)
        items = []
        for row in cleaner_rows:
            hrefs = [a.get('href') for a in row.find_all('a') if a.get('href')]
            for href in hrefs:
                item = self.parse_pattern_from_url(patterns, href)
                if item:
                    items.append(item)
                    break
        return items

    def change_stat_dict_orientation(self, *args, **kwargs):
        """
        This method is a placeholder for changing the orientation of stat dictionaries.
        
        Subclasses must implement this method to provide specific functionality for cleaning stats data.

        Parameters
        ----------
        *args : tuple
            Variable-length positional arguments. These arguments can be used to pass any additional parameters as required by subclasses.

        **kwargs : dict
            Arbitrary keyword arguments. These arguments can be used to pass any additional keyword parameters as required by subclasses.

        Raises
        ------
        NotImplementedError
            This method is not implemented in the base class and must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement change_stat_dict_orientation")

    def delete_rename_order_convert_sub_stat_dict(self, sub_stat_dict, stat_id_key, cmap):
        """
        Process a sub-stat dictionary by performing the following operations:

        1) Delete unwanted keys
        2) Rename keys
        3) Put keys in a specific order
        4) Convert key datatypes

        Parameters
        ----------
        sub_stat_dict : dict
            A sub-dictionary of the full stat dictionary where column headers are keys and lists of data are values.
        stat_id_key : str
            Stat id corresponding to the sub-dictionary.
        cmap : dict
            Column mapping dictionary attribute.

        Returns
        -------
        dict
            The processed sub-stat dictionary with unwanted keys deleted, keys renamed, keys reordered, and key datatypes converted.

        Notes
        -----
        This method uses the `cmap` dictionary to determine how to process the `sub_stat_dict`. It performs key deletion, renaming, reordering, and datatype conversion in sequence.
        """
        # Delete keys
        sub_stat_dict = self.delete_sub_stat_dict_keys(sub_stat_dict, stat_id_key, cmap)
        # Change key names
        sub_stat_dict = self.change_name_sub_stat_dict_keys(sub_stat_dict, stat_id_key, cmap)
        # Reorder keys
        sub_stat_dict = self.reorder_sub_stat_dict_keys(sub_stat_dict, stat_id_key, cmap)
        # Convert key datatypes
        sub_stat_dict = self.convert_sub_stat_dict_keys_dtypes(sub_stat_dict, stat_id_key, cmap)
        return sub_stat_dict

    def delete_sub_stat_dict_keys(self, sub_stat_dict, stat_id_key, cmap):
        """
        Delete keys from specific sub-stat dictionary and return sub-stat dictionary without the deleted keys.
            
        Parameters
        ----------
        sub_stat_dict : dict
            A sub-dictionary of the full stat dictionary where column headers are keys and lists of data are values.
        stat_id_key : str 
            Stat id corresponding to the sub-dictionary.
        cmap : dict
            Column mapping dictionary attribute.

        Returns
        -------
        dict
            The sub-stat dictionary with the specified keys removed.

        Notes
        -----
        This method uses the `cmap` dictionary to determine which keys should be deleted from the `sub_stat_dict`. It then applies these deletions using the `delete_dict_keys` method.
        """
        # delete unwanted keys
        keys_to_delete = cmap[stat_id_key]['drop_columns']
        sub_stat_dict = self.delete_dict_keys(sub_stat_dict, keys_to_delete)
        return sub_stat_dict
    
    def change_name_sub_stat_dict_keys(self, sub_stat_dict, stat_id_key, cmap):
        """
        Change names of specific sub-stat dictionary keys using a column mapping dictionary.

        Parameters
        ----------
        sub_stat_dict : dict
            A sub-dictionary of the full stat dictionary where column headers are keys and lists of data are values.
        stat_id_key : str 
            Stat id corresponding to the sub-dictionary.
        cmap : dict
            Column mapping dictionary attribute.

        Returns
        -------
        dict
            The sub-stat dictionary with keys renamed according to the specified mapping in the column mapping dictionary.

        Notes
        -----
        This method uses the `cmap` dictionary to determine the new names for keys in the `sub_stat_dict`.
        It then applies these changes using the `rename_dict_key` method.
        """
        # Convert key names in sub stat dict
        convert_dict = cmap[stat_id_key]['name_mapping']
        original_keys = list(sub_stat_dict.keys())
        for key2 in original_keys:
            if key2 in convert_dict.keys():
                new_key = convert_dict[key2]
                sub_stat_dict = self.rename_dict_key(sub_stat_dict, key2, new_key)
        return sub_stat_dict
    
    def reorder_sub_stat_dict_keys(self, sub_stat_dict, stat_id_key, cmap):
        """
        Reorder specific sub-stat dictionary keys using a column mapping dictionary.

        Parameters
        ----------
        sub_stat_dict : dict
            A sub-dictionary of the full stat dictionary where column headers are keys and lists of data are values.
        stat_id_key : str 
            Stat id corresponding to the sub-dictionary.
        cmap : dict
            Column mapping dictionary attribute.

        Returns
        -------
        dict
            The sub-stat dictionary with keys reordered according to the specified order in the column mapping dictionary.

        Notes
        -----
        This method uses the `cmap` dictionary to determine the final order of keys in the `sub_stat_dict`.
        It then applies this order using the `reorder_dict_keys` method.
        """
        # Order sub dictionary
        subdict_order = cmap[stat_id_key]['final_order']
        sub_stat_dict = self.reorder_dict_keys(sub_stat_dict, subdict_order)
        return sub_stat_dict
    
    def convert_sub_stat_dict_keys_dtypes(self, sub_stat_dict, stat_id_key, cmap):
        """
        Convert specific sub-stat dictionary keys from string to either integers or floats.

        Parameters
        ----------
        sub_stat_dict : dict
            A sub-dictionary of the full stat dictionary where column headers are keys and lists of data are values.
        stat_id_key : str 
            Stat id corresponding to the sub-dictionary.
        cmap : dict
            Column mapping dictionary attribute.

        Returns
        -------
        dict
            The sub-stat dictionary with keys converted to their appropriate data types.

        Notes
        -----
        This method uses the `cmap` dictionary to determine which keys in the `sub_stat_dict` should be converted to integers or floats.
        It then applies these conversions using the `convert_dict_dtypes` method.
        """
        # Retrieve integer keys and float keys from mapping
        int_keys = cmap[stat_id_key]['int_columns']
        float_keys = cmap[stat_id_key]['float_columns']
        # Apply datatype conversion
        sub_stat_dict = self.convert_dict_dtypes(
            sub_stat_dict,
            int_keys,
            float_keys
        )
        return sub_stat_dict

    def clean_stat_dict_columns(self, sub_stat_dict):
        """
        Clean stat columns using appropriate method if exist in stat_dict keys.

        Parameters
        ----------
        sub_stat_dict : dict
            A sub-dictionary of full stat dictionary where column headers are keys and lists of data are values

        Returns
        -------
        dict
            The cleaned stat dictionary with columns appropriately cleaned.

        """
        cleaning_map = {
            'positions': self.clean_player_position,
            'age': self.clean_player_age,
            'min': self.clean_player_min,
            'opponent': self.clean_team_name,
            'squad': self.clean_team_name,
            'gf': self.clean_gf_ga,
            'ga': self.clean_gf_ga,
            'team_name': self.clean_team_name
        }

        # Iterate over the keys in the cleaning map and apply the corresponding cleaning method
        for column, method in cleaning_map.items():
            if column in sub_stat_dict:
                sub_stat_dict[column] = [method(x) for x in sub_stat_dict[column]]

        return sub_stat_dict
    
    def clean_player_position(self, position):
        """
        Clean player position data.

        Parameters
        ----------
        position : str
            The player's position data to be cleaned.

        Returns
        -------
        str or list of str
            The cleaned player position data. If multiple positions are given, returns a list of positions; otherwise, returns a single position as a string.

        """
        if len(position.split(',')) > 1:
            return position.split(',')
        else:
            return position
    
    def clean_player_age(self, age):
        """
        Clean player age data.

        Parameters
        ----------
        age : str
            The player's age data to be cleaned.

        Returns
        -------
        str
            The cleaned player age data.

        Notes
        -----
        Sometimes football reference age data is given in yy-ddd format. This function extracts only the year in this case.

        """
        if len(age.split('-')) > 1:
            return age.split('-')[0]
        else:
            return age
    
    def clean_player_min(self, min):
        """
        Clean player minutes data.

        Parameters
        ----------
        min : str
            The player's minutes data to be cleaned.

        Returns
        -------
        str
            The cleaned player minutes data.

        """
        clean_min = min.replace(',','')
        return clean_min
    
    def get_adv_or_nadv_cmap(self, stat_dict, threshold=1):
        """
        Determine whether the given statistics are advanced or non-advanced and return the corresponding column mapping.

        Parameters
        ----------
        stat_dict : dict
            A dictionary containing stat IDs as keys and statistical data as values.

        threshold : int, optional
            The threshold above which the dictionary is considered to contain advanced statistics. 
            Default is 1.

        Returns
        -------
        dict
            A dictionary containing the mapping to clean specific stat tables.

        """
        if len(stat_dict.keys()) > threshold:
            cmap = self.column_map['advanced']
        else:
            cmap = self.column_map['non_advanced']
        return cmap
