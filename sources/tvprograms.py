import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from dateutil import relativedelta
import config
import re
from sources.utils import CINEUtils

URL = config.URL_PROGRAMS

HEADERS = {
    "User-Agent": "CineDiscovery-bot/1.0 (educational project; github.com/giulio-massacci/cinediscovery)"
}

class TVProgramms:

    def _fetch_soup(self, day, retries=3, backoff=2):
        for attempt in range(retries):
            try:
                r = requests.get(
                    URL + day,
                    headers=HEADERS,
                    timeout=30
                )
                r.raise_for_status()
                return BeautifulSoup(r.text, "lxml")
            except (requests.ConnectionError, requests.Timeout, requests.exceptions.SSLError) as e:
                if attempt < retries - 1:
                    time.sleep(backoff ** attempt)
                else:
                    raise

    def _extract_films(self, soup, d):
        films = []
        weekdays = config.ITA_W_DAYS
        page_title = soup.find("h1", class_="page-title").get_text(strip=True)
        if d in ["stasera"] or "domani" in page_title:
            day = weekdays[datetime.now().weekday() if d=="stasera" else (datetime.now() + timedelta(days=1)).weekday()]
            number = str(datetime.now().day) if d=="stasera" else str((datetime.now() + timedelta(days=1)).day)
        else:
            date_string = re.search(r'\d.*', page_title).group()
            date = CINEUtils().parse_ita_date(date_string)
            day = weekdays[date.weekday()]
            number = str(date.day)
 
        #selected = soup.find("a", class_="date-selector-button selected")
        #if selected:
        #    day = selected.find("div", class_="date-day").get_text(strip=True)
        #    number = selected.find("div", class_="date-number").get_text(strip=True)
        #else:
        #    weekdays = config.ITA_W_DAYS
        #    day = weekdays[datetime.now().weekday()]
        #    number = str(datetime.now().day)
        
        channels = soup.find_all("div", class_="channel-box")
        for channel_box in channels:
            channel_info = channel_box.find("div", class_="channel-header-info")
            titles = channel_box.find_all("h3", class_="channel-box-program-title")
            times = channel_box.find_all("div", class_="channel-box-program-time")
        
            for title_el, time_el in zip(titles, times):
                title = title_el.get_text(strip=True)
                time = time_el.get_text(strip=True)
                channel = channel_info.find("h2").get_text(strip=True)
                if title:
                    films.append((title, time, day, number, channel))
        return films

    def get_all_films(self):
        films = []
        today = datetime.now()
        end_of_month = today + relativedelta.relativedelta(months=1, day=1) - relativedelta.relativedelta(days=1)
        for d in config.URL_DAYS:
            soup = self._fetch_soup(d)
            for title, airtime, day, number, channel in self._extract_films(soup, d):
                day_order = int(number)-today.day if int(number)-today.day>=0 else end_of_month.day+int(number)-today.day
                films.append([day_order, day, number, airtime, title, channel])
            time.sleep(1)  # polite delay between pages
        films.sort()
        return [f[1:] for f in films]