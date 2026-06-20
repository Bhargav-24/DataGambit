
def parse_time_control(tc):
    if not tc or tc == "Unknown":
        return 0, 0, "unknown"

    base = tc
    inc = "0"

    if "+" in tc:
        base, inc = tc.split("+", 1)

    try:
        base_sec = float(base)
    except ValueError:
        base_sec = 0

    try:
        inc_sec = float(inc)
    except ValueError:
        inc_sec = 0

    if base_sec <= 180:
        bucket = "bullet"
    elif base_sec <= 600:
        bucket = "blitz"
    elif base_sec <= 1800:
        bucket = "rapid"
    else:
        bucket = "classical"

    return base_sec, inc_sec, bucket


def eco_mastery(games, eco):
    scores = [g["score"] for g in games if g["eco"] == eco]

    if not scores:
        return 0.5

    return (sum(scores) + 1.0) / (len(scores) + 2.0)


def build_feature_row(
    white_elo,
    black_elo,
    time_control,
    eco,
    opening,
    white_games,
    black_games,
    eco_global_rate=0.5,
):
    base_sec, inc_sec, time_bucket = parse_time_control(time_control)

    white_adj_elo = white_elo + (white_elo / 1000.0) * 20.0
    elo_d = white_adj_elo - black_elo
    avg_e = (white_adj_elo + black_elo) / 2.0

    w_eco = eco_mastery(white_games, eco)
    b_eco = eco_mastery(black_games, eco)

    return {
        "WhiteElo": white_elo,
        "BlackElo": black_elo,
        "WhiteAdjElo": white_adj_elo,
        "EloD": elo_d,
        "AvgE": avg_e,
        "BaseSec": base_sec,
        "IncSec": inc_sec,
        "EcoGlobalRate": eco_global_rate,
        "W_ECO12": w_eco,
        "B_ECO12": b_eco,
        "MGap": w_eco - b_eco,
        "TimeBucket": time_bucket,
        "ECO": eco,
        "Opening": opening,
    }