"""Document-style HTML for the Report page, the PDF export and the saved HTML.

Everything here is plain Python (no PyQt), so it can be tested on its own.
The markup sticks to tables and inline styles because Qt's QTextDocument only
understands a small part of HTML/CSS.
"""
import html
import json
from datetime import date, datetime

SYSTEM_NAME = "HIV ARV Allocation and Management System"
NAVY = "#123B69"
BLUE = "#1769D2"
INK = "#1F2A37"
MUTED = "#64748B"
LINE = "#D5DEEA"
LABEL_BG = "#F5F8FC"
SECTION_BG = "#EAF2FC"
LABEL_INK = "#244B7A"

# Fields that change automatically and would only add noise to a change list.
SKIP_IN_DIFF = {"age", "date_registered", "patient_id"}


# ---------------------------------------------------------------- helpers
def esc(value):
    return html.escape(str(value))


def blank(value):
    return value is None or str(value).strip() == ""


def show(value):
    """Escaped text for a table cell; empty values become a dash."""
    if blank(value):
        return "&mdash;"
    return esc(value).replace("\r\n", "\n").replace("\n", "<br>")


def humanize(key):
    return str(key).replace("_", " ").strip().title()


def fmt_value(value):
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return value


def today_text():
    return date.today().strftime("%B %d, %Y").replace(" 0", " ")


def spacer(points=6):
    return f'<p style="margin:0;font-size:{points}pt;">&nbsp;</p>'


# ----------------------------------------------------------- page pieces
def wrap(body):
    return (
        "<html><head><meta charset='utf-8'><style>"
        f"body{{font-family:'Segoe UI',Arial,sans-serif;font-size:10pt;color:{INK};}}"
        "p{margin-top:0;margin-bottom:8px;}"
        "</style></head><body>" + body + "</body></html>"
    )


def letterhead(label):
    return (
        '<table width="100%" cellspacing="0" cellpadding="14">'
        f'<tr><td bgcolor="{NAVY}" style="background-color:{NAVY};">'
        f'<span style="font-size:15pt;font-weight:bold;color:#FFFFFF;">{esc(SYSTEM_NAME)}</span><br>'
        '<span style="font-size:9pt;color:#CFE3FF;">Confidential patient care documentation</span></td>'
        f'<td bgcolor="{NAVY}" align="right" style="background-color:{NAVY};">'
        f'<span style="font-size:10pt;font-weight:bold;color:#FFFFFF;">{esc(label)}</span><br>'
        f'<span style="font-size:9pt;color:#CFE3FF;">{esc(today_text())}</span></td></tr></table>'
        '<table width="100%" cellspacing="0" cellpadding="0"><tr>'
        f'<td bgcolor="{BLUE}" height="4" style="background-color:{BLUE};font-size:2pt;">&nbsp;</td>'
        '</tr></table>'
    )


def title_block(title, subtitle=""):
    out = (
        f'<h1 align="center" style="font-size:19pt;color:{NAVY};margin-top:20px;'
        f'margin-bottom:2px;">{esc(title)}</h1>'
    )
    if subtitle:
        out += f'<p align="center" style="color:{MUTED};font-size:9pt;margin-bottom:14px;">{esc(subtitle)}</p>'
    return out


def section(title):
    return (
        spacer(5)
        + '<table width="100%" cellspacing="0" cellpadding="7"><tr>'
        f'<td bgcolor="{SECTION_BG}" style="background-color:{SECTION_BG};color:{NAVY};'
        f'font-weight:bold;font-size:10.5pt;">{esc(title)}</td></tr></table>'
        + spacer(3)
    )


def fields(rows, label_width=30):
    """Two-column label/value table. rows = [(label, value), ...]."""
    out = [
        f'<table width="100%" border="1" cellspacing="0" cellpadding="7" '
        f'style="border-color:{LINE};border-collapse:collapse;">'
    ]
    for label, value in rows:
        out.append(
            f'<tr><td width="{label_width}%" bgcolor="{LABEL_BG}" '
            f'style="background-color:{LABEL_BG};color:{LABEL_INK};font-weight:bold;">'
            f'{esc(label)}</td><td>{show(value)}</td></tr>'
        )
    out.append("</table>")
    return "".join(out)


