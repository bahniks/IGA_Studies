#! python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import re


DATA_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = DATA_DIR / "extracted"

SECTION_COLUMNS = {
    "Login": [
        "id",
        "condition",
        "distraction_1",
        "distraction_2",
        "distraction_3",
        "distraction_4",
        "distraction_5",
        "distraction_6",
        "distraction_7",
        "distraction_8",
    ],
    "Attention": ["id", "trial", "attention_to_video", "attention_drift"],
    "Game": [
        "id",
        "game_number",
        "video_number",
        "pressed_keys",
        "max_time_between_keys",
        "score_end",
        "start_time",
        "end_time",
    ],
    "Focus time": ["id", "trial", "content_type", "focus_time", "focus_proportion", "toggle_times"],
    "EndQuestionnaire": [
        "id",
        "overall_attention",
        "attention_drift_frequency",
        "intentional_refocus_frequency",
        "used_strategy",
        "strategy_usefulness",
        "strategy_description",
    ],
    "UPPS": ["id", "item", "answer"],
    "SCI": ["id", "sleep_1", "sleep_2", "sleep_3", "sleep_4", "sleep_5", "sleep_6", "sleep_7", "sleep_8"],
    "SAMS": ["id", "item", "answer", "statement"],
    "Mindset": ["id", "item", "answer", "statement"],
    "Attention checks": ["id", "questionnaire", "correct"],
    "Boost understanding": ["id", "trial", "answer"],
    "Boost plan choice": ["id", "when_part", "then_part"],
    "Quiz": ["id", "trial", "question", "answer", "correct", "total_correct"],
    "Postdiction": ["id", "estimate_correct", "actual_correct"],
    "Demographics": ["id", "sex", "age", "language", "student", "field"],
    "Comments": ["id", "comment"],
    "Ending": ["id", "reward"],
    "FiresRound": ["id", "trial", "condition", "chosen_condition"],
    "FiresGame": [
        "id",
        "frame",
        "round_condition",
        "chosen_condition",
        "score_halers",
        "reward_crowns",
        "time_left_seconds",
        "fires_spawned",
        "fires_remaining",
        "sprinkler_used",
        "completed_valves",
        "mouse_left_seconds",
        "mouse_right_seconds",
        "mouse_left_proportion",
        "mouse_right_proportion",
    ],
}

SECTION_FILENAME = {name: f"{name.lower().replace(' ', '_')}_results.tsv" for name in SECTION_COLUMNS}
SECTION_FILENAME["Focus time"] = "focus_time_results.tsv"

TIME_FILENAME = "time_results.tsv"
FRAME_TIME_SUMMARY_FILENAME = "frame_time_summary.tsv"
EXCEPTIONS_FILENAME = "exceptions_results.tsv"
EXCEPTIONS_COLUMNS = ["source_file", "participant_id", "timestamp", "traceback"]

UUID_RE = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")


def parse_participant_id_from_filename(path: Path) -> str:
    stem = path.stem
    parts = stem.split("_", 4)
    if len(parts) == 5 and UUID_RE.match(parts[4]):
        return parts[4]
    return ""


def parse_time_line(line: str) -> tuple[float, str, str] | None:
    if not line.startswith("time: "):
        return None
    payload = line[len("time: "):]
    pieces = payload.split("\t")
    if len(pieces) < 3:
        return None
    try:
        timestamp = float(pieces[0])
    except ValueError:
        return None
    order = pieces[1]
    frame = pieces[2]
    return timestamp, order, frame


def pad_or_extend(fields: list[str], width: int) -> list[str]:
    if len(fields) >= width:
        return fields
    return fields + [""] * (width - len(fields))


def normalize_row(section: str, row: str) -> list[str]:
    fields = row.split("\t")
    expected_cols = SECTION_COLUMNS.get(section, [])
    expected_width = len(expected_cols)
    if expected_width == 0:
        return fields
    return pad_or_extend(fields, expected_width)


def parse_file(path: Path, section_rows: dict[str, list[list[str]]], time_rows: list[list[str]], exception_rows: list[list[str]]) -> None:
    participant_id = parse_participant_id_from_filename(path)
    lines = path.read_text(encoding="utf-8").splitlines()

    previous_time = None
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if not line:
            i += 1
            continue

        if line.startswith("gui_exception	"):
            parts = line.split("\t", 2)
            timestamp = parts[1] if len(parts) > 1 else ""
            traceback = parts[2].replace(" | ", "\n").strip() if len(parts) > 2 else ""
            exception_rows.append([path.name, participant_id, timestamp, traceback])
            i += 1
            continue

        time_data = parse_time_line(line)
        if time_data is not None:
            timestamp, order, frame = time_data
            delta = "" if previous_time is None else str(timestamp - previous_time)
            time_rows.append([path.name, participant_id, order, frame, str(timestamp), delta])
            previous_time = timestamp
            i += 1
            continue

        if line.startswith("Focus time\t"):
            section = "Focus time"
            raw_fields = line.split("\t")
            section_rows[section].append(normalize_row(section, "\t".join(raw_fields[1:])))
            i += 1
            continue

        if line in SECTION_COLUMNS:
            section = line
            i += 1
            while i < len(lines):
                candidate = lines[i].strip()
                if not candidate:
                    i += 1
                    break
                if candidate.startswith("time: "):
                    break
                if candidate in SECTION_COLUMNS:
                    break
                section_rows[section].append(normalize_row(section, candidate))
                i += 1
            continue

        i += 1


def write_tsv(path: Path, header: list[str], rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as out:
        lines = ["\t".join(header)]
        lines.extend("\t".join(row) for row in rows)
        out.write("\n".join(lines))


def build_frame_summary(time_rows: list[list[str]]) -> list[list[str]]:
    by_frame = defaultdict(list)
    for _, _, _, frame, _, delta in time_rows:
        if delta:
            try:
                by_frame[frame].append(float(delta))
            except ValueError:
                pass

    rows = []
    for frame in sorted(by_frame):
        values = by_frame[frame]
        if not values:
            continue
        avg_seconds = sum(values) / len(values)
        rows.append([frame, str(len(values)), str(avg_seconds), str(avg_seconds / 60.0)])
    return rows


def main() -> None:
    section_rows: dict[str, list[list[str]]] = {name: [] for name in SECTION_COLUMNS}
    time_rows: list[list[str]] = []
    exception_rows: list[list[str]] = []

    for data_file in sorted(DATA_DIR.glob("*.txt")):
        parse_file(data_file, section_rows, time_rows, exception_rows)

    for section_name, rows in section_rows.items():
        if not rows:
            continue
        filename = SECTION_FILENAME[section_name]
        write_tsv(OUTPUT_DIR / filename, SECTION_COLUMNS[section_name], rows)

    write_tsv(
        OUTPUT_DIR / TIME_FILENAME,
        ["source_file", "participant_id", "order", "frame", "timestamp", "elapsed_from_previous"],
        time_rows,
    )

    frame_summary_rows = build_frame_summary(time_rows)
    write_tsv(
        OUTPUT_DIR / FRAME_TIME_SUMMARY_FILENAME,
        ["frame", "n", "avg_seconds", "avg_minutes"],
        frame_summary_rows,
    )

    write_tsv(
        OUTPUT_DIR / EXCEPTIONS_FILENAME,
        EXCEPTIONS_COLUMNS,
        exception_rows,
    )

    print(f"Extracted files written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

            
