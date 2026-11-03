"""Token labels -> character spans -> signed EPS values -> one primary value per filing.

The classifier outputs span and type only, with no sign and no period, so both are derived here.
PRIMARY_RULE was chosen on train+val gold before the test set was scored.
"""
import re
from collections import Counter

NUM_RE = re.compile(r"\d[\d,]*(?:\.\d+)?|\.\d+")


def bio_spans(labels, offsets, label_names):
    spans, cur = [], None
    for k, l in enumerate(labels):
        tag = label_names[l]
        a, b = offsets[k]
        if b <= a:
            continue
        if tag == "O":
            if cur: spans.append(tuple(cur)); cur = None
            continue
        bi, typ = tag.split("-", 1)
        if bi == "B" or cur is None or cur[2] != typ or a > cur[1] + 1:
            if cur: spans.append(tuple(cur))
            cur = [a, b, typ]
        else:
            cur[1] = b
    if cur: spans.append(tuple(cur))
    return spans


def tighten(text, s, e):
    m = NUM_RE.search(text, s, e)
    if not m:
        return None
    a, b = m.start(), m.end()
    # if the model cut the number short (e.g. tagged '0.' of '0.71'), extend to the full number
    while b < len(text) and (text[b].isdigit() or (text[b] == "." and b + 1 < len(text) and text[b + 1].isdigit())):
        b += 1
    while a > 0 and (text[a - 1].isdigit() or text[a - 1] == "."):
        a -= 1
    return a, b


_NEUTRAL = re.compile(
    r"(income|earnings|profit)\s*\(?\s*/?\s*\(?loss\)?"      # income (loss), earnings/(loss)
    r"|\(?loss\)?\s*/?\s*\(?\s*(income|earnings)"            # (loss) income
    r"|\(?gains?\)?\s*/?\s*\(?loss(es)?\)?", re.I)          # (gain)/loss, gain (loss)
_POSITIVE_AFTER_LOSS = re.compile(r"\b(net )?(income|earnings|profit)\b|\bEPS\b", re.I)


def signed_value(text, s, e):
    raw = text[s:e].replace(",", "")
    try:
        v = float(raw)
    except ValueError:
        return None
    if re.match(r"\s*cents\b", text[e:e + 12], re.I):
        v /= 100.0
    left = text[max(0, s - 3):s].replace("$", "").replace(" ", "")
    right = text[e:e + 3].lstrip()
    # "(0.42)" / "$(0.42)" / "($0.42)" are negative only when the parenthesis closes right after the number;
    # "($0.50 per diluted share)" is just a wrapper.
    if left.endswith("(") and right.startswith(")"):
        return -v
    # a minus sign must touch the number or its "$" ("-0.42", "-$0.42", "$-0.42"); "-- $0.50" is a dash
    tight = text[max(0, s - 2):s]
    if tight.endswith(("-", "−")) and not tight.endswith(("--", "−−")) or tight in ("-$", "−$"):
        return -v
    # textual loss: look back to the sentence start. Line breaks end the lookback inside table rows and
    # after a line that ends a sentence; otherwise a sentence wrapped across lines is followed back.
    line_start = text.rfind("\n", 0, s) + 1
    line_end = text.find("\n", s)
    in_table = " | " in text[line_start:line_end if line_end >= 0 else len(text)]
    prev_end = text[:max(0, line_start - 1)].rstrip()[-1:]
    if in_table or prev_end in (".", "!", "?", ":", ")", "") or line_start == 0:
        lo = max(line_start, text.rfind(". ", 0, s) + 2, s - 200)
    else:
        lo = max(text.rfind(". ", 0, s) + 2, s - 200)
    ctx = text[lo:s]
    if re.search(r"\blosse?s?\b", ctx, re.I) and not _NEUTRAL.search(ctx):
        tail = ctx[ctx.lower().rfind("loss"):]
        if not _POSITIVE_AFTER_LOSS.search(tail):
            return -v
    return v


