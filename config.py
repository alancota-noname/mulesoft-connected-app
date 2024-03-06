from decouple import config


class Config:
	DEBUG = config("DEBUG", cast=bool, default=False)
	ANYPOINT_URL = config("ANYPOINT_URL", default="https://anypoint.mulesoft.com")
	ANYPOINT_AUTH_API = config("ANYPOINT_AUTH_API", default="/api/v1/oauth/token")
	ANYPOINT_ACCOUNTS_API = config(
		"ANYPOINT_ACCOUNTS_API", default="/accounts/api/connectedApplications"
	)
	SCOPES_SAMPLE_FILE = config("SCOPES_SAMPLE_FILE", default="scopes.json")
	ANYPOINT_USERNAME = config("ANYPOINT_USERNAME", default=None)
	ANYPOINT_PASSWORD = config("ANYPOINT_PASSWORD", default=None)
	NONAME_CLIENT_NAME = config("NONAME_CLIENT_NAME", default=None)
	CREATE = config("CREATE", cast=bool, default=True)



settings = Config()
