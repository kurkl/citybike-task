import asyncio
import logging
import dataclasses
from typing import Any

from src.schemas import BikeStationSchema, BaseBikeStationSchema
from src.requests import make_request

logger = logging.getLogger(__name__)

STATIONS_URL = "https://wegfinder.at/api/v1/stations"
NEARBY_ADDRESS_URL = "https://api.i-mobility.at/routing/api/v1/nearby_address"


def filter_data(origin_data: dict) -> dict[str, Any]:
    """
    Modify origin fetched data
    """
    origin_data["active"] = True if origin_data.pop("status") == "aktiv" else False
    origin_data["free_ratio"] = round(origin_data["free_boxes"] / origin_data["boxes"], 2)
    origin_data["coordinates"] = [origin_data.pop("latitude"), origin_data.pop("longitude")]
    del origin_data["internal_id"]

    return origin_data


async def get_stations_data() -> list[BaseBikeStationSchema]:
    """
    Fetch bike stations data from api
    :return: Bike station data as python objects
    """
    response = await make_request("get", STATIONS_URL)

    return [BaseBikeStationSchema(**filter_data(row)) for row in response]


async def set_addresses(stations: list[BaseBikeStationSchema]) -> list[BikeStationSchema]:
    """
    Get station address info from coordinates, and modify origin object
    :param stations: stations without addresses
    :return: updated stations objects
    """
    limit = asyncio.BoundedSemaphore(5)  # Do no more than 5 rps

    async def bounded_request(station: BaseBikeStationSchema) -> BikeStationSchema:
        """
        Make requests with limits to avoid 429
        """
        async with limit:
            response = await make_request(
                "GET",
                url=NEARBY_ADDRESS_URL,
                params={"latitude": station.coordinates[0], "longitude": station.coordinates[1]},
            )
            if limit.locked():
                # Concurrency limit reached, waiting...
                await asyncio.sleep(1)

            return BikeStationSchema(**dataclasses.asdict(station), address=response["data"]["name"])

    tasks = [asyncio.create_task(bounded_request(station)) for station in stations]
    updated_stations = await asyncio.gather(*tasks)

    return updated_stations
