import pytest

from academy.sandbox import CompilerExplorer

C_SOURCE = """
int add(int a, int b) {
    return a + b;
}
"""


def test_compiler_available():
    explorer = CompilerExplorer()
    if not explorer.available:
        pytest.skip("no C compiler on host")
    assert explorer.compiler


def test_compile_c_all_optimizations():
    explorer = CompilerExplorer()
    if not explorer.available:
        pytest.skip("no C compiler on host")
    result = explorer.compile(C_SOURCE, "c")
    assert result.available
    assert not result.errors
    for opt in ("O0", "O1", "O2", "O3"):
        assert opt in result.variants
        assert "add" in result.variants[opt]


def test_optimization_levels_differ():
    explorer = CompilerExplorer()
    if not explorer.available:
        pytest.skip("no C compiler on host")
    result = explorer.compile(C_SOURCE, "c")
    assert result.variants["O0"] != result.variants["O3"]
    assert "lea" in result.variants["O3"]


def test_compile_cpp():
    explorer = CompilerExplorer()
    if not explorer.available:
        pytest.skip("no C compiler on host")
    result = explorer.compile("int f(int x) { return x * 2; }", "cpp")
    assert not result.errors


def test_assemble_asm_input():
    explorer = CompilerExplorer()
    result = explorer.compile(
        """
        mov rax, 5
        add rax, 2
        """,
        "asm",
    )
    assert "asm" in result.variants
    assert "add" in result.variants["asm"]


def test_unsupported_language():
    explorer = CompilerExplorer()
    with pytest.raises(ValueError):
        explorer.compile("int x;", "fortran")


def test_asm_bad_source_reports_error():
    explorer = CompilerExplorer()
    result = explorer.compile("mov rax,", "asm")
    assert "asm" in result.errors
