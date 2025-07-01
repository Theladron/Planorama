import openrouteservice
from typing import Optional, List


def geocode_town(client: openrouteservice.Client, town_name: str) -> Optional[dict]:
    results = client.pelias_search(text=town_name, size=1)  # type: ignore[attr-defined]
    features = results.get("features")
    if not features:
        return None
    try:
        country = features[0]['properties']['country']
        coords = features[0]['geometry']['coordinates']
        return {"lat": coords[1], "lon": coords[0], "country": country}
    except (KeyError, IndexError):
        return None


def get_route_directions(
    client: openrouteservice.Client, start_town: str, end_town: str
) -> Optional[tuple[list[str], str]]:
    start_loc = geocode_town(client, start_town)
    end_loc = geocode_town(client, end_town)
    if not start_loc or not end_loc:
        return None

    try:
        route = client.directions(  # type: ignore[attr-defined]
            coordinates=[(start_loc["lon"], start_loc["lat"]), (end_loc["lon"], end_loc["lat"])],
            profile='driving-car',
            instructions=True
        )

        steps = route['routes'][0]['segments'][0]['steps']
        duration_sec = route['routes'][0]['summary']['duration']

        if not steps or duration_sec is None:
            return None

        # Convert duration (in seconds) to "Xh Ym"
        hours = int(duration_sec // 3600)
        minutes = int((duration_sec % 3600) // 60)
        readable_duration = f"{hours}h {minutes}m" if hours else f"{minutes}m"

        directions_list = [step.get('instruction') for step in steps if step.get('instruction')]
        return (directions_list, readable_duration) if directions_list else None

    except (KeyError, IndexError):
        return None
