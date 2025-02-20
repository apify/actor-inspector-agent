"""This module defines the tools used by the agent.

Feel free to modify or add new tools to suit your specific needs.

To learn how to create a new tool, see:
- https://docs.crewai.com/concepts/tools
"""

from __future__ import annotations

import datetime

from apify_client import ApifyClient
from crewai.tools import tool

from src.models import ActorStoreList, PricingInfo
from src.utils import get_apify_api_token


@tool
def search_related_actors_by_keyword(search: str, limit: int | None = 10, offset: int | None = 0) -> ActorStoreList | None:
    """
    Discover available Actors using full-text search with specified keywords.

    The function returns a list of Actors, including details such as 
    name, description, run statistics, pricing information, number of stars, and URL.

    It may require multiple invocations of this method to find the most relevant Actor. 

    Args:
        limit (int, optional): The maximum number of Actors to return. Must be an integer
            between 1 and 100. Default is 10.
        offset (int, optional): The number of items to skip from the start of the results.
            Must be a non-negative integer. Default is 0.
        search (str, optional): A string of keywords to search by. The search is performed
            across the title, name, description, username, and README of an Actor. Only basic
            keyword search is supported; advanced search features are not available. Default
            is an empty string.

    Returns:
        ActorStoreList: A list of Actors. Each dictionary contains the following fields:
            - name (str): The name of the Actor.
            - description (str): A description of the Actor.
            - run statistics (dict): Statistics about the Actor's runs.
            - pricing (dict): Pricing information for the Actor.
            - stars (int): The number of stars the Actor has received.
            - url (str): The URL of the Actor.
    """
    apify_client = ApifyClient(token=get_apify_api_token())
    search_results = apify_client.store().list(limit=limit, offset=offset, search=search).items
    return ActorStoreList.model_validate(search_results, strict=False)

# @tool
def tool_get_actor_pricing_information(actor_id: str) -> PricingInfo:
    """Get the pricing information of an Apify Actor.

    Args:
        actor_id (str): The ID of the Apify Actor.

    Returns:
        str: The README content of the specified Actor.

    Raises:
        ValueError: If the README for the Actor cannot be retrieved.
    """
    apify_client = ApifyClient(token=get_apify_api_token())
    if not (actor := apify_client.actor(actor_id).get()):
        msg = f'Actor {actor_id} not found.'
        raise ValueError(msg)

    if not (pricing_info := actor.get('pricingInfos')):
        raise ValueError(f'Failed to find pricing information for the Actor {actor_id}.')

    current_pricing = None
    for pricing_entry in pricing_info:
        if pricing_entry.get('startedAt') > datetime.datetime.now(datetime.timezone.utc):
            break
        current_pricing = pricing_entry

    return PricingInfo.model_validate(current_pricing)
