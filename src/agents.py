from crewai import Agent

from src.tools import GetActorReadmeTool, GetGithubRepoContextTool, tool_get_actor_input_schema


def create_code_quality_agent(llm: str, debug: bool = False) -> Agent:
    """
    Create an Agent instance configured for code quality inspection.

    Args:
        debug (bool): If True, the agent will operate in verbose mode for debugging purposes.

    Returns:
        Agent: An instance of the Agent class configured for code quality inspection.
    """
    tools = [GetGithubRepoContextTool()]
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


def create_actor_quality_agent(llm: str, debug: bool = False) -> Agent:
    """
    Create an Agent instance configured for Apify Actor quality inspection.

    Args:
        debug (bool): If True, the agent will operate in verbose mode for debugging purposes.

    Returns:
        Agent: An instance of the Agent class configured for Apify Actor quality inspection.
    """
    tools = [tool_get_actor_input_schema, GetActorReadmeTool()]
    return Agent(
        role='Apify Actor Evaluator',
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
