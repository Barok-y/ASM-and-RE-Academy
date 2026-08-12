from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

from academy.grading.grading import Challenge as GradedChallenge
from academy.sandbox import PatchingLab
from academy.sandbox.toy import (
    build_flag_vault,
    build_function_sample,
    build_license_check,
    build_password_check,
)

Verifier = Callable[[Any], bool]

_CAMPAIGN_DEPTH = {
    "recover_password": 1,
    "patch_license": 3,
    "map_functions": 4,
    "extract_flag": 5,
    "exploit_overflow": 6,
    "advanced_syscalls": 7,
}


@dataclass
class Mission:
    mission_id: str
    title: str
    objective: str
    setup: Callable[[], Any]
    verify: Verifier
    difficulty: int = 1
    _solution: str = ""
    story: str = ""
    requires: Optional[str] = None
    challenge: Optional[GradedChallenge] = None

    def complete(self, answer: Any) -> bool:
        return self.verify(answer)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "id": self.mission_id,
            "title": self.title,
            "objective": self.objective,
            "difficulty": self.difficulty,
            "solution": self._solution,
            "story": self.story,
            "requires": self.requires,
        }


class MissionPack:
    def __init__(self) -> None:
        self._missions: Dict[str, Mission] = {}
        self._order: List[str] = []
        self._register_defaults()

    def _register_defaults(self) -> None:
        self.register(
            Mission(
                mission_id="recover_password",
                title="The Locked Gate",
                objective=(
                    "Reverse the password check binary: find which string the "
                    "program compares against the user input."
                ),
                setup=build_password_check,
                verify=lambda answer: isinstance(answer, bytes) and answer == b"Zx9!kq",
                difficulty=1,
                _solution="the password constant is b'Zx9!kq' at 0x600010",
                story=(
                    "CHAPTER I · The Locked Gate. The dungeon door hums with a "
                    "hex-wrought lock. It only yields to its master word. Reverse "
                    "the guard's magic to learn what it expects."
                ),
                challenge=_gate_challenge(),
            )
        )
        self.register(
            Mission(
                mission_id="patch_license",
                title="The Golem's Warden",
                objective=(
                    "Patch the golem so its blessing is granted no matter what "
                    "key you offer it."
                ),
                setup=build_license_check,
                verify=_verify_patched_license,
                difficulty=2,
                _solution="flip the conditional jump with PatchingLab.flip_jump(code, 'je')",
                story=(
                    "CHAPTER 2 · The Golem's Warden. A stone golem bars the iron "
                    "bridge, nodding only to the true key. You lack it. Break its "
                    "pact by bending the flow of command."
                ),
                requires="recover_password",
                challenge=_warden_challenge(),
            )
        )
        self.register(
            Mission(
                mission_id="map_functions",
                title="The Labyrinth of the Machine",
                objective=(
                    "The dungeon's lower halls pulse with clockwork subroutines. "
                    "Identify how many functions the machine runs and where each "
                    "routine begins."
                ),
                setup=build_function_sample,
                verify=lambda answer: isinstance(answer, dict)
                and answer.get("count") == 2
                and 0x400000 <= answer.get("starts", [0])[0] < 0x400020,
                difficulty=1,
                _solution="two functions: func_400000 and func_400020",
                story=(
                    "CHAPTER 3 · The Labyrinth of the Machine. The vault's "
                    "clockwork mind juggles several tasks at once. Map its "
                    "routines — every branch you fail to chart is a path you "
                    "cannot take below."
                ),
                requires="patch_license",
                challenge=_labyrinth_challenge(),
            )
        )
        self.register(
            Mission(
                mission_id="extract_flag",
                title="The Heart of the Dungeon",
                objective=(
                    "The final altar. A vault-machine stands at the world's core "
                    "guarding a single secret: the campaign flag. Run the vault, "
                    "read what it spills, and claim it."
                ),
                setup=build_flag_vault,
                verify=_verify_flag_vault,
                difficulty=3,
                _solution="auto-run the vault (A) to read the printed flag byte-for-byte",
                story=(
                    "FINAL · The Heart of the Dungeon. Beyond the golem and the "
                    "clockwork halls lies the machine-heart. It hums your own "
                    "ace; it only whispers the flag to those who let it run. "
                    "Capture the flag. You have earned it, archon."
                ),
                requires="map_functions",
                challenge=_heart_challenge(),
            )
        )
        self.register(
            Mission(
                mission_id="exploit_overflow",
                title="The Bleeding Relic",
                objective=(
                    "A relic whispers corrupted hex when overfilled. Smash its "
                    "guard and let the overflow overwrite RAX with the byte "
                    "stream 0x4141414141414141 ('AAAAAAAA')."
                ),
                setup=build_flag_vault,
                verify=lambda answer: isinstance(answer, int)
                and answer == 0x4141414141414141,
                difficulty=4,
                _solution="smudge the vault so the corrupted bytes land at 0x41414141...",
                story=(
                    "CHAPTER 5 · The Bleeding Relic. Beneath the vault a relic "
                    "bleeds hex over its own frame. It has no true defense — "
                    "only a squelched buffer. Spill 'AAAA' past its lip and let "
                    "the corruption write the numbers you need."),
                requires="extract_flag",
                challenge=_overflow_challenge(),
            )
        )
        self.register(
            Mission(
                mission_id="advanced_syscalls",
                title="The Polychord Gate",
                objective=(
                    "At the very threshold the machine speaks only in syscalls. "
                    "Raise RAX to the exit syscall number to make the gate stand "
                    "down cleanly and close the campaign."
                ),
                setup=build_flag_vault,
                verify=lambda answer: isinstance(answer, int) and answer == 60,
                difficulty=5,
                _solution="load the Linux exit syscall number 60 into RAX and syscall",
                challenge=_syscall_challenge(),
                requires="exploit_overflow",
                story=(
                    "FINAL GATE · The Kernel Chord. The last latch is bound to "
                    "the machine's very soul — the syscall table. Chord the exit "
                    "gate (RAX = 60) and the whole dungeon stands down. You have "
                    "walked from a locked door to the kernel itself, archon."
                ),
            )
        )

    def register(self, mission: Mission) -> None:
        self._missions[mission.mission_id] = mission
        if mission.mission_id not in self._order:
            self._order.append(mission.mission_id)

    def get(self, mission_id: str) -> Optional[Mission]:
        return self._missions.get(mission_id)

    def all(self) -> list[Mission]:
        return sorted(
            self._missions.values(),
            key=lambda m: (_CAMPAIGN_DEPTH.get(m.mission_id, 999), m.difficulty),
        )

    def campaign(self) -> list[Mission]:
        ordered = []
        for mid in self._order:
            if mid in self._missions:
                ordered.append(self._missions[mid])
        return ordered

    def available(self, completed: set) -> list[Mission]:
        """Story order but only missions whose prerequisite is met are active."""
        known = set(completed)
        out = []
        for m in self.campaign():
            if m.requires is None or m.requires in known:
                out.append(m)
        return out


