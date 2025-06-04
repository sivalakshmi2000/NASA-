import streamlit as st
import pandas as pd
import pymysql
from streamlit_option_menu import option_menu

# Page configuration
st.set_page_config(page_title="NASA NEO Dashboard", layout="wide")
st.title("☄️ NASA Near-Earth Object (NEO) Tracker")

# MySQL connection
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='Arvi@3194',
    database='Mini_NASA'
)
cursor = conn.cursor()

# Sidebar menu
with st.sidebar:
    selected = option_menu("Main Menu", ["Home", 'Queries', 'Filter Criteria'],
                           icons=['house', 'gear', 'sliders'], menu_icon="cast", default_index=1)

# Home page
if selected == "Home":
    st.write("This is my NASA Project")

# Queries page
elif selected == 'Queries':
    query_option = st.selectbox(
        "Choose a query:",
        [
            "1. Display full table",
            "2. Display only NEO names",
            "3. Display all hazardous NEOs",
            "4. Display NEOs approaching Earth only",
            "5. Display NEOs with magnitude above threshold",
            "6. Count how many times each asteroid has approached Earth",
            "7. Average velocity of each asteroid over multiple approaches",
            "8. Top 10 fastest asteroids",
            "9. Potentially hazardous asteroids with more than 3 approaches",
            "10. Month with most asteroid approaches",
            "11. Asteroid with fastest approach speed",
            "12. Sort by maximum estimated diameter",
            "13. Closest approach getting nearer over time",
            "14. Closest approach per asteroid",
            "15. Asteroids with velocity > 50000 km/h",
            "16. Approach count per month",
            "17. Asteroid with highest brightness (lowest magnitude)",
            "18. Hazardous vs non-hazardous count",
            "19. Asteroids closer than the Moon (<1 LD)",
            "20. Asteroids within 0.05 AU"
        ],
        placeholder="Choose an option..."
    )

    if query_option == "1. Display full table":
        cursor.execute("SELECT * FROM asteroids INNER JOIN close_approach ON asteroids.id = close_approach.neo_reference_id")

    elif query_option == "2. Display only NEO names":
        cursor.execute("SELECT name FROM asteroids")

    elif query_option == "3. Display all hazardous NEOs":
        cursor.execute("SELECT * FROM asteroids WHERE is_potentially_hazardous_asteroid = TRUE")

    elif query_option == "4. Display NEOs approaching Earth only":
        cursor.execute("SELECT * FROM close_approach WHERE orbiting_body = 'Earth'")

    elif query_option == "5. Display NEOs with magnitude above threshold":
        threshold = st.slider("Minimum Magnitude", 0.0, 100.0, 25.0)
        cursor.execute("SELECT * FROM asteroids WHERE absolute_magnitude > %s", (threshold,))

    elif query_option == "6. Count how many times each asteroid has approached Earth":
        cursor.execute("""
            SELECT a.name, COUNT(*) AS approach_count
            FROM asteroids a
            JOIN close_approach c ON a.id = c.neo_reference_id
            WHERE c.orbiting_body = 'Earth'
            GROUP BY a.name
        """)

    elif query_option == "7. Average velocity of each asteroid over multiple approaches":
        cursor.execute("""
            SELECT a.name, AVG(c.relative_velocity_kmph) AS avg_velocity
            FROM asteroids a
            JOIN close_approach c ON a.id = c.neo_reference_id
            GROUP BY a.name
        """)

    elif query_option == "8. Top 10 fastest asteroids":
        cursor.execute("""
            SELECT a.name, MAX(c.relative_velocity_kmph) AS top_speed
            FROM asteroids a
            JOIN close_approach c ON a.id = c.neo_reference_id
            GROUP BY a.name
            ORDER BY top_speed DESC
            LIMIT 10
        """)

    elif query_option == "9. Potentially hazardous asteroids with more than 3 approaches":
        cursor.execute("""
            SELECT a.name, COUNT(*) AS approaches
            FROM asteroids a
            JOIN close_approach c ON a.id = c.neo_reference_id
            WHERE a.is_potentially_hazardous_asteroid = TRUE
            GROUP BY a.name
            HAVING COUNT(*) > 3
        """)

    elif query_option == "10. Month with most asteroid approaches":
        cursor.execute("""
            SELECT MONTH(close_approach_date) AS month, COUNT(*) AS approach_count
            FROM close_approach
            GROUP BY month
            ORDER BY approach_count DESC
            LIMIT 1
        """)

    elif query_option == "11. Asteroid with fastest approach speed":
        cursor.execute("""
            SELECT a.name, c.relative_velocity_kmph
            FROM asteroids a
            JOIN close_approach c ON a.id = c.neo_reference_id
            ORDER BY c.relative_velocity_kmph DESC
            LIMIT 1
        """)

    elif query_option == "12. Sort by maximum estimated diameter":
        cursor.execute("""
            SELECT name, dia_max
            FROM asteroids
            ORDER BY dia_max DESC
        """)

    elif query_option == "13. Closest approach getting nearer over time":
        cursor.execute("""
            SELECT a.name, c.close_approach_date, c.miss_distance_km
            FROM asteroids a
            JOIN close_approach c ON a.id = c.neo_reference_id
            ORDER BY a.name, c.close_approach_date
        """)

    elif query_option == "14. Closest approach per asteroid":
        cursor.execute("""
            SELECT a.name, MIN(c.miss_distance_km) AS closest_distance
            FROM asteroids a
            JOIN close_approach c ON a.id = c.neo_reference_id
            GROUP BY a.name
        """)

    elif query_option == "15. Asteroids with velocity > 50000 km/h":
        cursor.execute("""
            SELECT a.name, c.relative_velocity_kmph
            FROM asteroids a
            JOIN close_approach c ON a.id = c.neo_reference_id
            WHERE c.relative_velocity_kmph > 50000
        """)

    elif query_option == "16. Approach count per month":
        cursor.execute("""
            SELECT MONTH(close_approach_date) AS month, COUNT(*) AS count
            FROM close_approach
            GROUP BY month
        """)

    elif query_option == "17. Asteroid with highest brightness (lowest magnitude)":
        cursor.execute("""
            SELECT name, absolute_magnitude
            FROM asteroids
            ORDER BY absolute_magnitude ASC
            LIMIT 1
        """)

    elif query_option == "18. Hazardous vs non-hazardous count":
        cursor.execute("""
            SELECT is_potentially_hazardous_asteroid, COUNT(*) AS count
            FROM asteroids
            GROUP BY is_potentially_hazardous_asteroid
        """)

    elif query_option == "19. Asteroids closer than the Moon (<1 LD)":
        cursor.execute("""
            SELECT a.name, c.miss_distance_lunar
            FROM asteroids a
            JOIN close_approach c ON a.id = c.neo_reference_id
            WHERE c.miss_distance_lunar < 1
        """)

    elif query_option == "20. Asteroids within 0.05 AU":
        cursor.execute("""
            SELECT a.name, c.astronomical_au
            FROM asteroids a
            JOIN close_approach c ON a.id = c.neo_reference_id
            WHERE c.astronomical_au <= 0.05
        """)

    else:
        st.warning("Please select a valid query.")

    # Show results if any
    if cursor.description:
        result = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(result, columns=columns)
        st.dataframe(df)

