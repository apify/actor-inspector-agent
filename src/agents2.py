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
            'Compare an Actors functionality and uniqueness by reading its README and '
            'searching related Actors using keywords.\n'
            'Provide very short report with one of these grades:\n'
            'GREAT (unique), GOOD (some similarity), BAD (similar to others).\n'
            'Always explain (briefly!) functional differences.\n'
            'Example output:\n'
            'Actor: apify/instagram-scraper\n'
            'Uniqueness score: GOOD\n'
            'Explanation: There are some Instagram Actors offering similar functionality.\n'
        ),
        backstory=(
            'I am an Apify expert familiar with the platform and its Actors.\n'
            'My tools include retrieving Actor READMEs and performing full-text searches to find related Actors.\n'
            'I need to execute search multiple times with different sets of keywords.'
            'I need to gather at least a couple of related Actors to provide a good comparison.'
        ),
        tools=tools,
        verbose=debug,
        llm=llm,
    )
