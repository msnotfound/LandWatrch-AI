"""Search ALL CSIDC layers for Amaseoni and Gondwara industrial areas."""
import urllib.request
import ssl
import json

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

BASE = "https://cggis.cgstate.gov.in/giscg/wmscgcog"

layers_to_search = [
    "csidc_old_IA",
    "csidc_old_IA_outer_b",
    "directoindustrialarea",
    "directoindustrialareaouterboundary",
    "industrial_area_outer_boundary",
    "industrial_area_(outer_boundary)__OLD",
    "old_industrial_area_plot",
    "csidc_industrial_plots",
    "csidc_industrialareaentities",
]

for layer in layers_to_search:
    url = f"{BASE}?service=WFS&version=1.1.0&request=GetFeature&typeName={layer}&outputFormat=application/json&maxFeatures=300"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        r = urllib.request.urlopen(req, context=ctx, timeout=30)
        data = json.loads(r.read())
        features = data.get("features", [])
        print(f"\n=== {layer}: {len(features)} features ===")
        
        for f in features:
            p = f.get("properties", {})
            # Search all string values for amaseoni/gondwara
            text = json.dumps(p).upper()
            if "AMAS" in text or "GOND" in text or "SILTARA" in text or "URLA" in text:
                name_fields = [v for k, v in p.items() if isinstance(v, str) and v.strip()]
                print(f"  FOUND: {name_fields[:3]}")
                # Get coordinates
                geom = f.get("geometry", {})
                coords = geom.get("coordinates", [])
                if coords:
                    # Get first coord
                    flat = coords
                    while isinstance(flat, list) and isinstance(flat[0], list):
                        flat = flat[0]
                    print(f"    Coords: [{flat[0]:.6f}, {flat[1]:.6f}]")
    except Exception as e:
        print(f"\n=== {layer}: ERROR - {e} ===")

# Also search the main boundary layer with all properties
print("\n\n=== Searching main boundary layer for ALL names ===")
url = f"{BASE}?service=WFS&version=1.1.0&request=GetFeature&typeName=csidc_industrial_area_outer_boundary&outputFormat=application/json&maxFeatures=200"
try:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    r = urllib.request.urlopen(req, context=ctx, timeout=30)
    data = json.loads(r.read())
    for f in data.get("features", []):
        p = f.get("properties", {})
        name = p.get("industrial", "Unknown")
        text = json.dumps(p).upper()
        has_match = any(k in text for k in ["AMAS", "GOND", "SILTARA", "URLA", "BHANPURI"])
        marker = " <<< MATCH" if has_match else ""
        print(f"  {name}{marker}")
except Exception as e:
    print(f"  ERROR: {e}")
