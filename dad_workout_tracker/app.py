import streamlit as st
import json
import os
from datetime import datetime, timedelta, date

st.set_page_config(page_title="Family Workouts")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden !important;}
    [data-testid="stToolbar"] {visibility: hidden !important;}
    [data-testid="stBottomBlockContainer"] {visibility: hidden !important;}
    .stDeployButton {visibility: hidden !important;}
    </style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# FILE SETUP
# ─────────────────────────────────────────

SESSIONS_FILE = "sessions.json"


def load_sessions():
    if not os.path.exists(SESSIONS_FILE):
        return {}
    with open(SESSIONS_FILE, "r") as f:
        return json.load(f)


def save_sessions(all_sessions):
    with open(SESSIONS_FILE, "w") as f:
        json.dump(all_sessions, f, indent=2)


def save_session_for_user(username, session_entry):
    all_sessions = load_sessions()
    if username not in all_sessions:
        all_sessions[username] = []
    all_sessions[username].append(session_entry)
    save_sessions(all_sessions)


def delete_session_for_user(username, index):
    all_sessions = load_sessions()
    all_sessions[username].pop(index)
    save_sessions(all_sessions)


# ─────────────────────────────────────────
# SESSION STATE SETUP
# ─────────────────────────────────────────

defaults = {
    "logged_in_user": None,
    "current_page": "login",
    "confirm_delete_index": None,
    # Day offsets — each arrow moves one day
    "personal_day_offset": 0,
    "family_day_offset": 0,
    "expanded_personal": False,
    "draft_workouts": [],
    "session_saved": False,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ─────────────────────────────────────────
# ACCOUNTS
# ─────────────────────────────────────────

accounts = ["Dad", "Mum", "Ozzie"]

account_colours = {
    "Dad":   "#FFD700",  # gold
    "Mum":   "#FF8C00",  # orange
    "Ozzie": "#FFFFFF",  # white
}

# ─────────────────────────────────────────
# WORKOUT LISTS
# ─────────────────────────────────────────

workout_types = [
    # Strength
    "Barbell back squat", "Front squat", "Deadlift", "Romanian deadlift",
    "Bench press", "Incline dumbbell press", "Overhead shoulder press",
    "Push-ups", "Pull-ups", "Chin-ups", "Bent-over barbell row",
    "Lat pulldown", "Dips", "Bicep curls", "Tricep pushdowns",
    "Leg press", "Walking lunges", "Step-ups", "Calf raises",
    "Farmer carries", "Sled pushes",
    # Cardio / Conditioning
    "Plank", "Hanging leg raises", "Russian twists", "Skipping",
    "Sprinting", "Box jumps", "Burpees", "Battle rope",
    "Mountain climbers", "Peloton bike workout",
    "Running", "Outdoor cycling", "Walking dog", "Rowing", "Trampolining",
    # Combat / Martial arts
    "Bag work", "Shadow boxing", "Muay Thai", "BJJ",
    # Classes / Sessions
    "Flexibility drills", "PT", "Pilates",
]

weighted_workouts = [
    "Barbell back squat", "Front squat", "Deadlift", "Romanian deadlift",
    "Bench press", "Incline dumbbell press", "Overhead shoulder press",
    "Bent-over barbell row", "Lat pulldown", "Bicep curls",
    "Tricep pushdowns", "Leg press", "Calf raises", "Farmer carries", "Sled pushes",
]

weighted_or_non_weighted_workouts = [
    "Dips", "Walking lunges", "Step-ups", "Pull-ups", "Chin-ups",
    "Sprinting", "Shadow boxing",
]

workouts_for_reps = [
    "Barbell back squat", "Front squat", "Deadlift", "Romanian deadlift",
    "Bench press", "Incline dumbbell press", "Overhead shoulder press",
    "Push-ups", "Pull-ups", "Chin-ups", "Bent-over barbell row",
    "Lat pulldown", "Dips", "Bicep curls", "Tricep pushdowns",
    "Leg press", "Step-ups", "Calf raises", "Hanging leg raises",
]

workouts_timed = [
    "Plank", "Skipping", "Battle rope", "Sled pushes", "Farmer carries",
    "Peloton bike workout", "Shadow boxing",
    "Running", "Outdoor cycling", "Walking dog", "Bag work", "Trampolining",
    "Flexibility drills", "PT", "Pilates", "Muay Thai", "BJJ",
]

workouts_timed_or_reps = [
    "Walking lunges", "Mountain climbers", "Russian twists",
    "Box jumps", "Burpees", "Sprinting", "Rowing",
]

workouts_with_sets = [
    "Barbell back squat", "Front squat", "Deadlift", "Romanian deadlift",
    "Bench press", "Incline dumbbell press", "Overhead shoulder press",
    "Push-ups", "Pull-ups", "Chin-ups", "Bent-over barbell row",
    "Lat pulldown", "Dips", "Bicep curls", "Tricep pushdowns",
    "Leg press", "Step-ups", "Calf raises", "Hanging leg raises",
    "Walking lunges", "Rowing", "Bag work", "Trampolining", "Shadow boxing",
]


# ─────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────

def parse_time_str(t_str):
    try:
        return datetime.strptime(t_str, "%H:%M").time()
    except (ValueError, TypeError):
        return None


def calc_duration_minutes(start_str, end_str):
    start = parse_time_str(start_str)
    end = parse_time_str(end_str)
    if start is None or end is None:
        return None
    base = date(2000, 1, 1)
    dt_start = datetime.combine(base, start)
    dt_end = datetime.combine(base, end)
    if dt_end < dt_start:
        dt_end += timedelta(days=1)
    delta = dt_end - dt_start
    return int(delta.total_seconds() // 60)


def format_duration(minutes):
    if minutes is None or minutes < 0:
        return "unknown duration"
    hours = minutes // 60
    mins = minutes % 60
    if hours > 0 and mins > 0:
        return f"{hours} hr {mins} mins"
    elif hours > 0:
        return f"{hours} hr"
    else:
        return f"{mins} mins"


def format_seconds(total_seconds):
    if total_seconds is None or total_seconds < 0:
        return "unknown"
    total_seconds = int(total_seconds)
    hours = total_seconds // 3600
    remainder = total_seconds % 3600
    mins = remainder // 60
    secs = remainder % 60
    parts = []
    if hours > 0:
        parts.append(f"{hours} hr")
    if mins > 0:
        parts.append(f"{mins} min")
    if secs > 0 or len(parts) == 0:
        parts.append(f"{secs} sec")
    return " ".join(parts)


def workout_summary_line(w):
    line = w["workout"]
    if w.get("weight_kg") is not None:
        line += f" — {w['weight_kg']}kg"
    if w.get("sets") is not None:
        line += f" — {w['sets']} sets"
    if w.get("reps") is not None:
        line += f" of {w['reps']} reps"
    elif w.get("duration_seconds") is not None:
        line += f" for {format_seconds(w['duration_seconds'])}"
    return line


def get_monday_of_week(target_date):
    return target_date - timedelta(days=target_date.weekday())


def sessions_by_date(username):
    all_sessions = load_sessions()
    user_sessions = all_sessions.get(username, [])
    by_date = {}
    for s in user_sessions:
        d = s.get("date")
        if d:
            if d not in by_date:
                by_date[d] = []
            by_date[d].append(s)
    return by_date


def family_sessions_by_date():
    all_sessions = load_sessions()
    by_date = {}
    for username, sessions in all_sessions.items():
        for s in sessions:
            d = s.get("date")
            if d:
                if d not in by_date:
                    by_date[d] = []
                if username not in by_date[d]:
                    by_date[d].append(username)
    return by_date


def render_family_dots(usernames_who_trained):
    if not usernames_who_trained:
        return "<div style='text-align:center; font-size:1.5rem; color:#444;'>⚫</div>"
    dots_html = ""
    for username in usernames_who_trained:
        colour = account_colours.get(username, "#888888")
        dots_html += (
            f"<span style='display:inline-block; width:16px; height:16px; "
            f"border-radius:50%; background-color:{colour}; "
            f"border: 1px solid #555; margin:2px;'></span>"
        )
    return f"<div style='text-align:center; padding: 4px 0;'>{dots_html}</div>"


def sessions_this_week(username):
    """Count how many sessions the user has logged in the current Mon-Sun week."""
    today = date.today()
    monday = get_monday_of_week(today)
    sunday = monday + timedelta(days=6)
    all_sessions = load_sessions()
    user_sessions = all_sessions.get(username, [])
    count = 0
    for s in user_sessions:
        raw = s.get("date")
        if raw:
            try:
                d = datetime.strptime(raw, "%Y-%m-%d").date()
                if monday <= d <= sunday:
                    count += 1
            except ValueError:
                pass
    return count


def timed_input(key_prefix):
    col_h, col_m, col_s = st.columns(3)
    with col_h:
        hours = st.number_input("Hours:", min_value=0, step=1, key=f"{key_prefix}_hours")
    with col_m:
        mins = st.number_input("Minutes:", min_value=0, step=1, key=f"{key_prefix}_mins")
    with col_s:
        secs = st.number_input("Seconds:", min_value=0, max_value=59, step=1, key=f"{key_prefix}_secs")
    return int((hours * 3600) + (mins * 60) + secs)


# ─────────────────────────────────────────
# FAMILY CALENDAR — single day view
# ─────────────────────────────────────────

def show_family_calendar():
    st.subheader(" Family activity ")

    today = date.today()
    displayed_date = today + timedelta(days=st.session_state.family_day_offset)
    date_str = displayed_date.strftime("%Y-%m-%d")
    friendly_date = displayed_date.strftime("%A %d %B %Y")
    is_today = displayed_date == today

    family_by_date = family_sessions_by_date()
    trainers_today = family_by_date.get(date_str, [])

    # Navigation row
    col_left, col_mid, col_right = st.columns([1, 4, 1])
    with col_left:
        if st.button("◀", key="fam_cal_prev"):
            st.session_state.family_day_offset -= 1
            st.rerun()
    with col_mid:
        label = f"**Today** — {friendly_date}" if is_today else friendly_date
        st.markdown(
            f"<p style='text-align:center; font-size:0.9rem; color:#888;'>{label}</p>",
            unsafe_allow_html=True,
        )
    with col_right:
        if st.button("▶", key="fam_cal_next"):
            st.session_state.family_day_offset += 1
            st.rerun()

    # Dots for this day
    st.markdown(render_family_dots(trainers_today), unsafe_allow_html=True)

    # Show who trained if anyone did
    if trainers_today:
        names = ", ".join(trainers_today)
        st.markdown(
            f"<p style='text-align:center; font-size:0.85rem; color:#aaa;'>{names}</p>",
            unsafe_allow_html=True,
        )

    # Colour key
    st.markdown("&nbsp;", unsafe_allow_html=True)
    key_html = ""
    for name, colour in account_colours.items():
        key_html += (
            f"<span style='display:inline-block; width:10px; height:10px; "
            f"border-radius:50%; background-color:{colour}; "
            f"border: 1px solid #555; margin-right:4px;'></span>"
            f"<span style='font-size:0.8rem; margin-right:12px;'>{name}</span>"
        )
    st.markdown(f"<div style='text-align:center;'>{key_html}</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────
# PAGE: LOGIN
# ───────────────────────────â─────────────

def show_login_page():
    st.title("Family Workout Tracker")
    st.write("---")

    show_family_calendar()

    st.write("---")
    st.subheader("Who's working out today?")
    for account in accounts:
        if st.button(account, use_container_width=True):
            st.session_state.logged_in_user = account
            st.session_state.current_page = "home"
            st.session_state.personal_day_offset = 0
            st.session_state.expanded_personal = False
            st.rerun()


# ─────────────────────────────────────────
# PAGE: HOME — single day personal calendar
# ─────────────────────────────────────────

def show_home_page():
    username = st.session_state.logged_in_user

    st.markdown(f"<h1 style='text-align: center;'>{username}</h1>", unsafe_allow_html=True)
    st.write("---")

    today = date.today()
    displayed_date = today + timedelta(days=st.session_state.personal_day_offset)
    date_str = displayed_date.strftime("%Y-%m-%d")
    friendly_date = displayed_date.strftime("%A %d %B %Y")
    is_today = displayed_date == today

    by_date = sessions_by_date(username)
    has_session = date_str in by_date

    # Navigation row
    col_left, col_mid, col_right = st.columns([1, 4, 1])
    with col_left:
        if st.button("◀", key="cal_prev"):
            st.session_state.personal_day_offset -= 1
            st.session_state.expanded_personal = False
            st.rerun()
    with col_mid:
        label = f"Today — {friendly_date}" if is_today else friendly_date
        st.markdown(
            f"<p style='text-align:center; font-size:0.9rem; color:#888;'>{label}</p>",
            unsafe_allow_html=True,
        )
    with col_right:
        if st.button("▶", key="cal_next"):
            st.session_state.personal_day_offset += 1
            st.session_state.expanded_personal = False
            st.rerun()

    # Bar for this day
    if has_session:
        if st.button("🔵  View sessions", key="personal_dot", use_container_width=True):
            st.session_state.expanded_personal = not st.session_state.expanded_personal
            st.rerun()
    else:
        st.markdown(
            "<div style='background-color:#2a2a2a; border-radius:8px; "
            "padding:10px; text-align:center; color:#555; font-size:0.85rem;'>"
            "No session logged</div>",
            unsafe_allow_html=True,
        )

    # Expanded session detail
    if has_session and st.session_state.expanded_personal:
        exp_sessions = by_date[date_str]
        with st.container(border=True):
            for idx, sess in enumerate(exp_sessions):
                dur = calc_duration_minutes(sess.get("start_time"), sess.get("end_time"))
                dur_str = format_duration(dur)
                st.markdown(
                    f"**Session {idx + 1}** — {sess.get('start_time', '?')} to "
                    f"{sess.get('end_time', '?')} ({dur_str})"
                )
                for w in sess.get("workouts", []):
                    st.markdown(f"&nbsp;&nbsp;• {workout_summary_line(w)}", unsafe_allow_html=True)

    st.write("---")

    # ── Stats ──
    all_sessions = load_sessions()
    user_sessions = all_sessions.get(username, [])

    this_week_count = sessions_this_week(username)
    st.markdown(f"This week: **{this_week_count} session(s)** so far.")

    if len(user_sessions) >= 2:
        all_dates = sorted(set(s["date"] for s in user_sessions if "date" in s))
        if len(all_dates) >= 2:
            first = datetime.strptime(all_dates[0], "%Y-%m-%d").date()
            last = datetime.strptime(all_dates[-1], "%Y-%m-%d").date()
            total_days = (last - first).days + 1
            total_weeks = max(1, round(total_days / 7))
            sessions_per_week = max(1, round(len(user_sessions) / total_weeks))
            durations = []
            for s in user_sessions:
                dur = calc_duration_minutes(s.get("start_time"), s.get("end_time"))
                if dur is not None and dur > 0:
                    durations.append(dur)
            avg_dur = format_duration(round(sum(durations) / len(durations))) if durations else "unknown"
            st.markdown(
                f"On average you train **{sessions_per_week}x per week** "
                f"for **{avg_dur}** per session."
            )

    st.write("---")

    if len(user_sessions) > 0:
        st.write(f"You have **{len(user_sessions)}** session(s) logged.")
        if st.button("See all sessions"):
            st.session_state.current_page = "history"
            st.rerun()

    if st.button("➕ New Session", use_container_width=True):
        st.session_state.draft_workouts = []
        st.session_state.session_saved = False
        st.session_state.current_page = "log_session"
        st.rerun()

    st.write("---")
    if st.button("Log out"):
        st.session_state.logged_in_user = None
        st.session_state.current_page = "login"
        st.rerun()


# ─────────────────────────────────────────
# PAGE: LOG A SESSION
# ─────────────────────────────────────────

def show_log_session_page():
    username = st.session_state.logged_in_user

    if st.button("← Back to home"):
        st.session_state.current_page = "home"
        st.rerun()

    st.title("Log a Session")
    st.write(f"Logging for: **{username}**")
    st.write("---")

    now = datetime.now()
    now_time_str = now.strftime("%H:%M")

    session_date_input = st.date_input("Session date:", value=now.date())
    session_date_str = session_date_input.strftime("%Y-%m-%d")

    st.write("**Session times** — pre-filled with the current time, change if needed:")
    col1, col2 = st.columns(2)
    with col1:
        start_time_str = st.text_input("Start time (HH:MM):", value=now_time_str, key="start_time_input")
    with col2:
        end_time_str = st.text_input("End time (HH:MM):", value=now_time_str, key="end_time_input")

    start_valid = parse_time_str(start_time_str) is not None
    end_valid = parse_time_str(end_time_str) is not None

    if not start_valid:
        st.warning("Start time doesn't look right — use HH:MM format, e.g. 07:30")
    if not end_valid:
        st.warning("End time doesn't look right — use HH:MM format, e.g. 08:45")

    if start_valid and end_valid:
        dur = calc_duration_minutes(start_time_str, end_time_str)
        if dur is not None and dur >= 0:
            st.info(f"Session duration: **{format_duration(dur)}**")

    st.write("---")

    # ── Workouts added so far ──
    if len(st.session_state.draft_workouts) > 0:
        st.subheader("Workouts in this session:")
        for i, w in enumerate(st.session_state.draft_workouts):
            col_w, col_del = st.columns([5, 1])
            with col_w:
                st.write(f"{i + 1}. {workout_summary_line(w)}")
            with col_del:
                if st.button("✕", key=f"remove_w_{i}"):
                    st.session_state.draft_workouts.pop(i)
                    st.rerun()
        st.write("---")

    # ── Add a workout ──
    st.subheader("Add a workout:")

    selected_workout = st.selectbox("Select workout type:", workout_types, key="workout_select")

    # Weight
    weight = None
    if selected_workout in weighted_workouts:
        weight = st.number_input("Amount of weight (kg):", min_value=0.0, step=2.5, key="weight_input")
    elif selected_workout in weighted_or_non_weighted_workouts:
        weight_choice = st.radio("Did you use added weight?", ["No weight", "With weight"], key="weight_choice")
        if weight_choice == "With weight":
            weight = st.number_input("Amount of weight (kg):", min_value=0.0, step=2.5, key="weight_input_optional")

    # Reps / Time
    reps = None
    duration_seconds = None

    if selected_workout in workouts_for_reps:
        reps = st.number_input("Number of reps:", min_value=0, step=1, key="reps_input")
    elif selected_workout in workouts_timed:
        st.write("How long did you do it for?")
        duration_seconds = timed_input("timed")
    elif selected_workout in workouts_timed_or_reps:
        measure_choice = st.radio("How are you tracking this?", ["Reps", "Time"], key="measure_choice")
        if measure_choice == "Reps":
            reps = st.number_input("Number of reps:", min_value=0, step=1, key="reps_input_alt")
        else:
            st.write("How long did you do it for?")
            duration_seconds = timed_input("timed_or_reps")

    # Sets
    how_many_sets = None
    if selected_workout in workouts_with_sets:
        how_many_sets = st.number_input(
            f"How many sets of {selected_workout}?",
            min_value=0, step=1, key="sets_input"
        )

    if st.button("➕ Add workout to session"):
        new_workout = {
            "workout": selected_workout,
            "weight_kg": weight,
            "sets": how_many_sets,
            "reps": reps,
            "duration_seconds": duration_seconds,
        }
        st.session_state.draft_workouts.append(new_workout)
        st.rerun()

    st.write("---")

    can_save = (
        len(st.session_state.draft_workouts) > 0
        and start_valid
        and end_valid
    )

    if not can_save and len(st.session_state.draft_workouts) == 0:
        st.caption("Add at least one workout before saving.")

    if st.button("Save Session", disabled=not can_save):
        session_entry = {
            "date": session_date_str,
            "start_time": start_time_str,
            "end_time": end_time_str,
            "workouts": st.session_state.draft_workouts.copy(),
        }
        save_session_for_user(username, session_entry)
        st.session_state.draft_workouts = []
        st.session_state.session_saved = True
        st.rerun()

    if st.session_state.session_saved:
        st.success("Session saved! Add another or head back home.")
        st.session_state.session_saved = False
        if st.button("Back to home"):
            st.session_state.current_page = "home"
            st.rerun()


# ─────────────────────────────────────────
# PAGE: SESSION HISTORY
# ─────────────────────────────────────────

def show_history_page():
    username = st.session_state.logged_in_user

    if st.button("← Back to home"):
        st.session_state.confirm_delete_index = None
        st.session_state.current_page = "home"
        st.rerun()

    st.title(f"{username}'s Session History")
    st.write("---")

    all_sessions = load_sessions()
    user_sessions = all_sessions.get(username, [])

    if len(user_sessions) == 0:
        st.info("No sessions saved yet — get after it!")
        return

    for real_index, session in reversed(list(enumerate(user_sessions))):
        dur = calc_duration_minutes(session.get("start_time"), session.get("end_time"))
        dur_str = format_duration(dur)

        raw_date = session.get("date", "")
        try:
            friendly_date = datetime.strptime(raw_date, "%Y-%m-%d").strftime("%A %d %B %Y")
        except ValueError:
            friendly_date = raw_date

        workouts = session.get("workouts", [])

        with st.container(border=True):
            st.markdown(
                f"**{friendly_date}** — "
                f"{session.get('start_time', '?')} to {session.get('end_time', '?')} "
                f"({dur_str})"
            )
            for w in workouts:
                st.markdown(f"• {workout_summary_line(w)}")

            if st.session_state.confirm_delete_index == real_index:
                st.warning("Are you sure you want to delete this session?")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Yes, delete it", key=f"confirm_{real_index}"):
                        delete_session_for_user(username, real_index)
                        st.session_state.confirm_delete_index = None
                        st.rerun()
                with col2:
                    if st.button("No, keep it", key=f"cancel_{real_index}"):
                        st.session_state.confirm_delete_index = None
                        st.rerun()
            else:
                if st.button("Delete", key=f"delete_{real_index}"):
                    st.session_state.confirm_delete_index = real_index
                    st.rerun()


# ─────────────────────────────────────────
# MAIN ROUTER
# ─────────────────────────────────────────

if st.session_state.current_page == "login":
    show_login_page()

elif st.session_state.current_page == "home":
    show_home_page()

elif st.session_state.current_page == "log_session":
    show_log_session_page()

elif st.session_state.current_page == "history":
    show_history_page()

