"""Tests for finance-related report routes."""
from datetime import UTC, datetime, timedelta

import pytest

from app.models import CashLedger, Product, Transaction, TransactionItem, User, db


class TestFinanceSetup:
    """Test cases for finance setup flow."""

    def test_staff_cannot_access_finance_setup(self, client, staff_user):
        """Staff users should be blocked from admin-only finance setup."""
        client.post('/', data={
            'username': 'staff',
            'password': 'staff123'
        })

        response = client.get('/reports/finance/setup', follow_redirects=True)

        assert response.status_code == 200
        assert b'permission' in response.data.lower()

    def test_admin_can_set_opening_balance_once(self, client, admin_user, app):
        """Admin can set opening balance once and duplicate submissions are rejected."""
        client.post('/', data={
            'username': 'admin',
            'password': 'admin123'
        })

        first_response = client.post('/reports/finance/setup', data={
            'opening_balance': '1250.50',
            'notes': 'Initial cash setup'
        }, follow_redirects=True)

        assert first_response.status_code == 200
        assert b'Opening cash balance has been saved successfully.' in first_response.data

        with app.app_context():
            entries = CashLedger.query.filter_by(entry_type='opening_balance').all()
            assert len(entries) == 1
            assert entries[0].running_balance == pytest.approx(1250.50)

        second_response = client.post('/reports/finance/setup', data={
            'opening_balance': '2000.00',
            'notes': 'Duplicate setup attempt'
        }, follow_redirects=True)

        assert second_response.status_code == 200
        assert b'already been configured' in second_response.data

        with app.app_context():
            assert CashLedger.query.filter_by(entry_type='opening_balance').count() == 1


class TestFinanceReports:
    """Test cases for cashflow and profitability reports."""

    def test_cashflow_report_filters_entries_by_date(self, client, staff_user, app):
        """Cashflow report should respect date filters and only show entries in range."""
        with app.app_context():
            staff = User.query.filter_by(username='staff').first()
            now = datetime.now(UTC)
            old_date = now - timedelta(days=40)

            db.session.add(CashLedger(
                entry_type='opening_balance',
                amount=1000.0,
                running_balance=1000.0,
                user_id=staff.id,
                notes='Old opening',
                created_at=old_date,
            ))
            db.session.add(CashLedger(
                entry_type='sale_inflow',
                amount=200.0,
                running_balance=1200.0,
                user_id=staff.id,
                notes='In range inflow',
                created_at=now,
            ))
            db.session.add(CashLedger(
                entry_type='purchase_outflow',
                amount=-50.0,
                running_balance=1150.0,
                user_id=staff.id,
                notes='In range outflow',
                created_at=now,
            ))
            db.session.commit()

        client.post('/', data={
            'username': 'staff',
            'password': 'staff123'
        })

        date_from = (datetime.now(UTC) - timedelta(days=1)).strftime('%Y-%m-%d')
        date_to = datetime.now(UTC).strftime('%Y-%m-%d')
        response = client.get(f'/reports/cashflow?date_from={date_from}&date_to={date_to}')

        assert response.status_code == 200
        assert b'In range inflow' in response.data
        assert b'In range outflow' in response.data
        assert b'Old opening' not in response.data

    def test_profitability_uses_sale_cost_snapshot(self, client, staff_user, test_product, app):
        """Profitability COGS should use item unit_cost_at_sale over current product cost."""
        with app.app_context():
            staff = User.query.filter_by(username='staff').first()
            product = db.session.get(Product, test_product.id)

            product.cost_price = 3.0  # Current cost differs from historical snapshot

            sale = Transaction(
                transaction_type='sale',
                reference_number='SAL-20260401120010-RPT01',
                user_id=staff.id,
                subtotal=50.0,
                tax=0.0,
                discount=0.0,
                total=50.0,
                customer_name='Report Customer',
            )
            db.session.add(sale)
            db.session.flush()

            db.session.add(TransactionItem(
                transaction_id=sale.id,
                product_id=product.id,
                quantity=2,
                unit_price=25.0,
                total_price=50.0,
                unit_cost_at_sale=12.0,
            ))
            db.session.commit()

        client.post('/', data={
            'username': 'staff',
            'password': 'staff123'
        })

        today = datetime.now(UTC).strftime('%Y-%m-%d')
        response = client.get(f'/reports/profitability?date_from={today}&date_to={today}')

        assert response.status_code == 200
        assert b'SAL-20260401120010-RPT01' in response.data
        assert b'24.00' in response.data  # COGS from snapshot: 12 * 2
        assert b'26.00' in response.data  # Gross profit: 50 - 24
        assert b'52.00%' in response.data
