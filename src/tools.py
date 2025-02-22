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
from src.models import ActorInputDefinition, ActorInputProperty, CodeContext, CodeFile
from src.utils import (
    generate_file_tree,
    get_actor_github_urls,
    get_actor_latest_build,
    get_actor_source_files,
    get_apify_token,
    github_repo_exists,
)

logger = logging.getLogger('apify')


class GetActorReadmeInput(BaseModel):
    """Input schema for GetActorReadme."""

    actor_name: str = Field(..., description='The name of the Apify Actor.')


class GetActorReadmeTool(BaseTool):
    name: str = 'get_actor_readme'
    description: str = 'Fetch the README content of the specified Apify Actor.'
    args_schema: type[BaseModel] = GetActorReadmeInput

    def _run(self, actor_name: str) -> str:
        logger.info('Getting README for actor %s', actor_name)
        apify_client = ApifyClient(token=get_apify_token())
        build = get_actor_latest_build(apify_client, actor_name)
        readme = build.get('actorDefinition', {}).get('readme')
        if not readme:
            raise ValueError(f'Failed to get the README for the Actor {actor_name}')
        return readme


@tool
def tool_get_actor_readme(actor_name: str) -> str:
    """Tool to get the README of an Apify Actor.

    Args:
        actor_name (str): The name of the Apify Actor.

    Returns:
        str: The README content of the specified Actor.

    Raises:
        ValueError: If the README for the Actor cannot be retrieved.
    """
    logger.info('Getting README for actor %s', actor_name)
    apify_client = ApifyClient(token=get_apify_token())
    build = get_actor_latest_build(apify_client, actor_name)

    if not (readme := build.get('actorDefinition', {}).get('readme')):
        raise ValueError(f'Failed to get the README for the Actor {actor_name}')

    return readme


@tool
def tool_get_actor_input_schema(actor_name: str) -> ActorInputDefinition | str:
    """Tool to get the input schema of an Apify Actor.

    If the input schema is not found a None value is returned.

    Args:
        actor_name (str): The ID or name of the Apify Actor.

    Returns:
        ActorInputDefinition: The input schema of the specified Actor.

    Raises:
        ValueError: If the input schema for the Actor cannot be retrieved.
    """
    apify_client = ApifyClient(token=get_apify_token())
    build = get_actor_latest_build(apify_client, actor_name)

    if not (actor_definition := build.get('actorDefinition')):
        raise ValueError(f'Actor definition not found in the Actor build for Actor: {actor_name}')

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

FILES_TO_SKIP = [
    'license',
    'package-lock.json',
    'yarn.lock',
    'readme.md',
    'poetry.lock',
    'requirements.txt',
    'setup.py',
    'uv.lock',
]


@tool
def tool_get_code_context(actor_name: str, max_tokens: int = 120_000) -> CodeContext | str:
    """Get code context for the specified Apify Actor, including file tree and file contents.

    Args:
        actor_name (str): The ID of the Apify Actor.
        max_tokens (int): Maximum number of tokens to retrieve. Default is 120,000.

    Returns:
        CodeContext: The code context of the specified Actor.
        str: Error message if the code context cannot be retrieved.
    """

    apify_client = ApifyClient(token=get_apify_token())
    source_files = get_actor_source_files(apify_client, actor_name)
    if source_files:
        tree = generate_file_tree(source_files)
        files = []
        for file in source_files:
            if any(substring in file['name'].lower() for substring in FILES_TO_SKIP):
                continue
            files.append(CodeFile(name=file['name'], content=file['content']))
        return CodeContext(tree=tree, files=files)

    repo_urls = get_actor_github_urls(apify_client, actor_name)
    for repo_url in repo_urls:
        if not github_repo_exists(repo_url):
            continue

        repo_path = repo_url.split('github.com/')[-1].replace('.git', '')

        url = UITHUB_LINK.format(repo_path=repo_path, max_tokens=max_tokens)
        response = requests.get(url, timeout=REQUESTS_TIMEOUT_SECS)

        data = response.json()
        tree = data['tree']
        files: list[CodeFile] = []

        for name, file in data.get('files', {}).items():
            if any(substring in name.lower() for substring in FILES_TO_SKIP):
                continue
            if file['type'] != 'content':
                continue
            files.append(CodeFile(name=name, content=file['content']))

        return CodeContext(tree=tree, files=files)

    return f'Code for Actor {actor_name} is not available. Skip the tool and grade the code as N/A.'
