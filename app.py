from flask import Flask, request
from flask import request
from flask_restful import Resource, Api
import scraper

app = Flask(__name__)
app.json.sort_keys = False # disable json sorting
# wrap app in flask Api module
api = Api(app)
# allow api to return non-ascii
api.app.config['RESTFUL_JSON'] = {
    'ensure_ascii': False
}


# define API endpoints
class Countries(Resource):
    """
    Endpoint to retrieve meta-data for all countries that have either domestic or international football teams that are tracked by football reference.

    If no parameters are passed, data for all countries is returned.

    If a country name is passed then data for only that specific country is returned.

    Query Parameters
    ----------------
    country - str, optional
        Name of country data to retrieve

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
    def get(self):
        # Extract query parameters
        country_name = request.args.get('country', None, type=str)

        # Get data
        countries_scraper = scraper.fbref_countries_scraper.FbrefCountriesScraper()
        country_data_dict_clean = countries_scraper.scrape_clean_data()
        if country_name:
            try:
                for i, country in enumerate(country_data_dict_clean['data']):
                    if country['country'] == country_name:
                        break
                small_country = country_data_dict_clean['data'][i]
                return small_country
            except:
                pass
        return country_data_dict_clean

class Leagues(Resource):
    """
    Endpoint to retrieve meta-data for all unique leagues associated with a specified country.

    Data is retrieved based on a country's three-letter country code used as identification within football reference. 

    Leagues are classified as one of the following:

    1) domestic_leagues - club-level league competitions occurring only within the specified country
    2) domestic_cups - club-level cup competitions occuring only within the specified country
    3) international_competitions - club-level competitions occuring between teams in specified coutnry and teams from other countries
    4) national_team_competitions - national team-level competitions where specified country's national team participated in

    Query Parameters
    ----------------
    country_code : str
        Three-letter code used by football reference to identify specific country

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
    def get(self):
        
        # Extract query parameters
        country_code = request.args.get('country_code', type=str)

        # Get data
        leagues_scraper = scraper.fbref_leagues_scraper.FbrefLeaguesScraper()
        leagues_dict_clean = leagues_scraper.scrape_clean_data(country_code)
        return leagues_dict_clean
    
class LeagueSeasons(Resource):
    """
    Endpoint to retrieve meta data for all season ids tracked by football reference, given a football reference league id.

    Query Parameters
    ----------------
    league_id : int
        Integer representing a league's football reference id

    Notes
    -------
    Meta-data, when available, includes:

    1) season_id - str; football reference season that is either in "%Y"  or "%Y-%Y" format, depending on the league
    2) competition_name - str; name of league; typically consistent across seasons although it does change on rare occassion
    3) #_squads - int; number of teams that competed in the league-season
    4) champion - str; name of team that won the competition for specified league-season
    5) top_scorer - dict; dictionary containing player(s) name (str) and number of goals scored (int) by top scorer for specified league-season
    """
    def get(self):
        # Extract query parameters
        league_id = request.args.get('league_id', type=int)
        
        # Get data
        ls_scraper = scraper.fbref_ls_scraper.FbrefLeagueSeasonsScraper()
        ls_data_dict_clean = ls_scraper.scrape_clean_data(league_id)
        
        return ls_data_dict_clean

class LeagueSeasonDetails(Resource):
    """
    Endpoint to retrieve meta-data for a specific league id and season id.

    Query Parameters
    ----------------
    league_id : int
        Football reference league id.
    season_id : str, optional
        Football reference season id. If not provided, defaults to None.

    Notes
    -------
    ** If season id parameter is not provided, data is scraped for most recent season id for the specified league id **

    Meta-data, when available, includes:

    1) league_start - str; string date in '%Y-%m-%d' format representing first match date for given league-season
    2) league_start - str; string date in '%Y-%m-%d' format representing last match date for given league-season
        ** Note ** If season has round format and still in progress, the actual last match date may be inaccurate due to currently unknown final match date
    3) league_type - str; either 'cup' or 'league'
    4) has_adv_stats - str; either 'yes' or 'no'; identifies whether advanced stats are available for specific league-season
    5) rounds - list of str; list of names of rounds if a league has a multiple round format
    """
    def get(self):
        # Extract query parameters
        league_id = request.args.get('league_id', type=int)
        season_id = request.args.get('season_id', None, type=str)
        
        # Get data
        ls_details_scraper = scraper.fbref_ls_details_scraper.FbrefLeagueSeasonDetailsScraper()
        ls_details_data_dict_clean = ls_details_scraper.scrape_clean_data(league_id, season_id)
        
        return ls_details_data_dict_clean

