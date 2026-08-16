# Yotod — Assembly & Reverse Engineering Academy

A terminal-first, interactive academy that teaches **assembly language, computer
architecture, reverse engineering, and low-level systems** through active
participation. It combines an instructor, a sandbox, an emulator, a debugger,
RE labs, CTF-style challenges, and a story campaign — all in your terminal.

Built on the master spec in
[`Assembly_Reverse_Engineering_Academy_Master_Spec.md`](Assembly_Reverse_Engineering_Academy_Master_Spec.md).

```
╭─────────────────────────────────────────────────────────────────────────╮
│ 0x0000  fetch · decode · execute                                        │
│                                                                         │
│   █ █ █   ███   █████   ███   ████                                     │
│    █ █   █   █    █    █   █   █   █                                   │
│     █    █   █    █    █   █   █   █                                   │
│     █    █   █    █    █   █   █   █                                   │
│     █     ███     █     ███   ████                                     │
│                                                                         │
│   ASSEMBLY · REVERSE ENGINEERING · SYSTEMS                              │
│   learn it. build it. break it.                                         │
│   0x59  0x4F  0x54  0x4F  0x44   # YOTOD in hex                         │
╰─────────────────────────────────────────────────────────────────────────╯
```

## Features

- **9 fully-authored modules, 42 interactive lessons** — every lesson follows
  the spec's 11-step loop (concept → intuition → analogy → visualization →
  example → execution walkthrough → prediction → response → feedback →
  challenge → reflection). Every runnable example, walkthrough, and challenge
  is a real `.asm` file. Module 8 (**Crackme Lab**) is built from real
  crackmes and picoCTF challenges: XOR obfuscation, NOP-patching, flag
  recovery from immediates, byte-transform loops, and a VM-bytecode
  interpreter. Module 9 (**Exploit Lab**) teaches return-to-win, format leaks,
  heap overflows, PIE leaks, and tcache poisoning — all emulated from real
  `.asm` programs.
- **Live emulator** — a register/flag/memory/stack model over Unicorn
  (x86-64), single-step execution, breakpoints, watchpoints, and reverse
  stepping (rewind).
- **Sandbox** — 20 commands (`run step next continue reset registers flags
  stack memory break watch disassemble hexdump trace explain rewind loadelf
  input help demo`) with plain-language explanations of every state change.
  `loadelf` loads a real ELF (glibc starts via a libc shim) and `input` feeds
  stdin bytes to the emulated process.
- **Debugger** — step into / over / out, continue, reset, live register, flag,
  code, and stack panels.
- **Practice & CTF challenges** — 10 challenge types across 5 difficulties,
  auto-graded with 5-level hints, a structured re-study plan, and flags
  (including an 11-challenge CTF track whose OracleVM entry runs a real
  SIGILL-decoded bytecode interpreter).
- **Reverse Engineering lab** — toy ELF-style binaries, CFG reconstruction,
  function identification, string extraction, and **automatic binary
  patching** with emulator-based verification.
- **Story campaign (Projects)** — a gated, narrative "Dungeon of the Machine"
  that ends in a final flag.
- **Compiler Explorer mode** — compile C/C++ at O0–O3 (gcc/clang) and show the
  generated Intel-syntax assembly side by side.
- **Architecture plugins** — x86_64, arm64, arm32, mips32, riscv64 through a
  plugin API, plus content modules (malware analysis, Windows internals,
  Linux kernel internals).
- **Adaptive learning** — mastery graph per topic, spaced repetition, heatmaps
  of weak spots, difficulty adjustment, and automatic recommendations.
- **Persistence** — SQLite + JSON: resume lessons exactly where you left off,
  save notebook entries, achievements, XP/level/streaks, and export/import your
  full profile.
- **Authoring mode** — add your own practice, CTF challenges, and whole
  11-step lessons from inside the app (no files to edit).
- **Command palette** — fuzzy-jump to any screen, lesson, or challenge with
  `Ctrl+K`.

## Requirements

- **Python 3.10+** (tested on 3.13)
- A terminal that supports full Unicode (the TUI uses block glyphs).
- Optional: `gcc` / `g++` / `clang` on `PATH` for the Compiler Explorer mode
  (the C/C++ → assembly comparison).
- `capstone`, `keystone-engine`, `unicorn`, and `rich` install as Python wheels
  (no system libraries needed on most platforms).

## Installation

Clone or copy this directory, then set up a virtual environment:

```bash
cd ASM

# 1. Create and activate a virtualenv (Python 3.10+)
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. Install the app plus its runtime dependencies
pip install -e .
```

For development (tests + lint + the TUI dev extras):

```bash
pip install -e ".[dev]"
```

> On this machine the system Python is externally managed; the repo ships a
> ready-made `.venv` at the project root. If you are on a similar setup, just
> reuse it: `source .venv/bin/activate` and skip step 1.

## Running the academy

```bash
# from the project root, after activating the venv:
python -m academy.ui
```

or, if `make` is available:

```bash
make run
```

