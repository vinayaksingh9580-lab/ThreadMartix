import os
import ipaddress

try:
    import geoip2.database
    GEOIP_AVAILABLE = True
except ImportError:
    GEOIP_AVAILABLE = False

# Bundled offline lists for demo purposes.
# In production, these would be updated via threat feeds (e.g., Dan.me.uk for Tor)
MOCK_TOR_NODES = {'185.20.10.5', '198.51.100.22'} 
MOCK_VPN_HOSTING_RANGES = [
    ipaddress.ip_network('45.55.0.0/16'), # DigitalOcean (example)
    ipaddress.ip_network('185.20.0.0/16') # Generic sketchy VPS block (example)
]

def is_private_ip(ip_str):
    try:
        ip = ipaddress.ip_address(ip_str)
        # We consider private, loopback, and link-local as internal routing
        return ip.is_private or ip.is_loopback or ip.is_link_local
    except ValueError:
        return True # Treat invalid IPs as private/unreliable to safely skip them

def get_originating_ip(hop_path):
    """
    Finds the earliest reliable originating IP from the SMTP relay chain.
    The hop_path is ordered chronologically (hop_number 1 = oldest/first).
    We skip private IPs (10.x, 192.168.x) as they are internal network routing.
    """
    for hop in hop_path:
        ip_str = hop.get('extracted_ip')
        if ip_str and not is_private_ip(ip_str):
            return ip_str
    return None

def check_infrastructure(ip_str):
    is_tor = ip_str in MOCK_TOR_NODES
    
    is_vpn_hosting = False
    try:
        ip = ipaddress.ip_address(ip_str)
        for net in MOCK_VPN_HOSTING_RANGES:
            if ip in net:
                is_vpn_hosting = True
                break
    except ValueError:
        pass
        
    return is_tor, is_vpn_hosting

def geolocate_ip(ip_str):
    """
    Geolocates an IP using MaxMind GeoLite2.
    If the .mmdb files are missing (requires free account to download),
    we fall back to a mock dictionary specifically for our test samples
    so the hackathon demo remains functional without keys.
    """
    result = {
        "origin_ip": ip_str,
        "country": "Unknown",
        "city": "Unknown",
        "isp": "Unknown",
        "lat": 0.0,
        "lon": 0.0,
        "is_tor": False,
        "is_vpn_or_hosting": False
    }

    if not ip_str:
        return result

    # Check threat intel flags
    is_tor, is_vpn_hosting = check_infrastructure(ip_str)
    result['is_tor'] = is_tor
    result['is_vpn_or_hosting'] = is_vpn_hosting

    # 1. Try real GeoIP2 if DB exists
    city_db_path = 'data/GeoLite2-City.mmdb'
    asn_db_path = 'data/GeoLite2-ASN.mmdb'
    
    if GEOIP_AVAILABLE and os.path.exists(city_db_path):
        try:
            with geoip2.database.Reader(city_db_path) as reader:
                response = reader.city(ip_str)
                result['country'] = response.country.name or "Unknown"
                result['city'] = response.city.name or "Unknown"
                result['lat'] = response.location.latitude or 0.0
                result['lon'] = response.location.longitude or 0.0
                
            if os.path.exists(asn_db_path):
                with geoip2.database.Reader(asn_db_path) as asn_reader:
                    asn_response = asn_reader.asn(ip_str)
                    result['isp'] = asn_response.autonomous_system_organization or "Unknown"
        except Exception:
            pass # Fallback to mock on error (e.g. IP not found)
        return result

    # 2. Fallback to demo mock data if DB is absent
    mock_geo_data = {
        '192.30.252.1': { # GitHub legit
            "country": "United States", "city": "San Francisco", "isp": "GitHub, Inc.",
            "lat": 37.7749, "lon": -122.4194
        },
        '185.20.10.5': { # Phishing Tor/VPN
            "country": "Russia", "city": "Moscow", "isp": "Obscure VPS Provider LLC",
            "lat": 55.7558, "lon": 37.6173
        },
        '45.55.66.77': { # BEC lookalike
            "country": "United States", "city": "Clifton", "isp": "DigitalOcean, LLC",
            "lat": 40.8584, "lon": -74.1638
        }
    }
    
    if ip_str in mock_geo_data:
        mock_result = mock_geo_data[ip_str]
        result.update(mock_result)
        
    return result
