from datetime import datetime

from extensions import db


class DonationHistory(db.Model):
    __tablename__ = "donation_history"

    id = db.Column(db.Integer, primary_key=True)
    donation_id = db.Column(db.Integer, db.ForeignKey("food_donations.id"), nullable=False, unique=True)
    request_id = db.Column(db.Integer, db.ForeignKey("donation_requests.id"), nullable=False, unique=True)
    completed_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    remarks = db.Column(db.Text)

    donation = db.relationship("FoodDonation")
    request = db.relationship("DonationRequest")
