"""Run the installed seoscout CLI with a site-local content pipeline config.

Copy this file into a website's `content-pipeline/` directory. It expects:

- `.env` for credentials and model settings.
- `keywords.json` for topic/category keywords.
- `generate-prompt.md` for draft generation.
- `translate-prompt.md` for translation.
- `draft_validation.py` for optional generation gates.

The wrapper deliberately does not publish, deploy, or modify the website.
"""

from __future__ import annotations

import os
from pathlib import Path
import socket
import sys
from urllib.parse import urlsplit

from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)
load_dotenv(ROOT / ".env")
os.environ["PATH"] = str(Path(sys.executable).parent) + os.pathsep + os.environ.get("PATH", "")


_PINNED_HOSTS = {
    "google.serper.dev": ["34.111.29.75"],
    "r.jina.ai": ["104.26.10.242", "104.26.11.242", "172.67.70.54"],
}
_ORIGINAL_GETADDRINFO = socket.getaddrinfo


def _getaddrinfo_with_pipeline_fallback(host, port, family=0, type=0, proto=0, flags=0):
    """Fallback for occasional local DNS failures, scoped to known pipeline hosts."""

    try:
        return _ORIGINAL_GETADDRINFO(host, port, family, type, proto, flags)
    except socket.gaierror:
        ips = _PINNED_HOSTS.get(str(host).lower())
        if not ips:
            raise
        return [
            (socket.AF_INET, type or socket.SOCK_STREAM, proto, "", (ip, port))
            for ip in ips
        ]


socket.getaddrinfo = _getaddrinfo_with_pipeline_fallback


def _configure_llm_aliases() -> None:
    """Preserve explicit endpoint/key pairing and support OpenAI-style env names."""

    if os.environ.get("LLM_API_KEY"):
        return
    if os.environ.get("OPENAI_API_KEY") and os.environ.get("OPENAI_BASE_URL"):
        os.environ["LLM_API_KEY"] = os.environ["OPENAI_API_KEY"]
        os.environ["LLM_API_BASE_URL"] = os.environ["OPENAI_BASE_URL"]
        os.environ["LLM_MODEL"] = os.environ.get("LLM_MODEL") or "gpt-5.6-luna"


def _configure_prompts() -> None:
    if len(sys.argv) <= 1:
        return
    command = sys.argv[1]
    if command in ("generate", "translate", "run"):
        required = ("LLM_API_KEY", "LLM_API_BASE_URL", "LLM_MODEL")
        if not all(os.environ.get(key) for key in required):
            raise SystemExit("Configure LLM_API_KEY, LLM_API_BASE_URL and LLM_MODEL in .env.")
    if command in ("generate", "run") and "--prompt" not in sys.argv:
        sys.argv.extend(["--prompt", str(ROOT / "generate-prompt.md")])
    if command == "translate" and "--prompt" not in sys.argv:
        sys.argv.extend(["--prompt", str(ROOT / "translate-prompt.md")])


def _configure_proxy_override() -> None:
    proxy_url = os.environ.get("PIPELINE_PROXY_URL")
    if not proxy_url:
        return
    if urlsplit(proxy_url).scheme not in ("http", "https", "socks5", "socks5h"):
        raise SystemExit("PIPELINE_PROXY_URL must be http, https, socks5, or socks5h.")

    from seoscout.core.config import Config

    Config.get_proxy_url_for_stage = classmethod(lambda cls, stage: proxy_url)
    Config.get_proxy_url = classmethod(lambda cls: proxy_url)


def _install_draft_validation() -> None:
    if len(sys.argv) <= 1 or sys.argv[1] not in ("generate", "run"):
        return
    try:
        import seoscout.generate as generate
        from draft_validation import validate_draft
    except Exception as exc:  # pragma: no cover - defensive import guard for local installs
        raise SystemExit(f"Could not load draft validation: {exc}") from exc

    generate.validate_markdown = validate_draft


_configure_llm_aliases()
_configure_prompts()
_configure_proxy_override()
_install_draft_validation()

from seoscout.cli import main


if __name__ == "__main__":
    main()
