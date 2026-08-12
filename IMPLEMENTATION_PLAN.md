# Implementation Plan

Plan for building the **Assembly & Reverse Engineering Academy** per `Assembly_Reverse_Engineering_Academy_Master_Spec.md` (the canonical spec).

## Progress

- **Phase 0 (scaffolding): DONE.** `academy/` package layout per spec §28, `pyproject.toml` (deps: capstone, keystone-engine, unicorn, rich; dev: pytest, ruff, textual), `.venv` created at repo root.
- **Phase 1 (emulator core §6): DONE.** Register model with sub-register access (RAX/EAX/AX/AH/AL, RSP/RBP/RIP, R8-R15), flag model (RFLAGS CF..OF), segmented memory model (text/data/bss/heap/stack), stack view, Unicorn executor with Keystone assemble + Capstone disassemble, single-step via `emu_start(count=1)`, syscall handling (write/exit, int 0x80 too), `StateSnapshot` + `StateDiff` for explain-every-state-change, breakpoints, watchpoints, reverse stepping, step_over/step_out, `last_instruction`, `registers()`/`flags()`/`stack_view()`.
- **Phase 2 (sandbox §5 + debugger §8): DONE.** `academy/sandbox/Sandbox` exposes all 15 commands (`run step next continue reset registers flags stack memory break watch disassemble hexdump trace explain`) as a string-command API; `explain_diff` renders register/flag/memory/output changes as prose. `academy/debugger/Debugger` adds step into/over/out, continue, and register/flag/memory/stack views, each with an explanation.
- **Phase 3 (compiler explorer §7): DONE.** `academy/sandbox/CompilerExplorer` detects gcc/g++/clang on host, compiles C/C++ at O0-O3 with `-masm=intel`, returns cleaned assembly per variant; `asm` input is assembled via Keystone and disassembled via Capstone.
- **Phase 4 (curriculum §2 + §3): DONE.** Data model (`Module`/`Lesson`/`LessonStep` with all 11 step kinds), `LessonSession` engine with prediction grading, walkthrough program execution, challenge verification against expected end-state, and the three-view engine (source / assembly / debugger state). **All seven modules are fully authored** (Module 1: FDE, registers, MOV, ADD/SUB, LEA, flags; Module 2: memory layout, stack/RSP, stack frames, heap; Module 3: CMP/TEST, conditional jumps, loops, switches, pseudocode rebuild; Module 4: CALL/RET, System V ABI, callee/caller-saved, stack alignment; Module 5: bitwise, shifts, syscalls, strings/arrays, SIMD; Module 6: ELF, sections/symbols, CFG, crackmes/patching; Module 7: breakpoints, memory inspection, runtime analysis). Every runnable example/walkthrough/challenge is a real `.asm` file under `academy/curriculum/content/asm/` loaded via `read_asm()`; `tests/test_curriculum_content.py` proves each assembles, runs to `exited`, and each challenge's reference passes `verify_challenge`.
- **Phase 5 (challenges, hints, grading §11-13): DONE.** `academy/grading` with `Challenge` model (10 types, 5 difficulties), `HintEngine` (5 levels, 10-point penalty each), `Grader` scoring correctness/efficiency/understanding/explanation/optimization, running submissions in a fresh Executor and comparing expected end-state, plus suggested-review feedback. Five sample challenges for Module 1.
- **Phase 6 (adaptive learning §14-16): DONE.** `academy/analytics` with `StudentTracker` (accuracy/hints/retries/duration), `MasteryGraph` (per-topic percentages), `SpacedRepetition` (1/3/7/14/30-day intervals), and `DifficultyAdjuster`.
- **Phase 7 (RE + patching labs §9-10): DONE.** `academy/debugger/static.py` (Capstone-based CFG basic-block builder, linear-sweep function identification, string extraction), `academy/sandbox/re.py` (`ReverseEngineeringLab` + `ToyBinary`), `academy/sandbox/patching.py` (`PatchingLab` with byte patches, conditional-jump flipping, and automatic emulator-based behavior verification), `academy/sandbox/toy.py` generator (license check, password check, function sample).
- **Phase 8 (TUI, persistence, meta features §24/25/21-23/20/17/18): DONE.** `academy/storage` (atomic `JsonStore`, `SessionStore` save/resume of progress/sandbox/challenges/notes/achievements, `Notebook` with note/code/session/bookmark entries, declarative `AchievementSystem` with module/count conditions, `SqliteStore` append-only attempt log), `academy/core` (`Mission`/`MissionPack` scenario missions wired to the RE + patching labs, six `LearningPath`s A-F), `academy/analytics/HeatmapAnalyzer` (common-mistakes/weak-instruction/slow-topic heatmaps + auto recommendations), and `academy/ui` Textual app (`AcademyApp` main menu routing to Learn/Sandbox/placeholder screens, SandboxScreen with the six resizable panels Code/Registers/Flags/Memory/Stack/Output and a command input wired to the Sandbox engine). **Follow-up: every menu route is now a real screen** — Learn → LessonList → LessonScreen (11-step loop driven by `LessonSession`), Practice/Challenges → ChallengeScreen (hints + grading), Debugger (step into/over/out/continue/reset), Projects → MissionScreen (auto-run labs), Notebook, Progress (mastery/achievements/recommendations), Settings (theme/clear state), Sandbox command palette with `help` — wired through a shared `AppState` in `academy/ui/state.py`.
- **Phase 9 (plugin architecture §26): DONE.** `academy/plugins` defines the plugin API — `Plugin`/`PluginInfo`, `PluginRegistry` with directory auto-discovery (`discover`), `Insn` — plus architecture plugins for **x86_64** (Intel-syntax Keystone/Capstone + the full Executor seam), **arm64**, **arm32**, **mips32** (all fully assemble/disassemble/emulate), and **riscv64** (disassembly + emulation; Keystone has no RISC-V). A generic `run_source`/`run_code` runner executes any target through the same backend surface (assemble/disassemble/create_engine/step/read_pc/registers), and content-module plugins cover malware analysis, Windows internals, and Linux kernel internals. `executor_for()` hands back the full x86-64 Executor.
- **Learning-feedback polish pass: DONE.** Tracks fixes and new features requested during use (see "Educational UX pass" below): free-form response steps are now answerable + validated via keywords/model answers; failed challenges leave the input focused for a clean retry (empty submissions no longer silently pass with the reference answer); solved practice/challenges fire a green toast and register first-solve + challenge-hunter achievements; `?` reachable from Practice/Sandbox/Debugger (usable even while an Input is focused); the practice post-grade review is rebuilt into a structured, curriculum-linked re-study plan via `Grader._review_for`; six CTF-style challenges (`academy/grading/ctf.py`) distinct from practice; a JSON-persisted user-content authoring system (`academy/storage/content.py` + `academy/ui/authoring.py`, accessible with `A` on Practice/Challenges) that can add new practice, challenges, and whole 11-step lessons that the Lesson engine picks up on reload; in-app Sandbox and Debugger tutorials (`?`); visual lesson polish (step-glyph header, colorized options/assembly, a block progress bar); and the practice library grew from 5 to 11 authored exercises. All new paths are covered by `tests/test_ctf_and_authoring.py`.
- **Test suite: 168 tests, all passing (`pytest`); `ruff check` clean.**
- **Packaging & docs polish pass: DONE.** `README.md` with install/run/usage
  walkthroughs; the app is branded **Yotod** (a pixel-font wordmark in
  `academy/ui/logo.py`, hex-flavoured `0x59 0x4F 0x54 0x4F 0x44`, and a themed
  tagline) shown in a new two-column main menu (buttons left, logo right,
  `#menu-body`/`#menu-side`/`#logo` in `app.tcss`); `App.TITLE`/`SUB_TITLE`
  updated; `.gitignore` expanded (Python, venv, tool caches, `.asm-academy/`
  runtime data, editor files). **Interaction fixes:** the Quit menu button now
  calls the correct Textual API (`App.exit()` instead of the non-existent
  `App.quit()`) and the menu is a two-column layout that fits ~30-row
  terminals (scrollable below that); the Settings screen opts out of auto-focus
  (`AUTO_FOCUS = ""`) so the profile-path Input no longer swallows the
  D/C/E/I/P hotkeys — `P` focuses it for editing and `Enter` hands focus back —
  and `C` finally works via a real `AppState.clear_state()` (with `reset()`/
  `clear()` methods added to `StudentTracker`, `MasteryGraph`, `SqliteStore`,
  `Notebook`, and `AchievementSystem`). Menu tests in `tests/test_ui_app.py`
  still cover every route and the logo panel.**

