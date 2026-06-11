"""Antigravity (agy) CLI agent hooks."""

from __future__ import annotations

from collections.abc import Sequence

from clink.models import ResolvedCLIClient, ResolvedCLIRole

from .base import AgentOutput, BaseCLIAgent


class AgyAgent(BaseCLIAgent):
    """Agent for the Antigravity (`agy`) CLI.

    Unlike the gemini/codex/claude CLIs, `agy` does not read the prompt from
    stdin: it takes the prompt as the value of its ``--print`` flag and writes a
    plain-text response to stdout. The fully-assembled prompt (which already
    embeds the role/system prompt for non-claude runners) is therefore appended
    as a command-line argument here.
    """

    def __init__(self, client: ResolvedCLIClient):
        super().__init__(client)
        self._pending_prompt: str = ""

    async def run(
        self,
        *,
        role: ResolvedCLIRole,
        prompt: str,
        system_prompt: str | None = None,
        files: Sequence[str] = (),
        images: Sequence[str] = (),
    ) -> AgentOutput:
        # Capture the prompt so _build_command can append it as the --print value.
        self._pending_prompt = prompt
        return await super().run(
            role=role,
            prompt=prompt,
            system_prompt=system_prompt,
            files=files,
            images=images,
        )

    def _build_command(self, *, role: ResolvedCLIRole, system_prompt: str | None) -> list[str]:
        command = list(self.client.executable)
        command.extend(self.client.internal_args)
        command.extend(self.client.config_args)
        command.extend(role.role_args)
        # The assembled prompt already contains the system/role prompt for agy
        # (clink only routes system prompts out-of-band for the claude runner).
        command.extend(["--print", self._pending_prompt])
        return command
