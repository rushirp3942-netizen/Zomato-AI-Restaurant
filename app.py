import streamlit as st
import os
import sys
import json
import sqlite3
import pandas as pd

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(PROJECT_ROOT)

# Load secrets from Streamlit Cloud or local .env
from dotenv import load_dotenv
load_dotenv()

# Set environment variables from Streamlit secrets if available (only on Streamlit Cloud)
try:
    if hasattr(st, 'secrets') and st.secrets._secrets is not None:
        if 'GROQ_API_KEY' in st.secrets:
            os.environ['GROQ_API_KEY'] = st.secrets['GROQ_API_KEY']
        if 'DB_PATH' in st.secrets:
            os.environ['DB_PATH'] = st.secrets['DB_PATH']
except Exception:
    pass  # No secrets available locally

# Function to initialize database for Streamlit Cloud
@st.cache_resource
def initialize_database():
    """Initialize the database if it doesn't exist (for Streamlit Cloud deployment)"""
    db_path = os.path.join(PROJECT_ROOT, "restaurants.db")
    
    # Check if database already exists and has data
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM restaurants")
            count = cursor.fetchone()[0]
            conn.close()
            if count > 0:
                return db_path
        except:
            pass
    
    # Try to load from D: drive if available (local development)
    d_drive_db = "D:/restaurants.db"
    if os.path.exists(d_drive_db):
        try:
            conn = sqlite3.connect(d_drive_db)
            df = pd.read_sql_query("SELECT * FROM restaurants", conn)
            conn.close()
            
            # Save to local path
            conn = sqlite3.connect(db_path)
            df.to_sql('restaurants', conn, if_exists='replace', index=False)
            conn.close()
            return db_path
        except:
            pass
    
    # Download from Hugging Face if no local database exists
    try:
        from phase1_ingestion.ingest_data import download_and_clean_data, save_to_sqlite
        df = download_and_clean_data()
        if df is not None:
            save_to_sqlite(df, db_path)
            return db_path
    except Exception as e:
        st.error(f"Failed to download dataset: {e}")
    
    return db_path

# Initialize database
DB_PATH = initialize_database()
if DB_PATH:
    os.environ['DB_PATH'] = DB_PATH

from phase3_llm.llm_service import RestaurantOrchestrator

