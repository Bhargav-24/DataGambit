import pandas as pd
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .model_loader import (
    MODEL,
    PREPROCESS,
    NUM_FEATURES,
    CAT_FEATURES
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