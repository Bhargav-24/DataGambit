# DataGambit

DataGambit is a Chrome extension for Lichess that recommends openings before a game starts.

The system analyzes recent games of both players and uses a machine learning model trained on over 6 million chess games to suggest openings with the highest winrate.

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the backend:

```bash
python manage.py runserver
```

The API will start on:

```text
http://127.0.0.1:8000
```

Load the Chrome extension and open a Lichess game to get opening recommendations.
