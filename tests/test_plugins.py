
from academy.plugins import (
    KIND_ARCHITECTURE,
    KIND_MODULE,
    Arm64Plugin,
    Mips32Plugin,
    Plugin,
    PluginInfo,
    PluginRegistry,
    ProgramRanTooLong,
    Riscv64Plugin,
    X8664Plugin,
    builtin_registry,
    executor_for,
    run_code,
    run_source,
)


def test_builtin_registry_contents():
    registry = builtin_registry()
    assert "x86_64" in registry.names()
    assert "arm64" in registry.names()
    assert "riscv64" in registry.names()
    assert len(registry.by_kind(KIND_ARCHITECTURE)) == 5
    assert len(registry.by_kind(KIND_MODULE)) == 3


def test_register_duplicate_rejected():
    registry = PluginRegistry()
    registry.register(X8664Plugin())
    try:
        registry.register(X8664Plugin())
        raise AssertionError("expected ValueError")
    except ValueError:
        pass


def test_require_unknown_plugin():
    registry = builtin_registry()
    assert registry.get("missing") is None
    try:
        registry.require("missing")
        raise AssertionError("expected KeyError")
    except KeyError:
        pass


def test_discover_finds_plugin_subclasses(tmp_path):
    (tmp_path / "my_plugin.py").write_text(
        "from academy.plugins import Plugin, PluginInfo\n"
        "class Demo(Plugin):\n"
        "    info = PluginInfo('demo', 'a demo plugin')\n"
        "class NotAPlugin:\n"
        "    pass\n"
    )
    registry = PluginRegistry()
    assert registry.discover(tmp_path) == 1
    assert registry.get("demo") is not None
    assert registry.names() == ["demo"]


def test_x86_64_roundtrip():
    plugin = X8664Plugin()
    code = plugin.assemble("mov rax, 5\nadd rax, 3")
    insns = plugin.disassemble(code)
    assert [i.mnemonic for i in insns] == ["mov", "add"]


def test_x86_64_assemble_error():
    plugin = X8664Plugin()
    try:
        plugin.assemble("this is not assembly")
        raise AssertionError("expected ValueError")
    except ValueError:
        pass


def test_arm64_roundtrip_and_run():
    plugin = Arm64Plugin()
    code = plugin.assemble("mov x0, #10\nadd x1, x0, #2")
    assert plugin.disassemble(code)[0].mnemonic in ("mov", "movz")
    trace, state = run_code(plugin, code, max_steps=10)
    assert len(trace) == 2
    assert state["x1"] == 12


def test_mips_roundtrip():
    plugin = Mips32Plugin()
    code = plugin.assemble("li $t0, 5\naddiu $t0, $t0, 7")
    insns = plugin.disassemble(code)
    assert [i.mnemonic for i in insns] == ["addiu", "addiu"]


def test_riscv_disassemble_no_assembler():
    plugin = Riscv64Plugin()
    try:
        plugin.assemble("addi x1, x0, 1")
        raise AssertionError("expected NotImplementedError")
    except NotImplementedError:
        pass
    # 0x00000013 is `addi x0, x0, 0`, rendered by Capstone as `nop`
    insns = plugin.disassemble(bytes([0x13, 0x00, 0x00, 0x00]))
    assert insns[0].mnemonic in ("addi", "nop")


def test_run_source_non_terminating():
    plugin = X8664Plugin()
    try:
        run_source(plugin, "jmp .", max_steps=50)
        raise AssertionError("expected ProgramRanTooLong")
    except ProgramRanTooLong:
        pass


def test_executor_for_x86_64_only():
    ex = executor_for("x86_64")
    from academy.emulator import Executor

    assert isinstance(ex, Executor)
    try:
        executor_for("arm64")
        raise AssertionError("expected ValueError")
    except ValueError:
        pass


def test_plugin_activate_hook():
    activated = []

    class Hooked(Plugin):
        info = PluginInfo("hooked", "hook test")

        def activate(self):
            activated.append(self.info.name)

    plugin = Hooked()
    plugin.activate()
    assert activated == ["hooked"]
