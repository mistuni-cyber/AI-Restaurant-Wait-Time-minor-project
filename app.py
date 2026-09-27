from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    url_for
)
from database import create_tables, get_db_connection
from ml.model import (
    get_crowd_level,
    get_recommendation,
    predict_wait_time
)

app = Flask(__name__)
app.secret_key = "restaurant-ai-demo-secret"

create_tables()


# =========================================================
# HOME PAGE
# =========================================================
# =========================================================
# HOME PAGE
# =========================================================
@app.route("/")
def index():
    connection = get_db_connection()
    
    # 1. Get all restaurants
    restaurants = connection.execute("SELECT * FROM restaurants ORDER BY name").fetchall()
    
    restaurant_data = []

    for restaurant in restaurants:
        # 2. Get the latest crowd update for this specific restaurant
        latest = connection.execute("""
            SELECT * FROM crowd_updates 
            WHERE restaurant_id = ? 
            ORDER BY timestamp DESC LIMIT 1
        """, (restaurant["id"],)).fetchone()

        wait_time = None
        crowd_level = "No Data"
        available_tables = 0
        last_updated = None
        
        recommendation = {
            "label": "DATA NEEDED",
            "class": "unknown",
            "icon": "⚪",
            "message": "Waiting for the restaurant to update its crowd information."
        }

        # 3. If we have live data, calculate the AI predictions!
        if latest:
            last_updated = latest["timestamp"]
            
            # Calculate available tables
            available_tables = restaurant["total_tables"] - latest["occupied_tables"]
            if available_tables < 0: available_tables = 0

            # Run AI Models
            wait_time = predict_wait_time(
                latest["people_inside"],
                restaurant["total_tables"],
                latest["occupied_tables"],
                latest["people_entered"],
                latest["people_left"],
                restaurant["average_stay_minutes"]
            )

            crowd_level = get_crowd_level(
                latest["people_inside"],
                restaurant["total_tables"],
                latest["occupied_tables"]
            )

            recommendation = get_recommendation(
                wait_time,
                available_tables,
                latest["people_inside"],
                restaurant["total_tables"]
            )

        # 4. Package it all up for index.html
        restaurant_data.append({
            "restaurant": dict(restaurant),
            "wait_time": wait_time,
            "crowd_level": crowd_level,
            "recommendation": recommendation,
            "available_tables": available_tables,
            "last_updated": last_updated
        })

    connection.close()

    return render_template(
        "index.html",
        restaurants=restaurant_data
    )

# =========================================================
# RESTAURANT DETAILS
# =========================================================
@app.route("/restaurant/<int:restaurant_id>")
def restaurant_details(restaurant_id):
    connection = get_db_connection()

    restaurant = connection.execute(
        "SELECT * FROM restaurants WHERE id = ?",
        (restaurant_id,)
    ).fetchone()

    if restaurant is None:
        connection.close()
        return "Restaurant not found", 404

    latest = connection.execute("""
        SELECT *
        FROM crowd_updates
        WHERE restaurant_id = ?
        ORDER BY timestamp DESC
        LIMIT 1
    """, (restaurant_id,)).fetchone()

    history = connection.execute("""
        SELECT *
        FROM crowd_updates
        WHERE restaurant_id = ?
        ORDER BY timestamp DESC
        LIMIT 10
    """, (restaurant_id,)).fetchall()

    connection.close()

    wait_time = None
    crowd_level = "No Data"

    recommendation = {
        "label": "DATA NEEDED",
        "class": "unknown",
        "icon": "⚪",
        "message": "Waiting for crowd information."
    }

    if latest:
        wait_time = predict_wait_time(
            latest["people_inside"],
            restaurant["total_tables"],
            latest["occupied_tables"],
            latest["people_entered"],
            latest["people_left"],
            restaurant["average_stay_minutes"]
        )

        crowd_level = get_crowd_level(
            latest["people_inside"],
            restaurant["total_tables"],
            latest["occupied_tables"]
        )

        recommendation = get_recommendation(
            wait_time,
            latest["available_tables"],
            latest["people_inside"],
            restaurant["total_tables"]
        )

    return render_template(
        "restaurant.html",
        restaurant=restaurant,
        latest=latest,
        history=history,
        wait_time=wait_time,
        crowd_level=crowd_level,
        recommendation=recommendation
    )


