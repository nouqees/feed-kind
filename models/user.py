from datetime import datetime

from extensions import db


class User(db.Model):
    __tablename__ = "users"

    ROLE_ADMIN = "ADMIN"
    ROLE_DONOR = "DONOR"
    ROLE_NGO = "NGO"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    role = db.Column(db.String(10), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    donations = db.relationship(
        "FoodDonation", backref="donor", lazy=True, foreign_keys="FoodDonation.donor_id"
    )
    requests = db.relationship(
        "DonationRequest", backref="ngo", lazy=True, foreign_keys="DonationRequest.ngo_id"
    )
