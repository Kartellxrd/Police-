import streamlit as st
import pandas as pd
import time
import random
from datetime import datetime

# --- 1. PAGE & THEME CONFIGURATION ---
st.set_page_config(
    page_title="Botswana National Intelligence & Crime Records System (NICRS)",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS injection for Dark Mode Command Center Styling
st.markdown("""
<style>
    .reportview-container { background: #0e1117; }
    .metric-card {
        background-color: #1f2937;
        border-left: 5px solid #3b82f6;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.3);
    }
    .critical-card {
        background-color: #3b0712;
        border-left: 5px solid #ef4444;
        padding: 15px;
        border-radius: 8px;
    }
    .success-card {
        background-color: #064e3b;
        border-left: 5px solid #10b981;
        padding: 15px;
        border-radius: 8px;
    }
    .restricted-card {
        background-color: #1f2937;
        border-left: 5px solid #f59e0b;
        padding: 15px;
        border-radius: 8px;
    }
    h1, h2, h3 { font-family: 'Courier New', Courier, monospace; color: #f3f4f6; }
</style>
""", unsafe_allow_html=True)

# --- 2. GLOBAL STATE (SIMULATED CENTRAL DATA NETWORK) ---
if "STATIONS" not in st.session_state:
    st.session_state.STATIONS = {
        1: {"name": "Gaborone Central CPS", "city": "Gaborone", "code": "GABS-01", "lat": -24.6282, "lon": 25.9231},
        2: {"name": "Francistown Phase IV", "city": "Francistown", "code": "FTWN-02", "lat": -21.1670, "lon": 27.5084},
        3: {"name": "Maun Central Station", "city": "Maun", "code": "MAUN-03", "lat": -19.9956, "lon": 23.4163},
        4: {"name": "Palapye Police Station", "city": "Palapye", "code": "PAL-04", "lat": -22.5500, "lon": 27.1167}
    }

# Demo staff directory -> backs the login + role-based access control (RBAC) layer.
# NOTE: plaintext demo passwords are for prototype/grading purposes only and are
# never how the production design (Argon2-hashed, see SADD) would work.
if "STAFF_USERS" not in st.session_state:
    st.session_state.STAFF_USERS = {
        "BPS-10001": {"password": "demo123", "first_name": "Kelebogile", "last_name": "Tau",
                      "station_id": 1, "role": "Desk_Officer"},
        "BPS-20002": {"password": "demo123", "first_name": "Onkemetse", "last_name": "Seretse",
                      "station_id": 2, "role": "Station_Commander"},
        "BPS-30003": {"password": "demo123", "first_name": "Naledi", "last_name": "Kgosi",
                      "station_id": 3, "role": "CID_Detective"},
        "BPS-99999": {"password": "admin123", "first_name": "Tshepo", "last_name": "Modise",
                      "station_id": 1, "role": "System_Admin"},
    }

if "SUSPECTS" not in st.session_state:
    st.session_state.SUSPECTS = {
        "123456789": {"first_name": "Thabo", "last_name": "Molefi", "dob": "1992-05-14", "gender": "Male", "risk_level": "HIGH RISK", "biometric_id": "FP-88A-92"},
        "987654321": {"first_name": "Lesedi", "last_name": "Phiri", "dob": "1995-11-23", "gender": "Female", "risk_level": "LOW RISK", "biometric_id": "FP-12B-45"},
        "555444333": {"first_name": "Kabelo", "last_name": "Ntuane", "dob": "1988-08-08", "gender": "Male", "risk_level": "CRITICAL / WANTED", "biometric_id": "FP-99F-01"}
    }

if "CRIMES" not in st.session_state:
    st.session_state.CRIMES = [
        {
            "case_id": "CR-2026-001",
            "omang": "123456789",
            "station_id": 1, 
            "crime_type": "Armed Robbery",
            "description": "Targeted a local electronics store in Gaborone Main Mall. Armed with a handgun. Fled on foot.",
            "date_committed": "2026-03-15 14:20:00",
            "status": "Warrant Active"
        },
        {
            "case_id": "CR-2026-002",
            "omang": "987654321",
            "station_id": 4, 
            "crime_type": "Fraud",
            "description": "Passed off falsified mobile money receipts to local apparel retailers.",
            "date_committed": "2026-05-10 09:15:00",
            "status": "Under Investigation"
        },
        {
            "case_id": "CR-2026-003",
            "omang": "555444333",
            "station_id": 2,
            "crime_type": "Stock Theft",
            "description": "Suspect allegedly moved livestock across district lines without permits.",
            "date_committed": "2026-04-02 06:40:00",
            "status": "Warrant Active"
        }
    ]

if "ALERTS" not in st.session_state:
    st.session_state.ALERTS = [
        {"time": "08:30 AM", "msg": "RED ALERT: Suspect Kabelo Ntuane spotted near Francistown railway station area."},
        {"time": "11:15 AM", "msg": "System Broadcast: Central server patch deployed successfully across all 4 nodes."}
    ]

if "AUDIT_LOG" not in st.session_state:
    st.session_state.AUDIT_LOG = []

if "current_user" not in st.session_state:
    st.session_state.current_user = None  # dict: staff_id, first_name, last_name, station_id, role


def log_audit(action, detail, result="SUCCESS"):
    """Append a tamper-evident style audit row. Every search, login, and
    write action gets logged here regardless of whether it succeeded or
    was blocked by an RLS policy."""
    user = st.session_state.current_user
    st.session_state.AUDIT_LOG.insert(0, {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "staff_id": user["staff_id"] if user else "UNAUTHENTICATED",
        "name": f"{user['first_name']} {user['last_name']}" if user else "-",
        "role": user["role"] if user else "-",
        "action": action,
        "detail": detail,
        "result": result,
    })


def has_clearance(crime):
    """Row-Level Security simulation: mirrors a Postgres RLS policy such as
    `USING (origin_station_id = current_setting('app.station_id') OR
            current_setting('app.role') IN ('CID_Detective','System_Admin'))`
    A Desk_Officer / Station_Commander may only see crime rows logged at
    their own station. CID_Detective and System_Admin see everything."""
    user = st.session_state.current_user
    if user["role"] in ("CID_Detective", "System_Admin"):
        return True
    return crime["station_id"] == user["station_id"]


# --- 3. LOGIN GATE ---
if st.session_state.current_user is None:
    st.markdown("<br>", unsafe_allow_html=True)
    col_l1, col_l2, col_l3 = st.columns([1, 1.4, 1])
    with col_l2:
        st.markdown("## 🛡️ NICRS Secure Terminal Login")
        st.caption("National Intelligence & Crime Records System — Authorized Personnel Only")
        with st.form("login_form"):
            staff_id_input = st.text_input("Staff ID", placeholder="e.g. BPS-10001")
            password_input = st.text_input("Password", type="password")
            login_submit = st.form_submit_button("🔐 AUTHENTICATE", use_container_width=True)

        if login_submit:
            record = st.session_state.STAFF_USERS.get(staff_id_input)
            if record and record["password"] == password_input:
                st.session_state.current_user = {"staff_id": staff_id_input, **record}
                log_audit("LOGIN", "Successful authentication from terminal.", "SUCCESS")
                st.rerun()
            else:
                log_audit("LOGIN", f"Failed login attempt for staff_id={staff_id_input}", "DENIED")
                st.error("❌ Invalid Staff ID or password. This attempt has been logged.")

        with st.expander("🧪 Demo accounts (for grading / testing only)"):
            st.write("Try logging in as different roles to see how access changes:")
            demo_df = pd.DataFrame([
                {"Staff ID": sid, "Password": v["password"], "Role": v["role"],
                 "Station": st.session_state.STATIONS[v["station_id"]]["city"]}
                for sid, v in st.session_state.STAFF_USERS.items()
            ])
            st.dataframe(demo_df, hide_index=True, use_container_width=True)
    st.stop()

user = st.session_state.current_user
station_lookup = st.session_state.STATIONS
home_station = station_lookup[user["station_id"]]

# --- 4. SIDEBAR CONTROLLER (THE LAW ENFORCEMENT TERMINAL) ---
st.sidebar.markdown("# 🛂 SYSTEM CONTROL")
st.sidebar.markdown(f"""
<div style='background-color:#111827; padding:15px; border-radius:5px; border:1px solid #374151;'>
    <p style='color:#9ca3af; margin:0;'>AUTHENTICATED OFFICER:</p>
    <p style='color:#3b82f6; font-weight:bold; font-size:16px; margin:0;'>{user['first_name']} {user['last_name']}</p>
    <p style='color:#9ca3af; margin:0; margin-top:8px;'>ROLE / CLEARANCE:</p>
    <p style='color:#f59e0b; font-weight:bold; margin:0;'>{user['role'].replace('_',' ')}</p>
    <p style='color:#9ca3af; margin:0; margin-top:8px;'>HOME STATION:</p>
    <p style='color:#10b981; font-weight:bold; margin:0;'>{home_station['name']}</p>
</div>
""", unsafe_allow_html=True)
st.sidebar.write("")
if st.sidebar.button("🚪 LOG OUT", use_container_width=True):
    log_audit("LOGOUT", "Officer ended session.", "SUCCESS")
    st.session_state.current_user = None
    st.rerun()

st.sidebar.write("---")
if user["role"] in ("CID_Detective", "System_Admin"):
    current_station_id = st.sidebar.selectbox(
        "Active Terminal Location (nationwide clearance):",
        options=list(station_lookup.keys()),
        format_func=lambda x: f"📍 {station_lookup[x]['city']} ({station_lookup[x]['code']})"
    )
else:
    current_station_id = user["station_id"]
    st.sidebar.caption(f"📍 Terminal locked to your assigned station: **{home_station['city']}**")

current_station = station_lookup[current_station_id]

st.sidebar.markdown(f"""
<div style='background-color:#111827; padding:15px; border-radius:5px; border:1px solid #374151; margin-top:10px;'>
    <p style='color:#9ca3af; margin:0;'>OPERATIONAL NODE:</p>
    <p style='color:#3b82f6; font-weight:bold; font-size:16px; margin:0;'>{current_station['name']}</p>
    <p style='color:#9ca3af; margin:0; margin-top:10px;'>ENCRYPTION STATUS:</p>
    <p style='color:#10b981; font-weight:bold; margin:0;'>🔒 AES-256 SECURED</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.write("---")
st.sidebar.markdown("### 🚨 LIVE SERVER ALERTS")
for alert in st.session_state.ALERTS:
    st.sidebar.caption(f"⏱️ **{alert['time']}** - {alert['msg']}")

# --- 5. TOP-LEVEL ANALYTICS DASHBOARD ---
st.title("🛡️ NATIONAL INTELLIGENCE & CRIME RECORDS SYSTEM")
st.caption("🚨 PROTOTYPE ENVIRONMENT // RESTRICTED ACCESS // MINISTRY OF DEFENSE & SECURITY")

visible_crimes = [c for c in st.session_state.CRIMES if has_clearance(c)]

col_a, col_b, col_c, col_d = st.columns(4)
with col_a:
    st.markdown(f"<div class='metric-card'><p style='color:#9ca3af; margin:0;'>CONNECTED NODES</p><h2 style='margin:0; color:#3b82f6;'>{len(station_lookup)} Stations</h2></div>", unsafe_allow_html=True)
with col_b:
    label = "OFFENSES VISIBLE TO YOU" if user["role"] not in ("CID_Detective", "System_Admin") else "TOTAL RECORDED OFFENSES"
    st.markdown(f"<div class='metric-card'><p style='color:#9ca3af; margin:0;'>{label}</p><h2 style='margin:0; color:#3b82f6;'>{len(visible_crimes)} Cases</h2></div>", unsafe_allow_html=True)
with col_c:
    st.markdown(f"<div class='metric-card'><p style='color:#9ca3af; margin:0;'>NATIONAL REGISTRY SIZE</p><h2 style='margin:0; color:#3b82f6;'>{len(st.session_state.SUSPECTS)} Profiles</h2></div>", unsafe_allow_html=True)
with col_d:
    warrants = len([c for c in visible_crimes if c["status"] == "Warrant Active"])
    st.markdown(f"<div class='critical-card'><p style='color:#fca5a5; margin:0;'>ACTIVE WARRANTS (IN SCOPE)</p><h2 style='margin:0; color:#ef4444;'>{warrants} Critical</h2></div>", unsafe_allow_html=True)

st.write("---")

# --- 6. INTERACTIVE INTERFACE TABS ---
tab_labels = [
    "🔍 INTER-DISTRICT SEARCH (WOW EFFECT)",
    "🧬 BIOMETRIC DIGITAL SCANNER",
    "📝 RECORD NEW OFFENSE ENTRY",
    "🗄️ LIVE CENTRAL LEDGER",
    "🗺️ STATION & INCIDENT MAP",
]
if user["role"] in ("Station_Commander", "CID_Detective", "System_Admin"):
    tab_labels.append("📋 AUDIT TRAIL")
else:
    tab_labels.append("📋 MY ACTIVITY LOG")

tabs = st.tabs(tab_labels)
T = dict(zip(tab_labels, tabs))

# ==================== TAB 1: INTER-DISTRICT LOOKUP ====================
with T["🔍 INTER-DISTRICT SEARCH (WOW EFFECT)"]:
    st.header("⚡ Instant Cross-District Background Check")
    st.write("Query the secure central database instantly. Results are filtered live by a Row-Level Security (RLS) policy tied to your role and home station.")
    
    search_omang = st.text_input("💳 Enter Suspect Omang Number (Try: 123456789, 987654321, or 555444333):", max_chars=9, placeholder="e.g., 123456789").strip()
    
    if search_omang:
        if search_omang in st.session_state.SUSPECTS:
            profile = st.session_state.SUSPECTS[search_omang]
            log_audit("SEARCH", f"Queried national registry for Omang {search_omang}", "SUCCESS")
            
            if "CRITICAL" in profile["risk_level"]:
                card_style = "critical-card"
                badge_color = "🔴"
            elif "HIGH" in profile["risk_level"]:
                card_style = "critical-card"
                badge_color = "🟠"
            else:
                card_style = "success-card"
                badge_color = "🟢"
                
            st.markdown(f"""
            <div class='{card_style}'>
                <h3>{badge_color} CENTRAL REGISTRY IDENTITY MATCH: {profile['first_name'].upper()} {profile['last_name'].upper()}</h3>
                <p style='margin:0;'><b>OMANG:</b> {search_omang} | <b>DOB:</b> {profile['dob']} | <b>GENDER:</b> {profile['gender']} | <b>BIOMETRIC TOKEN:</b> {profile['biometric_id']} | <b>STATUS:</b> {profile['risk_level']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("<br>", unsafe_allow_html=True)
            
            st.markdown("### 🤖 Automated AI Intelligence Analysis")
            with st.spinner("AI Engine cross-referencing regional patterns..."):
                time.sleep(0.6) 
                if search_omang == "123456789":
                    st.warning("⚠️ **AI Modus Operandi Warning:** Threat profile exhibits high mobility between urban transport hubs. Suspect history shows high likelihood of moving northward toward Francistown along the A1 highway corridor immediately after executing high-value commercial burglaries.")
                elif search_omang == "555444333":
                    st.error("🚨 **CRITICAL RISK ANALYSIS:** Suspect is actively evading local law enforcement. Highest trend vector suggests hideouts in Northern district zones. Exercise extreme caution during routine field questioning.")
                else:
                    st.info("ℹ️ **AI Analysis:** Low-frequency offender history. Standard tracking protocols apply. No cross-district migration alerts flag at this time.")

            st.write("### 📜 Historical Dossier (filtered by your clearance)")
            
            all_matches = [c for c in st.session_state.CRIMES if c["omang"] == search_omang]
            visible_matches = [c for c in all_matches if has_clearance(c)]
            restricted_count = len(all_matches) - len(visible_matches)

            if visible_matches:
                history = []
                for crime in visible_matches:
                    stat_info = station_lookup[crime["station_id"]]
                    history.append({
                        "Case ID": crime["case_id"],
                        "Offense Classification": crime["crime_type"],
                        "Arresting / Logging Node": stat_info["name"],
                        "District / Town": stat_info["city"],
                        "Official Case Log / Narrative": crime["description"],
                        "Timestamp Sync": crime["date_committed"],
                        "Current Legal Status": crime["status"]
                    })
                df = pd.DataFrame(history)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("No prior incidents visible within your clearance scope for this profile.")

            if restricted_count > 0:
                st.markdown(f"""
                <div class='restricted-card'>
                <b>🔒 ROW-LEVEL SECURITY NOTICE:</b> {restricted_count} additional case record(s) exist
                for this individual at other stations, but are hidden because they fall outside your
                role/station clearance. Escalate to a CID Detective or System Admin for nationwide access.
                </div>
                """, unsafe_allow_html=True)
                log_audit("SEARCH", f"{restricted_count} case row(s) hidden by RLS for Omang {search_omang}", "RLS_RESTRICTED")
        else:
            st.error("❌ NO DATABASE CORRELATION FOUND: This Omang number is not allocated inside the active national repository database.")
            log_audit("SEARCH", f"No match for Omang {search_omang}", "NOT_FOUND")

# ==================== TAB 2: BIOMETRIC SCANNER ====================
with T["🧬 BIOMETRIC DIGITAL SCANNER"]:
    st.header("🧬 Forensic Biometric Scan System")
    st.write("Simulates linking a physical forensic thumbprint scanner terminal to the national mainframe database instantly.")
    
    col_scan1, col_scan2 = st.columns([1, 2])
    with col_scan1:
        st.markdown("""
        <div style='background-color:#1f2937; padding:30px; text-align:center; border-radius:10px; border:2px dashed #4b5563;'>
            <h1 style='font-size:70px; margin:0; padding:0;'>🖐️</h1>
            <p style='color:#9ca3af; margin-top:10px;'>HARDWARE LINK STEADY</p>
        </div>
        """, unsafe_allow_html=True)
        scan_click = st.button("🔴 TRIGGER DIGITAL SCANNER TERMINAL")
        
    with col_scan2:
        if scan_click:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for percent_complete in range(100):
                time.sleep(0.01) 
                progress_bar.progress(percent_complete + 1)
                if percent_complete < 30:
                    status_text.text("⚡ Initiating laser array matrix scanner...")
                elif percent_complete < 70:
                    status_text.text("📡 Querying National Biometric Database Core nodes...")
                else:
                    status_text.text("🔏 Analyzing structural ridge configurations...")
            
            status_text.text("✅ Biometric Verification Success!")
            
            matched_omang = "123456789"
            profile = st.session_state.SUSPECTS[matched_omang]
            log_audit("BIOMETRIC_SCAN", f"Scanner matched profile to Omang {matched_omang}", "SUCCESS")
            
            st.success(f"🎯 **BIOMETRIC IDENTITY LOCK:** Found 99.8% Match token: **{profile['biometric_id']}**")
            st.write(f"**Identity:** {profile['first_name']} {profile['last_name']} ({profile['gender']})")
            st.write(f"**National ID Core ID (Omang):** {matched_omang}")
            st.info("💡 *How this works in the demo:* The biometric profile immediately extracted the citizen's primary national data key, allowing the system to instantly pull up their full histories across Gaborone or any outer branch station.")

# ==================== TAB 3: LOG NEW INCIDENT ====================
with T["📝 RECORD NEW OFFENSE ENTRY"]:
    st.header(f"📝 Incident Capture Terminal — {current_station['city']}")
    st.write(f"Any records typed below will be committed directly to the shared ledger network. Every branch in Botswana permitted to see this station's data will see it immediately.")
    
    with st.form("crime_log_form", clear_on_submit=True):
        crime_log_form = st.container() # Create structural internal container context
        col_form1, col_form2 = st.columns(2)
        with col_form1:
            input_omang = st.text_input("Suspect Omang Number:", placeholder="e.g., 123456789").strip()
            input_type = st.selectbox("Offense Category:", ["Armed Robbery", "Assault / GBH", "Theft / Burglary", "Cybercrime / Fraud", "Stock Theft", "Traffic Malfeasance"])
        with col_form2:
            input_desc = st.text_area("Detailed Case Manifest (Modus Operandi, Items Stolen, Physical Context):")
            
        # FIXED: Changed from 'st.form_submit_with_button' to explicit container form binder method
        submitted = st.form_submit_button("🛡️ BROADCAST CRIME TO CENTRAL NETWORK")
        
        if submitted:
            if not input_omang or not input_desc:
                st.error("❌ Submission Failed: Active database security parameters require all form data fields to be complete.")
                log_audit("LOG_INCIDENT", "Submission rejected — missing fields", "DENIED")
            elif input_omang not in st.session_state.SUSPECTS:
                st.warning("⚠️ Access Restrained: This identifier profile does not exist in the civil registry ledger database. Register civilian data before attaching crime rows.")
                log_audit("LOG_INCIDENT", f"Rejected — unknown Omang {input_omang}", "DENIED")
            else:
                new_case_id = f"CR-2026-{len(st.session_state.CRIMES) + 1:03d}"
                st.session_state.CRIMES.append({
                    "case_id": new_case_id,
                    "omang": input_omang,
                    "station_id": current_station_id, 
                    "crime_type": input_type,
                    "description": input_desc,
                    "date_committed": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "status": "Warrant Active"
                })
                
                st.session_state.ALERTS.insert(0, {
                    "time": datetime.now().strftime("%H:%M %p"),
                    "msg": f"🚨 NEW INCIDENT: {input_type} logged at {current_station['city']} Node against ID {input_omang}!"
                })
                log_audit("LOG_INCIDENT", f"Created {new_case_id} ({input_type}) for Omang {input_omang} at {current_station['city']}", "SUCCESS")
                
                st.balloons()
                st.success(f"🛰️ **CRIME RECONCILIATION SUCCESSFUL:** Case row **{new_case_id}** is now deployed to the Cloud Central Engine. System terminal states across Gaborone, Francistown, and Maun have completely harmonized their states.")

# ==================== TAB 4: CENTRAL LEDGER OVERVIEW ====================
with T["🗄️ LIVE CENTRAL LEDGER"]:
    st.header("🗄️ Raw Mainframe System Database Ledger Tables")
    st.write("This section shows the raw system ledger data to prove to stakeholders that data is structured relationally, clean, and fully cloud-ready.")
    
    if user["role"] in ("CID_Detective", "System_Admin"):
        st.caption("Nationwide clearance: showing all stations' raw rows.")
        ledger_crimes = st.session_state.CRIMES
    else:
        hidden_count = len(st.session_state.CRIMES) - len([c for c in st.session_state.CRIMES if c["station_id"] == current_station_id])
        st.markdown(f"""<div class='restricted-card'>🔒 RLS ACTIVE: showing only rows where
        <code>origin_station_id = {current_station_id}</code> ({current_station['city']}).
        {hidden_count} row(s) from other stations are hidden.</div>""", unsafe_allow_html=True)
        ledger_crimes = [c for c in st.session_state.CRIMES if c["station_id"] == current_station_id]
        log_audit("VIEW_LEDGER", f"Viewed station-scoped ledger ({len(ledger_crimes)} rows)", "SUCCESS")

    st.write("#### 📜 Central Incident Log (`crime_records` Table)")
    if ledger_crimes:
        st.dataframe(pd.DataFrame(ledger_crimes), use_container_width=True, hide_index=True)
    else:
        st.info("No active logs in scope.")
    
    col_led1, col_led2 = st.columns(2)
    with col_led1:
        st.write("#### 👤 National Biometric Registry Data (`suspects` Table)")
        st.json(st.session_state.SUSPECTS)
    with col_led2:
        st.write("#### 🏢 Node Infrastructure Directory (`stations` Table)")
        st.json(st.session_state.STATIONS)

# ==================== TAB 5: STATION & INCIDENT MAP ====================
with T["🗺️ STATION & INCIDENT MAP"]:
    st.header("🗺️ National Station Network & Incident Geography")
    st.write("All four stations are shown for situational awareness. Incident markers respect the same RLS clearance rules as the search and ledger tabs.")

    station_df = pd.DataFrame([
        {"lat": s["lat"], "lon": s["lon"], "label": s["name"]} for s in station_lookup.values()
    ])
    st.write("##### 📍 Station Nodes")
    st.map(station_df, latitude="lat", longitude="lon", size=200, color="#3b82f6")

    scoped_crimes = [c for c in st.session_state.CRIMES if has_clearance(c)]
    if scoped_crimes:
        incident_rows = []
        for c in scoped_crimes:
            s = station_lookup[c["station_id"]]
            incident_rows.append({"lat": s["lat"], "lon": s["lon"], "case": c["case_id"], "type": c["crime_type"]})
        incident_df = pd.DataFrame(incident_rows)
        st.write("##### 🚨 Incident Markers (within your clearance)")
        st.map(incident_df, latitude="lat", longitude="lon", size=400, color="#ef4444")
        with st.expander("View incident list behind these markers"):
            st.dataframe(incident_df.rename(columns={"case": "Case ID", "type": "Offense"}), hide_index=True, use_container_width=True)
    else:
        st.info("No incidents within your clearance scope to plot.")

# ==================== TAB 6: AUDIT TRAIL ====================
audit_tab_label = "📋 AUDIT TRAIL" if user["role"] in ("Station_Commander", "CID_Detective", "System_Admin") else "📋 MY ACTIVITY LOG"
with T[audit_tab_label]:
    if user["role"] in ("Station_Commander", "CID_Detective", "System_Admin"):
        st.header("📋 System-Wide Audit Trail")
        st.write("Every login, search, restricted-access attempt, and write action across the network — this is what makes the audit trail described in the SADD tamper-evident.")
        log_rows = st.session_state.AUDIT_LOG
    else:
        st.header("📋 My Activity Log")
        st.write("Desk Officers can review their own actions, but not the full network audit trail — that requires Station_Commander clearance or above.")
        log_rows = [r for r in st.session_state.AUDIT_LOG if r["staff_id"] == user["staff_id"]]

    if log_rows:
        df_log = pd.DataFrame(log_rows)
        result_filter = st.multiselect("Filter by result:", options=sorted(df_log["result"].unique()), default=list(df_log["result"].unique()))
        st.dataframe(df_log[df_log["result"].isin(result_filter)], use_container_width=True, hide_index=True)
    else:
        st.info("No activity logged yet this session.")
