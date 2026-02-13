"""
LandWatch AI - Automated Industrial Land Monitoring & Compliance System
Main FastAPI Application
"""

import os
import json
import random
import math
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List

from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# ─── App Setup ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="LandWatch AI",
    description="Automated Industrial Land Monitoring & Compliance System for CSIDC",
    version="1.0.0"
)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"
DATA_DIR = BASE_DIR / "data"

# Ensure directories exist
STATIC_DIR.mkdir(exist_ok=True)
TEMPLATES_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)
(STATIC_DIR / "css").mkdir(exist_ok=True)
(STATIC_DIR / "js").mkdir(exist_ok=True)
(STATIC_DIR / "img").mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


# ─── Demo Data ───────────────────────────────────────────────────────────────

def generate_demo_data():
    """Generate realistic demo data for CSIDC industrial areas in Chhattisgarh."""

    industrial_areas = [
        {
            "id": 1,
            "name": "Amaseoni Industrial Area",
            "location": "Raipur District",
            "center": [21.2514, 81.6296],
            "area_acres": 450,
            "total_plots": 78,
            "status": "active",
            "compliance_rate": 82,
            "last_scan": "2026-02-12",
            "violations_count": 14,
            "risk_level": "medium"
        },
        {
            "id": 2,
            "name": "Gondwara Industrial Area",
            "location": "Durg District",
            "center": [21.1904, 81.2840],
            "area_acres": 320,
            "total_plots": 56,
            "status": "active",
            "compliance_rate": 74,
            "last_scan": "2026-02-11",
            "violations_count": 22,
            "risk_level": "high"
        },
        {
            "id": 3,
            "name": "Siltara Industrial Area",
            "location": "Raipur District",
            "center": [21.3100, 81.5800],
            "area_acres": 680,
            "total_plots": 124,
            "status": "active",
            "compliance_rate": 91,
            "last_scan": "2026-02-12",
            "violations_count": 8,
            "risk_level": "low"
        },
        {
            "id": 4,
            "name": "Urla Industrial Area",
            "location": "Raipur District",
            "center": [21.2700, 81.5400],
            "area_acres": 520,
            "total_plots": 95,
            "status": "active",
            "compliance_rate": 68,
            "last_scan": "2026-02-10",
            "violations_count": 31,
            "risk_level": "high"
        },
        {
            "id": 5,
            "name": "Bhanpuri Industrial Area",
            "location": "Raipur District",
            "center": [21.2350, 81.6100],
            "area_acres": 180,
            "total_plots": 42,
            "status": "active",
            "compliance_rate": 88,
            "last_scan": "2026-02-12",
            "violations_count": 5,
            "risk_level": "low"
        },
        {
            "id": 6,
            "name": "Bhilai Industrial Area",
            "location": "Durg District",
            "center": [21.2093, 81.3784],
            "area_acres": 750,
            "total_plots": 142,
            "status": "active",
            "compliance_rate": 79,
            "last_scan": "2026-02-11",
            "violations_count": 19,
            "risk_level": "medium"
        },
        {
            "id": 7,
            "name": "Korba Industrial Area",
            "location": "Korba District",
            "center": [22.3595, 82.7501],
            "area_acres": 290,
            "total_plots": 48,
            "status": "active",
            "compliance_rate": 71,
            "last_scan": "2026-02-09",
            "violations_count": 16,
            "risk_level": "high"
        },
        {
            "id": 8,
            "name": "Bilaspur Industrial Area",
            "location": "Bilaspur District",
            "center": [22.0796, 82.1391],
            "area_acres": 340,
            "total_plots": 63,
            "status": "active",
            "compliance_rate": 85,
            "last_scan": "2026-02-12",
            "violations_count": 7,
            "risk_level": "low"
        }
    ]

    # Generate plots for each area
    all_plots = []
    plot_id = 1
    violation_types = ["encroachment", "unauthorized_construction", "boundary_deviation", "vacant_unused", "road_encroachment"]
    industry_names = [
        "Tata Steel Processing", "Rinl Castings Ltd", "Ambuja Cements",
        "Godawari Power & Ispat", "Hira Group Industries", "Jayaswal Neco",
        "Vandana Global", "Prakash Industries", "SKS Power Generation",
        "Monnet Ispat", "Bhushan Steel", "NMDC Steel",
        "Topworth Group", "Raipur Alloys", "Chhattisgarh Steels",
        "Balaji Industrial Corp", "Shri Ganesh Sponge", "Vacant Plot",
        "Under Construction", "Mahaveer Industries"
    ]

    for area in industrial_areas:
        cx, cy = area["center"]
        for i in range(area["total_plots"]):
            # Generate plot boundary as a polygon around the area center
            angle = (2 * math.pi * i) / area["total_plots"]
            radius = random.uniform(0.005, 0.02)
            px = cx + radius * math.cos(angle)
            py = cy + radius * math.sin(angle)

            plot_size = random.uniform(500, 5000)
            half = (plot_size ** 0.5) / 111000 / 2

            status_options = ["compliant", "compliant", "compliant", "violation", "under_review", "vacant"]
            plot_status = random.choice(status_options)

            plot = {
                "id": plot_id,
                "area_id": area["id"],
                "area_name": area["name"],
                "plot_number": f"P-{area['id']:02d}-{i+1:03d}",
                "industry_name": random.choice(industry_names),
                "allotment_date": f"20{random.randint(10,24)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
                "reference_area_sqm": round(plot_size, 1),
                "current_area_sqm": round(plot_size * random.uniform(0.85, 1.15), 1),
                "status": plot_status,
                "lat": round(px, 6),
                "lng": round(py, 6),
                "boundary": [
                    [round(px - half, 6), round(py - half, 6)],
                    [round(px + half, 6), round(py - half, 6)],
                    [round(px + half, 6), round(py + half, 6)],
                    [round(px - half, 6), round(py + half, 6)],
                    [round(px - half, 6), round(py - half, 6)]
                ]
            }
            all_plots.append(plot)
            plot_id += 1

    # Generate violations
    violations = []
    violation_id = 1
    severity_levels = ["critical", "high", "medium", "low"]
    for plot in all_plots:
        if plot["status"] == "violation":
            num_violations = random.randint(1, 3)
            for _ in range(num_violations):
                v = {
                    "id": violation_id,
                    "plot_id": plot["id"],
                    "plot_number": plot["plot_number"],
                    "area_name": plot["area_name"],
                    "industry_name": plot["industry_name"],
                    "violation_type": random.choice(violation_types),
                    "severity": random.choice(severity_levels),
                    "confidence": round(random.uniform(0.75, 0.99), 2),
                    "detected_date": f"2026-02-{random.randint(1,13):02d}",
                    "status": random.choice(["new", "investigating", "confirmed", "resolved"]),
                    "deviation_percent": round(random.uniform(5, 35), 1),
                    "lat": plot["lat"],
                    "lng": plot["lng"],
                    "description": ""
                }
                if v["violation_type"] == "encroachment":
                    v["description"] = f"Detected boundary encroachment of {v['deviation_percent']}% beyond allotted plot area"
                elif v["violation_type"] == "unauthorized_construction":
                    v["description"] = f"New construction activity detected with {v['confidence']*100:.0f}% confidence"
                elif v["violation_type"] == "boundary_deviation":
                    v["description"] = f"Plot boundary deviates {v['deviation_percent']}% from reference map"
                elif v["violation_type"] == "vacant_unused":
                    v["description"] = "Plot marked as allotted but no construction activity detected for >6 months"
                elif v["violation_type"] == "road_encroachment":
                    v["description"] = f"Unauthorized construction detected encroaching on public road by {v['deviation_percent']}%"
                violations.append(v)
                violation_id += 1

    # Generate alerts
    alerts = []
    alert_id = 1
    for v in violations[:30]:  # Top 30 violations as alerts
        a = {
            "id": alert_id,
            "violation_id": v["id"],
            "plot_number": v["plot_number"],
            "area_name": v["area_name"],
            "violation_type": v["violation_type"],
            "severity": v["severity"],
            "confidence": v["confidence"],
            "created_at": f"2026-02-{random.randint(1,13):02d}T{random.randint(6,22):02d}:{random.randint(0,59):02d}:00",
            "status": random.choice(["unread", "read", "acknowledged", "resolved"]),
            "description": v["description"]
        }
        alerts.append(a)
        alert_id += 1

    # Generate satellite scenes
    scenes = []
    scene_id = 1
    for area in industrial_areas:
        for day_offset in range(0, 60, 5):
            dt = datetime(2026, 2, 13) - timedelta(days=day_offset)
            s = {
                "id": scene_id,
                "area_id": area["id"],
                "area_name": area["name"],
                "capture_date": dt.strftime("%Y-%m-%d"),
                "source": "Sentinel-2",
                "cloud_cover": round(random.uniform(0, 40), 1),
                "processed": day_offset > 0,
                "bands": ["B02", "B03", "B04", "B08", "B11", "B12"],
                "resolution_m": 10
            }
            scenes.append(s)
            scene_id += 1

    # Historical compliance data
    compliance_history = []
    for area in industrial_areas:
        for month_offset in range(12):
            dt = datetime(2026, 2, 1) - timedelta(days=month_offset * 30)
            rate = area["compliance_rate"] + random.uniform(-8, 5) - (month_offset * 0.3)
            rate = max(50, min(100, rate))
            compliance_history.append({
                "area_id": area["id"],
                "area_name": area["name"],
                "month": dt.strftime("%Y-%m"),
                "compliance_rate": round(rate, 1),
                "violations_detected": random.randint(2, 25),
                "violations_resolved": random.randint(1, 15),
                "scans_completed": random.randint(4, 7)
            })

    return {
        "industrial_areas": industrial_areas,
        "plots": all_plots,
        "violations": violations,
        "alerts": alerts,
        "satellite_scenes": scenes,
        "compliance_history": compliance_history
    }


