# AI-Powered Customer Support & TAM Assistant

An internal tooling AI solution designed to assist Tier-1/Tier-2 Technical Support engineers with intelligent ticket triage and Technical Account Managers (TAMs) with automated account health briefs.

## Setup & Installation
1. Clone the repository and navigate to the project directory.
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables by copying `.env.example` to `.env` and adding your API credentials.

## Running the Evaluation Harness
Execute the automated evaluation test cases and generate the `eval_report.json` results file by running:
`python eval_harness.py`

## Design Note

### 1. Production Failure Scenarios

* **Incorrect citations:** The AI may sometimes refer to the wrong knowledge-base document. I handle this by validating the output and checking confidence. If the result is not reliable, the system falls back to a safer default response.

* **Invalid JSON:** LLM responses may occasionally have an incorrect format. Structured output validation and error handling are used to prevent these responses from breaking the application.

* **Outdated customer data:** Using old ticket history can lead to inaccurate summaries. Data is timestamped, and the latest customer context is fetched when processing a request.

### 2. Latency vs. Quality

The current implementation prioritizes response quality and accuracy over speed. Responses may take a few seconds depending on the processing involved.

If lower latency was required, I would use a smaller and faster model and pre-compute embeddings for the knowledge-base documents and customer summaries.

### 3. Data Sensitivity & PII

Support tickets may contain sensitive customer information. To reduce privacy risks, unnecessary personal information should be removed before sending data to external AI services.

Customer data should not be stored in plain-text logs, and API keys and other sensitive configuration values are kept in environment variables.

### 4. Scaling to 10× Volume

At 10× the current volume, synchronous processing and local file-based lookups could become bottlenecks.

For larger workloads, I would introduce an asynchronous message queue for ticket processing, move the data to an indexed/vector database for faster retrieval, and run the FastAPI service across multiple instances behind a load balancer.
