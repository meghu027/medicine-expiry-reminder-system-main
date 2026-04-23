# Flask backend (Medicine Expiry Reminder)

## What this adds

- A Flask API that reads `medicine_dataset.csv`
- JSON endpoints:
  - `GET /api/health`
  - `GET /api/medicines` (optional query params: `q`, `category`)
  - `GET /api/medicines/expiring?days=30`
- CORS enabled so your static `frontend/*.html` pages can call the API
- Optional serving of the frontend from Flask:
  - `GET /` serves `frontend/login.html`
  - `GET /<file>` serves files from `frontend/`

## Run on Windows (PowerShell)

From the project root (`medicine-expiry-reminder-system-main`):

```powershell
cd .\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

Then open:

- API health: `http://localhost:5000/api/health`
- Medicines: `http://localhost:5000/api/medicines`
- Expiring soon: `http://localhost:5000/api/medicines/expiring?days=30`
- Frontend (served by Flask): `http://localhost:5000/`

## Dataset path (optional)

By default, it reads `../medicine_dataset.csv`.
To override:

```powershell
$env:MEDICINE_DATASET="C:\full\path\to\your.csv"
python app.py
```