# Generate demo data on startup
DEMO_DATA = generate_demo_data()


# ─── Page Routes ─────────────────────────────────────────────────────────────

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login/authentication page."""
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page."""
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/map", response_class=HTMLResponse)
async def map_view(request: Request):
    """Full map view page."""
    return templates.TemplateResponse("map.html", {"request": request})


@app.get("/alerts", response_class=HTMLResponse)
async def alerts_page(request: Request):
    """Alerts management page."""
    return templates.TemplateResponse("alerts.html", {"request": request})


@app.get("/reports", response_class=HTMLResponse)
async def reports_page(request: Request):
    """Reports page."""
    return templates.TemplateResponse("reports.html", {"request": request})


@app.get("/analytics", response_class=HTMLResponse)
async def analytics_page(request: Request):
    """Analytics & trends page."""
    return templates.TemplateResponse("analytics.html", {"request": request})


@app.get("/satellite", response_class=HTMLResponse)
async def satellite_page(request: Request):
    """Satellite imagery viewer page."""
    return templates.TemplateResponse("satellite.html", {"request": request})


# ─── API Routes ──────────────────────────────────────────────────────────────

@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """Get aggregated dashboard statistics."""
    areas = DEMO_DATA["industrial_areas"]
    violations = DEMO_DATA["violations"]
    plots = DEMO_DATA["plots"]

    total_plots = sum(a["total_plots"] for a in areas)
    total_area = sum(a["area_acres"] for a in areas)
    avg_compliance = sum(a["compliance_rate"] for a in areas) / len(areas)
    active_violations = len([v for v in violations if v["status"] != "resolved"])
    critical_violations = len([v for v in violations if v["severity"] == "critical" and v["status"] != "resolved"])

    new_alerts = len([a for a in DEMO_DATA["alerts"] if a["status"] == "unread"])

    return {
        "total_areas": len(areas),
        "total_plots": total_plots,
        "total_area_acres": total_area,
        "avg_compliance": round(avg_compliance, 1),
        "active_violations": active_violations,
        "critical_violations": critical_violations,
        "new_alerts": new_alerts,
        "last_scan": "2026-02-12",
        "scans_this_month": 47,
        "cost_savings_percent": 95,
        "areas_by_risk": {
            "high": len([a for a in areas if a["risk_level"] == "high"]),
            "medium": len([a for a in areas if a["risk_level"] == "medium"]),
            "low": len([a for a in areas if a["risk_level"] == "low"])
        },
        "violation_types": {
            "encroachment": len([v for v in violations if v["violation_type"] == "encroachment"]),
            "unauthorized_construction": len([v for v in violations if v["violation_type"] == "unauthorized_construction"]),
            "boundary_deviation": len([v for v in violations if v["violation_type"] == "boundary_deviation"]),
            "vacant_unused": len([v for v in violations if v["violation_type"] == "vacant_unused"]),
            "road_encroachment": len([v for v in violations if v["violation_type"] == "road_encroachment"])
        }
    }


