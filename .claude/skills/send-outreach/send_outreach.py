#!/usr/bin/env python3
"""
MBB Send Outreach — sends approved messages from outreach-drafts.json via Resend.

Usage:
  python3 send_outreach.py --data /path/to/outreach-drafts.json --approve all
  python3 send_outreach.py --data /path/to/outreach-drafts.json --approve 1,3,5
  python3 send_outreach.py --data /path/to/outreach-drafts.json --dry-run
  python3 send_outreach.py --data /path/to/outreach-drafts.json --approve all --follow-up 1
  python3 send_outreach.py --data /path/to/outreach-drafts.json --approve all --follow-up 2

Requires in .env:
  RESEND_API_KEY=re_xxx
  FROM_EMAIL=you@company.com
  FROM_NAME=Your Name
"""

import argparse
import json
import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime


def ensure_package(package_name: str, import_name: str = None):
    import_name = import_name or package_name
    try:
        __import__(import_name)
    except ImportError:
        print(f"Installing {package_name}...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", package_name, "-q"],
            check=True
        )


def load_drafts(data_path: str) -> list:
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_drafts(drafts: list, data_path: str):
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(drafts, f, ensure_ascii=False, indent=2)


def save_log(log_entries: list, data_path: str):
    log_path = Path(data_path).parent / "outreach-log.json"
    existing = []
    if log_path.exists():
        with open(log_path, "r", encoding="utf-8") as f:
            existing = json.load(f)
    existing.extend(log_entries)
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)
    print(f"  Log saved: {log_path}")


