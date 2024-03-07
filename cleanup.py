from config import settings
from helpers import authenticate, delete_all_connected_apps, get_all_connected_apps
from log import logger


def main():
    """
    WARNING: THIS SCRIPT WILL DELETE ALL YOUR CONNECTED APPS!
    Used only for testing and development purposes.
    """

    if settings.DELETE_APPS:
        confirmation = input(
            "Are you sure you want to delete all the Connected Apps? (Y/n): "
        )
        if confirmation.upper() == "Y":
            signature = input("Please type Proceed to delete all the Connected Apps: ")
            if signature == "Proceed":
                logger.warning(
                    "🧨 Deleting all the Anypoint Connected Apps. You've been warned ☠️..."
                )
                # Token object with the access token
                token = authenticate(
                    username=settings.ANYPOINT_USERNAME,
                    password=settings.ANYPOINT_PASSWORD,
                )

                connected_apps = get_all_connected_apps(access_token=token.access_token)
                total_apps = len(connected_apps)
                logger.warning(
                    f"There are {total_apps} Connected Apps to be deleted\n\n"
                )

                delete_all_connected_apps(token=token, connected_apps=connected_apps)

            else:
                logger.info(f"Signature [{signature}] does not match with: Proceed")
        else:
            logger.info("Deletion aborted by the user")
    else:
        logger.info("The Connected App deletion is disabled")


if __name__ == "__main__":
    main()