@app.get("/api/areas")
async def get_areas():
    """Get all industrial areas."""
    return DEMO_DATA["industrial_areas"]


@app.get("/api/areas/{area_id}")
async def get_area(area_id: int):
    """Get specific industrial area details."""
    for area in DEMO_DATA["industrial_areas"]:
        if area["id"] == area_id:
            area_plots = [p for p in DEMO_DATA["plots"] if p["area_id"] == area_id]
            area_violations = [v for v in DEMO_DATA["violations"]
                             if any(p["id"] == v["plot_id"] for p in area_plots)]
            return {
                **area,
                "plots": area_plots,
                "violations": area_violations
            }
    return JSONResponse(status_code=404, content={"error": "Area not found"})


@app.get("/api/plots")
async def get_plots(area_id: Optional[int] = None, status: Optional[str] = None):
    """Get plots, optionally filtered."""
    plots = DEMO_DATA["plots"]
    if area_id:
        plots = [p for p in plots if p["area_id"] == area_id]
    if status:
        plots = [p for p in plots if p["status"] == status]
    return plots


@app.get("/api/violations")
async def get_violations(
    area_id: Optional[int] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50
):
    """Get violations with optional filters."""
    violations = DEMO_DATA["violations"]
    if severity:
        violations = [v for v in violations if v["severity"] == severity]
    if status:
        violations = [v for v in violations if v["status"] == status]
    if area_id:
        area_plots = [p["id"] for p in DEMO_DATA["plots"] if p["area_id"] == area_id]
        violations = [v for v in violations if v["plot_id"] in area_plots]
    return violations[:limit]


