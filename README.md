<img width="962" alt="image" src="https://github.com/user-attachments/assets/e3b1c0a7-c188-4636-8fbe-95972684f8ec" />

# **AutoC**

**AutoC** is an automated tool designed to extract and analyze Indicators of Compromise (IoCs) from open-source threat intelligence sources.

## **Features**

- **Threat Intelligence Parsing**: Parses blogs, reports, and feeds from various OSINT sources.
- **IoC Extraction**: Automatically extracts IoCs such as IP addresses, domains, file hashes, and more.
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
Set up API keys by adding them to the `.env` file (Use `.env.example` file as a template).
You can use either of multiple LLM providers (IBM WatsonX, OpenAI), you will configure which one to use in the next step.
```bash
cp .env.example .env
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
| OpenAI (openai) Experimental             | - `gpt-4o`                                                                                                                  |
| Ollama (ollama) Experimental | - `granite3.2:8b`                                                                                                  |

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
