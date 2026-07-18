from sources.tvprograms import TVProgramms
from sources.tmdb import TMDB
from tabulate import tabulate
import csv

tv = TVProgramms()
tmdb = TMDB()

films = tv.get_all_films()

rows = []
for day, number, time, title, channel in films:
    streaming, purchase, rent = tmdb.get_providers(title)
    if streaming is None and purchase is None and rent is None:
        s, b, r = "Not found on TMDB", "-", "-"
        availability = "Not found on TMDB"
    else:
        s = ", ".join(streaming) if streaming else "-"
        b = ", ".join(purchase) if purchase else "-"
        r = ", ".join(rent) if rent else "-"
        total = len(set((streaming or []) + (purchase or []) + (rent or [])))
        if not streaming and not purchase and not rent:
            availability = "Only on TV"
        elif streaming:
            availability = f"Available on {total} platform{'s' if total != 1 else ''}"
        else:
            availability = "Pay only"
    rows.append([f"{day} {number}", time, channel, title, s, b, r, availability])
headers = ["Date", "Time", "Channel", "Title", "Streaming", "Purchase", "Rent", "Availability"]
print(tabulate(rows, headers=headers, tablefmt="grid"))

with open("results.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(headers)
    writer.writerows(rows)