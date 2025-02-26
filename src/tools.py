"""This module defines the tools used by the agent.

Feel free to modify or add new tools to suit your specific needs.

To learn how to create a new tool, see:
- https://docs.crewai.com/concepts/tools
"""

from __future__ import annotations

import datetime
import logging

import requests
from apify_client import ApifyClient
from crewai.tools import BaseTool, tool  # type: ignore[import-untyped]
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
        return str(readme)


@tool  # type: ignore[misc]
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


@tool  # type: ignore[misc]
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
        filtered_source_files = [
            CodeFile(name=file['name'], content=file['content'])
            for file in source_files
            if not any(substring in file['name'].lower() for substring in FILES_TO_SKIP)
        ]
        return CodeContext(tree=tree, files=filtered_source_files)

    repo_urls = get_actor_github_urls(apify_client, actor_name)
    for repo_url in repo_urls:
        if not github_repo_exists(repo_url):
            continue

        repo_path = repo_url.split('github.com/')[-1].replace('.git', '')

        url = UITHUB_LINK.format(repo_path=repo_path, max_tokens=max_tokens)
        response = requests.get(url, timeout=REQUESTS_TIMEOUT_SECS)

        data = response.json()
        tree = data['tree']
        filtered_repo_files = [
            CodeFile(name=name, content=file['content'])
            for name, file in data.get('files', {}).items()
            if not any(substring in name.lower() for substring in FILES_TO_SKIP) and file['type'] == 'content'
        ]

        return CodeContext(tree=tree, files=filtered_repo_files)

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
            logger.info(f"Searching for Actors, search: '{search}'")
            apify_client = ApifyClient(token=get_apify_token())
            search_results = apify_client.store().list(limit=limit, offset=offset, search=search).items
            logger.info(f"Found {len(search_results)} Actors related to '{search}'")
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
        logger.info('Getting pricing information for actor %s', actor_name)
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


class GetApifyPlatformPricing(BaseTool):
    name: str = 'get_apify_platform_pricing_per_usage'
    description: str = 'Get pricing plans for Apify Platform for pay per platform usage.'

    def _run(self) -> list[dict]:
        logger.info('Getting pricing information of Apify')
        return [
            {
                'name': 'Free',
                'cost': '$0 per month',
                'prepaid_usage': '$5',
                'compute_unit_pricing': '$0.4 per CU',
                'actor_ram': '8 GB',
                'max_concurrent_runs': 25,
                'support_level': 'Community support',
                'proxy_access': {
                    'residential_proxies': '$8 per GB',
                    'datacenter_proxies': '5 IPs included',
                    'serps_proxy': '$2.5 per 1,000 SERPs',
                },
            },
            {
                'name': 'Starter',
                'cost': '$49 per month',
                'prepaid_usage': '$49',
                'compute_unit_pricing': '$0.4 per CU',
                'actor_ram': '32 GB',
                'max_concurrent_runs': 32,
                'support_level': 'Chat support',
                'proxy_access': {
                    'residential_proxies': '$8 per GB',
                    'datacenter_proxies': '30 IPs included; additional IPs at $1 per IP',
                    'serps_proxy': '$2.5 per 1,000 SERPs',
                },
            },
            {
                'name': 'Scale',
                'cost': '$199 per month',
                'prepaid_usage': '$199',
                'compute_unit_pricing': '$0.3 per CU',
                'actor_ram': '128 GB',
                'max_concurrent_runs': 128,
                'support_level': 'Priority chat support',
                'personal_tech_training': '1 hour per quarter',
                'proxy_access': {
                    'residential_proxies': '$7.5 per GB',
                    'datacenter_proxies': '200 IPs included; additional IPs at $0.8 per IP',
                    'serps_proxy': '$2 per 1,000 SERPs',
                },
            },
            {
                'name': 'Business',
                'cost': '$999 per month',
                'prepaid_usage': '$999',
                'compute_unit_pricing': '$0.25 per CU',
                'actor_ram': '256 GB',
                'max_concurrent_runs': 256,
                'support_level': 'Dedicated account manager',
                'personal_tech_training': '1 hour per month',
                'proxy_access': {
                    'residential_proxies': '$7 per GB',
                    'datacenter_proxies': '500 IPs included; additional IPs at $0.6 per IP',
                    'serps_proxy': '$1.7 per 1,000 SERPs',
                },
            },
            {
                'name': 'Enterprise',
                'cost': 'Custom pricing',
                'prepaid_usage': 'Custom',
                'compute_unit_pricing': 'Custom',
                'actor_ram': 'Custom',
                'max_concurrent_runs': 'Custom',
                'support_level': 'Service Level Agreement (SLA) with custom contract',
                'personal_tech_training': 'Custom',
                'proxy_access': 'Custom',
            },
        ]
