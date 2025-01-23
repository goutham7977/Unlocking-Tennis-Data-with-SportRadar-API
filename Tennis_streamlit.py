import streamlit as st
import pandas as pd
import pymysql

st.markdown(
    """
    <style>
 
    .stApp {
        #background: linear-gradient(135deg,rgb(16, 240, 184),rgb(231, 53, 136));
        #background: linear-gradient(135deg,rgb(16, 240, 184),rgb(231, 53, 136),#8AAAE5, #FFFFFF,#962E2A, #E3867D, #CEE6F2, #1995AD, #A1D6E2, #F1F1F2, #90AFC5);
        background: linear-gradient(135deg,#8AAAE5, #FFFFFF);
        #background: linear-gradient(135deg,#89ABE3, #EA738D);
        #background: linear-gradient(135deg, #00246B, #CADCF,#89ABE3, #EA738D);
        #background: linear-gradient(135deg, #89ABE3, #EA738D);
        #background: linear-gradient(135deg, #51e2f5, #9df9ef, #edf756, #ffa8B6);
        background-size: cover;
        background-attachment: fixed;
        
    }


    #section[data-testid="stSidebar"] {
        #background: linear-gradient(135deg,rgb(7, 156, 241),rgb(16, 240, 184));
        #background: linear-gradient(135deg,rgb(16, 240, 184),rgb(231, 53, 136));
        #color: white;
        #padding: 15px;
       #border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)




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
st.title("Tennis Data with SportRadar🏸")


st.header("Overview")
st.write("**Explore key metrics and navigate to different sections.**")
menu = st.selectbox(
    "Choose a section to explore:",
    ["Overview", "Competitor Analysis", "Venue Analysis", "Competition Analysis"],
)



# Section 1: Overview
#if menu == "Overview":
    #st.header("Overview")
    #st.write(" **Explore key metrics and insights about the tennis competitions, venues, and participants.**")
    
    # Total Competitors
if menu == "Overview":
    st.write("""The analysis highlights some key trends in tennis. Male participation is much higher
     than female and mixed categories, showing a clear gender imbalance. Players come from all over the world, reflecting the sport’s global reach, with top competitors standing out for their impressive rankings and points. Events are held in many venues, with some complexes hosting more tournaments than others. While competitions cover a variety of categories, the gender distribution is still uneven. Rankings show a highly competitive field, with top players consistently performing better. These findings point to opportunities to improve inclusivity and accessibility in the sport.""")
    mycursor.execute("SELECT COUNT(DISTINCT competitor_id) AS total_competitors FROM competitors")
    total_competitors = mycursor.fetchone()[0]
    #st.sidebar.metric("Total Competitors", f"{total_competitors} 🎾")
    st.markdown(f"<div style='font-size: 30px;'><b>Total Competitors:</b> <br>{total_competitors} 🎾</div>", unsafe_allow_html=True)

    # Total Countries
    mycursor.execute("SELECT COUNT(DISTINCT country) AS total_countries FROM competitors")
    total_countries = mycursor.fetchone()[0]
    #st.sidebar.metric("Total Countries", f"{total_countries} 🌏")
    st.markdown(f"<div style='font-size: 30px;'><b>Total Countries:</b><br> {total_countries} 🌏</div>", unsafe_allow_html=True)
    
    # Top Competitor (by points)
    mycursor.execute("""
    SELECT competitors.competito_name, competitor_rankings.ranks, competitor_rankings.points
    FROM competitors
    INNER JOIN competitor_rankings
    ON competitors.competitor_id = competitor_rankings.competitor_id
""")
    top_competitor = mycursor.fetchone()
    st.markdown(
    f"<div style='font-size: 30px;'><b>Top Competitor:</b> {top_competitor[0]} 🏆 <br>({top_competitor[2]} points)</div>",
    unsafe_allow_html=True
   
)
# Section 2: Competitor Analysis
elif menu == "Competitor Analysis":
    st.header("🤽Competitor Analysis")
    
    # Competitor Table
    mycursor.execute("SELECT * FROM competitors")
    data = mycursor.fetchall()
    #print('/n /n This is data')
    #print(data)
    columns = [desc[0] for desc in mycursor.description]
    #print('/n /n This is columns')
    #print(columns)
    df = pd.DataFrame(data, columns=columns)
    #print('/n /n This is df data')
    #print(df)
    
    # Search by Name
    search_name = st.text_input("🔎 Search for a competitor by name:")
    if search_name:
       query = """ 
       SELECT competitors.competitor_id, competitors.competito_name, competitors.country,
       competitor_rankings.ranks, competitor_rankings.points
       FROM competitors
       INNER JOIN competitor_rankings 
       ON competitors.competitor_id = competitor_rankings.competitor_id
       WHERE LOWER(competitors.competito_name) LIKE LOWER(%s);
       """
       params = (f"%{search_name}%",)  # Parameterized for safety
    else:
        query = """
        SELECT competitors.competitor_id, competitors.competito_name, competitors.country,
        competitor_rankings.ranks, competitor_rankings.points
        FROM competitors
        INNER JOIN competitor_rankings 
        ON competitors.competitor_id = competitor_rankings.competitor_id;
        """
        params = None
    mycursor.execute(query, params)   
    competitor_data = mycursor.fetchall()
    columns = [desc[0] for desc in mycursor.description]
    competitor_df = pd.DataFrame(competitor_data, columns=columns)
    st.dataframe(competitor_df, hide_index=True)
    
    #if search_name:
        #filtered_df = df[df["competito_name"].str.contains(search_name, case=False, na=False)]
        #st.dataframe(filtered_df, hide_index=True)
    #else:
       # st.dataframe(df, hide_index=True)



    
     # Filter by Country
    #country = st.selectbox("Select country", df["country"].unique())
    #filtered_df = df[df["country"] == country]
    #st.subheader("Competitors from Selected Country")
    #st.dataframe(filtered_df, hide_index=True)
    search_country = st.selectbox(" 🌍  Select country", df["country"].unique())
    query = """
       SELECT competitors.competitor_id, competitors.competito_name, competitors.country,
       competitor_rankings.ranks, competitor_rankings.points
       FROM competitors
       INNER JOIN competitor_rankings 
       ON competitors.competitor_id = competitor_rankings.competitor_id
       WHERE LOWER(competitors.country) LIKE LOWER (%s);
       """
    params = (search_country)  # Parameterized for safety
    mycursor.execute(query,params)   
    competitor_data = mycursor.fetchall()
    columns = [desc[0] for desc in mycursor.description]
    competitor_df = pd.DataFrame(competitor_data, columns=columns)
    st.subheader(f"Competitors from {search_country}")
    st.dataframe(competitor_df, hide_index=True)
    
    
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

    min_rank, max_rank = st.slider("🏅🏆 Select Rank Range", 1, 1000, (1, 100))
    rank_filtered = competitor_df[(competitor_df["ranks"] >= min_rank) & (competitor_df["ranks"] <= max_rank)]
    st.subheader("Filtered  by Rank")
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
    st.metric("Total Complexes", f"{total_complexes} 🏢")
    st.metric("Total Venues", f"{total_venues} 🏟")

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
    #gender = st.sidebar.selectbox("Filter by Gender", competition_df["gender"].unique())
    #gender_filtered = competition_df[competition_df["gender"] == gender]
    #st.subheader("Filtered Competitions by Gender")
    #st.dataframe(gender_filtered, hide_index=True)

    gender = st.selectbox("Filter by Gender", competition_df["gender"].unique())
    st.write(f"Selected Gender: {gender}")
    query = """
    SELECT competitions.competition_name, categories.category_name, competitions.gender
    FROM competitions
    INNER JOIN categories ON competitions.category_id = categories.category_id
    WHERE competitions.gender = %s;
    """
    params = (gender,)
    mycursor.execute(query,params)
    competition_data = mycursor.fetchall()
    columns = [desc[0] for desc in mycursor.description]
    competition_df = pd.DataFrame(competition_data, columns=columns)
    st.subheader(f"Filtered Competitions by Gender: {gender}")
    st.dataframe(competition_df, hide_index=True)
    


    

# Footer: Connection Closure
mycursor.close()
connection.close()
