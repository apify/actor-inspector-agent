"""This module defines the tools used by the agent.

Feel free to modify or add new tools to suit your specific needs.

To learn how to create a new tool, see:
- https://docs.crewai.com/concepts/tools
"""

from __future__ import annotations

import requests
from apify_client import ApifyClient
from crewai.tools import tool

from src.const import REQUESTS_TIMEOUT_SECS
from src.models import ActorInputDefinition, ActorInputProperty, GithubRepoContext, GithubRepoFile
from src.utils import get_actor_latest_build, get_apify_token



@tool
def tool_get_actor_readme(actor_id: str) -> str:
    """Tool to get the README of an Apify Actor.

    Args:
        actor_id (str): The ID of the Apify Actor.

    Returns:
        str: The README content of the specified Actor.

    Raises:
        ValueError: If the README for the Actor cannot be retrieved.
    """
    apify_client = ApifyClient(token=get_apify_token())
    build = get_actor_latest_build(apify_client, actor_id)

    if not (readme := build.get('actorDefinition', {}).get('readme')):
        raise ValueError(f'Failed to get the README for the Actor {actor_id}')

    return readme


@tool
def tool_get_actor_input_schema(actor_id: str) -> ActorInputDefinition:
    """Tool to get the input schema of an Apify Actor.

    Args:
        actor_id (str): The ID or name of the Apify Actor.

    Returns:
        ActorInputDefinition: The input schema of the specified Actor.

    Raises:
        ValueError: If the input schema for the Actor cannot be retrieved.
    """
    apify_client = ApifyClient(token=get_apify_token())
    build = get_actor_latest_build(apify_client, actor_id)


    if not (actor_definition := build.get('actorDefinition')):
        raise ValueError(f'Actor definition not found in the Actor build for Actor: {actor_id}')

    if not (actor_input := actor_definition.get('input')):
            raise ValueError(f'Input schema not found in the Actor build for Actor: {actor_id}')

    properties: dict[str, ActorInputProperty] = {}
    for name, prop in actor_input.get('properties', {}).items():
        # Use prefill, if available, then default, if available
        prop['default'] = prop.get('prefill', prop.get('default'))

        properties[name] = ActorInputProperty(**prop)

    return ActorInputDefinition(
        title=actor_definition.get('title'),
        description=actor_definition.get('description'),
        properties=properties,
    )


UITHUB_LINK = 'https://uithub.com/{repo_path}?accept=application/json&maxTokens={max_tokens}'


@tool
def tool_get_github_repo_context(repo_url: str, max_tokens: int = 120_000) -> GithubRepoContext:
    """Tool to get the context of a GitHub repository.

    Args:
        repo_url (str): The URL of the GitHub repository.
        max_tokens (int, optional): The maximum number of tokens to retrieve. Defaults to 120,000.

    Returns:
        GithubRepoContext: The context of the specified GitHub repository.

    Raises:
        ValueError: If the repository context cannot be retrieved.
    """
    repo_path = repo_url.split('github.com/')[-1]

    url = UITHUB_LINK.format(repo_path=repo_path, max_tokens=max_tokens)
    response = requests.get(url, timeout=REQUESTS_TIMEOUT_SECS)

    data = response.json()
    tree = data['tree']
    files: list[GithubRepoFile] = []

    for name, file in data.get('files', {}).items():
        if any(
            substring in name.lower()
            for substring in [
                'license',
                'package-lock.json',
                'yarn.lock',
                'readme.md',
                'poetry.lock',
                'requirements.txt',
                'setup.py',
                'uv.lock',
            ]
        ):
            continue
        if file['type'] != 'content':
            continue
        files.append(GithubRepoFile(name=name, content=file['content']))

    return GithubRepoContext(tree=tree, files=files)
