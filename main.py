from config import settings
from helpers import (
    AnypointBasicCredentials,
    ConnectedApp,
    authenticate,
    create_connected_app,
    load_scopes,
)
from log import logger
from utils import create_banner


def main():
    banner = create_banner("Noname SA Tools")
    logger.info(banner)

    # Credentials object
    credentials = AnypointBasicCredentials(
        username=settings.ANYPOINT_USERNAME, password=settings.ANYPOINT_PASSWORD
    )

    # Token object with the access token
    token = authenticate(username=credentials.username, password=credentials.password)

    scopes = load_scopes()

    payload = ConnectedApp(
        client_name=settings.NONAME_CLIENT_NAME,
        public_keys=[],
        redirect_uris=[],
        grant_types=["client_credentials"],
        scopes=scopes,
        enabled=True,
        audience="internal",
        generate_iss_claim_without_token=True,
    )

    if settings.CREATE:
        new_client = create_connected_app(token=token, payload=payload)
        logger.info(
            f"\n\nCopy the following information and use it when configuring the interation in your Noname Platform.\nNoname Connected App Credentials:\n\n client_name: \t\t{new_client['client_name']}\n client_id: \t\t{new_client['client_id']}\n client_secret: \t{new_client['client_secret']}\n\n"
        )
    else:
        logger.info("The Connected App creation is disabled")


if __name__ == "__main__":
    main()
