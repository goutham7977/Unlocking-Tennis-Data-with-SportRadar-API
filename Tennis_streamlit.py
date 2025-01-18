import streamlit as st
import pandas as pd
import pymysql

# Set custom style
st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(120deg, #84fab0 0%, #8fd3f4 100%);
        color: green;
    }
    .metric-container {
        text-align: center;
        background: #fdfcfb;
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 10px;
    }
    h1, h2, h3, h4, h5 {
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
        color: #2c3e50;
    }
    .dataframe {
        border: 1px solid #ddd;
        background: #ffffff;
    }
    </style>
""", unsafe_allow_html=True)

# Database connection
connection = pymysql.connect(
    host="localhost",
    port=3306,
    user="root",
    password="root",
    database="tennis"
)
mycursor = connection.cursor()

# Title and Sidebar
st.title("🎾 Tennis Sport Radar")
st.sidebar.title("📊 Navigation")
menu = st.sidebar.radio(
    "Choose a section:",
    ["Overview", "Competitor Analysis", "Venue Analysis", "Competition Analysis"]
)


# Rest of the logic remains the same...

# Section 1: Overview
if menu == "Overview":
    st.header("Overview")
    st.write(" **Explore key metrics and insights about the tennis competitions, venues, and participants.**")
    
    # Total Competitors
    mycursor.execute("SELECT COUNT(DISTINCT competitor_id) AS total_competitors FROM competitors")
    total_competitors = mycursor.fetchone()[0]
    st.sidebar.metric("Total Competitors", f"{total_competitors} 🎾")

    # Total Countries
    mycursor.execute("SELECT COUNT(DISTINCT country) AS total_countries FROM competitors")
    total_countries = mycursor.fetchone()[0]
    st.sidebar.metric("Total Countries", f"{total_countries} 🌏")

    # Top Competitor (by points)
    mycursor.execute("""
    SELECT competitors.competito_name, competitor_rankings.ranks, competitor_rankings.points
    FROM competitors
    INNER JOIN competitor_rankings
    ON competitors.competitor_id = competitor_rankings.competitor_id
""")
    top_competitor = mycursor.fetchone()
    st.sidebar.markdown(
    f"<div style='font-size: 12px;'><b>Top Competitor:</b> {top_competitor[0]} 🏆 ({top_competitor[2]} points)</div>",
    unsafe_allow_html=True
)
# Section 2: Competitor Analysis
elif menu == "Competitor Analysis":
    st.header("👥 Competitor Analysis")
    
    # Competitor Table
    mycursor.execute("SELECT * FROM competitors")
    data = mycursor.fetchall()
    columns = [desc[0] for desc in mycursor.description]
    df = pd.DataFrame(data, columns=columns)
    
    # Search by Name
    search_name = st.text_input("🔎 Search for a competitor by name:")
    if search_name:
        filtered_df = df[df["competito_name"].str.contains(search_name, case=False, na=False)]
        st.dataframe(filtered_df, hide_index=True)
    else:
        st.dataframe(df, hide_index=True)
    
     # Filter by Country
    country = st.selectbox("Select country", df["country"].unique())
    filtered_df = df[df["country"] == country]
    st.subheader("Competitors from Selected Country")
    st.dataframe(filtered_df, hide_index=True)
    
    # Filter by Rank Range
    mycursor.execute("""
        SELECT competitors.competitor_id, competitors.competito_name, competitors.country,
               competitor_rankings.ranks, competitor_rankings.points
        FROM competitors
        INNER JOIN competitor_rankings 
        ON competitors.competitor_id = competitor_rankings.competitor_id
    """)
    competitor_data = mycursor.fetchall()
    columns = [desc[0] for desc in mycursor.description]
    competitor_df = pd.DataFrame(competitor_data, columns=columns)

    min_rank, max_rank = st.sidebar.slider("Select Rank Range", 1, 1000, (1, 100))
    rank_filtered = competitor_df[(competitor_df["ranks"] >= min_rank) & (competitor_df["ranks"] <= max_rank)]
    st.subheader("Filtered Competitors by Rank")
    st.dataframe(rank_filtered, hide_index=True)

# Section 3: Venue Analysis
elif menu == "Venue Analysis":
    st.header("🏟 Venue Analysis")
    
    # Total Complexes and Venues
    mycursor.execute("""
        SELECT complexes.complex_name, COUNT(venues.venue_name) AS venue_count
        FROM complexes
        INNER JOIN venues ON complexes.complex_id = venues.complex_id
        GROUP BY complexes.complex_name
    """)
    venue_data = mycursor.fetchall()
    columns = [desc[0] for desc in mycursor.description]
    venue_df = pd.DataFrame(venue_data, columns=columns)
    
    st.subheader("Venues in Each Complex")
    st.dataframe(venue_df, hide_index=True)

    # Total Complexes and Venues Summary
    total_complexes = venue_df["complex_name"].nunique()
    total_venues = venue_df["venue_count"].sum()
    st.sidebar.metric("Total Complexes", f"{total_complexes} 🏢")
    st.sidebar.metric("Total Venues", f"{total_venues} 🏟")

# Section 4: Competition Analysis
elif menu == "Competition Analysis":
    st.header("🏆 Competition Analysis")
    
    # Competitions and Categories
    mycursor.execute("""
        SELECT competitions.competition_name, categories.category_name, competitions.gender
        FROM competitions
        INNER JOIN categories ON competitions.category_id = categories.category_id
    """)
    competition_data = mycursor.fetchall()
    columns = [desc[0] for desc in mycursor.description]
    competition_df = pd.DataFrame(competition_data, columns=columns)
    
    st.subheader("Competitions and Categories")
    st.dataframe(competition_df, hide_index=True)

    # Filter by Gender
    gender = st.sidebar.selectbox("Filter by Gender", competition_df["gender"].unique())
    gender_filtered = competition_df[competition_df["gender"] == gender]
    st.subheader("Filtered Competitions by Gender")
    st.dataframe(gender_filtered, hide_index=True)

# Footer: Connection Closure
mycursor.close()
connection.close()
