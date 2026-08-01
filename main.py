"""
===============================================================
 CRICKET STATISTICS TRACKER
 PHASE 1: Database (JSON), Login, Main Menu, Add Player, View Player
===============================================================

This program is designed to run on the Programiz Python Compiler.
It only uses Python's built-in modules (json, datetime),
so no installation of extra packages is required.
(The "os" module is intentionally avoided — Programiz's sandbox
does not make it available, so file existence is checked using
a try/except around open() instead.)

HOW DATA IS SAVED:
- All player data is stored in a JSON file called "players.json".
- Every time you add or change a player, the file is saved immediately.
- If you close the program and run it again, all your players will
  still be there, because the program loads "players.json" at startup.
"""

import json
from datetime import datetime

# ---------------------------------------------------------------
# CONFIGURATION / CONSTANTS
# ---------------------------------------------------------------

DATA_FILE = "players.json"          # The "database" file
ADMIN_PASSWORD = "admin123"         # Login password
MAX_LOGIN_ATTEMPTS = 3

VALID_CAMPUSES = ["PECHS", "DHA"]
VALID_TEAMS = ["Cedar Blues", "Cedar Gold", "Cedar White"]
VALID_ROLES = ["Batsman", "Bowler", "All-Rounder", "Wicket Keeper"]
VALID_BATTING_STYLES = ["Right Hand", "Left Hand"]
VALID_BOWLING_STYLES = [
    "Right Arm Fast", "Left Arm Fast", "Medium Pace",
    "Off Spin", "Leg Spin", "None"
]

# Tracks whether we've discovered this environment won't allow file writes.
# Once True, save_data() becomes a no-op so the program can keep running
# in memory-only mode instead of crashing every time.
FILE_SAVING_DISABLED = False


# ---------------------------------------------------------------
# DATA STORAGE FUNCTIONS
# ---------------------------------------------------------------

def load_data():
    """
    Loads player data from players.json.
    If the file does not exist yet, it creates an empty database
    and returns it, so the program never crashes on first run.
    """
    try:
        with open(DATA_FILE, "r") as file:
            data = json.load(file)
            # Safety check: make sure the expected key exists
            if "players" not in data:
                data["players"] = {}
            return data
    except FileNotFoundError:
        # File does not exist yet -> create an empty database structure
        empty_data = {"players": {}}
        save_data(empty_data)
        return empty_data
    except (json.JSONDecodeError, ValueError):
        # If the file is corrupted or empty, start fresh but do not
        # silently destroy anything the user might want to recover.
        print("Warning: players.json was unreadable. Starting with an empty database.")
        return {"players": {}}


def save_data(data):
    """
    Saves the given data dictionary to players.json.
    This is called immediately after every change, so nothing is lost.

    Some online sandboxes (certain Programiz environments included)
    do not allow writing files to disk. If that happens, we don't
    want to crash the whole program -- we just warn the user once
    that this session will be memory-only (no persistence between
    runs) and keep going.
    """
    global FILE_SAVING_DISABLED
    if FILE_SAVING_DISABLED:
        return

    try:
        with open(DATA_FILE, "w") as file:
            json.dump(data, file, indent=4)
    except PermissionError:
        FILE_SAVING_DISABLED = True
        print("\nNOTE: This environment does not allow saving files to disk.")
        print("The program will keep working for this session, but your")
        print("data will NOT be saved once the program closes.")
        print("Run this on Replit or a local Python installation for full")
        print("persistence across restarts.\n")


# ---------------------------------------------------------------
# GENERAL INPUT / VALIDATION HELPERS
# ---------------------------------------------------------------

def print_header(title):
    """Prints a consistent section header."""
    print("\n" + "=" * 50)
    print(title)
    print("=" * 50)


def get_nonempty_string(prompt):
    """Keeps asking until the user types something that isn't blank."""
    while True:
        value = input(prompt).strip()
        if value != "":
            return value
        print("This field cannot be empty. Please try again.")


def get_choice_from_list(prompt, options):
    """
    Displays a numbered list of options and forces the user to pick
    a valid one. Returns the chosen option as a string.
    """
    while True:
        print(prompt)
        for index, option in enumerate(options, start=1):
            print(f"  {index}. {option}")
        raw_choice = input("Enter choice number: ").strip()

        if raw_choice.isdigit():
            choice_num = int(raw_choice)
            if 1 <= choice_num <= len(options):
                return options[choice_num - 1]

        print("Invalid choice. Please enter a valid number from the list.\n")


def get_menu_choice(min_value, max_value):
    """
    Gets a validated integer menu choice between min_value and max_value.
    """
    while True:
        raw_choice = input("Enter your choice: ").strip()
        if raw_choice.isdigit():
            choice_num = int(raw_choice)
            if min_value <= choice_num <= max_value:
                return choice_num
        print(f"Invalid choice. Please enter a number between {min_value} and {max_value}.")