def _verify_flag_vault(answer: Any) -> bool:
    from academy.sandbox.toy import CAMPAIGN_FLAG

    if isinstance(answer, bytes):
        return answer.rstrip(b"\x00") == CAMPAIGN_FLAG.encode("ascii")
    if isinstance(answer, str):
        return answer.strip() == CAMPAIGN_FLAG
    return False


def _verify_patched_license(patched: bytes) -> bool:
    lab = PatchingLab()
    try:
        ok, _ = lab.verify(build_license_check(), patched)
    except Exception:
        return False
    return ok


def _overflow_challenge() -> GradedChallenge:
    return GradedChallenge(
        id="mission_overflow",
        challenge_type="registers",
        difficulty="hard",
        title="Smash the relic",
        spec=(
            "Overflow the relic's guard and plant the byte stream 0x4141... (the "
            "letters 'AAAA'). Write assembly that leaves RAX = 0x4141414141414141 "
            "— the exact pattern the relic charges to its pointer register."
        ),
        program="mov rax, 0x4141414141414141",
        expected={"registers": {"rax": 0x4141414141414141}},
        hints=[
            "The smudge is literally the letters 'A', repeated.",
            "Each 'A' is ASCII 0x41.",
            "mov rax, 0x4141414141414141 loads the whole smear.",
        ],
        solution="mov rax, 0x4141414141414141",
    )


