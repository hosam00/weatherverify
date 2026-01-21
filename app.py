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
# CUSTOM CSS FOR PROFESSIONAL LOOK
# ===============================

st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        text-align: center;
    }
    .verdict-significant {
        color: #d32f2f;
        font-size: 1.3rem;
        font-weight: 700;
        padding: 1rem;
        background-color: #ffebee;
        border-radius: 0.5rem;
        text-align: center;
    }
    .verdict-minor {
        color: #388e3c;
        font-size: 1.3rem;
        font-weight: 700;
        padding: 1rem;
        background-color: #e8f5e9;
        border-radius: 0.5rem;
        text-align: center;
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
    
    # Header
    st.markdown('<p class="main-header">🌦️ WeatherVerify</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Generate Official Weather Reports for Insurance Claims, Event Refunds & Work Disputes</p>', 
                unsafe_allow_html=True)
    
    st.markdown("---")
    
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
        # PAYWALL - Show Payment Link Instead of Download
        # ===============================
        st.subheader("📄 Download Official Report")
        st.write("Generate a professional PDF report to submit with your claim.")
        
        # PayPal Hosted Button - Direct URL (no JavaScript needed)
        # IMPORTANT: Configure Auto-Return URL in PayPal Button Settings to: YOUR_APP_URL?payment=success_confirmed
        PAYPAL_PAYMENT_URL = "https://www.paypal.com/ncp/payment/9MYQFDP4BGTBE"
        
        st.link_button(
            label="� Pay $5 to Download Official PDF",
            url=PAYPAL_PAYMENT_URL,
            use_container_width=True
        )
        
        st.caption("💡 You will be redirected back here automatically after payment to download your file.")
        
        st.info("🔒 **Secure Payment:** Your payment is processed securely through PayPal. After completing payment, you'll be redirected back to download your official weather verification PDF.")
    
    # Footer information
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #666; font-size: 0.9rem;'>
        <p><b>WeatherVerify</b> - Professional Weather Verification Reports</p>
        <p>Data provided by Open-Meteo Weather Archive | Report generated on {}</p>
        <p style='font-size: 0.8rem;'>💡 <i>Tip: Keep your PDF report safe for future reference</i></p>
        </div>
    """.format(datetime.now().strftime('%B %d, %Y')), unsafe_allow_html=True)


if __name__ == "__main__":
    main()