# Page configuration
st.set_page_config(
    page_title="Zomato AI Recommender",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS - Matching the UI image exactly
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    
    /* Hide default Streamlit header and sidebar */
    header {visibility: hidden;}
    .stSidebar {display: none;}
    
    /* Main background with gradient */
    .stApp {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d1f1f 50%, #1a1a1a 100%);
        min-height: 100vh;
    }
    
    /* Main content wrapper */
    .main-wrapper {
        margin-left: 60px;
        padding: 2rem 3rem;
        max-width: 1200px;
    }
    
    /* Zomato Sidebar */
    .zomato-sidebar {
        position: fixed;
        left: 0;
        top: 0;
        height: 100vh;
        width: 60px;
        background: linear-gradient(180deg, #dc2626 0%, #b91c1c 100%);
        display: flex;
        flex-direction: column;
        align-items: center;
        padding-top: 2rem;
        z-index: 1000;
    }
    
    .zomato-sidebar span {
        color: white;
        font-size: 1.5rem;
        font-weight: 800;
        line-height: 1.8;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    /* Header */
    .main-header {
        margin-bottom: 1.5rem;
    }
    
    .main-header h1 {
        font-size: 3rem;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 0.5rem;
        letter-spacing: -1px;
    }
    
    .highlight { color: #ef4f5f; }
    
    .subtitle {
        color: #a0a0a0;
        font-size: 1.1rem;
        font-weight: 400;
    }
    
    .city { 
        color: #ef4f5f; 
        font-weight: 600;
        text-decoration: underline;
        text-decoration-color: #ef4f5f;
    }
    
    /* Stats bar */
    .stats-bar {
        display: inline-flex;
        align-items: center;
        gap: 1.5rem;
        padding: 0.75rem 1.5rem;
        background: rgba(255,255,255,0.05);
        border-radius: 50px;
        margin-bottom: 2rem;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .stat-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: #b0b0b0;
        font-size: 0.9rem;
    }
    
    .stat-item b {
        color: #ef4f5f;
        font-size: 1rem;
        font-weight: 700;
    }
    
    .stat-divider {
        color: #555;
        font-weight: 300;
    }
    
    /* Top cuisines section */
    .top-cuisines-section {
        margin-bottom: 2rem;
    }
    
    .top-cuisines-title {
        color: #888;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 1rem;
    }
    
    .cuisine-chips-container {
        display: flex;
        gap: 0.75rem;
        flex-wrap: wrap;
    }
    
    .cuisine-chip {
        padding: 0.6rem 1.2rem;
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.15);
        border-radius: 25px;
        color: #e0e0e0;
        font-size: 0.9rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .cuisine-chip:hover {
        background: rgba(239, 79, 95, 0.2);
        border-color: #ef4f5f;
    }
    
    .cuisine-chip.active {
        background: #ef4f5f;
        border-color: #ef4f5f;
        color: white;
    }
    
    /* Form Card */
    .form-card {
        background: rgba(255,255,255,0.03);
        border-radius: 20px;
        padding: 2rem;
        border: 1px solid rgba(255,255,255,0.08);
    }
    
    .form-grid {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: 1.5rem;
        margin-bottom: 1.5rem;
    }
    
    .form-field {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .field-label {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: #e0e0e0;
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    .field-label .icon {
        color: #ef4f5f;
    }
    
    /* Custom select styling - smaller width */
    .stSelectbox > div > div {
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 10px !important;
        color: white !important;
        max-width: 100% !important;
    }
    
    .stSelectbox > div > div:hover {
        border-color: #ef4f5f !important;
    }
    
    /* Form grid columns - responsive sizing */
    @media (max-width: 768px) {
        .form-grid {
            grid-template-columns: 1fr !important;
        }
        
        .stSelectbox > div > div {
            font-size: 0.9rem !important;
        }
    }
    
    @media (min-width: 769px) {
        .form-grid {
            grid-template-columns: repeat(3, minmax(0, 1fr)) !important;
        }
    }
    
    /* Selected cuisine tags */
    .selected-tag {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.4rem 0.8rem;
        background: #ef4f5f;
        border-radius: 20px;
        color: white;
        font-size: 0.85rem;
        font-weight: 500;
        margin: 0.25rem;
    }
    
    .selected-tag .remove-btn {
        cursor: pointer;
        font-weight: bold;
    }
    
    /* Rating stepper - matching the image exactly */
    .rating-section {
        margin-bottom: 1.5rem;
    }
    
    .rating-stepper {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    /* Rating stepper container */
    .rating-stepper-container {
        display: flex;
        align-items: center;
        justify-content: flex-start;
        gap: 12px;
        margin-top: 8px;
    }
    
    /* Custom rating buttons */
    .rating-btn {
        width: 50px;
        height: 40px;
        border-radius: 10px;
        background: linear-gradient(135deg, #ef4f5f 0%, #dc2626 100%);
        border: 2px solid rgba(255,255,255,0.7);
        color: #ffffff;
        font-size: 24px;
        font-weight: bold;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 12px rgba(239, 79, 95, 0.4), inset 0 1px 0 rgba(255,255,255,0.3);
        text-shadow: 0 2px 4px rgba(0,0,0,0.4);
        transition: all 0.2s ease;
        line-height: 1;
        padding: 0;
        margin: 0;
    }
    
    .rating-btn:hover {
        background: linear-gradient(135deg, #ff6b7a 0%, #ef4f5f 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(239, 79, 95, 0.5), inset 0 1px 0 rgba(255,255,255,0.4);
        border-color: rgba(255,255,255,0.9);
    }
    
    .rating-btn:active {
        transform: translateY(0);
        box-shadow: 0 2px 8px rgba(239, 79, 95, 0.3);
    }
    
    /* Rating value display */
    .rating-value {
        font-size: 28px;
        font-weight: 700;
        color: #ffffff;
        min-width: 60px;
        text-align: center;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    /* Ensure rating section columns don't stretch */
    .rating-section > div > div {
        gap: 0.5rem !important;
    }
    
    /* Submit button */
    .submit-btn-container {
        margin-top: 1.5rem;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #ef4f5f 0%, #dc2626 100%) !important;
        color: white !important;
        border: none !important;
        padding: 1rem 2rem !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        width: 100% !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(239, 79, 95, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(239, 79, 95, 0.4) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
    }
    
    /* Recommendations Grid */
    .recommendations-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
        gap: 1.5rem;
        margin-top: 2rem;
    }
    
    /* Flash cards - Vertical Layout */
    .flash-card {
        background: rgba(255,255,255,0.05);
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid rgba(255,255,255,0.1);
        border-left: 4px solid #ef4f5f;
        display: flex;
        flex-direction: column;
        height: 100%;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .flash-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.3);
    }
    
    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 0.75rem;
    }
    
    .card-header h4 {
        margin: 0;
        font-size: 1.25rem;
        color: #ffffff;
        font-weight: 700;
        line-height: 1.3;
    }
    
    .match-score {
        background: linear-gradient(135deg, #ef4f5f 0%, #ff6b7a 100%);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
        white-space: nowrap;
    }
    
    .ai-summary {
        color: #a0a0a0;
        font-style: italic;
        margin-bottom: 1rem;
        font-size: 0.95rem;
        line-height: 1.4;
    }
    
    .card-meta {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
        margin-bottom: 0.75rem;
    }
    
    .card-meta span {
        display: flex;
        align-items: center;
        gap: 0.4rem;
        color: #b0b0b0;
        font-size: 0.9rem;
    }
    
    .why-this-box {
        background: rgba(0,0,0,0.2);
        border-radius: 12px;
        padding: 1rem;
        margin-top: auto;
        margin-bottom: 1rem;
        color: #d0d0d0;
        font-size: 0.9rem;
        line-height: 1.5;
    }
    
    .why-this-box b {
        color: #ef4f5f;
        display: block;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
    }
    
    /* Card Actions */
    .card-actions {
        display: flex;
        gap: 1rem;
        margin-top: 1rem;
        padding-top: 1rem;
        border-top: 1px solid rgba(255,255,255,0.1);
    }
    
    .action-btn {
        flex: 1;
        padding: 0.6rem 1rem;
        border-radius: 8px;
        border: 1px solid rgba(255,255,255,0.2);
        background: rgba(255,255,255,0.05);
        color: #e0e0e0;
        font-size: 0.9rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s;
        text-align: center;
    }
    
    .action-btn:hover {
        border-color: #ef4f5f;
        background: rgba(239, 79, 95, 0.1);
    }
    
    .action-btn.saved {
        background: #ef4f5f;
        border-color: #ef4f5f;
        color: white;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #666;
        font-size: 0.8rem;
        margin-top: 2rem;
        padding: 1rem;
    }
    
    /* Similar header */
    .similar-header {
        background: rgba(239, 79, 95, 0.1);
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        border: 1px solid rgba(239, 79, 95, 0.3);
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .form-grid {
            grid-template-columns: 1fr;
        }
        .main-wrapper {
            padding: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Data
LOCALITIES = ['BTM', 'Banashankari', 'Banaswadi', 'Bannerghatta Road', 'Basavanagudi', 'Basaveshwara Nagar', 'Bellandur', 'Bommanahalli', 'Brigade Road', 'Brookefield', 'CV Raman Nagar', 'Central Bangalore', 'Church Street', 'City Market', 'Commercial Street', 'Cunningham Road', 'Domlur', 'East Bangalore', 'Ejipura', 'Electronic City', 'Frazer Town', 'HBR Layout', 'HSR', 'Hebbal', 'Hennur', 'Hosur Road', 'ITPL Main Road, Whitefield', 'Indiranagar', 'Infantry Road', 'JP Nagar', 'Jakkur', 'Jalahalli', 'Jayanagar', 'Jeevan Bhima Nagar', 'KR Puram', 'Kaggadasapura', 'Kalyan Nagar', 'Kammanahalli', 'Kanakapura Road', 'Kengeri', 'Koramangala', 'Koramangala 1st Block', 'Koramangala 2nd Block', 'Koramangala 3rd Block', 'Koramangala 4th Block', 'Koramangala 5th Block', 'Koramangala 6th Block', 'Koramangala 7th Block', 'Koramangala 8th Block', 'Kumaraswamy Layout', 'Langford Town', 'Lavelle Road', 'MG Road', 'Magadi Road', 'Majestic', 'Malleshwaram', 'Marathahalli', 'Mysore Road', 'Nagarbhavi', 'Nagawara', 'New BEL Road', 'North Bangalore', 'Old Airport Road', 'Old Madras Road', 'Peenya', 'RT Nagar', 'Race Course Road', 'Rajajinagar', 'Rajarajeshwari Nagar', 'Rammurthy Nagar', 'Residency Road', 'Richmond Road', 'Sadashiv Nagar', 'Sahakara Nagar', 'Sanjay Nagar', 'Sankey Road', 'Sarjapur Road', 'Seshadripuram', 'Shanti Nagar', 'Shivajinagar', 'South Bangalore', 'St. Marks Road', 'Thippasandra', 'Ulsoor', 'Unknown', 'Uttarahalli', 'Varthur Main Road, Whitefield', 'Vasanth Nagar', 'Vijay Nagar', 'West Bangalore', 'Whitefield', 'Wilson Garden', 'Yelahanka', 'Yeshwantpur']

TOP_CUISINES = ['North Indian', 'Chinese', 'South Indian', 'Fast Food', 'Biryani']
ALL_CUISINES = ['Afghan', 'Afghani', 'African', 'American', 'Andhra', 'Arabian', 'Asian', 'Assamese', 'Australian', 'Awadhi', 'BBQ', 'Bakery', 'Bar Food', 'Belgian', 'Bengali', 'Beverages', 'Bihari', 'Biryani', 'Bohri', 'British', 'Bubble Tea', 'Burger', 'Burmese', 'Cafe', 'Cantonese', 'Charcoal Chicken', 'Chettinad', 'Chinese', 'Coffee', 'Continental', 'Desserts', 'Drinks Only', 'European', 'Fast Food', 'Finger Food', 'French', 'German', 'Goan', 'Greek', 'Grill', 'Gujarati', 'Healthy Food', 'Hot dogs', 'Hyderabadi', 'Ice Cream', 'Indian', 'Indonesian', 'Iranian', 'Italian', 'Japanese', 'Jewish', 'Juices', 'Kashmiri', 'Kebab', 'Kerala', 'Konkan', 'Korean', 'Lebanese', 'Lucknowi', 'Maharashtrian', 'Malaysian', 'Malwani', 'Mangalorean', 'Mediterranean', 'Mexican', 'Middle Eastern', 'Mithai', 'Modern Indian', 'Momos', 'Mongolian', 'Mughlai', 'N Naga', 'Nepalese', 'North Eastern', 'North Indian', 'Oriya', 'Other', 'Paan', 'Pan Asian', 'Parsi', 'Pizza', 'Portuguese', 'Rajasthani', 'Raw Meats', 'Roast Chicken', 'Rolls', 'Russian', 'Salad', 'Sandwich', 'Seafood', 'Sindhi', 'Singaporean', 'South American', 'South Indian', 'Spanish', 'Sri Lankan', 'Steak', 'Street Food', 'Sushi', 'Tamil', 'Tea', 'Tex-Mex', 'Thai', 'Tibetan', 'Turkish', 'Vegan', 'Vietnamese', 'Wraps']

# Initialize session state
if 'orchestrator' not in st.session_state:
    try:
        st.session_state.orchestrator = RestaurantOrchestrator()
        st.session_state.initialized = True
    except Exception as e:
        st.session_state.initialized = False
        st.session_state.init_error = str(e)

if 'selected_cuisines' not in st.session_state:
    st.session_state.selected_cuisines = set()

if 'recommendations' not in st.session_state:
    st.session_state.recommendations = None

if 'similar_mode' not in st.session_state:
    st.session_state.similar_mode = False

if 'original_recommendations' not in st.session_state:
    st.session_state.original_recommendations = None

if 'similar_context' not in st.session_state:
    st.session_state.similar_context = None

if 'rating' not in st.session_state:
    st.session_state.rating = 4.0

if 'saved_restaurants' not in st.session_state:
    st.session_state.saved_restaurants = set()

# Zomato Sidebar
st.markdown("""
<div class="zomato-sidebar">
    <span>Z</span>
    <span>O</span>
    <span>M</span>
    <span>A</span>
    <span>T</span>
    <span>O</span>
</div>
""", unsafe_allow_html=True)

# Main Content Wrapper
st.markdown('<div class="main-wrapper">', unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1><span class="highlight">Zomato</span> AI Recommender</h1>
    <p class="subtitle">Helping you find the best places to eat in <span class="city">Bangalore</span> city</p>
</div>
""", unsafe_allow_html=True)

# Stats bar
st.markdown("""
<div class="stats-bar">
    <div class="stat-item">📍 <b>94</b> Localities</div>
    <div class="stat-divider">|</div>
    <div class="stat-item">🍽️ <b>108</b> Cuisines</div>
</div>
""", unsafe_allow_html=True)

# Check initialization
if not st.session_state.get('initialized', False):
    st.error(f"Failed to initialize: {st.session_state.get('init_error', 'Unknown error')}")
    st.stop()

# Top Cuisines Section
st.markdown('<div class="top-cuisines-section">', unsafe_allow_html=True)
st.markdown('<div class="top-cuisines-title">Top cuisines in Bangalore</div>', unsafe_allow_html=True)

# Cuisine chips
chip_cols = st.columns(5)
for i, cuisine in enumerate(TOP_CUISINES):
    with chip_cols[i]:
        is_active = cuisine in st.session_state.selected_cuisines
        btn_type = "primary" if is_active else "secondary"
        if st.button(cuisine, key=f"chip_{cuisine}", type=btn_type, use_container_width=True):
            if is_active:
                st.session_state.selected_cuisines.discard(cuisine)
            else:
                st.session_state.selected_cuisines.add(cuisine)
            st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# Form Card
st.markdown('<div class="form-card">', unsafe_allow_html=True)

# Form Grid - Row 1: Locality, Price, Cuisines
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="form-field">', unsafe_allow_html=True)
    st.markdown('<div class="field-label"><span class="icon">📍</span> Select Locality *</div>', unsafe_allow_html=True)
    locality = st.selectbox("Locality", ["Select a locality..."] + LOCALITIES, label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="form-field">', unsafe_allow_html=True)
    st.markdown('<div class="field-label"><span class="icon">💰</span> Price Range *</div>', unsafe_allow_html=True)
    price_options = {
        "": "Select price range...",
        "cheap": "Budget (Under ₹500)",
        "moderate": "Mid-range (₹500 - ₹1500)",
        "expensive": "Premium (Above ₹1500)"
    }
    price = st.selectbox("Price", list(price_options.keys()), format_func=lambda x: price_options[x], label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="form-field">', unsafe_allow_html=True)
    st.markdown('<div class="field-label"><span class="icon">🍜</span> Cuisines (Multi-select) *</div>', unsafe_allow_html=True)
    
    # Display selected cuisines as tags
    if st.session_state.selected_cuisines:
        tags_html = ""
        for cuisine in st.session_state.selected_cuisines:
            tags_html += f'<span class="selected-tag">{cuisine} <span class="remove-btn" onclick="window.location.reload()">×</span></span>'
        st.markdown(tags_html, unsafe_allow_html=True)
    
    # Dropdown for additional cuisines
    remaining = [c for c in ALL_CUISINES if c not in st.session_state.selected_cuisines]
    selected = st.selectbox("Add cuisine", ["Add a cuisine..."] + remaining, label_visibility="collapsed")
    if selected != "Add a cuisine...":
        st.session_state.selected_cuisines.add(selected)
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# Rating Section with Stepper
st.markdown('<div class="rating-section">', unsafe_allow_html=True)
st.markdown('<div class="field-label"><span class="icon">⭐</span> Ratings *</div>', unsafe_allow_html=True)

# Custom HTML rating stepper with proper styling
rating_html = f"""
<div class="rating-stepper-container">
    <form action="" method="get" style="display: inline;">
        <input type="hidden" name="rating_action" value="minus">
        <button type="submit" class="rating-btn">−</button>
    </form>
    <div class="rating-value">{st.session_state.rating}</div>
    <form action="" method="get" style="display: inline;">
        <input type="hidden" name="rating_action" value="plus">
        <button type="submit" class="rating-btn">+</button>
    </form>
</div>
"""
st.markdown(rating_html, unsafe_allow_html=True)

# Handle rating changes from query params
query_params = st.query_params
if "rating_action" in query_params:
    action = query_params["rating_action"]
    if action == "minus" and st.session_state.rating > 0:
        st.session_state.rating = round(st.session_state.rating - 0.5, 1)
        st.query_params.clear()
        st.rerun()
    elif action == "plus" and st.session_state.rating < 5:
        st.session_state.rating = round(st.session_state.rating + 0.5, 1)
        st.query_params.clear()
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# Submit Button
st.markdown('<div class="submit-btn-container">', unsafe_allow_html=True)
get_rec_clicked = st.button("✨ Get Recommendations", type="primary", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # End form-card

# Similar mode header
if st.session_state.similar_mode and st.session_state.similar_context:
    st.markdown(f"""
    <div class="similar-header">
        <b>🔍 Similar to:</b> {st.session_state.similar_context}
    </div>
    """, unsafe_allow_html=True)
    if st.button("← Back to Original Results", type="secondary"):
        st.session_state.similar_mode = False
        st.session_state.recommendations = st.session_state.original_recommendations
        st.session_state.similar_context = None
        st.rerun()

# Handle recommendations
if get_rec_clicked:
    if locality == "Select a locality...":
        st.error("Please select a locality!")
    else:
        with st.spinner("🍽️ Scanning 51,717 restaurants..."):
            cuisines_str = ", ".join(st.session_state.selected_cuisines) if st.session_state.selected_cuisines else ""
            query_parts = []
            if cuisines_str:
                query_parts.append(f"{cuisines_str} food")
            query_parts.append(f"in {locality}")
            query_parts.append(f"with a minimum rating of {st.session_state.rating}")
            
            if price == 'cheap':
                query_parts.append("under 500 rupees")
            elif price == 'moderate':
                query_parts.append("between 500 and 1500 rupees")
            elif price == 'expensive':
                query_parts.append("above 1500 rupees")
            
            synthesized_query = "I want " + " ".join(query_parts)
            
            try:
                response = st.session_state.orchestrator.chat(synthesized_query)
                payload = json.loads(response)
                st.session_state.recommendations = payload.get('recommendations', [])
                st.session_state.similar_mode = False
                st.session_state.original_recommendations = None
                st.session_state.similar_context = None
            except Exception as e:
                st.error(f"Error getting recommendations: {str(e)}")

# Display recommendations
if st.session_state.recommendations:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🎯 Recommended Restaurants")
    
    if len(st.session_state.recommendations) == 0:
        st.info("No perfect matches found. Try relaxing your filters!")
    else:
        # Create grid layout for cards
        num_cards = len(st.session_state.recommendations)
        cols = st.columns(min(num_cards, 3))  # Max 3 cards per row
        
        for idx, rec in enumerate(st.session_state.recommendations):
            rec_name = rec.get('name', 'Unknown')
            is_saved = rec_name in st.session_state.saved_restaurants
            
            with cols[idx % 3]:
                st.markdown(f"""
                <div class="flash-card">
                    <div class="card-header">
                        <h4>{rec_name}</h4>
                        <div class="match-score">{rec.get('match_score', 0)}% Match</div>
                    </div>
                    <div class="ai-summary">{rec.get('ai_summary', '')}</div>
                    <div class="card-meta">
                        <span>⭐ {rec.get('rating', 'N/A')}</span>
                        <span>💰 ₹{rec.get('cost', 'N/A')} for two</span>
                        <span>📍 {rec.get('location', 'N/A')}</span>
                        <span>🍽️ {rec.get('cuisines', 'N/A')}</span>
                    </div>
                    <div class="why-this-box">
                        <b>Why This Recommendation</b>
                        {rec.get('why_this', '')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Action buttons row
                btn_col1, btn_col2 = st.columns(2)
                
                with btn_col1:
                    save_label = "⭐ Saved" if is_saved else "☆ Save"
                    if st.button(save_label, key=f"save_{idx}_{rec_name}", use_container_width=True):
                        if is_saved:
                            st.session_state.saved_restaurants.discard(rec_name)
                        else:
                            st.session_state.saved_restaurants.add(rec_name)
                        st.rerun()
                
                with btn_col2:
                    if not st.session_state.similar_mode:
                        if st.button("🔍 Similar", key=f"similar_{idx}_{rec_name}", use_container_width=True):
                            with st.spinner(f"Finding similar restaurants..."):
                                try:
                                    if not st.session_state.original_recommendations:
                                        st.session_state.original_recommendations = st.session_state.recommendations.copy()
                                    
                                    ref_restaurant = {
                                        'name': rec.get('name'),
                                        'cuisines': rec.get('cuisines'),
                                        'location': rec.get('location'),
                                        'rating': float(rec.get('rating', 0)),
                                        'cost': int(rec.get('cost', 0))
                                    }
                                    
                                    primary_cuisine = ref_restaurant['cuisines'].split(',')[0].strip()
                                    candidates = st.session_state.orchestrator.retrieval_engine.query_restaurants(
                                        cuisine=primary_cuisine,
                                        location=ref_restaurant['location'],
                                        min_rating=max(0.0, ref_restaurant['rating'] - 0.5),
                                        max_cost=int(ref_restaurant['cost'] * 1.5)
                                    )
                                    
                                    candidates = candidates[candidates['name'] != ref_restaurant['name']]
                                    similar_response = st.session_state.orchestrator.generate_similar_recommendations(ref_restaurant, candidates)
                                    similar_payload = json.loads(similar_response)
                                    
                                    st.session_state.recommendations = similar_payload.get('recommendations', [])
                                    st.session_state.similar_mode = True
                                    st.session_state.similar_context = f"{rec.get('name')} — based on cuisine, price, and rating"
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error finding similar restaurants: {str(e)}")

# Footer
st.markdown("""
<div class="footer">
    Note: Ratings are on a scale of 0-5. Price is for two people.<br>
    Powered by Groq LLM • Zomato Bangalore Dataset (51k+ restaurants)
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # End main-wrapper
