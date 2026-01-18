# 🌦️ WeatherVerify - Official Weather History Reports

A professional Micro-SaaS application that generates official weather verification reports for insurance claims, event refunds, and work disputes.

## Features

- 🌍 **Global Coverage**: Search any city worldwide
- 📅 **Historical Data**: Access weather data from the past 10 years
- 📊 **Detailed Analysis**: Precipitation, temperature, and wind speed metrics
- 📄 **Professional PDF Reports**: Download official-looking reports
- 🎯 **Smart Verdict System**: Automatic rain severity assessment
- 🚀 **Fast & Free**: Uses Open-Meteo's free API

## Installation

### Using UV (Recommended)
```bash
uv sync
```

### Using pip
```bash
pip install streamlit requests pandas reportlab
```

## Running the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## How It Works

1. **Enter Location**: Type in any city name
2. **Select Date**: Choose the date of the weather incident (must be in the past)
3. **Generate Report**: Click the button to fetch weather data
4. **Download PDF**: Get a professional PDF report for your records

## Deployment

### Streamlit Cloud (Easiest)
1. Push this repository to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Set `app.py` as the main file
5. Deploy!

### Railway
```bash
railway login
railway init
railway up
```

### Heroku
```bash
heroku create your-app-name
git push heroku main
```

## API Data Sources

- **Geocoding**: Open-Meteo Geocoding API
- **Weather Data**: Open-Meteo Historical Weather Archive

## Use Cases

- 🏠 Insurance claims for weather damage
- 🎪 Event cancellation refunds
- 💼 Work dispute documentation
- 📋 Legal evidence for weather-related issues

## License

MIT License - Feel free to use for commercial purposes

## Support

For issues or questions, please open a GitHub issue.

---

**Built with ❤️ using Streamlit and Python**
