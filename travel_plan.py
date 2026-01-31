# chatgpt_travel_guide.py

import os
from pathlib import Path
from datetime import datetime, timedelta
from textwrap import dedent
from urllib.parse import quote

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    ListFlowable,
    ListItem,
    PageBreak,
)
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import io
import requests

# --------------------------------------------
# ENVIRONMENT
# --------------------------------------------

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    st.error("OPENAI_API_KEY not found. Please set it in your .env file.")
    st.stop()

client = OpenAI(api_key=OPENAI_API_KEY)

st.set_page_config(
    page_title="Travel Guide",
    page_icon="🌍",
    layout="wide",
)

# --------------------------------------------
# DESTINATION BACKGROUNDS (WEB + PDF)
# --------------------------------------------

# Comprehensive list of verified images for world's most popular destinations
DEST_BG_IMAGES = {
    # Europe
    "paris": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=1200&q=80",  # Eiffel Tower
    "london": "https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?w=1200&q=80",  # Big Ben
    "rome": "https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=1200&q=80",  # Colosseum
    "barcelona": "https://images.unsplash.com/photo-1583422409516-2895a77efded?w=1200&q=80",  # Sagrada Familia
    "amsterdam": "https://images.unsplash.com/photo-1534351590666-13e3e96b5017?w=1200&q=80",  # Canals
    "venice": "https://images.unsplash.com/photo-1523906834658-6e24ef2386f9?w=1200&q=80",  # Grand Canal
    "athens": "https://images.unsplash.com/photo-1555993539-1732b0258235?w=1200&q=80",  # Acropolis
    "prague": "https://images.unsplash.com/photo-1541849546-216549ae216d?w=1200&q=80",  # Old Town
    "istanbul": "https://images.unsplash.com/photo-1524231757912-21f4fe3a7200?w=1200&q=80",  # Blue Mosque
    "vienna": "https://images.unsplash.com/photo-1516550893923-42d28e5677af?w=1200&q=80",  # Palace
    "budapest": "https://images.unsplash.com/photo-1541963058-d826d34c14e1?w=1200&q=80",  # Parliament
    "lisbon": "https://images.unsplash.com/photo-1585208798174-6cedd86e019a?w=1200&q=80",  # Tram
    "madrid": "https://images.unsplash.com/photo-1539037116277-4db20889f2d4?w=1200&q=80",  # Plaza
    "berlin": "https://images.unsplash.com/photo-1560969184-10fe8719e047?w=1200&q=80",  # Brandenburg Gate
    "moscow": "https://images.unsplash.com/photo-1513326738677-b964603b136d?w=1200&q=80",  # Red Square
    "dublin": "https://images.unsplash.com/photo-1549918864-48ac978761a4?w=1200&q=80",  # Temple Bar
    "edinburgh": "https://images.unsplash.com/photo-1555881675-ac4a4241c1e7?w=1200&q=80",  # Castle
    "santorini": "https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?w=1200&q=80",  # Blue domes
    "switzerland": "https://images.unsplash.com/photo-1527668752968-14dc70a27c95?w=1200&q=80",  # Alps
    "zurich": "https://images.unsplash.com/photo-1563301088-dd4ce16d5611?w=1200&q=80",  # Lake
    
    # Asia
    "tokyo": "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=1200&q=80",  # Shibuya
    "kyoto": "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=1200&q=80",  # Temple
    "dubai": "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=1200&q=80",  # Burj Khalifa
    "singapore": "https://images.unsplash.com/photo-1525625293386-3f8f99389edd?w=1200&q=80",  # Marina Bay
    "bangkok": "https://images.unsplash.com/photo-1508009603885-50cf7c579365?w=1200&q=80",  # Grand Palace
    "hong kong": "https://images.unsplash.com/photo-1536599018102-9f803c140fc1?w=1200&q=80",  # Skyline
    "seoul": "https://images.unsplash.com/photo-1517154421773-0529f29ea451?w=1200&q=80",  # Gyeongbokgung
    "bali": "https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=1200&q=80",  # Rice terraces
    "maldives": "https://images.unsplash.com/photo-1514282401047-d79a71a590e8?w=1200&q=80",  # Overwater bungalows
    "phuket": "https://images.unsplash.com/photo-1589394815804-964ed0be2eb5?w=1200&q=80",  # Beach
    "mumbai": "https://images.unsplash.com/photo-1570168007204-dfb528c6958f?w=1200&q=80",  # Gateway of India
    "delhi": "https://images.unsplash.com/photo-1587474260584-136574528ed5?w=1200&q=80",  # India Gate
    "karachi": "https://images.unsplash.com/photo-1588181680169-7f3ac63cbe4e?w=1200&q=80",  # Skyline
    "lahore": "https://images.unsplash.com/photo-1598127748100-48d56a1c684e?w=1200&q=80",  # Badshahi Mosque
    "beijing": "https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=1200&q=80",  # Forbidden City
    "shanghai": "https://images.unsplash.com/photo-1537890030206-1c0d99b5a6db?w=1200&q=80",  # Bund
    "hanoi": "https://images.unsplash.com/photo-1509966756634-9c23dd6e6815?w=1200&q=80",  # Old Quarter
    "kuala lumpur": "https://images.unsplash.com/photo-1596422846543-75c6fc197f07?w=1200&q=80",  # Petronas Towers
    "taipei": "https://images.unsplash.com/photo-1508623177105-8f9c3b5b7adb?w=1200&q=80",  # Taipei 101
    "osaka": "https://images.unsplash.com/photo-1590253230532-a67f6bc61c9e?w=1200&q=80",  # Dotonbori
    "riyadh": "https://images.unsplash.com/photo-1591608971362-f08b2a75731a?w=1200&q=80",  # Kingdom Centre
    "jeddah": "https://images.unsplash.com/photo-1578895101408-1a36b834405b?w=1200&q=80",  # Waterfront
    "kuala lumpur": "https://images.unsplash.com/photo-1596422846543-75c6fc197f07?w=1200&q=80",  # Petronas Towers
    "kl": "https://images.unsplash.com/photo-1596422846543-75c6fc197f07?w=1200&q=80",  # Petronas Towers (KL abbreviation)
    "malaysia": "https://images.unsplash.com/photo-1596422846543-75c6fc197f07?w=1200&q=80",  # Petronas Towers
    
    # Americas
    "new york": "https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?w=1200&q=80",  # Manhattan
    "los angeles": "https://images.unsplash.com/photo-1534190760961-74e8c1c5c3da?w=1200&q=80",  # Hollywood
    "san francisco": "https://images.unsplash.com/photo-1501594907352-04cda38ebc29?w=1200&q=80",  # Golden Gate
    "las vegas": "https://images.unsplash.com/photo-1605833556294-ea5c7a74f97a?w=1200&q=80",  # Strip
    "miami": "https://images.unsplash.com/photo-1533106497176-45ae19e68ba2?w=1200&q=80",  # Beach
    "chicago": "https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?w=1200&q=80",  # Skyline
    "vancouver": "https://images.unsplash.com/photo-1519575706483-221027bfbb31?w=1200&q=80",  # Harbor
    "toronto": "https://images.unsplash.com/photo-1517935706615-2717063c2225?w=1200&q=80",  # CN Tower
    "mexico city": "https://images.unsplash.com/photo-1518659526054-e6d9b0244b28?w=1200&q=80",  # Zocalo
    "cancun": "https://images.unsplash.com/photo-1570394782014-d18b9a5d2ed5?w=1200&q=80",  # Beach
    "rio de janeiro": "https://images.unsplash.com/photo-1483729558449-99ef09a8c325?w=1200&q=80",  # Christ statue
    "buenos aires": "https://images.unsplash.com/photo-1589909202802-8f4aadce1849?w=1200&q=80",  # Obelisk
    "lima": "https://images.unsplash.com/photo-1531968455001-5c5272a41129?w=1200&q=80",  # Plaza
    "machu picchu": "https://images.unsplash.com/photo-1587595431973-160d0d94add1?w=1200&q=80",  # Ruins
    
    # Middle East & Africa
    "cairo": "https://images.unsplash.com/photo-1572252009286-268acec5ca0a?w=1200&q=80",  # Pyramids
    "jerusalem": "https://images.unsplash.com/photo-1566814534947-46a09bccd284?w=1200&q=80",  # Old City
    "marrakech": "https://images.unsplash.com/photo-1597212618440-806262de4f6b?w=1200&q=80",  # Medina
    "cape town": "https://images.unsplash.com/photo-1580060839134-75a5edca2e99?w=1200&q=80",  # Table Mountain
    "nairobi": "https://images.unsplash.com/photo-1611348524140-53c9a25263d6?w=1200&q=80",  # Skyline
    
    # Oceania
    "sydney": "https://images.unsplash.com/photo-1506973035872-a4ec16b8e8d9?w=1200&q=80",  # Opera House
    "melbourne": "https://images.unsplash.com/photo-1514395462725-fb4566210144?w=1200&q=80",  # Flinders Street
    "auckland": "https://images.unsplash.com/photo-1507699622108-4be3abd695ad?w=1200&q=80",  # Sky Tower
    "fiji": "https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=1200&q=80",  # Beach
}