## Guiding principles

- **Emulator core first.** Every feature (sandbox, debugger, lessons, grading, RE labs) is a consumer of the execution engine. Nothing else is buildable until single-step execution + state snapshots work.
- **Hard requirements**: interactive-only pedagogy (§2), explain-every-state-change (§5), auto-verify for patching (§10).
- **Architecture**: pure-Python engine with a thin TUI layer so the engine is testable headlessly (pytest).

## Phase 0 — Scaffolding

- Layout per spec §28 (`academy/` package with `core/ curriculum/ sandbox/ emulator/ debugger/ grading/ analytics/ plugins/ storage/ ui/ tests/`).
- `pyproject.toml` (deps: textual, rich, capstone, keystone, unicorn; dev: pytest, ruff, mypy).
- CI-equivalent: `ruff check` → `pytest`.
- **Verify**: empty package imports, `pytest` green.

## Phase 1 — Emulator core (§6) — critical path

- Register model (RAX/EAX/AX/AH/AL + RSP/RBP/RIP + flags), memory model (text/data/bss/heap/stack segments), stack model, flag model.
- Executor over Unicorn (x86-64) with Keystone assembler + Capstone disassembler for the fetch/step loop.
- `Step()` returning a **state snapshot** (registers, flags, stack, memory deltas) — snapshots power reverse stepping, watchpoints, and "explain state change".
- Breakpoints, watchpoints, reverse-step.
- **Verify**: unit tests that load a small program, single-step N times, assert register/flag/stack changes after each instruction.

