"""
CSIDC GIS Client — Fetches real industrial area data from ALL layers
of the Chhattisgarh State Industrial Development Corporation GIS portal.

Sources:
  - CSIDC Industrial Areas (current)
  - Old Industrial Areas (Amaseoni, Gondwara, Siltara, Urla, etc.)
  - Directorate Industrial Areas
  - Land Bank data
  - Infrastructure/entities

WMS/WFS Endpoint: https://cggis.cgstate.gov.in/giscg/wmscgcog
"""
import urllib.request
import ssl
import json
import os
import logging
import math
from datetime import datetime

from config import (
    CSIDC_WMS_BASE,
    AREA_BOUNDARY_LAYERS,
    PLOT_LAYERS,
    LANDBANK_LAYERS,
    ENTITY_LAYERS,
    CSIDC_LAYERS,
)

logger = logging.getLogger(__name__)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Master cache file for all merged areas
ALL_AREAS_CACHE = os.path.join(DATA_DIR, "all_industrial_areas.json")
ALL_PLOTS_CACHE = os.path.join(DATA_DIR, "all_plots.json")
ALL_LANDBANK_CACHE = os.path.join(DATA_DIR, "all_landbank.json")


def _get_ssl_context():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def fetch_wfs_geojson(layer_name: str, max_features: int = 500) -> dict:
    """Fetch GeoJSON from CSIDC WFS service."""
    url = (
        f"{CSIDC_WMS_BASE}?service=WFS&version=1.1.0"
        f"&request=GetFeature&typeName={layer_name}"
        f"&outputFormat=application/json&maxFeatures={max_features}"
        f"&srsName=EPSG:4326"
    )
    logger.info(f"Fetching WFS: {layer_name} (max={max_features})")
    req = urllib.request.Request(url, headers={"User-Agent": "LandWatchAI/2.0"})
    ctx = _get_ssl_context()
    r = urllib.request.urlopen(req, context=ctx, timeout=60)
    data = json.loads(r.read().decode("utf-8"))
    logger.info(f"  Got {len(data.get('features', []))} features from {layer_name}")
    return data


def get_wms_tile_url(layer_name: str) -> str:
    """Get WMS tile URL template for Leaflet."""
    return CSIDC_WMS_BASE


def flatten_coords(coords, flat=None):
    """Flatten nested coordinate arrays to a list of [lon, lat] pairs."""
    if flat is None:
        flat = []
    if not coords:
        return flat
    if isinstance(coords[0], (int, float)):
        flat.append(coords)
    else:
        for item in coords:
            flatten_coords(item, flat)
    return flat


def get_center(coords):
    """Calculate center point from coordinate array."""
    flat = flatten_coords(coords)
    if not flat:
        return [0, 0]
    lons = [p[0] for p in flat]
    lats = [p[1] for p in flat]
    return [(min(lats) + max(lats)) / 2, (min(lons) + max(lons)) / 2]


def get_bbox(coords):
    """Calculate bounding box [min_lon, min_lat, max_lon, max_lat]."""
    flat = flatten_coords(coords)
    if not flat:
        return [0, 0, 0, 0]
    lons = [p[0] for p in flat]
    lats = [p[1] for p in flat]
    return [min(lons), min(lats), max(lons), max(lats)]


def _extract_area_name(props: dict) -> str:
    """Extract area name from properties, trying multiple field names."""
    for field in ["industrial", "industri_1", "ia_name", "name", "industrial_area",
                   "IA_NAME", "NAME", "INDUSTRIAL", "area_name", "ia_name_en"]:
        val = props.get(field)
        if val and isinstance(val, str) and val.strip():
            return val.strip()
    return ""


def _extract_district(props: dict) -> str:
    """Extract district from properties."""
    for field in ["district", "district_i", "DISTRICT", "dist_name", "dist"]:
        val = props.get(field)
        if val and isinstance(val, str) and val.strip():
            return val.strip()
    return ""


def _extract_location(props: dict) -> str:
    """Extract location from properties."""
    for field in ["location", "LOCATION", "loc_name", "tehsil", "block"]:
        val = props.get(field)
        if val and isinstance(val, str) and val.strip():
            return val.strip()
    return ""


def _transform_point(x, y):
    """
    Convert projected coordinates (likely UTM 44N for Chhattisgarh) to Lat/Lon.
    Heuristic: if |x| > 180, treat as projected.
    """
    if abs(x) < 180 and abs(y) < 180:
        return x, y
    
    # Rough approximation for UTM 44N (Chhattisgarh)
    # Zone 44N Central Meridian = 81°E
    try:
        lat = y / 110574
        lon = 81 + (x - 500000) / (111320 * math.cos(math.radians(lat)))
        return round(lon, 7), round(lat, 7) # Return in [Lon, Lat] order for GeoJSON
    except:
        return x, y


