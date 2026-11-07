"""Cross-language fixtures. These are not a blinded recovery trial."""
import collections
import json
from pathlib import Path
import random
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples/recovery-puzzle"
MAPS = [
 ["#######", "#@SD.E#", "###.###", "#.....#", "#######"],
 ["#######", "#@S...#", "#####D#", "#E....#", "#######"],
 ["#######", "#E.DS@#", "###.###", "#.....#", "#######"],
 ["#######", "#@....#", "#S###.#", "#..D.E#", "#######"],
 ["#######", "#@S#E.#", "#..D..#", "#.....#", "#######"],
 ["#######", "#@S.D.#", "#.###.#", "#....E#", "#######"],
]

def route(board):
    """Independent breadth-first route search over the documented board rules."""
    start = next((x, y, False) for y, row in enumerate(board) for x, ch in enumerate(row) if ch == "@")
    queue = collections.deque([(start, [])])
    seen = {start}
    while queue:
        (x, y, door), actions = queue.popleft()
        if board[y][x] == "E":
            return actions
        for name, dx, dy in [("up", 0, -1), ("down", 0, 1), ("left", -1, 0), ("right", 1, 0)]:
            nx, ny = x + dx, y + dy
            if not (0 <= nx < 7 and 0 <= ny < 5):
                continue
            cell = board[ny][nx]
            if cell == "#" or (cell == "D" and not door):
                continue
            state = (nx, ny, not door if cell == "S" else door)
            if state not in seen:
                seen.add(state)
                queue.append((state, actions + [name]))
    raise AssertionError("board is not solvable")

class SwitchboardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not shutil.which("clang") or not shutil.which("node"):
            raise unittest.SkipTest("clang and Node with TypeScript stripping are required")
        cls.temp = tempfile.TemporaryDirectory()
        cls.binary = Path(cls.temp.name) / "switchboard"
        subprocess.run(["clang", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                        str(EXAMPLE / "reference/switchboard.c"), "-o", str(cls.binary)], check=True, capture_output=True)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def run_game(self, engine, commands):
        argv = [str(self.binary), "--protocol"] if engine == "c" else ["node", str(EXAMPLE / "web/cli.ts")]
        result = subprocess.run(argv, input="\n".join(commands + ["quit"]) + "\n", text=True,
                                capture_output=True, timeout=15, check=True)
        return [json.loads(line) for line in result.stdout.splitlines()]

    def compare(self, commands):
        native, web = (self.run_game(engine, commands) for engine in ("c", "ts"))
        self.assertEqual(len(native), len(commands) + 1)
        self.assertEqual(native, web)
        return native

    def test_all_campaign_boards_through_normal_actions(self):
        commands = ["new campaign"]
        for index, board in enumerate(MAPS):
            commands.extend(route(board))
            if index < 5:
                commands.append("next")
        states = self.compare(commands)
        self.assertEqual(states[-1]["scene"], "campaign_complete")
        self.assertEqual(states[-1]["unlocked"], 6)
        self.assertEqual({s["board"] for s in states if s["scene"] == "board_complete"}, {1, 2, 3, 4, 5})

    def test_every_practice_board_and_undo_completion(self):
        for number, board in enumerate(MAPS, 1):
            with self.subTest(board=number):
                states = self.compare([f"new practice {number}", *route(board), "next", "undo"])
                self.assertEqual(states[-3]["scene"], "board_complete")
                self.assertEqual(states[-2]["error"], "cannot_advance")
                self.assertEqual(states[-1]["scene"], "playing")

    def test_switch_reversal_walls_and_empty_undo(self):
        states = self.compare(["new campaign", "up", "undo", "right", "left", "right", "right", "undo"])
        self.assertEqual(states[2]["error"], "blocked")
        self.assertEqual(states[3]["error"], "nothing_to_undo")
        self.assertFalse(states[-2]["door"])
        self.assertEqual(states[-2]["error"], "blocked")

    def test_restart_title_mute_and_invalid_input(self):
        states = self.compare(["left", "new practice 0", "new practice 7", "new practice 3", "mute", "left", "restart", "menu", "undo", "new campaign", "nonsense", "toString", "constructor"])
        self.assertEqual(states[1]["error"], "not_playing")
        self.assertEqual(states[2]["error"], "invalid_board")
        self.assertTrue(states[7]["muted"])
        self.assertEqual(states[7]["moves"], 0)
        self.assertEqual(states[-1]["error"], "unknown_action")

    def test_save_format_and_cross_language_cold_load_preserve_undo(self):
        with tempfile.TemporaryDirectory() as tmp:
            files = [Path(tmp) / "c.save", Path(tmp) / "ts.save"]
            commands = ["new practice 2", "mute", "right", "right", "undo", "right"]
            for engine, path in zip(("c", "ts"), files):
                self.run_game(engine, [*commands, f"save {path}"])
            self.assertEqual(files[0].read_bytes(), files[1].read_bytes())
            for path in files:
                states = self.compare([f"load {path}", "undo"])
                self.assertEqual(states[1]["moves"], 2)
                self.assertEqual(states[1]["undo"], 2)
                self.assertTrue(states[1]["muted"])
                self.assertEqual(states[2]["moves"], 1)

    def test_corrupt_and_truncated_saves_preserve_current_game(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.save"
            for content in [b"", b"SB1\n", b"SB1\n0 0 1 1 1 0 0 1 0 0\nEND 00000000\n", b"\x00SB1\n", b"x" * 20000]:
                path.write_bytes(content)
                states = self.compare(["new campaign", "right", f"load {path}"])
                self.assertEqual(states[-1]["error"], "invalid_save")
                self.assertEqual(states[-1]["moves"], 1)
                self.assertEqual(states[-1]["undo"], 1)

    def test_failed_save_preserves_old_file_and_unrelated_temp(self):
        with tempfile.TemporaryDirectory() as tmp:
            for engine in ("c", "ts"):
                path = Path(tmp) / f"{engine}.save"
                old = self.run_game(engine, ["new campaign", f"save {path}"])
                self.assertIsNone(old[-1]["error"])
                before = path.read_bytes()
                temp = path.with_name(path.name + ".tmp")
                temp.write_text("unrelated file")
                state = self.run_game(engine, ["new practice 6", f"save {path}"])[-1]
                self.assertEqual(state["error"], "save_failed")
                self.assertEqual(path.read_bytes(), before)
                self.assertEqual(temp.read_text(), "unrelated file")

    def test_checksummed_impossible_states_cannot_advance_past_final_board(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "invalid.save"
            for header in ["0 5 2 5 3 1 11 6 0 0", "0 5 1 1 1 0 0 1 0 0", "0 0 1 5 1 1 4 1 0 0"]:
                body = "SB1\n" + header + "\n"
                value = 2166136261
                for byte in body.encode():
                    value = ((value ^ byte) * 16777619) & 0xffffffff
                path.write_text(body + f"END {value:08x}\n")
                states = self.compare(["new campaign", f"load {path}", "next"])
                self.assertEqual(states[-2]["error"], "invalid_save")
                self.assertEqual(states[-1]["error"], "cannot_advance")
                self.assertEqual(states[-1]["board"], 1)

    def test_seeded_controller_exploration_and_history_bound(self):
        rng = random.Random(271828)
        commands = ["new practice 4"]
        commands += [rng.choice(["up", "down", "left", "right", "undo", "restart"]) for _ in range(600)]
        commands += ["restart"] + [action for _ in range(90) for action in ("right", "left")]
        commands += ["undo"] * 130
        states = self.compare(commands)
        self.assertEqual(max(state["undo"] for state in states), 128)
        self.assertEqual(states[-1]["error"], "nothing_to_undo")

    def test_cold_restore_at_history_capacity(self):
        with tempfile.TemporaryDirectory() as tmp:
            for engine in ("c", "ts"):
                path = Path(tmp) / f"{engine}.save"
                self.run_game(engine, ["new campaign", *(["right", "left"] * 80), f"save {path}"])
                states = self.compare([f"load {path}", *(["undo"] * 129)])
                self.assertEqual(states[1]["undo"], 128)
                self.assertEqual(states[-2]["moves"], 32)
                self.assertEqual(states[-1]["error"], "nothing_to_undo")

if __name__ == "__main__":
    unittest.main()
