# Agent Actor Inspector

[![Agent Actor Inspector](https://apify.com/actor-badge?actor=jakub.kopecky/agent-actor-inspector)](https://apify.com/jakub.kopecky/agent-actor-inspector)

Agent Actor Inspector is an Apify Actor designed to evaluate and rate other Apify Actors based on criteria such as documentation quality, input clarity, code standards, functionality, performance, and uniqueness.

## Features

- **README** – Is it well-written and properly documented?
- **Input description** – Is it clear and well-defined?
- **Examples** – Are relevant examples provided?
- **Pricing/Pricing model** – Is it **PPE, PPR,** or usage-based?
- **Open-source** – Is the code publicly available?
- **Code quality** – Is the implementation clean and maintainable?
- **Functionality** – Does the Agent perform as expected?
- **Run-time** – Does it take forever for the Agent to finish a task?
- **Uniqueness** - Does it duplicate current Actors?

## Use cases

- **Developer feedback**: Provides actionable insights for developers to enhance their Actors.
- **Quality assurance**: Helps maintain a high standard of Actors within the Apify platform.
- **User guidance**: Assists users in selecting well-documented and reliable Actors for their projects.

## How to use Agent Actor Inspector

1. **Configure input**: Provide the `actorId` array in the input configuration.
2. **Run**: Execute the Actor to start the evaluation process.
3. **Review results**: Once completed, access the output to review the evaluation summaries.

## How does Agent Actor Inspector works?

- Initializes agents
- Sets up tasks to:
  - Check code quality (tests, linter, code smells, security, performance, style).
  - Check actor quality (README content, input definitions, usability, examples, repository link).
  - Check uniqueness (distinctiveness and unique features).
  - Check pricing (competitiveness, pricing model, hidden costs).
- Aggregates results from all tasks to produce a final quality report.

![Agent Actor Inspector](https://raw.githubusercontent.com/apify/agent-actor-inspector/refs/heads/master/docs/agent_actor_inspector.png)

## Input

The Actor requires the following input configuration:

- `actorId` :  Actor ID to be evaluated.
