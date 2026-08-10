import json
import urllib.parse
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

st.set_page_config(page_title="CineDiscovery", page_icon="🎬", layout="wide")

st.title("🎬 CineDiscovery")
st.markdown(
    "A weekly guide to films on Italian TV, with streaming availability at a glance."
)
st.divider()

DATA_FILE = Path(__file__).parent / "data" / "films.json"

COLS = ["Date", "Time", "Channel", "Title", "Streaming", "Purchase", "Rent", "Availability", "Rating", "Director", "Details"]
VISIBLE_COLS = ["Title", "Director", "Time", "Channel", "Availability", "Rating", "Details"]
COLUMN_CONFIG = {
    **{c: st.column_config.TextColumn(c) for c in ["Time", "Channel", "Title", "Availability", "Director"]},
    "Rating": st.column_config.NumberColumn("Rating", format="⭐ %.1f", min_value=0, max_value=10),
    "Details": st.column_config.LinkColumn("Details", display_text="🔗 Link", width="small"),
}


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
            film.get("rating"),
            film.get("director") or "-",
            film.get("tmdb_url") or None,
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


def _parse_film_datetime(film_date: str, film_time: str, ref_iso: str) -> datetime | None:
    """Parse 'Mar 28' + '21:09' into a datetime using generated_at for month/year context."""
    try:
        ref = datetime.fromisoformat(ref_iso)
        day_num = int(film_date.split()[-1])
        month, year = ref.month, ref.year
        # If the film day is more than 7 days before the reference day, it belongs to the next month
        if day_num < ref.day - 7:
            month = month % 12 + 1
            if month == 1:
                year += 1
        return datetime(year, month, day_num, int(film_time[:2]), int(film_time[3:5]))
    except Exception:
        return None


def _google_calendar_url(row, ref_iso: str) -> str | None:
    dt = _parse_film_datetime(row["Date"], row["Time"], ref_iso)
    if dt is None:
        return None
    dt_end = dt + timedelta(hours=2)
    fmt = "%Y%m%dT%H%M%S"
    text = urllib.parse.quote(row["Title"])
    details_parts = [f"Canale: {row['Channel']}"]
    if row["Director"] not in ("-", ""):
        details_parts.append(f"Regia: {row['Director']}")
    if row["Availability"]:
        details_parts.append(row["Availability"])
    details = urllib.parse.quote("\n".join(details_parts))
    return (
        f"https://calendar.google.com/calendar/r/eventedit"
        f"?text={text}&dates={dt.strftime(fmt)}/{dt_end.strftime(fmt)}&details={details}"
    )


def _build_ics(row, ref_iso: str) -> str | None:
    dt = _parse_film_datetime(row["Date"], row["Time"], ref_iso)
    if dt is None:
        return None
    dt_end = dt + timedelta(hours=2)
    fmt = "%Y%m%dT%H%M%S"
    description = f"Canale: {row['Channel']}"
    if row["Director"] not in ("-", ""):
        description += f"\\nRegia: {row['Director']}"
    if row["Availability"]:
        description += f"\\n{row['Availability']}"
    return (
        "BEGIN:VCALENDAR\r\n"
        "VERSION:2.0\r\n"
        "PRODID:-//CineDiscovery//EN\r\n"
        "BEGIN:VEVENT\r\n"
        f"DTSTART:{dt.strftime(fmt)}\r\n"
        f"DTEND:{dt_end.strftime(fmt)}\r\n"
        f"SUMMARY:{row['Title']}\r\n"
        f"DESCRIPTION:{description}\r\n"
        "END:VEVENT\r\n"
        "END:VCALENDAR\r\n"
    )


@st.dialog("📽️ Streaming & Availability Details")
def _show_film_details(row, ref_iso: str | None = None):
    st.subheader(row["Title"])
    meta_parts = [f"{row['Date']} · {row['Time']} · {row['Channel']}"]
    if row["Director"] and row["Director"] != "-":
        meta_parts.append(f"Director: {row['Director']}")
    st.caption(" · ".join(meta_parts))
    rating = row["Rating"]
    if rating is not None and str(rating) not in ("", "nan"):
        st.caption(f"⭐ {rating}/10")
    tmdb_url = row["Details"]
    btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 1])
    with btn_col1:
        if tmdb_url:
            st.link_button("🔗 Details", tmdb_url)
    if ref_iso:
        with btn_col2:
            gcal_url = _google_calendar_url(row, ref_iso)
            if gcal_url:
                st.link_button("📅 Add to Google Calendar", gcal_url)
        with btn_col3:
            ics = _build_ics(row, ref_iso)
            if ics:
                safe_title = "".join(c for c in row["Title"] if c.isalnum() or c in " _-").strip().replace(" ", "_")
                st.download_button(
                    "⬇️ Download .ics",
                    data=ics,
                    file_name=f"{safe_title}.ics",
                    mime="text/calendar",
                )
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

