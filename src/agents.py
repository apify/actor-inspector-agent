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
        role='Expert code quality inspector',
        goal=(
            'Inspect the code quality of a GitHub repository and provide a '
            'report for these criteria: '
            '- Contains tests? \n'
            '- Is linter enabled? \n'
            '- Are there any code smells? \n'
            '- Are there any security vulnerabilities? \n'
            '- Are there any performance issues visible in the code? \n'
            '- Are there any code style issues?\n'
        ),
        backstory=(
            'I am an expert code quality inspector who can help you inspect the code quality '
            'of a GitHub repository. '
            'My tools include the ability to get the context of a GitHub repository, '
            'such as the repo file tree and file '
            'contents. I can help by delivering insights on the code quality of the repository.'
            '\n Code quality guidelines:'
            'Maintain high code quality to ensure readability, reliability, and scalability. Focus on these key principles:\n\n'
            '1. **Clarity**: Write self-explanatory code with meaningful variable names and comments where needed.\n'
            '2. **Consistency**: Follow a style guide (e.g., PEP 8 for Python) for formatting and structure.\n'
            '3. **Modularity**: Break code into reusable functions or classes to avoid repetition.\n'
            '4. **Testing**: Include unit tests to catch bugs and validate functionality.\n'
            '5. **Performance**: Optimize for efficiency without sacrificing readability.\n\n'
            'Tips:\n'
            '- Keep functions short and focused (single responsibility).\n'
            '- Use version control (e.g., Git) with clear commit messages.\n'
            '- Lint your code regularly to catch errors early.\n'
            'Good code is easy to understand, maintain, and extend—aim for simplicity and robustness.'
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
        role='Expert Apify Actor quality inspector',
        goal=(
            'Inspect the quality of an Apify Actor and provide a report for these criteria: '
            '- Is the README well-defined? \n'
            '- Are the input properties well-defined and do they make sense? \n'
            '- Is the actor easy to follow and use for a real user from the README? \n'
            '- Are use examples provided? \n'
            '- Is open source (github) repository provided link in the README? \n'
        ),
        backstory=(
            'I am an expert in inspecting the quality of Apify Actors. '
            'My tools include the ability to get the README and input schema of an Apify Actor. '
            'I can help by delivering insights on how well the README is defined and how easy it is '
            'for a real user to follow and use the actor for the first time. '
            'Additionally, I will analyze the input properties descriptions to ensure they are well-defined and make sense.'
            '\n Actor README guidelines:'
            "In Apify, a readme is more than a developer guide—it's the public Actor detail page in the Store, serving as a landing page for users. It has four main functions: **SEO** (use keywords for Google visibility), **first impression** (convince users to try your Actor), **extended instructions** (explain complex inputs), and **support** (offer troubleshooting and help links).\n"
            '\n'
            '### Key Elements:\n'
            '1. **Intro & Features**: Briefly explain what the Actor does, its benefits, and data it extracts (e.g., with a table). Highlight platform perks like scheduling or proxies.\n'
            '2. **Tutorial**: Provide simple steps or link to a guide for using the Actor.\n'
            '3. **Pricing**: Clarify costs (e.g., per result or compute units), set expectations, and optimize for cost-related Google searches.\n'
            '4. **Input/Output**: Show input examples (screenshots) and output data (JSON or tables).\n'
            '5. **Other Actors**: Promote your related tools.\n'
            '6. **FAQ/Support**: Address common questions, bugs, legality, and contact options.\n'
            '\n'
            '### Tips:\n'
            '- Write in **markdown** (H2/H3 headings for SEO and table of contents).\n'
            '- Match the **tone** to your audience’s skill level (technical or beginner-friendly).\n'
            '- Keep the first 25% engaging—most users don’t scroll further.\n'
            '- Use **images/videos** (SEO-friendly, clickable) for better engagement and ranking.\n'
            '\n'
            'A good readme balances user needs, Google discoverability, and clear guidance, making it a powerful tool to attract and retain users. Aim for at least 300 words.\n'
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
        role='Actor Inspector',
        goal=(
            'Inspect the quality of an Apify Actor and provide a report for these criteria: '
            'For each criterion below, use two sentences at maximum. Also, provide a score on a scale of 1 to 10: '
            '- Overall code quality: Summarize the code quality of the actor. '
            '- Overall actor definition quality: Summarize the quality of the actor definition. '
        ),
        backstory=(
            'You are an expert in inspecting the quality of Apify Actors. '
            'Your agent crew consists of other experts, for example in code quality inspection and '
            'actor definition quality inspection, and they provide a more in-depth analysis for you. '
            'You delegate tasks to them and they provide you with the results that you '
            'use to create a report.'
        ),
        allow_delegation=True,
        verbose=debug,
        llm=llm,
    )