The main menu offers: **Learn · Practice · Daily Challenge · Challenges ·
Projects · Author & Create · Sandbox · Debugger · Notebook · Profile ·
Progress · Settings · Quit**.

## Using the program — quick tour

### 1. Learn (start here)

`Enter` on **Learn** → pick a module → pick a lesson. Lessons are interactive
end to end:

| Key | Action |
| --- | --- |
| `Enter` / `N` / `Ctrl+N` | next step (and finish the lesson) |
| `1`–`9` | answer a multiple-choice question |
| `R` | run the step's program and watch the STATE panel |
| `C` / `Ctrl+Enter` | verify your challenge solution |
| `H` | reveal a hint for the current step |
| `V` | toggle the three-view panels (source / assembly / state) |
| `X` | toggle the opcode/register/syscall cheat sheet |
| `B` / `Esc` | go back |

Type assembly in the input box to solve a challenge (Shift+Enter adds a line).
The live STATE panel auto-runs example and walkthrough programs so you always
see real register values.

### 2. Sandbox — your own CPU

Pick **Sandbox**, type `help` for every command, and try:

```
run                 # execute the whole program
step 1              # run one instruction
registers           # inspect all registers
flags               # inspect the condition flags
memory 0x600000 16  # hexdump 16 bytes at an address
stack 8             # show the stack
break 0x400000      # stop at an address
watch 0x600000 8    # fire when 8 bytes at an address change
rewind              # undo the last step (or press Z)
trace 5             # step 5 times, listing each change
explain             # plain-language note on the last change
```

`?` shows the built-in tutorial. Six live panels (code, registers, flags,
memory, stack, output) update with every command.

### 3. Debugger

`F` step-into, `O` step-over, `T` step-out, `C` continue, `R` reset. Predict
what each instruction changes, then press `F` to check yourself.

### 4. Practice & Challenges

Pick **Practice** (training exercises) or **Challenges** (CTF & crackmes).
Type assembly and press `Ctrl+Enter`/`G` to grade. `H` costs points per hint,
`V` reveals the step-by-step solution, `D` loads the challenge into the
debugger, `L` jumps to the linked lesson for the topic you missed, `?` shows
how-to help.

### 5. Projects — the story campaign

A gated series of RE missions (recover a password, patch a toy license check,
map functions, extract a flag). Each chapter must be cleared to unlock the
next. `A` auto-runs a lab, `V` verifies text answers, `G` grades assembly.

### 6. Notebook, Profile, Progress, Settings

- **Notebook**: add `kind|title|content` entries (`note|MOV|mov rax,5`).
- **Profile**: XP, level, streaks, and badges.
- **Progress**: lessons complete, mastery percentages, achievements, and
  automatic recommendations.
- **Settings**: toggle dark mode, clear saved state, and export/import your
  full profile as JSON. The box under the info panel is the profile path used
  by export/import — press `P` to edit it, `Enter` hands focus back to the
  hotkeys (`D` dark, `C` clear, `E` export, `I` import).

### 7. Author & Create

Add your own practice exercises, CTF challenges, or whole lessons from the
app. Authored content is persisted and picked up by the lesson engine on the
next load.

### Global keys

| Key | Action |
| --- | --- |
| `Ctrl+Q` | quit |
| `Ctrl+K` | command palette (fuzzy jump anywhere) |
| `B` / `Esc` | go back |

## Development

```bash
source .venv/bin/activate

make lint            # ruff check academy tests
make test            # run the full pytest suite (177 tests)
make demo            # smoke-test the sandbox engine
```

or directly:

```bash
.venv/bin/ruff check academy tests
.venv/bin/python -m pytest
```

## Project layout

```
academy/
  core/         mission packs, learning paths
  curriculum/   lessons + 11-step lesson engine, authored .asm content
  emulator/     registers, flags, memory, stack, Unicorn executor
  sandbox/      Sandbox, CompilerExplorer, RE lab, patching lab, toy binaries
  debugger/     Debugger + static analysis (CFG, functions, strings)
  grading/      Challenge model, hint engine, grader, CTF challenges
  analytics/    tracker, mastery, spaced repetition, heatmaps, gamification
  plugins/      architecture + content module plugin API
  storage/      JSON/SQLite stores, notebook, achievements, user content
  ui/           Textual TUI (screens, app, theme, logo)
  tests/        (repo root: pytest suite)
```

## Notes & limitations

- Keystone (Intel syntax) accepts mnemonics but rejects data directives
  (`db`, `section`, `global`) and `;` comments — authored programs use plain
  mnemonics, register-indirect memory access, and end with a clean
  `mov rax, 60; mov rdi, 0; syscall` exit.
- MIPS programs NOP-pad and run until the step limit; test MIPS via assemble →
  disassemble round-trip. RISC-V has no Keystone backend (disassembly +
  emulation only). ARM64 is the second best target for generic emulation.
- Compiler Explorer needs `gcc`/`clang` on the host (installed by default on
  most Linux setups; this machine has gcc, g++, and clang).

## License & attribution

All lesson content and toy binaries are educational and authored in this repo.
The Yotod wordmark and palette are original to this project.
