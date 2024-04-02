# module Crunchyroll API

Git repo : https://github.com/jbsky/crunchyroll-api

All information is https://github.com/hyugogirubato/API-Crunchyroll-Beta/wiki

**WARNING: You MUST be a PREMIUM member to use this module!**
***

### Start
To give you an idea, it's possible to control this module with arguments.
```
python3 src/CrunchyrollAPI/crunchyrollapi.py -h
```
Identifiers are only mandatory for the 1st order, after which they are stored as JSON files.
```
python3 src/CrunchyrollAPI/crunchyrollapi.py -u USENAME -p PASSWORD --subtitle SUBTITLE --subtitle-fallback SUBTITLE_FALLBACK
```

### This is what the API does
* Everything is automatically tested by pytest.

- [x] Login with your account
- [x] Return list of seasons tag (format list str)
- [x] Return list of seasons tag (format list item)
- [x] Return list of categories (format list str)
- [x] Return list of categories (format list item)
- [x] Return episode for one season
- [x] Search for series by string
- [x] Search for episode by string
- [x] Return episodes by season id
- [x] Return seasons by series id


***