from crewai import Agent  # type: ignore[import-untyped]

from src.tools import (
    GetActorPricingInfoTool,
    GetActorReadmeTool,
    SearchRelatedActorsTool,
    tool_get_actor_input_schema,
    tool_get_code_context,
)


def create_code_quality_agent(llm: str, debug: bool = False) -> Agent:
    """
    Create an Agent instance configured for code quality inspection.

    Args:
        debug (bool): If True, the agent will operate in verbose mode for debugging purposes.

    Returns:
        Agent: An instance of the Agent class configured for code quality inspection.
    """
    tools = [tool_get_code_context]
    return Agent(
        role='Code Quality Specialist',
        goal=(
            'Deliver a precise evaluation of the code quality for a GitHub repository, focusing on tests, '
            'linting, code smells, security vulnerabilities, performance issues, and code style consistency.'
        ),
        backstory=(
            "I'm a seasoned software engineer with over a decade of experience auditing codebases for startups "
            'and enterprises alike. Armed with tools like GitHub repository analysis, I excel at identifying '
            'strengths and weaknesses in code quality, offering actionable insights to improve reliability, '
            'maintainability, and performance.'
        ),
        tools=tools,
        verbose=debug,
        llm=llm,
    )


def create_actor_definition_quality_agent(llm: str, debug: bool = False) -> Agent:
    """
    Create an Agent instance configured for Apify Actor quality inspection.

    Args:
        debug (bool): If True, the agent will operate in verbose mode for debugging purposes.

    Returns:
        Agent: An instance of the Agent class configured for Apify Actor quality inspection.
    """
    tools = [tool_get_actor_input_schema, GetActorReadmeTool()]
    return Agent(
        role='Apify Actor Definition Evaluator',
        goal=(
            "Assess the quality of an Apify Actor's documentation and usability by analyzing its README clarity, "
            'input properties, ease of use, example provision, and GitHub link visibility.'
        ),
        backstory=(
            "I'm a meticulous Apify expert with years of experience reviewing Actors for usability and documentation "
            'excellence. Using tools to fetch READMEs and input schemas, I ensure Actors are intuitive and '
            'well-documented, helping users adopt them seamlessly while meeting Apify Store standards.'
        ),
        tools=tools,
        verbose=debug,
        llm=llm,
    )


def create_actor_inspector_agent(llm: str, debug: bool = False) -> Agent:
    """
    Create an Agent instance configured for project management.

    Returns:
        Agent: An instance of the Agent class configured for project management.
    """
    return Agent(
        role='Lead Actor Inspector',
        goal=(
            'Coordinate a comprehensive quality review of an Apify Actor by synthesizing detailed reports from '
            'specialized agents and delivering a final assessment with clear ratings and justifications.'
        ),
        backstory=(
            "I'm a veteran project manager with a deep understanding of Apify Actors, skilled at orchestrating teams "
            'of expert agents. My strength lies in distilling complex analyses into concise, actionable reports that '
            'drive improvement and ensure quality.'
        ),
        allow_delegation=True,
        verbose=debug,
        llm=llm,
    )


def create_uniqueness_check_agent(llm_model_name: str, debug: bool = False) -> Agent:
    """
    Create an Agent instance configured for code quality inspection.

    Args:
        llm_model_name (str): LLM model name.
        debug (bool): If True, the agent will operate in verbose mode for debugging purposes.

    Returns:
        Agent: An instance of the Agent class configured for code quality inspection.
    """
    tools = [GetActorReadmeTool(), SearchRelatedActorsTool()]
    return Agent(
        role='Apify Actor Uniqueness expert',
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
            'I need to execute search multiple times with different sets of keywords.\n'
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
            'searching for related Actors using keywords.\n'
            'Apify pricing models:\n'
            '- 5$ Free Plan: Use selected Actors free of charge, paying only platform usage costs.\n'
            '- Rental Model: After a trial, pay a flat monthly fee; developers receive 80% of the fees.\n'
            '- Pay-per-Result: Pay only for the results produced, with no extra usage fees.\n'
            '- Pay-per-Event: Pay for each specific action or event.\n'
            '- Pay-per-Usage: Pay based on the Apify platform usage generated when running the Actor.\n'
            'Provide a very short report with one of these ratings:\n'
            'GREAT (competitive pricing), GOOD (moderate), BAD (expensive).\n'
            'Include a brief explanation;\n\n'
            'Example output:\n'
            'Actor: apify/xyz-actor\n'
            'Pricing rating: GOOD\n'
            'Explanation: The price per event is moderate compared to similar Actors.\n'
        ),
        backstory=(
            'I am an Apify expert specialized in pricing analysis. My tools help retrieve pricing details and perform'
            'full-text searches to find related Actors. I evaluate overall pricing competitiveness.\n'
            'I am able to perform multiple searches with different sets of keywords.\n'
            'I am able to compare different pricing models. For example, when an Actor is paid per platform usage, '
            "I need to retrieve Apify's pricing plans for the platform and compare them with other pricing models.\n"
        ),
        tools=tools,
        verbose=debug,
        llm=llm_model_name,
    )
