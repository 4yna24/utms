"""Deployment webhook endpoint for VPS sync."""

from __future__ import annotations

import hmac
import subprocess
from pathlib import Path

from flask import Blueprint, current_app, jsonify, request


deploy_bp = Blueprint("deploy", __name__, url_prefix="/api/deploy")


def _get_webhook_token() -> str:
    return request.headers.get("X-Webhook-Token", "")


@deploy_bp.post("/webhook")
def webhook():
    secret = current_app.config.get("DEPLOY_WEBHOOK_SECRET", "")
    command = current_app.config.get("DEPLOY_WEBHOOK_COMMAND", "")

    if not secret or not command:
        return jsonify({"ok": False, "message": "Webhook is not configured on this server."}), 503

    if not hmac.compare_digest(_get_webhook_token(), secret):
        return jsonify({"ok": False, "message": "Unauthorized."}), 401

    try:
        completed = subprocess.run(
            command,
            shell=True,
            cwd=Path(__file__).resolve().parents[2],
            capture_output=True,
            text=True,
            timeout=current_app.config.get("DEPLOY_WEBHOOK_TIMEOUT", 300),
            check=False,
        )
    except subprocess.TimeoutExpired:
        return jsonify({"ok": False, "message": "Deploy command timed out."}), 504

    if completed.returncode != 0:
        return (
            jsonify(
                {
                    "ok": False,
                    "message": "Deploy command failed.",
                    "stdout": completed.stdout,
                    "stderr": completed.stderr,
                }
            ),
            500,
        )

    return jsonify(
        {
            "ok": True,
            "message": "Deploy command completed successfully.",
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
    )