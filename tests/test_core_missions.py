from academy.core import default_mission_pack, get_path, path_index
from academy.sandbox import PatchingLab
from academy.sandbox.toy import build_license_check


def test_learning_paths_registered():
    index = path_index()
    assert set(index) == {
        "path_a",
        "path_b",
        "path_c",
        "path_d",
        "path_e",
        "path_f",
    }
    assert get_path("path_a").module_ids[0] == "module1"
    assert get_path("nope") is None


def test_mission_pack_registered():
    pack = default_mission_pack()
    assert {m.mission_id for m in pack.all()} >= {
        "recover_password",
        "patch_license",
        "map_functions",
        "extract_flag",
    }


def test_recover_password_mission():
    pack = default_mission_pack()
    mission = pack.get("recover_password")
    assert mission is not None
    assert mission.complete(b"Zx9!kq")
    assert not mission.complete(b"wrong")


def test_patch_license_mission_verifies():
    pack = default_mission_pack()
    mission = pack.get("patch_license")
    lab = PatchingLab()
    patched = lab.flip_jump(build_license_check().code, "je")
    assert mission.complete(patched)
    assert not mission.complete(build_license_check().code)


def test_map_functions_mission():
    pack = default_mission_pack()
    mission = pack.get("map_functions")
    assert mission.complete({"count": 2, "starts": [0x400000, 0x400020]})
    assert not mission.complete({"count": 3, "starts": [0x400000]})


def test_mission_as_dict():
    pack = default_mission_pack()
    data = pack.get("patch_license").as_dict()
    assert data["title"] == "The Golem's Warden"
    assert "flip_jump" in data["solution"]
    assert data["requires"] == "recover_password"


def test_campaign_gates_story_sequence():
    pack = default_mission_pack()
    campaign = pack.campaign()
    assert [m.mission_id for m in campaign] == [
        "recover_password",
        "patch_license",
        "map_functions",
        "extract_flag",
        "exploit_overflow",
        "advanced_syscalls",
    ]
    # nothing unlocked yet -> only the intro is active
    active = pack.available(set())
    assert {m.mission_id for m in active} == {"recover_password"}
    # solving chapter by chapter unlocks the next
    active = pack.available({"recover_password"})
    assert "patch_license" in {m.mission_id for m in active}
    final = pack.available({"recover_password", "patch_license", "map_functions"})
    assert "extract_flag" in {m.mission_id for m in final}
    postgame = pack.available(
        {"recover_password", "patch_license", "map_functions", "extract_flag"}
    )
    assert "exploit_overflow" in {m.mission_id for m in postgame}
    all_clear = pack.available(
        {
            "recover_password",
            "patch_license",
            "map_functions",
            "extract_flag",
            "exploit_overflow",
        }
    )
    assert "advanced_syscalls" in {m.mission_id for m in all_clear}


def test_overflow_and_syscall_missions_verify():
    pack = default_mission_pack()
    overflow = pack.get("exploit_overflow")
    syscall = pack.get("advanced_syscalls")
    assert overflow.complete(0x4141414141414141)
    assert not overflow.complete(0x4242424242424242)
    assert syscall.complete(60)
    assert not syscall.complete(1)


def test_final_flag_mission():
    pack = default_mission_pack()
    mission = pack.get("extract_flag")
    assert mission is not None
    assert mission.complete(b"ASM{DUNGEON_HEART_7F1E}")
    assert mission.complete("ASM{DUNGEON_HEART_7F1E}")
    assert not mission.complete(b"wrong")


def test_story_text_present():
    pack = default_mission_pack()
    for m in pack.campaign():
        assert m.story.strip()


def test_every_mission_has_runnable_challenge():
    from academy.grading.grading import Grader

    pack = default_mission_pack()
    grader = Grader()
    for m in pack.campaign():
        assert m.challenge is not None, f"{m.mission_id}: no graded challenge"
        assert m.challenge.program.strip()
        grade = grader.grade(m.challenge, m.challenge.program)
        assert grade.passed, f"{m.mission_id}: reference did not pass"
        assert m.challenge.solution.strip()
