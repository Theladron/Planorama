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
) -> Optional[List[str]]:
    start_loc = geocode_town(client, start_town)
    end_loc = geocode_town(client, end_town)
    if not start_loc or not end_loc:
        return None

    route = client.directions(  # type: ignore[attr-defined]
        coordinates=[(start_loc["lon"], start_loc["lat"]), (end_loc["lon"], end_loc["lat"])],
        profile='driving-car',
        instructions=True
    )

    try:
        steps = route['routes'][0]['segments'][0]['steps']
        if not steps:
            return None

        directions_list = [step.get('instruction') for step in steps if step.get('instruction')]
        return directions_list if directions_list else None

    except (KeyError, IndexError):
        return None
