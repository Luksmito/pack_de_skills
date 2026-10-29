#!/usr/bin/env python3
"""Send one task notification; never log credentials or raw API errors."""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request

LABELS = {"concluido": "Concluído", "bloqueado": "Bloqueado", "falhou": "Falhou", "progresso": "Em andamento"}


def call_api(token, method, payload):
    request = urllib.request.Request(
        "https://api.telegram.org/bot" + token + "/" + method,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(request, timeout=20) as response:
        result = json.load(response)
    if result.get("ok") is not True:
        raise ValueError("api_rejected")
    return result["result"]


def render(data):
    agent = data.get("agent", "Codex")
    status = data.get("status")
    if not isinstance(agent, str) or not agent.strip() or len(agent) > 100 or "\n" in agent:
        raise ValueError("invalid_agent")
    if status not in LABELS:
        raise ValueError("invalid_status")
    lines = [f"[{agent}] {LABELS[status]}"]
    if "message" in data:
        if not isinstance(data["message"], str) or not data["message"].strip():
            raise ValueError("invalid_message")
        lines.append(data["message"])
    else:
        for key, label in [("done", "Feito"), ("next", "Próximo"), ("blocker", "Bloqueio"), ("checks", "Verificações")]:
            value = data.get(key)
            if not isinstance(value, str) or not value.strip():
                raise ValueError("missing_summary_field")
            lines.append(f"{label}: {value}")
    text = "\n".join(lines)
    if len(text.encode("utf-16-le")) // 2 > 4000:
        raise ValueError("message_too_long_shorten_summary")
    return text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--discover-groups", action="store_true")
    args = parser.parse_args()
    if args.dry_run and args.discover_groups:
        raise ValueError("incompatible_options")
    if not args.discover_groups:
        text = render(json.load(sys.stdin))
        if args.dry_run:
            print(json.dumps({"sent": False, "dry_run": True, "text": text}, ensure_ascii=False))
            return
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    if not token:
        raise ValueError("missing_TELEGRAM_BOT_TOKEN")
    if args.discover_groups:
        if call_api(token, "getWebhookInfo", {}).get("url"):
            raise ValueError("webhook_active_use_existing_receiver")
        groups = {}
        for update in call_api(token, "getUpdates", {"timeout": 0, "limit": 100}):
            chat = update.get("message", {}).get("chat", {})
            if chat.get("type") in ("group", "supergroup"):
                groups[chat["id"]] = {"id": chat["id"], "title": chat.get("title", "")}
        print(json.dumps({"groups": list(groups.values())}, ensure_ascii=False))
        return
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    if not chat_id or not chat_id.lstrip("-").isdigit():
        raise ValueError("missing_or_invalid_TELEGRAM_CHAT_ID")
    payload = {"chat_id": chat_id, "text": text, "link_preview_options": {"is_disabled": True}}
    thread = os.environ.get("TELEGRAM_THREAD_ID")
    if thread:
        if not thread.isdigit() or int(thread) < 1:
            raise ValueError("invalid_TELEGRAM_THREAD_ID")
        payload["message_thread_id"] = int(thread)
    result = call_api(token, "sendMessage", payload)
    print(json.dumps({"sent": True, "message_id": result["message_id"]}))


if __name__ == "__main__":
    try:
        main()
    except urllib.error.HTTPError as error:
        # Never print URL or response body: either may include sensitive data.
        print(json.dumps({"sent": False, "error": "telegram_http_error", "code": error.code,
                          "delivery_uncertain": error.code >= 500}), file=sys.stderr)
        sys.exit(1)
    except (urllib.error.URLError, TimeoutError, OSError):
        print(json.dumps({"sent": False, "error": "network_error", "delivery_uncertain": True}), file=sys.stderr)
        sys.exit(1)
    except (ValueError, KeyError, TypeError):
        print(json.dumps({"sent": False, "error": "invalid_configuration_input_or_response"}), file=sys.stderr)
        sys.exit(1)
