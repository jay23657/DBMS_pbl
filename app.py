import streamlit as st
import pandas as pd
import datetime
import database as db

# Page setup
st.set_page_config(
    page_title="Police Complaint & Evidence Tracking System",
    page_icon="🚔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for clean, professional, non-generic styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .main-header {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .main-header h1 {
        color: #f8fafc !important;
        font-size: 22px !important;
        font-weight: 700 !important;
        margin: 0 !important;
    }

    .main-header p {
        color: #94a3b8;
        font-size: 13px;
        margin: 4px 0 0 0;
    }

    .station-tag {
        background: #0f172a;
        border: 1px solid #38bdf8;
        color: #38bdf8;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.5px;
    }

    .section-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 18px 20px;
        margin-bottom: 20px;
    }

    .section-card h3 {
        color: #f1f5f9;
        font-size: 16px !important;
        font-weight: 600 !important;
        margin-top: 0 !important;
        margin-bottom: 14px !important;
    }

    /* Style dataframe headers and rows */
    div[data-testid="stDataFrame"] {
        border: 1px solid #334155;
        border-radius: 8px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

# Top Bar Header
st.markdown("""
<div class="main-header">
    <div>
        <h1>🚔 Police Complaint & Evidence Tracking System</h1>
        <p>Station Records Management, Investigation Diary & Chain-of-Custody Tracking</p>
    </div>
    <div class="station-tag">
        CENTRAL STATION • DIVISION 1
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar Navigation
sidebar_nav = st.sidebar.radio(
    "Navigation",
    [
        "📊 Dashboard & Analytics",
        "📂 Cases & Details",
        "📝 Register New Complaint",
        "👮 Officers & Assignments",
        "🔍 Evidence Tracking",
        "🔒 Detention & Custody",
        "⚖️ Status & Court Updates",
        "📑 SQL Queries & Reports"
    ]
)

st.sidebar.markdown("---")
st.sidebar.caption("Connected to MySQL (`police_db`) | 3NF Schema")

# -------------------------------------------------------------
# 1. DASHBOARD & ANALYTICS
# -------------------------------------------------------------
if sidebar_nav == "📊 Dashboard & Analytics":
    # Key Summary Metrics
    try:
        total_c = db.fetch_data("SELECT COUNT(*) AS c FROM Complaints;")[0]['c']
        pending_c = db.fetch_data("SELECT COUNT(*) AS c FROM Complaints WHERE status = 'pending';")[0]['c']
        investigating_c = db.fetch_data("SELECT COUNT(*) AS c FROM Complaints WHERE status = 'under_investigation';")[0]['c']
        closed_c = db.fetch_data("SELECT COUNT(*) AS c FROM Complaints WHERE status = 'closed';")[0]['c']
        evidence_c = db.fetch_data("SELECT COUNT(*) AS c FROM EvidenceItems;")[0]['c']
        custody_c = db.fetch_data("SELECT COUNT(*) AS c FROM CustodyLogs WHERE check_out_time IS NULL;")[0]['c']
    except Exception as e:
        st.error(f"Error fetching dashboard statistics: {e}")
        total_c, pending_c, investigating_c, closed_c, evidence_c, custody_c = 0, 0, 0, 0, 0, 0

    # Metric Row
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    m1.metric("Total Cases", total_c)
    m2.metric("Pending Intake", pending_c)
    m3.metric("Under Investigation", investigating_c)
    m4.metric("Closed Cases", closed_c)
    m5.metric("Evidence Items", evidence_c)
    m6.metric("Active Custody", custody_c)

    st.markdown("<br>", unsafe_allow_html=True)

    # Visual Charts Row
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown('<div class="section-card"><h3>Case Distribution by Status</h3>', unsafe_allow_html=True)
        try:
            status_df = db.fetch_data("""
                SELECT status AS Status, COUNT(*) AS Cases
                FROM Complaints
                GROUP BY status;
            """)
            if status_df:
                df_stat = pd.DataFrame(status_df).set_index("Status")
                st.bar_chart(df_stat, color="#38bdf8")
            else:
                st.info("No cases available for chart.")
        except Exception as e:
            st.error(f"Error: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

    with chart_col2:
        st.markdown('<div class="section-card"><h3>Officer Workload (Assigned Active Cases)</h3>', unsafe_allow_html=True)
        try:
            workload_df = db.fetch_data("""
                SELECT 
                    CONCAT(o.first_name, ' ', o.last_name) AS Officer,
                    COUNT(a.assignment_id) AS `Active Cases`
                FROM Officers o
                LEFT JOIN Assignments a ON o.officer_id = a.officer_id
                LEFT JOIN Complaints c ON a.complaint_id = c.complaint_id AND c.status != 'closed'
                GROUP BY o.officer_id
                ORDER BY `Active Cases` DESC;
            """)
            if workload_df:
                df_wl = pd.DataFrame(workload_df).set_index("Officer")
                st.bar_chart(df_wl, color="#818cf8")
            else:
                st.info("No officer workload data.")
        except Exception as e:
            st.error(f"Error: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

    # Secondary Chart: Evidence by Storage Facility
    chart_col3, chart_col4 = st.columns(2)

    with chart_col3:
        st.markdown('<div class="section-card"><h3>Evidence Storage Locations</h3>', unsafe_allow_html=True)
        try:
            evi_loc_df = db.fetch_data("""
                SELECT current_location AS Location, COUNT(*) AS Items
                FROM EvidenceItems
                GROUP BY current_location;
            """)
            if evi_loc_df:
                df_el = pd.DataFrame(evi_loc_df).set_index("Location")
                st.bar_chart(df_el, color="#34d399")
            else:
                st.info("No evidence registered.")
        except Exception as e:
            st.error(f"Error: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

    with chart_col4:
        st.markdown('<div class="section-card"><h3>Recent Case Timeline</h3>', unsafe_allow_html=True)
        try:
            recent_timeline = db.fetch_data("""
                SELECT 
                    sh.change_date AS `Timestamp`,
                    c.title AS `Case Title`,
                    sh.status AS `Status`,
                    sh.remarks AS `Remarks`
                FROM StatusHistories sh
                JOIN Complaints c ON sh.complaint_id = c.complaint_id
                ORDER BY sh.change_date DESC
                LIMIT 5;
            """)
            if recent_timeline:
                st.dataframe(pd.DataFrame(recent_timeline), hide_index=True)
            else:
                st.info("No status history found.")
        except Exception as e:
            st.error(f"Error: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

    # Master Case Table with Filter
    st.markdown('<div class="section-card"><h3>Active Complaints Overview</h3>', unsafe_allow_html=True)
    try:
        complaints_table = db.fetch_data("""
            SELECT 
                c.complaint_id AS `Case ID`,
                c.title AS `Title`,
                c.status AS `Status`,
                c.incident_date AS `Incident Date`,
                c.filed_date AS `Filed Date`,
                (SELECT COUNT(*) FROM Assignments a WHERE a.complaint_id = c.complaint_id) AS `Assigned Officers`,
                (SELECT COUNT(*) FROM EvidenceItems e WHERE e.complaint_id = c.complaint_id) AS `Evidence Items`
            FROM Complaints c
            ORDER BY c.complaint_id DESC;
        """)
        if complaints_table:
            st.dataframe(pd.DataFrame(complaints_table), hide_index=True)
        else:
            st.info("No complaints found.")
    except Exception as e:
        st.error(f"Error: {e}")
    st.markdown('</div>', unsafe_allow_html=True)


# -------------------------------------------------------------
# 2. CASES & DETAILS
# -------------------------------------------------------------
elif sidebar_nav == "📂 Cases & Details":
    st.markdown("### 📂 Case Record & Dossier Search")
    
    try:
        all_cases = db.fetch_data("SELECT complaint_id, title, status, incident_date, filed_date, description, closure_details FROM Complaints ORDER BY complaint_id DESC")
    except Exception as e:
        st.error(f"Error: {e}")
        all_cases = []

    if all_cases:
        # Search & Filter
        search_col, filter_col = st.columns([2, 1])
        with search_col:
            search_query = st.text_input("Search Cases by Title or Keyword", placeholder="Type title keywords...")
        with filter_col:
            status_filter = st.selectbox("Filter by Status", ["All Statuses", "pending", "under_investigation", "closed", "referred_to_court"])

        filtered_cases = all_cases
        if search_query:
            filtered_cases = [c for c in filtered_cases if search_query.lower() in c['title'].lower() or search_query.lower() in (c['description'] or "").lower()]
        if status_filter != "All Statuses":
            filtered_cases = [c for c in filtered_cases if c['status'] == status_filter]

        st.caption(f"Showing {len(filtered_cases)} cases")
        
        # Display main filtered table
        if filtered_cases:
            df_disp = pd.DataFrame(filtered_cases)[['complaint_id', 'title', 'status', 'incident_date', 'filed_date']]
            df_disp.columns = ['ID', 'Case Title', 'Status', 'Incident Date', 'Filed Date']
            st.dataframe(df_disp, hide_index=True)

            st.markdown("---")
            st.markdown("#### Inspect Individual Case File")
            
            case_options = {f"Case #{c['complaint_id']}: {c['title']}": c['complaint_id'] for c in filtered_cases}
            selected_case_name = st.selectbox("Select Case File to View Details", list(case_options.keys()))
            selected_id = case_options[selected_case_name]

            # Fetch selected case record
            c_info = next(c for c in filtered_cases if c['complaint_id'] == selected_id)

            # Details Summary Card
            col_d1, col_d2, col_d3 = st.columns([2, 1, 1])
            with col_d1:
                st.write(f"**Title:** {c_info['title']}")
                st.write(f"**Incident Summary:** {c_info['description']}")
            with col_d2:
                st.write(f"**Status:** `{c_info['status']}`")
                st.write(f"**Incident Date:** {c_info['incident_date']}")
            with col_d3:
                st.write(f"**Filed Date:** {c_info['filed_date']}")
                st.write(f"**Closure Details:** {c_info['closure_details'] or 'N/A'}")

            st.markdown("<br>", unsafe_allow_html=True)

            # Sub-tables inside tabs
            tab_off, tab_act, tab_ev, tab_wit, tab_chg, tab_hist = st.tabs([
                "Assigned Officers", 
                "Investigation Log", 
                "Evidence Items", 
                "Witnesses", 
                "Charges & Court", 
                "Status History"
            ])

            with tab_off:
                assigned = db.fetch_data("""
                    SELECT 
                        CONCAT(o.first_name, ' ', o.last_name) AS `Officer Name`,
                        o.badge_number AS `Badge #`,
                        o.rank AS `Rank`,
                        a.role AS `Assigned Role`,
                        a.assignment_date AS `Date Assigned`,
                        o.contact_number AS `Phone`
                    FROM Assignments a
                    JOIN Officers o ON a.officer_id = o.officer_id
                    WHERE a.complaint_id = %s;
                """, (selected_id,))
                if assigned:
                    st.dataframe(pd.DataFrame(assigned), hide_index=True)
                else:
                    st.info("No officers assigned to this case.")

            with tab_act:
                activities = db.fetch_data("""
                    SELECT 
                        ia.activity_date AS `Date & Time`,
                        CONCAT(o.first_name, ' ', o.last_name) AS `Logged By`,
                        ia.description AS `Activity Details`
                    FROM InvestigationActivities ia
                    LEFT JOIN Officers o ON ia.officer_id = o.officer_id
                    WHERE ia.complaint_id = %s
                    ORDER BY ia.activity_date DESC;
                """, (selected_id,))
                if activities:
                    st.dataframe(pd.DataFrame(activities), hide_index=True)
                else:
                    st.info("No investigation activities recorded.")

            with tab_ev:
                ev_items = db.fetch_data("""
                    SELECT 
                        e.evidence_id AS `Evidence ID`,
                        e.description AS `Description`,
                        e.collection_date AS `Collection Date`,
                        e.current_location AS `Current Storage Location`,
                        CONCAT(o.first_name, ' ', o.last_name) AS `Collected By`
                    FROM EvidenceItems e
                    LEFT JOIN Officers o ON e.collected_by = o.officer_id
                    WHERE e.complaint_id = %s;
                """, (selected_id,))
                if ev_items:
                    st.dataframe(pd.DataFrame(ev_items), hide_index=True)
                else:
                    st.info("No evidence registered for this case.")

            with tab_wit:
                witness_rows = db.fetch_data("""
                    SELECT 
                        CONCAT(p.first_name, ' ', p.last_name) AS `Witness Name`,
                        p.contact_number AS `Contact Phone`,
                        w.statement_date AS `Date Recorded`,
                        w.statement AS `Statement`
                    FROM Witnesses w
                    JOIN Persons p ON w.person_id = p.person_id
                    WHERE w.complaint_id = %s;
                """, (selected_id,))
                if witness_rows:
                    st.dataframe(pd.DataFrame(witness_rows), hide_index=True)
                else:
                    st.info("No witness statements recorded.")

            with tab_chg:
                c1, c2 = st.columns(2)
                with c1:
                    charges_data = db.fetch_data("""
                        SELECT 
                            CONCAT(p.first_name, ' ', p.last_name) AS `Accused Person`,
                            c.description AS `Charge / Penal Code`
                        FROM Charges c
                        JOIN Persons p ON c.person_id = p.person_id
                        WHERE c.complaint_id = %s;
                    """, (selected_id,))
                    st.write("**Penal Charges:**")
                    if charges_data:
                        st.dataframe(pd.DataFrame(charges_data), hide_index=True)
                    else:
                        st.info("No charges filed.")
                with c2:
                    court_data = db.fetch_data("""
                        SELECT court_name AS `Court`, hearing_date AS `Hearing Date`, case_number AS `Docket #`
                        FROM CourtReferences
                        WHERE complaint_id = %s;
                    """, (selected_id,))
                    st.write("**Court Docket References:**")
                    if court_data:
                        st.dataframe(pd.DataFrame(court_data), hide_index=True)
                    else:
                        st.info("No court references linked.")

            with tab_hist:
                status_history = db.fetch_data("""
                    SELECT change_date AS `Timestamp`, status AS `Status`, remarks AS `Remarks`
                    FROM StatusHistories
                    WHERE complaint_id = %s
                    ORDER BY change_date DESC;
                """, (selected_id,))
                if status_history:
                    st.dataframe(pd.DataFrame(status_history), hide_index=True)
                else:
                    st.info("No status history found.")
        else:
            st.warning("No cases match your filter criteria.")
    else:
        st.info("No cases registered in the system.")


# -------------------------------------------------------------
# 3. REGISTER NEW COMPLAINT
# -------------------------------------------------------------
elif sidebar_nav == "📝 Register New Complaint":
    st.markdown("### 📝 Register New Complaint (FIR)")
    
    with st.form("register_complaint_form"):
        st.write("##### Complaint Details")
        c_title = st.text_input("Complaint Title / Subject*", placeholder="e.g. Theft of motor vehicle from residential parking")
        c_desc = st.text_area("Incident Description*", placeholder="Provide details of incident, suspect description, vehicles, etc.")
        
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            c_date = st.date_input("Date of Incident*", value=datetime.date.today())
        with col_c2:
            c_status = st.selectbox("Initial Status", ["pending", "under_investigation"])

        st.write("##### Optional: Assign Lead Officer")
        officers = db.fetch_data("SELECT officer_id, first_name, last_name, rank FROM Officers")
        officer_dict = {"-- None (Assign Later) --": None}
        for o in officers:
            officer_dict[f"{o['rank']} {o['first_name']} {o['last_name']} (ID: {o['officer_id']})"] = o['officer_id']
        
        assigned_officer_key = st.selectbox("Assign Lead Detective", list(officer_dict.keys()))
        assign_role = st.text_input("Role Title", value="Lead Investigator")

        submit_btn = st.form_submit_button("Submit & Register Complaint", type="primary")

        if submit_btn:
            if not c_title or not c_desc:
                st.error("Please fill in both the Title and Description fields.")
            else:
                try:
                    # Insert complaint
                    _, new_id = db.execute_query("""
                        INSERT INTO Complaints (title, description, incident_date, status)
                        VALUES (%s, %s, %s, %s);
                    """, (c_title, c_desc, c_date, c_status))

                    # Insert initial status history
                    db.execute_query("""
                        INSERT INTO StatusHistories (complaint_id, status, remarks)
                        VALUES (%s, %s, 'Case filed and entered into system');
                    """, (new_id, c_status))

                    # Assign officer if chosen
                    off_id = officer_dict[assigned_officer_key]
                    if off_id:
                        db.execute_query("""
                            INSERT INTO Assignments (complaint_id, officer_id, assignment_date, role)
                            VALUES (%s, %s, %s, %s);
                        """, (new_id, off_id, datetime.date.today(), assign_role))

                    st.success(f"Complaint registered successfully with ID #{new_id}!")
                except Exception as e:
                    st.error(f"Error saving to database: {e}")


# -------------------------------------------------------------
# 4. OFFICERS & ASSIGNMENTS
# -------------------------------------------------------------
elif sidebar_nav == "👮 Officers & Assignments":
    st.markdown("### 👮 Officers, Workload & Investigation Log")

    tab_assign, tab_log, tab_roster = st.tabs([
        "Assign Officer to Case", 
        "Log Investigation Activity", 
        "Officer Workload & Roster"
    ])

    with tab_assign:
        st.write("##### Assign Detective or Field Officer")
        cases = db.fetch_data("SELECT complaint_id, title FROM Complaints WHERE status != 'closed'")
        officers = db.fetch_data("SELECT officer_id, first_name, last_name, rank FROM Officers")
        
        if cases and officers:
            c_map = {f"#{c['complaint_id']} - {c['title']}": c['complaint_id'] for c in cases}
            o_map = {f"{o['rank']} {o['first_name']} {o['last_name']}": o['officer_id'] for o in officers}
            
            with st.form("assign_form"):
                sel_case = st.selectbox("Select Case", list(c_map.keys()))
                sel_off = st.selectbox("Select Officer", list(o_map.keys()))
                sel_role = st.selectbox("Role", ["Lead Investigator", "Assisting Detective", "Forensics Specialist", "Field Officer"])
                assign_date = st.date_input("Assignment Date", value=datetime.date.today())
                
                assign_btn = st.form_submit_button("Confirm Assignment", type="primary")
                if assign_btn:
                    c_id = c_map[sel_case]
                    o_id = o_map[sel_off]
                    try:
                        db.execute_query("""
                            INSERT INTO Assignments (complaint_id, officer_id, assignment_date, role)
                            VALUES (%s, %s, %s, %s);
                        """, (c_id, o_id, assign_date, sel_role))
                        
                        # Automatically update status to 'under_investigation' if pending
                        db.execute_query("""
                            UPDATE Complaints SET status = 'under_investigation'
                            WHERE complaint_id = %s AND status = 'pending';
                        """, (c_id,))

                        st.success(f"Officer assigned successfully to Case #{c_id}!")
                    except Exception as e:
                        st.error(f"Error: {e}")
        else:
            st.info("No active cases or officers available.")

    with tab_log:
        st.write("##### Record Investigation Event / Diary Entry")
        if cases and officers:
            with st.form("activity_form"):
                sel_case = st.selectbox("Associated Case", list(c_map.keys()))
                sel_off = st.selectbox("Officer Logging Entry", list(o_map.keys()))
                act_text = st.text_area("Activity Details", placeholder="e.g. Conducted site inspection; retrieved security footage; interrogated suspect.")
                
                log_btn = st.form_submit_button("Save Activity Log", type="primary")
                if log_btn:
                    if act_text:
                        try:
                            db.execute_query("""
                                INSERT INTO InvestigationActivities (complaint_id, officer_id, description)
                                VALUES (%s, %s, %s);
                            """, (c_map[sel_case], o_map[sel_off], act_text))
                            st.success("Investigation activity saved successfully!")
                        except Exception as e:
                            st.error(f"Error: {e}")
                    else:
                        st.warning("Please provide activity details.")

    with tab_roster:
        st.write("##### Police Officers Roster")
        roster_df = db.fetch_data("""
            SELECT 
                o.officer_id AS `ID`,
                o.badge_number AS `Badge #`,
                CONCAT(o.first_name, ' ', o.last_name) AS `Name`,
                o.rank AS `Rank`,
                o.contact_number AS `Contact Phone`,
                COUNT(a.assignment_id) AS `Total Assigned Cases`
            FROM Officers o
            LEFT JOIN Assignments a ON o.officer_id = a.officer_id
            GROUP BY o.officer_id
            ORDER BY `Total Assigned Cases` DESC;
        """)
        if roster_df:
            st.dataframe(pd.DataFrame(roster_df), hide_index=True)


# -------------------------------------------------------------
# 5. EVIDENCE TRACKING
# -------------------------------------------------------------
elif sidebar_nav == "🔍 Evidence Tracking":
    st.markdown("### 🔍 Forensic Evidence & Vault Inventory")

    tab_ev_reg, tab_ev_list = st.tabs(["Register New Evidence", "Evidence Inventory & Storage"])

    with tab_ev_reg:
        st.write("##### Add Evidence Item to Case")
        cases = db.fetch_data("SELECT complaint_id, title FROM Complaints")
        officers = db.fetch_data("SELECT officer_id, first_name, last_name FROM Officers")
        
        if cases and officers:
            c_map = {f"#{c['complaint_id']} - {c['title']}": c['complaint_id'] for c in cases}
            o_map = {f"{o['first_name']} {o['last_name']}": o['officer_id'] for o in officers}
            
            with st.form("register_evidence_form"):
                sel_case = st.selectbox("Associated Case", list(c_map.keys()))
                ev_desc = st.text_input("Evidence Description*", placeholder="e.g. 9mm shell casing, latent fingerprint lift card, recovered mobile phone")
                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    ev_date = st.date_input("Date Seized / Collected", value=datetime.date.today())
                    ev_off = st.selectbox("Collecting Officer", list(o_map.keys()))
                with col_e2:
                    ev_loc = st.text_input("Storage Vault / Locker Location*", placeholder="e.g. Vault Room 2, Locker A-12, Forensics Lab Safe")
                
                submit_ev = st.form_submit_button("Register Evidence", type="primary")
                if submit_ev:
                    if ev_desc and ev_loc:
                        try:
                            db.execute_query("""
                                INSERT INTO EvidenceItems (complaint_id, description, collection_date, collected_by, current_location)
                                VALUES (%s, %s, %s, %s, %s);
                            """, (c_map[sel_case], ev_desc, ev_date, o_map[ev_off], ev_loc))
                            st.success("Evidence item registered successfully!")
                        except Exception as e:
                            st.error(f"Error: {e}")
                    else:
                        st.warning("Please provide Description and Storage Location.")

    with tab_ev_list:
        st.write("##### Complete Evidence Inventory")
        ev_all = db.fetch_data("""
            SELECT 
                e.evidence_id AS `Evidence ID`,
                c.title AS `Case`,
                e.description AS `Description`,
                e.current_location AS `Vault / Locker`,
                e.collection_date AS `Date Collected`,
                CONCAT(o.first_name, ' ', o.last_name) AS `Collected By`
            FROM EvidenceItems e
            JOIN Complaints c ON e.complaint_id = c.complaint_id
            LEFT JOIN Officers o ON e.collected_by = o.officer_id
            ORDER BY e.evidence_id DESC;
        """)
        if ev_all:
            st.dataframe(pd.DataFrame(ev_all), hide_index=True)
        else:
            st.info("No evidence registered.")


# -------------------------------------------------------------
# 6. DETENTION & CUSTODY
# -------------------------------------------------------------
elif sidebar_nav == "🔒 Detention & Custody":
    st.markdown("### 🔒 Detention Logs, Custody Transfer & Witnesses")

    tab_active, tab_checkin, tab_checkout, tab_wit = st.tabs([
        "Active Custody Register", 
        "Book Suspect (Check-in)", 
        "Release / Transfer (Check-out)", 
        "Witness Statements"
    ])

    with tab_active:
        st.write("##### Detention Records")
        custody_data = db.fetch_data("""
            SELECT 
                cl.log_id AS `Log #`,
                CONCAT(p.first_name, ' ', p.last_name) AS `Person Name`,
                p.role AS `Role`,
                cl.location AS `Holding Cell`,
                cl.check_in_time AS `Check-in Time`,
                cl.check_out_time AS `Check-out Time`,
                TIMESTAMPDIFF(HOUR, cl.check_in_time, COALESCE(cl.check_out_time, NOW())) AS `Hours Detained`,
                CONCAT(o.first_name, ' ', o.last_name) AS `Supervising Officer`
            FROM CustodyLogs cl
            JOIN Persons p ON cl.person_id = p.person_id
            LEFT JOIN Officers o ON cl.officer_id = o.officer_id
            ORDER BY cl.check_in_time DESC;
        """)
        if custody_data:
            st.dataframe(pd.DataFrame(custody_data), hide_index=True)
        else:
            st.info("No custody records.")

    with tab_checkin:
        st.write("##### Book Suspect into Holding Facility")
        persons = db.fetch_data("SELECT person_id, first_name, last_name, role FROM Persons")
        officers = db.fetch_data("SELECT officer_id, first_name, last_name FROM Officers")
        
        if persons and officers:
            p_map = {f"{p['first_name']} {p['last_name']} ({p['role']}) - ID: {p['person_id']}": p['person_id'] for p in persons}
            o_map = {f"{o['first_name']} {o['last_name']}": o['officer_id'] for o in officers}
            
            with st.form("checkin_form"):
                sel_p = st.selectbox("Person to Detain", list(p_map.keys()))
                sel_o = st.selectbox("Supervising Officer", list(o_map.keys()))
                h_loc = st.text_input("Holding Location*", value="Holding Cell 1")
                
                checkin_btn = st.form_submit_button("Check-in Suspect", type="primary")
                if checkin_btn:
                    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    try:
                        db.execute_query("""
                            INSERT INTO CustodyLogs (person_id, officer_id, check_in_time, location)
                            VALUES (%s, %s, %s, %s);
                        """, (p_map[sel_p], o_map[sel_o], now_str, h_loc))
                        st.success(f"Person checked into {h_loc} at {now_str}!")
                    except Exception as e:
                        st.error(f"Error: {e}")

    with tab_checkout:
        st.write("##### Process Custody Release or Transfer (Check-out)")
        active_detainees = db.fetch_data("""
            SELECT cl.log_id, CONCAT(p.first_name, ' ', p.last_name) AS person_name, cl.location, cl.check_in_time
            FROM CustodyLogs cl
            JOIN Persons p ON cl.person_id = p.person_id
            WHERE cl.check_out_time IS NULL;
        """)
        if active_detainees:
            ad_map = {f"Log #{d['log_id']}: {d['person_name']} (In: {d['location']} since {d['check_in_time']})": d['log_id'] for d in active_detainees}
            with st.form("checkout_form"):
                sel_ad = st.selectbox("Select Detainee to Release / Transfer", list(ad_map.keys()))
                checkout_btn = st.form_submit_button("Record Check-out", type="primary")
                if checkout_btn:
                    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    try:
                        db.execute_query("""
                            UPDATE CustodyLogs 
                            SET check_out_time = %s
                            WHERE log_id = %s;
                        """, (now_str, ad_map[sel_ad]))
                        st.success(f"Check-out time recorded at {now_str}. Custody log closed!")
                    except Exception as e:
                        st.error(f"Error: {e}")
        else:
            st.info("No suspects currently in active detention.")

    with tab_wit:
        st.write("##### Witness Statements")
        cases = db.fetch_data("SELECT complaint_id, title FROM Complaints")
        persons = db.fetch_data("SELECT person_id, first_name, last_name FROM Persons WHERE role = 'witness' OR role = 'other'")
        if not persons:
            persons = db.fetch_data("SELECT person_id, first_name, last_name FROM Persons")
            
        if cases and persons:
            c_map = {f"#{c['complaint_id']} - {c['title']}": c['complaint_id'] for c in cases}
            p_map = {f"{p['first_name']} {p['last_name']} (ID: {p['person_id']})": p['person_id'] for p in persons}
            
            with st.form("witness_form"):
                sel_c = st.selectbox("Associated Case", list(c_map.keys()))
                sel_p = st.selectbox("Witness Person", list(p_map.keys()))
                w_date = st.date_input("Statement Date", value=datetime.date.today())
                w_stmt = st.text_area("Recorded Statement*", placeholder="Enter statement...")
                
                wit_btn = st.form_submit_button("Record Statement", type="primary")
                if wit_btn:
                    if w_stmt:
                        try:
                            db.execute_query("""
                                INSERT INTO Witnesses (complaint_id, person_id, statement, statement_date)
                                VALUES (%s, %s, %s, %s);
                            """, (c_map[sel_c], p_map[sel_p], w_stmt, w_date))
                            st.success("Witness statement recorded successfully!")
                        except Exception as e:
                            st.error(f"Error: {e}")
                    else:
                        st.warning("Please provide a statement.")


# -------------------------------------------------------------
# 7. STATUS & COURT UPDATES
# -------------------------------------------------------------
elif sidebar_nav == "⚖️ Status & Court Updates":
    st.markdown("### ⚖️ Case Status Transitions & Court References")

    tab_status, tab_charges, tab_court = st.tabs([
        "Update Case Status", 
        "File Charges", 
        "Link Court Docket Reference"
    ])

    with tab_status:
        st.write("##### Update Case Status (Enforcing Closure Rule)")
        st.caption("Business Rule: Marking a case as 'closed' requires detailed closure findings.")
        cases = db.fetch_data("SELECT complaint_id, title, status FROM Complaints")
        if cases:
            c_map = {f"#{c['complaint_id']} - {c['title']} (Current: {c['status']})": c for c in cases}
            with st.form("status_form"):
                sel_c_key = st.selectbox("Select Case", list(c_map.keys()))
                curr_c = c_map[sel_c_key]
                new_status = st.selectbox("New Status", ["pending", "under_investigation", "referred_to_court", "closed"])
                remarks = st.text_input("Status Transition Reason / Remarks*", placeholder="e.g. Evidence review completed; case submitted to prosecution")
                closure_text = st.text_area("Closure Details (Mandatory if marking 'closed')", placeholder="Detail verdict, culprit sentencing, restitution, or reason for case closing.")
                
                stat_btn = st.form_submit_button("Update Status", type="primary")
                if stat_btn:
                    if new_status == "closed" and (not closure_text or len(closure_text.strip()) < 5):
                        st.error("Validation Error: Closure details are required when closing a case!")
                    else:
                        c_id = curr_c['complaint_id']
                        try:
                            if new_status == "closed":
                                db.execute_query("""
                                    UPDATE Complaints 
                                    SET status = %s, closure_details = %s
                                    WHERE complaint_id = %s;
                                """, (new_status, closure_text, c_id))
                            else:
                                db.execute_query("""
                                    UPDATE Complaints 
                                    SET status = %s
                                    WHERE complaint_id = %s;
                                """, (new_status, c_id))
                                
                            # Record in history
                            db.execute_query("""
                                INSERT INTO StatusHistories (complaint_id, status, remarks)
                                VALUES (%s, %s, %s);
                            """, (c_id, new_status, remarks or f"Transitioned to {new_status}"))
                            
                            st.success(f"Case #{c_id} status updated to '{new_status}' successfully!")
                        except Exception as e:
                            st.error(f"Error: {e}")

    with tab_charges:
        st.write("##### File Charges against Accused")
        suspects = db.fetch_data("SELECT person_id, first_name, last_name FROM Persons WHERE role = 'suspect'")
        if not suspects:
            suspects = db.fetch_data("SELECT person_id, first_name, last_name FROM Persons")
        cases = db.fetch_data("SELECT complaint_id, title FROM Complaints")
        
        if cases and suspects:
            c_map = {f"#{c['complaint_id']} - {c['title']}": c['complaint_id'] for c in cases}
            s_map = {f"{s['first_name']} {s['last_name']} (ID: {s['person_id']})": s['person_id'] for s in suspects}
            
            with st.form("charge_form"):
                sel_c = st.selectbox("Associated Case", list(c_map.keys()))
                sel_s = st.selectbox("Charged Suspect", list(s_map.keys()))
                chg_desc = st.text_area("Penal Section / Charge Description*", placeholder="e.g. Section 380 - Theft in dwelling house")
                
                chg_btn = st.form_submit_button("File Formal Charge", type="primary")
                if chg_btn:
                    if chg_desc:
                        try:
                            db.execute_query("""
                                INSERT INTO Charges (complaint_id, person_id, description)
                                VALUES (%s, %s, %s);
                            """, (c_map[sel_c], s_map[sel_s], chg_desc))
                            st.success("Charge filed successfully!")
                        except Exception as e:
                            st.error(f"Error: {e}")
                    else:
                        st.warning("Please provide a description.")

    with tab_court:
        st.write("##### Link Court Docket Reference")
        if cases:
            c_map = {f"#{c['complaint_id']} - {c['title']}": c['complaint_id'] for c in cases}
            with st.form("court_form"):
                sel_c = st.selectbox("Case File", list(c_map.keys()))
                court_name = st.text_input("Court Name*", value="District Sessions & Criminal Court")
                case_no = st.text_input("Court Docket / Case #*", placeholder="e.g. CC-2026-4412")
                hearing_date = st.date_input("Scheduled Hearing Date", value=datetime.date.today() + datetime.timedelta(days=14))
                
                court_btn = st.form_submit_button("Link Court Reference", type="primary")
                if court_btn:
                    if court_name and case_no:
                        try:
                            db.execute_query("""
                                INSERT INTO CourtReferences (complaint_id, court_name, hearing_date, case_number)
                                VALUES (%s, %s, %s, %s);
                            """, (c_map[sel_c], court_name, hearing_date, case_no))
                            st.success("Court reference linked successfully!")
                        except Exception as e:
                            st.error(f"Error: {e}")
                    else:
                        st.warning("Please provide Court Name and Case Number.")


# -------------------------------------------------------------
# 8. SQL QUERIES & REPORTS (Academic Deliverables)
# -------------------------------------------------------------
elif sidebar_nav == "📑 SQL Queries & Reports":
    st.markdown("### 📑 Project Queries & Data Reports")
    st.caption("Demonstrates SQL retrieval, multi-table joins, aggregate functions, nested subqueries, and views.")

    rep_selection = st.selectbox("Select SQL Query to Execute", [
        "1. Pending Cases Backlog (Data Retrieval & Filter)",
        "2. Officer Workload (LEFT JOIN & GROUP BY with COUNT)",
        "3. Evidence Locations & Custodians (Multi-Table JOIN)",
        "4. Custody Audit Trail (Duration calculation via TIMESTAMPDIFF)",
        "5. Closed Cases Breakdown (Correlated Nested Subquery)",
        "6. Relational Schema Data Dictionary (3NF Analysis)"
    ])

    if "1. Pending Cases" in rep_selection:
        st.write("##### Query: Pending Cases Backlog")
        st.code("""
SELECT complaint_id, title, description, incident_date, filed_date
FROM Complaints
WHERE status = 'pending'
ORDER BY filed_date ASC;
        """, language="sql")
        res = db.fetch_data("SELECT complaint_id, title, description, incident_date, filed_date FROM Complaints WHERE status = 'pending' ORDER BY filed_date ASC;")
        if res:
            st.dataframe(pd.DataFrame(res), hide_index=True)
        else:
            st.info("No pending cases found.")

    elif "2. Officer Workload" in rep_selection:
        st.write("##### Query: Officer Workload (Join & Aggregation)")
        st.code("""
SELECT 
    CONCAT(o.first_name, ' ', o.last_name) AS officer_name,
    o.badge_number,
    o.rank,
    COUNT(a.assignment_id) AS active_cases
FROM Officers o
LEFT JOIN Assignments a ON o.officer_id = a.officer_id
LEFT JOIN Complaints c ON a.complaint_id = c.complaint_id AND c.status != 'closed'
GROUP BY o.officer_id
ORDER BY active_cases DESC;
        """, language="sql")
        res = db.fetch_data("""
            SELECT 
                CONCAT(o.first_name, ' ', o.last_name) AS officer_name,
                o.badge_number,
                o.rank,
                COUNT(a.assignment_id) AS active_cases
            FROM Officers o
            LEFT JOIN Assignments a ON o.officer_id = a.officer_id
            LEFT JOIN Complaints c ON a.complaint_id = c.complaint_id AND c.status != 'closed'
            GROUP BY o.officer_id
            ORDER BY active_cases DESC;
        """)
        if res:
            df = pd.DataFrame(res)
            st.bar_chart(df.set_index("officer_name")["active_cases"], color="#818cf8")
            st.dataframe(df, hide_index=True)

    elif "3. Evidence Locations" in rep_selection:
        st.write("##### Query: Evidence Storage & Recovering Officers (Multi-Table JOIN)")
        st.code("""
SELECT 
    e.evidence_id,
    e.description AS item_description,
    e.current_location,
    c.title AS case_title,
    CONCAT(o.first_name, ' ', o.last_name) AS collected_by_officer
FROM EvidenceItems e
JOIN Complaints c ON e.complaint_id = c.complaint_id
LEFT JOIN Officers o ON e.collected_by = o.officer_id
ORDER BY e.current_location;
        """, language="sql")
        res = db.fetch_data("""
            SELECT 
                e.evidence_id,
                e.description AS item_description,
                e.current_location,
                c.title AS case_title,
                CONCAT(o.first_name, ' ', o.last_name) AS collected_by_officer
            FROM EvidenceItems e
            JOIN Complaints c ON e.complaint_id = c.complaint_id
            LEFT JOIN Officers o ON e.collected_by = o.officer_id
            ORDER BY e.current_location;
        """)
        if res:
            st.dataframe(pd.DataFrame(res), hide_index=True)

    elif "4. Custody Audit Trail" in rep_selection:
        st.write("##### Query: Custody Records & Duration (Temporal Calculation)")
        st.code("""
SELECT 
    cl.log_id,
    CONCAT(p.first_name, ' ', p.last_name) AS detainee,
    cl.location AS cell_facility,
    cl.check_in_time,
    cl.check_out_time,
    TIMESTAMPDIFF(HOUR, cl.check_in_time, COALESCE(cl.check_out_time, NOW())) AS hours_held,
    CONCAT(o.first_name, ' ', o.last_name) AS supervising_officer
FROM CustodyLogs cl
JOIN Persons p ON cl.person_id = p.person_id
LEFT JOIN Officers o ON cl.officer_id = o.officer_id
ORDER BY cl.check_in_time DESC;
        """, language="sql")
        res = db.fetch_data("""
            SELECT 
                cl.log_id,
                CONCAT(p.first_name, ' ', p.last_name) AS detainee,
                cl.location AS cell_facility,
                cl.check_in_time,
                cl.check_out_time,
                TIMESTAMPDIFF(HOUR, cl.check_in_time, COALESCE(cl.check_out_time, NOW())) AS hours_held,
                CONCAT(o.first_name, ' ', o.last_name) AS supervising_officer
            FROM CustodyLogs cl
            JOIN Persons p ON cl.person_id = p.person_id
            LEFT JOIN Officers o ON cl.officer_id = o.officer_id
            ORDER BY cl.check_in_time DESC;
        """)
        if res:
            st.dataframe(pd.DataFrame(res), hide_index=True)

    elif "5. Closed Cases" in rep_selection:
        st.write("##### Query: Closed Cases with Correlated Nested Subqueries")
        st.code("""
SELECT 
    c.complaint_id,
    c.title,
    c.closure_details,
    (SELECT COUNT(*) FROM EvidenceItems e WHERE e.complaint_id = c.complaint_id) AS total_evidence_items,
    (SELECT COUNT(*) FROM Witnesses w WHERE w.complaint_id = c.complaint_id) AS total_witnesses
FROM Complaints c
WHERE c.status = 'closed';
        """, language="sql")
        res = db.fetch_data("""
            SELECT 
                c.complaint_id,
                c.title,
                c.closure_details,
                (SELECT COUNT(*) FROM EvidenceItems e WHERE e.complaint_id = c.complaint_id) AS total_evidence_items,
                (SELECT COUNT(*) FROM Witnesses w WHERE w.complaint_id = c.complaint_id) AS total_witnesses
            FROM Complaints c
            WHERE c.status = 'closed';
        """)
        if res:
            st.dataframe(pd.DataFrame(res), hide_index=True)
        else:
            st.info("No closed cases found.")

    elif "6. Relational Schema" in rep_selection:
        st.write("##### Schema Data Dictionary (3NF Normalization)")
        tables = [
            ("Complaints", "complaint_id (PK), title, description, incident_date, filed_date, status, closure_details", "Cases and FIRs. CHECK constraint for closure_details if closed."),
            ("Persons", "person_id (PK), first_name, last_name, dob, address, contact_number, role", "Suspects, victims, witnesses. Prevents duplicate entity records."),
            ("Officers", "officer_id (PK), badge_number (UNIQUE), first_name, last_name, rank, contact_number", "Police personnel roster."),
            ("Assignments", "assignment_id (PK), complaint_id (FK), officer_id (FK), assignment_date, role", "Resolves Many-to-Many relationship between Officers and Complaints."),
            ("InvestigationActivities", "activity_id (PK), complaint_id (FK), officer_id (FK), activity_date, description", "Case activity and diary logs."),
            ("EvidenceItems", "evidence_id (PK), complaint_id (FK), description, collection_date, collected_by (FK), current_location", "Chain-of-custody tracking for seized evidence items."),
            ("CustodyLogs", "log_id (PK), person_id (FK), officer_id (FK), check_in_time, check_out_time, location", "Detention log with CHECK (check_out > check_in)."),
            ("Witnesses", "witness_id (PK), complaint_id (FK), person_id (FK), statement, statement_date", "Witness statements linked to complaints."),
            ("CourtReferences", "court_ref_id (PK), complaint_id (FK), court_name, hearing_date, case_number", "Judicial references and hearing dates."),
            ("Charges", "charge_id (PK), complaint_id (FK), person_id (FK), description", "Charges filed against suspects."),
            ("StatusHistories", "history_id (PK), complaint_id (FK), status, change_date, remarks", "Audit trail for complaint status transitions.")
        ]
        df_schema = pd.DataFrame(tables, columns=["Table Name", "Attributes & Keys", "Role in 3NF Normalization & Integrity"])
        st.dataframe(df_schema, hide_index=True)
