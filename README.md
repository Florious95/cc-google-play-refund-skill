**English** | [简体中文](README.zh.md)

# google-play-refund-skill

An [Agent Skill](https://agentskills.io/specification) for Claude Code, Cursor, Codex and other coding agents. It helps you get **Google Play** to refund a **Claude (Anthropic) subscription bought through Google Play** after the Claude account was **banned or suspended**, once **Anthropic has already refused the refund in writing**.

It is based on two real cases that were resolved through the Google Play Help Center. Both ended in a manual refund, and the second was resolved with essentially one complete message. The skill teaches your agent to do the same thing:

1. Check that it can read your Gmail and take screenshots. If it can't, it looks up how to add those on *your* agent platform and gives you options.
2. Check the preconditions. Your mailbox must already contain the Play receipt, the ban notice, and a detailed exchange with Anthropic support that ends in an explicit refusal. If that refusal is missing, the agent helps you get it first.
3. Go through your mailbox once, build a timeline accurate to the minute with timezones, and then ask you for **all** missing screenshots in one message.
4. Redact everything unrelated (other inbox rows, card digits, other people's data) and add an English caption to every exhibit with the bundled scripts.
5. Draft **one** complete, polite English message from your real facts (no templates). You review it, and nothing is sent without your explicit approval.

> This is not legal or financial advice, and a refund is not guaranteed. Google decides each request case by case.

## Prerequisites

- An agent host that supports Agent Skills (`SKILL.md`): Claude Code, Cursor, Codex, GitHub Copilot, Gemini CLI and others.
- **Gmail access for the agent** (an official connector, an MCP server or a plugin) for the Google account that made the Play purchase.
- **Screenshot ability for the agent** (browser or computer-use tool, or headless Chrome).
- Python 3.8+ with [Pillow](https://pypi.org/project/Pillow/) for the scripts: `python3 -m pip install --user Pillow`. OCR auto-redaction is optional and needs `pytesseract` and the `tesseract` binary.
- Your mailbox already contains: the Google Play receipt (`GPA.…`), the Anthropic ban or suspension notice, and Anthropic support's **written refusal**.

## Install

Pick **one** option. The skill folder must be named `google-play-refund` (the same as `name:` in `SKILL.md`).

### Option A - `npx skills` (cross-agent installer)

```bash
npx skills add Florious95/google-play-refund-skill                                   # this project: ./.agents/skills (Codex, Cursor, Copilot …)
npx skills add Florious95/google-play-refund-skill -g                                # global: ~/.agents/skills
npx skills add Florious95/google-play-refund-skill -a claude-code -a cursor -a codex # also link into .claude/skills for Claude Code (add -g for ~/.claude/skills)
```

Claude Code only reads `.claude/skills`. If the installer does not detect Claude Code on your machine, pass `-a claude-code` so it creates the `.claude/skills/google-play-refund` link. Without `-a`, a non-interactive `-g` run may list harmless failures for agents that have no global skills directory. ([vercel-labs/skills](https://github.com/vercel-labs/skills). It needs a recent Node.js; v1.7.x requires Node ≥ 22.20. On older Node you can run `npx -p node@22 -p skills -- skills add …`.)

### Option B - `install.sh`

From a clone:

```bash
git clone https://github.com/Florious95/google-play-refund-skill.git
cd google-play-refund-skill
./install.sh --project            # ./.agents/skills/google-play-refund   (Codex, Cursor, Copilot, Gemini CLI … in the current project)
./install.sh --global             # ~/.agents/skills/google-play-refund   (Codex, Cursor; all projects)
./install.sh --claude             # ~/.claude/skills/google-play-refund   (Claude Code personal; Cursor reads it too)
./install.sh --claude --project   # ./.claude/skills/google-play-refund   (Claude Code, current project)
./install.sh --dir /some/skills   # any other skills directory
```

Or without cloning:

```bash
curl -fsSL https://raw.githubusercontent.com/Florious95/google-play-refund-skill/main/install.sh | bash -s -- --claude
```

`--project` and `--claude --project` install into the directory you run the command from. Flags can be combined, for example `--global --claude`. Use `--force` to replace an existing install.

### Option C - manual copy

Copy `SKILL.md`, `scripts/` and `examples/` into a folder named `google-play-refund` in one of these locations:

| Agent | Project scope | User (global) scope | Source |
|---|---|---|---|
| Claude Code | `.claude/skills/google-play-refund/` | `~/.claude/skills/google-play-refund/` | [Claude Code docs: Skills](https://code.claude.com/docs/en/skills) |
| Cursor | `.agents/skills/…` or `.cursor/skills/…` (also reads `.claude/skills/`, `.codex/skills/`) | `~/.agents/skills/…` or `~/.cursor/skills/…` (also reads `~/.claude/skills/`, `~/.codex/skills/`) | [Cursor docs: Agent Skills](https://cursor.com/docs/skills) |
| Codex | `.agents/skills/…` (from the current directory up to the repo root) | `~/.agents/skills/…` (`~/.codex/skills` is the deprecated legacy location) | [Codex skills docs](https://learn.chatgpt.com/docs/build-skills), [openai/codex#14337](https://github.com/openai/codex/issues/14337) |
| GitHub Copilot, Gemini CLI, … | `.agents/skills/…` (shared project directory) | depends on the host | [`gh skill install` manual](https://cli.github.com/manual/gh_skill_install) |

Restart or reload your agent after installing. Codex needs a restart. Claude Code picks up changes in existing skills folders live, but if the skills folder did not exist when the session started, run `/reload-skills`.

## Use

Ask your agent something like:

> My Claude Max subscription that I bought on Google Play got banned, and Anthropic refused to refund it. Help me get Google Play to refund it.

The agent loads the skill, checks its tools and your mailbox, and asks you for the missing screenshots in one message. Then it shows you the exhibits and the draft. **You approve before it sends anything.**

## Bundled scripts

| Script | What it does |
|---|---|
| `scripts/redact.py` | Black, fill, blur or pixelate rectangles (`--rect`) or whole-width rows (`--band`). It can also find text by OCR (`--ocr REGEX`). Output is re-encoded without metadata. |
| `scripts/annotate.py` | Adds an English exhibit banner (title and caption lines) **outside** the original pixels, plus boxes, arrows and notes. Works from CLI flags or a JSON spec. |
| `scripts/grid.py` | Draws a labelled coordinate grid on a copy of an image so you can read coordinates for the other two scripts. |

All of them take `--help`. To rebuild the fictional demo:

```bash
examples/demo.sh   # sample-inbox.png -> sample-inbox-redacted.png -> demo-exhibit.png
```

![demo exhibit](examples/demo-exhibit.png)

## Privacy

Everything in this repository is fictional (`jane.doe@example.com`, `GPA.0000-…`). Your own case sheet and exhibits belong on your machine and in your own mail drafts. Do not commit them to any repository.
