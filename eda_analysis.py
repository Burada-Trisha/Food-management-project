import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set working directory and database path
workspace = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(workspace, "food_wastage.db")
charts_dir = os.path.join(workspace, "charts")

# Ensure charts directory exists
os.makedirs(charts_dir, exist_ok=True)

# Connect to database
conn = sqlite3.connect(db_path)

# Load data into DataFrames
providers_df = pd.read_sql_query("SELECT * FROM providers;", conn)
receivers_df = pd.read_sql_query("SELECT * FROM receivers;", conn)
listings_df = pd.read_sql_query("SELECT * FROM food_listings;", conn)
claims_df = pd.read_sql_query("SELECT * FROM claims;", conn)

conn.close()

# Set modern plotting aesthetics
sns.set_theme(style="whitegrid")
plt.rcParams.update({
    'figure.figsize': (10, 6),
    'font.family': 'sans-serif',
    'font.size': 11,
    'axes.labelsize': 12,
    'axes.titlesize': 14,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'figure.titlesize': 16
})

# Premium color palettes
palette_primary = sns.color_palette("viridis", 8)
palette_accent = sns.color_palette("coolwarm", 7)
palette_muted = sns.color_palette("muted")

def save_plot(filename):
    plt.tight_layout()
    path = os.path.join(charts_dir, filename)
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Saved chart: {filename}")

# ==========================================
# 1. UNIVARIATE ANALYSIS
# ==========================================

# 1.1 Provider Type Distribution
plt.figure()
sns.countplot(data=providers_df, x='Type', hue='Type', palette="crest", legend=False)
plt.title("Provider Type Distribution")
plt.xlabel("Provider Type")
plt.ylabel("Count")
save_plot("univariate_1_provider_type.png")

# 1.2 Receiver Type Distribution
plt.figure()
sns.countplot(data=receivers_df, x='Type', hue='Type', palette="mako", legend=False)
plt.title("Receiver Type Distribution")
plt.xlabel("Receiver Type")
plt.ylabel("Count")
save_plot("univariate_2_receiver_type.png")

# 1.3 Food Type Distribution
plt.figure()
sns.countplot(data=listings_df, x='Food_Type', hue='Food_Type', palette="Set2", legend=False)
plt.title("Food Type Distribution (Listings)")
plt.xlabel("Food Type")
plt.ylabel("Count")
save_plot("univariate_3_food_type.png")

# 1.4 Meal Type Distribution
plt.figure()
sns.countplot(data=listings_df, x='Meal_Type', hue='Meal_Type', palette="rocket", legend=False)
plt.title("Meal Type Distribution (Listings)")
plt.xlabel("Meal Type")
plt.ylabel("Count")
save_plot("univariate_4_meal_type.png")

# ==========================================
# 2. BIVARIATE ANALYSIS
# ==========================================

# 2.1 City vs Food Listings (Top 10 Cities)
plt.figure()
city_listings = listings_df['Location'].value_counts().head(10).reset_index()
city_listings.columns = ['City', 'Listing_Count']
sns.barplot(data=city_listings, y='City', x='Listing_Count', hue='City', palette="viridis", legend=False)
plt.title("Top 10 Cities by Number of Food Listings")
plt.xlabel("Number of Food Listings")
plt.ylabel("City")
save_plot("bivariate_1_city_vs_listings.png")

# 2.2 Provider Type vs Quantity (Sum of Quantity by Provider Type)
plt.figure()
prov_qty = listings_df.groupby('Provider_Type')['Quantity'].sum().reset_index()
sns.barplot(data=prov_qty, x='Provider_Type', y='Quantity', hue='Provider_Type', palette="flare", legend=False)
plt.title("Total Food Quantity Contributed by Provider Type")
plt.xlabel("Provider Type")
plt.ylabel("Total Quantity")
save_plot("bivariate_2_provider_type_vs_quantity.png")

# 2.3 Food Type vs Quantity
plt.figure()
food_qty = listings_df.groupby('Food_Type')['Quantity'].sum().reset_index()
sns.barplot(data=food_qty, x='Food_Type', y='Quantity', hue='Food_Type', palette="pastel", legend=False)
plt.title("Total Food Quantity by Food Type")
plt.xlabel("Food Type")
plt.ylabel("Total Quantity")
save_plot("bivariate_3_food_type_vs_quantity.png")

# 2.4 Meal Type vs Quantity
plt.figure()
meal_qty = listings_df.groupby('Meal_Type')['Quantity'].sum().reset_index()
sns.barplot(data=meal_qty, x='Meal_Type', y='Quantity', hue='Meal_Type', palette="magma", legend=False)
plt.title("Total Food Quantity by Meal Type")
plt.xlabel("Meal Type")
plt.ylabel("Total Quantity")
save_plot("bivariate_4_meal_type_vs_quantity.png")

# ==========================================
# 3. MULTIVARIATE ANALYSIS
# ==========================================

