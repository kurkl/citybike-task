import re
import json
import asyncio
import logging
import argparse
import dataclasses

from src.citybyke_client import set_addresses, get_stations_data

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


def save_to_json_file(filename: str, data: list) -> None:
    with open(f"{filename}.json", "w") as file:
        dict_data = list(map(dataclasses.asdict, data))
        file.write(json.dumps(dict_data, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", type=str, help="Filename to save results")
    args = parser.parse_args()
    file_path = args.f

    base_stations_data = asyncio.run(get_stations_data())
    filtered_data = list(filter(lambda x: x.free_bikes > 0, base_stations_data))
    sorted_by_free_bikes = sorted(filtered_data, key=lambda x: x.free_bikes, reverse=True)
    sorted_by_names = sorted(sorted_by_free_bikes, key=lambda x: x.name)
    updated_stations_data = asyncio.run(set_addresses(sorted_by_names))

    if file_path:
        file_path = re.sub(r"(?u)[^-\w]", "", file_path)
        print(f"Saving results to '{file_path}_.json'")
        save_to_json_file(f"{file_path}_base", base_stations_data)
        save_to_json_file(f"{file_path}_updated", updated_stations_data)

    else:
        print(*map(dataclasses.asdict, base_stations_data))
        print()
        print(*map(dataclasses.asdict, updated_stations_data))
