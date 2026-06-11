"""Parser for Antigravity (agy) CLI plain-text output."""

from __future__ import annotations

from .base import BaseParser, ParsedCLIResponse, ParserError


class AgyTextParser(BaseParser):
    """Parse stdout produced by `agy --print <prompt>`.

    The agy CLI emits the model response as plain text on stdout (it has no
    structured/JSON output mode), so we surface stdout verbatim and attach any
    stderr as metadata for troubleshooting.
    """

    name = "agy_text"

    def parse(self, stdout: str, stderr: str) -> ParsedCLIResponse:
        text = (stdout or "").strip()
        if not text:
            detail = (stderr or "").strip()
            if detail:
                raise ParserError(f"agy CLI returned empty stdout. stderr: {detail}")
            raise ParserError("agy CLI returned empty stdout")

        metadata: dict[str, object] = {}
        if stderr and stderr.strip():
            metadata["stderr"] = stderr.strip()

        return ParsedCLIResponse(content=text, metadata=metadata)