# ── Top X Cards ─────────────────────────────────────────────────────────────
topX = (
    df[pd.notna(df["Rating"])]
    .drop_duplicates(subset="Title", keep="first")
    .nlargest(15, "Rating")
    .reset_index(drop=True)
)
if not topX.empty:
    st.subheader("🏆 Top 15 films this week")
    _AVAIL_COLOR = {
        "🟢Only on TV":            "#2ecc71",
        "🟠Available on platforms": "#e67e22",
        "🔵Pay only":              "#3498db",
    }
    cols = st.columns(5)
    for i, film in topX.iterrows():
        color = _AVAIL_COLOR.get(film["Availability"], "#666666")
        director_line = (
            f'<div style="font-size:10px;color:#aaa;margin-bottom:3px">'
            f'{film["Director"]}</div>'
            if film["Director"] != "-" else ""
        )
        tmdb_href = (
            f'href="{film["Details"]}" target="_blank"'
            if pd.notna(film["Details"]) and film["Details"] else ""
        )
        with cols[i % 5]:
            st.markdown(
                f"""<a {tmdb_href} style="text-decoration:none">
                <div style="
                    background:linear-gradient(150deg,#1e1e2e,#2a2a3e);
                    border-radius:12px; padding:14px; margin-bottom:8px;
                    border-left:4px solid {color}; min-height:150px;
                    cursor:{'pointer' if tmdb_href else 'default'};
                    transition:opacity .2s;
                " onmouseover="this.style.opacity='.8'"
                   onmouseout="this.style.opacity='1'">
                    <div style="font-size:15px;font-weight:700;color:#fff;
                                line-height:1.35;margin-bottom:6px"
                    >{film["Title"]}</div>
                    <div style="font-size:20px;font-weight:800;color:#f1c40f;
                                margin-bottom:4px">⭐ {film["Rating"]}</div>
                    {director_line}
                    <div style="font-size:10px;color:#888">
                        {film["Date"]} · {film["Time"]}<br>
                        {film["Channel"]}
                    </div>
                    <div style="font-size:10px;color:{color};margin-top:6px">
                        {film["Availability"]}
                    </div>
                </div></a>""",
                unsafe_allow_html=True,
            )
    st.divider()

# ── Filters ─────────────────────────────────────────────────────────────────
st.subheader("Filters")
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    search_title = st.text_input("Title", placeholder="Search by title...")
with col2:
    channels = ["All"] + sorted(df["Channel"].dropna().unique().tolist())
    selected_channel = st.selectbox("Channel", channels)
with col3:
    avail_opts = ["All"] + sorted(df["Availability"].dropna().unique().tolist())
    selected_availability = st.selectbox("Availability", avail_opts)

# ── Date tabs + Table ────────────────────────────────────────────────────────
days_opts = ["All"] + df["Date"].unique().tolist()
day_tabs = st.tabs(days_opts)
selected_film_row = None

VISIBLE_COLS_ALL = ["Date"] + VISIBLE_COLS
COLUMN_CONFIG_ALL = {**COLUMN_CONFIG, "Date": st.column_config.TextColumn("Date")}

for tab, day in zip(day_tabs, days_opts):
    with tab:
        filtered = _apply_filters(df, search_title, selected_channel, day, selected_availability)
        st.markdown(f"**{len(filtered)} films**")
        cols_to_show = VISIBLE_COLS_ALL if day == "All" else VISIBLE_COLS
        col_cfg = COLUMN_CONFIG_ALL if day == "All" else COLUMN_CONFIG
        ev = st.dataframe(
            filtered[cols_to_show],
            hide_index=True,
            column_config=col_cfg,
            on_select="rerun",
            selection_mode="single-row",
            key=f"table_{day}",
        )
        if ev.selection.rows and ev.selection.rows[0] < len(filtered):
            selected_film_row = filtered.iloc[ev.selection.rows[0]]

if selected_film_row is not None:
    new_key = (selected_film_row["Title"], selected_film_row["Date"], selected_film_row["Time"])
    if new_key != st.session_state.dialog_row_key:
        st.session_state.dialog_row_key = new_key
        _show_film_details(selected_film_row, generated_at)
else:
    st.session_state.dialog_row_key = None

# ── About / Credits ──────────────────────────────────────────────────────────
st.divider()
st.caption("TV schedule data sourced from [programmitv.com](https://www.programmitv.com).")
st.markdown(
    '<img src="https://www.themoviedb.org/assets/2/v4/logos/v2/blue_short-8e7b30f73a4020692ccca9c88bafe5dcb6f8a62a4c6bc55cd9ba82bb2cd95f6c.svg" '
    'height="14" style="vertical-align:middle;margin-right:6px;opacity:.7">'
    '<span style="font-size:12px;color:gray">This product uses the TMDB API but is not endorsed or certified by TMDB.</span>',
    unsafe_allow_html=True,
)
