# Digital Complaint Management System (ShaktiCMS)

A clean, responsive, and secure **Digital Complaint Management System** developed as a college mini-project. 

## Technology Stack
- **Backend**: Python (Flask)
- **Database**: ShaktiDB (compatible with PostgreSQL) / SQLite (Out-of-the-box local fallback)
- **Database Interface**: SQL (via `psycopg2` for ShaktiDB and `sqlite3` for local fallback)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla design with custom blue-white visual themes)
- **Operating System**: Linux

---

## Key Features

### Student Role
1. **Secure Access**: Dynamic, verified student registration and password-protected login.
2. **Dashboard**: Unified cards counting total, pending, under review, and resolved complaints.
3. **Complaint Submission**: Form supporting titles, category filters, detailed explanations, and supporting image uploads.
4. **Complaint History**: Instant client-side search and multi-column filtering.
5. **Timeline Tracking**: Visual vertical progress trail detailing status changes and admin action remarks.
6. **Notification Banner**: Automatic notification triggers on statuses updates with highlight flags.
7. **Profile Update**: Edit account details (Name, Email, Department) and passwords securely.

### Admin Role
1. **Administrative Portal**: Restricted administrative login.
2. **Operations Dashboard**: Summary counts and real-time canvas-drawn charts (Category distributions & Statuses).
3. **Complaint Review**: Full lists supporting ID searching, filtering, and assignment fields.
4. **Action Form**: Update workflow status, designate investigators, and publish resolution logs.
5. **Student Registry**: Form for adding students manually and options to delete accounts.
6. **Analytics Reports**: Detailed system metrics, resolution rates, category charts, and monthly submission trend lines, with a built-in print utility.

---

## Directory Structure

```text
DigitalComplaintSystem/
│── app.py                   # Main Flask application entry point
│── config.py                # System and upload configurations
│── requirements.txt         # Package dependencies
│── README.md                # Documentation guide
│
├── database/
│     ├── schema.sql         # ShaktiDB / PostgreSQL database schema
│     ├── sample_data.sql    # Sample data inserts for PostgreSQL
│     └── schema_sqlite.sql  # Database schema for SQLite fallback
│
├── docs/
│     ├── ER_Diagram.md      # Relational schemas documentation
│     └── Flowchart.md       # Complaint status lifecycles diagram
│
├── routes/
│     ├── auth.py            # Login, registration, and logout blueprints
│     ├── student.py         # Student-facing workflows
│     └── admin.py           # Admin-facing actions & reports
│
├── models/
│     └── db.py              # DB connection factory and seeding utilities
│
├── utils/
│     └── helpers.py         # Access decorators, notifications, file uploads
│
├── static/
│     ├── css/
│     │     └── style.css    # Responsive blue-white styling variables
│     └── js/
│           ├── main.js      # Sidebar toggles, image previews, searching
│           └── charts.js    # Canvas chart rendering scripts
│
└── templates/
      ├── base.html          # HTML frame shell layout
      ├── login.html         # Combined login/registration tab panels
      ├── student/           # Student page views
      └── admin/             # Administrator page views
```

---

## Database Configuration

### Option A: ShaktiDB (PostgreSQL) - Recommended for Production
ShaktiDB is a PostgreSQL fork. Make sure you have your database instance running.
Create a `.env` file in the root `DigitalComplaintSystem/` folder containing the connection URL:
```env
DATABASE_URL=postgresql://<username>:<password>@<host>:<port>/<dbname>
SECRET_KEY=any-custom-secure-key-string
```
The application will automatically pick up this environment variable and establish connections to ShaktiDB, running schema creations and loading sample records.

### Option B: Local SQLite Fallback (Runs Immediately Out-of-the-Box)
If no `DATABASE_URL` is set, the system automatically creates an SQLite file at `database/complaints.db` on launch. This allows immediate execution without setup dependencies.

---

## Installation & Launch (Linux)

Open your terminal and follow these steps:

### 1. Clone or Navigate to the Directory
Ensure you are inside the `DigitalComplaintSystem` root directory:
```bash
cd DigitalComplaintSystem
```

### 2. Set Up a Python Virtual Environment
Create a clean environment container:
```bash
python3 -m venv venv
```
Activate the virtual environment:
```bash
source venv/bin/activate
```

### 3. Install Required Dependencies
Install the Flask framework and database adapters:
```bash
pip install -r requirements.txt
```

### 4. Start the Application
Execute the python server entry file:
```bash
python app.py
```
On startup, the system will output verification lines, build database tables, seed sample records, and start hosting at:
**`http://127.0.0.1:5000`**

---

## Default Accounts for Testing

Use these pre-seeded accounts to explore the system:

### Student Credentials
- **Email**: `amit@college.edu`
- **Password**: `student123`

- **Email**: `priya@college.edu`
- **Password**: `student123`

### Admin Credentials
- **Username**: `admin`
- **Password**: `admin123`
