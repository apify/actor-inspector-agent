"""This module defines Pydantic models for this project.

These models are used mainly for the structured tool and LLM outputs.
Resources:
- https://docs.pydantic.dev/latest/concepts/models/
"""

from __future__ import annotations

from typing import Any, Dict

from pydantic import BaseModel, RootModel



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
    totalRuns: int | None = None
    totalUsers30Days: int | None = None
    publicActorRunStats30Days: dict = None

# Nested model for 'pricingInfos'
class ActorChargeEvent(BaseModel):
    eventDescription: str
    eventPriceUsd: float
    eventTitle: str

class PricingPerEvent(BaseModel):
    actorChargeEvents: Dict[str, ActorChargeEvent]

class PricingInfo(BaseModel):
    """Pricing information: Pay per usage, Pay per results, Pay per event."""
    pricingModel: str
    pricePerUnitUsd: float | None = None
    trialMinutes: int | None = None
    apifyMarginPercentage: float | None = None
    minimalMaxTotalChargeUsd: float | None = None
    pricingPerEvent: PricingPerEvent | None = None

class ActorStore(BaseModel):
    """ Actor Store List Pydantic model."""
    name: str
    username: str
    title: str
    description: str | None = None
    stats: Stats | None = None
    currentPricingInfo: PricingInfo | None = None
    url: str | None = None
    totalStars: int | None = None

class ActorStoreList(RootModel):
    """ Actor Store List Pydantic model."""
    root: list[ActorStore]

