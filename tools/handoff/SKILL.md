---
name: handoff
description: Write a concise, self-contained handoff checkpoint file so a fresh coding-agent session can continue the current task without the old conversation. Use when the user asks for a handoff or checkpoint, says the context is nearly full, or wants to stop now and continue in a new session — in any language. Only writes one Markdown file; never resumes sessions, edits source code, or changes Git state — not for committing work (use git for that).
---

# Handoff

Create one Markdown file that lets a fresh session with zero chat history pick up the current task. The next session's context window is the scarce resource, so the file preserves *state*, not transcript.

## Scope

The only write operations allowed are:

1. creating the handoffs directory if it does not exist;
2. creating the single handoff file.

Everything else is read-only. In particular, do not commit, push, checkout, reset, stash, edit `.gitignore`, touch product/source files, or create TODO databases, issue tickets, or memory files. The user may be mid-change, and any side effect here can destroy work they haven't saved. Do not start or resume another session afterwards.

Shell commands in this skill are POSIX (bash / Git Bash). If only PowerShell is available, use the equivalents rather than skipping the step — e.g. `Get-Date -Format 'yyyy-MM-dd-HHmm'` for the timestamp, `Get-Date -Format 'yyyy-MM-dd HH:mm K'` for the Generated line, and `Get-ChildItem <dir> -Name -ErrorAction SilentlyContinue | Select-Object -Last 20` for listing. `git` commands work unchanged.

## Step 1 — Locate output

- Find the Git root: `git rev-parse --show-toplevel`. If not a Git repo, use the current working directory.
- Pick the directory by which agent *you* are:
  - Claude Code → `<root>/.claude/handoffs/`
  - Codex → `<root>/.codex/handoffs/`
  - Any other agent → `<root>/.handoffs/`
- List existing handoffs: `ls -1 <dir> 2>/dev/null | tail -n 20`. If one covers the same task, reuse its `<topic>` and record it as the previous handoff. Judge relevance from filenames; do not read an old handoff unless it appears relevant to the same task — reading unrelated ones just burns context.

## Step 2 — Build the filename

Format: `YYYY-MM-DD-HHmm_<topic>.md`

- Get the timestamp from the shell, never from your own sense of time: `date +%Y-%m-%d-%H%M`.
- `<topic>`: 2–6 words, lowercase kebab-case, describing the primary task. No personal names, session IDs, branch names, or status words (`wip`, `done`, `final`).
- If the exact name exists, append `-02`, `-03`, …

Example: `2026-10-05-1315_nx-ci-fix.md`

## Step 3 — Inspect current state (cheaply)

Handoffs often run when context is nearly full, so keep output small:

```bash
git branch --show-current
git rev-parse --short HEAD
git status --short
git log --oneline -n 10
git diff --stat            # and git diff --cached --stat
```

Read full diffs only for specific files whose state is unclear. Reuse test/build/lint results already produced in this session; do not re-run long test suites just for the handoff.

When the repository contradicts something said in the conversation (e.g. a file claimed as fixed is unchanged), trust the repository and record the discrepancy under Current State.

## Step 4 — Extract durable context from the conversation

Keep only what the next session would otherwise have to rediscover:

- goal and what counts as done;
- current state;
- settled decisions and their reasons;
- approaches tried and rejected, with why — these are the highest-value lines, because they prevent repeated work;
- exact errors, measurements, commands, and observed behavior;
- user constraints and corrections relevant to the task;
- remaining work and blockers.

If earlier parts of the conversation have been compacted into a summary, trust only what the summary actually states. Exact errors, numbers, or command output that survive only as a vague mention go under Not Yet Verified (or are re-checked cheaply) — never reconstruct them from impression, because a plausible-looking but invented detail is worse than a gap.

Drop greetings, repeated explanations, and side discussions. A discarded idea goes under Tried / Rejected only if knowing about it saves the next session time — not because it took many turns to discuss.

## Step 5 — Write the file

Use the template below. Omit a section only if it is genuinely inapplicable. Aim for 1–3 screens.

For tasks that are not about changing code (investigation, data lookup, document review, etc.), the Git header lines and Changes Made are usually empty. Replace them with what that kind of task actually needs to resume: the data sources consulted (files, URLs, systems), the queries or conditions used, and the intermediate findings so far. Keep Branch/HEAD only if a repository is genuinely involved.

Write in the language the user has been using in this conversation. Keep code, paths, commands, and error messages verbatim.

```markdown
# Handoff: <short human-readable task title>

- Generated: <output of `date "+%Y-%m-%d %H:%M %Z"`>
- Agent: <Claude Code | Codex | other>
- Repository: <repo root or name>
- Branch: <branch or N/A>
- HEAD: <short commit or N/A>
- Uncommitted changes: <yes | no>
- Previous handoff: <path or none>

## Goal
<What must be achieved and what counts as done.>

## Current State
- <fact>

## Decisions
- **<decision>** — <why this is the accepted direction>

## Tried / Rejected / Obsolete
- **<approach or assumption>** — <what happened; why not to repeat it>

## Changes Made
<!-- Task-relevant files only; not a git status inventory. -->
- `<path>` — <what changed and why>

## Verification
### Verified
- `<command/check>` — <actual observed result>

### Not Yet Verified
- <specific unverified item>

## Open Questions / Blockers
- <question, dependency, or blocker>

## Next Steps
1. <specific, executable action>
2. <specific, executable action>
3. <specific, executable action>

## Quick Start
- Inspect first: `<path>`
- First action: <command, file to read, diff to review, or other concrete action>
- Must preserve: <constraint the next session must not break>
```

### Writing rules

- **Verified means observed in this session.** An unrun test or unchecked assumption goes under Not Yet Verified — a false "verified" sends the next session in the wrong direction.
- **Mark inference as inference** ("likely", "unconfirmed") instead of stating it as fact.
- **Next steps must be executable.** "Continue debugging" is not a step; "Add a log in `foo.ts:42` and rerun `pnpm test foo`" is.
- **Stay on task.** List only task-relevant changed files. Do not include unrelated uncommitted work merely because it appears in `git status` — the repo may hold the user's other in-progress changes. If such changes exist, add one line to Current State saying so and that they must be left alone, without listing them.
- **No secrets.** Never copy passwords, tokens, cookies, keys, or sensitive env values — including ones that appeared in diffs or command output. Refer to them by variable name only.- **Continuity.** If a previous handoff exists, carry forward only facts that are still true. Do not paste the old handoff in; the new one must stand alone.

## Step 6 — Self-check

Before finishing, confirm a fresh agent could answer from the file alone:

1. What are we trying to accomplish?
2. What is true right now?
3. What was tried and should not be repeated?
4. Which decisions are settled, and why?
5. What is verified versus assumed?
6. What should I do first, second, third?

Fix any gap, then stop.

## Step 7 — Report

Tell the user the created path in one or two lines, followed by a ready-to-paste opening message for the new session, in the user's language — for example:

> Read `.claude/handoffs/2026-10-05-1315_nx-ci-fix.md`, check that the repository still matches its Current State, then continue from Next Steps.

The handoff file itself is the whole mechanism; do not set up anything else for resuming.

If the handoffs directory is not ignored by Git (`git check-ignore -q <dir>` fails), add one line noting it could get committed by `git add .` — mention it, don't fix it.