class LeagueStandings(Resource):
    """
    Endpoint to retrieve all standings tables for a given league and season id.
    
    If no season id is passed, retrieve standings tables for current season.

    Standings data varies based on both league type (league or cup) and whether or not the league has advanced stats available on football reference.

    Query Parameters
    ----------------
    league_id : int
        Integer representing a league's football reference id
    season_id : str, optional
        Football reference season id. If not provided, defaults to None.
    
    
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
    def get(self):
        # Extract query parameters
        league_id = request.args.get('league_id', type=str)
        season_id = request.args.get('season_id', None, type=str)

        # Get data
        league_standings_scraper = scraper.fbref_league_standings_scraper.FbrefLeagueStandingsScraper()
        lstd_dict = league_standings_scraper.scrape_clean_data(league_id, season_id)

        return lstd_dict

class Teams(Resource):
    """
    Endpoint to retrieve football reference team data for a given team and, optionally, season.

    Team data is grouped into two categories:

    1) team_roster
        Contains meta-data for all players who participated for the specified team and season
    
    2) team_schedule
        Contains meta-data for all matches played by specified team and season
    
    Query Parameters
    ----------------
    team_id : str
        8-character string representing a teams's football reference id
    season_id : str, optional
        Football reference season id. If not provided, defaults to None.

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
    def get(self):
        # Extract query parameters
        team_id = request.args.get('team_id', type=str)
        season_id = request.args.get('season_id', None, type=str)
        
        # Get data
        team_scraper = scraper.fbref_teams_scraper.FbrefTeamsScraper()
        team_data_dict_clean = team_scraper.scrape_clean_data(team_id=team_id, season_id=season_id)
        return team_data_dict_clean

class Players(Resource):
    """
    Endpoint to retrieve football reference player data for a given player id

    Query Parameters
    ----------------
    player_id : str
        8-character string representing a player's football reference id

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
    def get(self):
        # Extract query parameters
        player_id = request.args.get('player_id', type=str)
        
        # Get data
        player_scraper = scraper.fbref_players_scraper.FbrefPlayersScraper()
        player_data_dict_clean = player_scraper.scrape_clean_data(player_id)

        return player_data_dict_clean

class Matches(Resource):
    """
    Endpoint to retrieve match meta-data from Football Reference.

    There are two distinct match data returned by this class: 

    1) Team match data - When a team id is passed, this signals to the class to retrieve match meta-data for a specific team

    2) League match data - When a team id is not passed but a league id is, this indicates to the class to retrieve match meta-data for a specific league

    Query Parameters
    ----------------
    team_id : str, optional
        8-character string representing a teams's football reference id. If not provided, defaults to None.
    league_id : int, optional
        Integer representing a player's football reference id. If not provided, defaults to None.
    season_id : str, optional
        Football reference season id. If not provided, defaults to None.

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
    def get(self):
        # Extract query parameters
        team_id = request.args.get('team_id', None, type=str)
        league_id = request.args.get('league_id', None, type=int)
        season_id = request.args.get('season_id', None, type=str)
        
        # Get clean data
        matches_scraper = scraper.fbref_matches_scraper.FbrefMatchesScraper()
        matches_data_dict_clean = matches_scraper.scrape_clean_data(team_id, league_id, season_id)
        # return data
        return matches_data_dict_clean

class TeamSeasonStats(Resource):
    """
    Endpoint to retrieve season-level team statistical data for a specified league and season.

    Statistics are aggregate, average, or per 90 statistics over the course of a single season.

    Query Parameters
    ----------------
    league_id : int
        Integer representing a league's football reference id. 
    season_id : str, optional
        Football reference season id. If not provided, defaults to None.

    Notes
    -------   
    Advanced Statistical Categories:

    1) stats - general team stats such as goals and goals against
    2) keepers - general goalkeeping statistics
    3) keepersadv - advanced goalkeeping statistics
    4) shooting - statistics related to shot taking
    5) passing - statistics related to passing performance
    6) passing_types - statistics related to passing types completed
    7) gca - statistics related to goal- and shot-creating actions
    8) defense - statistics related to defense
    9) possession - statistics related to possession
    10) playingtime - statistics related to roster playing time
    11) misc - miscellaneous stats including cards and penalties

    Non-Advanced Statistical Categories:

    1) stats
    2) keepers
    3) shooting
    4) playtingtime
    5) misc

    ** Detailed statistic descriptions can be found in the API Documentation **
    """
    def get(self):
        # Extract query parameters
        league_id = request.args.get('league_id', None, type=int)
        season_id = request.args.get('season_id', None, type=str)
        
        # Get clean data
        team_season_stats_scraper = scraper.fbref_team_season_stats_scraper.FbrefTeamSeasonStatsScraper()
        team_seasons_stats_dict_clean = team_season_stats_scraper.scrape_clean_stats(
            league_id=league_id,
            season_id=season_id
            )

        return team_seasons_stats_dict_clean
    
