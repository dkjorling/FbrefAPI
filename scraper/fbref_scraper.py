import requests
import warnings
from bs4 import BeautifulSoup, Comment, MarkupResemblesLocatorWarning
import re
import logging
import json
# Configure logging
logging.basicConfig(level=logging.INFO)
# Suppress the MarkupResemblesLocatorWarning
warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)

class FbrefScraper():
    """
    FbrefScraper is the foundational class for scraping and cleaning data from football reference.
    
    This class provides basic functionalities to:
    - Fetch HTML content from a given URL
    - Parse HTML content using BeautifulSoup
    - Define a structure for cleaning scraped data

    Attributes
    -------
    adv_cup_dict:
        This dictionary contains competition type and advance stats availability for all league ids tracked by football reference.

    Main Functionality Methods
    -------
    scrape_clean_data(self,*args, **kwargs):
        Performs common scraping and cleaning operations and delegates to subclass-specific scraping and cleaning methods.

    clean_data(self, *args, **kwargs):
        Performs common cleaning operations and delegates to subclass-specific cleaning methods.

    scrape_data_requests(url):
        Fetches and parses HTML content from the specified URL.

    get_and_parse_all_table_data(self, soup):
        Finds all tables in BeautifulSoup object and returns a list of dictionaries, each with table headers as keys and data as values.

    Notes
    -------
    This class serves as the base for more specialized classes:

        FbrefCountriesScraper: Scrape basic information about all football reference countries
        FbrefLeaguesScraper: Scrape league information a given football reference country
        FbrefLeagueSeasonsScraper: Scrape all season ids and basic information for each league-season, given a football reference league id
        FbrefLeagueSeasonDetailsScraper: Scrape meta-data for a given football reference league id and season id
        FbrefLeagueStandingsScraper: Scrape league standings for a given fbref league id and season id
        FbrefTeamsScraper: Scrape team meta-data for a given fbref team id
        FbrefPlayersScraper: Scrape player meta-data for a given fbref player id
        FbrefMatchesScraper: Scrape match meta-data for a given fbref match id
        FbrefStatsScraper: Scrape football reference match or season stats for teams and players
    """
    # Initializaiton Methods
    def __init__(self):
        self.set_league_adv_type()
     
    def set_league_adv_type(self):
        """
        Set league_adv_type attribute by loading json file
        """
        with open("data/sorted_adv_cup_dict.json", "r") as f:
            self.adv_cup_dict = json.load(f)
    
    # Main Functionality Methods
    def scrape_clean_data(self,*args, **kwargs):
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
        raise NotImplementedError("Subclasses must implement scrape_clean_data")
    
    def clean_data(self, *args, **kwargs):
        """
        This method is a placeholder for cleaning football reference data.

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
        raise NotImplementedError("Subclasses must implement clean_data")

    def scrape_data_requests(self, url):
        """
        Scrape data using requests and BeautifulSoup libraries.

        Parameters
        ----------
        url : str
            The URL to fetch data from.

        Returns
        -------
        BeautifulSoup or None
            A BeautifulSoup object containing the parsed HTML content if the request is successful.
            Returns None if the request fails.

        Raises
        ------
        requests.exceptions.HTTPError
            If the HTTP request returns a status code other than 200.
        requests.exceptions.RequestException
            If there is an issue with the HTTP request.

        Notes
        -----
        This function attempts to fetch the HTML content from the specified URL using the `requests` library.
        It parses the HTML content using BeautifulSoup and returns the BeautifulSoup object.
        If the request fails for any reason (e.g., network issues, invalid URL, etc.), the function prints an error message
        and returns None.
        """
        try:
            # Get content from url
            response = requests.get(url)
            # If request succeeds, return BeautifulSoup object
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")
                #print(f"Successfully scraped html content from {url}")
                return soup
            else:
                response.raise_for_status()
        except Exception as e:
            print(f"Unsuccessfully scraped html content from {url} due to error: {e}")
            return None
    
    def get_and_parse_all_table_data(self, soup):
        """
        Given a BeautifulSoup object, get all tables, parse column names and data, and return as a dictionary.

        Parameters
        ----------
        soup : BeautifulSoup
            The BeautifulSoup object containing the HTML content to be parsed.

        Returns
        -------
        dict
            A dictionary where keys are table names and values are the parsed table data.

        Notes
        -----
        This function extracts all tables from the given BeautifulSoup object, parses their column names and data,
        and returns the results as a dictionary. The keys in the dictionary are the table names, and the values are
        the parsed data from the tables.

        The function relies on the `get_all_tables`, `get_table_name`, and `parse_table_data` methods, which should be
        defined in the class.
        """

        tables = self.get_all_tables(soup)
        table_names = [self.get_table_name(x) for x in tables]
        all_tables_data = {}
        for i, table in enumerate(tables):
            all_tables_data[table_names[i]] = self.parse_table_data(table)
        return all_tables_data
    
    # Helper Methods
    def parse_table_data(self, table, skip_row=False, drop_rows=0, exclude_totals=False):
        """
        Given a BeautifulSoup table, parse data and return a dictionary with headers as keys and lists of values as data.

        Parameters
        ----------
        table : BeautifulSoup
            The BeautifulSoup object representing the table from which to parse the data.
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
        # Get list of BeautifulSoup objects representing table rows
        clean_rows = self.parse_table_rows(table)
        all_row_data = self.parse_all_row_data(clean_rows)
        # Skip_row if passed
        if skip_row:
            all_row_data = all_row_data[1:]
        # Exclude totals rows if True...this overwrites passed drop_rows
        if exclude_totals == True:
            totals_rows = self.detect_totals_rows(all_row_data)
            drop_rows = totals_rows
        # Drop rows if > 0
        if drop_rows > 0:
            all_row_data = all_row_data[:(-drop_rows)]
        data_dict = self.convert_row_data_to_dict(all_row_data)
        return data_dict

    def get_all_tables(self, soup):
        """
        Extract all tables from a BeautifulSoup object, including those embedded within comments.

        Parameters
        ----------
        soup : BeautifulSoup
            The BeautifulSoup object containing the HTML content to be parsed.

        Returns
        -------
        list of BeautifulSoup
            A list of BeautifulSoup objects representing all tables found in the HTML content, 
            including those within comments.

        Notes
        -----
        This function first finds all tables directly within the HTML content. It then uses the 
        `get_commented_tables` method to find and extract any tables that are embedded within comments.
        The combined list of tables is returned.
        """
        # Find all non-commented tables
        tables = soup.find_all('table')
        # Find all tables embedded in comments
        tables_commented = self.get_commented_tables(soup)
        
        # Return concatenated list of tables
        return tables + tables_commented

    def get_commented_tables(self, soup):
        """
        Extract tables embedded in comments from the HTML content and return them as BeautifulSoup objects.

        Parameters
        ----------
        soup : BeautifulSoup
            The BeautifulSoup object containing the HTML content to be parsed.

        Returns
        -------
        list of BeautifulSoup
            A list of BeautifulSoup objects representing the tables found within comments in the HTML.

        Notes
        -----
        Some tables in fbref HTML code are embedded in comments. This function finds all comments within the 
        BeautifulSoup object, checks if they contain tables, and if so, extracts and returns these tables 
        as BeautifulSoup objects.
        """ 
        # Find all comments in the BeautifulSoup object
        comments = soup.find_all(string=lambda text: isinstance(text, Comment))
        tables = []
        if comments:
            # check if comments have table object and return table as BeautifulSoup object if so
            for comment in comments:
                if(BeautifulSoup(comment, 'html.parser').find('table')):
                    tables.append(BeautifulSoup(comment, 'html.parser').find('table'))
        return tables
    
    def convert_row_data_to_dict(self, all_row_data):
        """
        Given BeautifulSoup rows, create a dictionary with headers as keys and lists of data as values.

        Parameters
        ----------
        all_row_data : list of BeautifulSoup
            A list of BeautifulSoup representing rows as the result of the parse_all_row_data method.

        Returns
        -------
        dict
            A dictionary where each key represents a header and the corresponding value is a list of data extracted from rows.

        Notes
        -----
        This function assumes that the first row in the input list represents the headers.
        It cleans the headers by formatting them and adds suffixes to repeated headers.
        Then, it iterates over each column name and its corresponding row data, storing them in a dictionary.
        """
        # Extract column header row
        headers = all_row_data[0]
        # Format and add suffixes if neccessary to column headers
        clean_headers = [self.format_field(x) for x in headers]
        clean_headers = self.add_suffix_to_repeat_headers(clean_headers)
        # Extract data rows
        row_data = all_row_data[1:]
        # Store in dictionary
        data_dict = {}
        # Iterate over each column name and its corresponding row data
        for ch, row_data in zip(clean_headers, zip(*row_data)):
            data_dict[ch] = list(row_data)
        return data_dict
    
    def detect_totals_rows(self, all_row_data):
        """
        Some rows in football reference tables are rows of totals which we may want to exclude.
                
        This function counts the rows which are 'totals' rows instead of standard rows.

        Parameters
        ----------
        all_row_data : list of BeautifulSoup
            A list of BeautifulSoup representing rows as the result of the parse_all_row_data method.

        Returns
        -------
        int
            The number of rows detected as 'totals' rows.

        Notes
        -----
        This function iterates over each row in the input list, starting from the end, and checks if the first element contains the string "Total".
        It counts the number of rows detected as 'totals' rows and returns this count.
        """
        totals_rows = 0
        for i in range(len(all_row_data)):
            check = all_row_data[-(i+1)][0]

            if "Total" in check:
                totals_rows += 1
            else:
                break
        return totals_rows
    
    def add_suffix_to_repeat_headers(self, headers):
        """
        Add suffixes to column headers if they are repeated.

        Parameters
        ----------
        headers : list of str
            A list containing column header strings.

        Returns
        -------
        list of str
            A list of header strings with suffixes added to repeated column headers.

        Notes
        -----
        This function iterates over each column header in the input list. If a column header is repeated, a numerical suffix is added
        to distinguish it from the previous occurrences. The modified list of headers is then returned.
        """
        # Keep track of header name occurrences
        header_count = {}
        result = []
        for header in headers:
            # Add distrinct suffix to repeat headers
            if header in header_count:
                header_count[header] += 1
                result.append(f"{header}{header_count[header] - 1}")
            else:
                header_count[header] = 1
                result.append(header)
        return result

    def parse_all_row_data(self, clean_rows):
        """
        Parse all clean table rows into a list of rows with headers in the first row and data in the remaining rows.

        Parameters
        ----------
        clean_rows : list of BeautifulSoup
            A list containing BeautifulSoup objects representing the clean rows of a table produced by the parse_table_rows method.

        Returns
        -------
        list of list
            A list of lists containing the parsed data from each row of the table.

        Notes
        -----
        This function iterates over each clean row and uses the `parse_row_data` function to extract the data. 
        The extracted data is then appended to a list, which is returned.
        """
        all_row_data = []
        for clean_row in clean_rows:
            all_row_data.append(self.parse_row_data(clean_row))
        return all_row_data

    def parse_row_data(self, clean_row):
        """
        Extract table header or table data from a clean row object produced by the parse_table_rows method.

        Parameters
        ----------
        clean_row : BeautifulSoup
            The BeautifulSoup object representing the clean row of a table.

        Returns
        -------
        list
            A list containing the extracted data from the row.

        Notes
        -----
        This function extracts both table headers and table data from the given clean row by finding all <th> and <td> tags
        and retrieving the text content.
        """
        row_data = []
        # Extract table header or table data rows only
        for entry in clean_row.find_all(['th', 'td']):
            row_data.append(entry.get_text(strip=True)) 
        return row_data
    
    def parse_table_rows(self, table):
        """
        Extract rows from a BeautifulSoup table, excluding empty rows.

        Parameters
        ----------
        table : BeautifulSoup
            The BeautifulSoup object representing the table from which to extract rows.

        Returns
        -------
        list of BeautifulSoup
            A list of BeautifulSoup objects representing the non-empty rows in the table.

        Notes
        -----
        This function retrieves all rows (`<tr>` elements) from the given table. It then filters out rows that 
        are considered empty, specifically those that have a class attribute with the value 'spacer'.
        """
        # Find all rows in table
        rows = table.find_all('tr')
        # Filter out empty rows
        clean_rows = [row for row in rows if 'class' not in row.attrs or 'spacer' not in row['class']]
        return clean_rows

    def get_tables_from_caption(self, all_tables, regex_patterns):
        """
        Identify and return a single table or multiple tables with specific names or name patterns from a larger list of tables.

        Parameters
        ----------
        all_tables : list of BeautifulSoup
            A list of BeautifulSoup table objects to search through; typically a result of get_all_tables method.
        regex_patterns : list of str
            A list of regex patterns to match against the table names.

        Returns
        -------
        list of BeautifulSoup or None
            A list of BeautifulSoup table objects that match any of the passed regex patterns.
            Returns None if no tables match the given patterns.

        Notes
        -----
        This function iterates through each table in `all_tables` and checks if its caption matches any of the `regex_patterns`.
        If a match is found and the table name has not been previously matched, the table is added to the list of matched tables.
        
        In some cases the get_all_tables may return multiple tables with the same table name.
        In this case the second table with the same name has been found to be erroneous. This function prevents the first table from being overwritten.
        """
        tables = []
        table_names = [] # Store names to check if repeat value or not
        # Iterate through
        for table in all_tables:
            for regex_pattern in regex_patterns:
                table_name = re.findall(regex_pattern, self.get_table_name(table))
                if table_name:
                    # Do not overwrite table if exists
                    if table_name not in table_names:
                        tables.append(table)
                        table_names.append(table_name)
        # Return None if there are no tables
        if len(tables) > 0:
            return tables
        else:
            return None
    
    def get_table_name(self, table, remove_table=True):
        """
        Extract the name of a football reference table.

        Parameters
        ----------
        table : BeautifulSoup
            The BeautifulSoup object representing the table from which to extract the name.
        remove_table : bool, optional
            Whether to remove the string "Table" from the table name. Default is True.

        Returns
        -------
        str or None
            The name of the table. If the table has no caption, returns None.

        Notes
        -----
        This function retrieves the name from the caption of the given table. If the `remove_table`
        parameter is True, it removes the string "Table" from the name.
        """
        # Fetch table name if exists
        try:
            table_name = table.caption.text.strip()
        except:
            return None
        # Remove the word "Table" if remove_table=True
        if ("Table" in table_name) & (remove_table):
            table_name = table_name.replace("Table", "").strip()
        return table_name
    
    def get_all_items_from_table_urls(self, table, patterns):
        """
        Extract string items from URLs in a table using specified patterns.

        Parameters
        ----------
        table : BeautifulSoup
            The BeautifulSoup object representing the table containing URLs.
        patterns : list of str
            A list of regex patterns to match against the URLs.

        Returns
        -------
        list
            A list of string items extracted from the URLs based on the provided patterns.
        """

        clean_rows = self.parse_table_rows(table)
        items = []
        for row in clean_rows:
            hrefs = [a.get('href') for a in row.find_all('a') if a.get('href')]
            for href in hrefs:
                item = self.parse_pattern_from_url(patterns, href)
                if item:
                    items.append(item)
                    break
        return items
    
    def parse_pattern_from_url(self, patterns, url):
        """
        Check if any of the provided regex patterns match the given URL.

        Parameters
        ----------
        patterns : list of str
            A list of regex patterns to check for matches in the URL.
        url : str
            The URL to be checked against the regex patterns.

        Returns
        -------
        str or None
            The first match found from the patterns in the URL. Returns None if no matches are found.

        Notes
        -----
        This function iterates through the list of regex `patterns` and applies each pattern to the `url`.
        If a match is found, the first match is returned. If no matches are found after checking all patterns,
        the function returns None.
        """
        # Iterate through each pattern specified
        for pattern in patterns:
            match = re.findall(pattern, url)
            # Check if match produced and return if so
            if len(match) > 0:
                return match[0]
            else:
                continue
        if len(match) == 0:
            return None
    
    def rename_dict_key(self, data_dict, old_key, new_key):
        """
        Rename a key in a dictionary.
        
        Parameters:
            - d : The dictionary
            - old_key : The old key to be renamed
            - new_key : The new key
        
        Returns:
            The modified dictionary with the key renamed.
        """
        # Create a new key-value pair with the new key and the value of the old key
        data_dict[new_key] = data_dict.pop(old_key)
        return data_dict
    
    def reorder_dict_keys(self, data_dict, new_order):
        """
        Reorder the keys of a dictionary based on a specified order.

        This function takes a dictionary `data_dict` and a list `new_order` containing
        the desired order of keys. It returns a new dictionary with the keys reordered
        according to the order specified in `new_order`.

        Parameters
        ----------
        data_dict : dict
            The dictionary whose keys are to be reordered.
        new_order : list
            A list containing the new order of keys. Keys not present in `new_order`
            are placed at the end of the dictionary in their original order.

        Returns
        -------
        dict
            A new dictionary with keys reordered according to the specified order.

        Notes
        -----
        If any key in `new_order` is not present in `data_dict`, it is ignored.
        """
        return {k: data_dict[k] for k in new_order if k in data_dict}
    
    def delete_dict_keys(self, data_dict, keys_to_delete):
        """
        Delete specified keys from a dictionary.

        This function takes a dictionary `data_dict` and a list of keys `keys_to_delete`,
        and removes the specified keys from the dictionary.

        Parameters
        ----------
        data_dict : dict
            The dictionary from which keys are to be deleted.
        keys_to_delete : list
            A list containing the keys to be deleted from the dictionary.

        Returns
        -------
        dict
            A dictionary with the specified keys removed.

        Notes
        -----
        If any key in `keys_to_delete` is not present in `data_dict`, it is ignored.

        This function modifies the input dictionary in place and returns the modified
        dictionary. If you need to keep the original dictionary intact, make a copy of
        the dictionary before passing it to this function.
        """
        for key in keys_to_delete:
            # Check if key in dict
            if key in data_dict.keys(): 
                # Delete keys
                data_dict.pop(key) 
        return data_dict
    
    def change_dict_orientation(self, input_dict, id_key):
        """
        Change the orientation of a dictionary.

        This function takes a dictionary where column names are keys and a list of column data
        are values, and transforms it into a dictionary where each row of data is represented
        as a dictionary with column names as keys and corresponding column data for that row
        as values.

        Parameters
        ----------
        input_dict : dict
            The input dictionary to be transformed. It should have column names as keys and
            a list of column data as values.
        id_key : str
            The key in the input dictionary representing the column that serves as the
            identifier for each row.

        Returns
        -------
        dict
            A dictionary representing the transformed data, with a list of rows where each
            row is a dictionary containing column names as keys and column data for that row
            as values.

        Notes
        -----
        This function assumes that the input dictionary represents tabular data, where each
        key corresponds to a column name and the associated value is a list of data points
        for that column. The `id_key` parameter specifies the key in the input dictionary
        that serves as the identifier for each row.

        This function recursively processes nested dictionaries within the input dictionary,
        ensuring that the orientation change applies to all levels of nesting.
        """
        def process_value(value):
            if isinstance(value, list):
                return value[i]
            elif isinstance(value, dict):
                return {k2: process_value(v2) for k2, v2 in value.items()}
            else:
                return value
        id_key_vals = input_dict[id_key]
        new_dict = {'data': []}
        for i, _ in enumerate(id_key_vals):
            mini_dict = {k: process_value(v) for k, v in input_dict.items()}
            new_dict['data'].append(mini_dict)
        return new_dict
    
    def convert_dict_dtypes(self, data_dict, int_keys, float_keys):
        """
        Convert specified keys in a dictionary from string data to integers or floats.

        This function takes a dictionary `data_dict` and converts the values of
        specified keys to integers or floats based on the `int_keys` and `float_keys`
        arguments. The values corresponding to keys in `int_keys` will be converted
        to integers, and the values corresponding to keys in `float_keys` will be
        converted to floats.

        Parameters
        ----------
        data_dict : dict
            The dictionary containing the data to be converted.

        int_keys : list
            A list of keys whose values should be converted to integers.

        float_keys : list
            A list of keys whose values should be converted to floats.

        Returns
        -------
        dict
            A dictionary with specified keys converted to the desired data types.
        """
        for k in data_dict.keys():
            # Convert int keys data to integers
            if k in int_keys:
                data_dict[k] = self.convert_list_from_str(data_dict[k])
            # Convert float keys data to floats
            elif k in float_keys:
                data_dict[k] = self.convert_list_from_str(data_dict[k], convert_to='float')
        return data_dict
    
    def convert_list_from_str(self, list_of_strings, convert_to='int'):
        """
        Convert a list of strings to a list of integers or floats.

        This function takes a list of strings `list_of_strings` and converts each
        string element to either integers or floats based on the `convert_to` argument.
        If `convert_to` is 'int', the strings are converted to integers. If it is
        'float', the strings are converted to floats. Any empty string or None value
        in the input list will be converted to None in the output list.

        Parameters
        ----------
        list_of_strings : list of str
            The list of strings to be converted.

        convert_to : {'int', 'float'}, optional
            The type to which the strings should be converted. Default is 'int'.

        Returns
        -------
        list
            A list of converted values.
        """
        # If int specified, convert list to integers
        if convert_to =='int':
            converted_list = [int(x) if x is not None and x != '' else None for x in list_of_strings]
        # If float specified, convert list to floats
        elif convert_to == 'float':
            converted_list = [float(x) if x is not None and x != '' else None for x in list_of_strings]
        else:
            converted_list = list_of_strings
        return converted_list
    
    
    def format_field(self, field):
        """
        Format a data field name to lowercase and remove white spaces.

        This function takes a field name `field` and returns a formatted version
        of it with the following modifications:
        - Convert the field name to lowercase.
        - Remove leading and trailing white spaces.
        - Replace any internal white spaces with underscores.

        Parameters
        ----------
        field : str
            The field name to be formatted.

        Returns
        -------
        str
            The formatted field name.
        """
        clean_field = field.strip().lower().replace(" ", "_")
        return clean_field
    
    def clean_team_name(self, team_name):
        """
        Clean raw team name data.

        Sometimes football reference team or country names begin with 2-3 lowercase letter
        abbreviations which are removed by this function. Additionally, some team names may
        have additional data preceded by a dash, which is also removed.

        Parameters
        ----------
        team_name : str
            The raw team name or country name to be cleaned.

        Returns
        -------
        str
            The cleaned team name.

        Notes
        -----
        This function removes any leading 2-3 letter abbreviations from the team name and
        any additional data preceded by a dash, returning the cleaned team name.
        """
        # Check for abbreviation and remove
        if len(re.findall(r"^[a-z]{2,3}(.*)", team_name)) > 0:
            team_name = re.findall(r"^[a-z]{2,3}(.*)", team_name)[0]
        # Check for additional data and remove
        if len(team_name.split('-')) > 1:
            team_name = ' '.join(team_name.split('-')[:-1])
        return team_name
    
    def clean_gf_ga(self, gf_ga):
        """
        Clean the goals for or goals against data.

        If the input string contains data in the format "X (Y)", where X is the actual
        number of goals and Y is the number of goals scored in a shootout, this function
        extracts and returns only the actual number of goals.

        Parameters
        ----------
        gf_ga : str
            The input string representing either goals for or goals against data entry.

        Returns
        -------
        str
            The cleaned goals for or goals against data.

        Notes
        -----
        If the input string contains data in the format "X (Y)", where X is the actual
        number of goals and Y is the number of goals scored in a shootout, this function
        extracts and returns only the actual number of goals. If the input string does not
        match this format, it is returned unchanged.
        """
        # Check the string to see if it includes shootout data
        check = re.findall(r"(\d+)\s*\((\d+)\)",gf_ga)
        # Remove shootout data if exists
        if len(check) > 0:
            gf_ga_clean = check[0][0]
        # Return original string otherwise
        else:
            gf_ga_clean = gf_ga
        return gf_ga_clean
        
    def get_league_type_adv(self, league_id):
        """
        Retrieve the competition type and advanced stats availability for a given football reference league ID.

        Parameters
        ----------
        league_id : int
            The football reference league ID for which to retrieve information.

        Returns
        -------
        tuple or None
            A tuple containing two elements:
                - The availability of advanced stats (either 'yes' or 'no').
                - The competition type ('cup' or 'league').
            Returns None if the league ID is not found in the adv_cup_dict attribute.

        Notes
        -----
        This function utilizes the adv_cup_dict attribute to identify the competition type (cup or league) 
        and the availability of advanced statistics (yes or no) for the given league ID. 
        If the league ID is not found in the adv_cup_dict attribute, the function returns None.
        """
        try:
            # Get has advanced stat and league type if exists
            has_adv_stats = self.adv_cup_dict[str(league_id)]['has_adv_stats']
            league_type = self.adv_cup_dict[str(league_id)]['comp_type']
            return has_adv_stats, league_type
        except:
            return None
    
    

    


        
