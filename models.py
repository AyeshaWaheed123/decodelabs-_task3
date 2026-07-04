from datetime import datetime
from extensions import db


class Car(db.Model):
    """
    Represents a single vehicle in the showroom inventory.
    Matches the car cards shown on the frontend (index.html).
    """
    __tablename__ = "cars"

    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(120), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Integer, nullable=False)          # stored in USD
    horsepower = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(500), nullable=True)
    category = db.Column(db.String(30), nullable=False)    # audi, bmw, supercar, muscle, electric

    __table_args__ = (
        db.CheckConstraint('price > 0', name='check_price_positive'),
        db.CheckConstraint('horsepower > 0', name='check_hp_positive'),
    )

    # One car can appear in many booking/test-drive requests
    bookings = db.relationship(
        "Booking",
        backref="car",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "brand": self.brand,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "horsepower": self.horsepower,
            "image_url": self.image_url,
            "category": self.category,
        }


class Booking(db.Model):
    """
    Represents a showroom visit / test-drive request submitted
    through the contact form on the frontend.
    """
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Foreign key -> links each booking to exactly one car (Preferred Model)
    car_id = db.Column(db.Integer, db.ForeignKey("cars.id"), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "message": self.message,
            "created_at": self.created_at.isoformat(),
            "car_id": self.car_id,
            "car_name": self.car.name if self.car else None,
        }
