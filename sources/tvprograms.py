import requests
from bs4 import BeautifulSoup
from datetime import datetime
import config

URL = config.URL_PROGRAMS

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

class TVProgramms:

    def _fetch_soup(self, day):
        r = requests.get(
            URL + day,
            headers=HEADERS,
            timeout=30
        )
        r.raise_for_status()
        return BeautifulSoup(r.text, "lxml")

    def _extract_films(self, soup):
        films = []
        selected = soup.find("a", class_="date-selector-button selected")
        if selected:
            day = selected.find("div", class_="date-day").get_text(strip=True)
            number = selected.find("div", class_="date-number").get_text(strip=True)
        else:
            weekdays = config.ITA_W_DAYS
            day = weekdays[datetime.now().weekday()]
            number = str(datetime.now().day)
        
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
        for d in config.URL_DAYS:
            soup = self._fetch_soup(d)
            for title, time, day, number, channel in self._extract_films(soup):
                films.append([day, number, time, title, channel])
        return films