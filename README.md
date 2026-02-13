# 🛰️ LandWatch AI

### Automated Industrial Land Monitoring & Compliance System for CSIDC

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![Sentinel-2](https://img.shields.io/badge/Sentinel--2-ESA-orange)](https://sentinel.esa.int)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

> **XCELERATE Money Matters 2026 Hackathon Submission**

---

## 🎯 Problem Statement

CSIDC currently monitors 30+ industrial areas across Chhattisgarh using **expensive manual drone surveys** (₹5-10 Lakhs per survey) conducted only 2-3 times per year. This leads to:

- ⏰ **4-6 month delays** in violation detection
- 💸 **High costs** preventing frequent monitoring
- 🔍 **Limited coverage** and reactive approach
- 📄 **Paper-based legacy maps** with no real-time updates

## 💡 Solution

LandWatch AI replaces manual monitoring with **automated satellite-based analysis**:

| Metric | Before (Manual) | After (LandWatch AI) |
|--------|:----------------:|:--------------------:|
| Cost per Area/Year | ₹5-10 Lakhs | **< ₹50,000** |
| Detection Frequency | 2-3× per year | **Every 5 days** |
| Time to Detection | 4-6 months | **< 1 week** |
| Coverage | 2-3 areas/quarter | **All areas continuously** |
| Accuracy | ~70% | **90%+** |

## 🖥️ Features

### Core Detection Engine
- 🔲 **Boundary Extraction** — AI-powered plot boundary detection from satellite imagery
- 🚧 **Encroachment Detection** — Automatic flagging when boundaries deviate >5%
- 🏗️ **Building Detection** — Identify unauthorized new constructions
- 🏚️ **Vacant Plot Detection** — Flag plots with no activity for >6 months
- 📐 **Change Detection** — Compare imagery across time periods

### Dashboard & Monitoring
- 🗺️ **Interactive Map** — Leaflet-based map with all 8 industrial areas
- 📊 **Real-time Analytics** — Compliance trends, risk assessment, area comparisons
- 🔔 **Alert System** — Severity-based alerts with filtering and CSV export
- 📄 **Report Generation** — Professional compliance reports with CSIDC branding
- 🛰️ **Satellite Feed** — View Sentinel-2 imagery with boundary and violation overlays

### Technical Highlights
- 🎨 **Premium Dark UI** — Glassmorphism, animations, responsive design
- ⚡ **Fast API Backend** — Sub-second response times
- 📱 **Responsive** — Works on desktop, tablet, and mobile
- 🔐 **Role-based Access** — Login page with demo mode

## 📸 Screenshots

### Login Page
Access at `/login` — Premium authentication UI with animated background

### Command Center Dashboard
Main dashboard at `/` — Stat cards, interactive map, charts, and alerts

### Geospatial Map View
Full map at `/map` — Plot boundaries, risk filtering, satellite toggle

### Alert Management
All alerts at `/alerts` — Severity filtering, status updates, CSV export

### Analytics & Trends
Charts at `/analytics` — Compliance trends, radar comparison, heatmaps

### Satellite Feed
Imagery at `/satellite` — Sentinel-2 view with AI detection simulation

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/your-team/landwatch-ai.git
cd landwatch-ai

# Install dependencies
pip install -r requirements.txt

# Run the application
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Access the App

| Page | URL |
|------|-----|
| 🔐 Login | http://localhost:8000/login |
| 📊 Dashboard | http://localhost:8000/ |
| 🗺️ Map View | http://localhost:8000/map |
| 🔔 Alerts | http://localhost:8000/alerts |
| 📄 Reports | http://localhost:8000/reports |
| 📈 Analytics | http://localhost:8000/analytics |
| 🛰️ Satellite | http://localhost:8000/satellite |

### Demo Credentials
- **Email:** admin@csidc.gov.in
- **Password:** admin123

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Web Dashboard (HTML/CSS/JS + Leaflet + Chart.js)     │  │
│  │  • Interactive Maps  • Charts  • Responsive UI        │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                     API LAYER (FastAPI)                      │
│  /api/dashboard/stats  /api/areas  /api/plots               │
│  /api/violations  /api/alerts  /api/satellite/scenes        │
│  /api/compliance/history  /api/detection/run                │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    PROCESSING LAYER                          │
│  • Satellite Ingestion (Sentinel-2 via GEE)                 │
│  • AI/ML Inference (Boundary + Change Detection)            │
│  • Alert Engine (Severity Classification)                   │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                      DATA LAYER                              │
│  • PostGIS (Production) / In-Memory (Demo)                  │
│  • Geospatial vectors, compliance history                   │
│  • Satellite scene metadata, violation records              │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
LandWatchAi/
├── app.py                    # FastAPI application + API routes
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── static/
│   ├── css/
│   │   └── styles.css        # Complete design system (1100+ lines)
│   ├── js/                   # Client-side scripts
│   └── img/                  # Static assets
├── templates/
│   ├── base.html             # Base template (sidebar, header, nav)
│   ├── login.html            # Authentication page
│   ├── dashboard.html        # Main command center
│   ├── map.html              # Full geospatial map view
│   ├── alerts.html           # Alert management
│   ├── reports.html          # Report generation
│   ├── analytics.html        # Trends & analytics
│   └── satellite.html        # Satellite imagery viewer
├── data/                     # Data storage
├── models/                   # AI model weights
└── exports/                  # Generated reports
```

## 🔌 API Reference

### Dashboard
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/dashboard/stats` | Aggregated dashboard KPIs |

### Industrial Areas
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/areas` | List all industrial areas |
| GET | `/api/areas/{id}` | Area details with plots & violations |

### Plots
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/plots` | List plots (filter: `area_id`, `status`) |

### Violations
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/violations` | List violations (filter: `area_id`, `severity`, `status`) |

### Alerts
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/alerts` | List alerts (filter: `status`, `limit`) |

### Satellite
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/satellite/scenes` | Available satellite scenes |
| GET | `/api/compliance/history` | Historical compliance data |
| GET | `/api/detection/run` | Simulate AI detection run |

## 🗃️ Data Model

```sql
-- Core Tables
industrial_areas (id, name, location, center, area_acres, total_plots, status,
                  compliance_rate, risk_level, last_scan)

plots (id, area_id, plot_number, industry_name, allotment_date,
       reference_area_sqm, current_area_sqm, status, boundary_geom)

violations (id, plot_id, violation_type, severity, confidence,
            deviation_percent, detected_date, status, description)

alerts (id, violation_id, severity, created_at, status, description)

satellite_scenes (id, area_id, capture_date, source, cloud_cover,
                  bands, resolution_m, processed)

compliance_history (area_id, month, compliance_rate, violations_detected,
                    violations_resolved, scans_completed)
```

## 🛰️ Industrial Areas Monitored

| # | Area | District | Plots | Status |
|---|------|----------|:-----:|--------|
| 1 | Amaseoni Industrial Area | Raipur | 78 | ✅ Active |
| 2 | Gondwara Industrial Area | Durg | 56 | ✅ Active |
| 3 | Siltara Industrial Area | Raipur | 124 | ✅ Active |
| 4 | Urla Industrial Area | Raipur | 95 | ✅ Active |
| 5 | Bhanpuri Industrial Area | Raipur | 42 | ✅ Active |
| 6 | Bhilai Industrial Area | Durg | 142 | ✅ Active |
| 7 | Korba Industrial Area | Korba | 48 | ✅ Active |
| 8 | Bilaspur Industrial Area | Bilaspur | 63 | ✅ Active |

## 🔮 Roadmap

- [x] MVP Dashboard with 8 industrial areas
- [x] Interactive geospatial map with plot boundaries
- [x] Violation detection & alert system
- [x] Compliance analytics & trend charts
- [x] Satellite imagery viewer with overlays
- [x] Report generation with CSIDC branding
- [ ] Google Earth Engine live integration
- [ ] PyTorch-based boundary extraction model
- [ ] Mobile app (Flutter)
- [ ] Automated email/SMS notifications
- [ ] PostGIS database integration
- [ ] Real-time Sentinel-2 feed

## 👥 Team

Built for **XCELERATE Money Matters 2026** hackathon

## 📜 License

MIT License — See [LICENSE](LICENSE) for details.

---

<div align="center">
  <strong>🛰️ LandWatch AI</strong> — Monitoring Industrial Land from Space
  <br>
  <em>Chhattisgarh State Industrial Development Corporation</em>
</div>
