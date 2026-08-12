PY := .venv/bin/python

.PHONY: run test lint demo

run:
	$(PY) -m academy.ui

demo:
	$(PY) -c "from academy.sandbox import Sandbox; s=Sandbox(); s.executor.load_asm('mov rax,5\nadd rax,3'); print(s.execute('run').text)"

test:
	$(PY) -m pytest -q

lint:
	.venv/bin/ruff check academy tests
