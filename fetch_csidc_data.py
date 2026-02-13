"""Fetch real CSIDC industrial area data from the GIS portal WFS service."""
import urllib.request
import ssl
import json

WMS_BASE = "https://cggis.cgstate.gov.in/giscg/wmscgcog"

def get_ssl_context():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx

def fetch_geojson(layer_name, max_features=200):
    url = (
        f"{WMS_BASE}?service=WFS&version=1.1.0"
        f"&request=GetFeature&typeName={layer_name}"
        f"&outputFormat=application/json&maxFeatures={max_features}"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    ctx = get_ssl_context()
    r = urllib.request.urlopen(req, context=ctx, timeout=60)
    return json.loads(r.read().decode("utf-8"))

def flatten_coords(coords, flat=None):
    if flat is None:
        flat = []
    if isinstance(coords[0], (int, float)):
        flat.append(coords)
    else:
        for item in coords:
            flatten_coords(item, flat)
    return flat

def get_center(coords):
    flat = flatten_coords(coords)
    lons = [p[0] for p in flat]
    lats = [p[1] for p in flat]
    return [(min(lats) + max(lats)) / 2, (min(lons) + max(lons)) / 2]

if __name__ == "__main__":
    # 1. Fetch outer boundaries
    print("=" * 60)
    print("Fetching CSIDC Industrial Area Outer Boundaries...")
    print("=" * 60)
    data = fetch_geojson("csidc_industrial_area_outer_boundary")
    features = data.get("features", [])
    print(f"Total industrial areas: {len(features)}\n")
    
    areas = []
    for f in features:
        props = f["properties"]
        geom = f["geometry"]
        center = get_center(geom["coordinates"])
        area_info = {
            "name": props.get("industrial") or "Unknown",
            "location": props.get("location") or "",
            "district": props.get("district") or "",
            "center": center,
            "gid": props.get("gid"),
            "properties": {k: v for k, v in props.items() if k not in ("geometry",)},
        }
        areas.append(area_info)
        name = (area_info['name'] or 'Unknown')[:25]
        loc = (area_info['location'] or '')[:15]
        dist = (area_info['district'] or '')[:15]
        print(f"  {name:25s} | {loc:15s} | {dist:15s} | {center}")
    
    # Save raw area boundaries data immediately
    import os
    os.makedirs("data", exist_ok=True)
    with open("data/csidc_areas.json", "w") as fp:
        json.dump(data, fp)
    print(f"\nSaved {len(features)} areas to data/csidc_areas.json")
    
    # 2. Try fetching plots
    print("\n" + "=" * 60)
    print("Fetching CSIDC Industrial Plots...")
    print("=" * 60)
    for layer in ["csidc_industrial_area_with_plots", "csidc_industrial_plots", "cg_industrial_area_with_plot_info"]:
        try:
            plots_data = fetch_geojson(layer, max_features=50)
            plot_features = plots_data.get("features", [])
            print(f"  Layer '{layer}': {len(plot_features)} features")
            if plot_features:
                first_props = plot_features[0]["properties"]
                print(f"  Properties: {list(first_props.keys())}")
                for p in plot_features[:3]:
                    print(f"    {p['properties']}")
                with open(f"data/csidc_plots_{layer}.json", "w") as fp:
                    json.dump(plots_data, fp)
                print(f"  Saved to data/csidc_plots_{layer}.json")
        except Exception as e:
            print(f"  Layer '{layer}': Error - {e}")
    
    # 3. Try fetching entities
    print("\n" + "=" * 60)
    print("Fetching CSIDC Industrial Area Entities...")
    print("=" * 60)
    try:
        entities_data = fetch_geojson("csidc_industrialareaentities", max_features=50)
        entity_features = entities_data.get("features", [])
        print(f"Total entities: {len(entity_features)}")
        if entity_features:
            print(f"Entity properties: {list(entity_features[0]['properties'].keys())}")
            for e in entity_features[:5]:
                print(f"  {e['properties']}")
            with open("data/csidc_entities.json", "w") as fp:
                json.dump(entities_data, fp)
    except Exception as e:
        print(f"Error: {e}")
    
    print("\nDone!")