def get_date_string(prompt):
    """
    Asks for a date and validates the format (YYYY-MM-DD).
    Keeps asking until a valid date is entered.
    """
    while True:
        raw_date = input(prompt + " (YYYY-MM-DD): ").strip()
        try:
            datetime.strptime(raw_date, "%Y-%m-%d")
            return raw_date
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD (e.g., 2026-08-01).")


def get_yes_no(prompt):
    """
    Asks a direct Y/N question (not a numbered list) and keeps asking
    until the user answers Y or N, case-insensitive. Returns "Y" or "N".
    """
    while True:
        raw_value = input(f"{prompt} (Y/N): ").strip().upper()
        if raw_value in ("Y", "N"):
            return raw_value
        print("Please enter Y or N.")


def get_nonnegative_int(prompt):
    """
    Keeps asking until the user enters a whole number that is 0 or greater.
    Used for every counting statistic (runs, wickets, catches, etc.) so
    negative numbers can never be entered.
    """
    while True:
        raw_value = input(prompt).strip()
        if raw_value.isdigit():
            return int(raw_value)
        print("Please enter a valid non-negative whole number.")


def get_overs_input(prompt):
    """
    Cricket overs are written like 4.3, meaning 4 COMPLETE overs plus
    3 balls of the next over (NOT 4.3 overs as a decimal number).
    This function validates that special format and returns the total
    number of legal balls bowled, so we can accumulate overs accurately
    across many matches without rounding errors.
    """
    while True:
        raw_value = input(f"{prompt} (format overs.balls, e.g. 4.3 = 4 overs 3 balls): ").strip()
        parts = raw_value.split(".")

        whole_overs = None
        balls_part = 0

        if len(parts) == 1 and parts[0].isdigit():
            whole_overs = int(parts[0])
        elif len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit() and len(parts[1]) == 1:
            whole_overs = int(parts[0])
            balls_part = int(parts[1])

        if whole_overs is None or whole_overs < 0 or not (0 <= balls_part <= 5):
            print("Invalid format. Overs must be a non-negative whole number, and the")
            print("balls part (after the dot) must be a single digit from 0 to 5.")
            continue

        return (whole_overs * 6) + balls_part


def balls_to_overs(total_balls):
    """Converts a total ball count back into cricket over notation, e.g. 27 balls -> 4.3"""
    whole_overs = total_balls // 6
    remaining_balls = total_balls % 6
    return float(f"{whole_overs}.{remaining_balls}")


def parse_best_bowling(best_bowling_str):
    """Parses a 'wickets/runs' string like '3/25' into (wickets, runs) integers."""
    try:
        wickets_str, runs_str = best_bowling_str.split("/")
        return int(wickets_str), int(runs_str)
    except (ValueError, AttributeError):
        return 0, 0


# ---------------------------------------------------------------
# STATISTIC CALCULATION FUNCTIONS
# ---------------------------------------------------------------

def calculate_strike_rate(runs, balls_faced):
    """Batting strike rate = runs scored per 100 balls faced."""
    if balls_faced == 0:
        return 0.0
    return round((runs / balls_faced) * 100, 2)


def calculate_batting_average(runs, outs):
    """
    Batting average = total runs / number of times out.
    If the player has never been out, cricket convention has no true
    average -- we simply show the total runs so it's never a crash-causing
    division by zero.
    """
    if outs == 0:
        return float(runs)
    return round(runs / outs, 2)


def calculate_boundary_percentage(fours, sixes, runs):
    """Percentage of total runs that came from boundaries (4s and 6s)."""
    if runs == 0:
        return 0.0
    boundary_runs = (fours * 4) + (sixes * 6)
    return round((boundary_runs / runs) * 100, 2)


def calculate_economy(runs_given, balls_bowled):
    """Economy rate = average runs conceded per over."""
    if balls_bowled == 0:
        return 0.0
    overs_bowled = balls_bowled / 6
    return round(runs_given / overs_bowled, 2)


def calculate_bowling_average(runs_given, wickets):
    """Bowling average = runs conceded per wicket taken."""
    if wickets == 0:
        return 0.0
    return round(runs_given / wickets, 2)


def calculate_bowling_strike_rate(balls_bowled, wickets):
    """Bowling strike rate = balls bowled per wicket taken."""
    if wickets == 0:
        return 0.0
    return round(balls_bowled / wickets, 2)


# ---------------------------------------------------------------
# LOGIN SCREEN
# ---------------------------------------------------------------

def login():
    """
    Displays the login screen and checks the password.
    Allows up to MAX_LOGIN_ATTEMPTS attempts.
    Returns True if login succeeds, False if all attempts are used up.
    """
    print_header("CEDAR COLLEGE\nCRICKET STATISTICS TRACKER")

    attempts_left = MAX_LOGIN_ATTEMPTS
    while attempts_left > 0:
        entered_password = input("Enter Password: ").strip()
        if entered_password == ADMIN_PASSWORD:
            print("\nLogin successful. Welcome!")
            return True
        else:
            attempts_left -= 1
            if attempts_left > 0:
                print(f"Incorrect password. Attempts remaining: {attempts_left}")
            else:
                print("Incorrect password. No attempts remaining.")

    return False


