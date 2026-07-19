from datetime import datetime
import config

class CINEUtils:

    @staticmethod
    def parse_ita_date(s):
        day, month_str, year = s.split()
        return datetime(int(year), config.MONTHS[month_str.lower()], int(day))