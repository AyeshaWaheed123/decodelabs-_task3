from flask import Flask, request, jsonify, send_from_directory
from sqlalchemy.exc import IntegrityError

from config import Config
from extensions import db
from models import Car, Booking

app = Flask(__name__, static_folder="static", static_url_path="")
app.config.from_object(Config)
db.init_app(app)


# ---------------------------------------------------------------------------
# Frontend routes (serves the existing HTML/CSS/JS as-is)
# ---------------------------------------------------------------------------
@app.route("/")
def home():
    return send_from_directory(app.static_folder, "index.html")


# ---------------------------------------------------------------------------
# CARS — full CRUD
# ---------------------------------------------------------------------------
@app.route("/api/cars", methods=["GET"])
def get_cars():
    """READ (list) — supports optional ?category= and ?search= filters."""
    query = Car.query

    category = request.args.get("category")
    if category and category != "all":
        query = query.filter(Car.category == category)

    search = request.args.get("search")
    if search:
        like = f"%{search}%"
        query = query.filter(
            db.or_(Car.name.ilike(like), Car.brand.ilike(like))
        )

    cars = query.order_by(Car.id).all()
    return jsonify([car.to_dict() for car in cars]), 200


@app.route("/api/cars/<int:car_id>", methods=["GET"])
def get_car(car_id):
    """READ (single)."""
    car = Car.query.get(car_id)
    if not car:
        return jsonify({"error": "Car not found"}), 404
    return jsonify(car.to_dict()), 200


@app.route("/api/cars", methods=["POST"])
def create_car():
    """CREATE."""
    data = request.get_json(silent=True) or {}

    required_fields = ["brand", "name", "price", "horsepower", "category"]
    missing = [f for f in required_fields if f not in data or data[f] in (None, "")]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    car = Car(
        brand=data["brand"],
        name=data["name"],
        description=data.get("description"),
        price=data["price"],
        horsepower=data["horsepower"],
        image_url=data.get("image_url"),
        category=data["category"],
    )

    try:
        db.session.add(car)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "A car with this name already exists, or a constraint was violated"}), 409

    return jsonify(car.to_dict()), 201


@app.route("/api/cars/<int:car_id>", methods=["PUT"])
def update_car(car_id):
    """UPDATE."""
    car = Car.query.get(car_id)
    if not car:
        return jsonify({"error": "Car not found"}), 404

    data = request.get_json(silent=True) or {}

    for field in ["brand", "name", "description", "price", "horsepower", "image_url", "category"]:
        if field in data:
            setattr(car, field, data[field])

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Update violates a database constraint"}), 409

    return jsonify(car.to_dict()), 200


@app.route("/api/cars/<int:car_id>", methods=["DELETE"])
def delete_car(car_id):
    """DELETE."""
    car = Car.query.get(car_id)
    if not car:
        return jsonify({"error": "Car not found"}), 404

    db.session.delete(car)
    db.session.commit()
    return jsonify({"message": f"Car {car_id} deleted"}), 200


# ---------------------------------------------------------------------------
# BOOKINGS — created from the contact/test-drive form
# ---------------------------------------------------------------------------
@app.route("/api/bookings", methods=["POST"])
def create_booking():
    """CREATE a booking. Expects car_id OR car name via 'model'."""
    data = request.get_json(silent=True) or {}

    required_fields = ["name", "email"]
    missing = [f for f in required_fields if f not in data or not data[f]]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    car = None
    if data.get("car_id"):
        car = Car.query.get(data["car_id"])
    elif data.get("model"):
        car = Car.query.filter_by(name=data["model"]).first()

    if not car:
        return jsonify({"error": "A valid car (car_id or model name) is required"}), 400

    booking = Booking(
        name=data["name"],
        email=data["email"],
        message=data.get("message"),
        car_id=car.id,
    )
    db.session.add(booking)
    db.session.commit()

    return jsonify(booking.to_dict()), 201


@app.route("/api/bookings", methods=["GET"])
def get_bookings():
    """READ (list) — simple admin view of all booking requests."""
    bookings = Booking.query.order_by(Booking.created_at.desc()).all()
    return jsonify([b.to_dict() for b in bookings]), 200