def grid(headers, rows, widths=None, small=False):
    """Real data table with a header row."""
    size = "8.5pt" if small else "9.5pt"
    out = [
        f'<table width="100%" border="1" cellspacing="0" cellpadding="6" '
        f'style="border-color:{LINE};border-collapse:collapse;font-size:{size};">',
        "<tr>",
    ]
    for index, head in enumerate(headers):
        width = f' width="{widths[index]}%"' if widths else ""
        out.append(
            f'<td{width} bgcolor="{NAVY}" style="background-color:{NAVY};color:#FFFFFF;'
            f'font-weight:bold;">{esc(head)}</td>'
        )
    out.append("</tr>")
    for number, row in enumerate(rows):
        shade = "#FFFFFF" if number % 2 == 0 else LABEL_BG
        out.append("<tr>")
        for cell in row:
            if isinstance(cell, _Raw):
                out.append(f'<td bgcolor="{shade}" style="background-color:{shade};">{cell.text}</td>')
            else:
                out.append(f'<td bgcolor="{shade}" style="background-color:{shade};">{show(cell)}</td>')
        out.append("</tr>")
    out.append("</table>")
    return "".join(out)


class _Raw:
    """Marks a table cell that already contains safe HTML."""
    def __init__(self, text):
        self.text = text


def badge(text, color):
    return _Raw(f'<span style="color:{color};font-weight:bold;">{esc(text)}</span>')


def tiles(items):
    """Row of summary tiles. items = [(label, value, color), ...]."""
    width = int(100 / max(len(items), 1))
    out = ['<table width="100%" cellspacing="6" cellpadding="10"><tr>']
    for label, value, _color in items:
        color = NAVY
        out.append(
            f'<td width="{width}%" align="center" bgcolor="{LABEL_BG}" '
            f'style="background-color:{LABEL_BG};">'
            f'<span style="font-size:18pt;font-weight:bold;color:{color};">{esc(value)}</span><br>'
            f'<span style="font-size:8.5pt;color:{MUTED};">{esc(label)}</span></td>'
        )
    out.append("</tr></table>")
    return "".join(out)


def paragraph(text, bold=False):
    weight = "font-weight:bold;" if bold else ""
    return f'<p style="margin-bottom:9px;line-height:140%;{weight}">{show_inline(text)}</p>'


def show_inline(text):
    return esc(text).replace("\n", "<br>")


def signature_block(name, role_line):
    return (
        spacer(14)
        + '<table width="100%" cellspacing="0" cellpadding="4"><tr>'
        '<td width="48%">&nbsp;<br>&nbsp;<br>'
        f'<span style="color:{MUTED};">______________________________</span><br>'
        f'<b>{esc(name)}</b><br><span style="color:{MUTED};font-size:9pt;">{esc(role_line)}</span></td>'
        '<td width="4%">&nbsp;</td>'
        '<td width="48%">&nbsp;<br>&nbsp;<br>'
        f'<span style="color:{MUTED};">______________________________</span><br>'
        f'<b>Date signed</b></td></tr></table>'
    )


def footer(generated_by):
    return (
        spacer(10)
        + f'<table width="100%" cellspacing="0" cellpadding="0"><tr><td bgcolor="{LINE}" height="1" '
        'style="font-size:1pt;">&nbsp;</td></tr></table>'
        f'<p style="font-size:8.5pt;color:{MUTED};margin-top:6px;">'
        f'Generated by {esc(generated_by)} on {esc(datetime.now().strftime("%Y-%m-%d %H:%M"))}.<br>'
        '<b>CONFIDENTIAL</b> &mdash; For authorized care and program use only. '
        'Keep this document secure and do not share it without authorization.</p>'
    )


