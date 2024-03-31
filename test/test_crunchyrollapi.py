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

from CrunchyrollAPI import SettingsData, CrunchyrollSettingsClass, CrunchyrollAPI, ListableItem, SeriesData, EpisodeData
import os

def get_config():
    return SettingsData({
    "setting_file": "settings.json",
    "profile_path": "./",
    "crunchyroll_username": os.environ.get('cu'),
    "crunchyroll_password": os.environ.get('cp'),
    "device_id": "dysqe0t1-gene-q716-13j9-fq575bh0d6vw",
    "subtitle": "en-US",
    "subtitle_fallback": "en-US",
    "log_file": "crunchy.log",
    })

def test_exported_env():
    assert type(os.environ.get('cu')) is str
    assert type(os.environ.get('cp')) is str
    assert os.environ.get('cu') != ""
    assert os.environ.get('cp') != ""

def test_history():
    argv = lambda: None
    argv.history = True
    argv.category_filter = False
    """ Main function for the settings """
    account = CrunchyrollSettingsClass(get_config())
    argv = CrunchyrollAPI.get_argv()
    argv.history = True

    # login
    API = CrunchyrollAPI(account=account)
    assert API.start(), "Attendu Api.start()"
    _list = API.check_arg(argv)
    assert type(_list) is list, "Attendu type list_seasons is list"
    assert len(_list) > 0
    for item in _list:
        assert issubclass(type(item), ListableItem)
        assert type(item) is EpisodeData

def test_continue_watching():
    argv = lambda: None
    argv.history = True
    argv.category_filter = False
    """ Main function for the settings """
    account = CrunchyrollSettingsClass(get_config())
    argv = CrunchyrollAPI.get_argv()
    argv.continue_watching = True

    # login
    API = CrunchyrollAPI(account=account)
    assert API.start(), "Attendu Api.start()"
    _list = API.check_arg(argv)
    assert type(_list) is list, "Attendu type list_seasons is list"
    assert len(_list) > 0
    for item in _list:
        assert issubclass(type(item), ListableItem)
        assert type(item) is EpisodeData

def test_playlist():
    argv = lambda: None
    argv.history = True
    argv.category_filter = False
    """ Main function for the settings """
    account = CrunchyrollSettingsClass(get_config())
    argv = CrunchyrollAPI.get_argv()
    argv.playlist = True

    # login
    API = CrunchyrollAPI(account=account)
    assert API.start(), "Attendu Api.start()"
    _list = API.check_arg(argv)
    assert type(_list) is list, "Attendu type list_seasons is list"
    assert len(_list) > 0
    for item in _list:
        assert issubclass(type(item), ListableItem)
        assert type(item) is EpisodeData

def test_search_one_serie():
    argv = lambda: None
    argv.history = True
    argv.category_filter = False
    """ Main function for the settings """
    account = CrunchyrollSettingsClass(get_config())
    argv = CrunchyrollAPI.get_argv()
    argv.search = 'one'
    argv.search_type = 'series'

    # login
    API = CrunchyrollAPI(account=account)
    assert API.start(), "Attendu Api.start()"
    _list = API.check_arg(argv)
    assert type(_list) is list, "Attendu type list_seasons is list"
    assert len(_list) > 0
    for item in _list:
        assert issubclass(type(item), ListableItem)
        assert type(item) is SeriesData

def test_search_one_episode():
    argv = lambda: None
    argv.history = True
    argv.category_filter = False
    """ Main function for the settings """
    account = CrunchyrollSettingsClass(get_config())
    argv = CrunchyrollAPI.get_argv()
    argv.search = 'one'
    argv.search_type = 'episode'

    # login
    API = CrunchyrollAPI(account=account)
    assert API.start(), "Attendu Api.start()"
    _list = API.check_arg(argv)
    assert type(_list) is list, "Attendu type list_seasons is list"
    assert len(_list) > 0
    for item in _list:
        assert issubclass(type(item), ListableItem)
        assert type(item) is EpisodeData


def test_crunchyrollapi_login_failed():
    print(__name__)

    from CrunchyrollAPI import SettingsData, CrunchyrollSettingsClass, CrunchyrollAPI, LoginError
    import pytest
    SC = SettingsData({
    "setting_file": "./raise/settings.json",
    "profile_path": "./raise/",
    "crunchyroll_username": "",
    "crunchyroll_password": "",
    "device_id": "",
    "subtitle": "en-US",
    "subtitle_fallback": "en-US",
    "log_file": "crunchy.log",
    })

    find="fall-2015"
    field = None

    _SC = CrunchyrollSettingsClass(SC)

    API = CrunchyrollAPI (_SC)

    with pytest.raises(LoginError):
        API.start()


def test_category_thriller():
    argv = lambda: None
    argv.history = True
    argv.category_filter = False
    """ Main function for the settings """
    account = CrunchyrollSettingsClass(get_config())
    argv = CrunchyrollAPI.get_argv()
    argv.category_filter = 'thriller'

    # login
    API = CrunchyrollAPI(account=account)
    assert API.start(), "Attendu Api.start()"
    _list = API.check_arg(argv)
    assert len(_list) > 0
    for item in _list:
        assert issubclass(type(item), ListableItem)
        assert type(item) is SeriesData
    
def test_list_season():
    print(__name__)

    SC = get_config()

    _SC = CrunchyrollSettingsClass(SC)

    API = CrunchyrollAPI (_SC)
    assert API.start(), "Attendu Api.start()"
    _list = API.list_seasons()
    assert type(_list) is list, "Attendu type list_seasons is list"
    assert len(_list) > 0


def test_list_categories():
    print(__name__)

    SC = get_config()

    _SC = CrunchyrollSettingsClass(SC)

    API = CrunchyrollAPI (_SC)
    assert API.start(), "Attendu Api.start()"
    _list = API.list_categories()
    assert type(_list) is list, "Attendu type list_categories is list"
    assert len(_list) > 0

def test_season_fall_2023():
    argv = lambda: None
    argv.history = True
    argv.category_filter = False
    """ Main function for the settings """
    account = CrunchyrollSettingsClass(get_config())
    argv = CrunchyrollAPI.get_argv()
    argv.season_filter = 'fall-2023'

    # login
    API = CrunchyrollAPI(account=account)
    assert API.start(), "Attendu Api.start()"
    _list = API.check_arg(argv)
    assert type(_list) is list
    assert len(_list) > 0
    for item in _list:
        assert issubclass(type(item), ListableItem)
        assert type(item) is SeriesData
