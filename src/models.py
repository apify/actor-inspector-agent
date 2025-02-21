"""This module defines Pydantic models for this project.

These models are used mainly for the structured tool and LLM outputs.
Resources:
- https://docs.pydantic.dev/latest/concepts/models/
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, RootModel
from pydantic.alias_generators import to_camel

config_to_camel = ConfigDict(
    alias_generator=to_camel,
    populate_by_name=True,
    from_attributes=True,
)


class CodeQualityOutput(BaseModel):
    contains_tests: bool
    is_linter_enabled: bool
    code_smells: bool
    security_vulnerabilities: bool
    performance_issues: bool
    code_style_issues: bool

class GithubRepoFile(BaseModel):
    """
    GithubRepoFile Pydantic model.

    Attributes:
        name: The name of the file.
        content: The content of the file.
    """

    name: str
    content: str


class GithubRepoContext(BaseModel):
    """
    GithubRepoContext Pydantic model.

    Attributes:
        tree: A dictionary representing the file tree of the repository.
        files: A list of GithubRepoFile objects representing the files in the repository.
    """

    tree: dict
    files: list[GithubRepoFile]


class ActorInputProperty(BaseModel):
    """Actor input property Pydantic model.

    title: The title of the property.
    description: The description of the property.
    type: The type of the property.
    default: The default or prefill value of the property.
    """

    title: str
    description: str
    type: str
    default: Any | None


class ActorInputDefinition(BaseModel):
    """Actor input definition Pydantic model.

    Returned as a structured output by the `tool_get_actor_input_schema` tool.

    title: The title of the input definition.
    description: The description of the input definition.
    properties: A dictionary of ActorInputProperty objects.
    """

    title: str
    description: str
    properties: dict[str, ActorInputProperty]

class Stats(BaseModel):
    """Actor statistics total runs, users"""
    total_runs: int | None = None
    total_users30_days: int | None = None
    public_actor_run_stats30_days: dict = None
    model_config = config_to_camel

# Nested model for 'pricingInfos'
class ActorChargeEvent(BaseModel):
    event_description: str
    event_price_usd: float
    event_title: str
    model_config = config_to_camel

class PricingPerEvent(BaseModel):
    actor_charge_events: dict[str, ActorChargeEvent] | None = None
    model_config = config_to_camel

class PricingInfo(BaseModel):
    """Pricing information: Pay per usage, Pay per results, Pay per event."""
    pricing_model: str
    price_per_unit_usd: float | None = None
    trial_minutes: int | None = None
    apify_margin_percentage: float | None = None
    minimal_max_total_charge_usd: float | None = None
    pricing_per_event: PricingPerEvent | None = None
    model_config = config_to_camel

class ActorStore(BaseModel):
    """ Actor Store List Pydantic model."""
    name: str
    username: str
    title: str
    description: str | None = None
    stats: Stats | None = None
    current_pricing_info: PricingInfo | None = None
    url: str | None = None
    total_stars: int | None = None
    model_config = config_to_camel

class ActorStoreList(RootModel):
    """ Actor Store List Pydantic model."""
    root: list[ActorStore]