# ------------------------------------------------------------- documents
def patient_record_html(patient, generated_by):
    p = patient.get
    body = [
        letterhead("Patient Record"),
        title_block("Patient Record", f"Patient ID: {p('patient_id', '')}"),
        section("Personal Information"),
        fields([
            ("Full Name", p("full_name")), ("Date of Birth", p("date_of_birth")),
            ("Age", p("age")), ("Sex", p("sex")),
            ("Contact Number", p("contact_number")), ("Address", p("address")),
            ("Emergency Contact", p("emergency_contact")),
            ("Relationship", p("emergency_relationship")),
        ]),
        section("Medical Background"),
        fields([
            ("Diagnosis", p("diagnosis")), ("Diagnosis Date", p("diagnosis_date")),
            ("Medical History", p("medical_history")), ("Other Conditions", p("conditions")),
            ("Allergies", p("allergies")), ("Current Medications", p("current_medications")),
            ("Clinical Notes", p("clinical_notes")),
        ]),
        section("Treatment"),
        fields([
            ("Attending Physician", p("attending_physician")), ("ARV Regimen", p("arv_regimen")),
            ("Treatment Start", p("treatment_start")), ("Treatment Status", p("treatment_status")),
        ]),
        section("Follow-up"),
        fields([
            ("Next Appointment", p("next_appointment")), ("Follow-up Notes", p("follow_up_notes")),
            ("Date Registered", p("date_registered")),
        ]),
        signature_block(generated_by, "Prepared by"),
        footer(generated_by),
    ]
    return wrap("".join(body))


def referral_html(patient, reason, facility, staff_name, staff_id):
    p = patient.get
    name = p("full_name", "the patient")
    facility_text = facility or "The Receiving Physician / Facility"
    sex = str(p("sex", "") or "")
    descriptor = ""
    if not blank(p("age")):
        descriptor = f", a {p('age')}-year-old"
        if sex and sex.lower() not in ("prefer not to specify", "other"):
            descriptor += f" {sex.lower()}"
        descriptor += " patient"

    if reason:
        intro = f"I am writing to refer {name}{descriptor}, to your care for the following reason: {reason}."
    else:
        intro = f"I am writing to refer {name}{descriptor}, to your care for further evaluation and continued management."

    dx = p("diagnosis", "")
    dx_text = f"{name} has a documented diagnosis of {dx}" if dx else f"No diagnosis is recorded for {name}"
    if dx and not blank(p("diagnosis_date")):
        dx_text += f", recorded on {p('diagnosis_date')}"
    dx_text += "."

    treatment = []
    if not blank(p("arv_regimen")):
        treatment.append(f"The current antiretroviral regimen on record is {p('arv_regimen')}.")
    else:
        treatment.append("No antiretroviral regimen is recorded in the system.")
    status = str(p("treatment_status", "") or "")
    if status and status.lower() != "not specified":
        treatment.append(f"Current treatment status: {status}.")
    if not blank(p("treatment_start")):
        treatment.append(f"Treatment started on {p('treatment_start')}.")

    summary_rows = []
    for label, key in (
        ("Medical history", "medical_history"), ("Other conditions", "conditions"),
        ("Current medications", "current_medications"), ("Clinical notes", "clinical_notes"),
    ):
        if not blank(p(key)):
            summary_rows.append((label, p(key)))
    summary_rows.insert(2 if len(summary_rows) >= 2 else len(summary_rows),
                        ("Allergies", p("allergies") if not blank(p("allergies")) else "None recorded"))

    body = [
        letterhead("Referral"),
        title_block("Patient Referral Form", f"Referral date: {today_text()}"),
        section("Patient Details"),
        fields([
            ("Patient Name", name), ("Patient ID", p("patient_id")),
            ("Date of Birth / Age", f"{p('date_of_birth', '')} / {p('age', '')}"),
            ("Referred To / Facility", facility or "Not specified"),
        ]),
        spacer(10),
        paragraph(f"To: {facility_text}", bold=True),
        paragraph(f"RE: Referral of {name} (Patient ID {p('patient_id', '')})", bold=True),
        paragraph("Dear Colleague,"),
        paragraph(intro),
        paragraph(dx_text + " " + " ".join(treatment)),
        section("Clinical Summary"),
        fields(summary_rows, label_width=26),
        spacer(8),
        paragraph(
            "Please contact our clinic if you need any further information about this patient. "
            "Thank you for your attention and continued care."
        ),
        paragraph("Respectfully yours,"),
        signature_block(staff_name or "Referring Staff", f"Referring Physician / Staff (ID: {staff_id})"),
        footer(staff_name or "Staff"),
    ]
    return wrap("".join(body))


