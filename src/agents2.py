from crewai import Agent

from src.tools import tool_get_actor_readme
from src.tools_2 import SearchRelatedActorsTool


def create_uniqueness_check_agent(llm: str, debug: bool = False) -> Agent:
    """
    Create an Agent instance configured for code quality inspection.

    Args:
        llm (str): If True, the agent will operate in verbose mode for debugging purposes.
        debug (bool): If True, the agent will operate in verbose mode for debugging purposes.

    Returns:
        Agent: An instance of the Agent class configured for code quality inspection.
    """
    tools = [tool_get_actor_readme,SearchRelatedActorsTool()]
    return Agent(
        role='Apify Actor expert',
        goal=(
            'You are an Apify expert to compare one Apify Actor to other Actors and judge its uniqueness '
            'in terms of functionality.'
            'Read Actor README and summarize it and search possible related Actors by keywords.'
            'You goal is to provide an analysis of the Actor functionality and list of related Actors.'
            '\nReport the following grade and explanation:'
            'GREAT: Actor is unique and there are no other Actors offering similar functionality.\n'
            'GOOD: Actor has some functionality that is similar to other Actors.\n'
            'BAD: Actor is very similar to other Actors and there are no clear distinguishable differences.\n'
            '\nAlways explain differences between Actors in terms of functionality.\n'
            '\nRemember always try to find relevant Actor with different keywords and multiple searches.\n'
        ),
        backstory=(
            'I am an Apify expert and I understand Apify platform and Actors.'
            'My tools include the ability to get Actor readme and search for other related Actors '
            'using full text search'
            'I should repeat the search if required with a different set of keywords.'
            '1. Actor is unique and there are no other Actors offering similar functionality.\n'
            '2. Actor has some functionality that is similar to other Actors.\n'
            '3. Actor is very similar to other Actors and there are no clear distinguishable differences.\n'
            'Always explain differences between Actors in terms of functionality.\n'
        ),
        tools=tools,
        verbose=debug,
        llm=llm,
    )
