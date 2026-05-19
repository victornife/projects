# Teams Auto Reply Agent

A standalone FastAPI project that listens for Microsoft Teams message events from Microsoft Graph and auto-replies **only** to selected contacts, using conversation context and an LLM-generated response.

## What this project does

- Receives webhook notifications from Microsoft Graph when new chat messages are created.
- Filters notifications by sender against `ALLOWED_CONTACT_IDS`.
- Pulls recent chat history for context.
- Generates a contextual reply with OpenAI.
- Sends the response back into the same Teams chat.

## Quick start

1. Create a virtual environment and install dependencies:

```bash
cd teams-auto-reply-agent
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Copy environment variables:

```bash
cp .env.example .env
```

3. Fill in `.env` values:

- `TENANT_ID`, `CLIENT_ID`, `CLIENT_SECRET`: Azure app registration credentials.
- `OPENAI_API_KEY`: your OpenAI key.
- `PUBLIC_BASE_URL`: externally reachable HTTPS URL for webhook callbacks.
- `ALLOWED_CONTACT_IDS`: comma-separated AAD object IDs of allowed senders.

4. Run locally:

```bash
uvicorn src.main:app --reload --port 8000
```

## Endpoints

- `GET /health` — health check.
- `POST /webhooks/teams` — Graph notifications + validation callback.
- `POST /subscriptions/create` — helper endpoint to create a Graph subscription.

## Azure / Graph prerequisites

- Register an app in Azure AD.
- Grant Microsoft Graph application permissions for reading and posting Teams chat messages.
- Grant admin consent.
- Expose this service over HTTPS publicly (for Graph validation/webhooks).

> Note: Production deployments should include signature/client-state validation, robust subscription renewal logic, audit logging, and retry/error handling.
