import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import pydeck as pdk
import numpy as np
import base64
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2

# ============================================
# 1. PAGE CONFIG (MUST BE FIRST)
# ============================================
st.set_page_config(
    page_title="Eco Tourism Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# 2. SESSION STATE INITIALIZATION (FIXED ORDER)
# ============================================
# This MUST come before the sidebar logic to prevent AttributeError
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'
if 'user_location' not in st.session_state:
    st.session_state.user_location = "Delhi"
if 'user_coords' not in st.session_state:
    st.session_state.user_coords = [77.2090, 28.6139]
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# 3. IMPORT AUTH & CHECK
import auth

if not st.session_state.logged_in:
    auth.show_login_page()
    st.stop()

# ============================================
# 4. UTILITY FUNCTIONS & DATA
# ============================================
def calculate_distance(coord1, coord2):
    """Calculate approximate distance between two coordinates"""
    R = 6371
    lat1, lon1 = radians(coord1[1]), radians(coord1[0])
    lat2, lon2 = radians(coord2[1]), radians(coord2[0])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return int(R * c)

def update_user_location(city):
    if city in INDIAN_CITIES:
        st.session_state.user_location = city
        st.session_state.user_coords = INDIAN_CITIES[city]

# --- DATA DICTIONARIES ---
DESTINATIONS = {
    "Mumbai": {"coords": [72.8777, 19.0760], "distance": 1150, "flight": {"name": "Indigo 6E-201", "price": 5400, "co2": 145, "time": "2h 10m"}, "train": {"name": "Rajdhani Express", "price": 2950, "co2": 35, "time": "15h 30m"}, "bus": {"name": "Volvo AC Sleeper", "price": 1800, "co2": 55, "time": "22h 00m"}},
    "Goa": {"coords": [73.8180, 15.2993], "distance": 1900, "flight": {"name": "SpiceJet SG-101", "price": 6500, "co2": 230, "time": "2h 30m"}, "train": {"name": "Goa Express", "price": 3200, "co2": 48, "time": "24h 00m"}, "bus": {"name": "Neeta Travels", "price": 2200, "co2": 85, "time": "36h 00m"}},
    "Jaipur": {"coords": [75.7873, 26.9124], "distance": 280, "flight": {"name": "Air India AI-403", "price": 3800, "co2": 45, "time": "1h 05m"}, "train": {"name": "Shatabdi Express", "price": 1200, "co2": 12, "time": "4h 30m"}, "bus": {"name": "Rajasthan Roadways", "price": 800, "co2": 18, "time": "6h 30m"}},
    "Varanasi": {"coords": [82.9739, 25.3176], "distance": 820, "flight": {"name": "Vistara UK-701", "price": 5200, "co2": 105, "time": "1h 45m"}, "train": {"name": "Vande Bharat", "price": 2100, "co2": 25, "time": "8h 15m"}, "bus": {"name": "UPSRTC AC", "price": 1500, "co2": 40, "time": "14h 00m"}},
    "Manali": {"coords": [77.1892, 32.2396], "distance": 540, "flight": {"name": "Helicopter Service", "price": 9500, "co2": 90, "time": "1h 30m"}, "train": {"name": "Kalka-Shimla + Bus", "price": 1800, "co2": 22, "time": "16h 00m"}, "bus": {"name": "HRTC Volvo", "price": 1200, "co2": 35, "time": "14h 00m"}},
    "Shimla": {"coords": [77.1734, 31.1048], "distance": 340, "flight": {"name": "Air India", "price": 4500, "co2": 55, "time": "1h 10m"}, "train": {"name": "Kalka-Shimla Toy Train", "price": 800, "co2": 8, "time": "5h 30m"}, "bus": {"name": "HRTC AC", "price": 700, "co2": 15, "time": "8h 00m"}},
    "Udaipur": {"coords": [73.7125, 24.5854], "distance": 660, "flight": {"name": "IndiGo 6E-501", "price": 4800, "co2": 85, "time": "1h 30m"}, "train": {"name": "Mewar Express", "price": 1900, "co2": 20, "time": "12h 00m"}, "bus": {"name": "RSRTC AC", "price": 1400, "co2": 30, "time": "13h 30m"}},
    "Amritsar": {"coords": [74.8723, 31.6340], "distance": 450, "flight": {"name": "SpiceJet SG-301", "price": 4200, "co2": 60, "time": "1h 15m"}, "train": {"name": "Shatabdi Express", "price": 1500, "co2": 15, "time": "6h 00m"}, "bus": {"name": "PRTC AC", "price": 1000, "co2": 25, "time": "9h 00m"}},
    "Rishikesh": {"coords": [78.2676, 30.0869], "distance": 240, "flight": {"name": "Helicopter", "price": 7000, "co2": 40, "time": "1h 00m"}, "train": {"name": "Dehradun Express", "price": 600, "co2": 6, "time": "4h 30m"}, "bus": {"name": "Uttarakhand Transport", "price": 400, "co2": 10, "time": "6h 00m"}},
    "Kolkata": {"coords": [88.3639, 22.5726], "distance": 1500, "flight": {"name": "Air India AI-202", "price": 6200, "co2": 190, "time": "2h 20m"}, "train": {"name": "Rajdhani Express", "price": 3500, "co2": 42, "time": "17h 30m"}, "bus": {"name": "Private AC Sleeper", "price": 2500, "co2": 75, "time": "28h 00m"}},
    "Hyderabad": {"coords": [78.4867, 17.3850], "distance": 1580, "flight": {"name": "IndiGo 6E-601", "price": 5800, "co2": 200, "time": "2h 15m"}, "train": {"name": "Rajdhani Express", "price": 3200, "co2": 40, "time": "20h 00m"}, "bus": {"name": "APSRTC Garuda", "price": 2300, "co2": 65, "time": "24h 00m"}},
    "Bengaluru": {"coords": [77.5946, 12.9716], "distance": 2100, "flight": {"name": "Vistara UK-801", "price": 7200, "co2": 265, "time": "2h 45m"}, "train": {"name": "Rajdhani Express", "price": 4200, "co2": 50, "time": "32h 00m"}, "bus": {"name": "KSRTC Airavat", "price": 3200, "co2": 85, "time": "36h 00m"}},
    "Chennai": {"coords": [80.2707, 13.0827], "distance": 2200, "flight": {"name": "Air India AI-303", "price": 6800, "co2": 275, "time": "2h 50m"}, "train": {"name": "Rajdhani Express", "price": 4500, "co2": 55, "time": "28h 30m"}, "bus": {"name": "TNSTC AC", "price": 3500, "co2": 90, "time": "34h 00m"}},
    "Kochi": {"coords": [76.2711, 9.9312], "distance": 2600, "flight": {"name": "IndiGo 6E-701", "price": 8200, "co2": 325, "time": "3h 30m"}, "train": {"name": "Kerala Express", "price": 4800, "co2": 65, "time": "38h 00m"}, "bus": {"name": "KSRTC AC", "price": 3800, "co2": 105, "time": "48h 00m"}},
    "Leh": {"coords": [77.5771, 34.1526], "distance": 1000, "flight": {"name": "Air India AI-401", "price": 9500, "co2": 130, "time": "1h 30m"}, "train": {"name": "Jammu + Bus", "price": 3500, "co2": 45, "time": "48h 00m"}, "bus": {"name": "HRTC + J&K Transport", "price": 2800, "co2": 70, "time": "36h 00m"}},
    "Srinagar": {"coords": [74.7973, 34.0837], "distance": 800, "flight": {"name": "Vistara UK-901", "price": 8800, "co2": 105, "time": "1h 40m"}, "train": {"name": "Jammu Tawi + Taxi", "price": 3200, "co2": 40, "time": "20h 00m"}, "bus": {"name": "J&K SRTC", "price": 2500, "co2": 50, "time": "18h 00m"}},
    "Agra": {"coords": [78.0081, 27.1767], "distance": 230, "flight": {"name": "N/A", "price": 0, "co2": 0, "time": "0h 00m"}, "train": {"name": "Gatiman Express", "price": 900, "co2": 8, "time": "1h 40m"}, "bus": {"name": "UPSRTC AC Volvo", "price": 600, "co2": 12, "time": "3h 30m"}},
    "Jaisalmer": {"coords": [70.9223, 26.9157], "distance": 800, "flight": {"name": "SpiceJet", "price": 5500, "co2": 95, "time": "1h 40m"}, "train": {"name": "Runicha Express", "price": 1800, "co2": 28, "time": "18h 00m"}, "bus": {"name": "RSRTC Sleeper", "price": 1200, "co2": 45, "time": "16h 00m"}},
    "Darjeeling": {"coords": [88.2627, 27.0410], "distance": 1500, "flight": {"name": "Via Bagdogra", "price": 6000, "co2": 180, "time": "2h 15m"}, "train": {"name": "North East Express", "price": 2800, "co2": 45, "time": "28h 00m"}, "bus": {"name": "Private Volvo", "price": 2200, "co2": 70, "time": "32h 00m"}},
    "Gangtok": {"coords": [88.6138, 27.3389], "distance": 1600, "flight": {"name": "Via Pakyong", "price": 7000, "co2": 190, "time": "2h 30m"}, "train": {"name": "NJP + Taxi", "price": 3000, "co2": 50, "time": "30h 00m"}, "bus": {"name": "NBSTC", "price": 2400, "co2": 80, "time": "35h 00m"}},
    "Ooty": {"coords": [76.6951, 11.4100], "distance": 2300, "flight": {"name": "Via Coimbatore", "price": 7500, "co2": 280, "time": "3h 00m"}, "train": {"name": "Nilgiri Mountain Rail", "price": 4000, "co2": 60, "time": "40h 00m"}, "bus": {"name": "KSRTC", "price": 3200, "co2": 95, "time": "48h 00m"}},
    "Munnar": {"coords": [77.0595, 10.0889], "distance": 2600, "flight": {"name": "Via Kochi", "price": 8000, "co2": 310, "time": "3h 15m"}, "train": {"name": "Kerala Express + Taxi", "price": 4500, "co2": 70, "time": "45h 00m"}, "bus": {"name": "KSRTC Sleeper", "price": 3500, "co2": 110, "time": "50h 00m"}},
    "Pondicherry": {"coords": [79.8145, 11.9416], "distance": 2400, "flight": {"name": "SpiceJet", "price": 7200, "co2": 290, "time": "2h 55m"}, "train": {"name": "Puducherry Exp", "price": 4200, "co2": 65, "time": "42h 00m"}, "bus": {"name": "TNSTC Ultra", "price": 3400, "co2": 100, "time": "46h 00m"}}
}

INDIAN_CITIES = {
    "Delhi": [77.2090, 28.6139], "Mumbai": [72.8777, 19.0760], "Bengaluru": [77.5946, 12.9716],
    "Chennai": [80.2707, 13.0827], "Kolkata": [88.3639, 22.5726], "Hyderabad": [78.4867, 17.3850],
    "Pune": [73.8567, 18.5204], "Ahmedabad": [72.5714, 23.0225], "Jaipur": [75.7873, 26.9124],
    "Lucknow": [80.9462, 26.8467], "Kanpur": [80.3319, 26.4499], "Nagpur": [79.0882, 21.1458],
    "Indore": [75.8577, 22.7196], "Thane": [72.9781, 19.2183], "Bhopal": [77.4126, 23.2599],
    "Visakhapatnam": [83.2185, 17.6868], "Patna": [85.1376, 25.5941], "Vadodara": [73.1812, 22.3072],
    "Ghaziabad": [77.4538, 28.6692], "Ludhiana": [75.8573, 30.9010], "Agra": [78.0081, 27.1767],
    "Nashik": [73.7898, 19.9975], "Faridabad": [77.3178, 28.4089], "Meerut": [77.7064, 28.9845],
    "Rajkot": [70.8029, 22.3039], "Kalyan": [73.1305, 19.2437], "Vasai": [72.7449, 19.3919],
    "Varanasi": [82.9739, 25.3176], "Srinagar": [74.7973, 34.0837], "Aurangabad": [75.3433, 19.8762],
    "Dhanbad": [86.4304, 23.7957], "Amritsar": [74.8723, 31.6340], "Allahabad": [81.8463, 25.4358],
    "Ranchi": [85.3096, 23.3441], "Howrah": [88.2644, 22.5958], "Coimbatore": [76.9558, 11.0168],
    "Jabalpur": [79.9865, 23.1815], "Gwalior": [78.1828, 26.2183], "Vijayawada": [80.6480, 16.5062],
    "Jodhpur": [73.0229, 26.2389], "Madurai": [78.1198, 9.9252], "Raipur": [81.6296, 21.2514],
    "Kota": [75.8648, 25.2138], "Chandigarh": [76.7794, 30.7333], "Guwahati": [91.7430, 26.1445],
    "Solapur": [75.9100, 17.6599], "Hubli": [75.1104, 15.3647], "Bareilly": [79.4150, 28.3670],
    "Moradabad": [78.7757, 28.8388], "Mysore": [76.6394, 12.2958], "Tiruchirappalli": [78.6808, 10.7905],
    "Bhubaneswar": [85.8245, 20.2961], "Salem": [78.1586, 11.6643], "Jamshedpur": [86.2029, 22.8046],
    "Warangal": [79.5882, 17.9689]
}

ACCOMMODATION_OPTIONS = {
    "Luxury Hotel (5-Star)": {"price": 8000, "co2": 60, "booking_link": "https://www.makemytrip.com/hotels/"},
    "Standard Hotel (3-Star)": {"price": 3500, "co2": 25, "booking_link": "https://www.goibibo.com/hotels/"},
    "Budget Hotel": {"price": 2000, "co2": 15, "booking_link": "https://www.oyorooms.com"},
    "Eco-Resort": {"price": 4500, "co2": 10, "booking_link": "https://www.treebo.com"},
    "Hostel/Dormitory": {"price": 800, "co2": 5, "booking_link": "https://www.zostel.com"},
    "Homestay": {"price": 1500, "co2": 8, "booking_link": "https://www.saffronstays.com"},
    "Camping (Tent/Van)": {"price": 1200, "co2": 5, "booking_link": "https://www.campervan.com"},
    "With Relatives": {"price": 0, "co2": 0, "booking_link": "#"}
}

FOOD_OPTIONS = {
    "Fine Dining (Restaurants)": {"price": 3000, "co2": 15, "booking_link": "https://www.eazydiner.com"},
    "Standard Restaurants": {"price": 1500, "co2": 8, "booking_link": "https://www.zomato.com"},
    "Local Street Food": {"price": 500, "co2": 3, "booking_link": "https://www.google.com/maps/search/street+food"},
    "Self-Cooking": {"price": 400, "co2": 2, "booking_link": "https://www.bigbasket.com"},
    "Food Stalls/Dhabas": {"price": 300, "co2": 2, "booking_link": "https://www.google.com/maps/search/dhaba"},
    "With Relatives": {"price": 0, "co2": 0, "booking_link": "#"}
}

# ============================================
# 5. SIDEBAR & THEME INIT
# ============================================
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'
if 'user_location' not in st.session_state:
    st.session_state.user_location = "Delhi"
if 'user_coords' not in st.session_state:
    st.session_state.user_coords = [77.2090, 28.6139]

def apply_theme(theme):
    if theme == 'dark':
        return """
        <style>
            .stApp {
                background: linear-gradient(rgba(0, 20, 10, 0.7), rgba(0, 10, 5, 0.8)), 
                            url('https://images.unsplash.com/photo-1511497584788-876760111969?q=80&w=2670&auto=format&fit=crop');
                background-size: cover; background-attachment: fixed; color: #e0e0e0;
            }
            section[data-testid="stSidebar"] { background: rgba(10, 25, 15, 0.6) !important; border-right: 1px solid rgba(100, 255, 140, 0.1); }
            section[data-testid="stSidebar"] * { color: #e0e0e0 !important; }
            .glass-card { background: rgba(20, 30, 25, 0.75); border: 1px solid rgba(100, 255, 140, 0.15); border-radius: 20px; padding: 24px; margin-bottom: 24px; }
            h1 { background: linear-gradient(90deg, #43e97b, #38f9d7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; }
            .metric-card { background: rgba(0, 0, 0, 0.4); border: 1px solid rgba(255, 255, 255, 0.1); border-left: 4px solid #43e97b; padding: 20px; border-radius: 12px; text-align: center; }
            .metric-value { font-size: 1.8rem; font-weight: bold; color: #fff; }
            .action-btn { color: black !important; background: linear-gradient(90deg, #11998e, #38ef7d); padding: 10px 25px; border-radius: 50px; text-decoration: none; font-weight: 700; display: inline-block; margin: 5px; }
            .stSelectbox div[data-baseweb="select"] > div { background-color: rgba(0,0,0,0.6) !important; color: white !important; border: 1px solid rgba(255,255,255,0.2) !important; }
            div[data-baseweb="popover"], div[data-baseweb="menu"] { background-color: #1a1a1a !important; }
            div[data-baseweb="menu"] div { color: white !important; }
            li[role="option"]:hover { background-color: #43e97b !important; color: black !important; }
        </style>
        """
    else:  
        return """
        <style>
            .stApp {
                background: linear-gradient(rgba(255, 255, 255, 0.85), rgba(255, 255, 255, 0.9)), 
                            url('https://images.unsplash.com/photo-1472214103451-9374bd1c798e?q=80&w=2070&auto=format&fit=crop');
                background-size: cover; background-attachment: fixed; color: #000000; 
            }
            section[data-testid="stSidebar"] { background: rgba(255, 255, 255, 0.95) !important; border-right: 1px solid #ccc; }
            section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] span, section[data-testid="stSidebar"] div { color: #000000 !important; }
            .glass-card { background: rgba(255, 255, 255, 0.95); border: 1px solid #aaa; border-radius: 20px; padding: 24px; margin-bottom: 24px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
            h1 { background: linear-gradient(90deg, #005c35, #009966); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; }
            h2, h3, h4, p, label, .stMarkdown, div, span, li, strong { color: #000000 !important; font-weight: 500; }
            .metric-card { background: #ffffff; border: 1px solid #999; border-left: 4px solid #009966; padding: 20px; border-radius: 12px; text-align: center; }
            .metric-value { font-size: 1.8rem; font-weight: bold; color: #000000 !important; }
            .metric-label { font-size: 0.8rem; color: #333333 !important; font-weight: bold; }
            .stSelectbox div[data-baseweb="select"] > div { background-color: #ffffff !important; color: #000000 !important; border: 1px solid #555 !important; }
            div[data-baseweb="popover"], div[data-baseweb="menu"] { background-color: #ffffff !important; border: 1px solid #555 !important; }
            div[data-baseweb="menu"] div, li[role="option"] { color: #000000 !important; background-color: #ffffff !important; }
            li[role="option"]:hover, li[role="option"][aria-selected="true"] { background-color: #e6f7ff !important; color: #000000 !important; }
            .action-btn { color: white !important; background: linear-gradient(90deg, #005c35, #009966); padding: 10px 25px; border-radius: 50px; text-decoration: none; font-weight: 600; display: inline-block; margin: 5px; }
        </style>
        """

st.markdown(apply_theme(st.session_state.theme), unsafe_allow_html=True)

with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <h2 style="margin-bottom: 5px; background: linear-gradient(90deg, #38ef7d, #11998e); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">🌿 ECO NET</h2>
        <p style="color: #bbb; font-size: 0.9rem;">Sustainable Travel Intelligence</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🎨 Theme Settings")
    theme_options = {"🌙 Dark Mode": "dark", "☀️ Light Mode": "light"}
    selected_theme_label = st.radio("Select Theme", list(theme_options.keys()), index=0 if st.session_state.theme == "dark" else 1, label_visibility="collapsed")
    selected_theme = theme_options[selected_theme_label]
    if selected_theme != st.session_state.theme:
        st.session_state.theme = selected_theme
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 🏠 Your Current Location")
    
    current_city_list = list(INDIAN_CITIES.keys())
    try:
        default_index = current_city_list.index(st.session_state.user_location)
    except ValueError:
        default_index = 0
        
    user_city = st.selectbox("Select your city", current_city_list, index=default_index)
    if user_city != st.session_state.user_location:
        update_user_location(user_city)
    
    st.markdown("---")
    st.markdown("### 🗺️ Trip Destination")
    destination = st.selectbox("Select your destination", ["Select a destination"] + list(DESTINATIONS.keys()))
    
    st.markdown("---")
    if destination != "Select a destination":
        dest_coords = DESTINATIONS[destination]["coords"]
        distance = calculate_distance(st.session_state.user_coords, dest_coords)
        st.markdown(f"""
        <div style="background: rgba(56, 239, 125, 0.1); padding: 15px; border-radius: 10px; margin: 15px 0; border: 1px solid rgba(56, 239, 125, 0.3);">
            <p style="margin: 0; font-size: 0.9rem; color: #e0e0e0;">
            📏 <strong>Distance:</strong> {distance} km<br>
            🚗 <strong>From:</strong> {st.session_state.user_location} → {destination}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 👥 Trip Details")
        travelers = st.slider("Number of travelers", 1, 10, 2)
        days = st.slider("Duration (days)", 1, 30, 5)
        st.markdown("---")
        st.markdown("### 🚗 Your Travel Plan")
        col1, col2 = st.columns(2)
        with col1: transport = st.selectbox("Transport Mode", ["Flight", "Train", "Bus", "Car (Personal)", "Car (Taxi/Rental)"])
        with col2: stay = st.selectbox("Accommodation", list(ACCOMMODATION_OPTIONS.keys()))
        food = st.selectbox("Dining Preference", list(FOOD_OPTIONS.keys()))
        
        st.markdown("---")
        calculate_clicked = st.button("📊 Calculate My Impact", type="primary", use_container_width=True)

    # Logout Button
    st.markdown("---")
    st.write(f"Logged in as: **{st.session_state.username}**")
    if st.button("Log Out"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

# ============================================
# 7. MAIN DASHBOARD CONTENT
# ============================================
user_loc = st.session_state.user_location
header_html = f"""
<div class="main-header">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h1>🌍 ECO TOURISM DASHBOARD</h1>
            <p style='color: #43e97b; font-size: 1.2rem; font-weight: 500;'>Plan sustainable. Travel responsibly. Save the planet.</p>
        </div>
        <div style="display: flex; gap: 15px;">
            <div style="background: rgba(255, 100, 100, 0.15); padding: 10px 20px; border-radius: 20px; border: 1px solid rgba(255, 100, 100, 0.3);">
                🏠 <strong>Departing from:</strong> {user_loc}
            </div>
        </div>
    </div>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)

# --- INFO SECTION ---
st.markdown("""
<div class="glass-card" style="margin-top: 20px;">
    <h3>🌱 What is Eco Net?</h3>
    <p>
        This dashboard helps conscious travelers minimize their carbon footprint while maximizing savings.
        By analyzing distances between <strong>50+ Indian cities</strong> and <strong>23 top destinations</strong>,
        we calculate the environmental impact of Flights, Trains, Buses, and Personal Vehicles.
    </p>
    <ul style="list-style-type: none; padding-left: 0;">
        <li>📊 <strong>Compare:</strong> See real-time cost vs. carbon emission trade-offs.</li>
        <li>💡 <strong>Optimize:</strong> Get AI-driven recommendations for the greenest travel routes.</li>
        <li>🌳 <strong>Impact:</strong> Visualize how many trees you save by choosing eco-friendly options.</li>
    </ul>
    <p style="font-size: 0.9rem; margin-top: 10px; font-weight: bold;">
        👉 Use the Sidebar to select your origin and destination to begin!
    </p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([2, 1, 1])
with col1: st.markdown(f"""<div class="metric-card" style="border-left-color: #00C9FF;"><div class="metric-value">{len(DESTINATIONS)}</div><div class="metric-label">DESTINATIONS</div></div>""", unsafe_allow_html=True)
with col2: st.markdown(f"""<div class="metric-card" style="border-left-color: #43e97b;"><div class="metric-value">{len(INDIAN_CITIES)}</div><div class="metric-label">CITIES</div></div>""", unsafe_allow_html=True)
with col3: st.markdown(f"""<div class="metric-card" style="border-left-color: #FF6B6B;"><div class="metric-value">5,000+</div><div class="metric-label">TREES SAVED</div></div>""", unsafe_allow_html=True)
st.markdown("---")

# --- MAP ---
st.markdown("### 🗺️ Destination Network")
map_data = []
for city, info in DESTINATIONS.items():
    color = [67, 233, 123, 160] if st.session_state.theme == 'dark' else [0, 150, 0, 150]
    radius = 40000
    if destination == city:
        color = [0, 201, 255, 200] if st.session_state.theme == 'dark' else [0, 114, 255, 200]
        radius = 80000
    map_data.append({"coords": info["coords"], "name": city, "color": color, "radius": radius})

map_data.append({"coords": st.session_state.user_coords, "name": f"{st.session_state.user_location} (Home)", "color": [255, 100, 100, 200], "radius": 50000})
layers = [pdk.Layer("ScatterplotLayer", data=map_data, get_position='coords', get_color='color', get_radius='radius', pickable=True)]

if destination != "Select a destination":
    route_data = [{"from": st.session_state.user_coords, "to": DESTINATIONS[destination]["coords"], "name": f"{st.session_state.user_location} → {destination}"}]
    layers.append(pdk.Layer("ArcLayer", data=route_data, get_source_position="from", get_target_position="to", get_source_color=[255, 100, 100], get_target_color=[0, 201, 255], get_width=6, get_tilt=15))

if destination != "Select a destination":
    dest_coords = DESTINATIONS[destination]["coords"]
    center_lat = (st.session_state.user_coords[1] + dest_coords[1]) / 2
    center_lon = (st.session_state.user_coords[0] + dest_coords[0]) / 2
    zoom = 4.0
else:
    center_lat, center_lon, zoom = 22.0, 79.0, 3.5

st.pydeck_chart(pdk.Deck(map_style="mapbox://styles/mapbox/dark-v10" if st.session_state.theme == 'dark' else "mapbox://styles/mapbox/light-v10", initial_view_state=pdk.ViewState(latitude=center_lat, longitude=center_lon, zoom=zoom, pitch=40), layers=layers, tooltip={"text": "{name}"}))

# --- CALCULATION RESULTS ---
if destination != "Select a destination" and 'calculate_clicked' in locals() and calculate_clicked:
    dest_info = DESTINATIONS[destination]
    try:
        distance = calculate_distance(st.session_state.user_coords, dest_info["coords"])
        car_speed_avg = 60
        car_time_hours = int(distance / car_speed_avg)
        car_time_str = f"{car_time_hours}h {int((distance % car_speed_avg))}m"
        base_delhi_distance = dest_info["distance"]
        distance_ratio = distance / base_delhi_distance if base_delhi_distance > 0 else 1
        
        transport_options_map = {
            "Flight": {"name": dest_info["flight"]["name"], "price_per_person": int(dest_info["flight"]["price"] * distance_ratio), "co2_per_person": int(dest_info["flight"]["co2"] * distance_ratio), "time": dest_info["flight"]["time"], "type": "Flight"},
            "Train": {"name": dest_info["train"]["name"], "price_per_person": int(dest_info["train"]["price"] * distance_ratio), "co2_per_person": int(dest_info["train"]["co2"] * distance_ratio), "time": dest_info["train"]["time"], "type": "Train"},
            "Bus": {"name": dest_info["bus"]["name"], "price_per_person": int(dest_info["bus"]["price"] * distance_ratio), "co2_per_person": int(dest_info["bus"]["co2"] * distance_ratio), "time": dest_info["bus"]["time"], "type": "Bus"},
            "Car (Personal)": {"name": "Personal Vehicle", "price_total_trip": distance * 15, "price_is_per_person": False, "co2_total_trip": distance * 0.15, "co2_is_per_person": False, "time": car_time_str, "type": "Car (Personal)"},
            "Car (Taxi/Rental)": {"name": "Taxi / Rental", "price_total_trip": distance * 22, "price_is_per_person": False, "co2_total_trip": distance * 0.15, "co2_is_per_person": False, "time": car_time_str, "type": "Car (Taxi/Rental)"}
        }
        
        user_trans_data = transport_options_map[transport]
        if user_trans_data.get("price_is_per_person", True):
            transport_cost = user_trans_data["price_per_person"] * travelers
            transport_co2 = user_trans_data["co2_per_person"] * travelers
        else:
            vehicles_needed = np.ceil(travelers / 4)
            transport_cost = user_trans_data["price_total_trip"] * vehicles_needed
            transport_co2 = user_trans_data["co2_total_trip"] * vehicles_needed
        transport_name = user_trans_data["name"]

        stay_cost = ACCOMMODATION_OPTIONS[stay]["price"] * days
        stay_co2 = ACCOMMODATION_OPTIONS[stay]["co2"] * days
        food_cost = FOOD_OPTIONS[food]["price"] * days * travelers
        food_co2 = FOOD_OPTIONS[food]["co2"] * days * travelers
        user_total_cost = transport_cost + stay_cost + food_cost
        user_total_co2 = transport_co2 + stay_co2 + food_co2
        
        all_combinations = []
        for t_key, t_data in transport_options_map.items():
            for s_key, s_data in ACCOMMODATION_OPTIONS.items():
                if stay != "With Relatives" and s_key == "With Relatives": continue
                if stay == "With Relatives" and s_key != "With Relatives": continue
                for f_key, f_data in FOOD_OPTIONS.items():
                    if food != "With Relatives" and f_key == "With Relatives": continue
                    if food == "With Relatives" and f_key != "With Relatives": continue
                    if t_data.get("price_is_per_person", True):
                        t_c = t_data["price_per_person"] * travelers
                        t_e = t_data["co2_per_person"] * travelers
                    else:
                        v_n = np.ceil(travelers / 4)
                        t_c = t_data["price_total_trip"] * v_n
                        t_e = t_data["co2_total_trip"] * v_n
                    s_c = s_data["price"] * days
                    s_e = s_data["co2"] * days
                    f_c = f_data["price"] * days * travelers
                    f_e = f_data["co2"] * days * travelers
                    tot_c = t_c + s_c + f_c
                    tot_e = t_e + s_e + f_e
                    eco_score = (tot_c / 1000) + (tot_e * 0.5)
                    all_combinations.append({"transport": t_key, "stay": s_key, "food": f_key, "total_cost": tot_c, "total_co2": tot_e, "transport_name": t_data["name"], "transport_cost": t_c, "stay_cost": s_c, "food_cost": f_c, "eco_score": eco_score})
        
        all_combinations.sort(key=lambda x: x["eco_score"])
        best_eco_combinations = all_combinations[:3] if all_combinations else [all_combinations[0]]
        eco_combo = best_eco_combinations[0]
        
        user_is_already_eco = (eco_combo["transport"] == transport and eco_combo["stay"] == stay and eco_combo["food"] == food)
        eco_transport = eco_combo["transport"]
        eco_stay = eco_combo["stay"]
        eco_food = eco_combo["food"]
        eco_transport_name = eco_combo["transport_name"]
        eco_transport_cost = eco_combo["transport_cost"]
        eco_stay_cost = eco_combo["stay_cost"]
        eco_food_cost = eco_combo["food_cost"]
        eco_total_cost = eco_combo["total_cost"]
        eco_total_co2 = eco_combo["total_co2"]
        
        savings = user_total_cost - eco_total_cost
        co2_savings = user_total_co2 - eco_total_co2
        
        if user_total_co2 > 0:
            percent_reduction = (co2_savings / user_total_co2) * 100
        else:
            percent_reduction = 0
            
        trees_needed = user_total_co2 / 21 if user_total_co2 > 0 else 0
        trees_for_offset = int(trees_needed/21) if trees_needed > 0 else 0
        
        st.markdown("---")
        st.markdown(f"### 📊 Analysis Results: {st.session_state.user_location} → {destination}")
        col1, col2, col3 = st.columns(3)
        with col1: st.markdown(f"""<div class="metric-card" style="border-left-color: #00C9FF;"><div class="metric-value">{distance}</div><div class="metric-label">DISTANCE (KM)</div></div>""", unsafe_allow_html=True)
        with col2: st.markdown(f"""<div class="metric-card" style="border-left-color: #43e97b;"><div class="metric-value">{travelers}</div><div class="metric-label">TRAVELERS</div></div>""", unsafe_allow_html=True)
        with col3: st.markdown(f"""<div class="metric-card" style="border-left-color: #FFD166;"><div class="metric-value">{days}</div><div class="metric-label">DAYS</div></div>""", unsafe_allow_html=True)
        
        if user_is_already_eco:
            st.markdown(f"""<div style="display:flex; align-items:center; margin: 20px 0; background: rgba(67, 233, 123, 0.2); padding: 15px; border-radius: 12px; border: 1px solid #43e97b;"><img src="https://cdn-icons-png.flaticon.com/512/3135/3135715.png" width="60" style="border-radius:50%; margin-right: 15px;"><div><strong>🌿 Eco Assistant:</strong> "Excellent! Your trip is already optimal! You're generating only <strong style='color:#43e97b'>{user_total_co2:.0f} kg CO₂</strong>. Have a safe and sustainable journey!"</div></div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""<div style="display:flex; align-items:center; margin: 20px 0; background: rgba(255, 100, 100, 0.1); padding: 15px; border-radius: 12px; border: 1px solid rgba(255,100,100,0.3);"><img src="https://cdn-icons-png.flaticon.com/512/3135/3135715.png" width="60" style="border-radius:50%; margin-right: 15px;"><div><strong>🌿 Eco Assistant:</strong> "Your current plan generates <strong style='color:#ff6b6b'>{user_total_co2:.0f} kg CO₂</strong>. Consider the eco-alternative below to save <strong style='color:#43e97b'>₹{savings:,}</strong>!"</div></div>""", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""<div class="glass-card"><h3>🚫 Your Current Plan</h3><div style="margin: 20px 0;"><p><strong>Transport:</strong> {transport_name} - ₹{transport_cost:,.0f}</p><p><strong>Stay:</strong> {stay} - ₹{stay_cost:,.0f}</p><p><strong>Food:</strong> {food} - ₹{food_cost:,.0f}</p></div><div style="background: rgba(255, 107, 107, 0.1); padding: 15px; border-radius: 10px;"><h4 style="color: #ff6b6b; margin: 0;">Total: ₹{user_total_cost:,.0f}</h4><p style="color: #ff6b6b; margin: 5px 0 0 0;">Carbon: {user_total_co2:.0f} kg CO₂</p></div></div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""<div class="glass-card"><h3>✅ Recommended Eco Plan</h3><div style="margin: 20px 0;"><p><strong>Transport:</strong> {eco_transport_name} - ₹{eco_transport_cost:,.0f}</p><p><strong>Stay:</strong> {eco_stay} - ₹{eco_stay_cost:,.0f}</p><p><strong>Food:</strong> {eco_food} - ₹{eco_food_cost:,.0f}</p></div><div style="background: rgba(67, 233, 123, 0.15); padding: 15px; border-radius: 10px;"><h4 style="color: #43e97b; margin: 0;">Total: ₹{eco_total_cost:,.0f}</h4><p style="color: #43e97b; margin: 5px 0 0 0;">Carbon: {eco_total_co2:.0f} kg CO₂</p></div></div>""", unsafe_allow_html=True)
            if eco_transport == "Train": transport_link = "https://www.irctc.co.in"
            elif eco_transport == "Bus": transport_link = "https://www.redbus.in"
            elif eco_transport == "Flight": transport_link = "https://www.makemytrip.com/flights/"
            else: transport_link = "#"
            
            food_link = FOOD_OPTIONS[eco_food]['booking_link']
            
            st.markdown(f"""<div style="margin-top: 15px; text-align: center;"><a href="{transport_link}" target="_blank" class="action-btn">🚗 Book {eco_transport} Tickets</a><a href="{ACCOMMODATION_OPTIONS[eco_stay]['booking_link']}" target="_blank" class="action-btn">🏨 Find {eco_stay} Stays</a><a href="{food_link}" target="_blank" class="action-btn">🍽️ Find {eco_food}</a></div>""", unsafe_allow_html=True)
            
        st.markdown("---")
        st.markdown("### 📊 Visual Comparison")
        fig = go.Figure()
        user_color = '#ff6b6b' if st.session_state.theme == 'dark' else '#ff4444'
        eco_color = '#43e97b' if st.session_state.theme == 'dark' else '#00a86b'
        line_color = '#00C9FF' if st.session_state.theme == 'dark' else '#0072ff'
        fig.add_trace(go.Bar(x=['Your Plan', 'Eco Plan'], y=[user_total_cost, eco_total_cost], name='Total Cost (₹)', marker_color=[user_color, eco_color], text=[f'₹{user_total_cost:,.0f}', f'₹{eco_total_cost:,.0f}'], textposition='outside'))
        fig.add_trace(go.Scatter(x=['Your Plan', 'Eco Plan'], y=[user_total_co2, eco_total_co2], name='CO₂ Emissions (kg)', mode='lines+markers', marker=dict(size=12, color=line_color), line=dict(width=3), yaxis='y2'))
        fig.update_layout(template='plotly_dark' if st.session_state.theme == 'dark' else 'plotly_white', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', title=f'Cost vs Carbon Impact: {st.session_state.user_location} → {destination}', xaxis=dict(title='Travel Plan'), yaxis=dict(title='Cost (₹)', color='#e0e0e0' if st.session_state.theme == 'dark' else '#333333'), yaxis2=dict(title='CO₂ Emissions (kg)', color=line_color, overlaying='y', side='right'), legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5), height=400, margin=dict(l=20, r=60, t=60, b=20))
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        st.markdown("### 🚌 Alternative Transport Options")
        cols = st.columns(5)
        display_options = []
        for t_key in ["Flight", "Train", "Bus", "Car (Personal)", "Car (Taxi/Rental)"]:
            data = transport_options_map[t_key]
            if data.get("price_is_per_person", True):
                p = data["price_per_person"] * travelers
                c = data["co2_per_person"] * travelers
            else:
                v_n = np.ceil(travelers / 4)
                p = data["price_total_trip"] * v_n
                c = data["co2_total_trip"] * v_n
            display_options.append({"key": t_key, "data": data, "p": p, "c": c})
        
        for idx, item in enumerate(display_options):
            mode = item["key"]
            data = item["data"]
            with cols[idx]:
                is_current = (transport == mode)
                is_recommended = (eco_transport == mode)
                border_color = "#43e97b" if is_recommended else "#00C9FF" if is_current else "rgba(255,255,255,0.2)"
                bg_color = "rgba(67, 233, 123, 0.1)" if is_recommended else "rgba(0, 201, 255, 0.1)" if is_current else "rgba(255,255,255,0.05)"
                html_content = f"""<div style="border: 1px solid {border_color}; background: {bg_color}; border-radius: 12px; padding: 15px; min-height: 150px; display: flex; flex-direction: column; justify-content: space-between;"><div style="display: flex; justify-content: space-between; align-items: center;"><span style="font-weight:bold; font-size: 0.9rem; color: #e0e0e0;">{mode}</span>{'✅' if is_recommended else '📌' if is_current else ''}</div><p style="margin: 10px 0 5px 0; font-size: 0.8rem; color: #aaa;">{data["name"]}</p><div style="font-size: 0.8rem; color: #e0e0e0;">Price: ₹{item["p"]:,.0f}<br>CO₂: {item["c"]:.0f}kg</div><div style="margin-top: 10px; font-size: 0.75rem; color: #888;">⏱️ {data["time"]}</div></div>"""
                st.markdown(html_content, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 🔄 More Eco Options")
        st.markdown("#### 🌟 Top 3 Eco-Friendly Combinations")
        cols = st.columns(3)
        for i, combo in enumerate(best_eco_combinations[:3]):
            with cols[i]:
                st.markdown(f"""<div style="border: 1px solid rgba(67, 233, 123, 0.4); border-radius: 12px; padding: 15px; background: rgba(67, 233, 123, 0.05);"><div style="display: flex; justify-content: space-between; align-items: center;"><span style="color: #43e97b; font-weight: bold;">Rank #{i+1}</span>{"🥇" if i == 0 else "🥈" if i == 1 else "🥉"}</div><p style="margin: 10px 0 5px 0; font-size: 0.9rem;"><strong>Transport:</strong> {combo['transport']}</p><p style="margin: 5px 0; font-size: 0.9rem;"><strong>Stay:</strong> {combo['stay']}</p><p style="margin: 5px 0; font-size: 0.9rem;"><strong>Food:</strong> {combo['food']}</p><div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-top: 10px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 5px;"><span>Cost: ₹{combo['total_cost']:,.0f}</span><span>CO₂: {combo['total_co2']:.0f}kg</span></div></div>""", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # --- RANK NAME AND DESCRIPTION LOGIC ---
        if percent_reduction >= 50: 
            rank_name, rank_color, badge_icon = "🌱 Guardian of the Earth", "linear-gradient(135deg, #00b09b, #96c93d)", "👑"
            rank_desc = "Outstanding! You are slashing carbon emissions in half. A true protector of the planet."
        elif percent_reduction >= 20: 
            rank_name, rank_color, badge_icon = "🌿 Eco Warrior", "linear-gradient(135deg, #4facfe, #00f2fe)", "🛡️"
            rank_desc = "Great job! You are making significant strides towards sustainable travel."
        else: 
            rank_name, rank_color, badge_icon = "🍂 Conscious Traveler", "linear-gradient(135deg, #f093fb, #f5576c)", "🚶"
            rank_desc = "You are aware of your impact. Small steps lead to big changes."
        
        st.markdown(f"""<div style="text-align: center; margin-bottom: 30px;"><h2 style="background: -webkit-linear-gradient(90deg, #00C9FF, #43e97b); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">🚀 YOUR CLIMATE IMPACT HUB</h2><p style="color: #888;">Turn your travel savings into real-world action.</p></div>""", unsafe_allow_html=True)
        col1, col2 = st.columns([1, 1.5])
        with col1:
            badge_html = f"""<div style="background: rgba(255,255,255,0.05); border-radius: 20px; padding: 30px; border: 1px solid rgba(255,255,255,0.1); position: relative; overflow: hidden; height: 100%;"><div style="background: {rank_color}; position: absolute; top: 0; left: 0; width: 100%; height: 5px;"></div><div style="font-size: 4rem; margin-top: 10px; text-align: center;">{badge_icon}</div><h2 style="margin: 10px 0; font-size: 1.5rem; background: {rank_color}; -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center;">{rank_name}</h2><p style="font-size: 0.9rem; color: #aaa; margin-bottom: 20px; text-align: center;">{rank_desc}</p><hr style="border-color: rgba(255,255,255,0.1);"><div style="display: flex; width: 100%; margin-top: 10px; background: rgba(0,0,0,0.2); border-radius: 10px;"><div style="flex: 1; text-align: center; padding: 15px; border-right: 1px solid rgba(255,255,255,0.1);"><div style="font-size: 1.5rem; font-weight: bold; color: #fff;">{co2_savings:.0f} kg</div><div style="font-size: 0.8rem; color: #43e97b;">CO₂ Avoided</div></div><div style="flex: 1; text-align: center; padding: 15px;"><div style="font-size: 1.5rem; font-weight: bold; color: #fff;">₹{savings:,}</div><div style="font-size: 0.8rem; color: #00C9FF;">Money Saved</div></div></div></div>"""
            st.markdown(badge_html, unsafe_allow_html=True)
            cert_html = f"""<!DOCTYPE html><html><head><style>body {{ font-family: sans-serif; background-color: #0c0c0c; color: #e0e0e0; padding: 40px; text-align: center; }} .cert {{ border: 2px solid #333; padding: 40px; border-radius: 20px; background: linear-gradient(135deg, #1a1a1a 0%, #0c0c0c 100%); margin: 0 auto; }}</style></head><body><div class="cert"><div style="font-size: 80px;">{badge_icon}</div><h1>{rank_name}</h1><p>Awarded for sustainable travel from {st.session_state.user_location} to {destination}</p><h2>{co2_savings:.0f} kg CO₂ Saved</h2></div></body></html>"""
            st.download_button(label="📥 Download Certificate", data=cert_html, file_name="Eco_Certificate.html", mime="text/html", use_container_width=True)
        
        with col2:
            st.markdown("### 🌍 Offset Your Footprint")
            projects = [{"name": "Mission Himalayas", "desc": f"Plant {trees_for_offset} trees in Uttarakhand.", "icon": "🌲", "link": "https://sankalptaru.org/", "color": "#43e97b"}, {"name": "Solar India", "desc": "Fund solar lamps for rural villages.", "icon": "☀️", "link": "https://www.giveindia.org/", "color": "#FFD166"}, {"name": "Clean Oceans", "desc": "Remove plastic from beaches.", "icon": "🌊", "link": "https://www.wwfindia.org/", "color": "#00C9FF"}]
            for p in projects:
                project_html = f"""<div style="background: rgba(255,255,255,0.05); border-radius: 12px; padding: 15px; margin-bottom: 12px; border-left: 4px solid {p['color']}; display: flex; justify-content: space-between; align-items: center;"><div style="display: flex; align-items: center;"><div style="font-size: 2rem; margin-right: 15px;">{p['icon']}</div><div><div style="font-weight: bold; font-size: 1rem; color: #e0e0e0;">{p['name']}</div><div style="font-size: 0.85rem; color: #aaa;">{p['desc']}</div></div></div><a href="{p['link']}" target="_blank" style="text-decoration: none; background: {p['color']}; color: #000; padding: 8px 16px; border-radius: 20px; font-weight: bold; font-size: 0.85rem;">Support</a></div>"""
                st.markdown(project_html, unsafe_allow_html=True)
            
            pledge_html = f"""<div style="background: linear-gradient(90deg, rgba(0,201,255,0.1), rgba(67,233,123,0.1)); padding: 15px; border-radius: 10px; margin-top: 10px; text-align: center;"><p style="margin: 0; color: #e0e0e0;">📢 <strong>Spread the Word:</strong> "I just saved {percent_reduction:.0f}% CO₂ on my trip to {destination} using #EcoNet!"<a href="https://twitter.com/intent/tweet?text=I%20just%20planned%20a%20sustainable%20trip%20to%20{destination}%20saving%20{percent_reduction:.0f}%25%20CO2!%20%23EcoTravel" target="_blank" style="margin-left: 10px; color: #00C9FF; font-weight: bold; text-decoration: none;">Tweet This</a></p></div>"""
            st.markdown(pledge_html, unsafe_allow_html=True)
            
    except Exception as e:
        st.error(f"Error: {str(e)}")

else:
    # Default View
    st.markdown("---")
    col1, col2 = st.columns([2, 1])
    with col1:
        welcome_html = f"""<div class="glass-card"><div style="display: flex; align-items: center; margin-bottom: 20px;"><div style="font-size: 3rem; margin-right: 20px;">🌟</div><div><h2 style="margin: 0;">Welcome to Eco Tourism Dashboard</h2><p style="color: #43e97b; margin: 5px 0 0 0;">Plan your next sustainable adventure from <strong>{st.session_state.user_location}</strong>!</p></div></div><div style="background: rgba(0, 201, 255, 0.1); padding: 20px; border-radius: 15px; margin: 20px 0;"><p style="font-size: 1.1rem; margin: 0; color: #e0e0e0;">This intelligent dashboard helps you make eco-friendly travel decisions:</p></div><div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin: 25px 0;"><div style="background: rgba(67, 233, 123, 0.1); padding: 15px; border-radius: 10px; border-left: 3px solid #43e97b;"><div style="font-size: 1.5rem; margin-bottom: 10px;">🌿</div><strong>Compare Carbon Footprints</strong></div><div style="background: rgba(0, 201, 255, 0.1); padding: 15px; border-radius: 10px; border-left: 3px solid #00C9FF;"><div style="font-size: 1.5rem; margin-bottom: 10px;">💰</div><strong>Calculate Cost Savings</strong></div><div style="background: rgba(255, 214, 102, 0.1); padding: 15px; border-radius: 10px; border-left: 3px solid #FFD166;"><div style="font-size: 1.5rem; margin-bottom: 10px;">🗺️</div><strong>Discover Destinations</strong></div><div style="background: rgba(255, 107, 107, 0.1); padding: 15px; border-radius: 10px; border-left: 3px solid #FF6B6B;"><div style="font-size: 1.5rem; margin-bottom: 10px;">📊</div><strong>Visualize Impact</strong></div></div><div style="background: rgba(67, 233, 123, 0.15); padding: 15px; border-radius: 10px; margin-top: 20px; border: 1px solid rgba(67, 233, 123, 0.3);"><p style="margin: 0; font-size: 1rem; color: #43e97b;"><strong>How to use:</strong> Select your current city and destination from the sidebar, customize your trip preferences, and click "Calculate My Impact".</p></div></div>"""
        st.markdown(welcome_html, unsafe_allow_html=True)
    with col2:
        # --- FIX: DYNAMIC TEXT COLOR FOR CARDS ---
        card_bg = "rgba(255,255,255,0.9)" if st.session_state.theme == 'light' else "rgba(20, 30, 25, 0.75)"
        text_col = "#000000" if st.session_state.theme == 'light' else "#e0e0e0"
        
        st.markdown(f"""<div class="glass-card"><h3>🏆 Top Eco Destinations</h3><p style="font-size: 0.9rem; color: {text_col}; margin-bottom: 15px;">From {st.session_state.user_location}</p>""", unsafe_allow_html=True)
        eco_destinations = [("Rishikesh", 6, "🏔️ Yoga"), ("Shimla", 8, "🚂 Toy Train"), ("Udaipur", 20, "🏰 Heritage"), ("Manali", 22, "❄️ Mountains"), ("Goa", 48, "🏖️ Beaches")]
        for dest, train_co2, tag in eco_destinations:
            dest_html = f"""<div style="background: {card_bg}; padding: 12px; border-radius: 8px; margin-bottom: 10px; border: 1px solid rgba(255,255,255,0.1);"><div style="display: flex; justify-content: space-between;"><strong style="color: {text_col};">{dest}</strong><span style="color: #43e97b;">{tag}</span></div><div style="font-size: 0.9rem; color: {text_col}; margin-top: 5px;">Train: ₹{DESTINATIONS[dest]["train"]["price"]:,} • {train_co2}kg CO₂</div></div>"""
            st.markdown(dest_html, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📊 Quick Statistics")
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown("""<div class="metric-card"><div class="metric-value">23</div><div class="metric-label">DESTINATIONS</div></div>""", unsafe_allow_html=True)
    with c2: st.markdown("""<div class="metric-card"><div class="metric-value">50+</div><div class="metric-label">CITIES</div></div>""", unsafe_allow_html=True)
    with c3: st.markdown("""<div class="metric-card"><div class="metric-value">25%</div><div class="metric-label">AVG SAVINGS</div></div>""", unsafe_allow_html=True)
    with c4: st.markdown("""<div class="metric-card"><div class="metric-value">5,000</div><div class="metric-label">TREES SAVED</div></div>""", unsafe_allow_html=True)

# ============================================
# 11. FOOTER
# ============================================
st.markdown("---")
footer_html = f"""<div style="text-align: center; color: #666; padding: 60px; font-size: 1.2rem; font-weight: 500;"><p>🌿 <strong>ECO TOURISM DASHBOARD</strong> • {st.session_state.theme.title()} Mode</p><p>Made with ❤️ for a greener planet</p><p style="margin-top: 10px; font-size: 0.9rem;">Data sources: IRCTC, MoEFCC • Last updated: {datetime.now().strftime('%d %b %Y')}</p></div>"""
st.markdown(footer_html, unsafe_allow_html=True)