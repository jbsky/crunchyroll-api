# Crunchyroll
# Copyright (C) 2024 Julien Blais
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os.path, os, random, json, argparse
from abc import abstractmethod

from datetime import timedelta, datetime
from typing import Optional, Dict

import requests
from requests import HTTPError, Response
from typing import Dict, List, Union


print (__name__)
if __name__ == "__main__":
    import utils
    from crunchyrollentity import *

if __name__ == "CrunchyrollAPI.crunchyrollapi":
    from CrunchyrollAPI.utils import *
    import CrunchyrollAPI.utils as utils
    from CrunchyrollAPI.crunchyrollentity import *

class CrunchyrollSettings:
    """Arguments class
    Hold all arguments passed to the script and also persistent user data and
    reference to the addon. It is intended to hold all data necessary for the
    script.
    """
    profile_path = './'
    device_id = None
    session_restart = False

    def __init__(self):
        """Initialize arguments object
        Hold also references to the addon which can't be kept at module level.
        """
        if not hasattr(self, "crunchyroll_username"):
            utils.crunchy_err(self, "No crunchyroll username")
            exit(11)

        if not hasattr(self, "crunchyroll_password"):
            utils.crunchy_err(self, "No crunchyroll password")
            exit(12)

        if not hasattr(self, "subtitle"):
            utils.crunchy_err(self, "No subtitle defined")
            exit(13)

        if not hasattr(self, "subtitle_fallback"):
            utils.crunchy_err(self, "subtitle_fallback")
            exit(13)

        if not self.device_id:
            char_set = "0123456789abcdefghijklmnopqrstuvwxyz0123456789"
            self.device_id = (
                    "".join(random.sample(char_set, 8)) +
                    "-" +
                    "".join(self.name[0:4]) +
                    "-" +
                    "".join(random.sample(char_set, 4)) +
                    "-" +
                    "".join(random.sample(char_set, 4)) +
                    "-" +
                    "".join(random.sample(char_set, 12))
            )
        
    @abstractmethod
    def name(self):
        pass

class CrunchyrollSettingsClass(CrunchyrollSettings):

        def __init__(self, SettingsData):

            if os.path.isfile(SettingsData.setting_file):
                with open(SettingsData.setting_file, "r") as infile:
                    setting = json.load(infile)

                for k, v in setting.items():
                    self.__setattr__(k, v)

            for i in SettingsData.__dict__:
                if SettingsData.__dict__[i] is not None:
                    self.__setattr__(i, SettingsData.__dict__[i])

            super().__init__()

            self.save()
        
        def save(self):
            json_save = self.__dict__
            rem_list = ["season_id", "id", "search", "session_restart", "search_type", "category_filter", "playlist", "crunchylist_filter", "season_filter", "field"]
            json_save = {k: v for k, v in self.__dict__.items() if k not in rem_list}

            with open(self.setting_file, "w") as outfile:
                    outfile.write(json.dumps(json_save, indent=2))
 
        @property
        def name(self):
              return "class"

class CrunchyrollSettingsArgs(CrunchyrollSettings):

        def __init__(self, argv):
            self.setting_file = argv.setting_file

            if os.path.isfile(argv.setting_file):
                with open(argv.setting_file, "r") as infile:
                    setting = json.load(infile)
            
                for k, v in setting.items():
                    self.__setattr__(k, v)

            for i in argv.__dict__:
                if argv.__dict__[i] is not None:
                    self.__setattr__(i, argv.__dict__[i])

                    # get account information
            if argv.username is not None and argv.username != "":
                self.crunchyroll_username = argv.username

            if argv.password is not None and argv.password != "":
                self.crunchyroll_password = argv.password
            
            if argv.subtitle is not None and argv.subtitle != "":
                self.subtitle = argv.subtitle
            
            if argv.subtitle_fallback is not None and argv.subtitle_fallback != "":
                self.subtitle_fallback = argv.subtitle_fallback

            super().__init__()

            self.save()

        def save(self):
                json_save = self.__dict__
                rem_list = ["season_id", "id", "search", "session_restart", "search_type", "category_filter", "playlist", "crunchylist_filter", "season_filter", "field"]
                json_save = {k: v for k, v in self.__dict__.items() if k not in rem_list}

                with open(self.setting_file, "w") as outfile:
                     outfile.write(json.dumps(json_save, indent=2))
        
        @property
        def name(self):
              return "argv"