def _syscall_challenge() -> GradedChallenge:
    return GradedChallenge(
        id="mission_syscall",
        challenge_type="registers",
        difficulty="medium",
        title="Chord the exit gate",
        spec=(
            "Write a program that finally stands the machine down: load RAX = 60 "
            "(the Linux exit syscall number) and invoke it so every example in "
            "the academy ends cleanly."
        ),
        program="mov rax, 60\nmov rdi, 0\nsyscall",
        expected={"registers": {"rax": 60}},
        hints=[
            "60 is the exit syscall in the Linux syscall table.",
            "mov rax, 60 then mov rdi, 0 then syscall ends a program.",
            "That is the exact pattern every runnable example in the academy uses.",
        ],
        solution="mov rax, 60\nmov rdi, 0\nsyscall",
    )


def default_mission_pack() -> MissionPack:
    return MissionPack()


def _gate_challenge() -> GradedChallenge:
    return GradedChallenge(
        id="mission_gate",
        challenge_type="registers",
        difficulty="easy",
        title="Decode the master word",
        spec="The lock knows its master word 'Zx9!kq'. Write assembly that leaves "
        "RAX = 0x5A — the ASCII value of its first glyph 'Z' — to prove you read "
        "the constant off the wire.",
        program="mov rax, 0x5A\n;# Z in ASCII\nmov rbx, 0x600000\nmov byte ptr [rbx], 0x5A",
        expected={"registers": {"rax": 0x5A}},
        hints=[
            "The first glyph of 'Zx9!' is 'Z'.",
            "Look up 'Z' in an ASCII table: it is 0x5A.",
            "mov rax, 0x5A loads the answer directly.",
        ],
        solution="mov rax, 0x5A",
    )


def _warden_challenge() -> GradedChallenge:
    return GradedChallenge(
        id="mission_warden",
        challenge_type="registers",
        difficulty="medium",
        title="Bend the Warden's pact",
        spec=(
            "The golem only walks past when its blessing holds. Force the pact to "
            "hold: write assembly that ends with RAX = 1 (granted) no matter which "
            "key the warden mutters. Use exactly the arithmetic of a patched "
            "check — set the blessing directly.",
        ),
        program="mov rax, 0\ninc rax",
        expected={"registers": {"rax": 1}},
        hints=[
            "You are not supplying a valid key; you are bending the flow.",
            "Force RAX to 1 directly rather than by hashing the key.",
            "xor rax, rax clears; inc rax raises it to 1.",
        ],
        solution="xor rax, rax\ninc rax",
    )


def _labyrinth_challenge() -> GradedChallenge:
    return GradedChallenge(
        id="mission_labyrinth",
        challenge_type="registers",
        difficulty="easy",
        title="Count the clockwork routines",
        spec=(
            "Your map of the lower halls shows exactly two subroutines. Write "
            "assembly that leaves RAX = 2 — the number of functions you charted — "
            "so the machine logs your count.",
        ),
        program="mov rax, 2",
        expected={"registers": {"rax": 2}},
        hints=[
            "The analyzer reported two function starts.",
            "RAX should simply carry the count, 2.",
            "mov rax, 2 is all you need.",
        ],
        solution="mov rax, 2",
    )


def _heart_challenge() -> GradedChallenge:
    from academy.sandbox.toy import CAMPAIGN_FLAG

    length = len(CAMPAIGN_FLAG)
    return GradedChallenge(
        id="mission_heart",
        challenge_type="registers",
        difficulty="medium",
        title="Read the length of the flag",
        spec=(
            "Before you raise the flag you must know its measure. Write assembly "
            f"that leaves RAX = {length} — the exact length of the campaign flag — "
            "as the final cipher for the vault.",
        ),
        program=f"mov rax, {length}",
        expected={"registers": {"rax": length}},
        hints=[
            "The campaign flag is recorded in the vault's data segment.",
            "Count every character of 'ASM{DUNGEON_HEART_7F1E}'.",
            f"Load the whole depth: mov rax, {length}",
        ],
        solution=f"mov rax, {length}",
    )
