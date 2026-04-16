from app import create_app
from database import database
from sqlalchemy.sql import text

app = create_app()
app.app_context().push()


def initialize_database() -> None:
    with open("schema.sql") as schema_file:
        schema = schema_file.readlines()

    database.session.execute(text("".join(schema)))
    database.session.commit()


if __name__ == "__main__":
    initialize_database()
