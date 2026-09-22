from database import create_tables, get_db_connection

create_tables()

connection = get_db_connection()

existing = connection.execute("""
    SELECT id
    FROM restaurants
    WHERE name = ?
""", ("Food Palace",)).fetchone()

if existing:
    print("Food Palace already exists.")
else:
    connection.execute("""
        INSERT INTO restaurants
        (
            name,
            address,
            latitude,
            longitude,
            total_tables,
            average_stay_minutes
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        "Food Palace",
        "Bhilai, Chhattisgarh",
        21.1938,
        81.3509,
        15,
        45
    ))

    connection.commit()
    print("Restaurant added successfully!")

connection.close()