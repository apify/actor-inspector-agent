"""This module defines the main entry point for the Apify Actor.

Feel free to modify this file to suit your specific needs.

To build Apify Actors, utilize the Apify SDK toolkit, read more at the official documentation:
https://docs.apify.com/sdk/python
"""

from __future__ import annotations

import logging

from apify import Actor
from crewai import Crew, Process, Task

from src.agents import create_actor_inspector_agent
from src.agents2 import create_pricing_check_agent, create_uniqueness_check_agent
from src.ppe_utils import charge_for_actor_start

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
        # github_repo_url = actor_input.get('githubRepoUrl')
        model_name = actor_input.get('modelName', 'gpt-4o-mini')
        if debug := actor_input.get('debug', True):
            Actor.log.setLevel(logging.DEBUG)
            logger = logging.getLogger('apify')
            logger.setLevel(logging.DEBUG)
        if not actor_id:
            raise ValueError('Missing the "actorId" attribute in the input!')
        # if not github_repo_url:
        #     raise ValueError('Missing the "githubRepoUrl" attribute in the input!')

        await charge_for_actor_start()

        inspector_agent = create_actor_inspector_agent(model_name)
        # code_quality_agent = create_code_quality_agent(model_name, debug=debug)
        # actor_quality_agent = create_actor_quality_agent(model_name, debug=debug)

        # Create a one-man crew
        # For more information, see https://docs.crewai.com/concepts/crews
        crew = Crew(
            agents=[
                # code_quality_agent,
                # actor_quality_agent,
                # create_uniqueness_check_agent(llm_model_name=model_name, debug=debug)
                create_pricing_check_agent( llm_model_name=model_name, debug=debug)
            ],
            tasks=[
                Task(
                    description=(
                        # f'analyze me quality of this Apif Actor {actor_id} and also the quality of the Actor code the code of the Actor is here {github_repo_url}'
                        # f'Analyze whether {actor_id} is similar to any existing Apify Actors'
                        f'Compare Actor: {actor_id} pricing with other similar Apify Actors'
                    ),
                    expected_output='A helpful response to the user query.',
                    #output_pydantic=
                )
            ],
            manager_agent=inspector_agent,
            process=Process.hierarchical,
        )

        # Kick off the crew and get the response
        crew_output = crew.kickoff()
        raw_response = crew_output.raw
        Actor.log.debug(raw_response)
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