# Beautiful generic travel background for initial load
GENERIC_BG_IMAGE = "https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=1200&q=80"  # Airplane wing over clouds

# Cache for fetched images
if 'image_cache' not in st.session_state:
    st.session_state.image_cache = {}


def fetch_destination_image(destination: str) -> str:
    """
    Get a verified image of the destination.
    Uses predefined verified images, otherwise returns generic travel image.
    """
    if not destination:
        return GENERIC_BG_IMAGE
    
    # Check cache first
    cache_key = destination.lower().strip()
    if cache_key in st.session_state.image_cache:
        return st.session_state.image_cache[cache_key]
    
    # Check predefined verified images with exact and substring matching
    dest_key = destination.strip().lower()
    
    # Exact match first
    if dest_key in DEST_BG_IMAGES:
        st.session_state.image_cache[cache_key] = DEST_BG_IMAGES[dest_key]
        return DEST_BG_IMAGES[dest_key]
    
    # Substring match (bidirectional)
    for key, url in DEST_BG_IMAGES.items():
        if key in dest_key or dest_key in key:
            st.session_state.image_cache[cache_key] = url
            return url
    
    # No verified image found - use generic travel background
    st.session_state.image_cache[cache_key] = GENERIC_BG_IMAGE
    return GENERIC_BG_IMAGE

