import sqlite3 #This imports Python’s built-in SQLite database module.#SQLite is a lightweight database stored in a single file.
import os      #The os module helps Python interact with the operating system. # You use it for things like: creating folders, checking files, getting paths, etc.

DB_PATH = "data/workspace.db"  #This is a variable. It holds the path to the SQLite database file.
                               #data/ → folder name
                               #workspace.db → SQLite database file
def get_connection():          # A function is a reusable block of code.Whenever you call: Python will run everything inside this function.
                               
    os.makedirs("data", exist_ok=True)          #This line creates a folder named "data" if it doesn't already exist. This prevents errors if the folder already exists.
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)        #Think of it like:Python app  <---->  Database file,#(The connection allows Python to: send queries, save data,retrieve data)
    conn.row_factory = sqlite3.Row          # allows dict-like access to rows, so you can do row["column_name"] instead of row[0]
    return conn                             #This sends the database connection back to wherever the function was called.
                                                                                             
                                                #1. Import database tools
                                                #2. Set database file location
                                                #3. Create function
                                                #4. Create folder if needed
                                                #5. Connect to database
                                                #6. Make results easier to read
                                                #7. Return the connection
                                                
                
def initialize_database():                      #The purpose of this function is: Prepare the database and create tables if they do not exist.
    conn = get_connection()                     #This line calls the get_connection() function to establish a connection to the SQLite database. It allows us to interact with the database.
    cursor = conn.cursor()                      #A cursor is like a control center for executing SQL commands. Example: CREATE TABLE, INSERT, SELECT, UPDATE,DELETE    
    
    #---EMPLOYEES TABLE---
                                                #''' - Triple quotes allow multi-line strings. Very useful for long SQL queries.
                                                #PRIMARY KEY: This is the unique identifier for each employee. No two employees can have the same ID.
                                                #AUTOINCREMENT: SQLite automatically increases the number. You don’t need to manually enter IDs.
                                                #UNIQUE NOT NULL,: No duplicate emails allowed.
                                                #status TEXT DEFAULT 'active', (Default value means: If no value is provided, SQLite automatically uses "active".

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            employee_id     INTEGER PRIMARY KEY AUTOINCREMENT,
            name            TEXT NOT NULL,
            email           TEXT UNIQUE NOT NULL,
            department      TEXT,
            role            TEXT,
            joining_date    TEXT,
            status          TEXT DEFAULT 'active',
            created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    #---REQUESTS TABLE---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS requests (
            request_id      INTEGER PRIMARY KEY AUTOINCREMENT,
            request_type    TEXT NOT NULL,
            employee_name   TEXT,
            department      TEXT,
            description     TEXT,
            status          TEXT DEFAULT 'pending',
            created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
            resolved_at     DATETIME
        )
    ''')
    
    #---USERS TABLE---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id         INTEGER PRIMARY KEY AUTOINCREMENT,
            username        TEXT UNIQUE NOT NULL,
            password_hash   TEXT NOT NULL,
            role            TEXT DEFAULT 'user',
            employee_id     INTEGER,
            created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
        )
    ''')
    
    #---IT TICKETS TABLE---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS it_tickets (
            ticket_id       INTEGER PRIMARY KEY AUTOINCREMENT,
            title           TEXT NOT NULL,
            issue_type      TEXT,
            reported_by     TEXT,
            assigned_to     TEXT,
            priority        TEXT DEFAULT 'medium',
            status          TEXT DEFAULT 'open',
            description     TEXT,
            created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
            resolved_at     DATETIME
        )
    ''')    
    
    #---AUDIT LOG TABLE---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_log (
            log_id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username       TEXT,
            action          TEXT NOT NULL,
            details         TEXT,
            timestamp       DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    #---ONBOARDING RECORDS TABLE---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS onboarding_records (
            onboarding_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id     INTEGER,
            employee_name   TEXT,
            department      TEXT,
            role            TEXT,
            joining_date    TEXT,
            required_access TEXT,
            drive_folder    TEXT,
            calendar_event  TEXT,
            welcome_email   TEXT DEFAULT 'pending',
            status          TEXT DEFAULT 'in_progress',
            completed_at    DATETIME,
            created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
        )
    """)
    #---EMAIL LOG TABLE---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS email_log (
            email_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            to_address  TEXT,
            subject     TEXT,
            body        TEXT,
            email_type  TEXT,
            status      TEXT DEFAULT 'sent',
            sent_at     DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()                   #This saves all the changes we made to the database. If you forget this, your tables won't actually be created.
    conn.close()                    #This closes the connection to the database. It's good practice to close connections when you're done with them to free up resources.
    print("✅ Database initialized.") #Output in Terminal: ✅ Database initialized.(It helps users/developers quickly see success messages.)
