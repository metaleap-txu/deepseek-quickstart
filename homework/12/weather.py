from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize the FastMCP server with the name "weather"
mcp = FastMCP("weather")

# Base URL for the National Weather Service (NWS) API
NWS_API_BASE = "https://api.weather.gov"

# User agent string for HTTP requests to the NWS API
USERT_AGENT = "weather-app/1.0"


@mcp.tool()
async def get_alerts(state: str) -> str:
    """
    Fetch weather alerts for a given state from the National Weather Service API.

    Args:
        state (str): The two-letter state abbreviation (e.g., 'CA' for California).

    Returns:
        str: A string containing the weather alerts for the specified state.
    """
    url = f"{NWS_API_BASE}/alerts/active?area={state}"
    data = await make_nws_request(url)

    if not data or "features" not in data:
        return "Unable to retrieve alerts or no alerts found."

    if not data["features"]:
        return "No active alerts found."

    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)

@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """
    Fetch the weather forecast for a given latitude and longitude from the National Weather Service API.

    Args:
        latitude (float): The latitude of the location.
        longitude (float): The longitude of the location.

    Returns:
        str: A string containing the weather forecast for the specified location.
    """
    # Construct the URL for the points endpoint using latitude and longitude
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)

    if not points_data or "properties" not in points_data:
        return "Unable to retrieve forecast data for the specified location."

    # Extract the forecast URL from the points data
    forecast_url = points_data["properties"].get("forecast")
    forecast_data = await make_nws_request(forecast_url)

    if not forecast_data or "properties" not in forecast_data:
        return "Unable to retrieve forecast data."

    # Extract the periods from the forecast data
    periods = forecast_data["properties"].get("periods", [])
    forecast = []
    for period in periods[:5]:
        forecast_text = f"""
{period['name']}:
Temperature: {period['temperature']}°{period['temperatureUnit']}
Wind: {period['windSpeed']} {period['windDirection']}
Forecast: {period['shortForecast']}
"""
        forecast.append(forecast_text)
    return "\n---\n".join(forecast)

async def make_nws_request(url: str) -> Any:
    """
    Make an HTTP GET request to the National Weather Service API.

    Args:
        url (str): The URL to make the request to.

    Returns:
        Any: The JSON response from the API, or None if the request fails.
    """
    headers = {
        "User-Agent": USERT_AGENT,
        "Accept": "application/geo+json"
    }
    # Use an asynchronous HTTP client to make the request
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=10.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e}")
        except httpx.RequestError as e:
            print(f"Request error occurred: {e}")
    return None


def format_alert(feature: dict) -> str:
    """
    Format a weather alert feature into a readable string.

    Args:
        feature (dict): A dictionary containing the alert feature data.

    Returns:
        str: A formatted string representing the alert.
    """
    properties = feature.get("properties", {})
    return f"""
Event: {properties.get('event', 'Unknown')}
Area: {properties.get('areaDesc', 'Unknown')}
Severity: {properties.get('severity', 'Unknown')}
Description: {properties.get('description', 'No description available')}
Instructions: {properties.get('instruction', 'No instructions available')}
"""


if __name__ == "__main__":
    # Start the FastMCP server
    mcp.run(transport="stdio")
