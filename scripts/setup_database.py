import sqlite3
import pandas as pd
import os

DB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database'))
DB_PATH = os.path.join(DB_DIR, 'placify.db')

JOBS_TSV = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'user_data.tsv'))
JDS_TSV = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'jds_data.tsv'))

def setup_database():
    os.makedirs(DB_DIR, exist_ok=True)
    
    print(f"Connecting to SQLite database at {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    
    try:
        if os.path.exists(JOBS_TSV):
            print("Loading Jobs Data into SQLite...")
            jobs_df = pd.read_csv(JOBS_TSV, sep='\t')
            jobs_df.to_sql('job_market', conn, if_exists='replace', index=False)
            print(f"Inserted {len(jobs_df)} rows into 'job_market' table.")
        else:
            print(f"Warning: {JOBS_TSV} not found.")

        if os.path.exists(JDS_TSV):
            print("Loading JDS Skills Data into SQLite...")
            jds_df = pd.read_csv(JDS_TSV, sep='\t')
            jds_df.to_sql('jds_skills', conn, if_exists='replace', index=False)
            print(f"Inserted {len(jds_df)} rows into 'jds_skills' table.")
        else:
            print(f"Warning: {JDS_TSV} not found.")
            
        print("Database setup complete! You can query 'placify.db' now.")
    except Exception as e:
        print(f"Error during SQLite setup: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    setup_database()