@app.route("/api/bookings/<int:booking_id>", methods=["DELETE"])
def delete_booking(booking_id):
    """DELETE a booking."""
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({"error": "Booking not found"}), 404

    db.session.delete(booking)
    db.session.commit()
    return jsonify({"message": f"Booking {booking_id} deleted"}), 200


# ---------------------------------------------------------------------------
# Seed data (runs once if the cars table is empty)
# ---------------------------------------------------------------------------
def seed_cars():
    if Car.query.first():
        return

    cars = [
        Car(brand="Audi", name="Audi R8 V10", category="audi", price=158000, horsepower=602,
            description="V10 coupe, quattro grip, carbon interior and track-inspired cockpit.",
            image_url="https://images.unsplash.com/photo-1542362567-b07e54358753?auto=format&fit=crop&w=900&q=80"),
        Car(brand="BMW", name="BMW M4 Competition", category="bmw", price=84000, horsepower=503,
            description="Twin-turbo power, sharp steering and daily comfort with M performance.",
            image_url="https://images.unsplash.com/photo-1556189250-72ba954cfc2b?auto=format&fit=crop&w=900&q=80"),
        Car(brand="Porsche", name="Porsche 911 Carrera", category="supercar", price=116000, horsepower=379,
            description="Rear-engine balance, timeless design and responsive grand touring feel.",
            image_url="https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=900&q=80"),
        Car(brand="AMG", name="Mercedes-AMG GT", category="supercar", price=132000, horsepower=523,
            description="Long-hood coupe with premium cabin materials and serious acceleration.",
            image_url="https://images.unsplash.com/photo-1617814076367-b759c7d7e738?auto=format&fit=crop&w=900&q=80"),
        Car(brand="Ferrari", name="Ferrari F8 Tributo", category="supercar", price=276000, horsepower=710,
            description="Mid-engine supercar with razor-sharp handling and dramatic Italian styling.",
            image_url="https://images.unsplash.com/photo-1592198084033-aade902d1aae?auto=format&fit=crop&w=900&q=80"),
        Car(brand="Lamborghini", name="Lamborghini Huracan", category="supercar", price=248000, horsepower=631,
            description="V10 excitement, low stance and aggressive performance for weekend drives.",
            image_url="https://images.unsplash.com/photo-1511919884226-fd3cad34687c?auto=format&fit=crop&w=900&q=80"),
        Car(brand="Tesla", name="Tesla Model S Plaid", category="electric", price=91000, horsepower=1020,
            description="Electric luxury sedan with instant torque, clean cabin and extreme speed.",
            image_url="https://images.unsplash.com/photo-1617788138017-80ad40651399?auto=format&fit=crop&w=900&q=80"),
        Car(brand="Ford", name="Ford Mustang GT", category="muscle", price=48000, horsepower=486,
            description="Classic American V8 muscle with bold design and strong road presence.",
            image_url="https://images.unsplash.com/photo-1584345604476-8ec5e12e42dd?auto=format&fit=crop&w=900&q=80"),
        Car(brand="Nissan", name="Nissan GT-R Nismo", category="supercar", price=215000, horsepower=600,
            description="All-wheel-drive icon with race-bred tuning and explosive acceleration.",
            image_url="https://images.unsplash.com/photo-1600712242805-5f78671b24da?auto=format&fit=crop&w=900&q=80"),
        Car(brand="McLaren", name="McLaren 720S", category="supercar", price=305000, horsepower=710,
            description="Lightweight carbon construction, twin-turbo power and futuristic cabin.",
            image_url="https://images.unsplash.com/photo-1621135802920-133df287f89c?auto=format&fit=crop&w=900&q=80"),
    ]
    db.session.bulk_save_objects(cars)
    db.session.commit()
    print(f"Seeded {len(cars)} cars into the database.")


with app.app_context():
    db.create_all()
    seed_cars()


if __name__ == "__main__":
    app.run(debug=True, port=5000)
