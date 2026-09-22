import os
import sqlite3

DATABASE = "database/restaurant.db"


def get_db_connection():
    os.makedirs("database", exist_ok=True)

    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row

    return connection


def create_tables():
    connection = get_db_connection()
    cursor = connection.cursor()

    # -----------------------------
    # Restaurants table
    # -----------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS restaurants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT NOT NULL,
            latitude REAL,
            longitude REAL,
            total_tables INTEGER NOT NULL,
            average_stay_minutes INTEGER DEFAULT 30
        )
    """)

    # -----------------------------
    # Owners table
    # -----------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS owners (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            restaurant_id INTEGER
        )
    """)

    # -----------------------------
    # Crowd updates table
    # -----------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS crowd_updates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            restaurant_id INTEGER NOT NULL,
            people_inside INTEGER NOT NULL,
            people_entered INTEGER DEFAULT 0,
            people_left INTEGER DEFAULT 0,
            occupied_tables INTEGER NOT NULL,
            available_tables INTEGER NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (restaurant_id)
            REFERENCES restaurants(id)
        )
    """)

    connection.commit()
    connection.close()


if __name__ == "__main__":
    create_tables()
    print("Database and tables created successfully!")