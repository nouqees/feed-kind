from extensions import db


class FoodCategory(db.Model):
    __tablename__ = "food_categories"

    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(50), unique=True, nullable=False)
