# AutoC Frontend

<img width="800" alt="Image" src="https://github.com/user-attachments/assets/aedf3614-78ef-438e-8db5-e7398f88fc6c" />

### Up and running options:

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
