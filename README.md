# Agent Actor Inspector 🕵️‍♂️✨

[![Agent Actor Inspector](https://apify.com/actor-badge?actor=jakub.kopecky/agent-actor-inspector)](https://apify.com/jakub.kopecky/agent-actor-inspector)
[![GitHub Repo stars](https://img.shields.io/github/stars/apify/agent-actor-inspector)](https://github.com/apify/agent-actor-inspector/stargazers)

The **Agent Actor Inspector** is an Apify AI Actor designed to evaluate and analyze other Apify Actors. It provides detailed reports on code quality, documentation, uniqueness, and pricing competitiveness, helping developers optimize their Actors and users choose the best tools for their needs.

## 🌟 What is Agent Actor Inspector?

This Actor is built to:

- **Analyze Apify Actors**: Assesses code quality, documentation clarity, uniqueness, and pricing for any specified Actor.
- **Generate Detailed Reports**: Produces structured markdown reports summarizing findings with clear ratings and actionable suggestions.
- **Leverage AI**: Uses OpenAI models (e.g., `gpt-4o`, `gpt-4o-mini`, or reasoning models like `o3-mini`) for intelligent analysis.
- **Push Results**: Stores the assessment in Apify’s dataset for easy access and review.

---

## 🎯 Features

- **Code Quality Evaluation**: Checks for tests, linting, security, performance, and style consistency.
- **Documentation Assessment**: Reviews README clarity, input properties, usability, examples, and GitHub visibility.
- **Uniqueness Check**: Compares functionality against similar Actors to determine distinctiveness.
- **Pricing Analysis**: Evaluates competitiveness and transparency of pricing models.
- **Customizable AI Models**: Choose between `gpt-4o`, `gpt-4o-mini`, or `o3-mini` for analysis speed and depth.

---

## 📈 How It Works

1. **Input**: Provide the Actor name (e.g., `apify/instagram-scraper`), select an AI model, and optionally enable debug mode.
2. **Processing**: The Actor fetches Actor details, source code (if available), README, pricing info, and related Actors, then analyzes them using specialized AI agents.
3. **Output**: Generates a markdown report summarizing findings across all categories, pushed to the Apify dataset.

### 💰 Pricing

This Actor uses the [Pay Per Event](https://docs.apify.com/sdk/js/docs/next/guides/pay-per-event) (PPE) model for flexible, usage-based pricing. It currently charges a flat fee per task completion.

| Event                  | Price (USD) |
|------------------------|-------------|
| Task Completion        | $1          |

Future updates may include token-based pricing for AI model usage (e.g., per 100 tokens), as hinted in `ppe_utils.py`.

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

Dataset output:
```json
{
  "actorId": "apify/website-content-crawler",
  "response": "...markdown report content..."
}
```

---

## ✨ Why Use Agent Actor Inspector?

- **Developer Insights**: Identify areas to improve your Actor’s code, docs, or pricing.
- **User Decision-Making**: Compare Actors to find the best fit for your needs.
- **Automation**: Streamlines Actor evaluation with AI-driven analysis.
- **Scalability**: Analyze multiple Actors by running the Inspector in parallel.

---

## 🔧 Technical Highlights

- **Built with Apify SDK**: Ensures seamless integration with the Apify platform.
- **CrewAI Powered**: Uses multi-agent workflows for thorough, modular analysis.
- **GitHub Integration**: Pulls source code from GitHub when available for deeper code quality checks.
- **Flexible Tools**: Custom tools fetch READMEs, input schemas, pricing info, and related Actors.

---

## 📖 Learn More

- [Apify Platform](https://apify.com)
- [Apify SDK Documentation](https://docs.apify.com/sdk/python)
- [CrewAI Documentation](https://docs.crewai.com)

---

## 🚀 Get Started

Evaluate your favorite Apify Actors today and unlock insights to build or choose better tools! 🤖🔍

---

🌐 Open source

This Actor is open source, hosted on [GitHub](https://github.com/apify/agent-actor-inspector).