class TeamMatchStats(Resource):
    """
    Endpoint to retrieve match-level team statistical data for a specified team, league and season.

    Query Parameters
    ----------------
    team_id : str
        8-character string representing football reference team id
    league_id : int
        Integer representing a league's football reference id. 
    season_id : str
        Football reference season id

    Notes
    -------   
    This class provides both meta-data related to each match and team statistics in covering various statistical categories.

    Match meta-data when available includes:

    1) match_id - str; 8-character football reference match id  
    2) date - str; date of match in %Y-%m-%d format
    3) round - str; name of round or matchweek number
    4) home_away - str; whether match was played 'Home' or 'Away' or 'Neutral'
    5) opponent - str; name of opposing team
    6) opponent_id str; 8-character football reference team id of opponent 

    Advanced Statistical Categories:

    1) schedule - general team stats such as goals and goals against
    2) keeper - all goalkeeping related stats
    3) shooting - statistics related to team shot taking
    4) passing - statistics related to passing performance
    5) passing_types - statistics related to passing types completed
    6) gca - statistics related to goal- and shot-creating actions
    7) defense - statistics related to defense
    8) possession - statistics related to possession
    9) misc - miscellaneous stats including cards and penalties

    Non-Advanced Statistical Categories:

    1) schedule
    2) keeper
    3) shooting
    4) misc

    ** Detailed statistic descriptions can be found in the API Documentation **
    """
    def get(self):
        # Extract query parameters
        team_id = request.args.get('team_id', None, type=str)
        league_id = request.args.get('league_id', None, type=int)
        season_id = request.args.get('season_id', None, type=str)
        
        # Get clean data
        team_match_stats_scraper = scraper.fbref_team_match_stats_scraper.FbrefTeamMatchStatsScraper()
        team_seasons_stats_dict_clean = team_match_stats_scraper.scrape_clean_stats(
            team_id=team_id,
            league_id=league_id,
            season_id=season_id
            )

        return team_seasons_stats_dict_clean

class PlayerSeasonStats(Resource):
    """
    Endpoint to retrieve season-level player statistical data for a specified team, league and season.

    Statistics are aggregate, average, or per 90 statistics over the course of a single season.

    Query Parameters
    ----------------
    team_id : str
        8-character string representing football reference team id
    league_id : int
        Integer representing a league's football reference id. If not provided, defaults to None
    season_id : str, optional
        Football reference season id. If not provided, defaults to None.


    Notes
    -------   
    Advanced Player Statistical Categories:

    1) stats - general team stats such as goals and goals against
    2) shooting - statistics related to shot taking
    3) passing - statistics related to passing performance
    4) passing_types - statistics related to passing types completed
    5) gca - statistics related to goal- and shot-creating actions
    6) defense - statistics related to defense
    7) possession - statistics related to possession
    8) playingtime - statistics related to roster playing time
    9) misc - miscellaneous stats including cards and penalties
    
    Advanced Keeper Statistical Categories:

    1) keepers - general goalkeeping statistics
    2) keepersadv - advanced goalkeeping statistics

    Non-Advanced Player Statistical Categories:

    1) stats
    2) keepers
    3) shooting
    4) playingtime
    5) misc

    Non-Advanced Keeper Statistical Categories:

    1) keepers

    This class provides both meta-data related to each player and team statistics in covering various statistical categories.

    Player meta-data when available includes:

    1) player_id - str; 8-character football reference player identification 
    2) player_name - str; name of player
    3) player_country_code - str; 3-digit country code attributed to player
    4) age - int; integer age of player at start of season

    ** Detailed statistic descriptions can be found in the API Documentation **
    """
    def get(self):
        # Extract query parameters
        team_id = request.args.get('team_id', None, type=str)
        league_id = request.args.get('league_id', None, type=int)
        season_id = request.args.get('season_id', None, type=str)
        
        # Get clean data
        player_season_stats_scraper = scraper.fbref_player_season_stats_scraper.FbrefPlayerSeasonStatsScraper()
        player_seasons_stats_dict_clean = player_season_stats_scraper.scrape_clean_stats(
            team_id=team_id,
            league_id=league_id,
            season_id=season_id
            )

        return player_seasons_stats_dict_clean

