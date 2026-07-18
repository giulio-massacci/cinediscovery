import streamlit as st
import pandas as pd
import db
from sources.tvprograms import TVProgramms
from sources.tmdb import TMDB

st.set_page_config(page_title="CineDiscovery", page_icon="🎬", layout="wide")

st.title("🎬 CineDiscovery")
st.markdown(
    "Discover the films airing on TV this week and instantly check "
    "where you can stream, buy, or rent them."
)
st.divider()

db.init()

COLS = ["Date", "Time", "Channel", "Title", "Streaming", "Purchase", "Rent", "Availability"]
VISIBLE_COLS = ["Date", "Time", "Channel", "Title", "Availability"]
COLUMN_CONFIG = {c: st.column_config.TextColumn(c) for c in VISIBLE_COLS}


@st.cache_data(show_spinner="Fetching TV schedule...", ttl=3600)
def get_tv_schedule():
    return TVProgramms().get_all_films()


def _make_row(day, number, time, title, channel, cached):
    date_str = f"{day} {number}"
    if cached is None:
        return [date_str, time, channel, title, "⏳", "⏳", "⏳", "⏳ Fetching..."]
    streaming, purchase, rent = cached
    if streaming is None and purchase is None and rent is None:
        return [date_str, time, channel, title, "Not found on TMDB", "-", "-", "⚪Not found on TMDB"]
    s = ", ".join(streaming) if streaming else "-"
    b = ", ".join(purchase) if purchase else "-"
    r = ", ".join(rent) if rent else "-"
    total = len(set((streaming or []) + (purchase or []) + (rent or [])))
    if not streaming and not purchase and not rent:
        availability = "🟢Only on TV"
    elif streaming:
        availability = "🟠Available on platforms"
    else:
        availability = "🔵Pay only"
    return [date_str, time, channel, title, s, b, r, availability]


def _apply_filters(dataframe, search_title, sel_channel, sel_day, sel_availability):
    f = dataframe.copy()
    if search_title:
        f = f[f["Title"].str.contains(search_title, case=False, na=False)]
    if sel_channel != "All":
        f = f[f["Channel"] == sel_channel]
    if sel_day != "All":
        f = f[f["Date"] == sel_day]
    if sel_availability != "All":
        f = f[f["Availability"] == sel_availability]
    return f


@st.dialog("📽️ Streaming & Availability Details")
def _show_film_details(row):
    st.subheader(row["Title"])
    st.caption(f"{row['Date']} · {row['Time']} · {row['Channel']}")
    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**🎬 Streaming**")
        st.write(row["Streaming"])
    with col2:
        st.markdown("**🛒 Purchase**")
        st.write(row["Purchase"])
    with col3:
        st.markdown("**🏷️ Rent**")
        st.write(row["Rent"])


# ── Load TV schedule + cache ────────────────────────────────────────────────
films = get_tv_schedule()
cache = db.get_all()

rows = [
    _make_row(day, number, time, title, channel, cache.get(title.lower()))
    for day, number, time, title, channel in films
]
df = pd.DataFrame(rows, columns=COLS)

uncached = [
    (i, day, number, time, title, channel)
    for i, (day, number, time, title, channel) in enumerate(films)
    if title.lower() not in cache
]

if "dialog_row_key" not in st.session_state:
    st.session_state.dialog_row_key = None

# ── Filters ─────────────────────────────────────────────────────────────────
st.subheader("Filters")
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
with col1:
    search_title = st.text_input("Title", placeholder="Search by title...")
with col2:
    channels = ["All"] + sorted(df["Channel"].dropna().unique().tolist())
    selected_channel = st.selectbox("Channel", channels)
with col3:
    days_opts = ["All"] + df["Date"].unique().tolist()
    selected_day = st.selectbox("Date", days_opts)
with col4:
    avail_opts = ["All"] + sorted(
        df[~df["Availability"].str.startswith("⏳")]["Availability"].dropna().unique().tolist()
    )
    selected_availability = st.selectbox("Availability", avail_opts)

# ── Table (live-updating placeholders) ──────────────────────────────────────
count_ph = st.empty()
table_ph = st.empty()

def _render(dataframe):
    filtered = _apply_filters(dataframe, search_title, selected_channel, selected_day, selected_availability)
    count_ph.markdown(f"**{len(filtered)} films**")
    event = table_ph.dataframe(
        filtered[VISIBLE_COLS],
        hide_index=True,
        column_config=COLUMN_CONFIG,
        on_select="rerun",
        selection_mode="single-row",
        key="main_table",
    )
    selected = event.selection.rows
    if selected and selected[0] < len(filtered):
        row = filtered.iloc[selected[0]]
        new_key = (row["Title"], row["Date"], row["Time"])
        if new_key != st.session_state.dialog_row_key:
            st.session_state.dialog_row_key = new_key
            _show_film_details(row)
    else:
        st.session_state.dialog_row_key = None


_render(df)

# ── Background fetch for uncached titles ────────────────────────────────────
if uncached:
    tmdb = TMDB()
    progress = st.progress(0, f"Fetching {len(uncached)} films from TMDB...")
    for step, (i, day, number, time, title, channel) in enumerate(uncached):
        streaming, purchase, rent = tmdb.get_providers(title)
        db.save(title, streaming, purchase, rent)
        rows[i] = _make_row(day, number, time, title, channel, (streaming, purchase, rent))
        df = pd.DataFrame(rows, columns=COLS)
        _render(df)
        progress.progress((step + 1) / len(uncached))
    progress.empty()

# ── About / Credits ──────────────────────────────────────────────────────────
st.divider()
col_logo, col_text = st.columns([1, 6])
with col_logo:
    st.image(
        "https://www.themoviedb.org/assets/2/v4/logos/v2/blue_short-8e7b30f73a4020692ccca9c88bafe5dcb6f8a62a4c6bc55cd9ba82bb2cd95f6c.svg",
        width=120,
    )
with col_text:
    st.caption(
        "This product uses the TMDB API but is not endorsed or certified by TMDB."
    )