# ---------------------------------------------------------------
# PLAYER STATISTICS TEMPLATE
# ---------------------------------------------------------------

def create_blank_statistics():
    """
    Returns a dictionary of every statistic a player can have,
    all initialized to zero. This template is used for both
    batting and bowling / keeping stats, so future phases (2, 3, 4)
    can fill them in without needing to redesign the data structure.
    """
    return {
        # Batting stats
        "matches": 0,
        "innings": 0,
        "runs": 0,
        "highest_score": 0,
        "balls_faced": 0,
        "fours": 0,
        "sixes": 0,
        "outs": 0,
        "not_outs": 0,
        "fifties": 0,
        "hundreds": 0,
        "ducks": 0,
        "strike_rate": 0.0,
        "batting_average": 0.0,
        "boundary_percentage": 0.0,
        "runs_per_match": 0.0,

        # Bowling stats
        # "balls_bowled" tracks the true total of legal balls bowled so
        # overs can be added up across matches with no rounding error.
        # "overs" is the human-readable version derived from it.
        "balls_bowled": 0,
        "overs": 0.0,
        "maidens": 0,
        "runs_given": 0,
        "wickets": 0,
        "wide_balls": 0,
        "no_balls": 0,
        "economy": 0.0,
        "bowling_average": 0.0,
        "bowling_strike_rate": 0.0,
        "best_bowling": "0/0",
        "four_wicket_hauls": 0,
        "five_wicket_hauls": 0,

        # Wicket Keeper stats
        "catches": 0,
        "stumpings": 0,
        "run_outs": 0,

        # Match history: a list of match record dictionaries.
        # This will be filled in during Phase 2, and old records
        # are never overwritten -- only new ones are appended.
        "match_history": []
    }


# ---------------------------------------------------------------
# ADD NEW PLAYER
# ---------------------------------------------------------------

def add_player(data):
    """
    Handles the "Add New Player" menu option.
    Asks for RFID first and checks for duplicates before continuing.
    """
    print_header("ADD NEW PLAYER")

    rfid = get_nonempty_string("Enter RFID (Student ID): ")

    if rfid in data["players"]:
        print("\nPlayer already exists.")
        return

    # Collect the rest of the player's details
    name = get_nonempty_string("Player Name: ")
    campus = get_choice_from_list("Select Campus:", VALID_CAMPUSES)
    team = get_choice_from_list("Select Team:", VALID_TEAMS)
    role = get_choice_from_list("Select Playing Role:", VALID_ROLES)
    batting_style = get_choice_from_list("Select Batting Style:", VALID_BATTING_STYLES)
    bowling_style = get_choice_from_list("Select Bowling Style:", VALID_BOWLING_STYLES)
    jersey_number = get_nonempty_string("Jersey Number: ")
    department = get_nonempty_string("Department / Class: ")
    date_joined = get_date_string("Date Joined")

    # Build the full player record
    player_record = {
        "rfid": rfid,
        "name": name,
        "campus": campus,
        "team": team,
        "role": role,
        "batting_style": batting_style,
        "bowling_style": bowling_style,
        "jersey_number": jersey_number,
        "department": department,
        "date_joined": date_joined,
        "statistics": create_blank_statistics()
    }

    # Save the new player into the database and write to disk immediately
    data["players"][rfid] = player_record
    save_data(data)

    print(f"\nPlayer '{name}' added successfully with all statistics initialized to zero.")


# ---------------------------------------------------------------
# VIEW PLAYER PROFILE
# ---------------------------------------------------------------

