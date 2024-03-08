from decouple import config


class Config:
    DEBUG = config("DEBUG", cast=bool, default=False)
    DATAFILE_DIRECTORY = config("DATAFILE_DIRECTORY", default="datafiles")
    OUTPUT_DIRECTORY = config("OUTPUT_DIRECTORY", default="output")
    ANYPOINT_URL = config("ANYPOINT_URL", default="https://anypoint.mulesoft.com")
    ANYPOINT_ORG_ID = config(
        "ANYPOINT_ORG_ID",
        default=None,
        cast=lambda v: [x.strip() for x in v.split(",")],
    )
    ANYPOINT_AUTH_API = config("ANYPOINT_AUTH_API", default="/api/v1/oauth/token")
    ANYPOINT_ACCOUNTS_API = config(
        "ANYPOINT_ACCOUNTS_API", default="/accounts/api/connectedApplications"
    )
    ANYPOINT_ENVIRONMENTS_API = config(
        "ANYPOINT_ENVIRONMENTS_API",
        default="/accounts/api/organizations/{orgId}/environments",
    )
    ANYPOINT_AUTHORIZE_SCOPES_API = config(
        "ANYPOINT_AUTHORIZE_SCOPES_API",
        default="/accounts/api/organizations/orgId/connectedApplications/clientId/scopes",
    )
    SCOPES_SAMPLE_FILE = config("SCOPES_SAMPLE_FILE", default="scopes.json")
    ANYPOINT_USERNAME = config("ANYPOINT_USERNAME", default=None)
    ANYPOINT_PASSWORD = config("ANYPOINT_PASSWORD", default=None)
    NONAME_CLIENT_NAME = config("NONAME_CLIENT_NAME", default=None)
    CREATE = config("CREATE", cast=bool, default=True)
    DELETE_APPS = config("DELETE_APPS", cast=bool, default=False)


settings = Config()