# 3.1 City + Provider Type + Quantity (Top 5 Cities)
plt.figure()
top_cities = listings_df['Location'].value_counts().head(5).index
city_prov_qty = listings_df[listings_df['Location'].isin(top_cities)].groupby(['Location', 'Provider_Type'])['Quantity'].sum().reset_index()
sns.barplot(data=city_prov_qty, x='Location', y='Quantity', hue='Provider_Type', palette="coolwarm")
plt.title("Food Quantity by City and Provider Type (Top 5 Cities)")
plt.xlabel("City")
plt.ylabel("Total Quantity")
plt.legend(title="Provider Type", bbox_to_anchor=(1.05, 1), loc='upper left')
save_plot("multivariate_1_city_provider_quantity.png")

# 3.2 Food Type + Meal Type + Quantity
plt.figure()
food_meal_qty = listings_df.groupby(['Food_Type', 'Meal_Type'])['Quantity'].sum().reset_index()
sns.barplot(data=food_meal_qty, x='Food_Type', y='Quantity', hue='Meal_Type', palette="Spectral")
plt.title("Food Quantity by Food Type and Meal Type")
plt.xlabel("Food Type")
plt.ylabel("Total Quantity")
plt.legend(title="Meal Type", bbox_to_anchor=(1.05, 1), loc='upper left')
save_plot("multivariate_2_food_meal_quantity.png")

# 3.3 Provider + Claims + Quantity (Top 5 Providers)
plt.figure()
# Merge claims with food listings to know which provider listed the claimed food
claims_listings = pd.merge(claims_df, listings_df, on='Food_ID')
claims_listings_prov = pd.merge(claims_listings, providers_df.rename(columns={'Name': 'Provider_Name'}), left_on='Provider_ID', right_on='Provider_ID')
prov_claims_qty = claims_listings_prov.groupby(['Provider_Name', 'Status'])['Quantity'].sum().reset_index()
top_prov_names = claims_listings_prov['Provider_Name'].value_counts().head(5).index
top_prov_claims = prov_claims_qty[prov_claims_qty['Provider_Name'].isin(top_prov_names)]
sns.barplot(data=top_prov_claims, y='Provider_Name', x='Quantity', hue='Status', palette="Set1")
plt.title("Quantity Listed by Top 5 Providers and their Claim Status")
plt.xlabel("Quantity")
plt.ylabel("Provider Name")
save_plot("multivariate_3_provider_claims_quantity.png")

# 3.4 Receiver + Claims + Quantity (Top 5 Receivers)
plt.figure()
claims_receivers = pd.merge(claims_df, receivers_df.rename(columns={'Name': 'Receiver_Name'}), on='Receiver_ID')
claims_rec_listings = pd.merge(claims_receivers, listings_df, on='Food_ID')
rec_claims_qty = claims_rec_listings.groupby(['Receiver_Name', 'Status'])['Quantity'].sum().reset_index()
top_rec_names = claims_rec_listings['Receiver_Name'].value_counts().head(5).index
top_rec_claims = rec_claims_qty[rec_claims_qty['Receiver_Name'].isin(top_rec_names)]
sns.barplot(data=top_rec_claims, y='Receiver_Name', x='Quantity', hue='Status', palette="Set2")
plt.title("Quantity Requested by Top 5 Receivers and Claim Status")
plt.xlabel("Quantity")
plt.ylabel("Receiver Name")
save_plot("multivariate_4_receiver_claims_quantity.png")

# ==========================================
# 4. CLAIM ANALYSIS
# ==========================================

# 4.1 Claim Status Distribution
plt.figure()
status_counts = claims_df['Status'].value_counts()
plt.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', colors=['#4F81BD', '#C0504D', '#9BBB59'], startangle=90, wedgeprops={'edgecolor': 'w'})
plt.title("Claim Status Distribution")
save_plot("claim_analysis_1_status_distribution.png")

# 4.2 Top Receivers (Most successful claims count)
plt.figure()
comp_claims = claims_df[claims_df['Status'] == 'Completed']
top_rec = comp_claims['Receiver_ID'].value_counts().head(5).reset_index()
top_rec.columns = ['Receiver_ID', 'Successful_Claims']
top_rec = pd.merge(top_rec, receivers_df, on='Receiver_ID')
sns.barplot(data=top_rec, x='Successful_Claims', y='Name', hue='Name', palette="copper", legend=False)
plt.title("Top 5 Receivers by Successful Claims")
plt.xlabel("Successful Claims Count")
plt.ylabel("Receiver Name")
save_plot("claim_analysis_2_top_receivers.png")

# 4.3 Top Providers (Most successful claims count)
plt.figure()
claims_listings_comp = claims_listings[claims_listings['Status'] == 'Completed']
top_prov = claims_listings_comp['Provider_ID'].value_counts().head(5).reset_index()
top_prov.columns = ['Provider_ID', 'Successful_Claims']
top_prov = pd.merge(top_prov, providers_df, on='Provider_ID')
sns.barplot(data=top_prov, x='Successful_Claims', y='Name', hue='Name', palette="bone", legend=False)
plt.title("Top 5 Providers by Successful Claims")
plt.xlabel("Successful Claims Count")
plt.ylabel("Provider Name")
save_plot("claim_analysis_3_top_providers.png")

print("All charts successfully generated and saved to 'charts' folder.")