# For PDF backgrounds (optional local images)
DEST_PDF_BG = {
    "paris": "static/paris_bg.jpg",
    "tokyo": "static/tokyo_bg.jpg",
    "new york": "static/nyc_bg.jpg",
    "karachi": "static/karachi_bg.jpg",
    "athens": "static/athens_bg.jpg",
}
GENERIC_PDF_BG = "static/generic_travel_bg.jpg"


def pick_bg_image(destination: str) -> str:
    """
    Pick a background image based on the destination string.
    Fetches real destination images dynamically.
    """
    return fetch_destination_image(destination)


def set_destination_background(destination: str):
    """Apply destination-specific background with enhanced styling."""
    img_url = pick_bg_image(destination)
    
    # Force a unique key to ensure CSS updates
    unique_key = f"{destination}_{datetime.now().timestamp()}"
    
    st.markdown(
        f"""
        <style>
        /* Background image - {unique_key} */
        .stApp {{
            background-color: #ffffff !important;
        }}
        
        /* Position image on the right side, expanded to cover full output area */
        .stApp::after {{
            content: "";
            position: absolute;
            top: 80px;
            right: 10px;
            width: 62%;
            min-height: 800px;
            background: url("{img_url}") center center / cover no-repeat;
            opacity: 0.15;
            z-index: 0;
            border-radius: 1.5rem;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
            pointer-events: none;
        }}
        
        /* Main content container */
        .main > div {{
            background-color: rgba(255, 255, 255, 0.98) !important;
            padding: 2rem 2.5rem !important;
            border-radius: 1rem !important;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1) !important;
            color: #1f2933 !important;
            position: relative;
            z-index: 10;
        }}
        
        /* Headers */
        h1, h2, h3, h4, h5, h6 {{
            color: #111827 !important;
            font-weight: 700 !important;
        }}
        
        /* Captions */
        .stCaption, .caption {{
            color: #4b5563 !important;
            font-weight: 600 !important;
        }}
        
        /* Buttons */
        .stButton>button {{
            background-color: #2563eb !important;
            color: white !important;
            border-radius: 999px !important;
            border: none !important;
            font-weight: 700 !important;
            padding: 0.5rem 2rem !important;
            transition: all 0.3s ease !important;
        }}
        .stButton>button:hover {{
            background-color: #1d4ed8 !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4) !important;
        }}
        
        /* Form labels */
        label {{
            font-weight: 700 !important;
            color: #111827 !important;
        }}
        
        /* Input fields */
        .stTextInput>div>div>input,
        .stNumberInput>div>div>input {{
            border-radius: 0.5rem !important;
            border: 2px solid #e5e7eb !important;
        }}
        
        /* Expander */
        .streamlit-expanderHeader {{
            background-color: rgba(37, 99, 235, 0.1) !important;
            border-radius: 0.5rem !important;
            font-weight: 600 !important;
        }}
        
        /* Download button special styling */
        .stDownloadButton>button {{
            background-color: #10b981 !important;
        }}
        .stDownloadButton>button:hover {{
            background-color: #059669 !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def get_pdf_bg_for_destination(destination: str):
    """Get PDF background image path for destination."""
    if not destination:
        return GENERIC_PDF_BG if Path(GENERIC_PDF_BG).exists() else None
    
    dest_key = destination.strip().lower()
    
    # Exact match first
    if dest_key in DEST_PDF_BG and Path(DEST_PDF_BG[dest_key]).exists():
        return DEST_PDF_BG[dest_key]
    
    # Substring fallback
    for key, path in DEST_PDF_BG.items():
        if (key in dest_key or dest_key in key) and Path(path).exists():
            return path
    
    # Generic fallback
    return GENERIC_PDF_BG if Path(GENERIC_PDF_BG).exists() else None


def get_multiple_images_for_destination(destination: str, count: int = 3):
    """Get multiple images for a destination using verified sources and variations."""
    images = []
    
    # Get the primary verified image
    img_url_base = pick_bg_image(destination)
    
    try:
        print(f"Fetching primary image for {destination}...")
        response = requests.get(img_url_base, timeout=10)
        if response.status_code == 200:
            images.append(ImageReader(io.BytesIO(response.content)))
            print(f"✓ Primary image loaded")
    except Exception as e:
        print(f"✗ Could not fetch primary image: {e}")
    
    # Try to get additional images with different Unsplash IDs
    # Using random parameter to get different images from same search
    dest_lower = destination.lower().strip()
    
    # Try variation 1: landmark focus
    try:
        query1 = quote(f"{destination} landmark architecture")
        url1 = f"https://source.unsplash.com/800x600/?{query1}&sig=1"
        response = requests.get(url1, timeout=10, allow_redirects=True)
        if response.status_code == 200:
            images.append(ImageReader(io.BytesIO(response.content)))
            print(f"✓ Landmark variation loaded")
    except Exception as e:
        print(f"✗ Variation 1 failed: {e}")
    
    # Try variation 2: cityscape/skyline
    if len(images) < count:
        try:
            query2 = quote(f"{destination} skyline city view")
            url2 = f"https://source.unsplash.com/800x600/?{query2}&sig=2"
            response = requests.get(url2, timeout=10, allow_redirects=True)
            if response.status_code == 200:
                images.append(ImageReader(io.BytesIO(response.content)))
                print(f"✓ Cityscape variation loaded")
        except Exception as e:
            print(f"✗ Variation 2 failed: {e}")
    
    # Try variation 3: tourist attraction
    if len(images) < count:
        try:
            query3 = quote(f"{destination} tourist attraction")
            url3 = f"https://source.unsplash.com/800x600/?{query3}&sig=3"
            response = requests.get(url3, timeout=10, allow_redirects=True)
            if response.status_code == 200:
                images.append(ImageReader(io.BytesIO(response.content)))
                print(f"✓ Tourist attraction variation loaded")
        except Exception as e:
            print(f"✗ Variation 3 failed: {e}")
    
    print(f"Total images loaded: {len(images)}")
    return images if images else None


def make_pdf_page_with_watermark(destination_images, page_num_container):
    """Create PDF page handler with rotating destination image watermarks."""
    def on_page(c: canvas.Canvas, doc):
        c.saveState()
        
        # Add watermark images if available - rotate through them
        if destination_images and len(destination_images) > 0:
            w, h = LETTER
            try:
                # Use different image on each page (cycle through available images)
                img_index = page_num_container[0] % len(destination_images)
                current_img = destination_images[img_index]
                
                # Calculate position for bottom-right watermark
                img_width = 3.5 * inch
                img_height = 3.5 * inch
                x_pos = w - img_width - 0.5 * inch
                y_pos = 0.5 * inch
                
                # Draw watermark with low opacity
                c.setFillAlpha(0.07)
                c.drawImage(current_img, x_pos, y_pos, 
                           width=img_width, height=img_height,
                           preserveAspectRatio=True, mask='auto')
                
                # Also add a smaller watermark in top-left
                if len(destination_images) > 1:
                    alt_img_index = (img_index + 1) % len(destination_images)
                    alt_img = destination_images[alt_img_index]
                    c.setFillAlpha(0.05)
                    c.drawImage(alt_img, 0.5 * inch, h - 3 * inch, 
                               width=2.5 * inch, height=2.5 * inch,
                               preserveAspectRatio=True, mask='auto')
                
                c.setFillAlpha(1.0)
                
                # Increment page counter
                page_num_container[0] += 1
            except Exception as e:
                print(f"Error adding watermark: {e}")
        
        c.restoreState()
    return on_page

# --------------------------------------------
# SESSION STATE
# --------------------------------------------


def init_session_state():
    """Initialize session state with defaults."""
    defaults = {
        "source_city": "Dallas, Texas",
        "destination": "",
        "start_date": datetime.now().date(),
        "end_date": (datetime.now() + timedelta(days=3)).date(),
        "days": 3,
        "interests": "",
        "guardrails": "",
        "plan_md": "",
        "last_bg_destination": "",  # Track background changes
        "airline_info": "",  # Store airline recommendations
    }
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)


def reset_form():
    """Reset form and clear plan."""
    st.session_state.source_city = "Dallas, Texas"
    st.session_state.destination = ""
    st.session_state.start_date = datetime.now().date()
    st.session_state.end_date = (datetime.now() + timedelta(days=3)).date()
    st.session_state.days = 3
    st.session_state.interests = ""
    st.session_state.guardrails = ""
    st.session_state.plan_md = ""
    st.session_state.airline_info = ""
    st.session_state.last_bg_destination = ""
    st.rerun()


init_session_state()

# --------------------------------------------
# PROMPTS
# --------------------------------------------

SYSTEM_PROMPT = dedent("""
You are an expert travel planner with deep knowledge of destinations worldwide and airline services.

Rules:
- Generate a realistic, well-paced day-by-day itinerary
- Each day must include Morning, Afternoon, and Evening activities
- Respect all user guardrails strictly
- Optimize pacing (no rushing, allow time for meals and rest)
- Include specific landmark names, restaurants, and practical tips
- Use clear Markdown formatting with ## for day headers
- IMPORTANT: After providing the date range, include expected temperature, weather, and clothing advice in this exact format:
  **Expected Temperature:** [temperature range] (e.g., 15-25°C / 59-77°F)
  **Weather:** [typical weather conditions] (e.g., Mild and sunny, occasional rain)
  **What to Wear:** [specific clothing recommendations based on weather and local customs] (e.g., Light layers, comfortable walking shoes, sun hat. Modest clothing recommended for religious sites.)
- At the END of your itinerary, add a section titled "## ✈️ Recommended Airlines" with 2-3 best airline options for this route, including why they're good choices (direct flights, price, comfort, etc.)

Output format:

**Travel Dates:** [dates]
**Expected Temperature:** [temp range in both Celsius and Fahrenheit]
**Weather:** [weather description]
**What to Wear:** [clothing advice considering weather, activities, and local customs]

## Day 1
**Morning:**
- Activity with details

**Afternoon:**
- Activity with details

**Evening:**
- Activity with details

...

## ✈️ Recommended Airlines
**[Airline Name 1]**
- Why it's a good choice (direct flights, service quality, typical price range)

**[Airline Name 2]**
- Why it's a good choice
""").strip()


def build_user_prompt(source_city, destination, start_date, end_date, days, interests, guardrails):
    """Build user prompt from form inputs."""
    date_range = f"{start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')}"
    
    return dedent(f"""
    Traveling FROM: {source_city}
    Traveling TO: {destination}
    Travel dates: {date_range}
    Number of days: {days}
    Special interests: {interests or "General sightseeing, culture, and local experiences"}
    Guardrails/Restrictions: {guardrails or "None"}

    Create a detailed travel itinerary that makes the most of the time available.
    
    IMPORTANT: Start your response with:
    **Travel Dates:** {date_range}
    **Expected Temperature:** [provide temperature range in both °C and °F for {destination} during these dates]
    **Weather:** [describe typical weather conditions]
    **What to Wear:** [provide specific clothing recommendations based on the weather, planned activities, and local customs/culture]
    
    Then provide the day-by-day itinerary with specific recommendations and practical tips.
    
    At the end, recommend 2-3 best airlines for flights from {source_city} to {destination}, considering factors like direct flights, service quality, and typical pricing.
    """).strip()

# --------------------------------------------
# OPENAI CALL
# --------------------------------------------


def generate_travel_plan(source_city, destination, start_date, end_date, days, interests, guardrails):
    """Generate travel plan using OpenAI API."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": build_user_prompt(
                    source_city, destination, start_date, end_date, days, interests, guardrails
                ),
            },
        ],
        temperature=0.7,
    )
    return response.choices[0].message.content

