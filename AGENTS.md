# AGENTS.md

## Repo context

This directory contains the **Assembly & Reverse Engineering Academy Master Spec** (`Assembly_Reverse_Engineering_Academy_Master_Spec.md`) — the design document and master prompt for an AI-powered, terminal-first CLI learning platform — plus a working implementation under `academy/`. Progress is tracked in `IMPLEMENTATION_PLAN.md`.

## Ground rules

- Treat `Assembly_Reverse_Engineering_Academy_Master_Spec.md` as the source of truth for all platform behavior. Read it before implementing anything; its 30 sections define scope, pedagogy, curriculum, and requirements.
- The spec mandates an **interactive** platform (active participation over passive reading). The 11-step lesson loop in §2 and the "always explain every state change" rule in §5 are hard requirements, not suggestions.
- Any implementation plan should be phased so that the emulator/execution core lands before UI or curriculum (everything depends on the execution engine).
- Phases 0–9 are complete (168 tests passing). Modules 1–7 are fully authored with complete 11-step lessons; every runnable example/walkthrough/challenge is a real `.asm` file under `academy/curriculum/content/asm/`. The master plan is implemented end-to-end; future work is polish and additional content. The app is branded **Yotod** — see `README.md` (install/run/usage) and `academy/ui/logo.py` (main-menu wordmark panel).

## Tech stack (per spec §27)

- Python backend; Textual + Rich for the TUI
- SQLite + JSON for persistence
- Capstone (disassembly), Keystone (assembly), Unicorn (CPU emulation)
- Directory layout per spec §28: `core/`, `curriculum/`, `sandbox/`, `emulator/`, `debugger/`, `grading/`, `analytics/`, `plugins/`, `storage/`, `ui/`, `tests/`

## Tooling

- Python 3.13 is externally managed: only use `/home/barok/Documents/ASM/.venv/bin/python` and `.venv/bin/pip`.
- Standardize on a `pyproject.toml` + pytest layout. Verify with `ruff check academy tests` then `pytest`.

## Notes

- Keystone (Intel syntax) accepts label/mnemonic syntax but rejects data directives (`db`, `section`, `global`); use plain mnemonics and absolute addresses (RIP-relative `lea rX,[rip+label]` fails with `KsError`). It also rejects `;` comments (use `//` or `#`), has no imm64-to-memory store (load the value into a register first), and encodes `mov [abs], imm` as RIP-relative — so authored programs address memory register-indirect (`mov rbx, 0x600000` then `mov byte ptr [rbx], 42`) and end with a clean exit syscall (`mov rax, 60; mov rdi, 0; syscall`). Only full-line/trailing `//` comments assemble, so lesson programs keep their comments.
- Authoring convention: lesson example/walkthrough/challenge programs live as real `.asm` files under `academy/curriculum/content/asm/<module>/<lesson>/` and are loaded via `read_asm()`; module builder files (e.g. `module2.py`) fill `LessonStep.program` from them. `tests/test_curriculum_content.py` guarantees every program assembles, runs to `exited`, and every challenge's reference solution passes `verify_challenge`.
- Keystone emits 6-byte `0F 84 rel32` conditional jumps; patching flips jumps by XORing the opcode byte (`0x70–0x7F` short, `0x0F 0x80–0x8F` near).
- Textual 8.x: `Header()` takes no `title` kwarg (uses `App.TITLE`); `Static` content is read via `.content`; `App.get_screen` must accept Screen instances; `App.dark` no longer exists — use `App.theme` / `App.current_theme.dark`. Never name a screen helper `_render()` — that collides with Textual's internal `Widget._render()` (must return a `Visual`), causing `'NoneType' object has no attribute 'render_strips'`; the UI uses `_render_view()` instead. `App.quit()` does NOT exist in Textual 8.2.8 — call `App.exit()` (or `action_quit` via a binding).
- Textual 8.x auto-focuses the first focusable widget after mount (`App.AUTO_FOCUS = "*"`), so `widget.blur()` inside `on_mount` is undone; a focused `Input` swallows letter hotkeys. The `SettingsScreen` opts out with `AUTO_FOCUS: ClassVar[str | None] = ""` and exposes `P` to focus its profile-path box, `Enter` to hand focus back. Other input-bearing screens (challenge/mission/lesson) rely on the input only being focused when typing is expected.
- Textual 8.x bindings dispatch an action ONLY against the owning screen's namespace (`check_action` may still return True because App has the method, but `_dispatch_action` never reaches the App). Screen-level bindings must use qualified actions like `Binding("b", "app.pop_screen", "Back")` — plain `"pop_screen"` silently no-ops. A hidden (invisible) focused `Input` still swallows letter/enter keys, so lessons focus the input only on challenge steps, blur it otherwise, and bind `ctrl+n` to advance so users can leave a challenge input.
- Authoring convention: the `.hidden` CSS class is not styled in `app.tcss`; `#views` panels are shown and populated by default in `LessonScreen`, with `V` toggling `display`.
- Lesson UX (module1 shows the full pattern): every lesson is interactive end-to-end. `LessonStep.hint` holds a per-step hint revealed with `H`; concept/visualization steps carry a tiny illustrative program and end with a self-check question (`options`+`answer`+`feedback`); prediction/response/challenge steps carry a program too so `R` reveals the answer and `C`/`Ctrl+Enter` verifies. `LessonScreen` auto-runs example/walkthrough programs into the live STATE panel (register diffs + friendly status), only loads quiz-step programs, and `_step_hint()` falls back to kind-aware hints for steps without an authored hint. The `engine.respond()` generalizes to any step with options+answer (not just prediction/response). Verify catches all exceptions so bad assembly never crashes the TUI, and completion fires `app.notify(..., severity="success")`.
- Capstone aliases some mnemonics (`li`→`addiu` on MIPS, `addi x0,x0,0`→`nop` on RISC-V); Keystone has no RISC-V backend, and MIPS NOP-padding makes bare-metal programs run until `max_steps` — test MIPS via round-trip, ARM64 for generic emulation.
- Only create educational/toy binaries for the RE and patching labs (§9, §10); automatic verification is required for patching tasks.
- Check the target host for `gcc`/`clang` availability before using the Compiler Explorer mode (§7).
