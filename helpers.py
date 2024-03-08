import json
from dataclasses import asdict
from typing import Dict, List

import requests

from config import settings
from log import logger
from models import (
    ConnectedApp,
    Environment,
    Organization,
    Token,
)


def get_environments(
    token: Token,
    organizations: List[str],
) -> List[Organization]:

    results = []
    for org in organizations:

        url = f"{settings.ANYPOINT_URL}{settings.ANYPOINT_ENVIRONMENTS_API}"
        url = url.replace("orgId", org)

        params = {
            "limit": 500,
            "offset": 0,
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token.access_token}",
        }

        logger.info(f"Getting all environments from the Anypoint Platform at {url}...")
        logger.debug(
            f"\n==\nAnypoint Get Environments parameters: \n\t--> URL: {url} \n\t--> Headers: {headers}\n==\n"
        )

        r = requests.get(url=url, params=params, headers=headers)
        environments = r.json()["data"]
        logger.info(f"Successfully obtained {len(environments)} environments")
        logger.debug(f"\n==\nAnypoint Environments \n\t--> {environments}\n==\n")

        envs = []
        for environment in environments:
            envs.append(
                Environment(
                    id=environment["id"],
                    name=environment["name"],
                    client_id=environment["clientId"],
                    is_production=environment["isProduction"],
                    type=environment["type"],
                    org_id=environment["organizationId"],
                )
            )

        results.append(Organization(org_id=org, environments=envs))

        logger.debug(f"\n==\nAnypoint Get Lisf of Environments: \n\t-->{results}\n==\n")

    return results


def load_scopes(filename: str = settings.SCOPES_SAMPLE_FILE) -> List[str]:
    logger.info(f"Loading scopes from file {filename}...")

    scopes_file = open(settings.DATAFILE_DIRECTORY + "/" + filename, "r")
    config = json.load(scopes_file)
    scopes_file.close()

    scopes = []
    org_only = []
    env_only = []
    no_context = []
    for scope in config["data"]:

        logger.debug(f"\n==\nScope \n\t--> name: {scope}")

        context_params = scope.get("context_params", {})
        org_present = "org" in context_params
        env_present = "envId" in context_params

        name = scope.get("scope", None)

        if name is None:
            logger.warning(f"Scope {scope} does not have a name")
            continue
        else:
            scopes.append(name)

            if org_present and env_present:
                logger.debug(f"Scope {scope} has both 'org' and 'envId'")
            elif org_present:
                org_only.append(name)
            elif env_present:
                env_only.append(name)
            else:
                no_context.append(name)

    logger.debug(
        f"Final results: \n\t--> scopes: {scopes}\n\t--> env_only: {env_only}\n\t--> org_only: {org_only}\n\t--> no_context: {no_context}\n==\n"
    )

    return scopes, org_only, env_only, no_context


def prepare_connected_app_payload(
    scopes: List[str], client_name: str = settings.NONAME_CLIENT_NAME
) -> ConnectedApp:
    logger.info("Preparing the Connected App payload...")

    payload = ConnectedApp(
        client_name=client_name,
        public_keys=[],
        redirect_uris=[],
        grant_types=["client_credentials"],
        scopes=scopes,
        enabled=True,
        audience="internal",
        generate_iss_claim_without_token=True,
    )

    logger.debug(f"\n==\nAnypoint Create App Payload: \n\t-->{payload}\n==\n")

    return payload


def prepare_scope_authorizations_payload(
    scopes: List[str],
    org_only: List[str],
    no_context: List[str],
    organizations: List[Organization],
) -> Dict[str, List[Dict[str, str]]]:
    logger.info("Authorizing scopes for the environments...")

    payload = {}
    total_scopes = len(scopes)
    total_orgs = len(organizations)

    logger.debug(
        f"\n==\nAuthZ Stats: \nOrganizations\t\t-->{total_orgs} \nScopes\t\t-->{total_scopes}\n==\n"
    )

    # Loop through each environment and create a list of scopes to authorize
    o: int = 0
    for organization in organizations:
        o += 1
        total_envs = len(organization.environments)
        logger.debug(f"[{o}/{total_orgs}] O:[{organization.org_id}]\n")
        e: int = 0
        entries = []
        for environment in organization.environments:
            e += 1
            logger.debug(
                f"--> [{o}/{total_orgs}] O:[{organization.org_id}] \n\t--> [{e}/{total_envs}] E:[{environment.id}]"
            )
            s: int = 0
            for scope in scopes:
                data = {}
                s += 1
                logger.debug(f"\t\t--> [{s}/{total_scopes}] S:[{scope}] ")
                if scope in no_context:
                    data = {"scope": scope, "context_params": {}}

                elif scope in org_only:
                    data = {
                        "scope": scope,
                        "context_params": {
                            "org": organization.org_id,
                        },
                    }
                else:
                    data = {
                        "scope": scope,
                        "context_params": {
                            "org": organization.org_id,
                            "envId": environment.id,
                        },
                    }

                entries.append(data)
            logger.debug(
                f"\n[{o}/{total_orgs}] Org [{organization.org_id}] - [{e}/{total_envs}] E:[{environment.id}] DONE"
            )
            # Save the payload for the org
            payload[organization.org_id] = entries
            logger.debug(
                f"[{o}/{total_orgs}] Org [{organization.org_id}] payload: {payload[organization.org_id]} DONE"
            )
            logger.debug(f"Processing next organization [{o+1}]")
        logger.debug(
            f"[{e}/{total_envs}] Envs - [{o}/{total_orgs}] Org [{organization.org_id}] processed"
        )
        logger.debug(f"Partial payload: \n{payload}\n")
    logger.debug(f"{o} Organizations {organization.org_id} processed")

    logger.debug(f"\n==\nFinal payload: \n\t--> {payload}\n==")

    output_file = open(settings.OUTPUT_DIRECTORY + "/authz_payload.json", "w")
    output_file.write(json.dumps(payload, indent=4))

    return payload


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


def authorize_connected_app(token: Token, data: dict, app_id: str) -> None:

    for org_id in data.keys():
        url = f"{settings.ANYPOINT_URL}{settings.ANYPOINT_AUTHORIZE_SCOPES_API}"
        url = url.replace("orgId", org_id)
        url = url.replace("clientId", app_id)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token.access_token}",
        }

        payload = {
            "scopes": data[org_id],
        }

        output_file = open(settings.OUTPUT_DIRECTORY + f"/authz_{org_id}.json", "w")
        output_file.write(json.dumps(payload, indent=4))
        # with open(f"authz_{org_id}.json", "w") as f:
        #     # Write data to the file
        #     f.write(json.dumps(payload, indent=4))

        logger.debug(
            f"\n==\nAuthorizing the new Connected App with the parameters: \n\t--> URL: {url} \n\t--> Headers: {headers}\n\t--> Payload: {payload}\n==\n"
        )

        r = requests.put(url=url, headers=headers, data=json.dumps(payload))

        if r.status_code != 204:
            logger.warning(f"Failed to autorize the new noname client: {r.status_code}")
        else:
            logger.info("Noname Connected App successfully authorized!")


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

        output_file = open(settings.OUTPUT_DIRECTORY + "/list_of_apps.json", "w")
        output_file.write(json.dumps(r.json(), indent=4))

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