def _changes(entry):
    """Rows describing what an audit entry changed."""
    previous = entry.get("previous_data") or {}
    new = entry.get("new_data") or {}
    rows = []
    if previous:
        for key in new:
            if key in SKIP_IN_DIFF:
                continue
            if previous.get(key) != new.get(key):
                rows.append((humanize(key), fmt_value(previous.get(key)), fmt_value(new.get(key))))
        for key in previous:
            if key not in new and key not in SKIP_IN_DIFF:
                rows.append((humanize(key), fmt_value(previous.get(key)), ""))
    return rows


def history_entry_html(entry):
    """One saved version, as a card. Also used by the Patient History dialog."""
    action = str(entry.get("action_type", ""))
    color = {"CREATE": "#15803D", "UPDATE": BLUE, "DELETE": "#B91C1C"}.get(action, "#7C3AED")
    when = f"{entry.get('date', '')} {entry.get('time', '')} UTC".strip()
    out = [
        spacer(6),
        '<table width="100%" cellspacing="0" cellpadding="8"><tr>'
        f'<td bgcolor="{NAVY}" style="background-color:{NAVY};color:#FFFFFF;font-weight:bold;">'
        f'Version {esc(entry.get("version", ""))}'
        f' &nbsp;&middot;&nbsp; <span style="color:#BFE0FF;">{esc(action)}</span></td>'
        f'<td bgcolor="{NAVY}" align="right" style="background-color:{NAVY};color:#CFE3FF;">'
        f'{esc(when)}</td></tr></table>',
        fields([
            ("Edited By", f"{entry.get('full_name', '')} ({entry.get('staff_id', '')})"),
            ("Summary", entry.get("changes_summary", "")),
            ("Audit ID", entry.get("audit_id", "")),
        ], label_width=22),
    ]
    changes = _changes(entry)
    if changes:
        out.append(spacer(4))
        out.append(f'<p style="margin-bottom:3px;color:{LABEL_INK};font-weight:bold;">Fields changed</p>')
        out.append(grid(["Field", "Previous", "Updated"],
                        [(a, b, c) for a, b, c in changes], widths=[24, 38, 38], small=True))
    else:
        new = entry.get("new_data") or {}
        shown = [(humanize(k), fmt_value(v)) for k, v in new.items()
                 if not blank(v) and k not in ("patient_id",)]
        if shown:
            out.append(spacer(4))
            out.append(f'<p style="margin-bottom:3px;color:{LABEL_INK};font-weight:bold;">Recorded data</p>')
            out.append(fields(shown, label_width=26))
    return "".join(out)


def patient_history_html(patient, history, generated_by):
    p = patient.get
    body = [
        letterhead("Patient Record History"),
        title_block("Patient Record History", f"{len(history)} saved version(s) shown"),
        section("Patient"),
        fields([
            ("Patient Name", p("full_name")), ("Patient ID", p("patient_id")),
            ("Date of Birth", p("date_of_birth")), ("Diagnosis", p("diagnosis")),
        ]),
    ]
    if len(history) > 1:
        body.append(section("Version Overview"))
        body.append(grid(
            ["Ver.", "Date / Time (UTC)", "Action", "Edited By", "Summary"],
            [(f"v{h.get('version', '')}", f"{h.get('date', '')} {h.get('time', '')}",
              h.get("action_type", ""), h.get("full_name", ""), h.get("changes_summary", ""))
             for h in history],
            widths=[7, 20, 12, 21, 40], small=True))
    body.append(section("Version Details"))
    for entry in history:
        body.append(history_entry_html(entry))
        body.append(spacer(8))
    body.append(footer(generated_by))
    return wrap("".join(body))