def view_player(data):
    """
    Handles the "View Player Profile" menu option.
    Displays all stored information about a single player.
    """
    print_header("VIEW PLAYER PROFILE")

    rfid = get_nonempty_string("Enter RFID: ")

    if rfid not in data["players"]:
        print("\nPlayer not found.")
        return

    player = data["players"][rfid]
    stats = player["statistics"]

    print_header(f"PROFILE: {player['name']}")
    print(f"RFID              : {player['rfid']}")
    print(f"Name              : {player['name']}")
    print(f"Campus            : {player['campus']}")
    print(f"Team              : {player['team']}")
    print(f"Role              : {player['role']}")
    print(f"Jersey Number     : {player['jersey_number']}")
    print(f"Department        : {player['department']}")
    print(f"Batting Style     : {player['batting_style']}")
    print(f"Bowling Style     : {player['bowling_style']}")
    print(f"Date Joined       : {player['date_joined']}")

    print("\n--- CAREER STATISTICS ---")
    print(f"Matches           : {stats['matches']}")
    print(f"Innings           : {stats['innings']}")
    print(f"Runs              : {stats['runs']}")
    print(f"Highest Score     : {stats['highest_score']}")
    print(f"Balls Faced       : {stats['balls_faced']}")
    print(f"Fours             : {stats['fours']}")
    print(f"Sixes             : {stats['sixes']}")
    print(f"Outs              : {stats['outs']}")
    print(f"Not Outs          : {stats['not_outs']}")
    print(f"50s               : {stats['fifties']}")
    print(f"100s              : {stats['hundreds']}")
    print(f"Ducks             : {stats['ducks']}")
    print(f"Strike Rate       : {stats['strike_rate']}")
    print(f"Batting Average   : {stats['batting_average']}")
    print(f"Boundary %        : {stats['boundary_percentage']}")
    print(f"Runs Per Match    : {stats['runs_per_match']}")
    print()
    print(f"Overs Bowled      : {stats['overs']}")
    print(f"Maidens           : {stats['maidens']}")
    print(f"Runs Given        : {stats['runs_given']}")
    print(f"Wickets           : {stats['wickets']}")
    print(f"Economy           : {stats['economy']}")
    print(f"Bowling Average   : {stats['bowling_average']}")
    print(f"Bowling Strike Rate: {stats['bowling_strike_rate']}")
    print(f"Best Bowling      : {stats['best_bowling']}")
    print(f"4-Wicket Hauls    : {stats['four_wicket_hauls']}")
    print(f"5-Wicket Hauls    : {stats['five_wicket_hauls']}")
    print()
    print(f"Catches           : {stats['catches']}")
    print(f"Stumpings         : {stats['stumpings']}")
    print(f"Run Outs          : {stats['run_outs']}")

    if stats["match_history"]:
        print(f"\n--- MATCH HISTORY ({len(stats['match_history'])} matches) ---")
        for match in stats["match_history"]:
            print(
                f"{match['date']} vs {match['opponent']} ({match['tournament']}, "
                f"{match['match_type']}) - Runs: {match['runs']}, Wickets: {match['wickets']}, "
                f"Overs: {match['overs']}, Result: {match['result']}"
            )
    else:
        print("\nNo match history recorded yet.")


# ---------------------------------------------------------------
# UPDATE PLAYER STATISTICS (PHASE 2)
# ---------------------------------------------------------------

VALID_MATCH_TYPES = ["T20", "ODI", "Test", "Practice"]
VALID_RESULTS = ["Win", "Loss", "Tie", "No Result"]


def apply_batting_stats(stats, runs, balls_faced, fours, sixes, dismissal):
    """
    Pure calculation logic: folds one match's batting numbers into the
    player's career totals and recalculates every dependent statistic.
    Contains no input() calls, so both the interactive menu and the
    file-import feature can call this with values from either source.
    """
    stats["innings"] += 1
    stats["runs"] += runs
    stats["balls_faced"] += balls_faced
    stats["fours"] += fours
    stats["sixes"] += sixes

    if runs > stats["highest_score"]:
        stats["highest_score"] = runs

    if dismissal == "Out":
        stats["outs"] += 1
        if runs == 0:
            stats["ducks"] += 1
    else:
        stats["not_outs"] += 1

    if 50 <= runs < 100:
        stats["fifties"] += 1
    elif runs >= 100:
        stats["hundreds"] += 1

    stats["strike_rate"] = calculate_strike_rate(stats["runs"], stats["balls_faced"])
    stats["batting_average"] = calculate_batting_average(stats["runs"], stats["outs"])
    stats["boundary_percentage"] = calculate_boundary_percentage(
        stats["fours"], stats["sixes"], stats["runs"]
    )
    stats["runs_per_match"] = round(stats["runs"] / stats["matches"], 2) if stats["matches"] else 0.0


def record_batting_stats(stats):
    """Interactively asks for this match's batting numbers, then applies them."""
    print("\n--- Batting Statistics ---")
    runs = get_nonnegative_int("Runs Scored: ")
    balls_faced = get_nonnegative_int("Balls Faced: ")
    fours = get_nonnegative_int("Fours: ")
    sixes = get_nonnegative_int("Sixes: ")
    dismissal = get_choice_from_list("Dismissal:", ["Out", "Not Out"])

    apply_batting_stats(stats, runs, balls_faced, fours, sixes, dismissal)
    return runs, balls_faced


def apply_bowling_stats(stats, balls_this_match, maidens, runs_given, wickets, wide_balls, no_balls):
    """Pure calculation logic for bowling stats (see apply_batting_stats)."""
    stats["balls_bowled"] += balls_this_match
    stats["overs"] = balls_to_overs(stats["balls_bowled"])
    stats["maidens"] += maidens
    stats["runs_given"] += runs_given
    stats["wickets"] += wickets
    stats["wide_balls"] += wide_balls
    stats["no_balls"] += no_balls

    stats["economy"] = calculate_economy(stats["runs_given"], stats["balls_bowled"])
    stats["bowling_average"] = calculate_bowling_average(stats["runs_given"], stats["wickets"])
    stats["bowling_strike_rate"] = calculate_bowling_strike_rate(stats["balls_bowled"], stats["wickets"])

    # Best bowling is the single-match performance with the most wickets;
    # fewest runs given breaks a tie between two similar performances.
    best_wickets, best_runs = parse_best_bowling(stats["best_bowling"])
    if wickets > best_wickets or (wickets == best_wickets and runs_given < best_runs):
        stats["best_bowling"] = f"{wickets}/{runs_given}"

    if wickets == 4:
        stats["four_wicket_hauls"] += 1
    elif wickets >= 5:
        stats["five_wicket_hauls"] += 1


