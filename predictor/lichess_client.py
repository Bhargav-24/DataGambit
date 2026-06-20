import json
import requests


def get_last_games(username, max_games=15):
    url = f"https://lichess.org/api/games/user/{username}"

    params = {
        "max": max_games,
        "opening": "true",
        "pgnInJson": "false",
        "clocks": "true",
        "evals": "false",
    }

    headers = {
        "Accept": "application/x-ndjson"
    }

    res = requests.get(url, params=params, headers=headers, timeout=10)
    res.raise_for_status()

    games = []

    for line in res.text.strip().splitlines():
        if not line.strip():
            continue

        raw = json.loads(line)
        parsed = parse_game(raw, username)

        if parsed is not None:
            games.append(parsed)

    return games


def parse_game(game, username):
    username = username.lower()

    players = game.get("players", {})
    white = players.get("white", {})
    black = players.get("black", {})

    white_user = white.get("user", {}).get("name", "").lower()
    black_user = black.get("user", {}).get("name", "").lower()

    if username == white_user:
        color = "white"
        player_rating = white.get("rating")
        opponent_rating = black.get("rating")
    elif username == black_user:
        color = "black"
        player_rating = black.get("rating")
        opponent_rating = white.get("rating")
    else:
        return None

    opening = game.get("opening", {})
    eco = opening.get("eco", "Unknown")
    opening_name = opening.get("name", "Unknown")

    winner = game.get("winner")

    if winner is None:
        score = 0.5
    elif winner == color:
        score = 1.0
    else:
        score = 0.0

    clock = game.get("clock", {})
    base = clock.get("initial")
    inc = clock.get("increment")

    if base is not None and inc is not None:
        time_control = f"{base}+{inc}"
    else:
        time_control = "Unknown"

    return {
        "eco": eco,
        "opening": opening_name,
        "color": color,
        "score": score,
        "player_rating": player_rating,
        "opponent_rating": opponent_rating,
        "time_control": time_control,
    }

def get_game_info(game_id):
    url = f"https://lichess.org/game/export/{game_id}"

    params = {
        "opening": "true",
        "clocks": "true",
        "evals": "false",
    }

    headers = {
        "Accept": "application/json"
    }

    res = requests.get(url, params=params, headers=headers, timeout=10)
    res.raise_for_status()

    game = res.json()

    players = game.get("players", {})
    white = players.get("white", {})
    black = players.get("black", {})

    white_username = white.get("user", {}).get("name")
    black_username = black.get("user", {}).get("name")

    white_elo = white.get("rating", 1500)
    black_elo = black.get("rating", 1500)

    clock = game.get("clock", {})
    base = clock.get("initial")
    inc = clock.get("increment")

    if base is not None and inc is not None:
        time_control = f"{base}+{inc}"
    else:
        time_control = "180+0"

    return {
        "white_username": white_username,
        "black_username": black_username,
        "white_elo": white_elo,
        "black_elo": black_elo,
        "time_control": time_control,
    }