# --------------------------------------------
# PDF GENERATION
# --------------------------------------------


def generate_pdf(plan_md: str, destination: str, source_city: str, start_date, end_date, days: int) -> str:
    """Generate beautifully formatted PDF from markdown plan with multiple destination images."""
    filename = f"travel_plan_{destination.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    doc = SimpleDocTemplate(
        filename,
        pagesize=LETTER,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.9 * inch,
        bottomMargin=0.9 * inch,
    )

    # Get multiple destination images for variety
    print(f"Fetching images for {destination}...")
    destination_images = get_multiple_images_for_destination(destination, count=3)
    if destination_images:
        print(f"Successfully loaded {len(destination_images)} images for PDF watermarks")
    else:
        print("No images loaded for watermarks")

    # Enhanced styles
    styles = getSampleStyleSheet()
    
    # Title style
    styles.add(
        ParagraphStyle(
            name="CustomTitle",
            fontSize=24,
            leading=28,
            spaceAfter=6,
            textColor=HexColor("#1f2933"),
            fontName="Helvetica-Bold",
            alignment=TA_CENTER,
        )
    )
    
    # Subtitle style (for dates and temperature info)
    styles.add(
        ParagraphStyle(
            name="CustomSubtitle",
            fontSize=11,
            leading=15,
            spaceAfter=8,
            textColor=HexColor("#4b5563"),
            fontName="Helvetica",
            alignment=TA_CENTER,
        )
    )
    
    # Day header style
    styles.add(
        ParagraphStyle(
            name="DayHeader",
            fontSize=16,
            leading=20,
            spaceAfter=12,
            spaceBefore=16,
            textColor=HexColor("#2563eb"),
            fontName="Helvetica-Bold",
            alignment=TA_LEFT,
        )
    )
    
    # Section header style (Morning, Afternoon, Evening)
    styles.add(
        ParagraphStyle(
            name="SectionHeader",
            fontSize=12,
            leading=16,
            spaceAfter=8,
            spaceBefore=4,
            textColor=HexColor("#1f2933"),
            fontName="Helvetica-Bold",
        )
    )
    
    # Body text style
    styles.add(
        ParagraphStyle(
            name="CustomBody",
            fontSize=10,
            leading=14,
            spaceAfter=6,
            textColor=HexColor("#374151"),
            fontName="Helvetica",
        )
    )
    
    # Airline header style
    styles.add(
        ParagraphStyle(
            name="AirlineHeader",
            fontSize=14,
            leading=18,
            spaceAfter=12,
            spaceBefore=20,
            textColor=HexColor("#059669"),
            fontName="Helvetica-Bold",
        )
    )

    story = []
    
    # Add title page
    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph(f"Travel Itinerary", styles["CustomTitle"]))
    story.append(Spacer(1, 0.1 * inch))
    story.append(Paragraph(f"{source_city} → {destination}", styles["CustomTitle"]))
    story.append(Spacer(1, 0.3 * inch))
    
    # Extract and display temperature info from the markdown if present
    temp_info_lines = []
    other_content_lines = []
    capturing_temp = True
    
    for line in plan_md.split("\n"):
        if line.strip().startswith("**Travel Dates:**") or \
           line.strip().startswith("**Expected Temperature:**") or \
           line.strip().startswith("**Weather:**") or \
           line.strip().startswith("**What to Wear:**"):
            temp_info_lines.append(line.strip())
        elif line.strip().startswith("##"):
            capturing_temp = False
            other_content_lines.append(line)
        elif not capturing_temp or (line.strip() and not line.strip().startswith("**")):
            capturing_temp = False
            other_content_lines.append(line)
    
    # Display temperature and weather info on title page
    if temp_info_lines:
        for info_line in temp_info_lines:
            story.append(Paragraph(info_line, styles["CustomSubtitle"]))
    else:
        # Fallback if AI didn't include it
        date_range = f"{start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}"
        story.append(Paragraph(f"**Travel Dates:** {date_range}", styles["CustomSubtitle"]))
        story.append(Paragraph(f"**Duration:** {days} day{'s' if days != 1 else ''}", styles["CustomSubtitle"]))
    
    story.append(Spacer(1, 0.4 * inch))
    
    # Divider line
    story.append(Spacer(1, 12))

    buffer_list_items = []
    in_airline_section = False
    skip_temp_info = True  # Skip temperature info lines since we already displayed them

    # Use filtered content that excludes already-displayed temp info
    content_to_process = "\n".join(other_content_lines) if temp_info_lines else plan_md

    for line in content_to_process.split("\n"):
        line_stripped = line.strip()
        
        # Skip the temperature/weather/clothing info lines if they appear in content
        if line_stripped.startswith("**Travel Dates:**") or \
           line_stripped.startswith("**Expected Temperature:**") or \
           line_stripped.startswith("**Weather:**") or \
           line_stripped.startswith("**What to Wear:**"):
            continue
        
        # Check if we're entering airline section
        if "✈️" in line_stripped or "airline" in line_stripped.lower():
            in_airline_section = True
        
        if line.startswith("##"):
            # Flush any buffered list items
            if buffer_list_items:
                story.append(
                    ListFlowable(
                        buffer_list_items,
                        bulletType="bullet",
                        leftIndent=20,
                        bulletFontSize=10,
                    )
                )
                buffer_list_items = []
            
            story.append(Spacer(1, 8))
            header_text = line.replace("##", "").strip()
            
            # Use different style for airline section
            if in_airline_section:
                story.append(Paragraph(header_text, styles["AirlineHeader"]))
            else:
                story.append(Paragraph(header_text, styles["DayHeader"]))
                
        elif line_stripped.startswith("**") and line_stripped.endswith("**"):
            # Section headers like "Morning:", "Afternoon:", etc.
            if buffer_list_items:
                story.append(
                    ListFlowable(
                        buffer_list_items,
                        bulletType="bullet",
                        leftIndent=20,
                        bulletFontSize=10,
                    )
                )
                buffer_list_items = []
            story.append(Paragraph(line_stripped, styles["SectionHeader"]))
            
        elif line_stripped.startswith("-"):
            # List items
            buffer_list_items.append(
                ListItem(Paragraph(line_stripped[1:].strip(), styles["CustomBody"]))
            )
        elif line_stripped:
            # Regular paragraphs
            if buffer_list_items:
                story.append(
                    ListFlowable(
                        buffer_list_items,
                        bulletType="bullet",
                        leftIndent=20,
                        bulletFontSize=10,
                    )
                )
                buffer_list_items = []
            story.append(Paragraph(line_stripped, styles["CustomBody"]))

    # Flush any remaining list items
    if buffer_list_items:
        story.append(
            ListFlowable(
                buffer_list_items,
                bulletType="bullet",
                leftIndent=20,
                bulletFontSize=10,
            )
        )

    # Build PDF with rotating watermarks
    # Use a list to track page numbers (mutable container for closure)
    page_counter = [0]
    on_page_fn = make_pdf_page_with_watermark(destination_images, page_counter)
    doc.build(story, onFirstPage=on_page_fn, onLaterPages=on_page_fn)
    
    return filename

