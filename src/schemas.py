from dataclasses import dataclass


@dataclass(kw_only=True)
class BaseBikeStationSchema:
    id: int
    name: str
    active: bool
    description: str
    boxes: int
    free_boxes: int
    free_bikes: int
    free_ratio: float
    coordinates: list[float]


@dataclass(kw_only=True)
class BikeStationSchema(BaseBikeStationSchema):
    address: str
