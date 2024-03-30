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
from abc import abstractmethod
from typing import Dict, Union
from json import dumps


print (__name__)

if __name__ == "crunchyrollentity":
    from utils import *

if __name__ == "CrunchyrollAPI.crunchyrollentity":
    from .utils import *

class Meta(type, metaclass=type("", (type,), {"__str__": lambda _: "~hi"})):
    def __str__(self):
        return f"<class 'crunchyroll_beta.types.{self.__name__}'>"

class Object(metaclass=Meta):
    @staticmethod
    def default(obj: "Object"):
        return {
            "_": obj.__class__.__name__,
            **{
                attr: (
                    getattr(obj, attr)
                )
                for attr in filter(lambda x: not x.startswith("_"), obj.__dict__)
                if getattr(obj, attr) is not None
            }
        }

    def __str__(self) -> str:
        return dumps(self, indent=4, default=Object.default, ensure_ascii=False)

class CMS(Object):
    def __init__(self, data: dict):
        self.bucket: str = data.get("bucket")
        self.policy: str = data.get("policy")
        self.signature: str = data.get("signature")
        self.key_pair_id: str = data.get("key_pair_id")

class SettingsData(Object):
    def __init__(self, data: dict):
        self.setting_file = data.get("setting_file")
        self.profile_path = data.get("profile_path")
        self.crunchyroll_username = data.get("crunchyroll_username")
        self.crunchyroll_password = data.get("crunchyroll_password")
        self.device_id = data.get("device_id")
        self.subtitle = data.get("subtitle")
        self.subtitle_fallback = data.get("subtitle_fallback")
        self.log_file = data.get("log_file")

class AccountData(Object):
    def __init__(self, data: dict):
        self.access_token: str = data.get("access_token")
        self.refresh_token: str = data.get("refresh_token")
        self.expires: str = data.get("expires")
        self.token_type: str = data.get("token_type")
        self.scope: str = data.get("scope")
        self.country: str = data.get("country")
        self.account_id: str = data.get("account_id")
        self.cms: CMS = CMS(data.get("cms", {}))
        self.service_available: bool = data.get("service_available")
        self.avatar: str = data.get("avatar")
        self.has_beta: bool = data.get("cr_beta_opt_in")
        self.email_verified: bool = data.get("crleg_email_verified")
        self.email: str = data.get("email")
        self.maturity_rating: str = data.get("maturity_rating")
        self.account_language: str = data.get("preferred_communication_language")
        self.default_subtitles_language: str = data.get("preferred_content_subtitle_language")
        self.default_audio_language: str = data.get("preferred_content_audio_language")
        self.username: str = data.get("username")

class ListableItem(Object):
    """ Base object for all DataObjects below that can be displayed in a Kodi List View """

    def __init__(self):
        super().__init__()
        # just a very few that all child classes have in common, so I can spare myself of using hasattr() and getattr()
        self.id: str | None = None
        self.title: str | None = None
        self.thumb: str | None = None
        self.fanart: str | None = None
        self.poster: str | None = None
        self.banner: str | None = None

    # @abstractmethod
    def get_info(self, field) -> Dict:
        """ return a dict with info to set on the kodi ListItem (filtered) and access some data """
        import json

        if field:
            list_field = list(field.split(","))
        else:
            list_field = list()

        if not list_field.__len__():
            return json.dumps(self.__dict__)

        data = {}
        for key in list_field:
            if key in self.__dict__.keys():
                data[key] = self.__dict__[key]
            else:
                utils.crunchy_err(None, "key %s does not exit"%(key))
                return False
        
        return data
    
    def get_keys(self) -> Dict:
        """ return a keys for help"""
        return str(list(self.__dict__.keys()))

    @abstractmethod
    def to_item(self) -> Dict:
        """ Convert ourselves if needed to items"""
        pass

    @abstractmethod
    def update_playcount_from_playhead(self, playhead_data: Dict):
        pass

class SeriesData(ListableItem):
    """ A Series containing Seasons containing Episodes """

    def __init__(self, data: dict):
        super().__init__()

        panel = data.get('panel') or data
        meta = panel.get("series_metadata") or panel

        self.id = panel.get("id")
        self.title: str = panel.get("title")
        self.series_title: str = panel.get("title")
        self.series_id: str | None = panel.get("id")
        self.season_id: str | None = None
        self.plot: str = panel.get("description", "")
        self.plotoutline: str = panel.get("description", "")
        self.year: str = str(meta.get("series_launch_year")) + '-01-01'
        self.aired: str = str(meta.get("series_launch_year")) + '-01-01'
        self.premiered: str = str(meta.get("series_launch_year"))
        self.episode: int = meta.get('episode_count')
        self.season: int = meta.get('season_count')

        self.thumb: str | None = get_image_from_struct(panel, "poster_tall", 2)
        self.fanart: str | None = get_image_from_struct(panel, "poster_wide", 2)
        self.poster: str | None = get_image_from_struct(panel, "poster_tall", 2)
        self.banner: str | None = None
        self.playcount: int = 0

    def recalc_playcount(self):
        # @todo: not sure how to get that without checking all child seasons and their episodes
        pass

