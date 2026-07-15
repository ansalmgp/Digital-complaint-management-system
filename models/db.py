import os
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash
from config import Config

def get_connection():
    """
    Establish connection with ShaktiDB (PostgreSQL) if configured,
    otherwise fallback to SQLite for local development.
    """
    if Config.DATABASE_URL:
        try:
            conn = psycopg2.connect(Config.DATABASE_URL)
            return conn, "shaktidb"
        except Exception as e:
            print(f"Warning: Failed to connect to ShaktiDB at {Config.DATABASE_URL}. Error: {e}")
            print("Falling back to local SQLite database...")
            
    # SQLite fallback
    os.makedirs(os.path.dirname(Config.SQLITE_DB_PATH), exist_ok=True)
    conn = sqlite3.connect(Config.SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn, "sqlite"

def query_db(query, args=(), one=False, commit=False):
    """
    Execute SQL queries against ShaktiDB or SQLite and return dict results.
    """
    conn, db_type = get_connection()
    cur = None
    try:
        if db_type == "shaktidb":
            # PostgreSQL uses %s placeholders
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute(query, args)
            if commit:
                conn.commit()
            
            if cur.description is not None:
                rv = cur.fetchall()
            else:
                rv = None
        else:
            # SQLite uses ? placeholders instead of %s
            sqlite_query = query.replace('%s', '?')
            cur = conn.cursor()
            cur.execute(sqlite_query, args)
            if commit:
                conn.commit()
                
            if cur.description is not None:
                rv = [dict(row) for row in cur.fetchall()]
            else:
                rv = None
                
        return (rv[0] if rv else None) if one else rv
    except Exception as e:
        if commit:
            conn.rollback()
        print(f"Database Query Error: {e}\nQuery: {query}\nArgs: {args}")
        raise e
    finally:
        if cur:
            cur.close()
        conn.close()

def init_db(force=False):
    """
    Initialize database tables and seed sample data.
    """
    conn, db_type = get_connection()
    
    # Check if database is already initialized
    initialized = False
    try:
        cur = conn.cursor()
        if db_type == "shaktidb":
            cur.execute("SELECT 1 FROM Students LIMIT 1;")
        else:
            cur.execute("SELECT 1 FROM Students LIMIT 1;")
        cur.close()
        initialized = True
    except Exception:
        # Table doesn't exist
        pass

    if initialized and not force:
        conn.close()
        print("Database already initialized.")
        return

    print(f"Initializing {db_type} database...")
    
    # Read appropriate schema file
    schema_file = "database/schema.sql" if db_type == "shaktidb" else "database/schema_sqlite.sql"
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    schema_path = os.path.join(base_dir, schema_file)
    
    with open(schema_path, 'r') as f:
        schema_sql = f.read()

    try:
        if db_type == "shaktidb":
            cur = conn.cursor()
            cur.execute(schema_sql)
            conn.commit()
            cur.close()
        else:
            conn.executescript(schema_sql)
            conn.commit()
        print("Schema applied successfully.")
    except Exception as e:
        print(f"Error applying schema: {e}")
        conn.close()
        return

    # Seed only admin accounts — no sample data
    try:
        admin_pwd = generate_password_hash("admin123")
        
        print("Seeding admin accounts...")
        
        if db_type == "shaktidb":
            cur = conn.cursor()
            
            # Truncate clean state
            cur.execute("TRUNCATE TABLE Notifications, ComplaintHistory, Complaints, Admins, Students RESTART IDENTITY CASCADE;")
            
            # Insert Admins only
            cur.execute("INSERT INTO Admins (Username, Password) VALUES (%s, %s);", ("admin", admin_pwd))
            cur.execute("INSERT INTO Admins (Username, Password) VALUES (%s, %s);", ("admin2", admin_pwd))
            
            conn.commit()
            cur.close()
        else:
            # SQLite seed — admins only
            cur = conn.cursor()
            
            # Insert Admins only
            cur.execute("INSERT INTO Admins (Username, Password) VALUES (?, ?);", ("admin", admin_pwd))
            cur.execute("INSERT INTO Admins (Username, Password) VALUES (?, ?);", ("admin2", admin_pwd))
            
            conn.commit()
            cur.close()
            
        print("Data seeded successfully.")
    except Exception as e:
        print(f"Error seeding database: {e}")
    finally:
        conn.close()
