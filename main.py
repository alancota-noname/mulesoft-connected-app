from config import settings
from helpers import (
    authenticate,
    authorize_connected_app,
    create_connected_app,
    get_environments,
    load_scopes,
    prepare_connected_app_payload,
    prepare_scope_authorizations_payload,
)
from log import logger
from models import AnypointBasicCredentials
from utils import create_banner

VERSION = "0.1.1"


def main():
    banner = create_banner("Noname SA Tools")
    logger.info(banner)

    # Print out the version of the script
    logger.info(f"Start version: {VERSION} 🐍")

    # Credentials object
    credentials = AnypointBasicCredentials(
        username=settings.ANYPOINT_USERNAME, password=settings.ANYPOINT_PASSWORD
    )

    # Token object with the access token
    token = authenticate(username=credentials.username, password=credentials.password)

    # List of scopes
    scopes, org_only, _, no_context = load_scopes()

    # List of Organizations and their environments
    organizations = get_environments(
        token=token, organizations=settings.ANYPOINT_ORG_ID
    )

    # Payload to authorize scopes for each environment
    authz_payload = prepare_scope_authorizations_payload(
        scopes=scopes,
        org_only=org_only,
        no_context=no_context,
        organizations=organizations,
    )

    # Payload to create a new Connected App
    new_app_payload = prepare_connected_app_payload(scopes=scopes)

    # This can be disabled for testing purposes
    if settings.CREATE:
        # Create the new Connected App
        new_client = create_connected_app(token=token, payload=new_app_payload)

        # Authorize new app scopes for each environment
        authorize_connected_app(
            token=token,
            app_id=new_client["client_id"],
            data=authz_payload,
        )

        logger.info(
            f"\n\nCopy the following information and use it when configuring the interation in your Noname Platform.\nNoname Connected App Credentials:\n\n client_name: \t\t{new_client['client_name']}\n client_id: \t\t{new_client['client_id']}\n client_secret: \t{new_client['client_secret']}\n\n"
        )

    else:
        logger.info("The Connected App creation is disabled")


if __name__ == "__main__":
    main()
