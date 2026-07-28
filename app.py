import json
import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="CineDiscovery", page_icon="🎬", layout="wide")

st.title("🎬 CineDiscovery")
st.markdown(
    "Discover the films airing on TV this week and instantly check "
    "where you can stream, buy, or rent them."
)
st.divider()

DATA_FILE = Path(__file__).parent / "data" / "films.json"

COLS = ["Date", "Time", "Channel", "Title", "Streaming", "Purchase", "Rent", "Availability"]
VISIBLE_COLS = ["Date", "Time", "Channel", "Title", "Availability"]
COLUMN_CONFIG = {c: st.column_config.TextColumn(c) for c in VISIBLE_COLS}


@st.cache_data(show_spinner="Loading film data...", ttl=3600)
def load_data():
    if not DATA_FILE.exists():
        return pd.DataFrame(columns=COLS), None
    with DATA_FILE.open(encoding="utf-8") as f:
        data = json.load(f)
    rows = []
    for film in data.get("films", []):
        streaming = film.get("streaming") or []
        purchase = film.get("purchase") or []
        rent = film.get("rent") or []
        rows.append([
            film["date"],
            film["time"],
            film["channel"],
            film["title"],
            ", ".join(streaming) if streaming else "-",
            ", ".join(purchase) if purchase else "-",
            ", ".join(rent) if rent else "-",
            film.get("availability", ""),
        ])
    return pd.DataFrame(rows, columns=COLS), data.get("generated_at")


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


# ── Load data ────────────────────────────────────────────────────────────────
df, generated_at = load_data()

if df.empty:
    st.warning("No data available yet. The scheduled scraper has not run yet.")
    st.stop()

if generated_at:
    st.caption(f"Data updated: {generated_at[:16].replace('T', ' ')} UTC")

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
    avail_opts = ["All"] + sorted(df["Availability"].dropna().unique().tolist())
    selected_availability = st.selectbox("Availability", avail_opts)

# ── Table ────────────────────────────────────────────────────────────────────
filtered = _apply_filters(df, search_title, selected_channel, selected_day, selected_availability)
st.markdown(f"**{len(filtered)} films**")
event = st.dataframe(
    filtered[VISIBLE_COLS],
    hide_index=True,
    column_config=COLUMN_CONFIG,
    on_select="rerun",
    selection_mode="single-row",
    key="main_table",
)
selected_rows = event.selection.rows
if selected_rows and selected_rows[0] < len(filtered):
    row = filtered.iloc[selected_rows[0]]
    new_key = (row["Title"], row["Date"], row["Time"])
    if new_key != st.session_state.dialog_row_key:
        st.session_state.dialog_row_key = new_key
        _show_film_details(row)
else:
    st.session_state.dialog_row_key = None

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
