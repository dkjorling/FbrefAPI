
import re
import datetime as dt
import numpy as np
from scraper.fbref_scraper import FbrefScraper

class FbrefPlayersScraper(FbrefScraper):
    """
    FbrefPlayersScraper scrapes and cleans football reference player data for a given player id

    Main Functionality Methods
    -------
    scrape_clean_data(self, team_id, season_id=None):
        Scrapes and cleans football reference players data for a specified football reference player id

    clean_data(self, team_tables):
        Cleans raw players data scraped by the scrape_player_data method
        
    scrape_player_data(self, team_id, season_id=None):
        Scrapes football reference standings data for a specified football reference league id and season id

    Notes
    -------   
    Player meta-data, when available includes:

    1) player_id - str; 8-character football reference player id
    2) full_name - str; player name
    3) positions - list of str; list of positions player plays in
    4) footed - str; whether a player is primarily right or left foted
    5) date_of_birth - str; date of birth in %Y-%m-%d format
    6) nationality - str; full country name of player nationality
    7) wages - str; amount of wages and how often wage is paid
    8) height - float; height in centimeters
    9) photo_url - str; url containing player photo
    10) birth_country - str; full country of birth name
    11) weight - float; player weight in kg
    """
    # Initialization Methods
    def __init__(self):
        # Call parent class (FbrefEntity) initialization
        super().__init__()
    
    # Main Functionality Methods
    def scrape_clean_data(self, player_id):
        """
        Scrapes and cleans football reference player data for a specified football reference player id

        Parameters
        ----------
        player_id : str
            8-character string representing a player's football reference id
        
        Returns
        -------
        dict
            A dictionary containing the cleaned player data for a specified player id
        """
        # Scrape player data
        player_data_dict = self.scrape_player_data(player_id)
        # Clean player data
        player_data_dict_clean = self.clean_data(player_data_dict)
        return player_data_dict_clean
    
    def clean_data(self, player_data_dict):
        """
        Clean football reference player data for a specified football reference player id

        Parameters
        ----------
        player_data_dict : dict
            Dictionary containing raw data fetched by the scrape_player_data method.
        
        Returns
        -------
        dict
            A dictionary containing the cleaned player data for a specified player id
           
        Notes
        -------
        This method calls sub-class specific cleaning method, clean_players
        """
        # Call sub-class specific cleaning method
        player_data_dict_clean = self.clean_players(player_data_dict)
        return player_data_dict_clean

    def scrape_player_data(self, player_id):
        """
        Scrapes football reference player data for a specified football reference player id

        Parameters
        ----------
        player_id : str
            8-character string representing a player's football reference id
        
        Returns
        -------
        dict
            A dictionary containing the raw player data for a specified player id
        """
        # Define url to scrape from
        url = f"https://fbref.com/en/players/{player_id}/"
        #  Create dictionary for storing
        player_data_dict = {}
        # Set non-name variables to np.nan by default
        try:
            soup = self.scrape_data_requests(url)
            player_info = soup.find('div', {'class': 'players', 'id': 'info'})
        except Exception as e:
            print(f"Could not get player info for player_id: {player_id} due to error: {e}")
            return None
        # Get player meta-data fields
        player_data_dict['player_id'] = player_id
        player_data_dict['full_name'] = self.parse_name(player_info) # name
        player_data_dict['positions'] = self.parse_position(player_info) 
        player_data_dict['footed'] = self.parse_footed(player_info) 
        player_data_dict['date_of_birth'] = self.parse_dob(player_info) 
        player_data_dict['birth_city'] = self.parse_birthplace(player_info) 
        player_data_dict['nationality'] = self.parse_nationality(player_info) 
        player_data_dict['wages'] = self.parse_wages(player_info) 
        player_data_dict['height'] = self.parse_height_weight(player_info) 
        player_data_dict['photo_url'] = self.parse_photo_url(player_info) 
        return player_data_dict
    
    # Helper Methods
    def clean_players(self, player_data_dict):
        """
        Clean football reference player data for a specified football reference player id
        
        Parameters
        ----------
        player_data_dict : dict
            Dictionary containing raw data fetched by the scrape_player_data method.
        
        Returns
        -------
        dict
            A dictionary containing the cleaned player data for a specified player id
        """
        # Clean player data dict fields
        player_data_dict['date_of_birth'] = self.clean_players_dob(player_data_dict['date_of_birth'])
        player_data_dict['birth_country'] = self.clean_players_birthplace(player_data_dict['birth_city'], return_value='country')
        player_data_dict['birth_city'] = self.clean_players_birthplace(player_data_dict['birth_city'], return_value='city')
        player_data_dict['weight'] = self.clean_players_htwt(player_data_dict['height'], return_value='wt')
        player_data_dict['height'] = self.clean_players_htwt(player_data_dict['height'], return_value='ht')
        return player_data_dict

    def parse_name(self, player_info):
        """
        Given BeautifulSoup object containing player meta-data, retrun player name
        
        Parameters
        ----------
        player_info : BeautifulSoup
            BeautifulSoup object containing player meta-data
        
        Returns
        -------
        str
            String representing player name
        """
        # Get player name if available; return None otherwise
        try:
            pname = player_info.find('span').text
            return pname
        except:
            return None

    def parse_position(self, player_info):
        """
        Given BeautifulSoup object containing player meta-data, retrun player position string
        
        Parameters
        ----------
        player_info : BeautifulSoup
            BeautifulSoup object containing player meta-data
        
        Returns
        -------
        str
            String representing player position(s)
        """
        # Get player position if available; return None otherwise
        strong = player_info.find_all('strong')
        strong_texts = [x.text for x in strong]
        if 'Position:' in strong_texts:
            position = re.findall(r'[A-Z]{2}', player_info.find('strong', text='Position:').find_next_sibling(string=True))
            return position
        else:
            return None

    def parse_footed(self, player_info):
        """
        Given BeautifulSoup object containing player meta-data, returns player footed info
        
        Parameters
        ----------
        player_info : BeautifulSoup
            BeautifulSoup object containing player meta-data
        
        Returns
        -------
        str
            String representing player footed
        """
        # Get player footed if available; return None otherwise
        strong = player_info.find_all('strong')
        strong_texts = [x.text for x in strong]
        if 'Footed:' in strong_texts:
            footed = player_info.find('strong', text='Footed:').find_next_sibling(string=True).strip()
            return footed
        else:
            return None

    def parse_dob(self, player_info):
        """
        Given BeautifulSoup object containing player meta-data, returns player date of birth info
        
        Parameters
        ----------
        player_info : BeautifulSoup
            BeautifulSoup object containing player meta-data
        
        Returns
        -------
        str
            String representing player date of birth info
        """
        # Get player date of birth if available; return None otherwise
        strong = player_info.find_all('strong')
        strong_texts = [x.text for x in strong]
        if 'Born:' in strong_texts:
            try:
                birth_tag = player_info.find('span', {'data-birth': True, 'id': 'necro-birth'})
                dob = birth_tag['data-birth']
                return dob
            except:
                    try:
                        dob = player_info.find('strong', string='Born:').find_next('span').text
                        return dob
                    except:
                        return None
        else:
            return None

    def parse_birthplace(self, player_info):
        """
        Given BeautifulSoup object containing player meta-data, returns player birthplace info
        
        Parameters
        ----------
        player_info : BeautifulSoup
            BeautifulSoup object containing player meta-data
        
        Returns
        -------
        str
            String representing player birthplace
        """
        # Get player birthplace if available; return None otherwise
        strong = player_info.find_all('strong')
        strong_texts = [x.text for x in strong]
        if 'Born:' in strong_texts:
            birth_tag = player_info.find('span', {'data-birth': True, 'id': 'necro-birth'})
            birth_city_tag = birth_tag.find_next('span').text
            if len(re.findall(r'\s+(in)\s+', birth_city_tag)) > 0:
                birthplace = re.findall(r'\s+(in.+)', birth_city_tag)[0]
                return birthplace
        else:
            return None
    
    def parse_nationality(self, player_info):
        """
        Given BeautifulSoup object containing player meta-data, returns player nationality
        
        Parameters
        ----------
        player_info : BeautifulSoup
            BeautifulSoup object containing player meta-data
        
        Returns
        -------
        str
            String representing player nationality
        """
        # Get player nationality if available; return None otherwise
        strong = player_info.find_all('strong')
        strong_texts = [x.text for x in strong]
        if 'National Team:' in strong_texts:
                nationality = player_info.find_all('strong', string='National Team:')[0].find_next('a').text
        elif ('Youth National Team:' in strong) & ('National Team:' not in strong):
            nationality = player_info.find_all('strong', string='Youth National Team:')[0].find_next('a').text
        elif ('National Team:' not in strong) & ('Youth National Team' not in strong) & ('Citizenship:' in strong):
            nationality = player_info.find_all('strong', string='Citizenship:')[0].find_next('a').text
        else:
            nationality = None
        return nationality

    def parse_wages(self, player_info):
        """
        Given BeautifulSoup object containing player meta-data, returns player wages
        
        Parameters
        ----------
        player_info : BeautifulSoup
            BeautifulSoup object containing player meta-data
        
        Returns
        -------
        str
            String representing player wages
        """
        # Get player wages if available; return None otherwise
        strong = player_info.find_all('strong')
        strong_texts = [x.text for x in strong]
        if 'Wages' in strong_texts:
            try:
                wages = re.sub(r"[￡$,]",'', player_info.find('span', class_='important poptip').text).strip()
                return wages
            except:
                return None
        else:
            return None

    def parse_height_weight(self, player_info):
        """
        Given BeautifulSoup object containing player meta-data, returns player height and weight info
        
        Parameters
        ----------
        player_info : BeautifulSoup
            BeautifulSoup object containing player meta-data
        
        Returns
        -------
        str
            String representing player height and weight
        """
        # Get player height/weight if available; return None otherwise
        try:
            ps = player_info.find_all('p')
            for p in ps:
                if re.search(r"\d+cm", p.text):
                    height_weight = p.text
                    return height_weight
        except:
            return None
    
    def parse_photo_url(self, player_info):
        """
        Given BeautifulSoup object containing player meta-data, returns player photo url
        
        Parameters
        ----------
        player_info : BeautifulSoup
            BeautifulSoup object containing player meta-data
        
        Returns
        -------
        str
            String representing player photo
        """
        # Get player photo if available; return None otherwise
        try:
            photo = player_info.find('img')['src']
            return photo
        except:
            return None
    
    def clean_players_dob(self, dob_raw):
        """
        Given raw date of birth string, return clean date of brith string
        
        Parameters
        ----------
        dob_raw : str
            Raw date of birth string
        
        Returns
        -------
        str
            String representing clean date of birth
        """
        if len(re.findall(r"\d{4}-\d{2}-\d{2}", str(dob_raw))) != 0:
            return dob_raw
        try:
            dob_clean = re.sub(r"\n", "", dob_raw)
            dob_clean = dob_clean.strip()
            dob_clean = dt.datetime.strptime(dob_clean, '%B %d, %Y')
            # Format the date in the desired format
            dob_clean = dob_clean.strftime('%Y-%m-%d')
        except:
            dob_clean = None
        return dob_clean
    
    def clean_players_birthplace(self, city_raw, return_value='all'):
        """
        Given raw city string, return clean city and country of birth if available
        
        Parameters
        ----------
        city_raw : str
            Raw city string
        
        return_value : str 
            one of ['all', 'city', 'country']
                - If all, then returns (city, country) tuple.
                - If city/country returns only city or country
        Returns
        -------
        tuple of str
            Returns clean city and country of birth where applicable
        """
        try:
            splt = city_raw.split(',')
            # Clean country data
            country_raw = splt[-1]
            country_clean = re.sub(r"['\[\]\",]", "", country_raw)
            country_clean = re.sub(r"in\s", "", country_clean)
            country_clean = country_clean.strip()
        
            city_raw = splt[:-1]
            if len(city_raw) == 0:
                city_clean = np.nan
            else:
                city_clean = str(city_raw[0])
                city_clean = re.sub(r"['\[\]\",]", "", city_clean)
                city_clean = re.sub(r"[-]", " ", city_clean)
                city_clean = re.sub(r"in\s", "", city_clean)
                city_clean = city_clean.strip()
            # If city_clean and country are equivalent, drop city
            if city_clean == country_clean:
                city_clean = np.nan
        except:
            city_clean = np.nan
            country_clean = np.nan

        # Return values
        if return_value == 'all':
            return (city_clean, country_clean)
        elif return_value == 'city':
            return city_clean
        elif return_value == 'country':
            return country_clean
        else:
            raise ValueError("return_value Value must be one of 'all', 'city', 'country'")
    
    def clean_players_htwt(self, htwt_raw, return_value='all'):
        """
        Given raw city string, return clean city and country of birth if available
        
        Parameters
        ----------
        htwt_raw : str
            Raw height and weight string
        
        return_value : str 
            one of ['all', 'ht', 'wt']
                -If all, then returns (ht, wt) tuple
                -If ht/wt returns only ht or wt
        Returns
        -------
        tuple of str
            Returns clean city and country of birth where applicable
        """
        # Clean height
        try:
            ht_raw = re.findall(r"\s*(\d+)cm", htwt_raw)[0]
            ht_clean = float(ht_raw)
        except:
            ht_clean = np.nan
        # Clean weight
        
        try:
            wt_raw = re.findall(r"\s*(\d+)kg", htwt_raw)[0]
            wt_clean = float(wt_raw)
        except:
            wt_clean = np.nan
        
        # Return values
        if return_value == 'all':
            return (ht_clean, wt_clean)
        elif return_value == 'ht':
            return ht_clean
        elif return_value == 'wt':
            return wt_clean
        else:
            raise ValueError("return_value Value must be one of 'all', 'ht', 'wt'")
    

    


    
            
        

    
        

    
        
        
            
        
        

    

    