# --------------------------------------------
# UI
# --------------------------------------------

# Update background if destination changed
current_dest = st.session_state.destination or ""
if current_dest != st.session_state.last_bg_destination:
    set_destination_background(current_dest)
    st.session_state.last_bg_destination = current_dest
else:
    # Show generic travel background on initial load
    set_destination_background("")

st.title("🌍 AI Travel Guide")
st.caption("Personalized itineraries with stunning destination backgrounds")

with st.expander("ℹ️ How it works"):
    st.markdown(
        """
        1. **Enter your destination** - The background will automatically change to match
        2. **Set your preferences** - Number of days, interests, and any restrictions
        3. **Generate your plan** - Get a detailed day-by-day itinerary
        4. **Download as PDF** - Save your itinerary with a beautiful layout
        
        Try destinations like: Paris, Tokyo, New York, Karachi, Athens, London, Rome, Dubai, Barcelona, Sydney
        """
    )

# Two-column layout
left_col, right_col = st.columns([1, 2])

with left_col:
    st.subheader("📝 Plan Your Trip")

    with st.form("travel_form"):
        # Source and Destination in same row
        col_cities1, col_cities2 = st.columns(2)
        with col_cities1:
            source_city_input = st.text_input(
                "🛫 From (Source City)",
                value=st.session_state.source_city,
                placeholder="e.g., Dallas, New York, London...",
                help="Where are you traveling from?"
            )
        
        with col_cities2:
            destination_input = st.text_input(
                "🛬 To (Destination)",
                value=st.session_state.destination,
                placeholder="e.g., Paris, Tokyo, Karachi...",
                help="Where do you want to go?"
            )
        
        # Date inputs
        col_date1, col_date2 = st.columns(2)
        with col_date1:
            start_date_input = st.date_input(
                "📅 Start Date",
                value=st.session_state.start_date,
                min_value=datetime.now().date(),
                help="When does your trip start?"
            )
        
        with col_date2:
            end_date_input = st.date_input(
                "📅 End Date",
                value=st.session_state.end_date,
                min_value=datetime.now().date(),
                help="When does your trip end?"
            )
        
        # Calculate days automatically - ALWAYS show this
        if start_date_input and end_date_input and end_date_input >= start_date_input:
            calculated_days = (end_date_input - start_date_input).days + 1
            st.success(f"📊 Trip duration: **{calculated_days} day{'s' if calculated_days != 1 else ''}**")
        elif start_date_input and end_date_input:
            st.error("⚠️ End date must be on or after start date")
            calculated_days = 1
        else:
            calculated_days = 3

        interests_input = st.text_input(
            "❤️ Special Interests",
            value=st.session_state.interests,
            placeholder="e.g., Museums, Food, Nature, Nightlife...",
            help="What are you most interested in experiencing?"
        )

        guardrails_input = st.text_input(
            "⚠️ Restrictions/Guardrails",
            value=st.session_state.guardrails,
            placeholder="e.g., Family-friendly, No walking tours, Budget-conscious...",
            help="Any restrictions or preferences to consider?"
        )

        submitted = st.form_submit_button("✨ Generate Travel Plan", use_container_width=True)

