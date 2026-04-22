# Greeniya Medicinal Plants Project

A Flask-based medicinal plants knowledge hub with searchable plant data, category browsing, and a bundled SQLite database.

## Features

- Search plants, families, groups, categories, types, and crown architecture
- Browse 500+ medicinal plant records from the included SQLite database
- Plant detail modal with descriptions and taxonomy data
- Automatic fallback placeholder for missing plant images

## Run locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`.

## Files

- `app.py`: main Flask app
- `plants.db`: SQLite database
- `templates/`: HTML templates
- `static/`: CSS, JavaScript, and images
- `scrape_plants.py`: scraper utility

## Notes

- Many plant records reference images that are not present locally. The app now uses a safe inline placeholder so the UI stays stable.
- There is also a nested duplicate folder named `vijayfinalpro/` inside the project. Review that before publishing so you do not upload duplicate content by mistake.
