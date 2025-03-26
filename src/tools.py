"""This module defines the tools used by the agent.

Feel free to modify or add new tools to suit your specific needs.

To learn how to create a new tool, see:
- https://docs.crewai.com/concepts/tools
"""

from __future__ import annotations

import datetime
import logging
from urllib.parse import urlparse

import requests
from apify_client import ApifyClient
from crewai.tools import BaseTool  # type: ignore[import-untyped]
from pydantic import BaseModel, Field

from src.const import REQUESTS_TIMEOUT_SECS
from src.models import ActorInputDefinition, ActorInputProperty, ActorStoreList, CodeContext, CodeFile, PricingInfo
from src.utils import (
    generate_file_tree,
    get_actor_github_urls,
    get_actor_latest_build,
    get_actor_source_files,
    get_apify_token,
    github_repo_exists,
)

logger = logging.getLogger('apify')

UITHUB_LINK = 'https://uithub.com/{repo_path}?accept=application/json&maxTokens={max_tokens}'

IGNORE_FILES = [
    'license',
    'package-lock.json',
    'yarn.lock',
    'readme.md',
    'poetry.lock',
    'requirements.txt',
    'setup.py',
    'uv.lock',
]


class GetActorReadmeInput(BaseModel):
    """Input schema for GetActorReadme."""

    actor_name: str = Field(..., description='The name of the Apify Actor.')


class GetActorReadmeTool(BaseTool):
    name: str = 'get_actor_readme'
    description: str = 'Fetch the README content of the specified Apify Actor.'
    args_schema: type[BaseModel] = GetActorReadmeInput

    def _run(self, actor_name: str) -> str:
        """Execute the tool to get the README of an Apify Actor.

        Args:
            actor_name (str): The name of the Apify Actor.
        Returns:
            A string containing the README content.
        """
        logger.info('Getting README for Actor %s', actor_name)
        build = get_actor_latest_build(actor_name)
        readme = build.get('actorDefinition', {}).get('readme')
        if not readme:
            raise ValueError(f'Failed to get the README for the Actor {actor_name}')
        return str(readme)


class GetActorInputSchemaInput(BaseModel):
    """Input schema for GetActorInputSchemaTool."""

    actor_name: str = Field(..., description='The ID or name of the Apify Actor.')


class GetActorInputSchemaTool(BaseTool):
    name: str = 'get_actor_input_schema'
    description: str = (
        'Retrieve the input schema of an Apify Actor. If no input schema is available, '
        'an appropriate message is returned.'
    )
    args_schema: type[BaseModel] = GetActorInputSchemaInput

    def _run(self, actor_name: str) -> ActorInputDefinition | str:
        """Execute the tool to get the input schema of an Apify Actor.

        Args:
            actor_name (str): The ID or name of the Apify Actor.

        Returns:
            ActorInputDefinition: The structured input schema of the Actor
            str: A message if the input schema is not available.

        Raises:
            ValueError: If the Actor's input schema cannot be retrieved.
        """
        build = get_actor_latest_build(actor_name)

        if not (actor_definition := build.get('actorDefinition')):
            raise ValueError(f'Actor definition not found in the Actor build for Actor: {actor_name}')

        if not (actor_input := actor_definition.get('input')):
            return 'Actor input schema is not available.'

        # Process properties
        properties: dict[str, ActorInputProperty] = {}
        for name, prop in actor_input.get('properties', {}).items():
            # Use prefill value if available, default value otherwise
            prop['default'] = prop.get('prefill', prop.get('default'))
            properties[name] = ActorInputProperty(**prop)

        return ActorInputDefinition(
            title=actor_definition.get('title'),
            description=actor_definition.get('description'),
            properties=properties,
        )


class GetActorCodeInput(BaseModel):
    """Input schema for GetCodeContextTool."""

    actor_name: str = Field(..., description='The ID or name of the Apify Actor.')
    max_tokens: int = Field(120_000, description='Maximum number of tokens to retrieve. Default is 120,000.', gt=0)


