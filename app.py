import streamlit as st
import pandas as pd
import sqlite3
import os
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Set page configuration with a wide layout and custom title
st.set_page_config(
    page_title="Local Food Wastage Management System",
    page_icon="🍲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Set database and charts path
workspace = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(workspace, "food_wastage.db")
charts_dir = os.path.join(workspace, "charts")

# Custom CSS for premium styling (dark mode theme with glassmorphic elements)
st.markdown("""
<style>
    /* Main body changes */
    .stApp {
        background: linear-gradient(135deg, #121824 0%, #1a233a 100%);
        color: #e2e8f0;
    }
    
    /* Title card style */
    .title-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 24px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 25px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }
    .title-text {
        font-family: 'Outfit', 'Inter', sans-serif;
        font-weight: 800;
        font-size: 2.8rem;
        background: linear-gradient(90deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
    }
    .subtitle-text {
        font-size: 1.1rem;
        color: #94a3b8;
    }
    
    /* Custom metric card */
    .kpi-container {
        display: flex;
        justify-content: space-between;
        gap: 15px;
        margin-bottom: 25px;
    }
    .kpi-card {
        flex: 1;
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(8px);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transition: transform 0.3s ease;
    }
    .kpi-card:hover {
        transform: translateY(-5px);
        border: 1px solid rgba(56, 189, 248, 0.4);
    }
    .kpi-val {
        font-size: 2.2rem;
        font-weight: 700;
        color: #38bdf8;
        margin-bottom: 5px;
    }
    .kpi-lbl {
        font-size: 0.9rem;
        text-transform: uppercase;
        color: #94a3b8;
        letter-spacing: 1px;
    }
    
    /* Section card */
    .section-card {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 12px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        margin-bottom: 20px;
    }
    
    /* Tab styling override */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 4px;
        color: #94a3b8;
        font-weight: 600;
        font-size: 1rem;
    }
    .stTabs [aria-selected="true"] {
        color: #38bdf8 !important;
        border-bottom-color: #38bdf8 !important;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to get database connection
def get_connection():
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

# Header section
st.markdown("""
<div class="title-card">
    <div class="title-text">🍲 Local Food Wastage Management System</div>
    <div class="subtitle-text">Connecting Surplus Food Donors to Food Seekers & NGOs for Waste Reduction and Social Good</div>
</div>
""", unsafe_allow_html=True)

# Sidebar Filters & Navigation
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3075/3075977.png", width=80)
st.sidebar.markdown("### 🔍 Dashboard Controls")

# Fetch unique values for filters
conn = get_connection()
cities = pd.read_sql_query("SELECT DISTINCT City FROM (SELECT City FROM providers UNION SELECT City FROM receivers UNION SELECT Location as City FROM food_listings);", conn)['City'].dropna().tolist()
provider_types = pd.read_sql_query("SELECT DISTINCT Type FROM providers;", conn)['Type'].dropna().tolist()
food_types = pd.read_sql_query("SELECT DISTINCT Food_Type FROM food_listings;", conn)['Food_Type'].dropna().tolist()
meal_types = pd.read_sql_query("SELECT DISTINCT Meal_Type FROM food_listings;", conn)['Meal_Type'].dropna().tolist()
conn.close()

selected_city = st.sidebar.selectbox("Filter by City", ["All"] + sorted(cities))
selected_prov_type = st.sidebar.selectbox("Filter by Provider Type", ["All"] + sorted(provider_types))
selected_food_type = st.sidebar.selectbox("Filter by Food Type", ["All"] + sorted(food_types))
selected_meal_type = st.sidebar.selectbox("Filter by Meal Type", ["All"] + sorted(meal_types))

# KPI Panel values
conn = get_connection()
total_listings = pd.read_sql_query("SELECT COUNT(*) as count FROM food_listings;", conn)['count'][0]
total_qty = pd.read_sql_query("SELECT SUM(Quantity) as qty FROM food_listings;", conn)['qty'][0]
claims_df = pd.read_sql_query("SELECT Status FROM claims;", conn)
total_claims = len(claims_df)
completed_claims = len(claims_df[claims_df['Status'] == 'Completed'])
completed_pct = (completed_claims / total_claims * 100) if total_claims > 0 else 0.0
active_donors = pd.read_sql_query("SELECT COUNT(DISTINCT Provider_ID) as count FROM food_listings;", conn)['count'][0]
active_receivers = pd.read_sql_query("SELECT COUNT(DISTINCT Receiver_ID) as count FROM claims WHERE Status='Completed';", conn)['count'][0]
conn.close()

# Render KPI metric cards
st.markdown(f"""
<div class="kpi-container">
    <div class="kpi-card">
        <div class="kpi-val">{total_qty:,} items</div>
        <div class="kpi-lbl">Total Donated Food</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-val">{completed_pct:.1f}%</div>
        <div class="kpi-lbl">Claim Completion Rate</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-val">{active_donors}</div>
        <div class="kpi-lbl">Active Providers</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-val">{active_receivers}</div>
        <div class="kpi-lbl">Active NGO / Receivers</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Tabs Navigation
tab_dashboard, tab_crud, tab_sql, tab_lookup, tab_insights = st.tabs([
    "📊 Analytics Dashboard", 
    "🛠️ CRUD Data Management", 
    "💻 SQL Console", 
    "📞 Provider/Receiver Directory", 
    "💡 Business Insights & recommendations"
])

# ==========================================
# TAB 1: ANALYTICS DASHBOARD
# ==========================================
with tab_dashboard:
    st.markdown("### Interactive Distribution & Exploratory Analysis")
    
    # Query matching sidebar filters
    query = """
    SELECT f.*, p.Name as Provider_Name, p.City as Provider_City
    FROM food_listings f
    JOIN providers p ON f.Provider_ID = p.Provider_ID
    WHERE 1=1
    """
    params = []
    if selected_city != "All":
        query += " AND p.City = ?"
        params.append(selected_city)
    if selected_prov_type != "All":
        query += " AND f.Provider_Type = ?"
        params.append(selected_prov_type)
    if selected_food_type != "All":
        query += " AND f.Food_Type = ?"
        params.append(selected_food_type)
    if selected_meal_type != "All":
        query += " AND f.Meal_Type = ?"
        params.append(selected_meal_type)
        
    conn = get_connection()
    filtered_df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    if filtered_df.empty:
        st.warning("⚠️ No records match the selected filters. Please adjust the sidebar options.")
    else:
        # Display sample matching records
        st.markdown(f"**Found {len(filtered_df)} matching food listings.** Showing a sample below:")
        st.dataframe(filtered_df[['Food_ID', 'Food_Name', 'Quantity', 'Expiry_Date', 'Provider_Name', 'Provider_City', 'Food_Type', 'Meal_Type']].head(5), use_container_width=True)
        
        # Dashboard charts columns
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("<div class='section-card'>", unsafe_allow_html=True)
            st.markdown("#### Univariate: Food Type & Meal Type Distribution")
            fig, ax = plt.subplots(1, 2, figsize=(10, 4.5))
            
            # Food Type countplot
            sns.countplot(data=filtered_df, x='Food_Type', ax=ax[0], palette="crest", hue='Food_Type', legend=False)
            ax[0].set_title("Food Category Count")
            ax[0].set_xlabel("")
            ax[0].tick_params(axis='x', rotation=30)
            
            # Meal Type countplot
            sns.countplot(data=filtered_df, x='Meal_Type', ax=ax[1], palette="flare", hue='Meal_Type', legend=False)
            ax[1].set_title("Meal Category Count")
            ax[1].set_xlabel("")
            ax[1].tick_params(axis='x', rotation=30)
            
            st.pyplot(fig)
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("<div class='section-card'>", unsafe_allow_html=True)
            st.markdown("#### Bivariate: Provider Type vs Quantity")
            fig, ax = plt.subplots(figsize=(10, 4.5))
            prov_qty = filtered_df.groupby('Provider_Type')['Quantity'].sum().reset_index()
            sns.barplot(data=prov_qty, x='Provider_Type', y='Quantity', ax=ax, palette="viridis", hue='Provider_Type', legend=False)
            ax.set_title("Total Food Quantity Contributed by Provider Type")
            ax.set_xlabel("Provider Type")
            ax.set_ylabel("Quantity")
            st.pyplot(fig)
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col2:
            st.markdown("<div class='section-card'>", unsafe_allow_html=True)
            st.markdown("#### Bivariate: Food Type vs Quantity")
            fig, ax = plt.subplots(figsize=(10, 4.5))
            food_qty = filtered_df.groupby('Food_Type')['Quantity'].sum().reset_index()
            sns.barplot(data=food_qty, x='Food_Type', y='Quantity', ax=ax, palette="magma", hue='Food_Type', legend=False)
            ax.set_title("Total Quantity of Food Listed by Food Type")
            ax.set_xlabel("Food Type")
            ax.set_ylabel("Quantity")
            st.pyplot(fig)
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='section-card'>", unsafe_allow_html=True)
            st.markdown("#### Multivariate: Food Type + Meal Type + Quantity")
            fig, ax = plt.subplots(figsize=(10, 4.5))
            food_meal_qty = filtered_df.groupby(['Food_Type', 'Meal_Type'])['Quantity'].sum().reset_index()
            sns.barplot(data=food_meal_qty, x='Food_Type', y='Quantity', hue='Meal_Type', ax=ax, palette="Spectral")
            ax.set_title("Food Quantity by Type and Meal Category")
            ax.set_xlabel("Food Type")
            ax.set_ylabel("Quantity")
            ax.legend(title="Meal Type", bbox_to_anchor=(1.02, 1), loc='upper left')
            st.pyplot(fig)
            st.markdown("</div>", unsafe_allow_html=True)

    # Static presentation charts view
    st.markdown("---")
    st.markdown("### 🖼️ Saved Presentation Charts (Static Report Images)")
    chart_files = sorted([f for f in os.listdir(charts_dir) if f.endswith('.png')])
    selected_chart = st.selectbox("Select a generated chart image to view in high resolution:", chart_files)
    if selected_chart:
        chart_path = os.path.join(charts_dir, selected_chart)
        st.image(chart_path, caption=selected_chart.replace('_', ' ').title(), use_container_width=True)

# ==========================================
# TAB 2: CRUD DATA MANAGEMENT
# ==========================================
with tab_crud:
    st.markdown("### 🛠️ Database CRUD Console")
    crud_mode = st.radio("Select Action:", ["Create Food Listing", "Update Food Listing", "Delete Record"], horizontal=True)
    
    conn = get_connection()
    # Fetch lists for selectors
    providers_list = pd.read_sql_query("SELECT Provider_ID, Name FROM providers ORDER BY Name;", conn)
    food_list = pd.read_sql_query("SELECT Food_ID, Food_Name, Quantity, Location FROM food_listings ORDER BY Food_ID DESC;", conn)
    conn.close()
    
    if crud_mode == "Create Food Listing":
        st.markdown("#### Add a New Food Listing")
        with st.form("add_food_form", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                new_food_name = st.text_input("Food Name (e.g. Pasta, Salad)", placeholder="Rice")
                new_qty = st.number_input("Quantity", min_value=1, max_value=1000, value=10)
                new_expiry = st.date_input("Expiry Date")
            with col2:
                provider_choice = st.selectbox("Listing Provider", [f"{r['Provider_ID']}: {r['Name']}" for _, r in providers_list.iterrows()])
                new_food_type = st.selectbox("Food Type", ["Vegetarian", "Non-Vegetarian", "Vegan"])
            with col3:
                new_meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snacks"])
                new_location = st.text_input("Location / City", placeholder="New York")
                
            submitted = st.form_submit_with_rows_col = st.form_submit_button("Submit New Listing")
            
            if submitted:
                if not new_food_name or not new_location:
                    st.error("❌ Food name and location/city are required fields!")
                else:
                    pid = int(provider_choice.split(":")[0])
                    prov_type = pd.read_sql_query(f"SELECT Type FROM providers WHERE Provider_ID={pid}", get_connection())['Type'][0]
                    expiry_str = new_expiry.strftime("%Y-%m-%d")
                    
                    conn = get_connection()
                    cursor = conn.cursor()
                    try:
                        # Find max id
                        max_id = cursor.execute("SELECT MAX(Food_ID) FROM food_listings;").fetchone()[0] or 0
                        new_id = max_id + 1
                        cursor.execute("""
                        INSERT INTO food_listings (Food_ID, Food_Name, Quantity, Expiry_Date, Provider_ID, Provider_Type, Location, Food_Type, Meal_Type)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                        """, (new_id, new_food_name, new_qty, expiry_str, pid, prov_type, new_location, new_food_type, new_meal_type))
                        conn.commit()
                        st.success(f"✅ Listing '{new_food_name}' successfully added to database with ID {new_id}!")
                    except Exception as e:
                        st.error(f"❌ Error adding listing: {e}")
                    finally:
                        conn.close()
                        
    elif crud_mode == "Update Food Listing":
        st.markdown("#### Modify Existing Food Listing Details")
        selected_listing = st.selectbox("Select Food Listing to Edit:", 
                                        [f"ID {r['Food_ID']} | {r['Food_Name']} ({r['Quantity']} items) in {r['Location']}" for _, r in food_list.iterrows()])
        if selected_listing:
            fid = int(selected_listing.split(" | ")[0].replace("ID ", ""))
            conn = get_connection()
            current_listing = pd.read_sql_query(f"SELECT * FROM food_listings WHERE Food_ID={fid};", conn).iloc[0]
            conn.close()
            
            with st.form("update_food_form"):
                col1, col2 = st.columns(2)
                with col1:
                    up_food_name = st.text_input("Food Name", value=current_listing['Food_Name'])
                    up_qty = st.number_input("Quantity", min_value=1, max_value=1000, value=int(current_listing['Quantity']))
                    curr_expiry_dt = datetime.strptime(current_listing['Expiry_Date'], "%Y-%m-%d") if current_listing['Expiry_Date'] else datetime.today()
                    up_expiry = st.date_input("Expiry Date", value=curr_expiry_dt)
                with col2:
                    up_food_type = st.selectbox("Food Type", ["Vegetarian", "Non-Vegetarian", "Vegan"], index=["Vegetarian", "Non-Vegetarian", "Vegan"].index(current_listing['Food_Type']))
                    up_meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snacks"], index=["Breakfast", "Lunch", "Dinner", "Snacks"].index(current_listing['Meal_Type']))
                    up_location = st.text_input("Location / City", value=current_listing['Location'])
                    
                up_submitted = st.form_submit_button("Update Listing Details")
                
                if up_submitted:
                    expiry_str = up_expiry.strftime("%Y-%m-%d")
                    conn = get_connection()
                    cursor = conn.cursor()
                    try:
                        cursor.execute("""
                        UPDATE food_listings 
                        SET Food_Name=?, Quantity=?, Expiry_Date=?, Location=?, Food_Type=?, Meal_Type=?
                        WHERE Food_ID=?;
                        """, (up_food_name, up_qty, expiry_str, up_location, up_food_type, up_meal_type, fid))
                        conn.commit()
                        st.success(f"✅ Food Listing ID {fid} successfully updated!")
                    except Exception as e:
                        st.error(f"❌ Error updating listing: {e}")
                    finally:
                        conn.close()
                        
    elif crud_mode == "Delete Record":
        st.markdown("#### Remove a Listing or Claim Record")
        delete_type = st.selectbox("Select Record Type to Delete:", ["Food Listing", "Claim Record"])
        
        if delete_type == "Food Listing":
            selected_to_del = st.selectbox("Select Food Listing to Remove (WARNING: This will delete associated claims):", 
                                            [f"ID {r['Food_ID']} | {r['Food_Name']} ({r['Quantity']} items) in {r['Location']}" for _, r in food_list.iterrows()])
            if selected_to_del:
                fid = int(selected_to_del.split(" | ")[0].replace("ID ", ""))
                confirm_del = st.checkbox("Confirm deletion of this listing permanently.")
                if st.button("Delete Listing"):
                    if confirm_del:
                        conn = get_connection()
                        cursor = conn.cursor()
                        try:
                            cursor.execute(f"DELETE FROM food_listings WHERE Food_ID={fid};")
                            conn.commit()
                            st.success(f"✅ Food Listing ID {fid} deleted from database!")
                        except Exception as e:
                            st.error(f"❌ Error deleting record: {e}")
                        finally:
                            conn.close()
                    else:
                        st.warning("⚠️ Please check the confirmation checkbox first.")
                        
        elif delete_type == "Claim Record":
            conn = get_connection()
            claims_list = pd.read_sql_query("SELECT c.Claim_ID, f.Food_Name, c.Status, r.Name as Receiver_Name FROM claims c JOIN food_listings f ON c.Food_ID = f.Food_ID JOIN receivers r ON c.Receiver_ID = r.Receiver_ID ORDER BY c.Claim_ID DESC;", conn)
            conn.close()
            
            selected_claim_to_del = st.selectbox("Select Claim Record to Remove:", 
                                                 [f"Claim ID {r['Claim_ID']} | {r['Receiver_Name']} claimed {r['Food_Name']} (Status: {r['Status']})" for _, r in claims_list.iterrows()])
            if selected_claim_to_del:
                cid = int(selected_claim_to_del.split(" | ")[0].replace("Claim ID ", ""))
                confirm_claim_del = st.checkbox("Confirm deletion of this claim record.")
                if st.button("Delete Claim"):
                    if confirm_claim_del:
                        conn = get_connection()
                        cursor = conn.cursor()
                        try:
                            cursor.execute(f"DELETE FROM claims WHERE Claim_ID={cid};")
                            conn.commit()
                            st.success(f"✅ Claim Record ID {cid} deleted from database!")
                        except Exception as e:
                            st.error(f"❌ Error deleting claim: {e}")
                        finally:
                            conn.close()
                    else:
                        st.warning("⚠️ Please check the confirmation checkbox first.")

# ==========================================
# TAB 3: SQL CONSOLE
# ==========================================
with tab_sql:
    st.markdown("### 💻 SQL Analytical Query Runner")
    st.markdown("Run pre-coded analytical queries directly against the database to trace trends and answer regulatory questions.")
    
    # 16 Precoded SQL Queries
    queries_dict = {
        "1. Providers Count by City": """
SELECT City, COUNT(*) as Provider_Count
FROM providers
GROUP BY City
ORDER BY Provider_Count DESC
LIMIT 10;""",
        "2. Receivers Count by City": """
SELECT City, COUNT(*) as Receiver_Count
FROM receivers
GROUP BY City
ORDER BY Receiver_Count DESC
LIMIT 10;""",
        "3. Most Contributing Provider (Top 10)": """
SELECT p.Provider_ID, p.Name, p.Type, p.City, SUM(f.Quantity) as Total_Quantity_Donated
FROM food_listings f
JOIN providers p ON f.Provider_ID = p.Provider_ID
GROUP BY p.Provider_ID
ORDER BY Total_Quantity_Donated DESC
LIMIT 10;""",
        "4. Most Claimed Food Category": """
SELECT f.Food_Name, COUNT(c.Claim_ID) as Claims_Count, SUM(f.Quantity) as Total_Quantity
FROM claims c
JOIN food_listings f ON c.Food_ID = f.Food_ID
GROUP BY f.Food_Name
ORDER BY Claims_Count DESC
LIMIT 10;""",
        "5. Total Food Quantity Contributed Overall": """
SELECT SUM(Quantity) as Total_Food_Quantity
FROM food_listings;""",
        "6. Top Cities by Food Listings (Top 10)": """
SELECT Location as City, COUNT(*) as Listings_Count, SUM(Quantity) as Total_Quantity
FROM food_listings
GROUP BY Location
ORDER BY Total_Quantity DESC
LIMIT 10;""",
        "7. Most Common Food Types Listed": """
SELECT Food_Type, COUNT(*) as Listings_Count, SUM(Quantity) as Total_Quantity
FROM food_listings
GROUP BY Food_Type
ORDER BY Total_Quantity DESC;""",
        "8. Claim Count per Food Item": """
SELECT f.Food_ID, f.Food_Name, f.Quantity, p.Name as Provider_Name,
       (SELECT COUNT(*) FROM claims WHERE Food_ID = f.Food_ID) as Claims_Count
FROM food_listings f
JOIN providers p ON f.Provider_ID = p.Provider_ID
ORDER BY Claims_Count DESC
LIMIT 10;""",
        "9. Providers with Most Successful Claims": """
SELECT p.Provider_ID, p.Name, p.Type, p.City, COUNT(c.Claim_ID) as Successful_Claims
FROM claims c
JOIN food_listings f ON c.Food_ID = f.Food_ID
JOIN providers p ON f.Provider_ID = p.Provider_ID
WHERE c.Status = 'Completed'
GROUP BY p.Provider_ID
ORDER BY Successful_Claims DESC
LIMIT 10;""",
        "10. Claim Status Distribution (%)": """
SELECT Status, COUNT(*) as Claim_Count, 
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims), 2) as Percentage
FROM claims
GROUP BY Status;""",
        "11. Average Quantity Claimed per Successful Transaction": """
SELECT ROUND(AVG(f.Quantity), 2) as Avg_Quantity_Claimed
FROM claims c
JOIN food_listings f ON c.Food_ID = f.Food_ID
WHERE c.Status = 'Completed';""",
        "12. Most Claimed Meal Types": """
SELECT f.Meal_Type, COUNT(c.Claim_ID) as Claims_Count
FROM claims c
JOIN food_listings f ON c.Food_ID = f.Food_ID
GROUP BY f.Meal_Type
ORDER BY Claims_Count DESC;""",
        "13. Total Donated Quantity by Provider Sector": """
SELECT Provider_Type, SUM(Quantity) as Total_Quantity, COUNT(*) as Listings_Count
FROM food_listings
GROUP BY Provider_Type
ORDER BY Total_Quantity DESC;""",
        "14. Top Receivers / NGOs by Completed Claims": """
SELECT r.Receiver_ID, r.Name, r.Type, r.City, COUNT(c.Claim_ID) as Completed_Claims, SUM(f.Quantity) as Total_Quantity_Claimed
FROM claims c
JOIN receivers r ON c.Receiver_ID = r.Receiver_ID
JOIN food_listings f ON c.Food_ID = f.Food_ID
WHERE c.Status = 'Completed'
GROUP BY r.Receiver_ID
ORDER BY Completed_Claims DESC
LIMIT 10;""",
        "15. Cities with Highest Food Demand (Claims Count)": """
SELECT r.City, COUNT(c.Claim_ID) as Claims_Count, SUM(f.Quantity) as Total_Quantity_Requested
FROM claims c
JOIN receivers r ON c.Receiver_ID = r.Receiver_ID
JOIN food_listings f ON c.Food_ID = f.Food_ID
GROUP BY r.City
ORDER BY Claims_Count DESC
LIMIT 10;""",
        "16. Overall System Balance Sheet (Listings vs Outcomes)": """
SELECT 
    COUNT(f.Food_ID) as Total_Listings,
    SUM(CASE WHEN c.Status = 'Completed' THEN 1 ELSE 0 END) as Completed_Claims,
    SUM(CASE WHEN c.Status = 'Pending' THEN 1 ELSE 0 END) as Pending_Claims,
    SUM(CASE WHEN c.Status = 'Cancelled' OR c.Status IS NULL THEN 1 ELSE 0 END) as Wasted_Unclaimed_Listings
FROM food_listings f
LEFT JOIN claims c ON f.Food_ID = c.Food_ID;"""
    }
    
    query_choice = st.selectbox("Select SQL Query to Execute:", list(queries_dict.keys()))
    
    # Custom Query area
    custom_query_mode = st.checkbox("Toggle Custom SQL Mode (Write your own SQL query)")
    
    if custom_query_mode:
        selected_sql = st.text_area("Write SQL Query:", "SELECT * FROM food_listings LIMIT 5;")
    else:
        selected_sql = queries_dict[query_choice]
        
    st.code(selected_sql, language="sql")
    
    if st.button("Execute Query"):
        conn = get_connection()
        try:
            query_results = pd.read_sql_query(selected_sql, conn)
            st.success("✅ Query executed successfully!")
            st.dataframe(query_results, use_container_width=True)
        except Exception as e:
            st.error(f"❌ SQL Execution Error: {e}")
        finally:
            conn.close()

# ==========================================
# TAB 4: PROVIDER/RECEIVER DIRECTORY
# ==========================================
with tab_lookup:
    st.markdown("### 📞 Donor and Receiver Contact Registry")
    st.markdown("Search details and coordinate pickups directly with food donors or receivers.")
    
    lookup_type = st.radio("Search Database For:", ["Food Providers (Donors)", "Food Receivers (NGOs/Shelters)"], horizontal=True)
    
    conn = get_connection()
    if lookup_type == "Food Providers (Donors)":
        st.markdown("#### Search Food Providers")
        city_search = st.selectbox("Search by City Location:", ["All"] + sorted(list(providers_df['City'].unique())))
        type_search = st.selectbox("Search by Provider Sector:", ["All"] + sorted(list(providers_df['Type'].unique())))
        
        query = "SELECT Name, Type, City, Address, Contact FROM providers WHERE 1=1"
        params = []
        if city_search != "All":
            query += " AND City = ?"
            params.append(city_search)
        if type_search != "All":
            query += " AND Type = ?"
            params.append(type_search)
            
        results = pd.read_sql_query(query, conn, params=params)
        st.dataframe(results, use_container_width=True)
        
    else:
        st.markdown("#### Search Food Receivers (NGOs/Shelters)")
        city_search = st.selectbox("Search by City Location:", ["All"] + sorted(list(receivers_df['City'].unique())))
        type_search = st.selectbox("Search by Receiver Type:", ["All"] + sorted(list(receivers_df['Type'].unique())))
        
        query = "SELECT Name, Type, City, Contact FROM receivers WHERE 1=1"
        params = []
        if city_search != "All":
            query += " AND City = ?"
            params.append(city_search)
        if type_search != "All":
            query += " AND Type = ?"
            params.append(type_search)
            
        results = pd.read_sql_query(query, conn, params=params)
        st.dataframe(results, use_container_width=True)
    conn.close()

# ==========================================
# TAB 5: BUSINESS INSIGHTS & RECOMMENDATIONS
# ==========================================
with tab_insights:
    st.markdown("### 💡 Business Intelligence Dashboard")
    
    st.markdown("""
    This section summarizes key answers to critical business questions derived from statistical analysis of the food donation datasets.
    """)
    
    col_ins1, col_ins2 = st.columns(2)
    
    with col_ins1:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("#### 1. Food Availability Analysis")
        st.info("📍 **City with the Most Food Available:** **South Kathryn** (Total Quantity: 179 items across 6 listings)\n\n"
                "Other high availability hotspots include *Jonathanstad* (169), *New Carol* (167), and *North Keith* (158).")
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("#### 2. Food Waste Analysis")
        st.warning("⏱️ **Meal Type most vulnerable to claims cancellation/waste:** **Breakfast** (278 total claims/listings)\n\n"
                   "Breakfast foods have short freshness lifespans, contributing heavily to cancellations and wasted logistics.")
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("#### 3. Provider Contributions")
        st.success("🏢 **Top Contributing Provider:** **Barry Group** (Restaurant in South Kathryn)\n\n"
                   "Total Quantity Donated: **179 items**, followed by *Evans, Wright and Mitchell* (158 items) and *Smith Group* (150 items).")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_ins2:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("#### 4. Receiver Analysis")
        st.info("🤝 **Top Claiming Receivers (NGOs/Charities):**\n"
                "- **Derek Potter** (Charity in South Laurachester) claimed **99 items** (3 completed claims).\n"
                "- **Timothy Garrett** (NGO in Andersonview) claimed **80 items** (3 completed claims).\n"
                "- **Alexandra Owens** (NGO in Bradleyland) claimed **61 items** (3 completed claims).")
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("#### 5. Claims & System Efficiency")
        st.success("📊 **Claim Status Breakdown:**\n"
                   "- **Completed Claims:** **33.9%** (339 claims)\n"
                   "- **Pending Claims:** **32.5%** (325 claims)\n"
                   "- **Cancelled Claims:** **33.6%** (336 claims)\n\n"
                   "Approximately **51.0%** of total listings overall go unclaimed or are cancelled, signaling a high potential food wastage rate.")
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("#### 6. Demand Hotspots")
        st.warning("📈 **Cities with the Highest Food Demand (Claims Count):**\n"
                   "- **West David** (5 claims, 191 items requested)\n"
                   "- **Smithshire** (5 claims, 134 items requested)\n"
                   "- **Port Richard** (5 claims, 135 items requested)")
        st.markdown("</div>", unsafe_allow_html=True)
        
    # Recommendations section
    st.markdown("---")
    st.markdown("### 📋 Executive Business Recommendations")
    
    rec_col1, rec_col2 = st.columns(2)
    with rec_col1:
        st.markdown("""
        > [!IMPORTANT]
        > **Recommendation 1: Targeted NGO Partnerships**
        > Cities with high food wastage listings (e.g., *South Kathryn*, *Jonathanstad*) should have more active NGO partnerships. We recommend establishing localized storage hubs in these cities to quickly absorb daily surplus donations.
        
        > [!NOTE]
        > **Recommendation 2: Donor Recognition Program**
        > Key donors like the **Barry Group** and **Evans, Wright and Mitchell** should receive corporate social responsibility (CSR) awards. This encourages continuous listing and motivates other providers to participate.
        """)
        
    with rec_col2:
        st.markdown("""
        > [!TIP]
        > **Recommendation 3: Expiry-Based Push Notifications**
        > Automated alerts should be pushed to nearby NGOs 12 hours before a listed item's expiry date (especially for short-life meals like Breakfast and Lunch) to accelerate claiming.
        
        > [!WARNING]
        > **Recommendation 4: Relocate Sourcing Logistics to High-Demand Hubs**
        > Increase collection and transport vehicle frequency to high-demand cities like **West David** and **Smithshire**, where the claim volume is high but local donation volume is comparatively low.
        """)

# Footer credits
st.markdown("---")
st.markdown("<p style='text-align: center; color: #64748b; font-size: 0.8rem;'>Local Food Wastage Management System Dashboard • Built for Project Submission • © 2026</p>", unsafe_allow_html=True)
