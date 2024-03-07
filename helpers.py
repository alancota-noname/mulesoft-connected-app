import json
import os
from dataclasses import asdict, dataclass
from typing import List

import requests

from config import settings
from log import logger


@dataclass
class AnypointBasicCredentials:
    username: str
    password: str


@dataclass
class ConnectedApp:
    client_name: str
    scopes: List[str]
    enabled: bool
    audience: str
    public_keys: List[str]
    redirect_uris: List[str]
    grant_types: List[str]
    generate_iss_claim_without_token: bool


@dataclass
class Token:
    access_token: str


# @dataclass
# class AnypointClient:
#     credentials: AnypointBasicCredentials
#     client_name: str
#     scopes: List[str]
#     url: str
#     access_token: str | None


def load_scopes(filename: str = settings.SCOPES_SAMPLE_FILE) -> List[str]:
    logger.info(f"Loading scopes from file {filename}...")
    with open(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), filename),
        "r",
    ) as f:
        config = json.load(f)

    scopes = []
    for scope in config["data"]:
        scopes.append(scope["scope"])

    return scopes


def authenticate(username: str, password: str) -> Token:
    payload = {
        "username": username,
        "password": password,
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    url = f"{settings.ANYPOINT_URL}{settings.ANYPOINT_AUTH_API}"

    logger.info(f"Authenticating with your Anypoint Platform at {url}...")

    logger.debug(
        f"\n==\nAnypoint Login parameters: \n\t--> URL: {url} \n\t--> Headers: {headers} \n\t--> Payload: {payload}\n==\n"
    )

    r = requests.post(url=url, headers=headers, data=payload)
    token = Token(access_token=r.json()["access_token"])
    logger.info("Successfully obtained Access Token")

    return token


def create_connected_app(token: Token, payload: ConnectedApp) -> dict:
    logger.info(f"Creating a new Connected App with the name {payload.client_name}...")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token.access_token}",
    }

    url = f"{settings.ANYPOINT_URL}{settings.ANYPOINT_ACCOUNTS_API}"

    json_payload = json.dumps(asdict(payload))

    logger.debug(
        f"\n==\nCreating a new Noname Connected App with the parameters: \n\t--> URL: {url} \n\t--> Headers: {headers} \n\t--> Payload: {json_payload}\n==\n"
    )

    r = requests.post(url=url, headers=headers, data=json_payload)

    if r.status_code != 201:
        raise Exception(f"Failed to create a new noname client: {r.status_code}")
    else:
        logger.info("Noname Connected App successfully created")
        logger.debug(
            f"\n==\nNew Connected App: \n{json.dumps(r.json(), indent=4)}\n==\n"
        )
        return r.json()


def get_all_connected_apps(access_token: str) -> List[dict]:
    logger.info("Fetching a list of all the Connected Apps")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }

    params = {
        "limit": 500,
        "offset": 0,
    }

    url = f"{settings.ANYPOINT_URL}{settings.ANYPOINT_ACCOUNTS_API}"

    logger.debug(
        f"\n==\nGetting a list of all Connected App with the parameters: \n\t--> URL: {url} \n\t--> Params: {params} \n\t--> Headers: {headers}\n==\n"
    )

    r = requests.get(url=url, headers=headers, params=params)

    if r.status_code != 200:
        logger.info(f"Failed to get a list of all connected apps: {r.status_code}")
    else:
        logger.info("List of connected apps successfully retrieved")
        logger.debug(f"\n==\nConnected Apps: \n{json.dumps(r.json(), indent=4)}\n==\n")

        with open("list_of_apps.json", "w") as f:
            # Write data to the file
            f.write(json.dumps(r.json(), indent=4))

        return r.json()["data"]


def delete_all_connected_apps(
    connected_apps: List[dict],
    token: Token,
) -> None:

    total_apps = len(connected_apps)
    total_deleted = 0

    logger.info(f"Deleting [{total_apps}] Connected Apps\n\n")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token.access_token}",
    }

    url = f"{settings.ANYPOINT_URL}{settings.ANYPOINT_ACCOUNTS_API}"

    status = []

    for connected_app in connected_apps:

        client_id = connected_app["client_id"]

        logger.info(
            f"Deleting connected app {client_id} - [{total_deleted+1}/{total_apps}]"
        )
        r = requests.delete(url=f"{url}/{client_id}", headers=headers)
        if r.status_code == 204:
            total_deleted += 1
            status.append({client_id, "deleted"})

    logger.info("\n==\n\nFinal results: \n")

    for id, status in status:
        logger.info(f"{id} -> {status}")

    logger.info("\n==\n")