def send_via_resend(api_key: str, from_email: str, from_name: str,
                    to_email: str, subject: str, body: str) -> bool:
    payload = json.dumps({
        "from": f"{from_name} <{from_email}>",
        "to": [to_email],
        "subject": subject,
        "text": body,
    })
    try:
        result = subprocess.run(
            [
                "curl", "-s", "-X", "POST", "https://api.resend.com/emails",
                "-H", f"Authorization: Bearer {api_key}",
                "-H", "Content-Type: application/json",
                "-d", payload,
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        response = json.loads(result.stdout)
        if "id" in response:
            return True
        print(f"  Resend error: {response}")
        return False
    except Exception as e:
        print(f"  Send error: {e}")
        return False



def resolve_approved_ids(approve_arg: str, drafts: list, follow_up: int = None) -> set:
    sent_key = f"sent_follow_up_{follow_up}" if follow_up else "sent"
    if approve_arg == "all":
        return {d["id"] for d in drafts if d.get("email") and not d.get(sent_key)}
    ids = set()
    for part in approve_arg.split(","):
        part = part.strip()
        if part.isdigit():
            ids.add(int(part))
    return ids


def get_email_content(draft: dict, follow_up: int = None) -> tuple:
    """Returns (subject, body) for initial email or follow-up."""
    email_data = draft.get("email", {})
    if follow_up == 1:
        body = email_data.get("follow_up_1", "")
        subject = "Re: " + email_data.get("subject", "")
    elif follow_up == 2:
        body = email_data.get("follow_up_2", "")
        subject = "Re: " + email_data.get("subject", "")
    else:
        body = email_data.get("body", "")
        subject = email_data.get("subject", "")
    return subject, body


def update_md_status(drafts: list, data_path: str):
    """Rewrites the sent-status block at the top of outreach-drafts.md."""
    md_path = Path(data_path).parent / "outreach-drafts.md"
    if not md_path.exists():
        return

    lines = []
    lines.append("## Outreach Status\n")
    lines.append(f"_Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}_\n\n")
    lines.append("| # | Contact | Company | Email | Initial | FU #1 | FU #2 |\n")
    lines.append("|---|---------|---------|-------|---------|-------|-------|\n")

    for d in drafts:
        contact = d.get("contact", {})
        name = contact.get("name", "?")
        company = d.get("company", "?")
        email = contact.get("email", "—")
        has_email = bool(contact.get("email"))

        def cell(key):
            if d.get(key):
                ts = d.get(f"{key}_at", "")[:10]
                return f"✅ {ts}"
            return "⬜" if has_email else "❌"

        row = f"| {d['id']} | {name} | {company} | {email} | {cell('sent')} | {cell('sent_follow_up_1')} | {cell('sent_follow_up_2')} |\n"
        lines.append(row)

    status_block = "".join(lines)

    content = md_path.read_text(encoding="utf-8")

    # Заменяем существующий блок статуса или вставляем в начало
    import re
    pattern = r"## Outreach Status\n.*?(?=\n## |\Z)"
    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, status_block.rstrip(), content, flags=re.DOTALL)
    else:
        content = status_block + "\n---\n\n" + content

    md_path.write_text(content, encoding="utf-8")
    print(f"  Status updated: {md_path}")


def print_draft_summary(draft: dict, follow_up: int = None):
    contact = draft.get("contact", {})
    subject, body = get_email_content(draft, follow_up)
    label = f"Follow-up #{follow_up}" if follow_up else "Email"
    print(f"\n  [{draft['id']}] {contact.get('name', 'Unknown')} — {contact.get('title', '')}")
    print(f"       {draft.get('company', '')} | {contact.get('email', 'no email')}")
    print(f"       [{label}] Subject: {subject}")
    preview = body[:120].replace("\n", " ")
    print(f"       Preview: {preview}...")


def main():
    parser = argparse.ArgumentParser(description="MBB Send Outreach")
    parser.add_argument("--data", required=True, help="Path to outreach-drafts.json")
    parser.add_argument("--approve", default=None,
                        help="Which contacts to send: 'all' or '1,3,5'")
    parser.add_argument("--follow-up", type=int, choices=[1, 2], default=None,
                        help="Send follow-up #1 (day 3) or #2 (day 7) instead of initial email")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview without sending")
    parser.add_argument("--status", action="store_true",
                        help="Show sending status for all contacts and exit")
    parser.add_argument("--from-email", help="Override FROM_EMAIL from env")
    parser.add_argument("--from-name", help="Override FROM_NAME from env")
    args = parser.parse_args()

    if not Path(args.data).exists():
        print(f"ERROR: File not found: {args.data}")
        sys.exit(1)

    # Загружаем конфиг из env
    resend_key = os.environ.get("RESEND_API_KEY")
    from_email = args.from_email or os.environ.get("FROM_EMAIL")
    from_name = args.from_name or os.environ.get("FROM_NAME", "")

    if not args.dry_run and not resend_key:
        print("ERROR: RESEND_API_KEY not configured.")
        print("Add to .env: RESEND_API_KEY=re_xxx")
        sys.exit(1)

    if not args.dry_run and not from_email:
        print("ERROR: FROM_EMAIL not set in .env")
        sys.exit(1)

    drafts = load_drafts(args.data)

    # --status: показать таблицу состояния и выйти
    if args.status:
        print(f"\n── Outreach Status: {Path(args.data).parent.name} ──────────")
        print(f"{'#':<4} {'Contact':<25} {'Company':<20} {'Initial':<12} {'FU#1':<12} {'FU#2':<12}")
        print("─" * 85)
        for d in drafts:
            contact = d.get("contact", {})
            name = (contact.get("name") or "?")[:24]
            company = (d.get("company") or "?")[:19]
            has_email = bool(contact.get("email"))

            def s(key):
                if d.get(key):
                    return "✅ " + d.get(f"{key}_at", "")[:10]
                return "⬜ pending" if has_email else "❌ no email"

            print(f"{d['id']:<4} {name:<25} {company:<20} {s('sent'):<12} {s('sent_follow_up_1'):<12} {s('sent_follow_up_2'):<12}")

        total = len(drafts)
        sent_i = sum(1 for d in drafts if d.get("sent"))
        sent_f1 = sum(1 for d in drafts if d.get("sent_follow_up_1"))
        sent_f2 = sum(1 for d in drafts if d.get("sent_follow_up_2"))
        print(f"\n  Total: {total} | Initial: {sent_i}/{total} | FU#1: {sent_f1}/{total} | FU#2: {sent_f2}/{total}")
        return

    follow_up = args.follow_up
    follow_up_label = f"Follow-up #{follow_up}" if follow_up else "Initial email"
    sent_key = f"sent_follow_up_{follow_up}" if follow_up else "sent"

    print(f"\n📧 MBB Send Outreach")
    print(f"   Data: {args.data}")
    print(f"   Mode: {follow_up_label}")
    print(f"   Provider: {'RESEND' if not args.dry_run else 'DRY RUN'}")
    print(f"   From: {from_name} <{from_email}>" if not args.dry_run else "   Mode: preview only")
    print(f"   Total drafts: {len(drafts)}\n")

    # Показываем все драфты для review
    print("── Drafts ──────────────────────────────")
    for draft in drafts:
        fu_sent = draft.get(sent_key)
        status = "✅ sent" if fu_sent else ("❌ no email" if not draft.get("email") else "⬜ draft")
        contact = draft.get("contact", {})
        print(f"  [{draft['id']}] {status} | {contact.get('name', '?')} ({draft.get('company', '?')}) | {contact.get('email', 'no email')}")

    if args.dry_run or not args.approve:
        if not args.approve:
            print("\nTip: Add --approve all  or  --approve 1,3,5  to send")
        else:
            # dry-run preview
            approved_ids = resolve_approved_ids(args.approve, drafts, follow_up)
            print(f"\n── Preview ({len(approved_ids)} contacts) ──────────────")
            for draft in drafts:
                if draft["id"] in approved_ids:
                    print_draft_summary(draft, follow_up)
            print(f"\n✅ Dry run complete. Remove --dry-run to send.")
        return

    # Отправляем
    approved_ids = resolve_approved_ids(args.approve, drafts, follow_up)
    to_send = [d for d in drafts if d["id"] in approved_ids and not d.get(sent_key)]

    if not to_send:
        print(f"\nNo new drafts to send (all already sent or not approved).")
        return

    print(f"\n── Sending {len(to_send)} {follow_up_label} messages ──────────────")
    log_entries = []
    sent_count = 0

    for draft in to_send:
        contact = draft.get("contact", {})
        to_email = contact.get("email")
        subject, body = get_email_content(draft, follow_up)

        if not to_email:
            print(f"  [{draft['id']}] ⚠️ SKIP — no email: {contact.get('name', '?')}")
            continue

        if not body:
            print(f"  [{draft['id']}] ⚠️ SKIP — no {follow_up_label} text: {contact.get('name', '?')}")
            continue

        print(f"  [{draft['id']}] Sending to {contact.get('name', '?')} <{to_email}>...", end=" ")

        success = send_via_resend(
            resend_key, from_email, from_name,
            to_email, subject, body
        )

        if success:
            print("✅")
            sent_count += 1
            draft[sent_key] = True
            draft[f"{sent_key}_at"] = datetime.now().isoformat()
            draft["approved"] = True
        else:
            print("❌ FAILED")

        log_entries.append({
            "id": draft["id"],
            "company": draft.get("company"),
            "contact_name": contact.get("name"),
            "to_email": to_email,
            "subject": subject,
            "type": follow_up_label,
            "provider": "resend",
            "success": success,
            "timestamp": datetime.now().isoformat()
        })

    # Сохраняем обновлённые статусы
    save_drafts(drafts, args.data)
    save_log(log_entries, args.data)
    update_md_status(drafts, args.data)

    print(f"\n{'─' * 45}")
    print(f"✅ Sent: {sent_count}/{len(to_send)}")
    print(f"📋 Log: {Path(args.data).parent}/outreach-log.json")

    if sent_count < len(to_send):
        print(f"⚠️  {len(to_send) - sent_count} failed — check log for details")


if __name__ == "__main__":
    main()
