import geoip2.database
from fastapi import Request

# открыть БД один раз при старте приложения
GEOIP_READER = geoip2.database.Reader("src/services/GeoLite2-City.mmdb")

def get_geo_by_ip(ip: str) -> dict | None:
    try:
        resp = GEOIP_READER.city(ip)
    except Exception:
        return None

    return {
        "country": resp.country.name,
        "city": resp.city.name
    }


def get_client_ip(request: Request) -> str:
    xff = request.headers.get("X-Forwarded-For")
    if xff:
        return xff.split(",")[0].strip()
    return request.client.host


def get_device_type(request: Request) -> str:
    ua = request.headers.get("user-agent", "").lower()
    if not ua:
        return "Unknown"

    mobile_markers = ["android", "iphone", "ipod", "windows phone", "mobile"]
    tablet_markers = ["ipad", "tablet"]

    if any(m in ua for m in tablet_markers):
        return "Tablet" 

    if any(m in ua for m in mobile_markers):
        return "Mobile"

    return "Desktop"
