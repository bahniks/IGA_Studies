#! python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import re
import unicodedata


DATA_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = DATA_DIR / "extracted"

SECTION_COLUMNS = {
    "Login": ["id", "login_token_1", "login_token_2", "coordination_role"],
    "Groups": ["id", "selected_groups"],
    "Coordination Control Questions": ["id", "question_number", "answer"],
    "CoordinationGame": ["id", "block", "trial", "decision", "prediction_percent"],
    "Coordination Results": ["id", "other_player_decision"],
    "Kontrolní otázky k úloze vstupu na trh": ["id", "question_number", "answer"],
    "MarketEntryQuiz": ["id", "block", "q1", "q2", "q3", "q4", "q5", "quiz_score", "confidence"],
    "MarketEntryGame": ["id", "block", "decision"],
    "Groups Results": ["id", "group_1", "group_2", "group_3"],
    "Trust Control Questions": ["id", "question_number", "answer"],
    "Trust": ["id", "block", "partner_id", "partner_groups", "send_a", "send_b_if0", "send_b_if8", "send_b_if16", "send_b_if24", "send_b_if32", "send_b_if40", "prediction"],
    "FiresInstructionsAndUnderstanding": ["id", "question_number", "answer"],
    "FiresRound": ["id", "trial", "round_condition", "chosen_condition"],
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
    "FiresQuestionnaire": ["id", "item", "answer", "statement"],
    "ProductsInstructionsAndUnderstanding": ["id", "question_number", "answer"],
    "Products": ["id", "order", "product_code", "label", "size", "category", "condition", "price_level", "shown_price", "choice", "rt_seconds"],
    "Numeracy": ["id", "item", "answer"],
    "Narcissism": ["id", "item", "answer"],
    "SalesProneness": ["id", "item", "answer"],
    "TransactionValue": ["id", "item", "answer"],
    "Demographics": ["id", "sex", "age", "language", "student", "field"],
    "Comments": ["id", "comment"],
    "Final Results": ["id", "result_1", "result_2", "result_3", "result_4", "result_5", "result_6", "result_7", "result_8", "result_9", "result_10"],
    "Ending": ["id", "reward", "rounded_reward"],
    "Focus time": ["id", "trial", "content_type", "focus_time", "focus_proportion", "toggle_times"],
}

INLINE_SECTION_NAMES = {"Focus time"}

EVENT_FILENAME = "event_timeline.tsv"
FRAME_TIME_SUMMARY_FILENAME = "frame_time_summary.tsv"
EXCEPTIONS_FILENAME = "exceptions_results.tsv"
SECTIONS_SUMMARY_FILENAME = "sections_summary.tsv"
UNKNOWN_ROWS_FILENAME = "unknown_rows.tsv"
EXCEPTIONS_COLUMNS = ["source_file", "participant_id", "timestamp", "traceback"]

UUID_RE = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")


def parse_participant_id_from_filename(path: Path) -> str:
    stem = path.stem
    parts = stem.split("_", 4)
    if len(parts) == 5 and UUID_RE.match(parts[4]):
        return parts[4]
    return ""


def parse_event_line(line: str) -> tuple[str, float, str, str] | None:
    for prefix in ("time: ", "resume: ", "restart: "):
        if line.startswith(prefix):
            event_kind = prefix[:-2]
            payload = line[len(prefix):]
            pieces = payload.split("\t")
            if len(pieces) < 3:
                return None
            try:
                timestamp = float(pieces[0])
            except ValueError:
                return None
            order = pieces[1]
            frame_or_reason = pieces[2]
            return event_kind, timestamp, order, frame_or_reason
        return None


def read_text_best_effort(path: Path) -> str:
    raw = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-8", "cp1250", "latin-1"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


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