# Filter Criteria Page
elif selected == 'Filter Criteria':
    st.subheader("🔎 Filter Near-Earth Objects")

    col1, col2 = st.columns(2)

    with col1:
        min_mag = st.slider("Min Magnitude", 0.0, 50.0, 10.0)
        min_dia = st.slider("Min Estimated Diameter (km)", 0.0, 10.0, 0.0)
        max_dia = st.slider("Max Estimated Diameter (km)", 0.0, 20.0, 10.0)

    with col2:
        min_vel = st.slider("Min Relative Velocity (kmph)", 0.0, 200000.0, 0.0)
        max_vel = st.slider("Max Relative Velocity (kmph)", 0.0, 200000.0, 200000.0)
        min_au = st.slider("Min Astronomical Unit", 0.0, 1.0, 0.0)
        max_au = st.slider("Max Astronomical Unit", 0.0, 1.0, 1.0)

    start_date = st.date_input("Start Date")
    end_date = st.date_input("End Date")

    hazardous = st.selectbox("Only Show Potentially Hazardous", ["All", "True", "False"])

    query = """
        SELECT * FROM asteroids a
        JOIN close_approach c ON a.id = c.neo_reference_id
        WHERE a.absolute_magnitude >= %s
        AND a.dia_min >= %s
        AND a.dia_max <= %s
        AND c.relative_velocity_kmph BETWEEN %s AND %s
        AND c.astronomical_au BETWEEN %s AND %s
        AND c.close_approach_date BETWEEN %s AND %s
    """
    params = [min_mag, min_dia, max_dia, min_vel, max_vel, min_au, max_au, start_date, end_date]

    if hazardous != "All":
        query += " AND a.is_potentially_hazardous_asteroid = %s"
        params.append(hazardous)

    if st.button("Filter"):
        cursor.execute(query, tuple(params))
        result = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(result, columns=columns)
        st.dataframe(df)

# Close MySQL connection
conn.close()