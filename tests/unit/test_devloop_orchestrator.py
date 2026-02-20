from collections import deque
from pathlib import Path
import subprocess
from types import SimpleNamespace

from pyignite.devloop.orchestrator import run_dev_loop
from pyignite.tooling import CommandResult, ToolKey


class FakeProcess:
    def __init__(self) -> None:
        self._running = True
        self.terminated = 0
        self.killed = 0

    def poll(self) -> int | None:
        return None if self._running else 0

    def terminate(self) -> None:
        self.terminated += 1
        self._running = False

    def wait(self, timeout: int) -> int:
        _ = timeout
        return 0

    def kill(self) -> None:
        self.killed += 1
        self._running = False


class FakePopenFactory:
    def __init__(self) -> None:
        self.calls: list[tuple[tuple[str, ...], Path]] = []
        self.processes: list[FakeProcess] = []

    def __call__(self, command: list[str], cwd: Path) -> FakeProcess:
        process = FakeProcess()
        self.calls.append((tuple(command), cwd))
        self.processes.append(process)
        return process


class FakeAdapters:
    def __init__(
        self, root_dir: Path, check_results: list[CommandResult], *, stop_on_first: bool = True
    ) -> None:
        self.config = SimpleNamespace(
            root_dir=root_dir,
            dev=SimpleNamespace(watch=("src", "tests"), debounce_ms=120),
            run=SimpleNamespace(app="myapi.main:app", host="127.0.0.1", port=8000),
            checks=SimpleNamespace(stop_on_first_failure=stop_on_first),
        )
        self._check_results = deque(check_results)
        self.run_calls: list[tuple[ToolKey, tuple[str, ...]]] = []

    def command(self, key: ToolKey, args: tuple[str, ...] = ()) -> tuple[str, ...]:
        assert key == ToolKey.RUNNING
        return ("uv", "run", "uvicorn", *args)

    def run(self, key: ToolKey, args: tuple[str, ...] = ()) -> CommandResult:
        self.run_calls.append((key, args))
        return self._check_results.popleft()


def _result(exit_code: int, stdout: str = "", stderr: str = "") -> CommandResult:
    return CommandResult(command=("tool",), exit_code=exit_code, stdout=stdout, stderr=stderr)


def test_dev_loop_single_burst_triggers_one_reload_and_check_pipeline(tmp_path: Path) -> None:
    adapters = FakeAdapters(
        root_dir=tmp_path,
        check_results=[_result(0), _result(0), _result(0)],
    )
    popen_factory = FakePopenFactory()

    src_file = tmp_path / "src" / "app.py"
    tests_file = tmp_path / "tests" / "test_api.py"
    src_file.parent.mkdir(parents=True, exist_ok=True)
    tests_file.parent.mkdir(parents=True, exist_ok=True)

    def watcher(*paths: Path, debounce: int):
        assert paths == (tmp_path / "src", tmp_path / "tests")
        assert debounce == 120
        yield {
            (object(), str(src_file)),
            (object(), str(tests_file)),
        }

    run_dev_loop(adapters, watch_factory=watcher, popen_factory=popen_factory)

    assert len(popen_factory.calls) == 2
    assert adapters.run_calls == [
        (ToolKey.LINTING, ("check", ".")),
        (ToolKey.TYPING, ()),
        (ToolKey.TESTING, ()),
    ]


def test_dev_loop_ignores_cache_noise_and_stays_stable_after_failures(tmp_path: Path) -> None:
    adapters = FakeAdapters(
        root_dir=tmp_path,
        check_results=[
            _result(1),
            _result(0),
            _result(0),
            _result(0),
        ],
    )
    popen_factory = FakePopenFactory()

    changed_file = tmp_path / "src" / "service.py"
    cache_file = tmp_path / "src" / "__pycache__" / "service.cpython-312.pyc"
    changed_file.parent.mkdir(parents=True, exist_ok=True)
    cache_file.parent.mkdir(parents=True, exist_ok=True)

    def watcher(*paths: Path, debounce: int):
        _ = (paths, debounce)
        yield {(object(), str(cache_file))}
        yield {(object(), str(changed_file))}
        yield {(object(), str(changed_file))}

    run_dev_loop(adapters, watch_factory=watcher, popen_factory=popen_factory)

    assert len(popen_factory.calls) == 3
    assert adapters.run_calls == [
        (ToolKey.LINTING, ("check", ".")),
        (ToolKey.LINTING, ("check", ".")),
        (ToolKey.TYPING, ()),
        (ToolKey.TESTING, ()),
    ]


def test_dev_loop_kills_process_if_terminate_times_out(tmp_path: Path) -> None:
    adapters = FakeAdapters(root_dir=tmp_path, check_results=[])

    class SlowProcess(FakeProcess):
        def __init__(self) -> None:
            super().__init__()
            self.wait_calls = 0

        def wait(self, timeout: int) -> int:
            self.wait_calls += 1
            if self.terminated == 1 and self.wait_calls == 1:
                raise subprocess.TimeoutExpired(cmd="cmd", timeout=timeout)
            return 0

    class SlowPopenFactory(FakePopenFactory):
        def __call__(self, command: list[str], cwd: Path) -> SlowProcess:
            process = SlowProcess()
            self.calls.append((tuple(command), cwd))
            self.processes.append(process)
            return process

    popen_factory = SlowPopenFactory()

    def watcher(*paths: Path, debounce: int):
        _ = (paths, debounce)
        return
        yield

    run_dev_loop(adapters, watch_factory=watcher, popen_factory=popen_factory)

    assert popen_factory.processes[-1].killed == 1
