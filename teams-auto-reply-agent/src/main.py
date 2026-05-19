import os
import time
from typing import Any

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, Request
from openai import OpenAI

load_dotenv()

TENANT_ID = os.getenv("TENANT_ID", "")
CLIENT_ID = os.getenv("CLIENT_ID", "")
CLIENT_SECRET = os.getenv("CLIENT_SECRET", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
SYSTEM_PROMPT = os.getenv(
    "SYSTEM_PROMPT",
    "You are a helpful assistant replying briefly and professionally in Microsoft Teams.",
)

ALLOWED_CONTACT_IDS = {
    x.strip() for x in os.getenv("ALLOWED_CONTACT_IDS", "").split(",") if x.strip()
}

app = FastAPI(title="Teams Auto Reply Agent", version="0.1.0")
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

_graph_token_cache: dict[str, Any] = {"token": None, "exp": 0}


def get_graph_token() -> str:
    now = int(time.time())
    cached = _graph_token_cache.get("token")
    exp = _graph_token_cache.get("exp", 0)
    if cached and now < exp - 120:
        return cached

    if not (TENANT_ID and CLIENT_ID and CLIENT_SECRET):
        raise RuntimeError("Missing Microsoft app credentials in environment.")

    token_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials",
        "scope": "https://graph.microsoft.com/.default",
    }

    with httpx.Client(timeout=15) as client:
        resp = client.post(token_url, data=data)
        resp.raise_for_status()
        payload = resp.json()

    token = payload["access_token"]
    expires_in = int(payload.get("expires_in", 3599))
    _graph_token_cache["token"] = token
    _graph_token_cache["exp"] = now + expires_in
    return token


def get_message_context(chat_id: str, message_id: str, token: str, limit: int = 8) -> str:
    headers = {"Authorization": f"Bearer {token}"}
    messages_url = (
        f"https://graph.microsoft.com/v1.0/chats/{chat_id}/messages"
        f"?$top={limit}&$orderby=createdDateTime desc"
    )
    with httpx.Client(timeout=20) as client:
        resp = client.get(messages_url, headers=headers)
        resp.raise_for_status()
        values = resp.json().get("value", [])

    lines = []
    for item in reversed(values):
        sender = (
            item.get("from", {})
            .get("user", {})
            .get("displayName", "Unknown sender")
        )
        body = item.get("body", {}).get("content", "")
        lines.append(f"{sender}: {body}")
    return "\n".join(lines)


def generate_reply(context: str, incoming_text: str) -> str:
    completion = openai_client.responses.create(
        model=OPENAI_MODEL,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    "Conversation context:\n"
                    f"{context}\n\n"
                    "Reply to this latest message:\n"
                    f"{incoming_text}"
                ),
            },
        ],
        max_output_tokens=180,
    )
    return completion.output_text.strip()


def send_reply(chat_id: str, reply_text: str, token: str) -> None:
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {"body": {"contentType": "html", "content": reply_text}}
    post_url = f"https://graph.microsoft.com/v1.0/chats/{chat_id}/messages"

    with httpx.Client(timeout=20) as client:
        resp = client.post(post_url, headers=headers, json=payload)
        resp.raise_for_status()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/webhooks/teams")
async def teams_webhook(
    request: Request,
    validationToken: str | None = Query(default=None),
) -> Any:
    if validationToken:
        return validationToken

    payload = await request.json()
    notifications = payload.get("value", [])
    results = []

    for n in notifications:
        resource_data = n.get("resourceData", {})
        chat_id = resource_data.get("chatId")
        message_id = resource_data.get("id")
        from_user = resource_data.get("from", {}).get("user", {})
        sender_id = from_user.get("id")

        if not chat_id or not message_id:
            continue

        if ALLOWED_CONTACT_IDS and sender_id not in ALLOWED_CONTACT_IDS:
            results.append({"chatId": chat_id, "status": "ignored_not_allowed"})
            continue

        try:
            token = get_graph_token()
            headers = {"Authorization": f"Bearer {token}"}
            message_url = f"https://graph.microsoft.com/v1.0/chats/{chat_id}/messages/{message_id}"
            with httpx.Client(timeout=20) as client:
                message_resp = client.get(message_url, headers=headers)
                message_resp.raise_for_status()
                message = message_resp.json()

            incoming_text = message.get("body", {}).get("content", "")
            context = get_message_context(chat_id=chat_id, message_id=message_id, token=token)
            reply = generate_reply(context=context, incoming_text=incoming_text)
            send_reply(chat_id=chat_id, reply_text=reply, token=token)
            results.append({"chatId": chat_id, "status": "replied"})
        except Exception as exc:
            results.append({"chatId": chat_id, "status": "error", "error": str(exc)})

    return {"processed": results}


@app.post("/subscriptions/create")
def create_subscription() -> dict[str, Any]:
    """
    Convenience endpoint to create a Microsoft Graph subscription for chat messages.
    You should normally run this once after deployment.
    """
    public_base = os.getenv("PUBLIC_BASE_URL", "").rstrip("/")
    if not public_base:
        raise HTTPException(status_code=400, detail="PUBLIC_BASE_URL must be set")

    token = get_graph_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "changeType": "created",
        "notificationUrl": f"{public_base}/webhooks/teams",
        "resource": "/chats/getAllMessages",
        "expirationDateTime": "2026-05-26T00:00:00Z",
        "clientState": "teams-auto-reply-agent",
    }

    with httpx.Client(timeout=20) as client:
        resp = client.post("https://graph.microsoft.com/v1.0/subscriptions", headers=headers, json=payload)
        resp.raise_for_status()
        return resp.json()