class PlayerMatchStats(Resource):
    """
    Endpoint to retrieve match-level player statistical data for a specified player, league and season.

    Query Parameters
    ----------------
    player_id : str
        8-character string representing football reference player id
    league_id : int
        Integer representing a league's football reference id.
    season_id : str, optional
        Football reference season id.

    Notes
    -------   
    ** IMPORTANT **
    
    For players where advanced stats are available, stat id types must be pulled one at a time.
    Football Reference has a scraping restriction of one every 3 seconds. 

    ** Therefore the main class functionality will take over 24 seconds to run each time **

    This class provides both meta-data related to each match and player statistics in covering various statistical categories.

    Match meta-data when available includes:

    1) match_id - str; 8-character football reference match id  
    2) date - str; date of match in %Y-%m-%d format
    3) round - str; name of round or matchweek number
    4) home_away - str; whether match was played 'Home' or 'Away' or 'Neutral'
    5) team_name - str; name of team that player played for
    6) team_id str; 8-character football reference team id for team player played for
    7) opponent - str; name of opposing team
    8) opponent_id str; 8-character football reference team id of opponent 

    Advanced Statistical Player Categories:

    1) summary - general team stats such as goals and goals against
    2) passing - statistics related to passing performance
    3) passing_types - statistics related to passing types completed
    4) gca - statistics related to goal- and shot-creating actions
    5) defense - statistics related to defense
    6) possession - statistics related to possession
    7) misc - miscellaneous stats including cards and penalties

    Non-Advanced Statistical Categories:

    1) summary

    ** Detailed statistic descriptions can be found in the API Documentation **
    """
    def get(self):
        # Extract query parameters
        player_id = request.args.get('player_id', type=str)
        league_id = request.args.get('league_id', type=int)
        season_id = request.args.get('season_id', type=str)
        
        # Get clean data
        player_match_stats_scraper = scraper.fbref_player_match_stats_scraper.FbrefPlayerMatchStatsScraper()
        player_match_stats_dict_clean = player_match_stats_scraper.scrape_clean_stats(
            player_id=player_id,
            league_id=league_id,
            season_id=season_id
            )

        return player_match_stats_dict_clean

class AllPlayersMatchStats(Resource):
    """
    Endpoint to retrieve match-level player statistical data for both teams for a specified match id

    Query Parameters
    ----------------
    match_id : str
            8-character string representing football reference match id
    
    Notes
    -------   
    This class provides both meta-data related to each player, and match-level player statistics covering various statistical categories.

    Player meta-data when available includes:

    1) player_id - str; 8-character football reference player id  
    2) player_name - str; name of player
    3) player_country_code - str; 3 letter abbreviation of player country
    4) player_number - str; number of player
    5) age - str; 

    Advanced Statistical Player Categories:

    1) summary - general team stats such as goals and goals against
    2) passing - statistics related to passing performance
    3) passing_types - statistics related to passing types completed
    4) defense - statistics related to defense
    5) possession - statistics related to possession
    6) misc - miscellaneous stats including cards and penalties
    7) keeper - basic and advanced keeper stats
    
    Non-Advanced Statistical Categories:

    1) summary
    2) keeper - basic keeper stats
    
    ** Detailed statistic descriptions can be found in the API Documentation **
    """
    def get(self):
        # Extract query parameters
        match_id = request.args.get('match_id', type=str)
        
        # Get clean data
        all_players_match_stats_scraper = scraper.fbref_all_players_match_stats_scraper.FbrefAllPlayersMatchStatsScraper()
        all_players_match_stats_dict_clean = all_players_match_stats_scraper.scrape_clean_stats(match_id)
        return all_players_match_stats_dict_clean



api.add_resource(Countries, '/countries/')
api.add_resource(Leagues, '/leagues/')
api.add_resource(LeagueSeasons, '/league-seasons/')
api.add_resource(LeagueSeasonDetails, '/league-season-details/')
api.add_resource(LeagueStandings, '/league-standings/')
api.add_resource(Teams, '/teams/')
api.add_resource(Players, '/players/')
api.add_resource(Matches, '/matches/')
api.add_resource(TeamSeasonStats, '/team-season-stats/')
api.add_resource(TeamMatchStats, '/team-match-stats/')
api.add_resource(PlayerSeasonStats, '/player-season-stats/')
api.add_resource(PlayerMatchStats, '/player-match-stats/')
api.add_resource(AllPlayersMatchStats, '/all-players-match-stats/')


if __name__ == '__main__':
    app.run(debug=True)  # Run the Flask application in debug mode
