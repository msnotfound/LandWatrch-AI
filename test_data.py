"""Quick test to verify app loads real CSIDC data."""
from app import APP_DATA

areas = APP_DATA.get("industrial_areas", [])
plots = APP_DATA.get("plots", [])
violations = APP_DATA.get("violations", [])
alerts = APP_DATA.get("alerts", [])

print(f"Industrial Areas: {len(areas)}")
print(f"Total Plots: {len(plots)}")
print(f"Violations: {len(violations)}")
print(f"Alerts: {len(alerts)}")

csidc_plots = [p for p in plots if p.get("data_source") == "CSIDC GIS"]
print(f"Real CSIDC Plots: {len(csidc_plots)}")

print("\nFirst 5 areas:")
for a in areas[:5]:
    print(f"  {a['id']:3d}. {a['name']:35s} | Center: {a['center']} | Source: {a.get('data_source', 'N/A')}")

print("\nFirst 3 CSIDC plots:")
for p in csidc_plots[:3]:
    print(f"  Plot {p['plot_number']:10s} | {p['area_name']:25s} | Status: {p.get('csidc_status', 'N/A'):12s} | UID: {p.get('uid', 'N/A')}")
