import os

import requests
from apify_client import ApifyClient

from src.const import REQUESTS_TIMEOUT_SECS

APIFY_API_ENDPOINT_GET_DEFAULT_BUILD = 'https://api.apify.com/v2/acts/{actor_id}/builds/default'


def get_apify_token() -> str:
    if not (token := os.getenv('APIFY_TOKEN')):
        raise ValueError('APIFY_TOKEN environment variable is not set')
    return token


def get_actor_latest_build(apify_client: ApifyClient, actor_id: str) -> dict:
    """Get the latest build of an Actor from the default build tag.

    Args:
        apify_client (ApifyClient): An instance of the ApifyClient class.
        actor_id (str): Actor name from Apify store to run.

    Returns:
        dict: The latest build of the Actor.

    Raises:
        ValueError: If the Actor is not found or the build data is not found.
        TypeError: If the build is not a dictionary.
    """
    if not (actor := apify_client.actor(actor_id).get()):
        msg = f'Actor {actor_id} not found.'
        raise ValueError(msg)

    if not (actor_obj_id := actor.get('id')):
        msg = f'Failed to get the Actor object ID for {actor_id}.'
        raise ValueError(msg)

    url = APIFY_API_ENDPOINT_GET_DEFAULT_BUILD.format(actor_id=actor_obj_id)
    response = requests.request('GET', url, timeout=REQUESTS_TIMEOUT_SECS)

    build = response.json()
    if not isinstance(build, dict):
        msg = f'Failed to get the latest build of the Actor {actor_id}.'
        raise TypeError(msg)

    if (data := build.get('data')) is None:
        msg = f'Failed to get the latest build data of the Actor {actor_id}.'
        raise ValueError(msg)

    return data
