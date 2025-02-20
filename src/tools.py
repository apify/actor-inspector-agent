"""This module defines the tools used by the agent.

Feel free to modify or add new tools to suit your specific needs.

To learn how to create a new tool, see:
- https://docs.crewai.com/concepts/tools
"""

from __future__ import annotations
import os

from apify import Actor
from apify_client import ApifyClient
from crewai.tools import tool

from src.models import ActorInputDefinition, ActorInputProperty
from src.utils import get_actor_latest_build, get_apify_api_token

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
    apify_client = ApifyClient(token=get_apify_api_token())
    build = get_actor_latest_build(apify_client, actor_id)

    if not (readme := build.get("actorDefinition", {}).get("readme")):
        raise ValueError(f"Failed to get the README for the Actor {actor_id}")

    return readme

@tool
def tool_get_actor_input_schema(actor_id: str) -> ActorInputDefinition:
    """Tool to get the input schema of an Apify Actor.

    Args:
        actor_id (str): The ID of the Apify Actor.

    Returns:
        ActorInputDefinition: The input schema of the specified Actor.

    Raises:
        ValueError: If the input schema for the Actor cannot be retrieved.
    """
    apify_client = ApifyClient(token=get_apify_api_token())
    build = get_actor_latest_build(apify_client, actor_id)

    if not (actor_input := build.get('actorDefinition', {}).get('input')):
        raise ValueError(f'Input schema not found in the Actor build for Actor: {actor_id}')

    properties: dict[str, ActorInputProperty] = {}
    for name, prop in actor_input.get('properties', {}).items():
        # Use prefill, if available, then default, if available
        prop['default'] = prop.get('prefill', prop.get('default'))

        properties[name] = ActorInputProperty(**prop)

    return ActorInputDefinition(
        title=actor_input.get('title'),
        description=actor_input.get('description'),
        properties=properties,
    )
