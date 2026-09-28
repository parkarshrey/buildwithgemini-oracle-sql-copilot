"""Google Maps Geocoding and Places (New) API tools."""

import os
import requests
from dotenv import load_dotenv

# Ensure local .env is loaded
load_dotenv()


def _get_api_key() -> str:
    """Retrieves the Maps API key from environment variable."""
    return os.getenv("GOOGLE_MAPS_API_KEY", "")


def geocode_address(address: str) -> dict:
    """Converts a physical address or place name into geographic coordinates (latitude, longitude).

    Args:
        address: The address or place string to geocode (e.g., '1600 Amphitheatre Pkwy, Mountain View, CA').

    Returns:
        A dictionary containing formatted_address, location (lat, lng), and status.
    """
    api_key = _get_api_key()
    if not api_key or api_key == "PASTE_KEY_HERE":
        return {
            "error": "GOOGLE_MAPS_API_KEY is not set or contains placeholder. Please set your real Maps API key in .env."
        }

    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": api_key}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "OK" or not data.get("results"):
            return {"error": f"Geocoding failed with status: {data.get('status')}"}

        first_result = data["results"][0]
        formatted_address = first_result.get("formatted_address")
        location = first_result.get("geometry", {}).get("location", {})

        return {
            "name": address,
            "address": formatted_address,
            "location": {
                "latitude": location.get("lat"),
                "longitude": location.get("lng"),
            },
            "place_id": first_result.get("place_id"),
        }
    except Exception as e:
        return {"error": f"Error calling Geocoding API: {str(e)}"}


def find_nearby_places(
    latitude: float,
    longitude: float,
    place_type: str = "restaurant",
    radius_meters: float = 1000.0,
) -> dict:
    """Finds nearby points of interest of a given type around a coordinate using Places API (New).

    Args:
        latitude: Center point latitude.
        longitude: Center point longitude.
        place_type: Type of place to search for (e.g., 'restaurant', 'cafe', 'bank', 'store').
        radius_meters: Search radius in meters (default 1000m).

    Returns:
        A dictionary with a list of nearby places including name, address, and location.
    """
    api_key = _get_api_key()
    if not api_key or api_key == "PASTE_KEY_HERE":
        return {
            "error": "GOOGLE_MAPS_API_KEY is not set or contains placeholder. Please set your real Maps API key in .env."
        }

    url = "https://places.googleapis.com/v1/places:searchNearby"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location,places.types",
    }
    body = {
        "includedTypes": [place_type],
        "locationRestriction": {
            "circle": {
                "center": {"latitude": latitude, "longitude": longitude},
                "radius": radius_meters,
            }
        },
    }

    try:
        response = requests.post(url, json=body, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        raw_places = data.get("places", [])
        if not raw_places:
            return {"places": [], "message": f"No nearby '{place_type}' places found within {radius_meters}m."}

        formatted_places = []
        for p in raw_places:
            display_name = p.get("displayName", {}).get("text", "Unknown")
            formatted_address = p.get("formattedAddress", "N/A")
            loc = p.get("location", {})
            formatted_places.append(
                {
                    "name": display_name,
                    "address": formatted_address,
                    "location": {
                        "latitude": loc.get("latitude"),
                        "longitude": loc.get("longitude"),
                    },
                    "types": p.get("types", []),
                }
            )

        return {"places": formatted_places, "count": len(formatted_places)}

    except Exception as e:
        return {"error": f"Error calling Places API (New): {str(e)}"}