# =========================================================
# OWNER DASHBOARD
# =========================================================
@app.route("/owner", methods=["GET", "POST"])
def owner_dashboard():
    connection = get_db_connection()

    restaurant = connection.execute("""
        SELECT *
        FROM restaurants
        WHERE id = 1
    """).fetchone()

    latest = connection.execute("""
        SELECT *
        FROM crowd_updates
        WHERE restaurant_id = 1
        ORDER BY timestamp DESC
        LIMIT 1
    """).fetchone()

    history = connection.execute("""
        SELECT *
        FROM crowd_updates
        WHERE restaurant_id = 1
        ORDER BY timestamp DESC
        LIMIT 10
    """).fetchall()

    connection.close()

    if restaurant is None:
        return "Please add a restaurant first."

    wait_time = None
    crowd_level = "No Data"

    if latest:
        wait_time = predict_wait_time(
            latest["people_inside"],
            restaurant["total_tables"],
            latest["occupied_tables"],
            latest["people_entered"],
            latest["people_left"],
            restaurant["average_stay_minutes"]
        )

        crowd_level = get_crowd_level(
            latest["people_inside"],
            restaurant["total_tables"],
            latest["occupied_tables"]
        )

    return render_template(
        "owner_dashboard.html",
        restaurant=restaurant,
        latest=latest,
        history=history,
        wait_time=wait_time,
        crowd_level=crowd_level
    )



# =========================================================
# UPDATE RESTAURANT CROWD
# =========================================================
@app.route("/update-crowd", methods=["POST"])
def update_crowd():
    try:
        # 1. Get data from the form
        restaurant_id = int(request.form.get("restaurant_id", 1))
        people_inside = int(request.form["people_inside"])
        people_entered = int(request.form["people_entered"])
        people_left = int(request.form["people_left"])
        occupied_tables = int(request.form["occupied_tables"])
        average_stay = int(request.form["average_stay_minutes"])
    except (ValueError, KeyError):
        flash("Please enter valid numbers.", "error")
        return redirect(url_for("owner_dashboard"))

    # 2. Basic validation
    if people_inside < 0 or people_entered < 0 or people_left < 0 or occupied_tables < 0 or average_stay <= 0:
        flash("Values cannot be negative or zero.", "error")
        return redirect(url_for("owner_dashboard"))

    connection = get_db_connection()

    # 3. Verify restaurant exists
    restaurant = connection.execute(
        "SELECT total_tables FROM restaurants WHERE id = ?", 
        (restaurant_id,)
    ).fetchone()

    if restaurant is None:
        connection.close()
        flash("Restaurant not found.", "error")
        return redirect(url_for("owner_dashboard"))

    if occupied_tables > restaurant["total_tables"]:
        connection.close()
        flash(f"Occupied tables cannot exceed total tables ({restaurant['total_tables']}).", "error")
        return redirect(url_for("owner_dashboard"))

    # 4. Save to Database
    try:
        # Save the live crowd data to crowd_updates (Removed average_stay_minutes from here!)
        connection.execute("""
            INSERT INTO crowd_updates 
            (restaurant_id, people_inside, people_entered, people_left, occupied_tables)
            VALUES (?, ?, ?, ?, ?)
        """, (restaurant_id, people_inside, people_entered, people_left, occupied_tables))
        
        # Update the average stay time in the restaurants table
        connection.execute("""
            UPDATE restaurants 
            SET average_stay_minutes = ? 
            WHERE id = ?
        """, (average_stay, restaurant_id))
        
        connection.commit() 
        flash("✓ Restaurant status updated successfully!", "success")
    except Exception as e:
        flash(f"Database error: {str(e)}", "error")
    finally:
        connection.close()

    return redirect(url_for("owner_dashboard"))


# =========================================================
# RESTAURANTS PAGE
# =========================================================
@app.route("/restaurants")
def restaurants():
    connection = get_db_connection()

    restaurants = connection.execute("""
        SELECT *
        FROM restaurants
        ORDER BY name
    """).fetchall()

    connection.close()

    return render_template(
        "index.html",
        restaurants=[
            {
                "restaurant": restaurant,
                "wait_time": None,
                "crowd_level": "No Data",
                "recommendation": {
                    "label": "VIEW DETAILS",
                    "class": "unknown",
                    "icon": "ℹ️",
                    "message": "Open restaurant details."
                },
                "last_updated": None
            }
            for restaurant in restaurants
        ]
    )


# =========================================================
# LOGIN PAGE
# =========================================================
@app.route("/login")
def login():
    return render_template("login.html")


# =========================================================
# RUN SERVER
# =========================================================
if __name__ == "__main__":
    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )