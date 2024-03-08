from dataclasses import dataclass
from typing import Dict, List


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


@dataclass
class Environment:
    id: str
    name: str
    client_id: str
    is_production: bool
    type: str
    org_id: str


@dataclass
class Organization:
    org_id: str
    environments: List[Environment]


@dataclass
class ContextParams:
    org: str
    envId: str


@dataclass
class ScopesAuthorization:
    scope: str
    context_params: ContextParams


@dataclass
class Authorizations:
    payload: Dict[str, Dict[str, str]]