class CategoriesData(ListableItem):
    """ A Season/Arc of a Series containing Episodes """

    def __init__(self, data: dict):
        super().__init__()

        self.tenant_category = data.get("tenant_category")
        self.slug = data.get("slug")
        self.title = data["localization"]["title"]
        self.description = data["localization"]["description"]
        self.locale = data["localization"]["locale"]
        self.href = data.get("__href__")

class SeasonData(ListableItem):
    """ A Season/Arc of a Series containing Episodes """

    def __init__(self, data: dict):
        super().__init__()

        self.id = data.get("id")
        self.description: str = data.get("description")
        self.title: str = data.get("title")
        self.series_title: str = data.get("title")
        self.series_id: str | None = data.get("series_id")
        self.season_id: str | None = data.get("id")
        self.plot: str = data.get("description")  # does not have description. maybe object endpoint?
        self.plotoutline: str = ""
        self.year: str = ""
        self.aired: str = ""
        self.premiered: str = ""
        self.season: int = data.get('season_number')
        self.thumb: str | None = None
        self.fanart: str | None = None
        self.poster: str | None = None
        self.banner: str | None = None
        self.playcount: int = 1 if data.get('is_complete') == 'true' else 0

        self.recalc_playcount()

    def recalc_playcount(self):
        # @todo: not sure how to get that without checking all child episodes
        pass

def get_stream_id_from_item(item: Dict) -> Union[str, None]:
    """ takes a URL string and extracts the stream ID from it """
    import re
    pattern = '/videos/([^/]+)/streams'
    stream_id = re.search(pattern, item.get('__links__', {}).get('streams', {}).get('href', ''))
    # history data has the stream_id at a different location
    if not stream_id:
        stream_id = re.search(pattern, item.get('streams_link', ''))

    if not stream_id:
        raise CrunchyrollError('Failed to get stream id')

    return stream_id[1]

class EpisodeData(ListableItem):
    """ A single Episode of a Season of a Series """

    def __init__(self, data: dict):
        super().__init__()

        panel = data.get('panel') or data
        meta = panel.get("episode_metadata") or panel

        self.id = panel.get("id")
        self.long_title: str =  "%s #%s - %s" % (meta.get("season_title"), str( meta.get("episode_number")), panel.get("title"))
        self.episode_number: int = meta.get("episode_number")
        self.season_title: str = meta.get("season_title")
        self.title: str = meta.get("title")
        self.series_title: str = meta.get("series_title", "")
        self.duration: int = int(meta.get("duration_ms", 0) / 1000)
        self.playhead: int = data.get("playhead", 0)
        self.season: int = meta.get("season_number", 1)
        self.episode: int = meta.get("episode", 1)
        self.episode_id: str | None = panel.get("id")
        self.season_id: str | None = meta.get("season_id")
        self.series_id: str | None = meta.get("series_id")
        self.plot: str = panel.get("description", "")
        self.plotoutline: str = panel.get("description", "")
        self.year: str = meta.get("episode_air_date")[:4] if meta.get("episode_air_date") is not None else ""
        self.aired: str = meta.get("episode_air_date")[:10] if meta.get("episode_air_date") is not None else ""
        self.premiered: str = meta.get("episode_air_date")[:10] if meta.get("episode_air_date") is not None else ""
        self.thumb: str | None = get_image_from_struct(panel, "thumbnail", 2)
        self.fanart: str | None = get_image_from_struct(panel, "thumbnail", 2)
        self.poster: str | None = None
        self.banner: str | None = None
        self.playcount: int = 0
        self.stream_id: str | None = get_stream_id_from_item(panel)

        # self.recalc_playcount()

    def recalc_playcount(self):
        if self.playhead is not None and self.duration is not None:
            self.playcount = 1 if (int(self.playhead / self.duration * 100)) > 90 else 0

class CrunchyrollError(Exception):
    pass

class LoginError(Exception):
    pass
from typing import Dict, Union

def get_image_from_struct(item: Dict, image_type: str, depth: int = 2) -> Union[str, None]:
    """ dive into API info structure and extract requested image from its struct """

    # @todo: add option to specify quality / max size
    if item.get("images") and item.get("images").get(image_type):
        src = item.get("images").get(image_type)
        for i in range(0, depth):
            if src[-1]:
                src = src[-1]
            else:
                return None
        if src.get('source'):
            return src.get('source')

    return None