def record_bowling_stats(stats):
    """Interactively asks for this match's bowling numbers, then applies them."""
    print("\n--- Bowling Statistics ---")
    balls_this_match = get_overs_input("Overs Bowled")
    maidens = get_nonnegative_int("Maidens: ")
    runs_given = get_nonnegative_int("Runs Given: ")
    wickets = get_nonnegative_int("Wickets: ")
    wide_balls = get_nonnegative_int("Wide Balls: ")
    no_balls = get_nonnegative_int("No Balls: ")

    apply_bowling_stats(stats, balls_this_match, maidens, runs_given, wickets, wide_balls, no_balls)
    match_overs = balls_to_overs(balls_this_match)
    return wickets, match_overs


def apply_keeper_stats(stats, catches, stumpings, run_outs):
    """Pure calculation logic for wicket-keeping stats (see apply_batting_stats)."""
    stats["catches"] += catches
    stats["stumpings"] += stumpings
    stats["run_outs"] += run_outs


def record_keeper_stats(stats):
    """Interactively asks for this match's keeping numbers, then applies them."""
    print("\n--- Wicket Keeping Statistics ---")
    catches = get_nonnegative_int("Catches: ")
    stumpings = get_nonnegative_int("Stumpings: ")
    run_outs = get_nonnegative_int("Run Outs: ")

    apply_keeper_stats(stats, catches, stumpings, run_outs)


def update_player(data):
    """
    Handles the "Update Existing Player Statistics" menu option.
    Looks up the player by RFID, records this match's details, then
    asks for whichever statistics fit the player's role (Batsman,
    Bowler, All-Rounder, or Wicket Keeper), updates career totals with
    all the automatic calculations, and appends a permanent match
    history record that is never overwritten.
    """
    print_header("UPDATE PLAYER STATISTICS")

    rfid = get_nonempty_string("Enter RFID: ")

    if rfid not in data["players"]:
        print("\nPlayer not found.")
        return

    player = data["players"][rfid]
    stats = player["statistics"]
    # Backward-compatible: older saved players may not have this key yet.
    stats.setdefault("balls_bowled", 0)

    print(f"\nRecording a new match for {player['name']} ({player['role']}).")

    match_date = get_date_string("Match Date")
    opponent = get_nonempty_string("Opponent: ")
    venue = get_nonempty_string("Venue: ")
    tournament = get_nonempty_string("Tournament: ")
    match_type = get_choice_from_list("Select Match Type:", VALID_MATCH_TYPES)
    result = get_choice_from_list("Match Result:", VALID_RESULTS)

    # Every update represents one match played, regardless of role
    stats["matches"] += 1

    match_runs = 0
    match_balls = 0
    match_wickets = 0
    match_overs = 0.0
    role = player["role"]

    if role in ("Batsman", "All-Rounder", "Wicket Keeper"):
        match_runs, match_balls = record_batting_stats(stats)

    if role in ("Bowler", "All-Rounder"):
        match_wickets, match_overs = record_bowling_stats(stats)

    if role == "Wicket Keeper":
        record_keeper_stats(stats)

    # Permanent match history record -- appended, never overwritten
    stats["match_history"].append({
        "date": match_date,
        "opponent": opponent,
        "venue": venue,
        "tournament": tournament,
        "match_type": match_type,
        "runs": match_runs,
        "balls": match_balls,
        "wickets": match_wickets,
        "overs": match_overs,
        "result": result
    })

    save_data(data)
    print(f"\nStatistics updated successfully for {player['name']}.")


# ---------------------------------------------------------------
# SEARCH, TEAM/CAMPUS STATISTICS, LEADERBOARDS (PHASE 3)
# ---------------------------------------------------------------

def get_all_players(data):
    """Returns a plain list of every player record in the database."""
    return list(data["players"].values())


def print_player_row(player):
    """Prints one line of a player summary table."""
    print(f"{player['rfid']:<10} {player['name']:<20} {player['campus']:<8} {player['team']:<14} {player['role']}")