def allocation_html(records, patient_id, generated_by):
    active = sum(1 for r in records if r.get("status") == "Active")
    cancelled = sum(1 for r in records if r.get("status") == "Cancelled")
    units = sum(int(r.get("quantity", 0) or 0) for r in records if r.get("status") == "Active")
    subtitle = f"Patient ID: {patient_id}" if patient_id else "All patients"
    body = [
        letterhead("Allocation History"),
        title_block("Medicine Allocation History", subtitle),
        tiles([("Allocations", len(records), BLUE), ("Active", active, "#15803D"),
               ("Cancelled", cancelled, "#B91C1C"), ("Active units issued", units, "#B45309")]),
    ]
    if len(records) > 1:
        body.append(section("Overview"))
        body.append(grid(
            ["ID", "Date", "Patient", "Medicine", "Qty", "Status"],
            [(r.get("allocation_id", ""), r.get("allocation_date", ""), r.get("patient_name", ""),
              f"{r.get('medicine_name', '')} {r.get('strength', '')}", r.get("quantity", ""),
              badge(r.get("status", ""), "#15803D" if r.get("status") == "Active" else "#B91C1C"))
             for r in records],
            widths=[12, 14, 24, 28, 8, 14], small=True))
    body.append(section("Allocation Details"))
    for r in records:
        status_color = "#15803D" if r.get("status") == "Active" else "#B91C1C"
        body.append(
            '<table width="100%" cellspacing="0" cellpadding="8"><tr>'
            f'<td bgcolor="{NAVY}" style="background-color:{NAVY};color:#FFFFFF;font-weight:bold;">'
            f'{esc(r.get("allocation_id", ""))}</td>'
            f'<td bgcolor="{NAVY}" align="right" style="background-color:{NAVY};color:#FFFFFF;">'
            f'{esc(r.get("status", ""))}</td></tr></table>'
        )
        batches = "\n".join(
            f"Batch {b.get('batch_number', '')} ({b.get('medicine_id', '')}): "
            f"{b.get('quantity', '')} unit(s), expires {b.get('expiry_date', '')}"
            for b in r.get("batches", [])
        )
        rows = [
            ("Patient", f"{r.get('patient_name', '')} ({r.get('patient_id', '')})"),
            ("Medicine", f"{r.get('medicine_name', '')} {r.get('strength', '')}"),
            ("Quantity / Dosage", f"{r.get('quantity', '')} unit(s) / {r.get('dosage', '')}"),
            ("Allocation Date", r.get("allocation_date")),
            ("Next Follow-up", r.get("next_followup_date")),
            ("Batches Used", batches),
            ("Allocated By", r.get("allocated_by")),
        ]
        if not blank(r.get("notes")):
            rows.append(("Notes", r.get("notes")))
        if r.get("status") == "Cancelled":
            rows.append(("Cancelled", f"{r.get('cancelled_at', '')} by {r.get('cancelled_by', '')}"))
            rows.append(("Cancellation Reason", r.get("cancel_reason")))
        body.append(fields(rows, label_width=24))
        body.append(spacer(10))
    body.append(footer(generated_by))
    return wrap("".join(body))


def stock_html(records, summary, generated_by):
    stock_in = summary.get("stock_in", 0)
    stock_out = summary.get("stock_out", 0)
    body = [
        letterhead("Stock Movement"),
        title_block("Medicine Stock Movement", f"{len(records)} movement record(s)"),
        tiles([("Received (stock in)", stock_in, "#15803D"), ("Issued / removed", stock_out, "#B91C1C"),
               ("Net movement", stock_in - stock_out, BLUE), ("Records", len(records), "#B45309")]),
        section("Movement Records"),
    ]
    rows = []
    for r in records:
        kind = str(r.get("transaction_type", ""))
        rows.append((
            f"{str(r.get('transaction_date', ''))[:16]}\n{r.get('transaction_id', '')}",
            badge(kind, "#15803D" if kind == "STOCK IN" else "#B91C1C"),
            f"{r.get('medicine_name', '')} {r.get('strength', '')}\nBatch {r.get('batch_number', '')}",
            r.get("quantity", ""), r.get("balance_after", ""),
            f"{r.get('reference', '')} {r.get('remarks', '')}".strip(),
            r.get("performed_by", ""),
        ))
    # Cells with line breaks need the same treatment as other text cells.
    if rows:
        body.append(grid(
            ["Date / ID", "Type", "Medicine", "Qty", "Balance", "Reference / Remarks", "By"],
            rows, widths=[15, 10, 20, 6, 8, 25, 16], small=True))
    else:
        body.append(paragraph("No stock movement has been recorded yet."))
    body.append(footer(generated_by))
    return wrap("".join(body))
