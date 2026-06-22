import csv
import sqlite3
import os
from datetime import datetime

# Define workspace and DB paths
workspace = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(workspace, "food_wastage.db")

def parse_date(date_str):
    if not date_str or date_str.lower() in ('null', 'nan', ''):
        return None
    try:
        # Input format from CSV is usually M/D/YYYY (e.g., 3/17/2025)
        return datetime.strptime(date_str.strip(), "%m/%d/%Y").strftime("%Y-%m-%d")
    except ValueError:
        try:
            return datetime.strptime(date_str.strip(), "%Y-%m-%d").strftime("%Y-%m-%d")
        except ValueError:
            return date_str

def parse_datetime(dt_str):
    if not dt_str or dt_str.lower() in ('null', 'nan', ''):
        return None
    try:
        # Input format is usually M/D/YYYY H:M (e.g., 3/5/2025 5:26)
        return datetime.strptime(dt_str.strip(), "%m/%d/%Y %H:%M").strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        try:
            return datetime.strptime(dt_str.strip(), "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            return dt_str

def init_db():
    print("Initializing Database...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # Drop child tables first to avoid foreign key violations
    cursor.execute("DROP TABLE IF EXISTS claims;")
    cursor.execute("DROP TABLE IF EXISTS food_listings;")
    cursor.execute("DROP TABLE IF EXISTS receivers;")
    cursor.execute("DROP TABLE IF EXISTS providers;")
    
    # 1. Create providers table
    cursor.execute("""
    CREATE TABLE providers (
        Provider_ID INTEGER PRIMARY KEY,
        Name TEXT NOT NULL,
        Type TEXT NOT NULL,
        Address TEXT,
        City TEXT NOT NULL,
        Contact TEXT
    );
    """)
    
    # 2. Create receivers table
    cursor.execute("""
    CREATE TABLE receivers (
        Receiver_ID INTEGER PRIMARY KEY,
        Name TEXT NOT NULL,
        Type TEXT NOT NULL,
        City TEXT NOT NULL,
        Contact TEXT
    );
    """)

    # 3. Create food_listings table
    cursor.execute("""
    CREATE TABLE food_listings (
        Food_ID INTEGER PRIMARY KEY,
        Food_Name TEXT NOT NULL,
        Quantity INTEGER NOT NULL,
        Expiry_Date TEXT,
        Provider_ID INTEGER NOT NULL,
        Provider_Type TEXT,
        Location TEXT NOT NULL,
        Food_Type TEXT,
        Meal_Type TEXT,
        FOREIGN KEY (Provider_ID) REFERENCES providers(Provider_ID) ON DELETE CASCADE
    );
    """)

    # 4. Create claims table
    cursor.execute("DROP TABLE IF EXISTS claims;")
    cursor.execute("""
    CREATE TABLE claims (
        Claim_ID INTEGER PRIMARY KEY,
        Food_ID INTEGER NOT NULL,
        Receiver_ID INTEGER NOT NULL,
        Status TEXT NOT NULL CHECK(Status IN ('Pending', 'Completed', 'Cancelled')),
        Timestamp TEXT,
        FOREIGN KEY (Food_ID) REFERENCES food_listings(Food_ID) ON DELETE CASCADE,
        FOREIGN KEY (Receiver_ID) REFERENCES receivers(Receiver_ID) ON DELETE CASCADE
    );
    """)

    conn.commit()
    conn.close()
    print("Database tables created.")

def load_csv_data():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Load Providers
    providers_file = os.path.join(workspace, "providers_data.csv")
    with open(providers_file, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader) # skip headers
        rows = [row for row in reader]
        cursor.executemany("INSERT INTO providers VALUES (?, ?, ?, ?, ?, ?);", rows)
        print(f"Loaded {len(rows)} records into 'providers'.")
        
    # Load Receivers
    receivers_file = os.path.join(workspace, "receivers_data.csv")
    with open(receivers_file, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)
        rows = [row for row in reader]
        cursor.executemany("INSERT INTO receivers VALUES (?, ?, ?, ?, ?);", rows)
        print(f"Loaded {len(rows)} records into 'receivers'.")

    # Load Food Listings (normalize Expiry Date)
    listings_file = os.path.join(workspace, "food_listings_data.csv")
    with open(listings_file, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)
        formatted_rows = []
        for r in reader:
            formatted_rows.append((
                int(r[0]), # Food_ID
                r[1],      # Food_Name
                int(r[2]) if r[2] else 0, # Quantity
                parse_date(r[3]), # Expiry_Date
                int(r[4]), # Provider_ID
                r[5],      # Provider_Type
                r[6],      # Location
                r[7],      # Food_Type
                r[8]       # Meal_Type
            ))
        cursor.executemany("INSERT INTO food_listings VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);", formatted_rows)
        print(f"Loaded {len(formatted_rows)} records into 'food_listings'.")

    # Load Claims (normalize Timestamp)
    claims_file = os.path.join(workspace, "claims_data.csv")
    with open(claims_file, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)
        formatted_claims = []
        for r in reader:
            formatted_claims.append((
                int(r[0]), # Claim_ID
                int(r[1]), # Food_ID
                int(r[2]), # Receiver_ID
                r[3],      # Status
                parse_datetime(r[4]) # Timestamp
            ))
        cursor.executemany("INSERT INTO claims VALUES (?, ?, ?, ?, ?);", formatted_claims)
        print(f"Loaded {len(formatted_claims)} records into 'claims'.")

    conn.commit()
    conn.close()
    print("All datasets loaded into SQLite database successfully!")

if __name__ == "__main__":
    init_db()
    load_csv_data()
