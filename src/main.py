"""This module defines the main entry point for the Apify Actor.

Feel free to modify this file to suit your specific needs.

To build Apify Actors, utilize the Apify SDK toolkit, read more at the official documentation:
https://docs.apify.com/sdk/python
"""

from __future__ import annotations

import logging

from apify import Actor
from apify_client import ApifyClient
from crewai import Crew, Process, Task

from src.agents import create_actor_inspector_agent, create_code_quality_agent, create_actor_quality_agent
from src.agents2 import create_pricing_check_agent, create_uniqueness_check_agent
from src.models import FinalTaskOutput
from src.ppe_utils import charge_for_actor_start
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
        if (debug := actor_input.get('debug', True)):
            Actor.log.setLevel(logging.DEBUG)
            logger = logging.getLogger('apify')
            logger.setLevel(logging.DEBUG)
        if not actor_id:
            raise ValueError('Missing the "actorId" attribute in the input!')

        apify_client = ApifyClient(token=get_apify_token())
        build = get_actor_latest_build(apify_client, actor_id)
        github_repo_url = build.get('actVersion', {}).get('gitRepoUrl')

        if not github_repo_url:
            github_repo_url = "GITHUB REPO URL IS NOT PROVIDED, SKIP ALL CHEKS AND TOOLS THAT REQUIRE IT."
            code_quality_remark = "IF THE GITHUB REPO URL IS NOT PROVIDED, GRADE THE CODE QUALITY AS 'N/A'."
        else:
            code_quality_remark = ""


        print(github_repo_url)

        inspector_agent = create_actor_inspector_agent(model_name)
        code_quality_agent = create_code_quality_agent(model_name, debug=debug)
        actor_quality_agent = create_actor_quality_agent(model_name, debug=debug)
        uniqueness_check_agent = create_uniqueness_check_agent(model_name, debug=debug)
        pricing_check_agent = create_pricing_check_agent(model_name, debug=debug)
        code_quality_task = Task(
            description=(
                f'Perform a code quality check on the Apify Actor: {actor_id}. '
                f'The code can be found at the following GitHub repository URL: {github_repo_url}. '
                '!!! IF THE CODE URL IS NOT EXPLICITLY PROVIDED, DO NOT CALL ANY CODE RELATED TOOLS, DO NOT TRY TO COME UP WITH IT OR DO NOT USE ACTOR NAME AS A URL. '
                'JUST TELL THAT CODE CANNOT BE EVALUATED AND GRADE IT AS "N/A" !!!'
                'Report for these criteria: '
                '- Contains tests? Classify as bad if no tests, good if some tests are missing major functionality, great if most important functionality is tested. Provide a brief description explaining the rating, e.g., "Contains tests but only basic, majority of functionality was not tested." \n'
                '- Is linter enabled? Classify as bad if not enabled, good if partially enabled, great if fully enabled. Provide a brief description explaining the rating, e.g., "Linter is partially enabled, missing configurations for some files." \n'
                '- Are there any code smells? Classify as bad if many code smells, good if some code smells, great if no code smells. Provide a brief description explaining the rating, e.g., "Several instances of duplicate code found." \n'
                '- Are there any security vulnerabilities? Classify as bad if many vulnerabilities, good if some vulnerabilities, great if no vulnerabilities. Provide a brief description explaining the rating, e.g., "Multiple dependencies with known vulnerabilities." \n'
                '- Are there any performance issues visible in the code? Classify as bad if many issues, good if some issues, great if no issues. Provide a brief description explaining the rating, e.g., "Several inefficient loops detected." \n'
                '- Are there any code style issues? Classify as bad if many issues, good if some issues, great if no issues. Provide a brief description explaining the rating, e.g., "Inconsistent naming conventions used." \n'
                f'{code_quality_remark}'
            ),
            expected_output='A detailed report on the code quality, including any issues found and suggestions for improvement.',
            agent=code_quality_agent,
        )
        actor_quality_task = Task(
            description=(
                f'Perform an actor quality check on the Apify Actor {actor_id}. '
                f'The code can be found at the following GitHub repository URL: {github_repo_url}. '
                'Report for these criteria: '
                '- Is the README well-defined? Classify as bad if not well-defined, good if partially well-defined, great if fully well-defined. Provide a brief description explaining the rating, e.g., "README is partially well-defined, missing sections on usage examples." \n'
                '- Are the input properties well-defined and do they make sense? Classify as bad if not well-defined, good if partially well-defined, great if fully well-defined. Provide a brief description explaining the rating, e.g., "Input properties are partially well-defined, some properties lack descriptions." \n'
                '- Is the actor easy to follow and use for a real user from the README? Classify as bad if not easy to follow, good if somewhat easy to follow, great if very easy to follow. Provide a brief description explaining the rating, e.g., "README is somewhat easy to follow, but lacks detailed usage instructions." \n'
                '- Are use examples provided? Classify as bad if no examples, good if some examples, great if comprehensive examples. Provide a brief description explaining the rating, e.g., "README contains some examples, but they are not comprehensive." \n'
                '- Is open source (GitHub) repository link provided in the README? Classify as bad if no link, good if link is provided but not prominent, great if link is prominently provided. Provide a brief description explaining the rating, e.g., "GitHub repository link is provided but not prominently displayed." \n'
            ),
            expected_output='A detailed report on the actor quality, including any issues found and suggestions for improvement.',
            agent=actor_quality_agent,
        )
        uniqueness_task = Task(
            description=(
                f'Perform an actor uniqueness check on the Apify Actor {actor_id}. '
                f'The code can be found at the following GitHub repository URL: {github_repo_url}. '
                'Report for these criteria: '
                '- Is the actor unique compared to other similar actors? Classify as bad if very similar to others, good if somewhat similar, great if unique. Provide a brief description explaining the rating, e.g., "Actor has unique features not found in other similar actors." \n'
                '- Does the actor offer unique functionality? Classify as bad if no unique functionality, good if some unique functionality, great if highly unique functionality. Provide a brief description explaining the rating, e.g., "Actor offers unique data extraction methods not found in other actors." \n'
                '- Are there any unique selling points? Classify as bad if no unique selling points, good if some unique selling points, great if multiple unique selling points. Provide a brief description explaining the rating, e.g., "Actor has multiple unique selling points such as advanced data processing capabilities." \n'
            ),
            expected_output='A detailed report on the actor uniqueness, including any unique features and suggestions for improvement.',
            agent=uniqueness_check_agent,
        )
        pricing_task = Task(
            description=(
                f'Perform a pricing check on the Apify Actor {actor_id}. '
                f'The code can be found at the following GitHub repository URL: {github_repo_url}. '
                'Report for these criteria: '
                '- Is the pricing competitive compared to similar actors? Classify as bad if expensive, good if moderately priced, great if competitively priced. Provide a brief description explaining the rating, e.g., "Pricing is competitive compared to similar actors offering the same functionality." \n'
                '- Does the pricing model make sense for the functionality offered? Classify as bad if not sensible, good if somewhat sensible, great if very sensible. Provide a brief description explaining the rating, e.g., "Pricing model is very sensible given the advanced features offered by the actor." \n'
                '- Are there any hidden costs or fees? Classify as bad if many hidden costs, good if some hidden costs, great if no hidden costs. Provide a brief description explaining the rating, e.g., "No hidden costs, all fees are transparent and clearly stated." \n'
            ),
            expected_output='A detailed report on the actor pricing, including any issues found and suggestions for improvement.',
            agent=pricing_check_agent,
        )
        final_task = Task(
            description=(
                f'Perform a final overall inspection quality check on the Apify Actor {actor_id}. '
                f'The code can be found at the following GitHub repository URL: {github_repo_url}. '
                'Summarize the findings from the previous tasks and provide a final mark: '
                '- Code Quality: Summarize the findings and classify as bad, good, or great. Provide a brief description explaining the rating. \n'
                '- Actor Quality: Summarize the findings and classify as bad, good, or great. Provide a brief description explaining the rating. \n'
                '- Actor Uniqueness: Summarize the findings and classify as bad, good, or great. Provide a brief description explaining the rating. \n'
                '- Pricing: Summarize the findings and classify as bad, good, or great. Provide a brief description explaining the rating. \n'
                'Provide an overall final mark for the actor: bad, good, or great, with a brief description summarizing the overall quality.'
            ),
            expected_output='A final overall inspection report summarizing the findings from the previous tasks and providing a final mark for the actor.',
            context=[code_quality_task, actor_quality_task, uniqueness_task, pricing_task],
            #output_pydantic=FinalTaskOutput,
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
            tasks=[
                final_task
            ],
            manager_agent=inspector_agent,
            #process=Process.hierarchical,
        )

        # Kick off the crew and get the response
        Actor.log.info('Kicking off the crew...')
        crew_output = crew.kickoff()
        raw_response = crew_output.raw
        Actor.log.debug(raw_response)

        response = crew_output.pydantic

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

        """
        #response = crew_output.pydantic

        # Charge the user for the tokens used by the model
        total_tokens = crew_output.token_usage.total_tokens
        await charge_for_model_tokens(model_name, total_tokens)

        if not response or not raw_response:
            Actor.log.error('Failed to get a response from the agent!')
            await Actor.fail(status_message='Failed to get a response from the agent!')

        # Push results to the key-value store and dataset
        store = await Actor.open_key_value_store()
        await store.set_value('response.txt', raw_response)
        Actor.log.info('Saved the "response.txt" file into the key-value store!')

        await Actor.push_data(
            {
                'query': query,
                'response': raw_response,
                'structured_response': response.dict() if response else {},
            }
        )
        Actor.log.info('Pushed the data into the dataset!')
        """

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
