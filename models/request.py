from datetime import datetime

from extensions import db


class DonationRequest(db.Model):
    __tablename__ = "donation_requests"

    STATUS_PENDING = "Pending"
    STATUS_ACCEPTED = "Accepted"
    STATUS_REJECTED = "Rejected"
    STATUS_CANCELLED = "Cancelled"

    id = db.Column(db.Integer, primary_key=True)
    donation_id = db.Column(db.Integer, db.ForeignKey("food_donations.id"), nullable=False)
    ngo_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    requested_quantity = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=False, default=STATUS_PENDING)
    requested_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
