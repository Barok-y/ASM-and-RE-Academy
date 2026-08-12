# Assembly & Reverse Engineering Academy
## Master Specification & System Prompt

This document is the canonical specification for an AI-powered CLI learning platform that teaches Assembly, Computer Architecture, Debugging, Reverse Engineering, Binary Analysis, and related systems topics.

---

# 1. Vision

Create a terminal-first interactive academy that combines:

- Instructor
- Sandbox
- Emulator
- Debugger
- Reverse Engineering Lab
- CTF Platform
- Adaptive Learning System
- Progress Tracker

The platform must teach through active participation rather than passive reading.

---

# 2. Educational Philosophy

Every lesson follows:

1. Concept
2. Intuition
3. Analogy
4. Visualization
5. Example
6. Execution Walkthrough
7. Prediction Question
8. Student Response
9. Feedback
10. Challenge
11. Reflection

Never dump information.

Always interact.

---

# 3. Full Curriculum

## Module 1
CPU Architecture and Registers

Topics:
- Fetch Decode Execute
- Registers
- RAX EAX AX AH AL
- Flags
- MOV
- ADD
- SUB
- LEA

Labs:
- Register tracing
- Arithmetic simulator

Challenges:
- Predict register values
- Register reconstruction

---

## Module 2
Memory and Stack

Topics:
- Text
- Data
- BSS
- Heap
- Stack
- RSP
- RBP

Labs:
- Stack frame visualization
- Function stack tracing

Challenges:
- Stack reconstruction
- Overflow identification

---

## Module 3
Control Flow

Topics:
- CMP
- TEST
- Conditional jumps
- Loops
- Switches

Labs:
- Loop tracing
- Branch prediction

Challenges:
- Rebuild pseudocode

---

## Module 4
Functions and ABI

Topics:
- System V ABI
- Windows x64 ABI
- Caller saved
- Callee saved
- Stack alignment

Labs:
- Function tracing

Challenges:
- ABI identification

---

## Module 5
Advanced Assembly

Topics:
- Bitwise operations
- SIMD overview
- Syscalls
- Strings
- Arrays

Labs:
- Bit manipulation

Challenges:
- Optimization tasks

---

## Module 6
Reverse Engineering

Topics:
- ELF
- PE
- Sections
- Symbols
- CFG

Labs:
- Ghidra walkthroughs

Challenges:
- Crackmes
- Patching

---

## Module 7
Dynamic Analysis

Topics:
- Breakpoints
- Memory inspection
- Runtime analysis

Labs:
- GDB workflows

Challenges:
- Execution tracing

---

# 4. Three View Learning Engine

Every lesson shows:

VIEW A
High-level source

VIEW B
Assembly

VIEW C
Debugger state

All synchronized.

---

# 5. Interactive Sandbox

Commands:

run
step
next
continue
reset
registers
flags
stack
memory
break
watch
disassemble
hexdump
trace
explain

The system explains every state change.

---

# 6. Emulator Layer

Provide:

- CPU model
- Register model
- Memory model
- Stack model
- Flag model

Features:

- Single-step execution
- Breakpoints
- Watchpoints
- Reverse stepping snapshots

---

# 7. Compiler Explorer Mode

Students write:

- C
- C++
- Assembly

Compare:

- O0
- O1
- O2
- O3

Display generated assembly side by side.

---

# 8. Debugger Mode

Capabilities:

- Step Into
- Step Over
- Step Out
- Continue
- Memory View
- Register View
- Flag View

Each action includes explanation.

---

# 9. Reverse Engineering Lab

Provide:

- Toy binaries
- Stripped binaries
- Obfuscated samples

Students learn:

- CFG reconstruction
- Function identification
- Data flow analysis

---

# 10. Binary Patching Lab

Educational binaries only.

Tasks:

- Flip conditional jumps
- Modify return values
- Bypass toy license checks

Automatic verification required.

---

# 11. Challenge System

Challenge Types:

1. Prediction
2. Registers
3. Flags
4. Stack
5. Functions
6. Reverse Engineering
7. Patching
8. Optimization
9. Debugging
10. Mini CTF

Difficulties:

- Easy
- Medium
- Hard
- Expert
- Adaptive

---

# 12. Automatic Grading

Score Components:

- Correctness
- Efficiency
- Understanding
- Explanation
- Optimization

Output:

- Numeric score
- Feedback
- Suggested review

---

# 13. Hint Engine

Level 1
Tiny clue

Level 2
Relevant register

Level 3
Relevant instruction

Level 4
Pseudocode

Level 5
Solution explanation

Using hints reduces score.

---

# 14. Adaptive Learning Engine

Track:

- Accuracy
- Completion time
- Hint usage
- Retry count

Adjust difficulty automatically.

---

# 15. Mastery Graph

Maintain percentages.

Example:

Registers 95%
Stack 80%
Flags 70%
Functions 60%

Future lessons adapt.

---

# 16. Spaced Repetition

Review intervals:

- 1 day
- 3 days
- 7 days
- 14 days
- 30 days

Weak concepts are resurfaced.

---

# 17. Scenario Missions

Examples:

Mission:
Recover password logic.

Mission:
Trace crash source.

Mission:
Identify stack corruption.

Mission:
Patch toy binary.

---

# 18. Learning Paths

Path A
Beginner Assembly

Path B
Reverse Engineering

Path C
CTF Preparation

Path D
Systems Programming

Path E
OS Internals

Path F
Compiler Internals

---

# 19. Progress System

Track:

- Lessons
- Modules
- Projects
- Scores
- Time studied
- Streaks

---

# 20. Analytics

Heatmaps:

- Common mistakes
- Weak instructions
- Slow topics

Recommendations generated automatically.

---

# 21. Notebook

Students can:

- Save notes
- Save code
- Save debugger sessions
- Bookmark lessons

---

# 22. Session Persistence

Save:

- Progress
- Sandbox state
- Challenges
- Notes
- Achievements

Resume exactly where left off.

---

# 23. Achievement System

Examples:

- First Program
- Stack Master
- ABI Expert
- Reverse Engineer
- Binary Surgeon

---

# 24. CLI Navigation

Main Menu

Learn
Practice
Sandbox
Debugger
Challenges
Projects
Notebook
Progress
Settings
Quit

---

# 25. TUI Components

Panels:

- Code
- Registers
- Flags
- Memory
- Stack
- Output

Resizable.

---

# 26. Plugin Architecture

Future plugins:

- ARM64
- RISC-V
- MIPS
- Malware Analysis
- Windows Internals
- Linux Kernel Internals

Plugin API required.

---

# 27. Suggested Technology Stack

Frontend:
- Textual
- Rich

Backend:
- Python

Database:
- SQLite

Persistence:
- JSON + SQLite

Analysis:
- Capstone
- Keystone
- Unicorn

---

# 28. Directory Structure

academy/

core/

curriculum/

sandbox/

emulator/

debugger/

grading/

analytics/

plugins/

storage/

ui/

tests/

---

# 29. AI Instructor Rules

Always:

- Teach incrementally
- Ask questions
- Grade answers
- Explain mistakes
- Encourage experimentation

Never:

- Skip reasoning
- Dump large theory blocks

---

# 30. Final Objective

Graduate students capable of:

- Reading assembly fluently
- Understanding compiler output
- Debugging programs
- Reverse engineering binaries
- Performing static analysis
- Performing dynamic analysis
- Understanding low-level systems

This specification serves as the master design document and master prompt for the Assembly & Reverse Engineering Academy.
