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
    layout="centered",
    initial_sidebar_state="collapsed"
)


# ===============================
# CUSTOM CSS FOR WEATHER-THEMED DESIGN
# ===============================

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    /* Global Styles */
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    }
    
    .main .block-container {
        padding-top: 2rem;
        max-width: 900px;
    }
    
    /* Hero Section */
    .hero-container {
        background: linear-gradient(135deg, rgba(79, 172, 254, 0.15) 0%, rgba(0, 242, 254, 0.1) 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 2.5rem;
        margin-bottom: 2rem;
        backdrop-filter: blur(10px);
        text-align: center;
    }
    
    .main-header {
        font-family: 'Inter', sans-serif;
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 0.5rem;
        text-shadow: 0 0 40px rgba(79, 172, 254, 0.5);
    }
    
    .sub-header {
        font-family: 'Inter', sans-serif;
        font-size: 1.15rem;
        color: rgba(255, 255, 255, 0.7);
        text-align: center;
        margin-bottom: 1rem;
        line-height: 1.6;
    }
    
    /* Trust Badges */
    .trust-badges {
        display: flex;
        justify-content: center;
        gap: 2rem;
        margin-top: 1.5rem;
        flex-wrap: wrap;
    }
    
    .badge {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: rgba(255, 255, 255, 0.6);
        font-size: 0.9rem;
    }
    
    /* Feature Cards */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    .feature-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1.25rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        background: rgba(255, 255, 255, 0.1);
        transform: translateY(-3px);
    }
    
    .feature-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    
    .feature-title {
        color: #fff;
        font-weight: 600;
        font-size: 0.95rem;
        margin-bottom: 0.3rem;
    }
    
    .feature-desc {
        color: rgba(255, 255, 255, 0.5);
        font-size: 0.8rem;
    }
    
    /* Form Styling */
    .stForm {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.5rem;
        backdrop-filter: blur(10px);
    }
    
    /* Verdict Boxes */
    .verdict-significant {
        color: #fff;
        font-size: 1.3rem;
        font-weight: 700;
        padding: 1.5rem;
        background: linear-gradient(135deg, rgba(255, 107, 107, 0.2) 0%, rgba(255, 107, 107, 0.1) 100%);
        border: 1px solid rgba(255, 107, 107, 0.3);
        border-radius: 12px;
        text-align: center;
        backdrop-filter: blur(10px);
    }
    
    .verdict-minor {
        color: #fff;
        font-size: 1.3rem;
        font-weight: 700;
        padding: 1.5rem;
        background: linear-gradient(135deg, rgba(46, 213, 115, 0.2) 0%, rgba(46, 213, 115, 0.1) 100%);
        border: 1px solid rgba(46, 213, 115, 0.3);
        border-radius: 12px;
        text-align: center;
        backdrop-filter: blur(10px);
    }
    
    /* Weather Stats Cards */
    .stats-container {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    .stat-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
    }
    
    .stat-icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    
    .stat-value {
        color: #4facfe;
        font-size: 1.8rem;
        font-weight: 700;
    }
    
    .stat-label {
        color: rgba(255, 255, 255, 0.6);
        font-size: 0.9rem;
    }
    
    /* CTA Section */
    .cta-section {
        background: linear-gradient(135deg, rgba(79, 172, 254, 0.2) 0%, rgba(0, 242, 254, 0.15) 100%);
        border: 1px solid rgba(79, 172, 254, 0.3);
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        margin: 1.5rem 0;
    }
    
    .cta-title {
        color: #fff;
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .cta-subtitle {
        color: rgba(255, 255, 255, 0.7);
        font-size: 1rem;
        margin-bottom: 1rem;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: rgba(255, 255, 255, 0.4);
        font-size: 0.85rem;
        padding: 2rem 0;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        margin-top: 2rem;
    }
    
    /* Weather Image Banner */
    .weather-banner {
        width: 100%;
        height: 200px;
        object-fit: cover;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        opacity: 0.9;
    }
    
    /* Success Box */
    .success-box {
        background: linear-gradient(135deg, rgba(46, 213, 115, 0.2) 0%, rgba(46, 213, 115, 0.1) 100%);
        border: 1px solid rgba(46, 213, 115, 0.3);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        margin: 1rem 0;
    }
    
    .success-title {
        color: #2ed573;
        font-size: 1.5rem;
        font-weight: 700;
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(79, 172, 254, 0.3);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(79, 172, 254, 0.5);
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
    # HERO SECTION WITH WEATHER IMAGE
    # ===============================
    
    # Weather banner image from Unsplash (free to use)
    st.markdown('''
        <img src="https://images.unsplash.com/photo-1534088568595-a066f410bcda?w=1200&h=400&fit=crop" 
             class="weather-banner" alt="Storm clouds over city">
    ''', unsafe_allow_html=True)
    
    # Hero container with title and subtitle
    st.markdown('''
        <div class="hero-container">
            <p class="main-header">🌦️ WeatherVerify</p>
            <p class="sub-header">
                Get Official Weather History Reports for Insurance Claims, Event Refunds & Work Disputes.<br>
                Instant verification • Court-ready documentation • Trusted data sources
            </p>
            <div class="trust-badges">
                <span class="badge">✓ 10,000+ Reports Generated</span>
                <span class="badge">✓ Accurate Historical Data</span>
                <span class="badge">✓ Instant PDF Download</span>
            </div>
        </div>
    ''', unsafe_allow_html=True)
    
    # Feature cards
    st.markdown('''
        <div class="feature-grid">
            <div class="feature-card">
                <div class="feature-icon">🌧️</div>
                <div class="feature-title">Rain Verification</div>
                <div class="feature-desc">Exact rainfall amounts in mm with hourly breakdowns</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">💨</div>
                <div class="feature-title">Wind Analysis</div>
                <div class="feature-desc">Maximum wind speeds and storm conditions</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">📄</div>
                <div class="feature-title">Official PDF Report</div>
                <div class="feature-desc">Professional documentation for claims</div>
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
    
    # Footer information
    st.markdown('''
        <div class="footer">
            <p><strong>WeatherVerify</strong> - Professional Weather Verification Reports</p>
            <p>Data provided by <a href="https://open-meteo.com" target="_blank" style="color: #4facfe;">Open-Meteo Weather Archive</a></p>
            <p style="margin-top: 1rem;">🌧️ Rain • � Wind • 🌡️ Temperature • 📄 Official Reports</p>
        </div>
    ''', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
