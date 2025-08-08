from accounting.models import Accounting_Account
from decimal import Decimal
from datetime import datetime
import calendar

def generate_income_statement(from_date, to_date, method='accrual'):
    """
    Generate an income statement for the given period
    :param from_date: Start date of the period
    :param to_date: End date of the period
    :param method: 'accrual' or 'cash' accounting method
    :return: Dictionary with income statement data
    """
    # Filter accounts by type
    income_accounts = Accounting_Account.objects.filter(
        category__category_type='I',
        is_active=True
    )
    expense_accounts = Accounting_Account.objects.filter(
        category__category_type='X',
        is_active=True
    )

    # Calculate totals
    income_data = []
    total_income = Decimal('0')

    for account in income_accounts:
        if method == 'cash':
            # For cash method, only consider transactions where cash was received/paid
            balance = account.get_period_balance(from_date, to_date)['balance']
        else:
            balance = account.get_period_balance(from_date, to_date)['balance']

        if balance != 0:
            income_data.append({
                'account': account,
                'amount': balance
            })
            total_income += balance

    # if method === "cash":
    #     account = Accounting_Account.objects.filter(code="cash").first()
    #     total_income = account.get_period_balance(from_date, to_date)['balance']
    #     income_data = []
    #     income_data.append({
    #         'account': account,
    #         'amount': account['balance']
    #     })
    expense_data = []
    total_expenses = Decimal('0')

    for account in expense_accounts:
        if method == 'cash':
            # For cash method, only consider transactions where cash was received/paid
            balance = account.get_period_balance(from_date, to_date)['balance']
        else:  # accrual
            balance = account.get_period_balance(from_date, to_date)['balance']

        if balance != 0:
            expense_data.append({
                'account': account,
                'amount': balance
            })
            total_expenses += balance

    net_income = total_income - total_expenses

    return {
        'from_date': from_date,
        'to_date': to_date,
        'accounting_method': method,
        'income': income_data,
        'total_income': total_income,
        'expenses': expense_data,
        'total_expenses': total_expenses,
        'net_income': net_income
    }


def generate_balance_sheet(as_of_date):
    """
    Generate a balance sheet as of a specific date
    :param as_of_date: The date to generate the balance sheet for
    :return: Dictionary with balance sheet data
    """
    # Get all active accounts grouped by category type
    asset_accounts = Accounting_Account.objects.filter(
        category__category_type='A',
        is_active=True
    ).order_by('code')

    liability_accounts = Accounting_Account.objects.filter(
        category__category_type='L',
        is_active=True
    ).order_by('code')

    equity_accounts = Accounting_Account.objects.filter(
        category__category_type='E',
        is_active=True
    ).order_by('code')

    # Calculate totals
    assets_data = []
    total_assets = Decimal('0')

    for account in asset_accounts:
        balance = account.get_balance_as_of(as_of_date)['balance']
        print(balance)
        assets_data.append({
            'account': account,
            'balance': balance
        })
        total_assets += balance

    liabilities_data = []
    total_liabilities = Decimal('0')

    for account in liability_accounts:
        balance = account.get_balance_as_of(as_of_date)['balance']
        liabilities_data.append({
            'account': account,
            'balance': balance
        })
        total_liabilities += balance

    equity_data = []
    total_equity = Decimal('0')

    for account in equity_accounts:
        balance = account.get_balance_as_of(as_of_date)['balance']
        equity_data.append({
            'account': account,
            'balance': balance
        })
        total_equity += balance

    # Also include current period net income in equity (Retained Earnings)
    income_statement = generate_income_statement(
        from_date=None,  # From beginning
        to_date=as_of_date,
        method='accrual'
    )
    net_income = income_statement['net_income']
    total_equity += net_income

    return {
        'as_of_date': as_of_date,
        'assets': assets_data,
        'total_assets': total_assets,
        'liabilities': liabilities_data,
        'total_liabilities': total_liabilities,
        'equity': equity_data,
        'total_equity': total_equity,
        'net_income': net_income,
        'liabilities_and_equity': total_liabilities + total_equity
    }


