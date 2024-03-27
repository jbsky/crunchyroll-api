# -*- coding: utf-8 -*-
# Crunchyroll
# Copyright (C) 2018 MrKrabat
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
import logging, time
from json import dumps
from datetime import datetime

def crunchy_dump(crunchyroll_settings, data) -> None:
    crunchy_err(crunchyroll_settings, dumps(data, indent=4))

def crunchy_log(crunchyroll_settings, message, loglevel=logging.INFO, filename = 'crunchy.log') -> None:
    addon_name = crunchyroll_settings.addon_name if crunchyroll_settings is not None and hasattr(crunchyroll_settings, 'addon_name') else "Crunchyroll"
    text= "%s: %s" % (addon_name, str(message))

    logger = logging.getLogger(__name__)
    logging.basicConfig(level=loglevel, encoding='utf-8',
                       format="%(asctime)s [%(levelname)s] %(message)s",
                       handlers=[ logging.FileHandler(filename), logging.StreamHandler()])

    if loglevel ==  logging.DEBUG:
            logger.debug(text)
    if loglevel ==  logging.INFO:
            logger.info(text)
    if loglevel ==  logging.WARNING:
            logger.warning(text)
    if loglevel ==  logging.ERROR:
            logger.error(text)

def crunchy_info(crunchyroll_settings, message, filename = 'crunchy.log') -> None:
    crunchy_log(crunchyroll_settings, message, loglevel=logging.INFO, filename = filename)

def crunchy_debug(crunchyroll_settings, message, filename = 'crunchy.log') -> None:
    crunchy_log(crunchyroll_settings, message, loglevel=logging.DEBUG, filename = filename)

def crunchy_warn(crunchyroll_settings, message, filename = 'crunchy.log') -> None:
    crunchy_log(crunchyroll_settings, message, loglevel=logging.WARN, filename = filename)

def crunchy_err(crunchyroll_settings, message, filename = 'crunchy.log') -> None:
    crunchy_log(crunchyroll_settings, message, loglevel=logging.ERROR, filename = filename)


def date_to_str(date: datetime) -> str:
    return "{}-{}-{}T{}:{}:{}Z".format(
        date.year, date.month,
        date.day, date.hour,
        date.minute, date.second
    )

def str_to_date(string: str) -> datetime:
    time_format = "%Y-%m-%dT%H:%M:%SZ"

    try:
        res = datetime.strptime(string, time_format)
    except TypeError:
        res = datetime(*(time.strptime(string, time_format)[0:6]))

    return res