# Apex Autohaus — Backend (Project 3: Database Integration)

Flask + SQLAlchemy backend for the Apex Autohaus car showroom frontend,
with full CRUD operations and a relational schema (PostgreSQL by default,
SQLite fallback for zero-setup testing).

## Project Structure

```
apex_autohaus_backend/
├── app.py            # Flask app, routes, seed data
├── models.py         # Car & Booking models (schema, constraints, FK relationship)
├── extensions.py      # SQLAlchemy instance
├── config.py          # Database configuration
├── requirements.txt
├── static/
│   ├── index.html
│   ├── styles.css
│   └── script.js       # Now fetches car data from the API instead of hardcoded HTML
└── README.md
```

## Database Schema

**cars**
| column       | type    | constraints                  |
|--------------|---------|-------------------------------|
| id           | Integer | Primary Key                   |
| brand        | String  | NOT NULL                      |
| name         | String  | NOT NULL, UNIQUE               |
| description  | Text    |                                 |
| price        | Integer | NOT NULL, CHECK (price > 0)    |
| horsepower   | Integer | NOT NULL, CHECK (horsepower > 0) |
| image_url    | String  |                                 |
| category     | String  | NOT NULL                       |

**bookings**
| column      | type     | constraints                          |
|-------------|----------|----------------------------------------|
| id          | Integer  | Primary Key                            |
| name        | String   | NOT NULL                               |
| email       | String   | NOT NULL                               |
| message     | Text     |                                          |
| created_at  | DateTime | default: now                            |
| car_id      | Integer  | Foreign Key → cars.id, NOT NULL          |

Relationship: **one Car → many Bookings** (a car can receive multiple test-drive requests).

## Setup

1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Database options:**

   **Option A — SQLite (default, zero setup)**
   Just run the app — a local `apex_autohaus.db` file is created automatically.

   **Option B — PostgreSQL**
   Create a database first:
   ```sql
   CREATE DATABASE apex_autohaus;
   ```
   Then set the environment variable before running:
   ```bash
   export DATABASE_URL="postgresql://username:password@localhost:5432/apex_autohaus"
   ```

3. Run the app:
   ```bash
   python app.py
   ```
   Visit `http://127.0.0.1:5000` — the showroom loads with 10 seeded cars pulled live from the database.

## API Endpoints

| Method | Endpoint              | Description                          |
|--------|------------------------|----------------------------------------|
| GET    | /api/cars              | List all cars (supports `?category=` and `?search=`) |
| GET    | /api/cars/<id>          | Get a single car                        |
| POST   | /api/cars              | Create a new car                        |
| PUT    | /api/cars/<id>          | Update an existing car                  |
| DELETE | /api/cars/<id>          | Delete a car                            |
| POST   | /api/bookings           | Submit a test-drive / visit request     |
| GET    | /api/bookings           | List all booking requests               |
| DELETE | /api/bookings/<id>      | Delete a booking                        |

### Example: create a car
```bash
curl -X POST http://127.0.0.1:5000/api/cars \
  -H "Content-Type: application/json" \
  -d '{
    "brand": "Aston Martin",
    "name": "Aston Martin Vantage",
    "description": "British grand tourer with V8 punch.",
    "price": 142000,
    "horsepower": 503,
    "category": "supercar",
    "image_url": "https://example.com/vantage.jpg"
  }'
```

### Example: submit a booking
```bash
curl -X POST http://127.0.0.1:5000/api/bookings \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Ayesha Waheed",
    "email": "ayesha@example.com",
    "model": "Audi R8 V10",
    "message": "Interested in a Saturday visit."
  }'
```

## Notes on Security

All queries go through SQLAlchemy's ORM, which uses parameterized queries
under the hood — raw string concatenation is never used, so this backend
is not vulnerable to SQL injection in the way covered in the Project 3 slides.
