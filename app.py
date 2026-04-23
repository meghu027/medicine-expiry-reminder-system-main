from __future__ import annotations

import csv
import os
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET_PATH = REPO_ROOT / "medicine_dataset.csv"
FRONTEND_DIR = REPO_ROOT / "frontend"


def _parse_iso_date(value: str) -> Optional[date]:
    value = (value or "").strip()
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def _to_int(value: str) -> Optional[int]:
    value = (value or "").strip()
    if not value:
        return None
    try:
        return int(value)
    except ValueError:
        return None


@dataclass(frozen=True)
class Medicine:
    medicine_name: str
    category: str
    batch_number: str
    manufacturing_date: Optional[date]
    expiry_date: Optional[date]
    quantity: Optional[int]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "medicine_name": self.medicine_name,
            "category": self.category,
            "batch_number": self.batch_number,
            "manufacturing_date": self.manufacturing_date.isoformat()
            if self.manufacturing_date
            else None,
            "expiry_date": self.expiry_date.isoformat() if self.expiry_date else None,
            "quantity": self.quantity,
            "days_to_expiry": (self.expiry_date - date.today()).days
            if self.expiry_date
            else None,
        }


def load_medicines(csv_path: Path) -> List[Medicine]:
    medicines: List[Medicine] = []
    if not csv_path.exists():
        return medicines

    with csv_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Skip completely empty rows
            if not row or not any((v or "").strip() for v in row.values()):
                continue

            medicines.append(
                Medicine(
                    medicine_name=(row.get("Medicine Name") or "").strip(),
                    category=(row.get("Category") or "").strip(),
                    batch_number=(row.get("Batch Number") or "").strip(),
                    manufacturing_date=_parse_iso_date(row.get("Manufacturing Date") or ""),
                    expiry_date=_parse_iso_date(row.get("Expiry Date") or ""),
                    quantity=_to_int(row.get("Quantity") or ""),
                )
            )
    return medicines


def create_app() -> Flask:
    app = Flask(__name__)

    # Allow your static HTML pages (and any local dev origin) to call the API.
    CORS(app)

    dataset_path = Path(os.environ.get("MEDICINE_DATASET", str(DEFAULT_DATASET_PATH)))

    @app.get("/api/health")
    def health():
        return jsonify(
            {
                "ok": True,
                "dataset": str(dataset_path),
            }
        )

    @app.get("/api/medicines")
    def list_medicines():
        medicines = load_medicines(dataset_path)

        category = (request.args.get("category") or "").strip()
        q = (request.args.get("q") or "").strip().lower()

        if category:
            medicines = [m for m in medicines if m.category.lower() == category.lower()]
        if q:
            medicines = [
                m
                for m in medicines
                if q in m.medicine_name.lower() or q in m.batch_number.lower()
            ]

        return jsonify([m.to_dict() for m in medicines])

    @app.get("/api/medicines/expiring")
    def expiring_soon():
        days = request.args.get("days", default="30")
        try:
            days_int = int(days)
        except ValueError:
            return jsonify({"error": "days must be an integer"}), 400

        today = date.today()
        medicines = [
            m
            for m in load_medicines(dataset_path)
            if m.expiry_date is not None and 0 <= (m.expiry_date - today).days <= days_int
        ]
        medicines.sort(key=lambda m: (m.expiry_date or date.max, m.medicine_name))
        return jsonify([m.to_dict() for m in medicines])

    @app.post("/api/notifications/send-expiry-alert")
    def send_expiry_alert():
        """
        Send expiry notification email to user
        """
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400
            
            user_email = data.get("email")
            if not user_email:
                return jsonify({"error": "Email is required"}), 400
            
            # Get expired medicines (including already expired)
            today = date.today()
            expired_medicines = [
                m.to_dict()
                for m in load_medicines(dataset_path)
                if m.expiry_date is not None and (m.expiry_date - today).days <= 0
            ]
            
            if not expired_medicines:
                return jsonify({
                    "message": "No expired medicines found",
                    "expired_count": 0
                }), 200
            
            # Send email notification
            email_sent = send_expiry_notification_email(user_email, expired_medicines)
            
            if email_sent:
                return jsonify({
                    "message": f"Expiry alert sent successfully to {user_email}",
                    "expired_count": len(expired_medicines),
                    "expired_medicines": expired_medicines
                }), 200
            else:
                return jsonify({
                    "error": "Failed to send email notification"
                }), 500
                
        except Exception as e:
            return jsonify({"error": f"Internal server error: {str(e)}"}), 500

    @app.get("/api/medicines/expired")
    def get_expired_medicines():
        """
        Get all expired medicines
        """
        today = date.today()
        expired_medicines = [
            m.to_dict()
            for m in load_medicines(dataset_path)
            if m.expiry_date is not None and (m.expiry_date - today).days <= 0
        ]
        expired_medicines.sort(key=lambda m: (m.get('expiry_date', ''), m.get('medicine_name', '')))
        return jsonify(expired_medicines)

    # Optional: serve your existing frontend HTML through Flask
    @app.get("/")
    def index():
        if FRONTEND_DIR.exists():
            return send_from_directory(FRONTEND_DIR, "login.html")
        return jsonify({"message": "Frontend not found"}), 404

    @app.get("/<path:filename>")
    def frontend_files(filename: str):
        if not FRONTEND_DIR.exists():
            return jsonify({"message": "Frontend not found"}), 404
        return send_from_directory(FRONTEND_DIR, filename)

    return app


app = create_app()


if __name__ == "__main__":
    # Use 0.0.0.0 so it's reachable on LAN if needed.
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=True)
