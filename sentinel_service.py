"""
Sentinel Hub Service — Fetches real Sentinel-2 satellite imagery 
via the Copernicus Data Space Ecosystem API.

Uses OAuth2 Client Credentials flow for authentication.
"""
import urllib.request
import urllib.parse
import ssl
import json
import os
import logging
from datetime import datetime, timedelta

from config import SH_CLIENT_ID, SH_CLIENT_SECRET

logger = logging.getLogger(__name__)

# Copernicus Data Space Ecosystem endpoints
TOKEN_URL = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
CATALOG_URL = "https://sh.dataspace.copernicus.eu/api/v1/catalog/1.0.0/search"
PROCESS_URL = "https://sh.dataspace.copernicus.eu/api/v1/process"
WMS_URL = "https://sh.dataspace.copernicus.eu/ogc/wms"

DATA_DIR = os.path.join(os.path.dirname(__file__), "data", "satellite")
os.makedirs(DATA_DIR, exist_ok=True)

_token_cache = {"token": None, "expires_at": None}


def _get_ssl_context():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def get_access_token() -> str:
    """Get OAuth2 access token from Copernicus CDSE."""
    now = datetime.now()
    
    # Return cached token if valid
    if _token_cache["token"] and _token_cache["expires_at"] and now < _token_cache["expires_at"]:
        return _token_cache["token"]
    
    if not SH_CLIENT_ID or not SH_CLIENT_SECRET:
        raise ValueError("Sentinel Hub credentials not configured. Set SH_CLIENT_ID and SH_CLIENT_SECRET in .env")
    
    data = urllib.parse.urlencode({
        "grant_type": "client_credentials",
        "client_id": SH_CLIENT_ID,
        "client_secret": SH_CLIENT_SECRET,
    }).encode("utf-8")
    
    req = urllib.request.Request(TOKEN_URL, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    
    ctx = _get_ssl_context()
    r = urllib.request.urlopen(req, context=ctx, timeout=30)
    result = json.loads(r.read().decode("utf-8"))
    
    _token_cache["token"] = result["access_token"]
    _token_cache["expires_at"] = now + timedelta(seconds=result.get("expires_in", 300) - 30)
    
    logger.info("Sentinel Hub: Got new access token")
    return _token_cache["token"]


def search_scenes(bbox: list, start_date: str = None, end_date: str = None, 
                  max_cloud: int = 30, limit: int = 10) -> list:
    """
    Search for Sentinel-2 scenes in the catalog.
    
    Args:
        bbox: [min_lon, min_lat, max_lon, max_lat]
        start_date: YYYY-MM-DD (default: 3 months ago)
        end_date: YYYY-MM-DD (default: today)
        max_cloud: Maximum cloud coverage percentage
        limit: Max number of results
    
    Returns:
        List of scene dicts with id, datetime, cloud_cover, etc.
    """
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")
    if not start_date:
        start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
    
    token = get_access_token()
    
    body = {
        "bbox": bbox,
        "datetime": f"{start_date}T00:00:00Z/{end_date}T23:59:59Z",
        "collections": ["sentinel-2-l2a"],
        "limit": limit,
        "filter": f"eo:cloud_cover < {max_cloud}",
        "filter-lang": "cql2-text",
    }
    
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(CATALOG_URL, data=data, method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    
    ctx = _get_ssl_context()
    r = urllib.request.urlopen(req, context=ctx, timeout=30)
    result = json.loads(r.read().decode("utf-8"))
    
    scenes = []
    for feature in result.get("features", []):
        props = feature.get("properties", {})
        scenes.append({
            "id": feature.get("id", ""),
            "datetime": props.get("datetime", ""),
            "cloud_cover": props.get("eo:cloud_cover", 0),
            "constellation": props.get("constellation", "sentinel-2"),
            "platform": props.get("platform", ""),
            "bbox": feature.get("bbox", []),
            "geometry": feature.get("geometry", {}),
        })
    
    logger.info(f"Sentinel Hub: Found {len(scenes)} scenes for bbox {bbox}")
    return scenes


def get_true_color_image(bbox: list, date: str, width: int = 512, height: int = 512) -> bytes:
    """
    Fetch a true-color (RGB) Sentinel-2 image using the Process API.
    
    Args:
        bbox: [min_lon, min_lat, max_lon, max_lat]
        date: YYYY-MM-DD
        width: Image width in pixels
        height: Image height in pixels
    
    Returns:
        PNG image bytes
    """
    token = get_access_token()
    
    evalscript = """
    //VERSION=3
    function setup() {
        return {
            input: [{ bands: ["B04", "B03", "B02"] }],
            output: { bands: 3, sampleType: "AUTO" }
        };
    }
    function evaluatePixel(sample) {
        return [3.5 * sample.B04, 3.5 * sample.B03, 3.5 * sample.B02];
    }
    """
    
    from_date = f"{date}T00:00:00Z"
    to_date = f"{date}T23:59:59Z"
    
    body = {
        "input": {
            "bounds": {
                "bbox": bbox,
                "properties": {"crs": "http://www.opengis.net/def/crs/EPSG/0/4326"}
            },
            "data": [{
                "type": "sentinel-2-l2a",
                "dataFilter": {
                    "timeRange": {"from": from_date, "to": to_date},
                    "maxCloudCoverage": 50
                }
            }]
        },
        "output": {
            "width": width,
            "height": height,
            "responses": [{"identifier": "default", "format": {"type": "image/png"}}]
        },
        "evalscript": evalscript
    }
    
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(PROCESS_URL, data=data, method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "image/png")
    
    ctx = _get_ssl_context()
    r = urllib.request.urlopen(req, context=ctx, timeout=60)
    image_bytes = r.read()
    
    logger.info(f"Sentinel Hub: Got {len(image_bytes)} bytes for {date} at {bbox}")
    return image_bytes


def get_ndvi_image(bbox: list, date: str, width: int = 512, height: int = 512) -> bytes:
    """
    Fetch NDVI (Normalized Difference Vegetation Index) image.
    Red = low vegetation, Green = high vegetation.
    """
    token = get_access_token()
    
    evalscript = """
    //VERSION=3
    function setup() {
        return {
            input: [{ bands: ["B04", "B08"] }],
            output: { bands: 3, sampleType: "AUTO" }
        };
    }
    function evaluatePixel(sample) {
        let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
        if (ndvi < -0.2) return [0.05, 0.05, 0.05];
        if (ndvi < 0) return [0.7, 0.2, 0.1];
        if (ndvi < 0.1) return [0.9, 0.5, 0.2];
        if (ndvi < 0.2) return [0.95, 0.8, 0.2];
        if (ndvi < 0.4) return [0.5, 0.8, 0.2];
        if (ndvi < 0.6) return [0.2, 0.7, 0.1];
        return [0.05, 0.5, 0.05];
    }
    """
    
    body = {
        "input": {
            "bounds": {
                "bbox": bbox,
                "properties": {"crs": "http://www.opengis.net/def/crs/EPSG/0/4326"}
            },
            "data": [{
                "type": "sentinel-2-l2a",
                "dataFilter": {
                    "timeRange": {
                        "from": f"{date}T00:00:00Z",
                        "to": f"{date}T23:59:59Z"
                    },
                    "maxCloudCoverage": 50
                }
            }]
        },
        "output": {
            "width": width,
            "height": height,
            "responses": [{"identifier": "default", "format": {"type": "image/png"}}]
        },
        "evalscript": evalscript
    }
    
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(PROCESS_URL, data=data, method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "image/png")
    
    ctx = _get_ssl_context()
    r = urllib.request.urlopen(req, context=ctx, timeout=60)
    return r.read()


def save_image(image_bytes: bytes, filename: str) -> str:
    """Save image bytes to the satellite data directory."""
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(image_bytes)
    return filepath