def search_player(data):
    """
    Handles the "Search Player" menu option.
    Lets the user search by RFID, Player Name, Team, Campus, or Role,
    and displays every matching player in a summary table.
    """
    print_header("SEARCH PLAYER")

    search_by = get_choice_from_list(
        "Search By:", ["RFID", "Player Name", "Team", "Campus", "Role"]
    )

    all_players = get_all_players(data)
    matches = []

    if search_by == "RFID":
        query = get_nonempty_string("Enter RFID: ")
        matches = [p for p in all_players if p["rfid"] == query]
    elif search_by == "Player Name":
        query = get_nonempty_string("Enter Player Name (or part of it): ").lower()
        matches = [p for p in all_players if query in p["name"].lower()]
    elif search_by == "Team":
        query = get_choice_from_list("Select Team:", VALID_TEAMS)
        matches = [p for p in all_players if p["team"] == query]
    elif search_by == "Campus":
        query = get_choice_from_list("Select Campus:", VALID_CAMPUSES)
        matches = [p for p in all_players if p["campus"] == query]
    elif search_by == "Role":
        query = get_choice_from_list("Select Role:", VALID_ROLES)
        matches = [p for p in all_players if p["role"] == query]

    if not matches:
        print("\nNo players found matching your search.")
        return

    print(f"\nFound {len(matches)} player(s):\n")
    print(f"{'RFID':<10} {'Name':<20} {'Campus':<8} {'Team':<14} {'Role'}")
    print("-" * 65)
    for player in matches:
        print_player_row(player)


def compute_team_stats(team, all_players):
    """
    Computes the summary statistics for one team.
    Returns a dictionary so both the on-screen display and the
    exported report can use the exact same calculation.
    """
    team_players = [p for p in all_players if p["team"] == team]
    total_runs = sum(p["statistics"]["runs"] for p in team_players)
    total_wickets = sum(p["statistics"]["wickets"] for p in team_players)

    if team_players:
        top_scorer = max(team_players, key=lambda p: p["statistics"]["runs"])
        top_wicket_taker = max(team_players, key=lambda p: p["statistics"]["wickets"])
        top_scorer_text = f"{top_scorer['name']} ({top_scorer['statistics']['runs']} runs)"
        top_wicket_text = f"{top_wicket_taker['name']} ({top_wicket_taker['statistics']['wickets']} wickets)"
    else:
        top_scorer_text = "N/A"
        top_wicket_text = "N/A"

    return {
        "team": team,
        "num_players": len(team_players),
        "total_runs": total_runs,
        "total_wickets": total_wickets,
        "top_scorer_text": top_scorer_text,
        "top_wicket_text": top_wicket_text,
    }


def compute_campus_stats(campus, all_players):
    """Computes the summary statistics for one campus (see compute_team_stats)."""
    campus_players = [p for p in all_players if p["campus"] == campus]
    num_players = len(campus_players)
    total_runs = sum(p["statistics"]["runs"] for p in campus_players)
    total_wickets = sum(p["statistics"]["wickets"] for p in campus_players)

    return {
        "campus": campus,
        "num_players": num_players,
        "total_runs": total_runs,
        "total_wickets": total_wickets,
        "avg_runs": round(total_runs / num_players, 2) if num_players else 0.0,
        "avg_wickets": round(total_wickets / num_players, 2) if num_players else 0.0,
    }


def get_leaderboard_sections(all_players):
    """
    Builds every leaderboard category as a list of
    (title, ranked_players, stat_getter) tuples. Used by both the
    on-screen leaderboards view and the exported report, so the
    ranking logic only has to be written once.
    """
    batted_players = [p for p in all_players if p["statistics"]["innings"] > 0]
    wicket_takers = [p for p in all_players if p["statistics"]["wickets"] > 0]
    bowlers_with_overs = [p for p in all_players if p["statistics"].get("balls_bowled", 0) > 0]

    return [
        ("Top Run Scorers",
         sorted(all_players, key=lambda p: p["statistics"]["runs"], reverse=True),
         lambda p: p["statistics"]["runs"]),
        ("Top Wicket Takers",
         sorted(all_players, key=lambda p: p["statistics"]["wickets"], reverse=True),
         lambda p: p["statistics"]["wickets"]),
        ("Highest Batting Average",
         sorted(batted_players, key=lambda p: p["statistics"]["batting_average"], reverse=True),
         lambda p: p["statistics"]["batting_average"]),
        ("Highest Strike Rate",
         sorted(batted_players, key=lambda p: p["statistics"]["strike_rate"], reverse=True),
         lambda p: p["statistics"]["strike_rate"]),
        ("Most Sixes",
         sorted(all_players, key=lambda p: p["statistics"]["sixes"], reverse=True),
         lambda p: p["statistics"]["sixes"]),
        ("Most Fours",
         sorted(all_players, key=lambda p: p["statistics"]["fours"], reverse=True),
         lambda p: p["statistics"]["fours"]),
        ("Best Bowling Average",
         sorted(wicket_takers, key=lambda p: p["statistics"]["bowling_average"]),
         lambda p: p["statistics"]["bowling_average"]),
        ("Best Economy",
         sorted(bowlers_with_overs, key=lambda p: p["statistics"]["economy"]),
         lambda p: p["statistics"]["economy"]),
    ]


