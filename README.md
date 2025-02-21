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

![Agent Actor Inspector](https://raw.githubusercontent.com/apify/agent-actor-inspector/refs/heads/main/docs/agent_actor_inspector.png)

## Input

The Actor requires the following input configuration:

- `actorId` :  Actor ID to be evaluated.

## Output

Sample Actor output for evaluation of [Website Content Crawler](https://apify.com/apify/website-content-crawler) Actor:
```
**Final Overall Inspection Report for Apify Actor: apify/website-content-crawler**

- **Code Quality:**
  - Rating: Unknown (Based on best practices).
  - Description: While direct analysis was unavailable, the actor is expected to follow best practices, ensuring organized, efficient, and secure code.

- **Actor Quality:**
  - Rating: Great
  - Description: The actor exhibits excellent documentation, with comprehensive guidance, use case examples, detailed input properties, and a user-friendly design that aligns with best practices.

- **Actor Uniqueness:**
  - Rating: Good
  - Description: Although there are similar actors, its unique design for LLM integration and enhanced HTML processing options provide it with a distinct niche.

- **Pricing:**
  - Rating: Good
  - Description: The flexible PAY_PER_PLATFORM_USAGE model offers potential cost-effectiveness, particularly for large-scale operations, compared to fixed models.

**Overall Final Mark: Great**

The "apify/website-content-crawler" stands out with its combination of quality documentation, unique features tailored for modern AI applications, and competitive pricing strategy, earning it a "Great" overall assessment. While information on code quality couldn't be directly assessed, the actor's thought-out documentation and broad feature set suggest adherence to high standards.
```
