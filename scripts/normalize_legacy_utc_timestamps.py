"""One-time utility to normalize legacy naive timestamps to UTC-aware values.

Run this only after creating a backup of instance/inventory.db.
"""

from __future__ import annotations

import argparse
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app import create_app  # noqa: E402
from app.models import (  # noqa: E402
    AuditLog,
    CashLedger,
    Category,
    Product,
    StockMovement,
    Supplier,
    Transaction,
    User,
    db,
)

MARKER_PATH = ROOT_DIR / 'instance' / '.legacy_utc_normalized'
MODEL_FIELDS = [
    (User, ['created_at', 'last_login']),
    (Category, ['created_at']),
    (Supplier, ['created_at', 'updated_at']),
    (Product, ['created_at', 'updated_at']),
    (Transaction, ['created_at']),
    (StockMovement, ['created_at']),
    (CashLedger, ['created_at']),
    (AuditLog, ['created_at']),
]


def convert_to_utc(value):
    """Return UTC-aware datetime and whether a change was needed."""
    if value is None:
        return value, False

    if value.tzinfo is None:
        return value.replace(tzinfo=UTC), True

    normalized = value.astimezone(UTC)
    return normalized, normalized != value


def parse_args():
    parser = argparse.ArgumentParser(
        description='Normalize legacy naive timestamps in the local SQLite database to UTC-aware datetimes.'
    )
    parser.add_argument('--dry-run', action='store_true', help='Show what would change without committing.')
    parser.add_argument('--force', action='store_true', help='Run even if marker file already exists.')
    return parser.parse_args()


def main():
    args = parse_args()

    if MARKER_PATH.exists() and not args.force:
        print('Normalization marker already exists. Nothing to do.')
        print(f'If you need to rerun, use --force. Marker: {MARKER_PATH}')
        return 0

    app = create_app()
    total_checked = 0
    total_updated = 0

    with app.app_context():
        for model, fields in MODEL_FIELDS:
            rows = model.query.all()
            for row in rows:
                for field_name in fields:
                    current_value = getattr(row, field_name)
                    total_checked += 1

                    updated_value, changed = convert_to_utc(current_value)
                    if changed:
                        setattr(row, field_name, updated_value)
                        total_updated += 1

        if args.dry_run:
            db.session.rollback()
            print(f'DRY RUN: checked {total_checked} timestamp values, would update {total_updated}.')
            return 0

        db.session.commit()

    MARKER_PATH.parent.mkdir(parents=True, exist_ok=True)
    MARKER_PATH.write_text(
        '\n'.join(
            [
                'legacy UTC normalization completed',
                f'run_at={datetime.now(UTC).isoformat()}',
                f'timestamps_checked={total_checked}',
                f'timestamps_updated={total_updated}',
            ]
        ),
        encoding='utf-8',
    )

    print(f'Completed normalization. Checked {total_checked}, updated {total_updated}.')
    print(f'Marker written to: {MARKER_PATH}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