## Phase 2 — Sandbox + Debugger (§5, §8)

- All 15 sandbox commands (`run step next continue reset registers flags stack memory break watch disassemble hexdump trace explain`) as engine API + CLI.
- Every action emits a human-readable explanation of what changed (wired to snapshot diffs).
- Debugger: step into/over/out, continue, memory/register/flag views.

## Phase 3 — Compiler Explorer mode (§7)

- Detect `gcc`/`clang` on host; compile C/C++/ASM at O0–O3 and show generated assembly side-by-side via Capstone.

## Phase 4 — Curriculum + lesson engine (§2, §3)

- Data-driven lesson format implementing the 11-step loop (concept → intuition → analogy → visualization → example → execution walkthrough → prediction question → response → feedback → challenge → reflection).
- Three View Learning Engine (§4): synchronized source / assembly / debugger-state panes.
- Author Module 1 (CPU/registers/MOV/ADD/SUB/LEA) end-to-end as template; scaffold Modules 2–7.

## Phase 5 — Challenge system, hints, grading (§11, §12, §13)

- 10 challenge types across 5 difficulties; challenge = spec + expected end-state (registers/flag/stack/output) checked against a fresh emulator run.
- Hint engine (5 levels, score penalty), auto-grading (correctness/efficiency/understanding/explanation/optimization).

## Phase 6 — Adaptive learning (§14, §15, §16)

- Track accuracy/time/hints/retries; mastery graph per topic; spaced-repetition scheduler; difficulty adjustment.

## Phase 7 — RE + patching labs (§9, §10)

- Toolchain to generate toy binaries (stripped/obfuscated variants); CFG reconstruction and function identification via Capstone + static analysis; patching tasks with **automatic verification** (patch binary, re-run emulator, assert behavior).

## Phase 8 — TUI, persistence, meta features (§24, §25, §21–§23, §20)

> **Status: DONE** (see progress log). Scenario missions (§17) and learning
> paths (§18) live in `academy/core`; heatmaps in `academy/analytics`;
> persistence/notebook/achievements in `academy/storage`; TUI in `academy/ui`.

- Textual app: main menu (Learn/Practice/Sandbox/Debugger/Challenges/Projects/Notebook/Progress/Settings/Quit), resizable 6-panel layout.
- SQLite + JSON persistence (§22 session resume), notebook, achievements, analytics heatmaps, scenario missions, learning paths.

## Phase 9 — Plugin architecture (§26)

> **Status: DONE** (see progress log). `academy/plugins` with `Plugin`/
> `PluginRegistry`/auto-discovery, five architecture plugins
> (x86_64/arm64/arm32/mips32/riscv64), a generic runner, and three
> content-module plugins.

- Define plugin API so future targets (ARM64, RISC-V, MIPS) can plug into the emulator/disassembler abstraction.
