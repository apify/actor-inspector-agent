from crewai import Agent

from src.tools import tool_get_github_repo_context


def create_code_quality_agent(llm: str, debug: bool = False) -> Agent:
    """
    Create an Agent instance configured for code quality inspection.

    Args:
        debug (bool): If True, the agent will operate in verbose mode for debugging purposes.

    Returns:
        Agent: An instance of the Agent class configured for code quality inspection.
    """
    tools = [tool_get_github_repo_context]
    return Agent(
        role='Expert code quality inspector',
        goal='Inspect the code quality of a GitHub repository.',
        backstory=(
            'I am an expert code quality inspector who can help you inspect the code quality '
            'of a GitHub repository. '
            'My tools include the ability to get the context of a GitHub repository, '
            'such as the repo file tree and file '
            'contents. I can help by delivering insights on the code quality of the repository.'
            ' The main criteria for '
            'code quality are cleanliness and maintainability.'
        ),
        tools=tools,
        verbose=debug,
        llm=llm,
    )




def create_manager_agent(llm: str, debug: bool = False) -> Agent:
    """
    Create an Agent instance configured for project management.

    Returns:
        Agent: An instance of the Agent class configured for project management.
    """
    return Agent(
        role='Project Manager',
        goal='Efficiently manage the crew and ensure high-quality task completion',
        backstory=(
            "You're an experienced project manager, skilled in overseeing complex "
            'projects and guiding teams to success. '
            'Your role is to coordinate the efforts of the crew members, '
            'ensuring that each task is completed on time '
            'and to the highest standard.'
        ),
        allow_delegation=True,
        verbose=debug,
        llm=llm,
    )
