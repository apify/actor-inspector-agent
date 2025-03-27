"""Main file of the Actor Inspector Agent for Apify Actors"""

from __future__ import annotations

import logging
import math

from apify import Actor
from crewai import Crew, Task  # type: ignore[import-untyped]

from src.agents import (
    create_actor_definition_quality_agent,
    create_actor_inspector_agent,
    create_code_quality_agent,
    create_pricing_check_agent,
    create_uniqueness_check_agent,
)
from src.const import PEDANTIC_MESSAGE


async def main() -> None:
    """Main entry point for the Apify Actor.

    This coroutine is executed using `asyncio.run()`, so it must remain an
    asynchronous function for proper execution.
    Asynchronous execution is required for communication with the Apify platform,
    and it also enhances performance in
    the field of web scraping significantly.

    """
    async with Actor:
        Actor.log.info('Starting Actor Inspector Agent')
        count = math.ceil((Actor.get_env().get('memory_mbytes', 1024) or 1024) // 1024)
        await Actor.charge(event_name='actor-start-gb', count=count)
        Actor.log.info('Charged for Actor start %d GB', count)

        actor_input = await Actor.get_input() or {}
        Actor.log.info('Received input: %s', actor_input)

        if not (actor_name := actor_input.get('actorName')):
            await Actor.fail(
                status_message='Missing the "actorName" attribute in the input!'
                ' Please provide the name of the actor in the form of user-name/actor-name.',
            )

        pedantic = actor_input.get('pedantic', True)
        model_name = actor_input.get('modelName', 'gpt-4o-mini')
        if debug := actor_input.get('debug', True):
            Actor.log.setLevel(logging.DEBUG)
            logger = logging.getLogger('apify')
            logger.setLevel(logging.DEBUG)

        inspector_agent = create_actor_inspector_agent(model_name, debug=debug, pedantic=pedantic)
        code_quality_agent = create_code_quality_agent(model_name, debug=debug, pedantic=pedantic)
        actor_quality_agent = create_actor_definition_quality_agent(model_name, debug=debug, pedantic=pedantic)
        uniqueness_check_agent = create_uniqueness_check_agent(model_name, debug=debug, pedantic=pedantic)
        pricing_check_agent = create_pricing_check_agent(model_name, debug=debug, pedantic=pedantic)

        code_quality_task = Task(
            description=(
                f'Analyze the code quality of the Apify Actor "{actor_name}"\n'
                'If code is not available, skip all code-related tools '
                'and explicitly state that the code cannot be evaluated, '
                'assigning an "N/A" grade. '
                f'{PEDANTIC_MESSAGE if pedantic else ""}'
                'Evaluate the following criteria:\n'
                '- **Tests**: Are tests present? Rate as "bad" (no tests), "good" '
                '(some tests, missing major functionality), or "great" (most '
                'key functionality tested). Explain briefly.\n'
                '- **Linter**: Is a linter enabled? Rate as "bad" (not enabled), '
                '"good" (partially enabled), or "great" (fully enabled). Explain '
                'briefly.\n'
                '- **Code smells**: Are there code smells (e.g., duplication)? '
                'Rate as "bad" (many), "good" (some), or "great" (none). Explain '
                'briefly.\n'
                '- **Security**: Are there visible security vulnerabilities '
                '(e.g., outdated dependencies)? Rate as "bad" (many), "good" '
                '(some), or "great" (none). Explain briefly.\n'
                '- **Performance**: Are there performance issues (e.g., '
                'inefficient loops)? Rate as "bad" (many), "good" (some), or '
                '"great" (none). Explain briefly.\n'
                '- **Style**: Are there code style issues (e.g., inconsistent '
                'naming)? Rate as "bad" (many), "good" (some), or "great" (none). '
                'Explain briefly.\n'
            ),
            expected_output=(
                'A structured report in markdown format with:\n'
                '- A section for each criterion (Tests, Linter, Code smells, '
                'Security, Performance, Style).\n'
                '- Each section includes a rating ("bad", "good", "great" or '
                '"N/A" if no URL) and a 1-2 sentence explanation.\n'
                '- A brief list of suggestions for improvement if applicable.\n'
                '- A brief overall summary (2-3 sentences) with suggestions for '
                'improvement if applicable.'
            ),
            agent=code_quality_agent,
        )

        actor_quality_task = Task(
            description=(
                f'Assess the quality of the Apify Actor "{actor_name}" based on its '
                'documentation and usability. '
                f'{PEDANTIC_MESSAGE if pedantic else ""}'
                'Evaluate the following criteria:\n'
                '- **README clarity**: Is the README well-defined? Rate as "bad" '
                '(poorly defined), "good" (partially clear), or "great" (fully '
                'detailed). Explain briefly.\n'
                '- **Input properties**: Are input properties clear and logical? '
                'Rate as "bad" (unclear), "good" (partially clear), or "great" '
                '(well-defined). Explain briefly.\n'
                '- **Usability**: Is the Actor easy to use based on the README? '
                'Rate as "bad" (confusing), "good" (somewhat clear), or "great" '
                '(very intuitive). Explain briefly.\n'
                '- **Examples**: Are usage examples provided? Rate as "bad" '
                '(none), "good" (some), or "great" (comprehensive). Explain '
                'briefly.\n'
                '- **GitHub link**: Is the GitHub link in the README? Rate as '
                '"bad" (missing), "good" (present but not prominent), or "great" '
                '(clearly visible). Explain briefly.'
            ),
            expected_output=(
                'A structured report in markdown format with:\n'
                '- A section for each criterion (README clarity, Input '
                'properties, Usability, Examples, GitHub link).\n'
                '- Each section includes a rating ("bad", "good", "great") and a '
                '1-2 sentence explanation.\n'
                '- A brief list of suggestions for improvement if applicable.\n'
                '- A brief overall summary (2-3 sentences) with suggestions for '
                'improvement.'
            ),
            agent=actor_quality_agent,
        )

        uniqueness_task = Task(
            description=(
                f'Evaluate the uniqueness of the Apify Actor "{actor_name}" '
                'compared to similar actors. '
                f'{PEDANTIC_MESSAGE if pedantic else ""}'
                'Assess the following criteria:\n'
                '- **Comparison**: Is the Actor unique compared to peers? Rate '
                'as "bad" (very similar), "good" (somewhat unique), or "great" '
                '(highly distinct). Explain briefly.\n'
                '- **Functionality**: Does it offer unique features? Rate as '
                '"bad" (none), "good" (some), or "great" (highly unique). Explain '
                'briefly.\n'
                '- **Selling points**: Are there standout selling points? Rate '
                'as "bad" (none), "good" (some), or "great" (multiple). Explain '
                'briefly.'
            ),
            expected_output=(
                'A structured report in markdown format with:\n'
                '- A section for each criterion (Comparison, Functionality, '
                'Selling points).\n'
                '- Each section includes a rating ("bad", "good", "great") and a '
                '1-2 sentence explanation.\n'
                '- A brief overall summary (2-3 sentences) highlighting unique '
                'aspects and improvement ideas.'
            ),
            agent=uniqueness_check_agent,
        )

        pricing_task = Task(
            description=(
                f'Analyze the pricing of the Apify Actor "{actor_name}" for '
                'competitiveness and sensibility. '
                f'{PEDANTIC_MESSAGE if pedantic else ""}'
                'Evaluate the following criteria:\n'
                '- **Competitiveness**: Is pricing competitive with similar '
                'Actors? Rate as "bad" (expensive), "good" (moderate), or "great" '
                '(highly competitive). Explain briefly.\n'
                '- **Sensibility**: Does the pricing align with functionality? '
                'Rate as "bad" (not sensible), "good" (somewhat sensible), or '
                '"great" (very sensible). Explain briefly.\n'
                '- **Transparency**: Are there hidden costs? Rate as "bad" '
                '(many), "good" (some), or "great" (none). Explain briefly.'
            ),
            expected_output=(
                'A structured report in markdown format with:\n'
                '- A section for each criterion (Competitiveness, Sensibility, '
                'Transparency).\n'
                '- Each section includes a rating ("bad", "good", "great") and a '
                '1-2 sentence explanation.\n'
                '- A brief list of suggestions for improvement if applicable.\n'
                '- A brief overall summary (2-3 sentences) with pricing '
                'improvement suggestions.'
            ),
            agent=pricing_check_agent,
        )

        final_task = Task(
            description=(
                f'Compile a final quality assessment for the Apify Actor '
                f'"{actor_name}". '
                'Include the Actor name and a brief summary of its purpose. '
                'Always Actor not Actor.'
                f'{PEDANTIC_MESSAGE if pedantic else ""}'
                'Summarize findings from previous tasks and assign an overall '
                'rating:\n'
                '- **Code quality**: Summarize code quality findings. Rate as '
                '"bad", "good", or "great". Explain in 1-2 sentences.\n'
                '- **Actor quality**: Summarize Actor quality findings. Rate as '
                '"bad", "good", or "great". Explain in 1-2 sentences.\n'
                '- **Uniqueness**: Summarize uniqueness findings. Rate as "bad", '
                '"good", or "great". Explain in 1-2 sentences.\n'
                '- **Pricing**: Summarize pricing findings. Rate as "bad", '
                '"good", or "great". Explain in 1-2 sentences.\n'
                '- **Overall**: Provide a final rating ("bad", "good", "great") '
                'with a 2-3 sentence justification.'
            ),
            expected_output=(
                'A concise final report in markdown format with:\n'
                '- A header section including the Actor Name and a brief Summary '
                'of what the Actor does (2-3 sentences).\n'
                '- A section for each category (Code quality, Actor quality, '
                'Uniqueness, Pricing, Suggestions, Overall).\n'
                '- Each section includes a rating ("bad", "good", "great") and a '
                '1-2 sentence explanation.\n'
                '- The Suggestions section provides a list of suggestions for improvement.\n'
                '- The Overall section provides a final rating and a 2-3 sentence summary.'
            ),
            context=[actor_quality_task, code_quality_task, pricing_task, uniqueness_task],
            agent=inspector_agent,
        )

        # Create a one-man crew
        # For more information, see https://docs.crewai.com/concepts/crews
        crew = Crew(
            agents=[
                actor_quality_agent,
                code_quality_agent,
                pricing_check_agent,
                uniqueness_check_agent,
            ],
            tasks=[final_task],
            manager_agent=inspector_agent,
        )

        # Kick off the crew and get the response
        Actor.log.info('Kicking off the crew...')
        crew_output = crew.kickoff()
        raw_response = crew_output.raw
        Actor.log.debug('Raw response: %s', raw_response)

        total_tokens = crew_output.token_usage.total_tokens
        Actor.log.debug('Total tokens used: %d', total_tokens)

        await Actor.push_data(
            {
                'actorId': actor_name,
                'response': raw_response,
            }
        )
        Actor.log.info('Pushed the data into the dataset!')
        await Actor.charge(event_name='task-completed', count=1)
        Actor.log.info('Charged for task completed')
