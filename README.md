# DataGambit

DataGambit is a Chrome extension for Lichess that recommends openings before a game starts.

It analyzes recent games of both players and uses a machine learning model trained on over 6 million chess games to suggest openings with the highest winrate.

## Extension Setup

1. Clone this repository.

2. Open Chrome and go to:

```text
chrome://extensions/
```

3. Enable **Developer mode**.

4. Click **Load unpacked**.

5. Select the `extension/` folder.

6. Open a Lichess game and click the DataGambit extension icon.

By default, the extension uses the deployed backend API.

## Local Backend Setup

Use this only if you want to run the backend locally.

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the Django server:

```bash
python manage.py runserver
```

The local API will start at:

```text
http://127.0.0.1:8000
```

To use the local backend, update the API URL inside `extension/popup.js`:

```js
const API_URL = "http://127.0.0.1:8000/recommend/";
```

Then reload the extension from `chrome://extensions/`.

## Notes

The backend may take a few seconds to respond if the deployed server is sleeping.