def parse_file(
    path: Path,
    section_rows: dict[str, list[dict[str, object]]],
    event_rows: list[list[str]],
    exception_rows: list[list[str]],
    unknown_rows: list[list[str]],
) -> None:
    participant_id = parse_participant_id_from_filename(path)
    lines = read_text_best_effort(path).splitlines()

    previous_time_by_file = None
    current_section = ""
    row_counter_by_section = defaultdict(int)

    i = 0
    while i < len(lines):
        line = lines[i].rstrip("\r\n")
        stripped = line.strip()

        if not stripped:
            current_section = ""
            i += 1
            continue

        if stripped.startswith("gui_exception\t"):
            parts = stripped.split("\t", 2)
            timestamp = parts[1] if len(parts) > 1 else ""
            traceback = parts[2].replace(" | ", "\n").strip() if len(parts) > 2 else ""
            exception_rows.append([path.name, participant_id, timestamp, traceback])
            i += 1
            continue

        event_data = parse_event_line(stripped)
        if event_data is not None:
            event_kind, timestamp, order, frame_or_reason = event_data
            delta = "" if previous_time_by_file is None else str(timestamp - previous_time_by_file)
            event_rows.append([
                path.name,
                participant_id,
                event_kind,
                order,
                frame_or_reason,
                str(timestamp),
                delta,
            ])
            previous_time_by_file = timestamp
            current_section = ""
            i += 1
            continue

        if "\t" not in stripped:
            current_section = stripped
            i += 1
            continue

        fields = stripped.split("\t")
        if fields and fields[0] in INLINE_SECTION_NAMES:
            section = fields[0]
            row_counter_by_section[section] += 1
            section_rows[section].append(
                {
                    "source_file": path.name,
                    "participant_id": participant_id,
                    "row_in_section": row_counter_by_section[section],
                    "fields": normalize_row(section, "\t".join(fields[1:])),
                }
            )
            current_section = section
            i += 1
            continue

        if current_section:
            row_counter_by_section[current_section] += 1
            section_rows[current_section].append(
                {
                    "source_file": path.name,
                    "participant_id": participant_id,
                    "row_in_section": row_counter_by_section[current_section],
                    "fields": normalize_row(current_section, stripped),
                }
            )
        else:
            unknown_rows.append([path.name, participant_id, stripped])

        i += 1


def write_tsv(path: Path, header: list[str], rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as out:
        lines = ["\t".join(header)]
        lines.extend("\t".join(str(cell) for cell in row) for row in rows)
        out.write("\n".join(lines))


def build_frame_summary(event_rows: list[list[str]]) -> list[list[str]]:
    by_frame = defaultdict(list)
    for _, _, event_kind, _, frame, _, delta in event_rows:
        if event_kind == "time" and delta:
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


def slugify_section_name(section: str) -> str:
    normalized = unicodedata.normalize("NFKD", section)
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "_", ascii_only).strip("_").lower()
    return cleaned or "unnamed_section"


def build_header_for_section(section: str, width: int) -> list[str]:
    base = ["source_file", "participant_id", "row_in_section"]
    known = SECTION_COLUMNS.get(section)
    if known:
        if len(known) >= width:
            return base + known[:width]
        extra = [f"extra_{i}" for i in range(1, width - len(known) + 1)]
        return base + known + extra
    return base + [f"value_{i}" for i in range(1, width + 1)]


def write_section_files(section_rows: dict[str, list[dict[str, object]]]) -> list[list[str]]:
    summary_rows: list[list[str]] = []
    for section in sorted(section_rows):
        rows = section_rows[section]
        if not rows:
            continue

        max_width = max(len(item["fields"]) for item in rows)
        header = build_header_for_section(section, max_width)
        output_filename = f"section_{slugify_section_name(section)}.tsv"

        out_rows: list[list[str]] = []
        for item in rows:
            fields = pad_or_extend(list(item["fields"]), max_width)
            out_rows.append([
                str(item["source_file"]),
                str(item["participant_id"]),
                str(item["row_in_section"]),
            ] + fields)

        write_tsv(OUTPUT_DIR / output_filename, header, out_rows)
        summary_rows.append([section, output_filename, str(len(rows)), str(max_width)])
    return summary_rows


def main() -> None:
    section_rows: dict[str, list[dict[str, object]]] = defaultdict(list)
    event_rows: list[list[str]] = []
    exception_rows: list[list[str]] = []
    unknown_rows: list[list[str]] = []

    for data_file in sorted(DATA_DIR.glob("*.txt")):
        parse_file(data_file, section_rows, event_rows, exception_rows, unknown_rows)

    section_summary_rows = write_section_files(section_rows)
    write_tsv(
        OUTPUT_DIR / SECTIONS_SUMMARY_FILENAME,
        ["section", "output_file", "rows", "max_fields"],
        section_summary_rows,
    )

    write_tsv(
        OUTPUT_DIR / EVENT_FILENAME,
        ["source_file", "participant_id", "event_kind", "order", "frame_or_reason", "timestamp", "elapsed_from_previous"],
        event_rows,
    )

    frame_summary_rows = build_frame_summary(event_rows)
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

    write_tsv(
        OUTPUT_DIR / UNKNOWN_ROWS_FILENAME,
        ["source_file", "participant_id", "raw_line"],
        unknown_rows,
    )

    print(f"Extracted files written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

            
