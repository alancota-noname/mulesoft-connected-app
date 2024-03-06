import json
import logging
import os
from dataclasses import asdict, dataclass
from typing import List

import requests
from pyfiglet import Figlet

from config import settings
from log import config_logger

scopes = []
figlet = Figlet(font="smslant")

log_level = logging.DEBUG if settings.DEBUG else logging.INFO
logger = config_logger(log_level)


@dataclass
class AnypointBasicCredentials:
	username: str
	password: str


@dataclass
class ConnectedAppCreationPayload:
	client_name: str
	scopes: List[str]
	enabled: bool
	audience: str
	public_keys: List[str]
	redirect_uris: List[str]
	grant_types: List[str]
	generate_iss_claim_without_token: bool


# TODO: Add support for client_credentials authentication
@dataclass
class AnypointClient:
	credentials: AnypointBasicCredentials
	client_name: str
	scopes: List[str] | None = None
	access_token: str | None = None
	url: str | None = settings.ANYPOINT_URL

	def load_scopes(self) -> None:
		logger.info(f"Loading scopes from file {settings.SCOPES_SAMPLE_FILE}...")
		with open(
			os.path.join(
				os.path.dirname(os.path.realpath(__file__)), settings.SCOPES_SAMPLE_FILE
			),
			"r",
		) as f:
			config = json.load(f)

		for scope in config["data"]:
			scopes.append(scope["scope"])

		self.scopes = scopes

	def authenticate(self) -> None:
		payload = {
			"username": self.credentials.username,
			"password": self.credentials.password,
		}

		headers = {"Content-Type": "application/x-www-form-urlencoded"}

		url = f"{self.url}{settings.ANYPOINT_AUTH_API}"

		logger.info(f"Authenticating with your Anypoint Platform at {url}...")

		logger.debug(f"\n==\nAnypoint Login parameters: \n\t--> URL: {url} \n\t--> Headers: {headers} \n\t--> Payload: {payload}\n==\n")

		r = requests.post(url=url, headers=headers, data=payload)
		self.access_token = r.json()["access_token"]
		logger.info("Successfully obtained Access Token")

	def create_noname_client(self):
		logger.info(f"Creating a new Connected App with the name {self.client_name}...")
		payload = ConnectedAppCreationPayload(
			client_name=self.client_name,
			public_keys=[],
			redirect_uris=[],
			grant_types=["client_credentials"],
			scopes=self.scopes,
			enabled=True,
			audience="internal",
			generate_iss_claim_without_token=True,
		)

		headers = {
			"Content-Type": "application/json",
			"Authorization": f"Bearer {self.access_token}",
		}

		url = f"{self.url}{settings.ANYPOINT_ACCOUNTS_API}"
		json_payload = json.dumps(asdict(payload))

		logger.debug(f"\n==\nCreating a new Noname Connected App with the parameters: \n\t--> URL: {url} \n\t--> Headers: {headers} \n\t--> Payload: {json_payload}\n==\n")

		r = requests.post(url=url, headers=headers, data=json_payload)

		if r.status_code != 201:
			raise Exception(f"Failed to create a new noname client: {r.status_code}")
		else:
			logger.info("Noname Connected App successfully created")
			logger.debug(f"\n==\nNew Connected App: \n{json.dumps(r.json(), indent=4)}\n==\n")
			return r.json()


def print_banner(text: str):
	logger.info(figlet.renderText(text))


def main():
	print_banner("Noname SA Tools")
	credentials = AnypointBasicCredentials(
		username=settings.ANYPOINT_USERNAME, password=settings.ANYPOINT_PASSWORD
	)

	if credentials.username:
		anypoint = AnypointClient(
			credentials=credentials,
			client_name=settings.NONAME_CLIENT_NAME,
		)
		anypoint.authenticate()
		anypoint.load_scopes()

		if settings.CREATE:
			new_client = anypoint.create_noname_client()
			logger.info(
				f"\n\nCopy the following information and use it when configuring the interation in your Noname Platform.\nNoname Connected App Credentials:\n\n client_name: {new_client['client_name']}\n client_id: {new_client['client_id']}\n client_secret: {new_client['client_secret']}"
			)
		else:
			logger.info("The Connected App creation is disabled")
	else:
		logger.error("No credentials provided. Please edit the .env file and try again.")


if __name__ == "__main__":
	main()
