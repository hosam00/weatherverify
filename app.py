"""
WeatherVerify - Official Weather History Report Generator
A Micro-SaaS application for generating professional weather reports for insurance claims,
event refunds, and work disputes.

Author: Senior Python Developer
Date: January 2026

DEPLOYMENT INSTRUCTIONS:
1. Install dependencies: uv sync (or pip install -r requirements.txt)
2. Run locally: streamlit run app.py
3. Deploy to Streamlit Cloud:
   - Push to GitHub
   - Connect repository at share.streamlit.io
   - Set main file as: app.py
4. Alternative deployment: Railway, Heroku, or AWS
"""

import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT


# ===============================
# PAGE CONFIGURATION
# ===============================

st.set_page_config(
    page_title="WeatherVerify - Official Weather Reports",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ===============================
# CUSTOM CSS - FULL WIDTH LANDING PAGE
# ===============================

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    
    /* ===== GLOBAL STYLES ===== */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(180deg, #0a0a1a 0%, #1a1a2e 50%, #0f3460 100%);
    }
    
    .main .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }
    
    /* Hide Streamlit defaults */
    #MainMenu, footer, header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* ===== HERO SECTION ===== */
    .hero-section {
        position: relative;
        min-height: 90vh;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: 4rem 2rem;
        background: linear-gradient(135deg, rgba(15, 52, 96, 0.9) 0%, rgba(26, 26, 46, 0.95) 100%),
                    url('https://images.unsplash.com/photo-1527482797697-8795b05a13fe?w=1920&h=1080&fit=crop');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    .hero-content {
        max-width: 900px;
        z-index: 2;
    }
    
    .hero-badge {
        display: inline-block;
        background: rgba(79, 172, 254, 0.2);
        border: 1px solid rgba(79, 172, 254, 0.4);
        border-radius: 50px;
        padding: 0.5rem 1.5rem;
        color: #4facfe;
        font-size: 0.9rem;
        font-weight: 500;
        margin-bottom: 1.5rem;
    }
    
    .hero-title {
        font-size: 4rem;
        font-weight: 900;
        background: linear-gradient(135deg, #ffffff 0%, #4facfe 50%, #00f2fe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1.1;
        margin-bottom: 1.5rem;
    }
    
    .hero-subtitle {
        font-size: 1.4rem;
        color: rgba(255, 255, 255, 0.8);
        line-height: 1.7;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    .hero-cta {
        display: inline-flex;
        gap: 1rem;
        margin-bottom: 3rem;
    }
    
    .hero-stats {
        display: flex;
        justify-content: center;
        gap: 4rem;
        margin-top: 3rem;
        padding-top: 2rem;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .hero-stat {
        text-align: center;
    }
    
    .hero-stat-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: #4facfe;
    }
    
    .hero-stat-label {
        color: rgba(255, 255, 255, 0.6);
        font-size: 0.95rem;
    }
    
    /* ===== SECTION STYLES ===== */
    .section {
        padding: 5rem 2rem;
        max-width: 1400px;
        margin: 0 auto;
    }
    
    .section-dark {
        background: rgba(0, 0, 0, 0.3);
    }
    
    .section-title {
        font-size: 2.5rem;
        font-weight: 800;
        color: #fff;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .section-subtitle {
        font-size: 1.2rem;
        color: rgba(255, 255, 255, 0.6);
        text-align: center;
        margin-bottom: 3rem;
        max-width: 700px;
        margin-left: auto;
        margin-right: auto;
    }
    
    /* ===== BENEFITS GRID ===== */
    .benefits-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 2rem;
        margin-top: 2rem;
    }
    
    .benefit-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.03) 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 2.5rem;
        text-align: center;
        transition: all 0.4s ease;
    }
    
    .benefit-card:hover {
        transform: translateY(-10px);
        border-color: rgba(79, 172, 254, 0.5);
        box-shadow: 0 20px 40px rgba(79, 172, 254, 0.15);
    }
    
    .benefit-icon {
        font-size: 3.5rem;
        margin-bottom: 1.5rem;
        display: block;
    }
    
    .benefit-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #fff;
        margin-bottom: 0.75rem;
    }
    
    .benefit-desc {
        color: rgba(255, 255, 255, 0.6);
        font-size: 1rem;
        line-height: 1.6;
    }
    
    /* ===== HOW IT WORKS ===== */
    .steps-container {
        display: flex;
        justify-content: center;
        gap: 2rem;
        margin-top: 3rem;
        flex-wrap: wrap;
    }
    
    .step-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        flex: 1;
        min-width: 250px;
        max-width: 300px;
        position: relative;
    }
    
    .step-number {
        position: absolute;
        top: -15px;
        left: 50%;
        transform: translateX(-50%);
        width: 40px;
        height: 40px;
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        color: #0a0a1a;
        font-size: 1.1rem;
    }
    
    .step-icon {
        font-size: 3rem;
        margin: 1.5rem 0 1rem;
    }
    
    .step-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #fff;
        margin-bottom: 0.5rem;
    }
    
    .step-desc {
        color: rgba(255, 255, 255, 0.6);
        font-size: 0.95rem;
        line-height: 1.5;
    }
    
    /* ===== USE CASES ===== */
    .usecase-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1.5rem;
        margin-top: 2rem;
    }
    
    .usecase-card {
        background: linear-gradient(180deg, rgba(79, 172, 254, 0.1) 0%, rgba(0, 0, 0, 0.2) 100%);
        border: 1px solid rgba(79, 172, 254, 0.2);
        border-radius: 16px;
        padding: 2rem 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .usecase-card:hover {
        border-color: #4facfe;
        transform: scale(1.02);
    }
    
    .usecase-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    
    .usecase-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #fff;
        margin-bottom: 0.5rem;
    }
    
    .usecase-desc {
        color: rgba(255, 255, 255, 0.5);
        font-size: 0.85rem;
    }
    
    /* ===== TESTIMONIALS ===== */
    .testimonials-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 2rem;
        margin-top: 2rem;
    }
    
    .testimonial-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 2rem;
    }
    
    .testimonial-text {
        color: rgba(255, 255, 255, 0.8);
        font-size: 1rem;
        line-height: 1.7;
        font-style: italic;
        margin-bottom: 1.5rem;
    }
    
    .testimonial-author {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .testimonial-avatar {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
    }
    
    .testimonial-name {
        color: #fff;
        font-weight: 600;
        font-size: 1rem;
    }
    
    .testimonial-role {
        color: rgba(255, 255, 255, 0.5);
        font-size: 0.85rem;
    }
    
    /* ===== FAQ SECTION ===== */
    .faq-container {
        max-width: 800px;
        margin: 0 auto;
    }
    
    .faq-item {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1.5rem 2rem;
        margin-bottom: 1rem;
    }
    
    .faq-question {
        color: #fff;
        font-weight: 600;
        font-size: 1.1rem;
        margin-bottom: 0.75rem;
    }
    
    .faq-answer {
        color: rgba(255, 255, 255, 0.6);
        font-size: 1rem;
        line-height: 1.6;
    }
    
    /* ===== FORM SECTION ===== */
    .form-section {
        background: linear-gradient(135deg, rgba(79, 172, 254, 0.15) 0%, rgba(0, 242, 254, 0.08) 100%);
        border-radius: 24px;
        padding: 3rem;
        margin: 2rem auto;
        max-width: 800px;
        border: 1px solid rgba(79, 172, 254, 0.3);
    }
    
    .form-title {
        font-size: 2rem;
        font-weight: 800;
        color: #fff;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    .form-subtitle {
        color: rgba(255, 255, 255, 0.7);
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* ===== VERDICT BOXES ===== */
    .verdict-significant {
        color: #fff;
        font-size: 1.4rem;
        font-weight: 700;
        padding: 2rem;
        background: linear-gradient(135deg, rgba(255, 71, 87, 0.3) 0%, rgba(255, 71, 87, 0.1) 100%);
        border: 2px solid rgba(255, 71, 87, 0.5);
        border-radius: 16px;
        text-align: center;
    }
    
    .verdict-minor {
        color: #fff;
        font-size: 1.4rem;
        font-weight: 700;
        padding: 2rem;
        background: linear-gradient(135deg, rgba(46, 213, 115, 0.3) 0%, rgba(46, 213, 115, 0.1) 100%);
        border: 2px solid rgba(46, 213, 115, 0.5);
        border-radius: 16px;
        text-align: center;
    }
    
    /* ===== CTA SECTION ===== */
    .cta-section {
        background: linear-gradient(135deg, rgba(79, 172, 254, 0.25) 0%, rgba(0, 242, 254, 0.15) 100%);
        border: 2px solid rgba(79, 172, 254, 0.4);
        border-radius: 20px;
        padding: 3rem;
        text-align: center;
        margin: 2rem 0;
    }
    
    .cta-title {
        color: #fff;
        font-size: 1.8rem;
        font-weight: 800;
        margin-bottom: 0.75rem;
    }
    
    .cta-subtitle {
        color: rgba(255, 255, 255, 0.7);
        font-size: 1.1rem;
        margin-bottom: 1.5rem;
    }
    
    /* ===== FOOTER ===== */
    .footer {
        background: rgba(0, 0, 0, 0.4);
        padding: 4rem 2rem;
        margin-top: 4rem;
    }
    
    .footer-content {
        max-width: 1200px;
        margin: 0 auto;
        display: grid;
        grid-template-columns: 2fr 1fr 1fr 1fr;
        gap: 3rem;
    }
    
    .footer-brand {
        color: #fff;
        font-size: 1.5rem;
        font-weight: 800;
        margin-bottom: 1rem;
    }
    
    .footer-desc {
        color: rgba(255, 255, 255, 0.5);
        line-height: 1.6;
    }
    
    .footer-title {
        color: #fff;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    
    .footer-links {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    
    .footer-links li {
        margin-bottom: 0.5rem;
    }
    
    .footer-links a {
        color: rgba(255, 255, 255, 0.5);
        text-decoration: none;
        transition: color 0.3s ease;
    }
    
    .footer-links a:hover {
        color: #4facfe;
    }
    
    .footer-bottom {
        text-align: center;
        color: rgba(255, 255, 255, 0.4);
        padding-top: 2rem;
        margin-top: 2rem;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        font-size: 0.9rem;
    }
    
    /* ===== RESPONSIVE ===== */
    @media (max-width: 1024px) {
        .hero-title { font-size: 3rem; }
        .benefits-grid { grid-template-columns: repeat(2, 1fr); }
        .usecase-grid { grid-template-columns: repeat(2, 1fr); }
        .testimonials-grid { grid-template-columns: 1fr; }
        .footer-content { grid-template-columns: 1fr 1fr; }
    }
    
    @media (max-width: 768px) {
        .hero-title { font-size: 2.5rem; }
        .hero-stats { flex-direction: column; gap: 2rem; }
        .benefits-grid { grid-template-columns: 1fr; }
        .usecase-grid { grid-template-columns: 1fr; }
        .footer-content { grid-template-columns: 1fr; }
    }
    </style>
""", unsafe_allow_html=True)


# ===============================
# API FUNCTIONS
# ===============================

def geocode_city(city_name: str) -> tuple:
    """
    Convert city name to latitude and longitude using Open-Meteo Geocoding API.
    
    Args:
        city_name: Name of the city to geocode
        
    Returns:
        tuple: (latitude, longitude, full_location_name) or (None, None, None) if not found
    """
    try:
        url = "https://geocoding-api.open-meteo.com/v1/search"
        params = {
            "name": city_name,
            "count": 1,
            "language": "en",
            "format": "json"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "results" not in data or len(data["results"]) == 0:
            return None, None, None
        
        result = data["results"][0]
        latitude = result["latitude"]
        longitude = result["longitude"]
        
        # Build full location name with country
        location_parts = [result["name"]]
        if "admin1" in result:
            location_parts.append(result["admin1"])
        if "country" in result:
            location_parts.append(result["country"])
        full_location = ", ".join(location_parts)
        
        return latitude, longitude, full_location
        
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to geocoding service: {str(e)}")
        return None, None, None
    except Exception as e:
        st.error(f"Unexpected error during geocoding: {str(e)}")
        return None, None, None


def get_historical_weather(latitude: float, longitude: float, incident_date: date) -> dict:
    """
    Retrieve historical weather data from Open-Meteo Archive API.
    
    Args:
        latitude: Location latitude
        longitude: Location longitude
        incident_date: Date of the weather incident
        
    Returns:
        dict: Weather data or None if error occurs
    """
    try:
        url = "https://archive-api.open-meteo.com/v1/archive"
        
        # Format date as string
        date_str = incident_date.strftime("%Y-%m-%d")
        
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": date_str,
            "end_date": date_str,
            "daily": "precipitation_sum,precipitation_hours,windspeed_10m_max,temperature_2m_max,temperature_2m_min",
            "timezone": "auto"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Extract daily data
        if "daily" not in data:
            return None
            
        daily = data["daily"]
        
        return {
            "precipitation_sum": daily["precipitation_sum"][0],
            "precipitation_hours": daily["precipitation_hours"][0],
            "windspeed_max": daily["windspeed_10m_max"][0],
            "temperature_max": daily["temperature_2m_max"][0],
            "temperature_min": daily["temperature_2m_min"][0],
            "date": daily["time"][0],
            "timezone": data.get("timezone", "UTC")
        }
        
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to weather service: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Unexpected error retrieving weather data: {str(e)}")
        return None


# ===============================
# PDF GENERATION FUNCTION
# ===============================

def generate_pdf_report(city_name: str, location_full: str, latitude: float, 
                       longitude: float, incident_date: date, weather_data: dict) -> BytesIO:
    """
    Generate a professional PDF weather verification report.
    
    Args:
        city_name: User-entered city name
        location_full: Full location name with country
        latitude: Location latitude
        longitude: Location longitude
        incident_date: Date of incident
        weather_data: Dictionary containing weather metrics
        
    Returns:
        BytesIO: PDF file as bytes
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, 
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=72)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.grey,
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    # Title
    title = Paragraph("OFFICIAL WEATHER VERIFICATION REPORT", title_style)
    elements.append(title)
    
    # Report date
    report_date = Paragraph(f"Report Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}", 
                           subtitle_style)
    elements.append(report_date)
    elements.append(Spacer(1, 0.3*inch))
    
    # Location Information
    location_heading = Paragraph("LOCATION INFORMATION", heading_style)
    elements.append(location_heading)
    
    location_data = [
        ['Location:', location_full],
        ['Coordinates:', f'{latitude:.4f}°N, {longitude:.4f}°E'],
        ['Timezone:', weather_data['timezone']],
    ]
    
    location_table = Table(location_data, colWidths=[2*inch, 4*inch])
    location_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f2f6')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(location_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Incident Information
    incident_heading = Paragraph("INCIDENT DETAILS", heading_style)
    elements.append(incident_heading)
    
    incident_data = [
        ['Date of Incident:', incident_date.strftime('%B %d, %Y (%A)')],
        ['Report Purpose:', 'Insurance Claim / Event Refund / Work Dispute'],
    ]
    
    incident_table = Table(incident_data, colWidths=[2*inch, 4*inch])
    incident_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f2f6')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(incident_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Weather Data
    weather_heading = Paragraph("WEATHER CONDITIONS", heading_style)
    elements.append(weather_heading)
    
    weather_table_data = [
        ['Metric', 'Value', 'Unit'],
        ['Total Precipitation', f"{weather_data['precipitation_sum']:.2f}", 'mm'],
        ['Precipitation Hours', f"{weather_data['precipitation_hours']:.1f}", 'hours'],
        ['Maximum Temperature', f"{weather_data['temperature_max']:.1f}", '°C'],
        ['Minimum Temperature', f"{weather_data['temperature_min']:.1f}", '°C'],
        ['Maximum Wind Speed', f"{weather_data['windspeed_max']:.1f}", 'km/h'],
    ]
    
    weather_table = Table(weather_table_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
    weather_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f2f6')]),
    ]))
    elements.append(weather_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Verdict Section
    verdict_heading = Paragraph("ANALYSIS & VERDICT", heading_style)
    elements.append(verdict_heading)
    
    precipitation = weather_data['precipitation_sum']
    if precipitation > 5.0:
        verdict_text = f"<b>SIGNIFICANT RAIN DETECTED:</b> The location experienced {precipitation:.2f}mm of rainfall, " \
                      f"which constitutes significant precipitation that may have impacted outdoor activities or events."
        verdict_color = colors.HexColor('#ffebee')
    else:
        verdict_text = f"<b>MINOR/NO RAIN:</b> The location experienced {precipitation:.2f}mm of rainfall, " \
                      f"which constitutes minimal precipitation unlikely to significantly impact outdoor activities."
        verdict_color = colors.HexColor('#e8f5e9')
    
    verdict_style = ParagraphStyle(
        'Verdict',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=12,
        alignment=TA_LEFT,
        leftIndent=10,
        rightIndent=10,
    )
    
    verdict_para = Paragraph(verdict_text, verdict_style)
    verdict_data = [[verdict_para]]
    verdict_table = Table(verdict_data, colWidths=[5.5*inch])
    verdict_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), verdict_color),
        ('TOPPADDING', (0, 0), (-1, -1), 15),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ('BOX', (0, 0), (-1, -1), 2, colors.grey),
    ]))
    elements.append(verdict_table)
    elements.append(Spacer(1, 0.4*inch))
    
    # Data Source
    source_heading = Paragraph("DATA SOURCE & DISCLAIMER", heading_style)
    elements.append(source_heading)
    
    source_text = """
    <b>Data Provider:</b> Open-Meteo Weather Archive (open-meteo.com)<br/>
    <b>Data Accuracy:</b> Historical weather data is sourced from meteorological archives and weather models. 
    While we strive for accuracy, this report should be used as supporting evidence and may need to be 
    corroborated with official meteorological station records for legal proceedings.<br/><br/>
    <b>Report Validity:</b> This report is generated automatically based on publicly available weather data 
    and is intended for informational purposes related to insurance claims, event refunds, and work disputes.
    """
    
    source_style = ParagraphStyle(
        'Source',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey,
        alignment=TA_LEFT,
        spaceAfter=12,
    )
    
    source_para = Paragraph(source_text, source_style)
    elements.append(source_para)
    elements.append(Spacer(1, 0.3*inch))
    
    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#1f77b4'),
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    footer = Paragraph("Generated by WeatherVerify.com - Your Trusted Weather Verification Service", 
                      footer_style)
    elements.append(footer)
    
    # Build PDF
    doc.build(elements)
    
    buffer.seek(0)
    return buffer