def team_statistics(data):
    """
    Handles the "View Team Statistics" menu option.
    Shows player count, total runs, total wickets, and the top run
    scorer / wicket taker for each of the three teams.
    """
    print_header("TEAM STATISTICS")
    all_players = get_all_players(data)

    for team in VALID_TEAMS:
        info = compute_team_stats(team, all_players)
        print(f"\n--- {team} ---")
        print(f"Number of Players     : {info['num_players']}")
        print(f"Total Runs            : {info['total_runs']}")
        print(f"Total Wickets         : {info['total_wickets']}")
        print(f"Highest Run Scorer    : {info['top_scorer_text']}")
        print(f"Highest Wicket Taker  : {info['top_wicket_text']}")


def campus_statistics(data):
    """
    Handles the "View Campus Statistics" menu option.
    Shows total players, total runs/wickets, and per-player averages
    for each of the two campuses.
    """
    print_header("CAMPUS STATISTICS")
    all_players = get_all_players(data)

    for campus in VALID_CAMPUSES:
        info = compute_campus_stats(campus, all_players)
        print(f"\n--- {campus} ---")
        print(f"Total Players          : {info['num_players']}")
        print(f"Total Runs             : {info['total_runs']}")
        print(f"Total Wickets          : {info['total_wickets']}")
        print(f"Average Runs/Player    : {info['avg_runs']}")
        print(f"Average Wickets/Player : {info['avg_wickets']}")


def print_leaderboard_section(title, players_list, stat_getter, top_n=5):
    """Prints one ranked leaderboard section (or a 'no data' message)."""
    print(f"\n--- {title} ---")
    if not players_list:
        print("No data available.")
        return
    for rank, player in enumerate(players_list[:top_n], start=1):
        print(f"{rank}. {player['name']} ({player['team']}) - {stat_getter(player)}")


def leaderboards(data):
    """
    Handles the "Leaderboards" menu option.
    Automatically ranks players across eight different categories,
    sorted from best to worst (lowest is best for averages/economy).
    """
    print_header("LEADERBOARDS")
    all_players = get_all_players(data)

    if not all_players:
        print("\nNo players in the database yet.")
        return

    for title, ranked_players, stat_getter in get_leaderboard_sections(all_players):
        print_leaderboard_section(title, ranked_players, stat_getter)


# ---------------------------------------------------------------
# DELETE PLAYER (PHASE 4)
# ---------------------------------------------------------------

def delete_player(data):
    """
    Handles the "Delete Player" menu option.
    Requires an explicit Y/N confirmation before anything is removed,
    so a player is never deleted by accident.
    """
    print_header("DELETE PLAYER")

    rfid = get_nonempty_string("Enter RFID: ")

    if rfid not in data["players"]:
        print("\nPlayer not found.")
        return

    player_name = data["players"][rfid]["name"]
    print(f"\nYou are about to delete '{player_name}' (RFID {rfid}). This cannot be undone.")
    confirmation = get_yes_no("Are you sure?")

    if confirmation == "Y":
        del data["players"][rfid]
        save_data(data)
        print(f"\nPlayer '{player_name}' has been deleted.")
    else:
        print("\nDeletion cancelled. No changes were made.")


# ---------------------------------------------------------------
# EXPORT STATISTICS (PHASE 4)
# ---------------------------------------------------------------

def build_player_report_lines(player):
    """Builds the report lines for a single player's full profile."""
    stats = player["statistics"]
    lines = []
    lines.append("-" * 60)
    lines.append(f"RFID: {player['rfid']}  |  Name: {player['name']}")
    lines.append(f"Campus: {player['campus']}  |  Team: {player['team']}  |  Role: {player['role']}")
    lines.append(
        f"Jersey #: {player['jersey_number']}  |  Department: {player['department']}  |  "
        f"Joined: {player['date_joined']}"
    )
    lines.append(f"Batting Style: {player['batting_style']}  |  Bowling Style: {player['bowling_style']}")
    lines.append("")
    lines.append(
        f"Matches: {stats['matches']}  Innings: {stats['innings']}  Runs: {stats['runs']}  "
        f"Highest Score: {stats['highest_score']}"
    )
    lines.append(
        f"Balls Faced: {stats['balls_faced']}  Fours: {stats['fours']}  Sixes: {stats['sixes']}  "
        f"Outs: {stats['outs']}  Not Outs: {stats['not_outs']}"
    )
    lines.append(f"50s: {stats['fifties']}  100s: {stats['hundreds']}  Ducks: {stats['ducks']}")
    lines.append(
        f"Strike Rate: {stats['strike_rate']}  Batting Average: {stats['batting_average']}  "
        f"Boundary %: {stats['boundary_percentage']}  Runs/Match: {stats['runs_per_match']}"
    )
    lines.append(
        f"Overs: {stats['overs']}  Maidens: {stats['maidens']}  Runs Given: {stats['runs_given']}  "
        f"Wickets: {stats['wickets']}"
    )
    lines.append(
        f"Economy: {stats['economy']}  Bowling Average: {stats['bowling_average']}  "
        f"Bowling Strike Rate: {stats['bowling_strike_rate']}  Best Bowling: {stats['best_bowling']}"
    )
    lines.append(f"4-Wicket Hauls: {stats['four_wicket_hauls']}  5-Wicket Hauls: {stats['five_wicket_hauls']}")
    lines.append(f"Catches: {stats['catches']}  Stumpings: {stats['stumpings']}  Run Outs: {stats['run_outs']}")
    lines.append(f"Matches Recorded in History: {len(stats['match_history'])}")
    return lines


