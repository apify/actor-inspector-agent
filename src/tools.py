"""This module defines the tools used by the agent.

Feel free to modify or add new tools to suit your specific needs.

To learn how to create a new tool, see:
- https://docs.crewai.com/concepts/tools
"""

from __future__ import annotations

import logging

import requests
from apify_client import ApifyClient
from crewai.tools import BaseTool, tool
from pydantic import BaseModel, Field

from src.const import REQUESTS_TIMEOUT_SECS
from src.models import ActorInputDefinition, ActorInputProperty, GithubRepoContext, GithubRepoFile
from src.utils import get_actor_latest_build, get_apify_token

logger = logging.getLogger('apify')


class GetActorReadmeInput(BaseModel):
    """Input schema for GetActorReadme."""

    actor_id: str = Field(..., description='The ID of the Apify Actor.')


class GetActorReadmeTool(BaseTool):
    name: str = 'get_actor_readme'
    description: str = 'Fetch the README content of the specified Apify Actor.'
    args_schema: type[BaseModel] = GetActorReadmeInput

    def _run(self, actor_id: str) -> str:
        logger.info('Getting README for actor %s', actor_id)
        apify_client = ApifyClient(token=get_apify_token())
        build = get_actor_latest_build(apify_client, actor_id)
        readme = build.get('actorDefinition', {}).get('readme')
        if not readme:
            raise ValueError(f'Failed to get the README for the Actor {actor_id}')
        return readme


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
    logger.info('Getting README for actor %s', actor_id)
    apify_client = ApifyClient(token=get_apify_token())
    build = get_actor_latest_build(apify_client, actor_id)

    if not (readme := build.get('actorDefinition', {}).get('readme')):
        raise ValueError(f'Failed to get the README for the Actor {actor_id}')

    return readme


@tool
def tool_get_actor_input_schema(actor_id: str) -> ActorInputDefinition | str:
    """Tool to get the input schema of an Apify Actor.

    If the input schema is not found a None value is returned.

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
        return 'Actor input schema is not available.'

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


class GetGithubRepoContextInput(BaseModel):
    """Input schema for GetGithubRepoContext."""

    repository_url: str = Field(..., description='The URL of the GitHub repository')
    max_tokens: int = Field(120_000, description='Maximum number of tokens to retrieve')


class GetGithubRepoContextTool(BaseTool):
    name: str = 'get_github_repo_context'
    description: str = 'Fetch the context of the specified GitHub repository.'
    args_schema: type[BaseModel] = GetGithubRepoContextInput

    def _run(self, repository_url: str, max_tokens: int = 120_000) -> GithubRepoContext | str:
        verify_response = requests.get(repository_url, timeout=REQUESTS_TIMEOUT_SECS)
        if verify_response.status_code == requests.codes.not_found:
            return (
                f'Repository {repository_url} does not exist. Code is not available. '
                'If other repository links are available, use them; otherwise, '
                'skip the tool and grade the code as N/A.'
            )

        repo_path = repository_url.split('github.com/')[-1].replace('.git', '')

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
