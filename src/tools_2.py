"""This module defines the tools used by the agent.

Feel free to modify or add new tools to suit your specific needs.

To learn how to create a new tool, see:
- https://docs.crewai.com/concepts/tools
"""

from __future__ import annotations

import datetime
import logging

from apify_client import ApifyClient
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from src.models import ActorStoreList, PricingInfo
from src.utils import get_apify_token

logger = logging.getLogger('apify')

class SearchRelatedActorsInput(BaseModel):
    """Input schema for SearchRelatedActors."""
    search: str = Field(..., description='A string of keywords to search by. The search is performed across the title,'
                                         'name, description, username, and README of an Actor.')
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
        """ Execute the tool's logic to search related actors by keyword. """
        try:
            logger.info(f"Searching for Actors related to '{search}'")
            apify_client = ApifyClient(token=get_apify_token())
            search_results = apify_client.store().list(limit=limit, offset=offset, search=search).items
            logger.info(f"Found {len(search_results)} Actors related to '{search}'")
        except Exception as e:
            logger.exception(f"Failed to search for Actors related to '{search}'")
            raise ValueError(f"Failed to search for Actors related to '{search}': {e}") from None

        return ActorStoreList.model_validate(search_results, strict=False)


class GetActorPricingInformationInput(BaseModel):
    """Input schema for GetActorPricingInformation."""
    actor_id: str = Field(..., description='The ID of the Apify Actor.')

class GetActorPricingInformationTool(BaseTool):
    name: str = 'get_actor_pricing_information'
    description: str = 'Fetch and return the pricing information of an Apify Actor.'
    args_schema: type[BaseModel] = GetActorPricingInformationInput

    def _run(self, actor_id: str) -> PricingInfo | None:
        apify_client = ApifyClient(token=get_apify_token())
        actor = apify_client.actor(actor_id).get()
        if not actor:
            raise ValueError(f'Actor {actor_id} not found.')

        pricing_info = actor.get('pricingInfos')
        if not pricing_info:
            return PricingInfo(pricing_model='PRICE_PER_USAGE')

        current_pricing = None
        now = datetime.datetime.now(datetime.UTC)
        for pricing_entry in pricing_info:
            if pricing_entry.get('startedAt') > now:
                break
            current_pricing = pricing_entry

        return PricingInfo.model_validate(current_pricing)