with right_col:
    if submitted:
        if not source_city_input.strip():
            st.error("⚠️ Please enter your source city.")
        elif not destination_input.strip():
            st.error("⚠️ Please enter a destination.")
        elif calculated_days < 1:
            st.error("⚠️ Please select valid travel dates (end date must be after start date).")
        else:
            # Update session state
            st.session_state.source_city = source_city_input
            st.session_state.destination = destination_input
            st.session_state.start_date = start_date_input
            st.session_state.end_date = end_date_input
            st.session_state.days = calculated_days
            st.session_state.interests = interests_input
            st.session_state.guardrails = guardrails_input
            
            # Update background immediately
            set_destination_background(destination_input)
            st.session_state.last_bg_destination = destination_input

            with st.spinner(f"🗺️ Creating your personalized {calculated_days}-day itinerary from {source_city_input} to {destination_input}..."):
                try:
                    plan = generate_travel_plan(
                        source_city_input,
                        destination_input,
                        start_date_input,
                        end_date_input,
                        calculated_days,
                        interests_input,
                        guardrails_input,
                    )
                    st.session_state.plan_md = plan
                    st.success(f"✅ Your {source_city_input} → {destination_input} itinerary is ready!")
                except Exception as e:
                    st.error(f"❌ Error generating plan: {str(e)}")

    if st.session_state.plan_md:
        st.markdown("---")
        st.subheader(f"✈️ {st.session_state.source_city} → {st.session_state.destination}")
        st.caption(f"🗓️ {st.session_state.start_date.strftime('%B %d, %Y')} - {st.session_state.end_date.strftime('%B %d, %Y')} ({st.session_state.days} days)")
        st.markdown(st.session_state.plan_md)

        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            try:
                pdf_path = generate_pdf(
                    st.session_state.plan_md,
                    st.session_state.destination,
                    st.session_state.source_city,
                    st.session_state.start_date,
                    st.session_state.end_date,
                    st.session_state.days,
                )
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        "📄 Download PDF",
                        f,
                        file_name=pdf_path,
                        mime="application/pdf",
                        use_container_width=True,
                    )
            except Exception as e:
                st.error(f"Error generating PDF: {str(e)}")

        with col2:
            if st.button("🔄 Start Over", use_container_width=True):
                reset_form()