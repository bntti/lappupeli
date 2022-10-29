# Lappupeli

A game in Finnish written with Python using Flask.
[Link to the website](https://lappupeli.motsgar.fi/)

## Running the project

### Initialization

1. Create a `.env` file and add the following lines to it

   ```
   SECRET_KEY=<secret_key>
   DATABASE_URL=<postgresql:///database_name>
   ```

   Where `<secret_key>` is a secret key and `<postgresql:///database_name>` is the database url.

2. Install the dependencies and initialize the database
   ```
   $ poetry install
   $ poetry run invoke initialize-database
   ```

### Running the project

```
$ poetry run invoke start
```
