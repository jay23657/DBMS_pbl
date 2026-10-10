# Police Complaint and Evidence Tracking System

This project is a relational database management system built for a Police Station to track complaints, officers, investigation activities, evidence, and custody logs. 

## Features
- **Normalized Relational Database (3NF)**: Covers Complaints, Persons, Officers, Assignments, Activities, Evidence, Custody, Witnesses, Court, Charges, and Statuses.
- **Constraints & Business Rules Enforced**: Unique IDs, proper foreign key cascades, date validations, checking complete custody transfers, closure detail requirements.
- **Python-Streamlit Frontend**: A simple interactive dashboard with visualization, CRUD capabilities, and reporting elements.
- **Meaningful Queries**: Contains nested queries, JOINS, aggregation functions (for Officer load, case timeline, and active evidence locations).

## Setup Instructions

### 1. Database Setup
You need MySQL Server running.
1. Open your terminal or MySQL Workbench.
2. Run the `schema.sql` script to create the `police_db` database, tables, and insert sample data.
   ```bash
   mysql -u root -p < schema.sql
   ```

### 2. Python Environment
Make sure you have Python 3 installed.
1. Navigate to the project directory.
2. Install the required libraries:
   ```bash
   pip install -r requirements.txt
   ```

### 3. Database Connection Configuration
If your MySQL root password is not `password`, you will need to update the environment variables or edit `database.py`:
- Open `database.py`.
- Update `DB_PASSWORD = os.getenv("DB_PASSWORD", "your_password_here")` with your actual MySQL password.

### 4. Run the Application
1. Start the Streamlit application by running:
   ```bash
   streamlit run app.py
   ```
2. Open your web browser to the provided local URL (usually `http://localhost:8501`).

## Deliverables Met:
- **Review 1**: The ER diagram is implicitly represented via the comprehensive DDL provided in `schema.sql`.
- **Review 2**: The normalized database design (up to 3NF) with constraints, data insertion, and queries (demonstrated in `app.py`).
- **Review 3**: The Streamlit application written in Python (`app.py`), connected to the database to handle case management, reporting, error handling, and CRUD operations.