class CrunchyrollAPI:
    """ Api documentation https://github.com/hyugogirubato/API-Crunchyroll-Beta/wiki/Api """
    URL = "https://api.crunchyroll.com/"
    VERSION = "1.1.21.0"

    INDEX_ENDPOINT = "https://beta-api.crunchyroll.com/index/v2"
    PROFILE_ENDPOINT = "https://beta-api.crunchyroll.com/accounts/v1/me/profile"
    TOKEN_ENDPOINT = "https://beta-api.crunchyroll.com/auth/v1/token"
    SEARCH_ENDPOINT = "https://beta-api.crunchyroll.com/content/v1/search"
    STREAMS_ENDPOINT = "https://beta-api.crunchyroll.com/cms/v2{}/videos/{}/streams"
    # SERIES_ENDPOINT = "https://beta-api.crunchyroll.com/cms/v2{}/series/{}"
    SEASONS_ENDPOINT = "https://beta-api.crunchyroll.com/cms/v2{}/seasons"
    EPISODES_ENDPOINT = "https://beta-api.crunchyroll.com/cms/v2{}/episodes"
    OBJECTS_BY_ID_LIST_ENDPOINT = "https://beta-api.crunchyroll.com/content/v2/cms/objects/{}"
    # SIMILAR_ENDPOINT = "https://beta-api.crunchyroll.com/content/v1/{}/similar_to"
    # NEWSFEED_ENDPOINT = "https://beta-api.crunchyroll.com/content/v1/news_feed"
    BROWSE_ENDPOINT = "https://beta-api.crunchyroll.com/content/v1/browse"
    # there is also a v2, but that will only deliver content_ids and no details about the entries
    WATCHLIST_LIST_ENDPOINT = "https://beta-api.crunchyroll.com/content/v1/{}/watchlist"
    # only v2 will allow removal of watchlist entries.
    # !!!! be super careful and always provide a content_id, or it will delete the whole playlist! *sighs* !!!!
    # WATCHLIST_REMOVE_ENDPOINT = "https://beta-api.crunchyroll.com/content/v2/{}/watchlist/{}"
    WATCHLIST_V2_ENDPOINT = "https://beta-api.crunchyroll.com/content/v2/{}/watchlist"
    CONTINUEWATCHING_ENDPOINT = "https://beta-api.crunchyroll.com/content/v1/{}/continue_watching"
    PLAYHEADS_ENDPOINT = "https://beta-api.crunchyroll.com/content/v2/{}/playheads"
    HISTORY_ENDPOINT = "https://beta-api.crunchyroll.com/content/v2/{}/watch-history"
    RESUME_ENDPOINT = "https://beta-api.crunchyroll.com/content/v2/discover/{}/history"
    SEASONAL_TAGS_ENDPOINT = "https://beta-api.crunchyroll.com/content/v2/discover/seasonal_tags"
    CATEGORIES_ENDPOINT = "https://beta-api.crunchyroll.com/content/v1/tenant_categories"
    SKIP_EVENTS_ENDPOINT = "https://static.crunchyroll.com/skip-events/production/{}.json"  # request w/o auth req.
    INTRO_V2_ENDPOINT = "https://static.crunchyroll.com/datalab-intro-v2/{}.json"

    CRUNCHYLISTS_LISTS_ENDPOINT = "https://beta-api.crunchyroll.com/content/v2/{}/custom-lists"
    CRUNCHYLISTS_VIEW_ENDPOINT = "https://beta-api.crunchyroll.com/content/v2/{}/custom-lists/{}"

    AUTHORIZATION = "Basic bHF0ai11YmY1aHF4dGdvc2ZsYXQ6N2JIY3hfYnI0czJubWE1bVdrdHdKZEY0ZTU2UU5neFQ="

    def __init__(self, account: CrunchyrollSettings = None, mode = "") -> None:
        self.http = requests.Session()
        self.locale: str = account.subtitle if hasattr(account, "subtitle") else None
        self.mode: str = mode
        self.account_data: AccountData = AccountData(dict())
        self.api_headers: Dict = {
            "User-Agent": "Crunchyroll/3.50.2",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        self.account = account
        self.account.items_per_page = 50
        self.account.offset = 0

    def start(self) -> bool:
        session_restart = self.account.session_restart

        # restore account data from file
        session_data = self.load_from_storage()
        if session_data and not session_restart:
            self.account_data = AccountData(session_data)
            account_auth = {"Authorization": f"{self.account_data.token_type} {self.account_data.access_token}"}
            self.api_headers.update(account_auth)

            # check if tokes are expired
            if datetime.utcnow() > utils.str_to_date(self.account_data.expires):
                session_restart = True
            else:
                return True

        # session management
        self.create_session(session_restart)

        return True

    def create_session(self, refresh=False) -> None:
        headers = {"Authorization": self.AUTHORIZATION}

        if not refresh:
            data = {
                "username": self.account.crunchyroll_username,
                "password": self.account.crunchyroll_password,
                "grant_type": "password",
                "scope": "offline_access",
            }
        else:
            data = {
                "refresh_token": self.account_data.refresh_token,
                "grant_type": "refresh_token",
                "scope": "offline_access",
            }

        r = self.http.request(method="POST", url=self.TOKEN_ENDPOINT, headers=headers, data=data)

        # if refreshing and refresh token is expired, it will throw a 400
        if r.status_code == 400:
            if refresh:
                utils.crunchy_info(self.account, "Invalid/Expired credentials, try restarting session from scratch")
                self.delete_storage()
                return self.create_session()
            else:
                utils.crunchy_err(self.account, "Failed to authenticate!")
                raise LoginError("Failed to authenticate")

        r_json = self.get_json_from_response(r)

        self.api_headers.clear()
        self.api_headers.update({"Authorization": "%s %s" % (r_json["token_type"], r_json["access_token"])})

        account_data = dict()
        account_data.update(r_json)

        # before make_request for refresh account data, we must clear object
        self.account_data = AccountData({})
        r = self.make_request(method="GET", url=self.INDEX_ENDPOINT)
        account_data.update(r)

        r = self.make_request(method="GET", url=self.PROFILE_ENDPOINT)
        account_data.update(r)

        expire = datetime.utcnow() + timedelta(seconds=float(account_data["expires_in"]))
        account_data["expires"] = utils.date_to_str(expire)

        self.account_data = AccountData(account_data)

        self.write_to_storage()

    def close(self) -> None:
        """Saves cookies and session
        """
        # no longer required, data is saved upon session update already

    def destroy(self) -> None:
        """Destroys session
        """
        self.delete_storage()

    def make_request(self, method: str, url: str, headers=dict(), params=dict(), data=None, json_data=None, is_retry=False ) -> Optional[Dict]:
        if self.account_data:
            if expiration := self.account_data.expires:
                if datetime.utcnow() > utils.str_to_date(expiration):
                    self.create_session(refresh=True)
            params.update({
                "Policy": self.account_data.cms.policy,
                "Signature": self.account_data.cms.signature,
                "Key-Pair-Id": self.account_data.cms.key_pair_id
            })
        request_headers = {}
        request_headers.update(self.api_headers)
        request_headers.update(headers)

        r = self.http.request(method, url, headers=request_headers, params=params, data=data, json=json_data)

        # something went wrong with authentication, possibly an expired token that wasn't caught above due to host
        # clock issues. set expiration date to 0 and re-call, triggering a full session refresh.
        if r.status_code == 401:
            if is_retry:
                raise LoginError('Request to API failed twice due to authentication issues.')

            utils.crunchy_err(self.account, "make_request_proposal: request failed due to auth error")
            self.account_data.expires = 0
            return self.make_request(method, url, headers, params, data, json_data, True)

        return self.get_json_from_response(r)

    def make_unauthenticated_request(self, method: str, url: str, headers=None, params=None, data=None, json_data=None) -> Optional[Dict]:
        """ Send a raw request without any session information """

        req = requests.Request(method, url, data=data, params=params, headers=headers, json=json_data)
        prepped = req.prepare()
        r = self.http.send(prepped)

        return self.get_json_from_response(r)

    def get_storage_path(self) -> str:
        """Get cookie file path
        """
        return self.account.profile_path

    def load_from_storage(self) -> Optional[Dict]:
        storage_file = self.get_storage_path() + "session_data.json"

        if not os.path.isfile(storage_file):
            return None

        with open(storage_file, 'r') as file:
            data = json.load(file)

        return data

    def delete_storage(self) -> None:
        storage_file = self.get_storage_path() + "session_data.json"

        if not os.path.isfile(storage_file):
            return None

        os.remove(storage_file)

    def write_to_storage(self) -> bool:
        storage_file = self.get_storage_path() + "session_data.json"

        with open(storage_file, 'w') as file:
            # serialize (Object has a to_str serializer)
            result = file.write(str(self.account_data))

        return result
    
    def list_categories(self):
        # api request for category names / tags
        req = self.make_request(method="GET", url=self.CATEGORIES_ENDPOINT, params={ "locale": self.account.subtitle })
        
        list = []

        for f in req["items"]:
            list.append(f['tenant_category'])

        return list

    def search_items_by_category(self, filter_categories):
        """ view all anime from selected mode """
        # category_filter: str = filter_categories
        params = {
            "locale": self.account.subtitle,
            "categories": filter_categories,
            "n": int(self.account.items_per_page) or 50,
            "start": int(self.account.offset) or 0,
            "ratings": 'true'
        }

        # api request
        req = self.make_request(method="GET", url=self.BROWSE_ENDPOINT, params = params)

        return self.get_listables_from_response(req.get('items'))

    def search_items_by_season(self, season_filter):
        """ view all available anime seasons """

        params = { "locale": self.account.subtitle, "season_tag": season_filter, "n": 100}

        req = self.make_request(method = "GET", url = self.BROWSE_ENDPOINT, params = params)

        return self.get_listables_from_response(req.get('items'))

    def search_season_by_series_id(self, id):
        """ view all seasons/arcs of an anime """

        if not hasattr(self.account, 'subtitle'):
            raise CrunchyrollError('subtitle not defined')

        url = self.SEASONS_ENDPOINT.format(self.account_data.cms.bucket)
        params = { "locale": self.account.subtitle,
                   "series_id": id,
                   "preferred_audio_language": self.account_data.default_audio_language,
                   "force_locale": ""
        }
        # api request
        req = self.make_request(method = "GET", url = url, params = params)

        return self.get_listables_from_response(req.get('items'))

    def list_seasons(self) -> List[ListableItem]:
        """ view all available seasons """
        params = {"locale": self.account.subtitle}

        req = self.make_request(method = "GET", url = self.SEASONAL_TAGS_ENDPOINT, params = params )

        list = []

        for f in req["data"]:
            list.append(f['id'])

        return list
    
    def search_items_by_string(self, search, search_type ="series"):
        """ Search for string by type 
            available types seem to be: music,series,episode,top_results,movie_listing
            TODO: Extract all search type
        """

        if not hasattr(self.account, "offset"):
                self.account.offset = 0

        url = self.SEARCH_ENDPOINT
        params = {
            "n": 50,
            "q": search,
            "locale": self.account.subtitle,
            "start": int(self.account.offset) or 0,
            "type": search_type
        }

        req = self.make_request(method="GET", url = url, params = params)

        type_data = req.get('items')[0]  # @todo: for now we support only the first type, which should be series
        return self.get_listables_from_response(type_data.get('items'))

    def search_item_by_season_id(self, season_id):
        """ view all episodes of season """

        url = self.EPISODES_ENDPOINT.format(self.account_data.cms.bucket)
        params = { "locale": self.account.subtitle, "season_id": season_id }

        req = self.make_request(method = "GET", url = url, params = params)

        return self.get_listables_from_response(req.get('items'))

    def list_item_by_history(self):
        """ shows history of watched anime
        """
        items_per_page = 50
        current_page = int(self.account.offset) or 1

        url = self.HISTORY_ENDPOINT.format(self.account_data.account_id)
        params = { "page_size": items_per_page, "page": current_page, "locale": self.account.subtitle}
        
        req = self.make_request( method="GET", url = url, params = params)

        return self.get_listables_from_response(req.get('data'))

    def list_item_resume(self):
        """ shows episode to resume for continue_watching animes
        """
        items_per_page = 50

        if not hasattr(account, "offset"):
                self.account.offset = 0

        url = self.RESUME_ENDPOINT.format(self.account_data.account_id)
        params = { "n": items_per_page, "locale": self.account.subtitle, "start": int(self.account.offset) }

        req = self.make_request(method = "GET", url = url, params = params)

        return self.get_listables_from_response(req.get('data'))

    def get_playlist(self):
        """ shows anime queue/playlist """
        params = { "n": 1024, "locale": self.account.subtitle }
        url = self.WATCHLIST_LIST_ENDPOINT.format(self.account_data.account_id)

        req = self.make_request(method = "GET", url = url, params = params)

        return self.get_listables_from_response(req.get('items'))

    def list_crunchylists(self):
        """ Retrieve all crunchylists """

        url = self.CRUNCHYLISTS_LISTS_ENDPOINT.format(self.account_data.account_id)
        params = { 'locale': self.account.subtitle }
        req = self.make_request(method = 'GET', url = url, params = params)

        # check for error
        if not req or 'error' in req:
            return False

        return self.get_listables_from_response(req.get('data'))

    def search_items_by_crunchylist(self):
        """ Retrieve all items for a crunchylist """

        utils.crunchy_log(self.account, "Fetching crunchylist: %s" % self.account.crunchylist_item_id)
        url = self.CRUNCHYLISTS_VIEW_ENDPOINT.format(self.account_data.account_id, self.account.crunchylist_item_id)
        params = { 'locale': self.account.subtitle }

        req = self.make_request(method='GET', url = url, params = params)

        return self.get_listables_from_response(req.get('data'))


    # @todo we could change the return type and along with the listables return additional data that we preload
    #       like info what is on watchlist, artwork, playhead, ...
    #       for that we should use async requests (asyncio)
    def get_listables_from_response(self, data: Dict) -> List[ListableItem]:
        """ takes an API response object, determines type of its contents and creates DTOs for further processing """

        listable_items = []

        for item in data:

            if 'panel' in item.keys():
                if item['panel']['type'] == 'episode':
                    listable_items.append(EpisodeData(item['panel']))
            elif item['__class__'] == 'series':
                listable_items.append(SeriesData(item))
            elif item['__class__'] == 'episode':
                listable_items.append(EpisodeData(item))
            elif item['__class__'] == 'season':
                listable_items.append(SeasonData(item))
            elif item['__class__'] == 'panel' and item['type'] == 'series':
                listable_items.append(SeriesData(item))
            elif item['__class__'] == 'panel' and item['type'] == 'episode':
                listable_items.append(EpisodeData(item))
            elif hasattr(item, 'panel'):
                if item['panel']['type'] == 'episode':
                    listable_items.append(EpisodeData(item))
            else:
                utils.crunchy_err(self.account, "unhandled index for metadata. %s"
                                  % (json.dumps(item, indent=4)))
                continue

        if listable_items.__len__():
            return listable_items
        else:
            return False

    def get_json_from_response(self, r: Response) -> Optional[Dict]:

        code: int = r.status_code
        response_type: str = r.headers.get("Content-Type")

        # no content - possibly POST/DELETE request?
        if not r or not r.text:
            try:
                r.raise_for_status()
                return None
            except HTTPError as e:
                # r.text is empty when status code cause raise
                r = e.response

        # handle text/plain response (e.g. fetch subtitle)
        if response_type == "text/plain":
            # if encoding is not provided in the response, Requests will make an educated guess and very likely fail
            # messing encoding up - which did cost me hours. We will always receive utf-8 from crunchy, so enforce that
            r.encoding = "utf-8"
            d = dict()
            d.update({
                'data': r.text
            })
            return d

        if not r.ok and r.text[0] != "{":
            raise CrunchyrollError(f"[{code}] {r.text}")

        try:
            r_json: Dict = r.json()
        except requests.exceptions.JSONDecodeError:
            utils.crunchy_err(self.account, "Failed to parse response data")
            return None

        if "error" in r_json:
            error_code = r_json.get("error")
            if error_code == "invalid_grant":
                raise LoginError(f"[{code}] Invalid login credentials.")
        elif "message" in r_json and "code" in r_json:
            message = r_json.get("message")
            raise CrunchyrollError(f"[{code}] Error occurred: {message}")
        if not r.ok:
            raise CrunchyrollError(f"[{code}] {r.text}")

        return r_json

    def get_series_data_from_series_ids(self, ids: list) -> dict:
        """ fetch info from api object endpoint for given ids. Useful to complement missing data """

        req = self.make_request(
            method="GET",
            url=api.OBJECTS_BY_ID_LIST_ENDPOINT.format(','.join(ids)),
            params={
                "locale": self.account.subtitle,
                # "preferred_audio_language": ""
            }
        )
        if not req or "error" in req:
            return {}

        return {item.get("id"): item for item in req.get("data")}

    def get_playheads_from_content_ids(self, episode_ids: Union[str, list]) -> Dict:
        """ Retrieve playhead data from API for given episode / movie ids """

        if isinstance(episode_ids, str):
            episode_ids = [episode_ids]

        response = self.make_request(
            method='GET',
            url=self.PLAYHEADS_ENDPOINT.format(self.account_data.account_id),
            params={
                'locale': self.account.subtitle,
                'content_ids': ','.join(episode_ids)
            }
        )

        out = {}

        if not response:
            return out

        # prepare by id
        for item in response.get('data'):
            out[item.get('content_id')] = {
                'playhead': item.get('playhead'),
                'fully_watched': item.get('fully_watched')
            }

        return out

    def get_queue_from_content_ids(self, ids: list) -> list:
        """ retrieve watchlist status for given media ids """

        req = self.make_request(
            method="GET",
            url=self.WATCHLIST_V2_ENDPOINT.format(self.account_data.account_id),
            params={
                "content_ids": ','.join(ids),
                "locale": self.account.subtitle
            }
        )

        return [item.get('id') for item in req.get('data')]

    def get_continue_watching(self) -> list:
        """ retrieve watchlist status for given media ids """

        req = self.make_request(
            method="GET",
            url=self.CONTINUEWATCHING_ENDPOINT.format(self.account_data.account_id),
            params={
                "n":  1024,
                "locale": self.account.subtitle
            }
        )

        return self.get_listables_from_response(req.get('items'))

    def check_arg(self, argv):
        """Run mode-specific functions
            series -> episodes
            list categories
            search item by categories
            list seasons
            get anime/season
            get search/type 
            get episodes/season
            get history
            get playlist
            get crunchylists

        """
        if argv.category_filter is not None:
            filter_categories = self.list_categories()
            if argv.category_filter in filter_categories:
                # return Series
                return self.search_items_by_category(argv.category_filter)
            else:
                return filter_categories

        if argv.season_filter is not None:
            filter_season = self.list_seasons()     # return [winter|fall|summer|spring]-YYYY
            if argv.season_filter in filter_season:
                # return series
                return self.search_items_by_season(argv.season_filter)
            else:
                return filter_season
            
        if argv.season_id is not None or \
            argv.id is not None and argv.search_type == "season":
            # episode
            return self.search_item_by_season_id(argv.season_id)

        # return 1 Serie
        if argv.id is not None and argv.search_type == 'series':
            return self.search_season_by_series_id(argv.id)

        # return Series
        if argv.search is not None:
            return self.search_items_by_string(argv.search, argv.search_type)

        if argv.crunchylist_filter is not None:
            filter_crunchylists = self.list_crunchylists()
            if argv.crunchylist_filter in filter_crunchylists:
                return self.search_items_by_crunchylist()
            else:
                utils.crunchy_info(self.account, "list crunchylist filter %s" % str(filter_crunchylists))
                return filter_crunchylists

        # return Episode
        if argv.playlist:
            return self.get_playlist()

        if argv.queue:
            return self.get_queue_from_content_ids()

        # return Episode
        if argv.continue_watching:
            return self.get_continue_watching()

        # return Episode
        if argv.history:
            return self.list_item_by_history()

        utils.crunchy_err(self.account, "Missing arg defined")
        return None

    @staticmethod
    def get_argv():
        parser = argparse.ArgumentParser()
        parser.add_argument("--log_file", type=str, help="setting_file", required=False, default="crunchy.log")
        groupAPI = parser.add_argument_group('Using the Crunchyroll API',"")
        groupAPI.add_argument("--season_id", type=str, required=False)
        groupAPI.add_argument("--serie_id", type=str, required=False)
        groupAPI.add_argument("--search","-s", type=str, help="string search", required=False)
        groupAPI.add_argument("--search_type", type=str, help="search type", required=False, default="series")
        groupAPI.add_argument("--id", type=str, required=False)
        groupAPI.add_argument("--crunchylist_filter", help="list filter or filter by crunchylist", required=False, action='store', const="", nargs='?', type = str)
        groupAPI.add_argument("--category_filter", help="list filter or filter by category", required=False, action='store', const="", nargs='?', type = str)
        groupAPI.add_argument("--season_filter", help="list filter or filter by saison", required=False, action='store', const="", nargs='?', type = str)
        groupAPI.add_argument("--history", help="history", required=False, action='store_true')
        groupAPI.add_argument("--playlist", help="playlist", required=False, action='store_true')
        groupAPI.add_argument("--queue", help="queue", required=False, action='store_true')
        groupAPI.add_argument("--continue_watching", help="continue continue_watching endpoint", required=False, action='store_true')
        groupAPI.add_argument("--field","-f", help="list filter or filter by crunchylist", required=False, action='store', const="", nargs='?', type = str)

        groupLogin = parser.add_argument_group('Account settings management',"")
        groupLogin.add_argument("-u", "--username", type=str, help="username", required=False)
        groupLogin.add_argument("-p", "--password", type=str, help="password", required=False)
        groupLogin.add_argument("--profile_path", type=str, help="profile_path", required=False, default="./")
        groupLogin.add_argument("--setting_file", type=str, help="setting_file", required=False, default="settings.json")
        groupLogin.add_argument("--subtitle", type=str, help="""
        en-US, en-GB , es-419, es-ES, pt-BR, pt-PT, fr-FR, de-DE, ar-ME, it-IT, ru-RU, en-US
        """, required=False)
        groupLogin.add_argument("--subtitle-fallback", type=str, help="""
        en-US, en-GB , es-419, es-ES, pt-BR, pt-PT, fr-FR, de-DE, ar-ME, it-IT, ru-RU, en-US
        """, required=False)

        return parser.parse_args()
    
def filter_seasons(crunchyroll_settings: CrunchyrollSettings, item: Dict) -> bool:
    """ takes an API info struct and returns if it matches user language settings """

    # is it a dub in my main language?
    if crunchyroll_settings.subtitle == item.get('audio_locale', ""):
        return True

    # is it a dub in my alternate language?
    if crunchyroll_settings.subtitle_fallback and crunchyroll_settings.subtitle_fallback == item.get('audio_locale', ""):
        return True

    # is it japanese audio, but there are subtitles in my main language?
    if item.get("audio_locale") == "ja-JP":
        # fix for missing subtitles in data
        if item.get("subtitle_locales", []) == [] and item.get('is_subbed', False) is True:
            return True

        if crunchyroll_settings.subtitle in item.get("subtitle_locales", []):
            return True

        if crunchyroll_settings.subtitle_fallback and crunchyroll_settings.subtitle_fallback in item.get("subtitle_locales", []):
            return True

    return False

def debug(crunchyroll_settings, _list, argv):
    text = ""
    for item in _list:
        if issubclass(type(item), ListableItem):
            if argv.field is not None and not argv.field.__len__():
                utils.crunchy_info(crunchyroll_settings, "list available keys : " + str(item.get_keys()))
                exit(0)
            _text = item.get_info(argv.field)
            if _text:
                text+="\n" + str(_text)
            else:
                utils.crunchy_err(crunchyroll_settings, "list available keys : " + str(item.get_keys()))
                exit(15)
        elif type(item) is str:
            text+=item + '\n'

    utils.crunchy_info(crunchyroll_settings, text)




if __name__ == "__main__":
    import utils
    from crunchyrollentity import *

    argv = CrunchyrollAPI.get_argv()

    """ Main function for the settings """
    account = CrunchyrollSettingsArgs(argv)

    if not (account.crunchyroll_username and account.crunchyroll_password):
        # open settings settings
        utils.crunchy_err(account, "Missing username/password")
        exit(1)

    # login
    api = CrunchyrollAPI(account=account)

    if not api.start():
        utils.crunchy_err(account, "Login failed")
        exit(2)

    utils.crunchy_info(account, "Login successful")

    _list = api.check_arg(argv)

    if _list is None:
        utils.crunchy_dump(account, argv.__dict__)
        exit(3)
    
    debug(account, _list, argv)