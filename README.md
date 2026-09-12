# AI Business Operations Copilot

An AI-powered business operations dashboard designed to help businesses monitor sales, manage inventory, analyze customers, and generate data-driven insights.

## Overview

AI Business Operations Copilot combines business analytics with AI-powered assistance to help users make faster and smarter operational decisions.

The application provides a centralized dashboard for sales performance, inventory monitoring, customer analytics, forecasting, reports, and natural-language business queries.

## Key Features

- 📊 Business performance dashboard
- 💰 Sales analytics and revenue tracking
- 📦 Inventory monitoring and reorder recommendations
- 👥 Customer performance and satisfaction analysis
- 📈 AI-powered sales forecasting
- 🤖 AI business assistant for natural-language queries
- 📑 Business reports with CSV export
- 🔐 Role-based login for Admin and Staff
- 🗄️ SQLite database integration

## AI Capabilities

The AI layer is integrated using Google's Gemini API.

It is used for:

- Business question answering
- Sales and performance insights
- Inventory recommendations
- Forecast interpretation
- Business report generation

The application also uses data-driven calculations and analysis with Python and Pandas.

## Technology Stack

### Frontend
- Streamlit

### Backend
- Python

### Database
- SQLite

### Data Analysis
- Pandas
- Plotly

### AI
- Google Gemini API

### Development Tools
- VS Code
- Git
- GitHub

## Project Structure

```text
ai-business-copilot/
│
├── app.py
├── database.py
├── users.py
├── requirements.txt
├── README.md
├── .gitignore
│
└── data/
    ├── sales.csv
    ├── inventory.csv
    └── customers.csv
## Application Screenshots

### Login
![Login](screenshots/login.png)

### Dashboard
![Dashboard](screenshots/dashboard.png)

### AI Assistant
![AI Assistant](screenshots/ai-assistant.png)

### Inventory & AI Recommendations
![Inventory](screenshots/inventory.png)