def transform_coords(coords):
    """Recursively transform coordinates in-place if projected."""
    if not coords:
        return
    
    # Check if leaf node (point)
    if isinstance(coords[0], (int, float)):
        # It's a point [x, y]
        nx, ny = _transform_point(coords[0], coords[1])
        coords[0], coords[1] = nx, ny
        return

    # It's a list of something
    for item in coords:
        transform_coords(item)


# ─── Fetch ALL Industrial Areas ──────────────────────────────────────────────

def _fetch_areas_from_layer(layer_key: str, layer_name: str, source_label: str) -> list:
    """Fetch and parse areas from a single WFS layer."""
    cache_file = os.path.join(DATA_DIR, f"raw_{layer_key}.json")
    
    # Try cache
    data = None
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r") as f:
                data = json.load(f)
            logger.info(f"  Cache hit: {layer_key} ({len(data.get('features', []))} features)")
        except Exception:
            data = None
    
    # Fetch from WFS
    if not data:
        try:
            data = fetch_wfs_geojson(layer_name, max_features=500)
            with open(cache_file, "w") as f:
                json.dump(data, f)
        except Exception as e:
            logger.warning(f"  Failed to fetch {layer_name}: {e}")
            return []
    
    areas = []
    for feature in data.get("features", []):
        props = feature.get("properties", {})
        geom = feature.get("geometry", {})
        coords = geom.get("coordinates", [])
        
        # Check and fix projection if needed
        if coords:
            # Check first point to see if projection is needed
            flat = flatten_coords(coords)
            if flat and (abs(flat[0][0]) > 180 or abs(flat[0][1]) > 180):
                 transform_coords(coords)
        
        name = _extract_area_name(props)
        if not name:
            continue
        
        center = get_center(coords)
        bbox = get_bbox(coords)
        
        areas.append({
            "name": name,
            "location": _extract_location(props),
            "district": _extract_district(props),
            "center": center,
            "bbox": bbox,
            "boundary": coords,
            "geometry_type": geom.get("type", ""),
            "area_sqm": props.get("st_area_sh") or props.get("shape_area") or 0,
            "perimeter_m": props.get("st_length_") or props.get("shape_len") or 0,
            "source_layer": source_label,
            "layer_key": layer_key,
            "gid": props.get("gid") or props.get("objectid"),
            "raw_properties": {k: v for k, v in props.items()
                               if k not in ("geometry", "the_geom") and v is not None},
        })
    
    return areas


def load_industrial_areas(use_cache: bool = True) -> list:
    """
    Load ALL industrial areas from ALL CSIDC GIS layers.
    Merges: CSIDC current, CSIDC old, Directorate, old IA boundaries.
    Deduplicates by name (keeping the one with better data).
    """
    # Check master cache
    if use_cache and os.path.exists(ALL_AREAS_CACHE):
        try:
            with open(ALL_AREAS_CACHE, "r") as f:
                areas = json.load(f)
            logger.info(f"Loaded {len(areas)} areas from master cache (all sources)")
            return areas
        except Exception:
            pass
    
    logger.info("Fetching areas from ALL CSIDC GIS layers...")
    all_areas = []
    
    # Fetch from each boundary layer
    for key, layer_name in AREA_BOUNDARY_LAYERS.items():
        source_label = {
            "csidc_current": "CSIDC Current IA",
            "csidc_old": "CSIDC Old IA",
            "csidc_old_boundary": "CSIDC Old IA Boundary",
            "directorate": "Directorate of Industries",
            "directorate_boundary": "Directorate IA Boundary",
            "ia_outer_boundary": "IA Outer Boundary",
            "ia_outer_boundary_old": "IA Outer Boundary (Old)",
        }.get(key, key)
        
        areas = _fetch_areas_from_layer(key, layer_name, source_label)
        logger.info(f"  {key}: {len(areas)} areas")
        all_areas.extend(areas)
    
    # Deduplicate: group by normalized name
    seen = {}
    for area in all_areas:
        norm_name = area["name"].upper().strip()
        # Remove common suffixes for matching
        for suffix in [" INDUSTRIAL AREA", " IA", " PHASE", " SECTOR"]:
            if norm_name.endswith(suffix):
                norm_name = norm_name[:-len(suffix)].strip()
        
        if norm_name in seen:
            existing = seen[norm_name]
            # Keep the one with more boundary data or larger area
            existing_coord_count = len(flatten_coords(existing["boundary"]))
            new_coord_count = len(flatten_coords(area["boundary"]))
            if new_coord_count > existing_coord_count:
                # New one has more detailed boundary, merge
                area["also_in"] = existing.get("also_in", []) + [existing["source_layer"]]
                seen[norm_name] = area
            else:
                existing["also_in"] = existing.get("also_in", []) + [area["source_layer"]]
        else:
            seen[norm_name] = area
    
    merged = list(seen.values())
    
    # Sort by name
    merged.sort(key=lambda a: a["name"].upper())
    
    # Assign sequential IDs
    for i, area in enumerate(merged, 1):
        area["id"] = i
    
    logger.info(f"Total unique areas after merge: {len(merged)} (from {len(all_areas)} raw features)")
    
    # Cache merged result
    try:
        with open(ALL_AREAS_CACHE, "w") as f:
            json.dump(merged, f)
        logger.info(f"Cached {len(merged)} merged areas")
    except Exception as e:
        logger.warning(f"Failed to cache: {e}")
    
    return merged