def decode_mentions(text, spans):
    out = []
    for s, e, typ in spans:
        t = tighten(text, s, e)
        if t is None:
            continue
        a, b = t
        v = signed_value(text, a, b)
        if v is None:
            continue
        out.append({"start": a, "end": b, "type": typ, "value": round(v, 4), "span_text": text[a:b]})
    return out


def _is_table_row(text, s):
    ls = text.rfind("\n", 0, s) + 1
    return " | " in text[ls:text.find("\n", s) if text.find("\n", s) > 0 else len(text)]


def _first_cell(text, s):
    """The first numeric column is assumed to be the current period."""
    ls = text.rfind("\n", 0, s) + 1
    prefix = text[ls:s]
    cells = prefix.split(" | ")
    return len(cells) >= 2 and not any(NUM_RE.search(c) for c in cells[1:-1])


def pick_primary(text, mentions, rule):
    dil = [m for m in mentions if m["type"] == "EPS_GAAP_DILUTED"]
    if not dil:
        return None
    if rule == "first":
        return dil[0]["value"]
    if rule == "mode":
        c = Counter(m["value"] for m in dil)
        top = max(c.values())
        return next(m["value"] for m in dil if c[m["value"]] == top)  # tie -> earliest
    if rule == "first_table_first_cell":
        tab = [m for m in dil if _is_table_row(text, m["start"]) and _first_cell(text, m["start"])]
        return (tab or dil)[0]["value"]
    if rule == "mode_first_cells":
        # values in the current-period column of tables, plus narrative mentions; most frequent wins
        pool = [m for m in dil if not _is_table_row(text, m["start"]) or _first_cell(text, m["start"])]
        pool = pool or dil
        c = Counter(m["value"] for m in pool)
        top = max(c.values())
        return next(m["value"] for m in pool if c[m["value"]] == top)
    if rule == "header_current_column":
        # pick the first GAAP-diluted table value whose column the table header marks as the latest year;
        # fall back to first_table_first_cell when no header can be read
        for m in dil:
            if not _is_data_row(text, m["start"]):
                continue
            col = _cell_index(text, m["start"])
            cur = _current_column(text, m["start"])
            if cur is not None and col == cur:
                return m["value"]
        return pick_primary(text, mentions, "first_table_first_cell")
    raise ValueError(rule)


_YEAR = re.compile(r"\b(?:19|20)\d{2}\b")
_HDR_NUM = re.compile(r"\d[\d,]*\.\d+|\d{1,3},\d{3}")


def _cell_index(text, s):
    ls = text.rfind("\n", 0, s) + 1
    cells = text[ls:s].split(" | ")
    return sum(1 for c in cells[1:-1] if NUM_RE.search(c))


def _current_column(text, s, max_lines=80):
    ls = text.rfind("\n", 0, s)
    lines = text[:max(ls, 0)].split("\n")
    for line in reversed(lines[-max_lines:]):
        if _HDR_NUM.search(line):
            continue
        cells = [c for c in line.split(" | ")]
        year_cells = [c for c in cells if _YEAR.search(c)]
        if len(year_cells) < 2 or len(line) > 200:
            continue  # prose sentences that mention years are not headers
        years = [max(int(y) for y in _YEAR.findall(c)) for c in year_cells]
        return years.index(max(years))
    return None


def _is_data_row(text, s):
    """Bullets render as two-cell rows, so they are excluded."""
    ls = text.rfind("\n", 0, s) + 1
    le = text.find("\n", s)
    line = text[ls:le if le >= 0 else len(text)]
    return " | " in line and not line.lstrip().startswith(("•", "◦", "·", "▪", "-"))


RULES = ["first", "mode", "first_table_first_cell", "mode_first_cells", "header_current_column"]
PRIMARY_RULE = "first_table_first_cell"  # chosen on train+val gold (35/35; other rules 34/35, all missing AZZ)
