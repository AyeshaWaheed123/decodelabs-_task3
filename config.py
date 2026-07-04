import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Reads DATABASE_URL from environment if set (PostgreSQL),
    # otherwise falls back to a local SQLite file so the project
    # runs out of the box with zero setup.
    #
    # To use PostgreSQL, set an environment variable before running:
    #   export DATABASE_URL="postgresql://username:password@localhost:5432/apex_autohaus"
    #
    # Example on Windows (cmd):
    #   set DATABASE_URL=postgresql://username:password@localhost:5432/apex_autohaus

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(BASE_DIR, 'apex_autohaus.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False
