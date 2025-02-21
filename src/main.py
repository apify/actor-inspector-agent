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

        if not github_repo_url:
            github_repo_url = 'GITHUB REPO URL IS NOT PROVIDED, SKIP ALL CHEKS AND TOOLS THAT REQUIRE IT.'
            code_quality_remark = "IF THE GITHUB REPO URL IS NOT PROVIDED, GRADE THE CODE QUALITY AS 'N/A'."
        else:
            code_quality_remark = ''

        Actor.log.debug('Github repo URL: %s', github_repo_url)

        inspector_agent = create_actor_inspector_agent(model_name)
        code_quality_agent = create_code_quality_agent(model_name, debug=debug)
        actor_quality_agent = create_actor_quality_agent(model_name, debug=debug)
        uniqueness_check_agent = create_uniqueness_check_agent(model_name, debug=debug)
        pricing_check_agent = create_pricing_check_agent(model_name, debug=debug)
        code_quality_task = Task(
            description=(
                f'Perform a code quality check on the Apify Actor: {actor_id}. '
                f'The code can be found at the following GitHub repository URL: {github_repo_url}. '
                '!!! IF THE CODE URL IS NOT EXPLICITLY PROVIDED, DO NOT CALL ANY CODE RELATED'
                ' TOOLS, DO NOT TRY TO COME UP WITH IT OR DO NOT USE ACTOR NAME AS A URL. '
                'JUST TELL THAT CODE CANNOT BE EVALUATED AND GRADE IT AS "N/A" !!!'
                'Report for these criteria: '
                '- Contains tests? Classify as bad if no tests, good if some tests are missing '
                'major functionality, great if most important functionality is tested. '
                'Provide a brief description explaining the rating, '
                'e.g., "Contains tests but only basic, majority of functionality was not tested." \n'
                '- Is linter enabled? Classify as bad if not enabled, good if partially '
                'enabled, great if fully enabled. Provide a brief description explaining the '
                'rating, e.g., "Linter is partially enabled, missing configurations for some files." \n'
                '- Are there any code smells? Classify as bad if many code smells, good '
                'if some code smells, great if no code smells. Provide a brief description '
                'explaining the rating, e.g., "Several instances of duplicate code found." \n'
                '- Are there any security vulnerabilities? Classify as bad if many '
                'vulnerabilities, good if some vulnerabilities, great if no vulnerabilities. '
                'Provide a brief description explaining the rating, e.g., '
                '"Multiple dependencies with known vulnerabilities." \n'
                '- Are there any performance issues visible in the code? '
                'Classify as bad if many issues, good if some issues, great if no issues. '
                'Provide a brief description explaining the rating, e.g., '
                '"Several inefficient loops detected." \n'
                '- Are there any code style issues? Classify as bad if many issues, '
                'good if some issues, great if no issues. Provide a brief description '
                'explaining the rating, e.g., "Inconsistent naming conventions used." \n'
                f'{code_quality_remark}'
            ),
            expected_output=(
                'A detailed report on the code quality, including any issues found and suggestions for improvement.'
            ),
            agent=code_quality_agent,
        )
        actor_quality_task = Task(
            description=(
                f'Perform an actor quality check on the Apify Actor {actor_id}. '
                f'The code is at: {github_repo_url}. Report for these criteria:\n'
                '- Is the README well-defined? Classify as bad if not well-defined, '
                'good if partially well-defined, great if fully well-defined. '
                'Explain the rating, e.g., "README is partially well-defined, '
                'missing usage examples."\n'
                '- Are input properties well-defined and sensible? Classify as bad '
                'if not well-defined, good if partially well-defined, great if '
                'fully well-defined. Explain the rating, e.g., "Input properties '
                'are partially well-defined, some lack descriptions."\n'
                '- Is the actor easy to follow and use from the README? Classify as '
                'bad if not easy, good if somewhat easy, great if very easy. Explain '
                'the rating, e.g., "README is somewhat easy to follow, but lacks '
                'detailed usage instructions."\n'
                '- Are use examples provided? Classify as bad if none, good if some, '
                'great if comprehensive. Explain the rating, e.g., "README has some '
                'examples, but they are not comprehensive."\n'
                '- Is the GitHub link provided in the README? Classify as bad if no '
                'link, good if provided but not prominent, great if prominent. '
                'Explain the rating, e.g., "GitHub link is provided but not prominent."\n'
            ),
            expected_output='A detailed report on the actor quality, including issues '
            'found and suggestions for improvement.',
            agent=actor_quality_agent,
        )
        uniqueness_task = Task(
            description=(
                f'Perform an actor uniqueness check on the Apify Actor {actor_id}. '
                f'The code is at: {github_repo_url}. Report for these criteria:\n'
                '- Is the actor unique compared to similar actors? Classify as bad '
                'if very similar, good if somewhat similar, great if unique. Explain '
                'the rating, e.g., "Actor has unique features not found in others."\n'
                '- Does the actor offer unique functionality? Classify as bad if none, '
                'good if some, great if highly unique. Explain the rating, e.g., '
                '"Actor offers unique data extraction methods not found elsewhere."\n'
                '- Are there unique selling points? Classify as bad if none, good if '
                'some, great if multiple. Explain the rating, e.g., "Actor has multiple '
                'unique selling points like advanced data processing."\n'
            ),
            expected_output='A detailed report on actor uniqueness, including unique '
            'features and improvement suggestions.',
            agent=uniqueness_check_agent,
        )

        pricing_task = Task(
            description=(
                f'Perform a pricing check on the Apify Actor {actor_id}. '
                f'The code is at: {github_repo_url}. Report for these criteria:\n'
                '- Is pricing competitive compared to similar actors? Classify as bad '
                'if expensive, good if moderate, great if competitive. Explain the '
                'rating, e.g., "Pricing is competitive for the functionality offered."\n'
                '- Does the pricing model make sense for the functionality? Classify '
                'as bad if not sensible, good if somewhat sensible, great if very '
                'sensible. Explain the rating, e.g., "Pricing is very sensible given '
                'the advanced features."\n'
                '- Are there hidden costs or fees? Classify as bad if many, good if '
                'some, great if none. Explain the rating, e.g., "No hidden costs, all '
                'fees are transparent."\n'
            ),
            expected_output='A detailed report on actor pricing, including issues found and improvement suggestions.',
            agent=pricing_check_agent,
        )

        final_task = Task(
            description=(
                f'Perform a final quality check on the Apify Actor {actor_id}. '
                f'The code is at: {github_repo_url}. Summarize previous task findings '
                'and provide a final mark:\n'
                '- Code Quality: Summarize findings and classify as bad, good, or '
                'great. Explain the rating.\n'
                '- Actor Quality: Summarize findings and classify as bad, good, or '
                'great. Explain the rating.\n'
                '- Actor Uniqueness: Summarize findings and classify as bad, good, '
                'or great. Explain the rating.\n'
                '- Pricing: Summarize findings and classify as bad, good, or great. '
                'Explain the rating.\n'
                'Provide an overall mark: bad, good, or great, with a brief summary.'
            ),
            expected_output='A final report summarizing previous task findings and '
            'providing an overall mark for the actor.',
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
