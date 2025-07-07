import openrouteservice
from typing import Optional, List


def geocode_town(client: openrouteservice.Client,
                 town_name: str,
                 lang: str = "en") -> Optional[dict]:
    results = client.pelias_search(text=town_name, size=1, lang=lang)  # type: ignore[attr-defined]
    features = results.get("features")
    if not features:
        return None
    try:
        country = features[0]['properties']['country']
        coords = features[0]['geometry']['coordinates']
        return {"lat": coords[1], "lon": coords[0], "country": country}
    except (KeyError, IndexError):
        return None


def reverse_geocode_name(client: openrouteservice.Client, lat: float, lon: float, lang: str = "en") -> Optional[str]:
    try:
        response = client.reverse_geocode(
            coordinates=[[lon, lat]],
            size=1,
            lang=lang
        )
        features = response.get("features")
        if not features:
            return None
        props = features[0]['properties']
        place_name = props.get('locality')
        return place_name
    except Exception:
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

def get_full_route_data_by_coords(
    client: openrouteservice.Client,
    start_lat: float,
    start_lon: float,
    end_lat: float,
    end_lon: float
) -> Optional[dict]:
    try:
        route = client.directions(
            coordinates=[(start_lon, start_lat), (end_lon, end_lat)],
            profile="driving-car",
            instructions=True
        )

        route_data = route['routes'][0]
        geometry = route_data['geometry']
        decoded_coords = [
            [coord[1], coord[0]] for coord in
            openrouteservice.convert.decode_polyline(geometry)['coordinates']
        ]
        print("Decoded polyline:", decoded_coords[:5])
        steps = route_data['segments'][0]['steps']
        duration_sec = route_data['summary']['duration']
        readable_duration = (
            f"{int(duration_sec // 3600)}h {int((duration_sec % 3600) // 60)}m"
            if duration_sec else None
        )

        directions = [
            {
                "instruction": step.get("instruction"),
                "distance": step.get("distance"),
                "name": step.get("name")
            }
            for step in steps
            if step.get("instruction")
        ]

        return {
            "polyline": decoded_coords,
            "duration": readable_duration,
            "directions": directions
        }

    except (KeyError, IndexError, TypeError):
        return None