def generate_trial_balance(as_of_date=None, from_date=None, to_date=None):
    """
    Generate a trial balance
    :param as_of_date: If provided, shows balances up to this date (includes opening balances)
    :param from_date/to_date: If provided, shows activity during this period (excludes opening balances)
    :return: Dictionary with trial balance data
    """
    if as_of_date:
        # Get balances as of a specific date (includes opening balances)
        accounts = Accounting_Account.objects.filter(is_active=True).order_by('code')
        trial_balance_data = []

        total_debits = Decimal('0')
        total_credits = Decimal('0')

        for account in accounts:
            balance_info = account.get_balance_as_of(as_of_date)
            balance = balance_info['balance']

            if balance == 0:
                continue

            if account.category.category_type in ['A', 'X']:  # Assets and Expenses
                debits = balance if balance > 0 else Decimal('0')
                credits = -balance if balance < 0 else Decimal('0')
            else:  # Liabilities, Equity, and Income
                credits = balance if balance > 0 else Decimal('0')
                debits = -balance if balance < 0 else Decimal('0')

            trial_balance_data.append({
                'account': account,
                'debits': debits,
                'credits': credits,
            })

            total_debits += debits
            total_credits += credits

        return {
            'type': 'as_of',
            'date': as_of_date,
            'accounts': trial_balance_data,
            'total_debits': total_debits,
            'total_credits': total_credits,

        }
    elif from_date and to_date:
        # Get activity for a specific period (excludes opening balances)
        accounts = Accounting_Account.objects.filter(is_active=True).order_by('code')
        trial_balance_data = []

        total_debits = Decimal('0')
        total_credits = Decimal('0')

        for account in accounts:
            balance_info = account.get_period_balance(from_date, to_date)
            debits = balance_info['debit']
            credits = balance_info['credit']

            if debits == 0 and credits == 0:
                continue

            trial_balance_data.append({
                'account': account,
                'debits': debits,
                'credits': credits,

            })

            total_debits += debits
            total_credits += credits

        return {
            'type': 'period',
            'from_date': from_date,
            'to_date': to_date,
            'accounts': trial_balance_data,
            'total_debits': total_debits,
            'total_credits': total_credits,

        }
    else:
        # Default to all-time balances
        accounts = Accounting_Account.objects.filter(is_active=True).order_by('code')
        trial_balance_data = []

        total_debits = Decimal('0')
        total_credits = Decimal('0')

        current_balance = 0
        for account in accounts:
            balance_info = account.get_balance()
            balance = balance_info['balance']

            if balance == 0:
                continue

            if account.category.category_type in ['A', 'X']:  # Assets and Expenses
                debits = balance if balance > 0 else Decimal('0')
                credits = -balance if balance < 0 else Decimal('0')
            else:  # Liabilities, Equity, and Income
                credits = balance if balance > 0 else Decimal('0')
                debits = -balance if balance < 0 else Decimal('0')

            trial_balance_data.append({
                'account': account,
                'debits': debits,
                'credits': credits
            })

            total_debits += debits
            total_credits += credits

        return {
            'type': 'all_time',
            'accounts': trial_balance_data,
            'total_debits': total_debits,
            'total_credits': total_credits,
        }


def yearly_basis_income_statement(year):

    print(f"First and last days of each month in {year}:")
    print("-" * 50)
    print(f"{'Month':<15}{'First Day':<15}{'Last Day':<15}")
    print("-" * 50)

    for month in range(1, 13):
        # Get first day (always the 1st)
        first_day = datetime(year, month, 1)

        # Get last day by finding the number of days in the month
        _, last_day_num = calendar.monthrange(year, month)
        last_day = datetime(year, month, last_day_num)

        # Format the output
        month_name = calendar.month_name[month]
        print(f"{month_name:<15}{first_day.strftime('%Y-%m-%d'):<15}{last_day.strftime('%Y-%m-%d'):<15}")

    return 0
'''
from datetime import date

from django.utils import timezone
from datetime import datetime
naive_datetime = datetime.datetime(2025, 8, 4, 0, 0, 0)
aware_datetime = timezone.make_aware(naive_datetime)


# 1. Generate Income Statement (Accrual basis for Q1 2023)
income_statement = generate_income_statement(
    from_date=timezone.make_aware(datetime(2023, 1, 1)),
    to_date=timezone.make_aware(datetime(2025, 8, 7)),
    method='accrual'
)
print(income_statement)

income_statement = generate_income_statement(
    from_date=timezone.make_aware(datetime(2023, 1, 1)),
    to_date=timezone.make_aware(datetime(2025, 8, 7)),
    method='cash'
)
print(income_statement)

from django.utils import timezone
from datetime import datetime
from accounting.financial_reports import *

# 2. Generate Balance Sheet as of March 31, 2023
balance_sheet = generate_balance_sheet(
    as_of_date=timezone.make_aware(datetime(2025, 8, 9))
)
balance_sheet

# 3. Generate Trial Balance for a period

trial_balance_period = generate_trial_balance(
    from_date=timezone.make_aware(datetime(2023, 1, 1)),
    to_date=timezone.make_aware(datetime(2025, 8, 3))
)
trial_balance_period

# 3. Generate Trial Balance as of a date
trial_balance_as_of = generate_trial_balance(
    as_of_date=timezone.make_aware(datetime(2025, 8, 3))
)
'''
