import streamlit as st
import json
import os
import hashlib
import time
import random

# --- USER DATABASE FILE ---
USER_DB_FILE = "users.json"

# --- BACKEND FUNCTIONS ---
def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def load_users():
    if not os.path.exists(USER_DB_FILE):
        return {}
    try:
        with open(USER_DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_user(username, password):
    users = load_users()
    users[username] = hash_password(password)
    with open(USER_DB_FILE, "w") as f:
        json.dump(users, f)

def check_credentials(username, password):
    users = load_users()
    if username in users and users[username] == hash_password(password):
        return True
    return False

def reset_password(username, new_password):
    users = load_users()
    if username in users:
        users[username] = hash_password(new_password)
        with open(USER_DB_FILE, "w") as f:
            json.dump(users, f)
        return True
    return False

# --- FRONTEND LOGIN UI ---
def show_login_page():
    # 1. ANIMATION
    leaves_html = ""
    for i in range(25):
        left = random.randint(0, 100)
        dur = random.randint(10, 20)
        delay = random.randint(0, 10)
        leaf = random.choice(["🍃", "🍂", "🌿"])
        leaves_html += f'<div class="leaf" style="left:{left}%; animation-duration:{dur}s; animation-delay:{delay}s;">{leaf}</div>'

    # 2. CSS - SINGLE BLACK LAYER
    st.markdown("""
    <style>
        /* Main Background */
        .stApp {
            background: url('https://images.unsplash.com/photo-1518173946687-a4c8892bbd9f?q=80&w=2574&auto=format&fit=crop');
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }
        
        /* Hide Navbar/Sidebar */
        [data-testid="stSidebar"], header, footer { display: none !important; }
        
        /* Falling Leaves */
        .leaf-container { position: fixed; top:0; left:0; width:100%; height:100%; pointer-events:none; z-index:0; overflow:hidden; }
        .leaf { position: absolute; top: -10%; font-size: 25px; opacity: 0.8; animation: fall linear infinite; }
        @keyframes fall {
            0% { transform: translateY(0) rotate(0deg); opacity: 0; }
            10% { opacity: 1; }
            100% { transform: translateY(110vh) rotate(360deg); opacity: 0; }
        }

        /* --- THE SINGLE BLACK LAYER --- */
        /* Targets the middle column container */
        div[data-testid="column"]:nth-of-type(2) > div {
            background-color: rgba(0, 0, 0, 0.9) !important; /* SOLID BLACK BACKGROUND */
            padding: 40px !important;
            border-radius: 20px !important;
            box-shadow: 0 20px 60px rgba(0,0,0,0.9) !important;
            border: 1px solid #333;
            border-top: 5px solid #4caf50; /* Green accent on top */
        }

        /* --- TYPOGRAPHY (WHITE) --- */
        h1 {
            color: #ffffff !important;
            font-family: sans-serif;
            font-weight: 800;
            text-align: center;
            margin-bottom: 0px;
        }
        p {
            color: #b9f6ca !important; /* Light Green Text */
            font-weight: 600;
            text-align: center;
            margin-bottom: 20px;
        }

        /* --- INPUT FIELDS --- */
        .stTextInput label {
            color: #ffffff !important; /* White Label */
            font-weight: 700 !important;
        }
        div[data-baseweb="input"] > div {
            background-color: #ffffff !important; /* White Input Box */
            border: 1px solid #ccc !important;
            border-radius: 8px !important;
            color: #000000 !important; /* Black Text Inside */
        }
        input {
            color: #000000 !important;
            font-weight: 600 !important;
        }
        
        /* --- TABS --- */
        .stTabs [data-baseweb="tab-list"] { gap: 10px; justify-content: center; }
        .stTabs [data-baseweb="tab"] { color: #888; }
        .stTabs [aria-selected="true"] { 
            color: #4caf50 !important; 
            border-bottom-color: #4caf50 !important; 
        }
        
        /* --- BUTTONS --- */
        div.stButton > button {
            width: 100%;
            background: linear-gradient(135deg, #2e7d32 0%, #66bb6a 100%);
            color: white !important;
            font-weight: bold;
            padding: 12px;
            border-radius: 8px;
            border: none;
            transition: 0.3s;
        }
        div.stButton > button:hover {
            transform: translateY(-3px);
            box-shadow: 0 5px 15px rgba(76, 175, 80, 0.4);
        }
        div.stButton > button p { color: white !important; }
        
        /* Error messages text color */
        .stAlert { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

    # Render Animation
    st.markdown(f'<div class="leaf-container">{leaves_html}</div>', unsafe_allow_html=True)

    # 3. LAYOUT
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        # Title & Subtitle inside the column (sits on the black layer via CSS)
        st.markdown("<h1>🌿 Eco Tourism</h1>", unsafe_allow_html=True)
        st.markdown("<p>Begin your sustainable journey</p>", unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["🔒 Login", "📝 Sign Up", "🔑 Forgot"])
        
        # --- LOGIN ---
        with tab1:
            st.write("")
            username = st.text_input("Username", key="login_u")
            password = st.text_input("Password", type="password", key="login_p")
            st.write("")
            if st.button("Login", key="btn_login"):
                if check_credentials(username, password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success("Success! Loading...")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("Incorrect credentials.")

        # --- SIGN UP ---
        with tab2:
            st.write("")
            new_user = st.text_input("Create Username", key="reg_u")
            new_pass = st.text_input("Create Password", type="password", key="reg_p")
            st.write("")
            if st.button("Sign Up", key="btn_reg"):
                users = load_users()
                if new_user in users:
                    st.warning("Username taken.")
                elif new_user and new_pass:
                    save_user(new_user, new_pass)
                    st.success("Account created! Please Login.")
                else:
                    st.error("Fill all fields.")

        # --- FORGOT PASSWORD ---
        with tab3:
            st.write("")
            st.markdown("<div style='color:white; font-weight:bold; margin-bottom:5px;'>Reset Password</div>", unsafe_allow_html=True)
            reset_user = st.text_input("Confirm Username", key="reset_u")
            reset_pass = st.text_input("New Password", type="password", key="reset_p")
            st.write("")
            if st.button("Update Password", key="btn_reset"):
                if reset_password(reset_user, reset_pass):
                    st.success("Password Updated! Please Login.")
                else:
                    st.error("Username not found.")