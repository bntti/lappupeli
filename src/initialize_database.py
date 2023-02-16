from sqlalchemy.sql import text

from app import create_app
from database import database

app = create_app()
app.app_context().push()


def initialize_database():
    with open("schema.sql", "r", encoding="utf8") as schema_file:
        schema = schema_file.readlines()

    database.session.execute(text("".join(schema)))
    database.session.commit()


if __name__ == "__main__":
    initialize_database()
