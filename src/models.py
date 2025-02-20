"""This module defines Pydantic models for this project.

These models are used mainly for the structured tool and LLM outputs.
Resources:
- https://docs.pydantic.dev/latest/concepts/models/
"""

from __future__ import annotations
from typing_extensions import Any

from pydantic import BaseModel

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
