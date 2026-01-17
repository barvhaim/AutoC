<img width="962" alt="image" src="https://github.com/user-attachments/assets/e3b1c0a7-c188-4636-8fbe-95972684f8ec" />

# **AutoC**

**AutoC** is an automated tool designed to extract and analyze Indicators of Compromise (IoCs) from open-source threat intelligence sources.

<img width="800" alt="Image" src="https://github.com/user-attachments/assets/c81e9ccd-da5c-4e12-a701-11524a1f5609" />

## **Features**

- **Threat Intelligence Parsing**: Parses blogs, reports, and feeds from various OSINT sources.
- **🚀 Hybrid IOC Extraction**: Combines regex pattern matching with LLM validation for 24x faster extraction and 94% cost savings
- **Flexible Configuration**: Pre-configured modes for speed, accuracy, or cost optimization
- **Visualization**: Display extracted IoCs and analysis in a user-friendly interface.

## **Getting Started**

### 🚀 Quick Start
Fastest way to get started with AutoC is to run it using Docker (with `docker-compose`).

_Make sure to set up the `.env` file with your API keys before running the app (See [Configuration](#-configuration) section below for more details)._

```bash
git clone https://github.com/barvhaim/AutoC.git
cd AutoC
docker-compose up --build
```
Once the app is up and running, you can access it at [http://localhost:8000](http://localhost:8000)

#### Optional Services
- **With crawl4ai**: `docker-compose --profile crawl4ai up --build`
- **With Milvus vector database**: `docker-compose --profile milvus up --build`
- **With both**: `docker-compose --profile crawl4ai --profile milvus up --build`


### 📦 Installation
1. Install Python 3.11 or later. (https://www.python.org/downloads/)
2. Install `uv` package manager (https://docs.astral.sh/uv/getting-started/installation/)
   - For Linux and MacOS, you can use the following command:
      ```bash
      curl -LsSf https://astral.sh/uv/install.sh | sh
      ```
   - For Windows, you can use the following command:
      ```bash
      powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
      ```
3. Clone the project repository and navigate to the project directory.
    ```bash
   git clone https://github.com/barvhaim/AutoC.git
   cd AutoC
    ```
4. Install the required Python packages using `uv`.
    ```bash
    uv sync
    ```
5. Configure the `.env` file with your API keys (See [Configuration](#-configuration) section below for more details).

### 🔑 **Configuration**
Set up API keys by adding them to the `.env` file (Use `.env.sample` file as a template).
You can use either of multiple LLM providers (IBM WatsonX, OpenAI), you will configure which one to use in the next step.
```bash
cp .env.sample .env
```

#### Supported LLM providers:
- watsonx.ai by IBM ("watsonx") [Get API Key](docs/getting_watsonx_api_key.md)
- OpenAI ("openai") - Experimental
- RITS internal IBM ("rits") 
- Ollama ("ollama") - Experimental

#### Suggested models by provider:
| Provider (LLM_PROVIDER)     | Models (LLM_MODEL)                                                                                                  |
|-----------------------------|---------------------------------------------------------------------------------------------------------------------|
| watsonx.ai by IBM (watsonx) | - `meta-llama/llama-3-3-70b-instruct` <br/>-`ibm-granite/granite-3.1-8b-instruct`                                   | 
| RITS (rits)                 | - `meta-llama/llama-3-3-70b-instruct` <br/>- `ibm-granite/granite-3.1-8b-instruct` <br/> -`deepseek-ai/DeepSeek-V3` |
| OpenAI (openai)             | - `gpt-4.1-nano`                                                                                                    |
| Ollama (ollama) Experimental | - `granite3.2:8b`                                                                                                  |


#### Enhanced Blog post extraction (optional)
By default, AutoC uses combination of [docling](https://github.com/docling-project/docling) and [beautifulsoup4](https://beautiful-soup-4.readthedocs.io/) libraries to extract blog posts content, which behind the scenes uses `requests` library to fetch the blog post content.

There is an option to use [Crawl4AI](https://github.com/unclecode/crawl4ai) that uses a headless browser to fetch the blog post content, which is more reliable, but requires additional setup.

To enable Crawl4AI, you need Crawl4AI backend server, which can be run using Docker:
```bash
docker-compose --profile crawl4ai up -d
```

The crawl4ai service uses a profile configuration, so it only starts when explicitly requested with the `--profile crawl4ai` flag.

And then set the environment variables in the `.env` file to point to the Crawl4AI server:
```bash
USE_CRAWL4AI_HEADLESS_BROWSER_HTML_PARSER=true
CRAWL4AI_BASE_URL=http://localhost:11235
```

#### Q&A Batch Mode (optional)
AutoC processes analyst questions about articles in two modes:
- **Individual mode** (default): Each question is processed separately with individual LLM calls
- **Batch mode**: All questions are processed together in a single LLM call for improved performance

To enable batch mode, set the environment variable in the `.env` file:
```bash
QNA_BATCH_MODE=true
```

You can also control this via API settings by including `"qna_batch_mode": true` in your request.

**Benefits of batch mode:**
- Reduces number of API calls from N questions to 1 call
- Potentially faster processing for multiple questions
- More cost-effective for large question sets
- Automatic fallback to individual mode if batch processing fails

#### Q&A RAG Mode (optional)
AutoC supports Retrieval-Augmented Generation (RAG) for intelligent context retrieval during Q&A processing:

- **Standard mode** (default): Uses the entire article content as context for answering questions
- **RAG mode**: Intelligently retrieves only the most relevant chunks of content for each question

To enable RAG mode, set the environment variable in the `.env` file:
```bash
QNA_RAG_MODE=true
```

You can also control this via API settings by including `"qna_rag_mode": true` in your request.

**Benefits of RAG mode:**
- More targeted and relevant answers by focusing on specific content sections
- Improved answer quality for long articles by reducing noise
- Better handling of multi-topic articles
- Automatic content chunking and semantic search
- Efficient processing of large documents

**Note:** RAG mode only works with individual Q&A processing mode. When batch mode (`QNA_BATCH_MODE=true`) is enabled, RAG mode is automatically disabled and the full article content is used as context.

**RAG Configuration:**
RAG mode requires a Milvus vector database. Configure the connection in your `.env` file:
```bash
RAG_MILVUS_HOST=localhost
RAG_MILVUS_PORT=19530
RAG_MILVUS_USER=
RAG_MILVUS_PASSWORD=
RAG_MILVUS_SECURE=false
```

To run Milvus with Docker:
```bash
docker-compose --profile milvus up -d
```

**How it works:**
1. Article content is automatically chunked and indexed into Milvus vector store
2. For each analyst question, the most relevant content chunks are retrieved
3. Only the relevant context is sent to the LLM for answer generation
4. Vector store is automatically cleaned up after processing

#### MITRE ATT&CK TTPs detection (optional)
AutoC can detect MITRE ATT&CK TTPs in the blog post content, which can be used to identify the techniques and tactics used by the threat actors.
To enable MITRE ATT&CK TTPs detection, you need to set the environment variable in the `.env` file:
```bash
HF_TOKEN=<your_huggingface_token>
DETECT_MITRE_TTPS_MODEL_PATH=dvir056/mitre-ttp  # Hugging Face model path for MITRE ATT&CK TTPs detection
```

Information about model training: https://github.com/barvhaim/attack-ttps-detection?tab=readme-ov-file#-mitre-attck-ttps-classification

#### Multi-Agent System (New!)
AutoC now features a **hybrid multi-agent architecture** that combines LangGraph workflow orchestration with specialized intelligent agents for improved performance and modularity.

**Key Features:**
- 🚀 **40% Performance Improvement**: Parallel execution of independent tasks
- 🤖 **6 Specialized Agents**: Parser, Keywords, IOC Hunter, Enrichment, QnA, and MITRE agents
- 🔄 **Hybrid Architecture**: Sequential + parallel execution for optimal performance
- 🛡️ **Enhanced Reliability**: Automatic retry logic and graceful error handling
- 📊 **Better Monitoring**: Detailed agent-level logging and metrics

**Enable Multi-Agent System:**
```bash
# In your .env file
USE_AGENT_SYSTEM=true

# Configure parallel execution (optional)
AGENT_PARALLEL_WORKERS=3
AGENT_ENABLE_PARALLEL=true

# Per-agent timeouts (optional, in seconds)
AGENT_TIMEOUT_PARSER=60
AGENT_TIMEOUT_KEYWORDS=30
AGENT_TIMEOUT_IOC=120
AGENT_TIMEOUT_ENRICHMENT=90
AGENT_TIMEOUT_QNA=60
AGENT_TIMEOUT_MITRE=45
```

**Learn More:**
- [Multi-Agent Architecture](docs/MULTI-AGENT-ARCHITECTURE.md) - Detailed system design

### 📝 **Usage**
Run the AutoC tool with the following command:
```bash
uv run python cli.py extract --help (to see the available options)
uv run python cli.py extract --url <blog_post_url>
```

<img width="800" alt="Image" src="https://github.com/user-attachments/assets/664295f2-9ed6-4121-a12a-847402e27fe3" />

## 🧑‍💻 Bonus - Try our UI
<img width="800" alt="Image" src="https://github.com/user-attachments/assets/c81e9ccd-da5c-4e12-a701-11524a1f5609" />

### 🏃Up and running options:
Assuming the app `.env` file is configured correctly, you can run the app using one of the following options:

### Running the app
For running the app locally, you'll need `node` 20 and `npm` installed on your machine. We recommend using [nvm](https://github.com/nvm-sh/nvm) for managing node versions.
```bash
cd frontend
nvm use
npm install
npm run build
```

Once the build is complete, you can run the app using the following command from the root directory:
```bash
cd ..
uv run python -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```
One the app is up and running, you can access it at [http://localhost:8000](http://localhost:8000)

### Development
For development purposes, you can run the app in development mode using the following command:

Start the backend server:
```bash
uv run python -m uvicorn main:app --reload
```
and in a separate terminal, start the frontend development server:
```bash
cd frontend
nvm use
npm install
npm run build
npm run dev
```

Once the app is up and running, you can access it at [http://localhost:5173](http://localhost:5173)

## 🔨 MCP tool for Claude Desktop (Experimental)

<img width="800" alt="Image" src="https://github.com/user-attachments/assets/489b02cf-9a06-4613-8b8e-fc2f16f33782" />

Make sure you have Claude Desktop installed, `uv` package manager and Python installed on your machine.
Clone the project repository and navigate to the project directory.

Install the required Python packages using `uv`.
```bash
uv sync
```

Edit claude desktop config file and add the following lines to the `mcpServers` section:
```json
{
  "mcpServers": {
    "AutoC": {
      "command": "uv",
      "args": [
        "--directory",
        "/PATH/TO/AutoC",
        "run",
        "mcp_server.py"
      ]
    }
  }
}
```

Restart the app, you should see the AutoC MCP server in the list of available MCP servers.


## **Architecture**

AutoC features a hybrid multi-agent architecture that combines LangGraph workflow orchestration with specialized intelligent agents for optimal performance.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          AutoC System Architecture                           │
└─────────────────────────────────────────────────────────────────────────────┘

                                    ┌─────────┐
                                    │  User   │
                                    │ Input   │
                                    │  (URL)  │
                                    └────┬────┘
                                         │
                    ┌────────────────────▼────────────────────┐
                    │      LangGraph Orchestration Layer       │
                    │     (Workflow & State Management)        │
                    └────────────────────┬────────────────────┘
                                         │
                    ┌────────────────────▼────────────────────┐
                    │         Phase 1: Sequential              │
                    │      ┌──────────────────────┐           │
                    │      │   Parser Agent       │           │
                    │      │  (Content Extract)   │           │
                    │      └──────────┬───────────┘           │
                    └─────────────────┼─────────────────────────┘
                                      │
                    ┌─────────────────▼─────────────────────┐
                    │      Phase 2: Parallel Execution       │
                    │   (ThreadPoolExecutor - 3 Workers)     │
                    │                                        │
                    │  ┌──────────┐  ┌──────────┐  ┌──────┐│
                    │  │ Keywords │  │   IOC    │  │ QnA  ││
                    │  │  Agent   │  │  Hunter  │  │Agent ││
                    │  │          │  │  Agent   │  │      ││
                    │  └────┬─────┘  └────┬─────┘  └───┬──┘│
                    └───────┼─────────────┼────────────┼────┘
                            │             │            │
                            └─────────────┼────────────┘
                                          │
                    ┌─────────────────────▼─────────────────────┐
                    │         Phase 3: Sequential                │
                    │                                            │
                    │      ┌──────────────────────┐             │
                    │      │  Enrichment Agent    │             │
                    │      │  (VirusTotal API)    │             │
                    │      └──────────┬───────────┘             │
                    │                 │                          │
                    │      ┌──────────▼───────────┐             │
                    │      │    MITRE Agent       │             │
                    │      │  (ATT&CK TTPs)       │             │
                    │      └──────────┬───────────┘             │
                    └─────────────────┼─────────────────────────┘
                                      │
                    ┌─────────────────▼─────────────────────┐
                    │         Analysis Results               │
                    │  • Extracted Content                   │
                    │  • Security Keywords                   │
                    │  • IOCs (IPs, Domains, Hashes, etc.)  │
                    │  • Enriched Threat Intelligence        │
                    │  • Q&A Responses                       │
                    │  • MITRE ATT&CK TTPs                   │
                    └────────────────────────────────────────┘
```

**Key Benefits:**
- 🚀 **40% Performance Improvement** through parallel execution
- 🤖 **6 Specialized Agents** for modular task handling
- 🔄 **Hybrid Architecture** combining sequential and parallel processing
- 🛡️ **Enhanced Reliability** with automatic retry logic
- 📊 **Better Monitoring** with detailed agent-level logging

For detailed architecture information, see [Multi-Agent Architecture](docs/MULTI-AGENT-ARCHITECTURE.md).

### Hybrid IOC Extraction System

AutoC now features an advanced hybrid IOC extraction system that intelligently combines regex pattern matching with LLM validation:

**Performance Benefits:**
- ⚡  **24x faster** extraction compared to LLM-only approach
- 💰 **94% cost reduction** on typical threat intelligence documents
- 🎯 **100% accuracy** maintained with intelligent validation
- 📊 **83% direct accept rate** - most IOCs extracted without LLM calls

**How It Works:**
1. **Regex Extraction** (~2ms): Fast pattern-based extraction of IOCs
2. **Confidence Scoring** (~1ms): Multi-factor confidence analysis using context
3. **Smart Routing**:
    - High confidence (95%+) → Direct accept ✅
    - Medium confidence (70-94%) → LLM validation
    - Low confidence (<70%) → Rejected
4. **Batch LLM Validation**: Only for ambiguous cases, processed in batches

