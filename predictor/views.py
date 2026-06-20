import json

import pandas as pd
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from concurrent.futures import ThreadPoolExecutor

from .lichess_client import get_last_games, get_game_info
from .opening_loader import CANDIDATE_OPENINGS
from .feature_builder import build_feature_row
from .model_loader import (
    MODEL,
    PREPROCESS,
    # NUM_FEATURES,
    # CAT_FEATURES,
)


def home(request):
    return JsonResponse({"status": "DataGambit running"})


@csrf_exempt
def analyse(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    data = json.loads(request.body)
    row = pd.DataFrame([data])
    X = PREPROCESS.transform(row)
    probs = MODEL.predict_proba(X)[0]

    return JsonResponse({
        "black_win": float(probs[0]),
        "draw": float(probs[1]),
        "white_win": float(probs[2]),
    })


@csrf_exempt
def recommend(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    data = json.loads(request.body)
    game_id = data.get("game_id")
    white_username = data.get("white_username")
    black_username = data.get("black_username")
    white_elo = data.get("white_elo")
    black_elo = data.get("black_elo")
    time_control = data.get("time_control")
    for_color = data.get("for_color", "white").lower()
    for_username = data.get("for_username", "").strip()

    if game_id:
        try:
            game = get_game_info(game_id)
        except (requests.exceptions.RequestException, ValueError) as exc:
            return JsonResponse({
                "error": f"Failed to fetch game info from Lichess: {exc}"
            }, status=502)

        white_username = game["white_username"]
        black_username = game["black_username"]
        white_elo = game["white_elo"]
        black_elo = game["black_elo"]
        time_control = game["time_control"]

        if not white_username or not black_username:
            return JsonResponse({
                "error": "Could not read both Lichess usernames from this game"
            }, status=400)

        if for_username.lower() == white_username.lower():
            for_color = "white"
        elif for_username.lower() == black_username.lower():
            for_color = "black"
    else:
        if not all([white_username, black_username, white_elo, black_elo, time_control]):
            return JsonResponse({
                "error": "white_username, black_username, white_elo, black_elo, time_control required"
            }, status=400)

    try:
        with ThreadPoolExecutor(max_workers=2) as executor:
            white_future = executor.submit(get_last_games, white_username, 15)
            black_future = executor.submit(get_last_games, black_username, 15)

            white_games = white_future.result()
            black_games = black_future.result()
    except (requests.exceptions.RequestException, ValueError) as exc:
        return JsonResponse({
            "error": f"Failed to fetch player history from Lichess: {exc}"
        }, status=502)

    rows = []
    for op in CANDIDATE_OPENINGS:
        rows.append(
            build_feature_row(
                white_elo=float(white_elo),
                black_elo=float(black_elo),
                time_control=time_control,
                eco=op["eco"],
                opening=op["opening"],
                white_games=white_games,
                black_games=black_games,
                eco_global_rate=0.5,
            )
        )

    df = pd.DataFrame(rows)
    X = PREPROCESS.transform(df)
    probs = MODEL.predict_proba(X)

    class_to_idx = {int(c): i for i, c in enumerate(MODEL.classes_)}
    black_idx = class_to_idx[0]
    draw_idx = class_to_idx[1]
    white_idx = class_to_idx[2]

    scored = []
    for op, p in zip(CANDIDATE_OPENINGS, probs):
        black_win = float(p[black_idx])
        draw = float(p[draw_idx])
        white_win = float(p[white_idx])

        if for_color == "black":
            expected_score = black_win + 0.5 * draw
        else:
            expected_score = white_win + 0.5 * draw

        scored.append({
            "eco": op["eco"],
            "opening": op["opening"],
            "score": round(expected_score, 4),
        })

    scored.sort(key=lambda x: x["score"], reverse=True)

    unique_results = []
    seen_names = set()
    for item in scored:
        if item["opening"] not in seen_names:
            seen_names.add(item["opening"])
            unique_results.append({
                "opening": item["opening"],
                "score": item["score"],
            })
        if len(unique_results) == 3:
            break

    opponent_username = black_username if for_color == "white" else white_username
    return JsonResponse({
        "for_color": for_color,
        "opponent_username": opponent_username,
        "recommended": unique_results,
        "white_games_used": len(white_games),
        "black_games_used": len(black_games),
        "white_username": white_username,
        "black_username": black_username,
        "time_control": time_control,
    })
