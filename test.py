import openrouteservice
import json
from typing import Optional, List


def geocode_town(client: openrouteservice.Client, town_name: str) -> Optional[dict]:
    results = client.pelias_search(text=town_name, size=1)  # type: ignore[attr-defined]
    features = results.get("features")
    if not features:
        return None
    country = features[0]['properties']['country']
    coords = features[0]['geometry']['coordinates']
    return {"lat": coords[1], "lon": coords[0], "country": country}


geocode_town(openrouteservice.Client(key="5b3ce3597851110001cf62484ec0c938eea74fbe9d716b3692d3211b"), "Lisbon")