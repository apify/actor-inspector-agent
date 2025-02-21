"""This module defines the main entry point for the Apify Actor.

Feel free to modify this file to suit your specific needs.

To build Apify Actors, utilize the Apify SDK toolkit, read more at the official documentation:
https://docs.apify.com/sdk/python
"""

from __future__ import annotations

import logging

from apify import Actor
from apify_client import ApifyClient
from crewai import Crew, Task

from src.agents import create_actor_inspector_agent, create_actor_quality_agent, create_code_quality_agent
from src.agents2 import create_pricing_check_agent, create_uniqueness_check_agent
from src.utils import get_actor_latest_build, get_apify_token

fallback_input = {
    'actorId': 'apify/rag-web-browser',
    'modelName': 'gpt-4o-mini',
}


async def main() -> None:
    """Main entry point for the Apify Actor.

    This coroutine is executed using `asyncio.run()`, so it must remain an asynchronous function for proper execution.
    Asynchronous execution is required for communication with the Apify platform, and it also enhances performance in
    the field of web scraping significantly.

    Raises:
        ValueError: If the input is missing required attributes.
    """
    async with Actor:
        # Handle input
        actor_input = await Actor.get_input() or {}
        # fallback input is provided only for testing, you need to delete this line
        actor_input = {**fallback_input, **actor_input}

        actor_id = actor_input.get('actorId')
        model_name = actor_input.get('modelName', 'gpt-4o-mini')
        if debug := actor_input.get('debug', True):
            Actor.log.setLevel(logging.DEBUG)
            logger = logging.getLogger('apify')
            logger.setLevel(logging.DEBUG)
        if not actor_id:
            raise ValueError('Missing the "actorId" attribute in the input!')

        apify_client = ApifyClient(token=get_apify_token())
        build = get_actor_latest_build(apify_client, actor_id)
        github_repo_url = build.get('actVersion', {}).get('gitRepoUrl')

        Actor.log.debug('Github repo URL: %s', github_repo_url)

        inspector_agent = create_actor_inspector_agent(model_name)
        code_quality_agent = create_code_quality_agent(model_name, debug=debug)
        actor_quality_agent = create_actor_quality_agent(model_name, debug=debug)
        uniqueness_check_agent = create_uniqueness_check_agent(model_name, debug=debug)
        pricing_check_agent = create_pricing_check_agent(model_name, debug=debug)

        code_quality_task = Task(
            description=(
                f"Analyze the code quality of the Apify Actor '{actor_id}' using the GitHub repository at: {github_repo_url}. "
                "If the GitHub URL is not provided, skip all code-related tools and explicitly state that the code cannot be evaluated, assigning an 'N/A' grade. "
                "Evaluate the following criteria:\n"
                "- **Tests**: Are tests present? Rate as 'bad' (no tests), 'good' (some tests, missing major functionality), or 'great' (most key functionality tested). Explain briefly.\n"
                "- **Linter**: Is a linter enabled? Rate as 'bad' (not enabled), 'good' (partially enabled), or 'great' (fully enabled). Explain briefly.\n"
                "- **Code Smells**: Are there code smells (e.g., duplication)? Rate as 'bad' (many), 'good' (some), or 'great' (none). Explain briefly.\n"
                "- **Security**: Are there visible security vulnerabilities (e.g., outdated dependencies)? Rate as 'bad' (many), 'good' (some), or 'great' (none). Explain briefly.\n"
                "- **Performance**: Are there performance issues (e.g., inefficient loops)? Rate as 'bad' (many), 'good' (some), or 'great' (none). Explain briefly.\n"
                "- **Style**: Are there code style issues (e.g., inconsistent naming)? Rate as 'bad' (many), 'good' (some), or 'great' (none). Explain briefly.\n"
            ),
            expected_output=(
                "A structured report in markdown format with:\n"
                "- A section for each criterion (Tests, Linter, Code Smells, Security, Performance, Style).\n"
                "- Each section includes a rating ('bad', 'good', 'great' or 'N/A' if no URL) and a 1-2 sentence explanation.\n"
                "- A brief overall summary (2-3 sentences) with suggestions for improvement if applicable."
            ),
            agent=code_quality_agent,
        )

        actor_quality_task = Task(
            description=(
                f"Assess the quality of the Apify Actor '{actor_id}' based on its documentation and usability, using the GitHub repository at: {github_repo_url}. "
                "Evaluate the following criteria:\n"
                "- **README Clarity**: Is the README well-defined? Rate as 'bad' (poorly defined), 'good' (partially clear), or 'great' (fully detailed). Explain briefly.\n"
                "- **Input Properties**: Are input properties clear and logical? Rate as 'bad' (unclear), 'good' (partially clear), or 'great' (well-defined). Explain briefly.\n"
                "- **Usability**: Is the actor easy to use based on the README? Rate as 'bad' (confusing), 'good' (somewhat clear), or 'great' (very intuitive). Explain briefly.\n"
                "- **Examples**: Are usage examples provided? Rate as 'bad' (none), 'good' (some), or 'great' (comprehensive). Explain briefly.\n"
                "- **GitHub Link**: Is the GitHub link in the README? Rate as 'bad' (missing), 'good' (present but not prominent), or 'great' (clearly visible). Explain briefly."
            ),
            expected_output=(
                "A structured report in markdown format with:\n"
                "- A section for each criterion (README Clarity, Input Properties, Usability, Examples, GitHub Link).\n"
                "- Each section includes a rating ('bad', 'good', 'great') and a 1-2 sentence explanation.\n"
                "- A brief overall summary (2-3 sentences) with suggestions for improvement."
            ),
            agent=actor_quality_agent,
        )

        uniqueness_task = Task(
            description=(
                f"Evaluate the uniqueness of the Apify Actor '{actor_id}' compared to similar actors, using the GitHub repository at: {github_repo_url}. "
                "Assess the following criteria:\n"
                "- **Comparison**: Is the actor unique compared to peers? Rate as 'bad' (very similar), 'good' (somewhat unique), or 'great' (highly distinct). Explain briefly.\n"
                "- **Functionality**: Does it offer unique features? Rate as 'bad' (none), 'good' (some), or 'great' (highly unique). Explain briefly.\n"
                "- **Selling Points**: Are there standout selling points? Rate as 'bad' (none), 'good' (some), or 'great' (multiple). Explain briefly."
            ),
            expected_output=(
                "A structured report in markdown format with:\n"
                "- A section for each criterion (Comparison, Functionality, Selling Points).\n"
                "- Each section includes a rating ('bad', 'good', 'great') and a 1-2 sentence explanation.\n"
                "- A brief overall summary (2-3 sentences) highlighting unique aspects and improvement ideas."
            ),
            agent=uniqueness_check_agent,
        )

        pricing_task = Task(
            description=(
                f"Analyze the pricing of the Apify Actor '{actor_id}' for competitiveness and sensibility, using the GitHub repository at: {github_repo_url}. "
                "Evaluate the following criteria:\n"
                "- **Competitiveness**: Is pricing competitive with similar actors? Rate as 'bad' (expensive), 'good' (moderate), or 'great' (highly competitive). Explain briefly.\n"
                "- **Sensibility**: Does the pricing align with functionality? Rate as 'bad' (not sensible), 'good' (somewhat sensible), or 'great' (very sensible). Explain briefly.\n"
                "- **Transparency**: Are there hidden costs? Rate as 'bad' (many), 'good' (some), or 'great' (none). Explain briefly."
            ),
            expected_output=(
                "A structured report in markdown format with:\n"
                "- A section for each criterion (Competitiveness, Sensibility, Transparency).\n"
                "- Each section includes a rating ('bad', 'good', 'great') and a 1-2 sentence explanation.\n"
                "- A brief overall summary (2-3 sentences) with pricing improvement suggestions."
            ),
            agent=pricing_check_agent,
        )

        final_task = Task(
            description=(
                f"Compile a final quality assessment for the Apify Actor '{actor_id}' using the GitHub repository at: {github_repo_url}. "
                "Include the actor name and a brief summary of its purpose. "
                "Summarize findings from previous tasks and assign an overall rating:\n"
                "- **Code Quality**: Summarize code quality findings. Rate as 'bad', 'good', or 'great'. Explain in 1-2 sentences.\n"
                "- **Actor Quality**: Summarize actor quality findings. Rate as 'bad', 'good', or 'great'. Explain in 1-2 sentences.\n"
                "- **Uniqueness**: Summarize uniqueness findings. Rate as 'bad', 'good', or 'great'. Explain in 1-2 sentences.\n"
                "- **Pricing**: Summarize pricing findings. Rate as 'bad', 'good', or 'great'. Explain in 1-2 sentences.\n"
                "- **Overall**: Provide a final rating ('bad', 'good', 'great') with a 2-3 sentence justification."
            ),
            expected_output=(
                "A concise final report in markdown format with:\n"
                "- A header section including the Actor Name and a brief Summary of what the actor does (2-3 sentences).\n"
                "- A section for each category (Code Quality, Actor Quality, Uniqueness, Pricing, Overall).\n"
                "- Each section includes a rating ('bad', 'good', 'great') and a 1-2 sentence explanation.\n"
                "- The Overall section provides a final rating and a 2-3 sentence summary."
            ),
            context=[code_quality_task, actor_quality_task, uniqueness_task, pricing_task],
            agent=inspector_agent,
        )

        # Create a one-man crew
        # For more information, see https://docs.crewai.com/concepts/crews
        crew = Crew(
            agents=[
                code_quality_agent,
                actor_quality_agent,
                uniqueness_check_agent,
                pricing_check_agent,
            ],
            tasks=[final_task],
            manager_agent=inspector_agent,
        )

        # Kick off the crew and get the response
        Actor.log.info('Kicking off the crew...')
        crew_output = crew.kickoff()
        raw_response = crew_output.raw
        Actor.log.debug(raw_response)

        total_tokens = crew_output.token_usage.total_tokens
        Actor.log.debug(total_tokens)
        # charge for task completion
        await Actor.charge(event_name='task-completed')

        await Actor.push_data(
            {
                'actorId': actor_id,
                'response': raw_response,
            }
        )
        Actor.log.info('Pushed the data into the dataset!')


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())
