# Actor Inspector Agent

[![Agent Actor Inspector](https://apify.com/actor-badge?actor=jakub.kopecky/actor-inspector-agent)](https://apify.com/jakub.kopecky/actor-inspector-agent)
[![GitHub Repo stars](https://img.shields.io/github/stars/apify/actor-inspector-agent)](https://github.com/apify/actor-inspector-agent/stargazers)

The **Actor Inspector Agent** is designed to evaluate and analyze other Apify Actors.
It provides detailed reports on code quality, documentation, uniqueness, and pricing competitiveness, helping developers optimize their Actors and users choose the best tools for their needs.

This Agent is built using [CrewAI](https://docs.crewai.com/) and [Apify SDK](https://docs.apify.com/sdk/python) and is using modern and flexible pricing model for AI Agents [Pay Per Event](https://docs.apify.com/sdk/js/docs/next/guides/pay-per-event).

## 🎯 Features

- 🧪 **Code quality**: Evaluates tests, linting, security, performance, and code style
- 📚 **Documentation**: Reviews readme clarity, input schema, examples, and GitHub presence
- 💫 **Uniqueness**: Compares features with similar actors to assess distinctiveness
- 💰 **Pricing**: Analyzes price competitiveness and model transparency
- 🚧 **Actor run** _(Coming soon)_: Tests actor execution and generates performance report

## 🔄 How it works?

1. 📥 **Input**
   - Actor name (e.g., `apify/instagram-scraper`)
   - AI model selection (`gpt-4o`, `gpt-4o-mini`, `o3-mini`)
   - _Optional_ debug mode

2. 🤖 **Processing with CrewAI**
   - Uses specialized AI agents working as a team:
     - Code quality specialist: Reviews source code and tests
     - Documentation expert: Analyzes readme and input schema
     - Apify Store analyst: Evaluates pricing and uniqueness
   - Each agent focuses on their expertise while collaborating for comprehensive analysis

3. 📤 **Output**
   - Generates detailed markdown report
   - Includes ratings and suggestions for each category
   - Automatically saves to Apify dataset

### 💰 Pricing

This Actor uses the [Pay Per Event](https://docs.apify.com/sdk/js/docs/next/guides/pay-per-event) (PPE) model for flexible, usage-based pricing. It currently charges for Actor start and a flat fee per task completion.

| Event                  | Price (USD) |
|------------------------|-------------|
| Actor start            | $0.05       |
| Task Completion        | $0.95       |

### Input Example

```json
{
  "actorName": "apify/instagram-scraper",
  "modelName": "gpt-4o-mini",
  "debug": false
}
```

### Output Example

A sample report might look like this (stored in the dataset):

```markdown
**Final Overall Inspection Report for Apify Actor: apify/website-content-crawler**

- **Code quality:**
  - Rating: Unknown (Based on best practices).
  - Description: While direct analysis was unavailable, the actor is expected to follow best practices, ensuring organized, efficient, and secure code.

- **Actor quality:**
  - Rating: Great
  - Description: The actor exhibits excellent documentation, with comprehensive guidance, use case examples, detailed input properties, and a user-friendly design that aligns with best practices.

- **Actor uniqueness:**
  - Rating: Good
  - Description: Although there are similar actors, its unique design for LLM integration and enhanced HTML processing options provide it with a distinct niche.

- **Pricing:**
  - Rating: Good
  - Description: The flexible PAY_PER_PLATFORM_USAGE model offers potential cost-effectiveness, particularly for large-scale operations, compared to fixed models.

**Overall Final Mark: Great**

The "apify/website-content-crawler" stands out with its combination of quality documentation, unique features tailored for modern AI applications, and competitive pricing strategy, earning it a "Great" overall assessment. While information on code quality couldn't be directly assessed, the actor's thought-out documentation and broad feature set suggest adherence to high standards.
```

Dataset output:
```json
{
  "actorId": "apify/website-content-crawler",
  "response": "...markdown report content..."
}
```

## ✨ Why Use Agent Actor Inspector?

- **Developer insights**: Identify areas to improve your Actor’s code, docs, or pricing.
- **User decision-making**: Compare Actors to find the best fit for your needs.
- **Automation**: Streamlines Actor evaluation with AI-driven analysis.
- **Scalability**: Analyze multiple Actors by running the Inspector in parallel.

## 🔧 Technical highlights

- **Built with Apify SDK**: Ensures seamless integration with the Apify platform.
- **CrewAI powered**: Uses multi-agent workflows for thorough, modular analysis.
- **GitHub integration**: Pulls source code from GitHub when available for deeper code quality checks.
- **Flexible tools**: Tools to fetch README, input schemas, pricing information, and related Actors.

## 🤖 Under the hood with [CrewAI](https://docs.crewai.com/)

This Actor uses CrewAI to orchestrate a team of specialized AI agents that work together to analyze Apify Actors:

### 👥 The crew

1. **Code quality specialist**
   ```python
   goal = 'Deliver precise evaluation of code quality, focusing on tests, linting, code smells, security, performance, and style'
   tools = [...]  # Fetches and analyzes source code
   ```

2. **Documentation expert**
   ```python
   goal = 'Evaluate documentation completeness, clarity, and usefulness for potential users'
   tools = [...]  # Analyzes readme and input schema
   ```

3. **Pricing expert**
   ```python
   goal = 'Analyze pricing with respect to other Actors'
   tools = [...]  # Analyzes competition
   ```

#### 🔄 Workflow

1. The main process creates a crew of agents, each with:
   - Specific role and expertise
   - Defined goal and backstory
   - Access to relevant tools
   - Selected LLM model

2. Agents work sequentially to:
   - Gather required information using their tools
   - Analyze data within their domain
   - Provide structured evaluations
   - Pass insights to other agents when needed

3. Results are combined into a comprehensive markdown report with:
   - Detailed analysis per category
   - Clear ratings (great/good/bad)
   - Actionable improvement suggestions

#### 🛠️ Tools

Each agent has access to specialized tools that:
- Fetch actor source code and analyze its structure
- Retrieve documentation and readme content
- Get pricing information and find similar actors
- Process and structure the gathered data

The CrewAI framework ensures collaboration between agents while maintaining focus on their specific areas of expertise.


## 📖 Learn more

- [Apify Platform](https://apify.com)
- [Apify SDK Documentation](https://docs.apify.com/sdk/python)
- [CrewAI Documentation](https://docs.crewai.com)
- [What are AI Agents?](https://blog.apify.com/what-are-ai-agents/)
- [AI agent architecture](https://blog.apify.com/ai-agent-architecture)

## 🚀 Get started

Evaluate your favorite Apify Actors today and unlock insights to build or choose better tools! 🤖🔍

## 🌐 Open source

This Actor is open source, hosted on [GitHub](https://github.com/apify/agent-actor-inspector).

Are you missing any features?  Open an issue here or [create a pull request](https://github.com/apify/agent-actor-inspector/pulls).
