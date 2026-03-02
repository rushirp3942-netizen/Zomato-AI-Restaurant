import streamlit as st
import os
import sys
import json

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(PROJECT_ROOT)

# Load secrets from Streamlit Cloud or local .env
from dotenv import load_dotenv
load_dotenv()

# Set environment variables from Streamlit secrets if available
if hasattr(st, 'secrets'):
    if 'GROQ_API_KEY' in st.secrets:
        os.environ['GROQ_API_KEY'] = st.secrets['GROQ_API_KEY']
    if 'DB_PATH' in st.secrets:
        os.environ['DB_PATH'] = st.secrets['DB_PATH']

from phase3_llm.llm_service import RestaurantOrchestrator

# Page configuration
st.set_page_config(
    page_title="Zomato AI Recommender",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    
    .main-header {
        text-align: center;
        padding: 2rem 0;
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 800;
        color: #1c1c1c;
        margin-bottom: 0.5rem;
    }
    
    .highlight { color: #ef4f5f; }
    
    .subtitle {
        color: #686b78;
        font-size: 1.1rem;
    }
    
    .city { color: #ef4f5f; font-weight: 600; }
    
    .stats-bar {
        display: flex;
        justify-content: center;
        gap: 2rem;
        padding: 1rem;
        background: linear-gradient(135deg, #f8f8f8 0%, #fff 100%);
        border-radius: 12px;
        margin: 1rem 0;
    }
    
    .stat-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: #686b78;
    }
    
    .stat-item b {
        color: #ef4f5f;
        font-size: 1.2rem;
    }
    
    .form-card {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin: 1.5rem 0;
    }
    
    .section-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1c1c1c;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .cuisine-chip {
        display: inline-block;
        padding: 0.4rem 1rem;
        margin: 0.25rem;
        background: #f8f8f8;
        border: 2px solid #e5e5e5;
        border-radius: 20px;
        cursor: pointer;
        transition: all 0.2s;
        font-size: 0.9rem;
    }
    
    .cuisine-chip:hover {
        border-color: #ef4f5f;
        background: #fff0f1;
    }
    
    .cuisine-chip.selected {
        background: #ef4f5f;
        color: white;
        border-color: #ef4f5f;
    }
    
    .flash-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
        border-left: 4px solid #ef4f5f;
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
        color: #1c1c1c;
    }
    
    .match-score {
        background: linear-gradient(135deg, #ef4f5f 0%, #ff6b7a 100%);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    
    .ai-summary {
        color: #686b78;
        font-style: italic;
        margin-bottom: 1rem;
        font-size: 0.95rem;
    }
    
    .card-meta {
        display: flex;
        gap: 1.5rem;
        margin-bottom: 0.75rem;
        flex-wrap: wrap;
    }
    
    .card-meta span {
        display: flex;
        align-items: center;
        gap: 0.4rem;
        color: #686b78;
        font-size: 0.9rem;
    }
    
    .why-this-box {
        background: #f8f8f8;
        border-radius: 12px;
        padding: 1rem;
        margin-top: 1rem;
    }
    
    .why-this-box b {
        color: #ef4f5f;
        display: block;
        margin-bottom: 0.5rem;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #ef4f5f 0%, #ff6b7a 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 12px;
        font-weight: 600;
        font-size: 1rem;
        width: 100%;
        transition: transform 0.2s;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(239, 79, 95, 0.4);
    }
    
    .stButton>button:disabled {
        background: #ccc;
        transform: none;
    }
    
    .similar-btn {
        background: #f8f8f8;
        border: 2px solid #e5e5e5;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        cursor: pointer;
        font-size: 0.9rem;
        transition: all 0.2s;
    }
    
    .similar-btn:hover {
        border-color: #ef4f5f;
        background: #fff0f1;
    }
    
    .footer {
        text-align: center;
        color: #686b78;
        font-size: 0.85rem;
        margin-top: 2rem;
        padding: 1rem;
    }
    
    .top-cuisines {
        margin: 1.5rem 0;
    }
    
    .top-cuisines p {
        color: #686b78;
        margin-bottom: 0.75rem;
        font-size: 0.95rem;
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

# Header
st.markdown("""
<div class="main-header">
    <h1><span class="highlight">Zomato</span> AI Recommender</h1>
    <p class="subtitle">Helping you find the best places to eat in <span class="city">Bangalore</span> city</p>
</div>
""", unsafe_allow_html=True)

# Stats bar
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("""
    <div class="stats-bar">
        <div class="stat-item">📍 <b>94</b> Localities</div>
        <div style="color: #ddd;">|</div>
        <div class="stat-item">🍽️ <b>108</b> Cuisines</div>
    </div>
    """, unsafe_allow_html=True)

# Check initialization
if not st.session_state.get('initialized', False):
    st.error(f"Failed to initialize the recommendation engine: {st.session_state.get('init_error', 'Unknown error')}")
    st.stop()

# Form Card
with st.container():
    st.markdown('<div class="form-card">', unsafe_allow_html=True)
    
    # Top Cuisines
    st.markdown('<div class="top-cuisines"><p>Top cuisines in Bangalore</p></div>', unsafe_allow_html=True)
    
    # Cuisine chips
    cols = st.columns(5)
    for i, cuisine in enumerate(TOP_CUISINES):
        with cols[i]:
            is_selected = cuisine in st.session_state.selected_cuisines
            if st.button(
                cuisine, 
                key=f"chip_{cuisine}",
                type="primary" if is_selected else "secondary",
                use_container_width=True
            ):
                if is_selected:
                    st.session_state.selected_cuisines.discard(cuisine)
                else:
                    st.session_state.selected_cuisines.add(cuisine)
                st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Form inputs
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="section-title">📍 Select Locality *</div>', unsafe_allow_html=True)
        locality = st.selectbox("", [""] + LOCALITIES, label_visibility="collapsed")
    
    with col2:
        st.markdown('<div class="section-title">💰 Price Range *</div>', unsafe_allow_html=True)
        price_options = {
            "": "Select price range...",
            "cheap": "Budget (Under ₹500)",
            "moderate": "Mid-range (₹500 - ₹1500)",
            "expensive": "Premium (Above ₹1500)"
        }
        price = st.selectbox("", list(price_options.keys()), format_func=lambda x: price_options[x], label_visibility="collapsed")
    
    # Additional cuisines dropdown
    st.markdown('<div class="section-title">🍜 Additional Cuisines (Optional)</div>', unsafe_allow_html=True)
    remaining_cuisines = [c for c in ALL_CUISINES if c not in st.session_state.selected_cuisines]
    additional_cuisine = st.selectbox("Add more cuisines...", [""] + remaining_cuisines, label_visibility="collapsed")
    if additional_cuisine:
        st.session_state.selected_cuisines.add(additional_cuisine)
        st.rerun()
    
    # Display selected cuisines
    if st.session_state.selected_cuisines:
        st.markdown("**Selected Cuisines:**")
        selected_cols = st.columns(min(len(st.session_state.selected_cuisines), 5))
        for i, cuisine in enumerate(st.session_state.selected_cuisines):
            with selected_cols[i % 5]:
                if st.button(f"❌ {cuisine}", key=f"remove_{cuisine}", help="Click to remove"):
                    st.session_state.selected_cuisines.discard(cuisine)
                    st.rerun()
    
    # Rating
    st.markdown('<div class="section-title">⭐ Minimum Rating *</div>', unsafe_allow_html=True)
    rating = st.slider("", min_value=0.0, max_value=5.0, value=4.0, step=0.5, label_visibility="collapsed")
    st.markdown(f"<p style='text-align: center; color: #ef4f5f; font-weight: 600;'>Minimum Rating: {rating}</p>", unsafe_allow_html=True)
    
    # Submit button
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Similar mode header
    if st.session_state.similar_mode and st.session_state.similar_context:
        st.markdown(f"""
        <div style="background: #fff0f1; padding: 1rem; border-radius: 12px; margin-bottom: 1rem;">
            <b>🔍 Similar to:</b> {st.session_state.similar_context}
        </div>
        """, unsafe_allow_html=True)
        if st.button("← Back to Original Results", type="secondary"):
            st.session_state.similar_mode = False
            st.session_state.recommendations = st.session_state.original_recommendations
            st.session_state.similar_context = None
            st.rerun()
    
    get_rec_clicked = st.button("✨ Get Recommendations", type="primary", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Handle recommendations
if get_rec_clicked:
    if not locality:
        st.error("Please select a locality!")
    else:
        with st.spinner("🍽️ Scanning 51,717 restaurants..."):
            # Build query
            cuisines_str = ", ".join(st.session_state.selected_cuisines) if st.session_state.selected_cuisines else ""
            query_parts = []
            if cuisines_str:
                query_parts.append(f"{cuisines_str} food")
            query_parts.append(f"in {locality}")
            query_parts.append(f"with a minimum rating of {rating}")
            
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
        for rec in st.session_state.recommendations:
            with st.container():
                st.markdown(f"""
                <div class="flash-card">
                    <div class="card-header">
                        <h4>{rec.get('name', 'Unknown')}</h4>
                        <div class="match-score">{rec.get('match_score', 0)}% Match</div>
                    </div>
                    <div class="ai-summary">{rec.get('ai_summary', '')}</div>
                    <div class="card-meta">
                        <span>⭐ {rec.get('rating', 'N/A')}</span>
                        <span>💰 ₹{rec.get('cost', 'N/A')} for two</span>
                        <span>📍 {rec.get('location', 'N/A')}</span>
                    </div>
                    <div class="card-meta">
                        <span>🍽️ {rec.get('cuisines', 'N/A')}</span>
                    </div>
                    <div class="why-this-box">
                        <b>Why This Recommendation</b>
                        {rec.get('why_this', '')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Similar button
                if not st.session_state.similar_mode:
                    if st.button(f"🔍 Find Similar to {rec.get('name', '')}", key=f"similar_{rec.get('name', '')}"):
                        with st.spinner(f"Finding restaurants similar to {rec.get('name')}..."):
                            try:
                                # Save original results
                                if not st.session_state.original_recommendations:
                                    st.session_state.original_recommendations = st.session_state.recommendations.copy()
                                
                                # Get similar restaurants
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
                                
                                # Filter out original
                                candidates = candidates[candidates['name'] != ref_restaurant['name']]
                                
                                # Generate similar recommendations
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
