from crewai import Agent

from src.tools import GetActorReadmeTool
from src.tools_2 import GetActorPricingInfoTool, SearchRelatedActorsTool


def create_uniqueness_check_agent(llm_model_name: str, debug: bool = False) -> Agent:
    """
    Create an Agent instance configured for code quality inspection.

    Args:
        llm_model_name (str): LLM model name.
        debug (bool): If True, the agent will operate in verbose mode for debugging purposes.

    Returns:
        Agent: An instance of the Agent class configured for code quality inspection.
    """
    tools = [GetActorReadmeTool(),SearchRelatedActorsTool()]
    return Agent(
        role='Apify Actor expert',
        goal=(
            'Compare an Actors functionality and uniqueness by reading its README and '
            'searching related Actors using keywords.\n'
            'Provide very short report with one of these grades:\n'
            'GREAT (unique), GOOD (some similarity), BAD (similar to others).\n'
            'Always explain (briefly!) functional differences.\n\n'
            'Example output:\n'
            'Actor: apify/instagram-scraper\n'
            'Uniqueness score: GOOD\n'
            'Explanation: There are some Instagram Actors offering similar functionality.\n'
        ),
        backstory=(
            'I am an Apify expert familiar with the platform and its Actors.\n'
            'My tools include retrieving Actor README and performing full-text searches to find related Actors.\n'
            'I need to execute search multiple times with different sets of keywords.'
            'I need to gather at least a couple of related Actors to provide a good comparison.'
        ),
        tools=tools,
        verbose=debug,
        llm=llm_model_name,
    )


def create_pricing_check_agent(llm_model_name: str, debug: bool = False) -> Agent:
    """
    Create an Agent instance configured for pricing comparison of Apify Actors.

    Args:
        llm_model_name (str): LLM model name.
        debug (bool): If True, the agent will operate in verbose mode.

    Returns:
        Agent: An instance of the Agent class configured for pricing analysis.
    """
    tools = [GetActorPricingInfoTool(), SearchRelatedActorsTool()]
    return Agent(
        role='Apify Pricing expert',
        goal=(
            "Compare an Actor's pricing by retrieving its pricing information and "
            "searching for related Actors using keywords.\n"
            "Apify pricing models:\n"
            "- 5$ Free Plan: Use selected Actors free of charge, paying only platform usage costs.\n"
            "- Rental Model: After a trial, pay a flat monthly fee; developers receive 80% of the fees.\n"
            "- Pay-per-Result: Pay only for the results produced, with no extra usage fees.\n"
            "- Pay-per-Event: Pay for each specific action or event.\n"
            "- Pay-per-Usage: Pay based on the platform usage generated when running the Actor.\n"
            "Provide a very short report with one of these ratings:\n"
            "GREAT (competitive pricing), GOOD (moderate), BAD (expensive).\n"
            "Include a brief explanation;\n\n"
            "Example output:\n"
            "Actor: apify/xyz-actor\n"
            "Pricing rating: GOOD\n"
            "Explanation: The price per event is moderate compared to similar Actors.\n"
        ),
        backstory=(
            'I am an Apify expert specialized in pricing analysis. My tools help retrieve pricing details and '
            'perform full-text searches to find related Actors. I evaluate overall pricing competitiveness.'
        ),
        tools=tools,
        verbose=debug,
        llm=llm_model_name,
    )