class GetActorCodeTool(BaseTool):
    name: str = 'get_actor_code'
    description: str = (
        'Retrieve source code for a specified Apify Actor, including the file tree and file contents. '
        'If no data is available from the Actor, the tool attempts to fetch code from GitHub.'
    )
    args_schema: type[BaseModel] = GetActorCodeInput

    @staticmethod
    def _get_code_from_github(repo_urls: list[str], max_tokens: int) -> CodeContext | None:
        """Get code context from GitHub repository."""

        for repo_url in repo_urls:
            if not github_repo_exists(repo_url):
                continue

            parsed_url = urlparse(repo_url)
            repo_path = parsed_url.path.strip('/').replace('.git', '').split('#')[0]

            url = UITHUB_LINK.format(repo_path=repo_path, max_tokens=max_tokens)
            response = requests.get(url, timeout=REQUESTS_TIMEOUT_SECS)
            data = response.json()

            tree = data['tree']
            filtered_repo_files = [
                CodeFile(name=name, content=file['content'])
                for name, file in data.get('files', {}).items()
                if not any(substring in name.lower() for substring in IGNORE_FILES) and file['type'] == 'content'
            ]
            return CodeContext(tree=tree, files=filtered_repo_files)
        return None

    @staticmethod
    def _get_code_from_source(source_files: list[dict]) -> CodeContext:
        """Get code from source files."""

        tree = generate_file_tree(source_files)
        filtered_source_files = [
            CodeFile(name=file['name'], content=file['content'])
            for file in source_files
            if not any(substring in file['name'].lower() for substring in IGNORE_FILES)
        ]
        return CodeContext(tree=tree, files=filtered_source_files)

    def _run(self, actor_name: str, max_tokens: int = 120_000) -> CodeContext | str:
        """Execute the tool to retrieve the source code for Apify Actor.

        Args:
            actor_name (str): The ID or name of the Apify Actor.
            max_tokens (int, optional): Maximum number of tokens to retrieve. Defaults to 120_000.

        Returns:
            CodeContext: Structured code context of the specified Actor.
            str: An error message if code context cannot be retrieved at all.
        """
        logger.info('Get code context for Actor %s, max_tokens=%s', actor_name, max_tokens)
        # Try to get the source files
        if source_files := get_actor_source_files(actor_name):
            return self._get_code_from_source(source_files)

        # Fall back to GitHub repository
        repo_urls = get_actor_github_urls(actor_name)
        logger.info('Falling back to GitHub URL for Actor %s, repo URLs: %s', actor_name, repo_urls)

        if code_context := self._get_code_from_github(repo_urls, max_tokens):
            return code_context

        # If no data is available, return an error message
        return f'Code for Actor {actor_name} is not available. Skip the tool and grade the code as N/A.'


class SearchRelatedActorsInput(BaseModel):
    """Input schema for SearchRelatedActors."""

    search: str = Field(
        ...,
        description='A string of keywords to search by. The search is performed across the title,'
        'name, description, username, and README of an Actor.',
    )
    limit: int = Field(10, description='The maximum number of Actors to return', gt=0, le=100)
    offset: int = Field(0, description='The number of items to skip from the start of the results.', ge=0)


class SearchRelatedActorsTool(BaseTool):
    name: str = 'search_related_actors'
    description: str = (
        'Discover available Actors using a full-text search with specified keywords.'
        'The tool returns a list of Actors, including details such as name, description, run statistics,'
        'and pricing information, number of stars, and URL.'
        'Search with only few keywords, otherwise it will return empty results'
    )
    args_schema: type[BaseModel] = SearchRelatedActorsInput

    def _run(self, search: str, limit: int = 10, offset: int = 0) -> ActorStoreList | None:
        """Execute the tool's logic to search related actors by keyword."""
        try:
            logger.info('Search related Actors with key words: %s', search)
            apify_client = ApifyClient(token=get_apify_token())
            search_results = apify_client.store().list(limit=limit, offset=offset, search=search).items
            logger.info('Found %s Actors related with key words: %s', len(search_results), search)
            return ActorStoreList.model_validate(search_results, strict=False)
        except Exception as e:
            logger.exception(f"Failed to search for Actors related to '{search}'")
            raise ValueError(f"Failed to search for Actors related to '{search}': {e}") from None


class GetActorPricingInfoInput(BaseModel):
    """Input schema for GetActorPricingInformation."""

    actor_name: str = Field(..., description='The name of the Apify Actor.')


class GetActorPricingInfoTool(BaseTool):
    name: str = 'get_actor_pricing_information'
    description: str = 'Fetch and return the pricing information of an Apify Actor.'
    args_schema: type[BaseModel] = GetActorPricingInfoInput

    def _run(self, actor_name: str) -> PricingInfo | None:
        logger.info('Get pricing information for actor %s', actor_name)
        apify_client = ApifyClient(token=get_apify_token())
        actor = apify_client.actor(actor_name).get()
        if not actor:
            raise ValueError(f'Actor {actor_name} not found.')

        pricing_info = actor.get('pricingInfos')
        if not pricing_info:
            return PricingInfo(pricing_model='PAY_PER_PLATFORM_USAGE')

        current_pricing = None
        now = datetime.datetime.now(datetime.UTC)
        for pricing_entry in pricing_info:
            if pricing_entry.get('startedAt') > now:
                break
            current_pricing = pricing_entry

        return PricingInfo.model_validate(current_pricing)
