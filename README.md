<img width="962" alt="image" src="https://github.com/user-attachments/assets/e3b1c0a7-c188-4636-8fbe-95972684f8ec" />

# **AutoC**

**AutoC** is an automated tool designed to extract and analyze Indicators of Compromise (IoCs) from open-source threat intelligence sources.

## **Features**

- **Threat Intelligence Parsing**: Parses blogs, reports, and feeds from various OSINT sources.
- **IoC Extraction**: Automatically extracts IoCs such as IP addresses, domains, file hashes, and more.
- **Visualization**: Display extracted IoCs and analysis in a user-friendly interface. (Experimental)

## **Getting Started**

### 📦 Installation

1. Install Python 3.11 or later. (https://www.python.org/downloads/)
2. Clone the project repository and navigate to the project directory.
    ```bash
   git clone https://github.com/barvhaim/AutoC.git
   cd AutoC
    ```
3. Install the required Python packages using pip.
    ```bash
   pip install -r requirements.txt
    ```
4. Set up API keys by adding them to the `.env` file (Use `.env.example` file as a template).
   You can use either of multiple LLM providers (IBM WatsonX, OpenAI), you will configure which one to use in the next step.
    ```bash
   cp .env.example .env
    ```

### 🔑 **Configuration**
Supported LLM providers:
- RITS ("rits")
- WatsonX ("watsonx") [Get API Key](docs/getting_watsonx_api_key.md)
- OpenAI ("openai") - Not tested yet

### 📝 **Usage**
Run the AutoC tool with the following command:
```bash
python cli.py extract --help (to see the available options)
python cli.py extract --url <blog_post_url>
```

<img width="800" alt="Image" src="https://github.com/user-attachments/assets/664295f2-9ed6-4121-a12a-847402e27fe3" />

## 🚀 Bonus - Try our UI (Experimental)
<img width="801" alt="Image" src="https://github.com/user-attachments/assets/aedf3614-78ef-438e-8db5-e7398f88fc6c" />

### 🏃Up and running options:
Assuming the app `.env` file is configured correctly, you can run the app using one of the following options:

#### Docker (Recommended)
```bash
docker-compose up --build
```
Once the app is up and running, you can access it at [http://localhost:8000](http://localhost:8000)

### Local
For running the app locally, you'll need `node` and `npm` installed on your machine. We recommend using [nvm](https://github.com/nvm-sh/nvm) for managing node versions.
```bash
cd frontend
nvm use
npm install
npm run build
```

Once the build is complete, you can run the app using the following command from the root directory:
```bash
cd ..
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```
One the app is up and running, you can access it at [http://localhost:8000](http://localhost:8000)

### Development
For development purposes, you can run the app in development mode using the following command:

Start the backend server:
```bash
python -m uvicorn main:app --reload
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