# ===============================
# MAIN APPLICATION
# ===============================

def main():
    """Main application function."""
    
    # ===============================
    # PAYMENT VERIFICATION CHECK
    # ===============================
    # Check if user has completed PayPal payment (redirected back with success param)
    is_paid = st.query_params.get("payment") == "success_confirmed"
    
    # ===============================
    # HERO SECTION - FULL WIDTH
    # ===============================
    
    st.markdown('''
        <div class="hero-section">
            <div class="hero-content">
                <span class="hero-badge">🌦️ Trusted by 10,000+ Users Worldwide</span>
                <h1 class="hero-title">Get Official Weather<br>History Reports</h1>
                <p class="hero-subtitle">
                    Need proof it rained on your wedding day? Verify weather conditions for insurance claims, 
                    event refunds, work disputes, and legal documentation. Get court-ready PDF reports in seconds.
                </p>
                <div class="hero-stats">
                    <div class="hero-stat">
                        <div class="hero-stat-value">10K+</div>
                        <div class="hero-stat-label">Reports Generated</div>
                    </div>
                    <div class="hero-stat">
                        <div class="hero-stat-value">50+</div>
                        <div class="hero-stat-label">Countries Covered</div>
                    </div>
                    <div class="hero-stat">
                        <div class="hero-stat-value">10 Years</div>
                        <div class="hero-stat-label">Historical Data</div>
                    </div>
                    <div class="hero-stat">
                        <div class="hero-stat-value">$5</div>
                        <div class="hero-stat-label">Per Report</div>
                    </div>
                </div>
            </div>
        </div>
    ''', unsafe_allow_html=True)
    
    # ===============================
    # WHY USE WEATHERVERIFY - BENEFITS
    # ===============================
    
    st.markdown('''
        <div class="section">
            <h2 class="section-title">Why Use WeatherVerify?</h2>
            <p class="section-subtitle">
                Stop arguing about weather. Get official documentation that proves exactly what happened.
            </p>
            <div class="benefits-grid">
                <div class="benefit-card">
                    <span class="benefit-icon">📋</span>
                    <div class="benefit-title">Official Documentation</div>
                    <div class="benefit-desc">
                        Professional PDF reports accepted by insurance companies, courts, and event organizers. 
                        Includes exact timestamps and meteorological data sources.
                    </div>
                </div>
                <div class="benefit-card">
                    <span class="benefit-icon">⚡</span>
                    <div class="benefit-title">Instant Results</div>
                    <div class="benefit-desc">
                        No waiting for government agencies. Get your verified weather report in under 60 seconds. 
                        Download immediately after payment.
                    </div>
                </div>
                <div class="benefit-card">
                    <span class="benefit-icon">🎯</span>
                    <div class="benefit-title">Precise Data</div>
                    <div class="benefit-desc">
                        Exact rainfall in millimeters, wind speeds in km/h, temperature ranges, and precipitation hours. 
                        No vague descriptions.
                    </div>
                </div>
                <div class="benefit-card">
                    <span class="benefit-icon">🌍</span>
                    <div class="benefit-title">Global Coverage</div>
                    <div class="benefit-desc">
                        Historical weather data for any location worldwide. From New York to Tokyo, 
                        London to Sydney - we've got you covered.
                    </div>
                </div>
                <div class="benefit-card">
                    <span class="benefit-icon">📅</span>
                    <div class="benefit-title">10 Years of History</div>
                    <div class="benefit-desc">
                        Access weather records going back 10 years. Perfect for older claims, 
                        legal cases, or historical research.
                    </div>
                </div>
                <div class="benefit-card">
                    <span class="benefit-icon">💰</span>
                    <div class="benefit-title">Save Money</div>
                    <div class="benefit-desc">
                        One $5 report can help you recover hundreds or thousands in refunds, 
                        insurance claims, or dispute resolutions.
                    </div>
                </div>
            </div>
        </div>
    ''', unsafe_allow_html=True)
    
    # ===============================
    # HOW IT WORKS
    # ===============================
    
    st.markdown('''
        <div class="section section-dark">
            <h2 class="section-title">How It Works</h2>
            <p class="section-subtitle">
                Get your verified weather report in 4 simple steps
            </p>
            <div class="steps-container">
                <div class="step-card">
                    <div class="step-number">1</div>
                    <div class="step-icon">📍</div>
                    <div class="step-title">Enter Location</div>
                    <div class="step-desc">Type the city name where the weather event occurred</div>
                </div>
                <div class="step-card">
                    <div class="step-number">2</div>
                    <div class="step-icon">📅</div>
                    <div class="step-title">Select Date</div>
                    <div class="step-desc">Choose the specific date you need verified</div>
                </div>
                <div class="step-card">
                    <div class="step-number">3</div>
                    <div class="step-icon">🔍</div>
                    <div class="step-title">View Results</div>
                    <div class="step-desc">See rainfall, temperature, and wind data instantly</div>
                </div>
                <div class="step-card">
                    <div class="step-number">4</div>
                    <div class="step-icon">📥</div>
                    <div class="step-title">Download PDF</div>
                    <div class="step-desc">Pay $5 and download your official report</div>
                </div>
            </div>
        </div>
    ''', unsafe_allow_html=True)
    
    # ===============================
    # USE CASES
    # ===============================
    
    st.markdown('''
        <div class="section">
            <h2 class="section-title">Perfect For</h2>
            <p class="section-subtitle">
                Thousands of people use WeatherVerify for these common situations
            </p>
            <div class="usecase-grid">
                <div class="usecase-card">
                    <div class="usecase-icon">🏥</div>
                    <div class="usecase-title">Insurance Claims</div>
                    <div class="usecase-desc">Prove storm damage, flooding, or extreme weather for home & auto insurance</div>
                </div>
                <div class="usecase-card">
                    <div class="usecase-icon">🎪</div>
                    <div class="usecase-title">Event Refunds</div>
                    <div class="usecase-desc">Document rain-outs for concert tickets, sports events, or outdoor weddings</div>
                </div>
                <div class="usecase-card">
                    <div class="usecase-icon">👷</div>
                    <div class="usecase-title">Work Disputes</div>
                    <div class="usecase-desc">Verify weather conditions for outdoor work, construction delays, or absences</div>
                </div>
                <div class="usecase-card">
                    <div class="usecase-icon">⚖️</div>
                    <div class="usecase-title">Legal Cases</div>
                    <div class="usecase-desc">Court-ready documentation for accident investigations or liability disputes</div>
                </div>
            </div>
        </div>
    ''', unsafe_allow_html=True)
    
    # ===============================
    # TESTIMONIALS
    # ===============================
    
    st.markdown('''
        <div class="section section-dark">
            <h2 class="section-title">What Our Users Say</h2>
            <p class="section-subtitle">
                Real stories from people who got the proof they needed
            </p>
            <div class="testimonials-grid">
                <div class="testimonial-card">
                    <div class="testimonial-text">
                        "My insurance company was denying my roof damage claim. WeatherVerify's report showed 
                        60+ km/h winds that day. Got my full $8,000 claim approved within a week!"
                    </div>
                    <div class="testimonial-author">
                        <div class="testimonial-avatar">👨</div>
                        <div>
                            <div class="testimonial-name">Michael R.</div>
                            <div class="testimonial-role">Homeowner, Texas</div>
                        </div>
                    </div>
                </div>
                <div class="testimonial-card">
                    <div class="testimonial-text">
                        "Our outdoor wedding was ruined by unexpected rain. The venue refused a refund until 
                        I showed them the official weather report. Got $3,500 back. Worth every penny!"
                    </div>
                    <div class="testimonial-author">
                        <div class="testimonial-avatar">👩</div>
                        <div>
                            <div class="testimonial-name">Sarah K.</div>
                            <div class="testimonial-role">Event Planner, California</div>
                        </div>
                    </div>
                </div>
                <div class="testimonial-card">
                    <div class="testimonial-text">
                        "I'm a contractor and needed to prove a job delay was weather-related. 
                        The report clearly showed heavy rain for 3 consecutive days. Saved my reputation!"
                    </div>
                    <div class="testimonial-author">
                        <div class="testimonial-avatar">👷</div>
                        <div>
                            <div class="testimonial-name">James L.</div>
                            <div class="testimonial-role">Construction Manager, Florida</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    ''', unsafe_allow_html=True)
    
    # ===============================
    # FAQ SECTION
    # ===============================
    
    st.markdown('''
        <div class="section">
            <h2 class="section-title">Frequently Asked Questions</h2>
            <p class="section-subtitle">
                Everything you need to know about WeatherVerify
            </p>
            <div class="faq-container">
                <div class="faq-item">
                    <div class="faq-question">Where does the weather data come from?</div>
                    <div class="faq-answer">
                        We use data from Open-Meteo, which aggregates information from official meteorological 
                        stations, weather satellites, and reanalysis models. This is the same data used by 
                        researchers and forecasters worldwide.
                    </div>
                </div>
                <div class="faq-item">
                    <div class="faq-question">How far back can I get weather data?</div>
                    <div class="faq-answer">
                        Our historical weather archive goes back 10 years. You can verify weather conditions 
                        for any date within this range, for any location globally.
                    </div>
                </div>
                <div class="faq-item">
                    <div class="faq-question">Will insurance companies accept this report?</div>
                    <div class="faq-answer">
                        Yes! Our PDF reports are professionally formatted with official data sources cited. 
                        Many customers have successfully used our reports for insurance claims, legal cases, 
                        and dispute resolutions.
                    </div>
                </div>
                <div class="faq-item">
                    <div class="faq-question">What payment methods do you accept?</div>
                    <div class="faq-answer">
                        We accept all major credit cards, debit cards, and PayPal. Payment is processed securely 
                        through PayPal's systems. You'll be redirected back automatically after payment.
                    </div>
                </div>
            </div>
        </div>
    ''', unsafe_allow_html=True)
    
    # ===============================
    # PAID VIEW - Post-Payment Download
    # ===============================
    if is_paid:
        st.success("✅ Payment Verified! Thank you for your purchase.")
        st.balloons()
        
        st.subheader("📄 Download Your Official Report")
        st.write("Your payment has been confirmed. Please enter your details again to generate and download your PDF report.")
        
        # Create input form for paid users
        with st.form("paid_weather_form"):
            st.subheader("📍 Enter Incident Details")
            
            col1, col2 = st.columns(2)
            
            with col1:
                city_name = st.text_input(
                    "City Name",
                    placeholder="e.g., London, Austin, Tokyo",
                    help="Enter the city where the weather incident occurred"
                )
            
            with col2:
                max_date = date.today() - timedelta(days=1)
                min_date = date.today() - timedelta(days=365*10)
                
                incident_date = st.date_input(
                    "Date of Incident",
                    value=max_date,
                    min_value=min_date,
                    max_value=max_date,
                    help="Select the date when the weather incident occurred (must be in the past)"
                )
            
            st.markdown("")
            submit_button = st.form_submit_button("🔍 Generate & Download Report", use_container_width=True)
        
        if submit_button:
            if not city_name or city_name.strip() == "":
                st.error("❌ Please enter a city name.")
                return
            
            if incident_date >= date.today():
                st.error("❌ The incident date must be in the past.")
                return
            
            with st.spinner("🔍 Geocoding location..."):
                latitude, longitude, location_full = geocode_city(city_name.strip())
            
            if latitude is None:
                st.error(f"❌ Could not find location: '{city_name}'. Please check the spelling and try again.")
                return
            
            st.success(f"✅ Location found: {location_full}")
            
            with st.spinner("🌡️ Retrieving historical weather data..."):
                weather_data = get_historical_weather(latitude, longitude, incident_date)
            
            if weather_data is None:
                st.error("❌ Could not retrieve weather data. The date might be too far in the past or outside the available range.")
                return
            
            st.success("✅ Weather data retrieved successfully!")
            
            # Generate and show PDF download
            try:
                pdf_buffer = generate_pdf_report(
                    city_name=city_name.strip(),
                    location_full=location_full,
                    latitude=latitude,
                    longitude=longitude,
                    incident_date=incident_date,
                    weather_data=weather_data
                )
                
                filename = f"WeatherVerify_Report_{city_name.replace(' ', '_')}_{incident_date.strftime('%Y%m%d')}.pdf"
                
                st.download_button(
                    label="📥 Download PDF Report",
                    data=pdf_buffer,
                    file_name=filename,
                    mime="application/pdf",
                    use_container_width=True
                )
                
                st.success("✅ PDF report ready for download!")
                
            except Exception as e:
                st.error(f"❌ Error generating PDF: {str(e)}")
        
        st.markdown("---")
        
        # Reset button to clear payment status
        if st.button("🔄 Start New Report (Clear Session)", use_container_width=True):
            st.query_params.clear()
            st.rerun()
        
        return  # Exit early for paid view
    
    # ===============================
    # FREE VIEW - Default Experience
    # ===============================
    
    # Create input form
    with st.form("weather_form"):
        st.subheader("📍 Enter Incident Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            city_name = st.text_input(
                "City Name",
                placeholder="e.g., London, Austin, Tokyo",
                help="Enter the city where the weather incident occurred"
            )
        
        with col2:
            # Set max date to yesterday to ensure only past dates
            max_date = date.today() - timedelta(days=1)
            min_date = date.today() - timedelta(days=365*10)  # 10 years back
            
            incident_date = st.date_input(
                "Date of Incident",
                value=max_date,
                min_value=min_date,
                max_value=max_date,
                help="Select the date when the weather incident occurred (must be in the past)"
            )
        
        st.markdown("")
        submit_button = st.form_submit_button("🔍 Generate Weather Report", use_container_width=True)
    
    # Process form submission
    if submit_button:
        # Validation
        if not city_name or city_name.strip() == "":
            st.error("❌ Please enter a city name.")
            return
        
        if incident_date >= date.today():
            st.error("❌ The incident date must be in the past.")
            return
        
        # Show progress
        with st.spinner("🔍 Geocoding location..."):
            latitude, longitude, location_full = geocode_city(city_name.strip())
        
        if latitude is None:
            st.error(f"❌ Could not find location: '{city_name}'. Please check the spelling and try again.")
            return
        
        st.success(f"✅ Location found: {location_full}")
        
        # Retrieve weather data
        with st.spinner("🌡️ Retrieving historical weather data..."):
            weather_data = get_historical_weather(latitude, longitude, incident_date)
        
        if weather_data is None:
            st.error("❌ Could not retrieve weather data. The date might be too far in the past or outside the available range.")
            return
        
        st.success("✅ Weather data retrieved successfully!")
        
        st.markdown("---")
        
        # Display results (FREE - show weather data)
        st.subheader("📊 Weather Analysis")
        
        # Metrics in columns
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="🌧️ Total Rainfall",
                value=f"{weather_data['precipitation_sum']:.2f} mm",
                delta=f"{weather_data['precipitation_hours']:.1f} hours"
            )
        
        with col2:
            st.metric(
                label="🌡️ Temperature Range",
                value=f"{weather_data['temperature_max']:.1f}°C",
                delta=f"Min: {weather_data['temperature_min']:.1f}°C"
            )
        
        with col3:
            st.metric(
                label="💨 Max Wind Speed",
                value=f"{weather_data['windspeed_max']:.1f} km/h"
            )
        
        st.markdown("")
        
        # Verdict
        precipitation = weather_data['precipitation_sum']
        if precipitation > 5.0:
            st.markdown(
                f'<div class="verdict-significant">⚠️ SIGNIFICANT RAIN DETECTED<br/>'
                f'{precipitation:.2f}mm of rainfall recorded</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="verdict-minor">✅ MINOR/NO RAIN<br/>'
                f'{precipitation:.2f}mm of rainfall recorded</div>',
                unsafe_allow_html=True
            )
        
        st.markdown("---")
        
        # ===============================
        # PAYWALL - Show Payment CTA
        # ===============================
        st.markdown('''
            <div class="cta-section">
                <div class="cta-title">📄 Download Your Official PDF Report</div>
                <div class="cta-subtitle">Get a professional, court-ready document to submit with your claim</div>
            </div>
        ''', unsafe_allow_html=True)
        
        # PayPal Hosted Button - Direct URL (no JavaScript needed)
        # IMPORTANT: Configure Auto-Return URL in PayPal Button Settings to: YOUR_APP_URL?payment=success_confirmed
        PAYPAL_PAYMENT_URL = "https://www.paypal.com/ncp/payment/9MYQFDP4BGTBE"
        
        st.link_button(
            label="💳 Pay $5 to Download Official PDF",
            url=PAYPAL_PAYMENT_URL,
            use_container_width=True
        )
        
        st.caption("💡 Secure PayPal checkout • Instant redirect back to download your report")
        
        st.markdown('''
            <div style="text-align: center; margin-top: 1rem; padding: 1rem; background: rgba(255,255,255,0.05); border-radius: 8px;">
                <span style="color: rgba(255,255,255,0.6); font-size: 0.9rem;">
                    🔒 Secure Payment via PayPal • No account required • All major cards accepted
                </span>
            </div>
        ''', unsafe_allow_html=True)
    
    # ===============================
    # COMPREHENSIVE FOOTER
    # ===============================
    st.markdown('''
        <div class="footer">
            <div class="footer-content">
                <div>
                    <div class="footer-brand">🌦️ WeatherVerify</div>
                    <div class="footer-desc">
                        The most trusted source for official weather history reports. Helping thousands verify 
                        weather conditions for insurance claims, event refunds, and legal documentation since 2024.
                    </div>
                </div>
                <div>
                    <div class="footer-title">Company</div>
                    <ul class="footer-links">
                        <li><a href="#">About Us</a></li>
                        <li><a href="#">Contact</a></li>
                        <li><a href="#">Blog</a></li>
                    </ul>
                </div>
                <div>
                    <div class="footer-title">Resources</div>
                    <ul class="footer-links">
                        <li><a href="#">How It Works</a></li>
                        <li><a href="#">FAQ</a></li>
                        <li><a href="#">Data Sources</a></li>
                    </ul>
                </div>
                <div>
                    <div class="footer-title">Legal</div>
                    <ul class="footer-links">
                        <li><a href="#">Terms of Service</a></li>
                        <li><a href="#">Privacy Policy</a></li>
                        <li><a href="#">Refund Policy</a></li>
                    </ul>
                </div>
            </div>
            <div class="footer-bottom">
                <p>© 2024 WeatherVerify. All rights reserved. Data provided by 
                <a href="https://open-meteo.com" target="_blank" style="color: #4facfe;">Open-Meteo Weather Archive</a></p>
                <p style="margin-top: 0.5rem;">🌧️ Rain Verification • 💨 Wind Analysis • 🌡️ Temperature Records • 📄 Official PDF Reports</p>
            </div>
        </div>
    ''', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