# ─── Fetch ALL Plots ─────────────────────────────────────────────────────────

def _fetch_plots_from_layer(layer_key: str, layer_name: str) -> list:
    """Fetch and parse plots from a single WFS layer."""
    cache_file = os.path.join(DATA_DIR, f"raw_plots_{layer_key}.json")
    
    data = None
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r") as f:
                data = json.load(f)
            logger.info(f"  Plot cache hit: {layer_key} ({len(data.get('features', []))} features)")
        except Exception:
            data = None
    
    if not data:
        try:
            data = fetch_wfs_geojson(layer_name, max_features=3000)
            with open(cache_file, "w") as f:
                json.dump(data, f)
        except Exception as e:
            logger.warning(f"  Failed to fetch plots from {layer_name}: {e}")
            return []
    
    plots = []
    for feature in data.get("features", []):
        props = feature.get("properties", {})
        geom = feature.get("geometry", {})
        coords = geom.get("coordinates", [])
        center = get_center(coords) if coords else [0, 0]
        
        # Try multiple field names for plot number
        plot_no = ""
        for field in ["plotno_inf", "PLOT_NO", "plot_no", "plotno", "PLOTNO", "plot_numb", "plot_id"]:
            val = props.get(field)
            if val:
                plot_no = str(val).strip()
                break
        
        # Area name
        area_name = _extract_area_name(props)
        
        # Status
        status = ""
        for field in ["status_from_csidc", "status_inf", "status", "STATUS", "plotstatus"]:
            val = props.get(field)
            if val and isinstance(val, str):
                status = val.strip()
                break
        
        # Label/industry name
        label = ""
        for field in ["label", "LABEL", "industry_name", "occupant", "lessee", "allottee_n",
                       "allottee_name", "allottee", "plot_label"]:
            val = props.get(field)
            if val and isinstance(val, str):
                label = val.strip()
                break
        
        plots.append({
            "plot_no": plot_no,
            "area_name": area_name,
            "label": label,
            "district": _extract_district(props),
            "status": status,
            "category": props.get("category_i") or props.get("LABEL") or "",
            "total_area_sqm": props.get("total_area") or props.get("shape_area") or 0,
            "premium_base": props.get("premium_ba") or 0,
            "premium_total": props.get("total_prem") or 0,
            "uid": props.get("uid") or props.get("uidv1") or "",
            "plotactiva": props.get("plotactiva") or "",
            "center": center,
            "boundary": coords,
            "geometry_type": geom.get("type", ""),
            "source_layer": layer_key,
            "gid": props.get("gid") or props.get("objectid"),
        })
    
    return plots