def build_full_report(data):
    """
    Builds the entire text report as one string: all players, team
    statistics, campus statistics, and leaderboards. Reuses the exact
    same computation helpers as the on-screen menu options, so the
    exported numbers always match what's shown in the program.
    """
    all_players = get_all_players(data)
    lines = []

    lines.append("=" * 60)
    lines.append("CEDAR COLLEGE CRICKET STATISTICS TRACKER - FULL REPORT")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 60)

    lines.append("\n\nALL PLAYERS")
    lines.append("=" * 60)
    if not all_players:
        lines.append("No players in the database.")
    for player in all_players:
        lines.append("")
        lines.extend(build_player_report_lines(player))

    lines.append("\n\nTEAM STATISTICS")
    lines.append("=" * 60)
    for team in VALID_TEAMS:
        info = compute_team_stats(team, all_players)
        lines.append(f"\n{team}:")
        lines.append(f"  Players: {info['num_players']}  Total Runs: {info['total_runs']}  "
                     f"Total Wickets: {info['total_wickets']}")
        lines.append(f"  Highest Run Scorer: {info['top_scorer_text']}")
        lines.append(f"  Highest Wicket Taker: {info['top_wicket_text']}")

    lines.append("\n\nCAMPUS STATISTICS")
    lines.append("=" * 60)
    for campus in VALID_CAMPUSES:
        info = compute_campus_stats(campus, all_players)
        lines.append(f"\n{campus}:")
        lines.append(f"  Total Players: {info['num_players']}  Total Runs: {info['total_runs']}  "
                     f"Total Wickets: {info['total_wickets']}")
        lines.append(f"  Average Runs/Player: {info['avg_runs']}  Average Wickets/Player: {info['avg_wickets']}")

    lines.append("\n\nLEADERBOARDS")
    lines.append("=" * 60)
    for title, ranked_players, stat_getter in get_leaderboard_sections(all_players):
        lines.append(f"\n{title}:")
        if not ranked_players:
            lines.append("  No data available.")
            continue
        for rank, player in enumerate(ranked_players[:5], start=1):
            lines.append(f"  {rank}. {player['name']} ({player['team']}) - {stat_getter(player)}")

    return "\n".join(lines)


def export_report(data):
    """
    Handles the "Export Statistics" menu option.
    Writes a full text report to cricket_report.txt. If this
    environment doesn't allow writing files (see save_data), the
    report is printed to the screen instead so nothing is lost.
    """
    print_header("EXPORT STATISTICS")
    report_text = build_full_report(data)

    try:
        with open("cricket_report.txt", "w") as report_file:
            report_file.write(report_text)
        print("\nReport successfully exported to 'cricket_report.txt'.")
    except PermissionError:
        print("\nThis environment does not allow saving files to disk, so the report")
        print("could not be written to 'cricket_report.txt'. Here it is instead:\n")
        print(report_text)


# ---------------------------------------------------------------
# MAIN MENU
# ---------------------------------------------------------------

def main_menu(data):
    """
    Displays the main menu in a loop until the user chooses Exit.
    """
    while True:
        print_header("MAIN MENU")
        print("1.  Add New Player")
        print("2.  Update Existing Player Statistics")
        print("3.  View Player Profile")
        print("4.  Search Player")
        print("5.  View Team Statistics")
        print("6.  View Campus Statistics")
        print("7.  Leaderboards")
        print("8.  Delete Player")
        print("9.  Export Statistics")
        print("10. Exit")

        choice = get_menu_choice(1, 10)

        if choice == 1:
            add_player(data)
        elif choice == 2:
            update_player(data)
        elif choice == 3:
            view_player(data)
        elif choice == 4:
            search_player(data)
        elif choice == 5:
            team_statistics(data)
        elif choice == 6:
            campus_statistics(data)
        elif choice == 7:
            leaderboards(data)
        elif choice == 8:
            delete_player(data)
        elif choice == 9:
            export_report(data)
        elif choice == 10:
            print("\nExiting program. All data has been saved. Goodbye!")
            break


# ---------------------------------------------------------------
# PROGRAM ENTRY POINT
# ---------------------------------------------------------------

def main():
    """
    The starting point of the program:
    1. Show the login screen.
    2. If login succeeds, load the data and show the main menu.
    3. If login fails, exit without touching the data.
    """
    if login():
        data = load_data()
        main_menu(data)
    else:
        print("\nToo many incorrect attempts. Exiting program.")


# This line makes sure main() only runs when this file is executed directly,
# which is exactly how Programiz will run it.
if __name__ == "__main__":
    main()
