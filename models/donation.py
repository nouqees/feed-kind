from datetime import datetime

from extensions import db


class FoodDonation(db.Model):
    __tablename__ = "food_donations"

    STATUS_AVAILABLE = "Available"
    STATUS_RESERVED = "Reserved"
    STATUS_COMPLETED = "Completed"
    STATUS_CANCELLED = "Cancelled"

    id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    food_name = db.Column(db.String(120), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("food_categories.id"), nullable=False)
    quantity = db.Column(db.String(50), nullable=False)
    prepared_at = db.Column(db.DateTime, nullable=False)
    available_until = db.Column(db.DateTime, nullable=False)
    pickup_location = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    image_path = db.Column(db.String(255))
    status = db.Column(db.String(20), nullable=False, default=STATUS_AVAILABLE)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    category = db.relationship("FoodCategory")
    requests = db.relationship("DonationRequest", backref="donation", lazy=True)
