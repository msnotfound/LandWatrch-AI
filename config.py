"""Centralized configuration for LandWatch AI."""
import os
from dotenv import load_dotenv

load_dotenv()

# Sentinel Hub / Copernicus CDSE
SH_CLIENT_ID = os.getenv("SH_CLIENT_ID", "")
SH_CLIENT_SECRET = os.getenv("SH_CLIENT_SECRET", "")

# CSIDC GIS Portal
CSIDC_WMS_BASE = os.getenv("CSIDC_WMS_BASE", "https://cggis.cgstate.gov.in/giscg/wmscgcog")

# ── ALL WFS/WMS layers to fetch data from ────────────────────────────────────
# We need to pull from ALL sources — CSIDC new, CSIDC old, Directorate, LandBank

# Industrial Area BOUNDARY layers (polygons showing IA outlines)
AREA_BOUNDARY_LAYERS = {
    "csidc_current": "csidc_industrial_area_outer_boundary",     # Current CSIDC IAs (36 areas)
    "csidc_old": "csidc_old_IA",                                  # Old IAs (includes Amaseoni, Gondwara, Siltara, Urla etc.)
    "csidc_old_boundary": "csidc_old_IA_outer_b",                # Old IA outer boundaries
    "directorate": "directoindustrialarea",                       # Directorate of Industries areas
    "directorate_boundary": "directoindustrialareaouterboundary", # Directorate IA boundaries
    "ia_outer_boundary": "industrial_area_outer_boundary",        # Combined IA outer boundaries
    "ia_outer_boundary_old": "industrial_area_(outer_boundary)__OLD",  # Historical IA boundaries
}

# Plot-level layers (individual plots within IAs)
PLOT_LAYERS = {
    "csidc_plots_with_info": "csidc_industrial_area_with_plots",  # Plots with detailed info
    "cg_plot_info": "cg_industrial_area_with_plot_info",          # CG state plot info
    "cg_plot_info_sld": "cg_industrial_area_with_plot_info_sld",  # Styled plot info
    "csidc_industrial_plots": "csidc_industrial_plots",           # CSIDC individual plots
    "old_ia_plots": "old_industrial_area_plot",                   # Old IA plots
}

# Land Bank layers
LANDBANK_LAYERS = {
    "landbank_cadastrals": "csidc_landbank_cadastrals",
    "landbank_cadastrals_new": "csidc_landbank_cadastrals__new",
    "landbank_cadastral": "csidc_landbank_cadastral",
    "landbank_point": "csidc_landbank_point",
    "land_bank_villages": "csidc_land_bank_villages",
    "landbank_villages": "csidc_landbank_villages",
}

# Entity/infrastructure layers
ENTITY_LAYERS = {
    "entities": "csidc_industrialareaentities",
    "districts": "csidc_industrial_districts",
    "villages": "csidc_villages_boundary",
    "village_cadastral": "csidc_village_cadastral",
    "firestation": "csidc_firestations",
    "policestation": "csidc_policestation",
    "substations": "csidc_substations",
    "rivers": "csidc_rivers",
    "transmission_line": "csidc_transmission_line",
}

# Combined dictionary for WMS overlay display
CSIDC_LAYERS = {
    **AREA_BOUNDARY_LAYERS,
    **PLOT_LAYERS,
    **LANDBANK_LAYERS,
    **ENTITY_LAYERS,
}

# Google Earth Engine
GEE_SERVICE_ACCOUNT_KEY = os.getenv("GEE_SERVICE_ACCOUNT_KEY", "")
