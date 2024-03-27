def test_crunchyrollapi_login_failed():
    print(__name__)

    from CrunchyrollAPI import SettingsData, CrunchyrollSettingsClass, CrunchyrollAPI, LoginError
    import pytest
    SC = SettingsData({
    "setting_file": "settings.json",
    "profile_path": "./",
    "crunchyroll_username": "",
    "crunchyroll_password": "",
    "device_id": "dysqe0t1-gene-q716-13j9-fq575bh0d6vw",
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

def test_crunchyrollapi():
    print(__name__)

    from CrunchyrollAPI import SettingsData, CrunchyrollSettingsClass, CrunchyrollAPI, ListableItem
    import os

    SC = SettingsData({
    "setting_file": "settings.json",
    "profile_path": "./",
    "crunchyroll_username": os.environ.get('cu'),
    "crunchyroll_password": os.environ.get('cp'),
    "device_id": "dysqe0t1-gene-q716-13j9-fq575bh0d6vw",
    "subtitle": "en-US",
    "subtitle_fallback": "en-US",
    "log_file": "crunchy.log",
    })

    find="fall-2015"
    field = None

    _SC = CrunchyrollSettingsClass(SC)

    API = CrunchyrollAPI (_SC)
    assert API.start(), "Attendu Api.start()"
    if API.start():
        _list = API.list_seasons()
        assert type(_list) is list, "Attendu type list_seasons is list"

    text=""
    for item in _list:
        if issubclass(type(item), ListableItem):
            if field is not None and not field.__len__():
                print("list available keys : " + str(item.get_keys()))
            _text = item.get_info()
            if _text:
                text+="\n" + str(_text)
            else:
                print("list available keys : " + str(item.get_keys()))
        elif type(item) is str:
            text+=item + '\n'

    print(text)