def load_plots(area_name: str = None, use_cache: bool = True) -> list:
    """
    Load ALL plots from ALL CSIDC GIS plot layers.
    Merges: csidc_plots_with_info, cg_plot_info, csidc_industrial_plots, old_ia_plots.
    """
    if use_cache and os.path.exists(ALL_PLOTS_CACHE):
        try:
            with open(ALL_PLOTS_CACHE, "r") as f:
                plots = json.load(f)
            logger.info(f"Loaded {len(plots)} plots from master cache (all sources)")
            if area_name:
                plots = [p for p in plots if area_name.upper() in (p.get("area_name", "") or "").upper()]
            return plots
        except Exception:
            pass
    
    logger.info("Fetching plots from ALL CSIDC GIS layers...")
    all_plots = []
    
    for key, layer_name in PLOT_LAYERS.items():
        plots = _fetch_plots_from_layer(key, layer_name)
        logger.info(f"  {key}: {len(plots)} plots")
        all_plots.extend(plots)
    
    logger.info(f"Total plots from all layers: {len(all_plots)}")
    
    # Cache
    try:
        with open(ALL_PLOTS_CACHE, "w") as f:
            json.dump(all_plots, f)
    except Exception as e:
        logger.warning(f"Failed to cache plots: {e}")
    
    if area_name:
        all_plots = [p for p in all_plots if area_name.upper() in (p.get("area_name", "") or "").upper()]
    
    return all_plots


# ─── Fetch Land Bank Data ───────────────────────────────────────────────────

def load_landbank(use_cache: bool = True) -> list:
    """Load all land bank data from CSIDC GIS layers."""
    if use_cache and os.path.exists(ALL_LANDBANK_CACHE):
        try:
            with open(ALL_LANDBANK_CACHE, "r") as f:
                data = json.load(f)
            logger.info(f"Loaded {len(data)} landbank features from cache")
            return data
        except Exception:
            pass
    
    logger.info("Fetching land bank data from all layers...")
    all_landbank = []
    
    for key, layer_name in LANDBANK_LAYERS.items():
        cache_file = os.path.join(DATA_DIR, f"raw_landbank_{key}.json")
        
        data = None
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r") as f:
                    data = json.load(f)
            except Exception:
                pass
        
        if not data:
            try:
                data = fetch_wfs_geojson(layer_name, max_features=1000)
                with open(cache_file, "w") as f:
                    json.dump(data, f)
            except Exception as e:
                logger.warning(f"  Failed to fetch landbank {layer_name}: {e}")
                continue
        
        for feature in data.get("features", []):
            props = feature.get("properties", {})
            geom = feature.get("geometry", {})
            coords = geom.get("coordinates", [])
            center = get_center(coords) if coords else [0, 0]
            
            all_landbank.append({
                "name": _extract_area_name(props) or props.get("village") or props.get("khasra_no") or "",
                "district": _extract_district(props),
                "area_sqm": props.get("area") or props.get("total_area") or props.get("shape_area") or 0,
                "center": center,
                "boundary": coords,
                "geometry_type": geom.get("type", ""),
                "source_layer": key,
                "raw_properties": {k: v for k, v in props.items() if v is not None},
            })
        
        logger.info(f"  {key}: {len(data.get('features', []))} features")
    
    try:
        with open(ALL_LANDBANK_CACHE, "w") as f:
            json.dump(all_landbank, f)
    except Exception:
        pass
    
    return all_landbank


# ─── Sync Everything ─────────────────────────────────────────────────────────

def sync_all_data() -> dict:
    """Force re-fetch ALL data from ALL CSIDC GIS portal layers."""
    results = {"synced_at": datetime.now().isoformat()}
    
    # Remove master caches to force re-fetch
    for cache_file in [ALL_AREAS_CACHE, ALL_PLOTS_CACHE, ALL_LANDBANK_CACHE]:
        if os.path.exists(cache_file):
            os.remove(cache_file)
    
    # Remove raw caches too
    for fname in os.listdir(DATA_DIR):
        if fname.startswith("raw_"):
            os.remove(os.path.join(DATA_DIR, fname))
    
    # Re-fetch everything
    try:
        areas = load_industrial_areas(use_cache=False)
        results["areas"] = len(areas)
        results["area_sources"] = list(set(a.get("source_layer", "") for a in areas))
    except Exception as e:
        results["areas_error"] = str(e)
    
    try:
        plots = load_plots(use_cache=False)
        results["plots"] = len(plots)
        results["plot_sources"] = list(set(p.get("source_layer", "") for p in plots))
    except Exception as e:
        results["plots_error"] = str(e)
    
    try:
        landbank = load_landbank(use_cache=False)
        results["landbank"] = len(landbank)
    except Exception as e:
        results["landbank_error"] = str(e)
    
    # Sync entities
    for key, layer_name in ENTITY_LAYERS.items():
        try:
            data = fetch_wfs_geojson(layer_name, max_features=2000)
            with open(os.path.join(DATA_DIR, f"raw_entity_{key}.json"), "w") as f:
                json.dump(data, f)
            results[f"entity_{key}"] = len(data.get("features", []))
        except Exception as e:
            results[f"entity_{key}_error"] = str(e)
    
    return results