@app.get("/api/alerts")
async def get_alerts(status: Optional[str] = None, limit: int = 30):
    """Get alerts."""
    alerts = DEMO_DATA["alerts"]
    if status:
        alerts = [a for a in alerts if a["status"] == status]
    return sorted(alerts, key=lambda x: x["created_at"], reverse=True)[:limit]


@app.get("/api/satellite/scenes")
async def get_scenes(area_id: Optional[int] = None):
    """Get satellite scenes."""
    scenes = DEMO_DATA["satellite_scenes"]
    if area_id:
        scenes = [s for s in scenes if s["area_id"] == area_id]
    return scenes


@app.get("/api/compliance/history")
async def get_compliance_history(area_id: Optional[int] = None):
    """Get compliance history data."""
    history = DEMO_DATA["compliance_history"]
    if area_id:
        history = [h for h in history if h["area_id"] == area_id]
    return history


@app.get("/api/detection/run")
async def simulate_detection(area_id: int = 1):
    """Simulate an AI detection run."""
    import time
    area = None
    for a in DEMO_DATA["industrial_areas"]:
        if a["id"] == area_id:
            area = a
            break
    if not area:
        return JSONResponse(status_code=404, content={"error": "Area not found"})

    return {
        "status": "completed",
        "area": area["name"],
        "run_id": f"DR-{random.randint(10000,99999)}",
        "timestamp": datetime.now().isoformat(),
        "model_version": "v2.3.1-sentinel",
        "processing_time_seconds": round(random.uniform(45, 180), 1),
        "results": {
            "plots_analyzed": area["total_plots"],
            "encroachments_detected": random.randint(1, 5),
            "new_constructions": random.randint(0, 3),
            "boundary_changes": random.randint(0, 4),
            "vacant_plots": random.randint(2, 8),
            "confidence_avg": round(random.uniform(0.85, 0.96), 2)
        }
    }
