import logging
import os
from typing import Any

import requests
from apify_client import ApifyClient

from src.const import REQUESTS_TIMEOUT_SECS

APIFY_API_GET_DEFAULT_BUILD = 'https://api.apify.com/v2/acts/{actor_id}/builds/default'

logger = logging.getLogger('apify')


def get_apify_token() -> str:
    """
    Retrieve the Apify API token from environment variables.

    Returns:
        str: The Apify API token.

    Raises:
        ValueError: If the APIFY_TOKEN environment variable is not set.
    """
    if not (token := os.getenv('APIFY_TOKEN')):
        raise ValueError('APIFY_TOKEN environment variable is not set')
    return token


def get_actor_id(actor_name: str) -> str:
    """
    Retrieve the actor ID for a given actor name.

    Args:
        actor_name (str): The name of the actor.

    Returns:
        str: The ID of the actor.

    Raises:
        ValueError: If the actor is not found or the actor ID cannot be retrieved.
    """
    logger.debug('Get actor ID for actor %s', actor_name)
    apify_client = ApifyClient(token=get_apify_token())
    if not (actor := apify_client.actor(actor_name).get()):
        raise ValueError(f'Actor {actor_name} not found.')

    if not (actor_id := actor.get('id')):
        raise ValueError(f'Failed to get the Actor object ID for {actor_name}.')

    return str(actor_id)


def generate_file_tree(files: list[dict]) -> dict:
    """
    Generate a file tree hierarchy from a list of file dictionaries.

    Args:
        files (list): List of dictionaries containing 'name' keys with file paths

    Returns:
        dict: Nested dictionary representing the file tree structure
    """
    tree: dict = {}

    for file_info in files:
        # Split the path into components
        path_parts = file_info['name'].split('/')

        # Start with the root of our tree
        current = tree

        # Process each part of the path
        for i, part in enumerate(path_parts):
            # If it's the last part (the file), set it to None
            if i == len(path_parts) - 1:
                current[part] = None
            # Otherwise, it's a directory
            else:
                # If the directory doesn't exist yet, create it
                if part not in current:
                    current[part] = {}
                # Move to the next level
                current = current[part]

    return tree


def get_actor_github_urls(actor_name: str) -> list[str]:
    """
    Retrieve the GitHub repository URLs associated with an actor.

    Args:
        actor_name (str): The name of the actor.

    Returns:
        list[str]: A list of GitHub repository URLs associated with the actor.

    Raises:
        ValueError: If the actor is not found or the actor ID cannot be retrieved.
    """
    logger.debug('Get GitHub URLs for actor %s', actor_name)
    apify_client = ApifyClient(token=get_apify_token())
    actor_id = get_actor_id(actor_name)
    github_urls = []
    build = get_actor_latest_build(actor_id)
    if github_repo_url := build.get('actVersion', {}).get('gitRepoUrl'):
        github_urls.append(github_repo_url)

    versions = apify_client.actor(actor_id).versions().list().items
    github_urls.extend(version.get('gitRepoUrl') for version in versions if version.get('gitRepoUrl'))

    return github_urls


def github_repo_exists(repository_url: str) -> bool:
    """
    Check if a GitHub repository exists.

    Args:
        repository_url (str): The URL of the GitHub repository.

    Returns:
        bool: True if the repository exists, False otherwise.
    """
    verify_response = requests.get(repository_url, timeout=REQUESTS_TIMEOUT_SECS)
    return bool(verify_response.status_code == requests.codes.ok)


def get_actor_source_files(actor_name: str) -> list[dict]:
    """
    Retrieve the source files for the latest version of an actor from the default build tag.

    Args:
        actor_name (str): The name of the actor.

    Returns:
        list[dict]: A list of dictionaries representing the source files of the actor.
    """
    logger.debug('Get source files for actor %s', actor_name)
    apify_client = ApifyClient(token=get_apify_token())
    actor_id = get_actor_id(actor_name)
    versions = apify_client.actor(actor_id).versions().list().items
    if latest_version := next((x for x in versions if x.get('buildTag') == 'latest'), None):
        source_files = latest_version.get('sourceFiles', [])
        return [file for file in source_files if file.get('format', '').lower() == 'text']
    return []


def get_actor_latest_build(actor_name: str) -> dict[str, Any]:
    """Get the latest build of an Actor from the default build tag.

    Args:
        actor_name (str): Actor name from Apify store to run.

    Returns:
        dict: The latest build of the Actor.

    Raises:
        ValueError: If the Actor is not found or the build data is not found.
        TypeError: If the build is not a dictionary.
    """
    actor_obj_id = get_actor_id(actor_name)
    url = APIFY_API_GET_DEFAULT_BUILD.format(actor_id=actor_obj_id)

    logger.debug('Get latest build for Actor URL: %s', url)
    response = requests.request('GET', url, timeout=REQUESTS_TIMEOUT_SECS)

    build = response.json()
    if not isinstance(build, dict):
        msg = f'Failed to get the latest build of the Actor {actor_name}.'
        raise TypeError(msg)

    if (data := build.get('data')) is None:
        msg = f'Failed to get the latest build data of the Actor {actor_name}.'
        raise ValueError(msg)

    if not isinstance(data, dict):
        msg = f'Received invalid data for the latest build of the Actor {actor_name}.'
        raise TypeError(msg)

    return data
