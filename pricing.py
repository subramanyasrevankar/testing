"""
Subscription Billing Engine
Business rules:
- Proration is based on the exact fraction of the billing period remaining.
- Coupons apply to the prorated plan-change charge before tax.
- Tax is calculated after the coupon discount.
- Currency amounts are rounded to two decimal places.
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import Iterable

CENT = Decimal("0.01")
HUNDRED = Decimal("100")


def money(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class Plan:
    plan_id: str
    name: str
    monthly_price: Decimal
    annual_price: Decimal

    def price(self, annual: bool) -> Decimal:
        return self.annual_price if annual else self.monthly_price


@dataclass(frozen=True)
class Coupon:
    code: str
    percent_off: Decimal
    active: bool = True

    def validate(self) -> None:
        if not self.active:
            raise ValueError("Coupon is inactive")
        if not Decimal("0") <= self.percent_off <= HUNDRED:
            raise ValueError("Coupon percentage must be between 0 and 100")


@dataclass(frozen=True)
class Subscription:
    subscription_id: str
    current_plan: Plan
    annual: bool
    period_start: date
    period_end: date
    tax_rate_percent: Decimal
    currency: str = "USD"

    def validate(self) -> None:
        if self.period_end <= self.period_start:
            raise ValueError("Invalid billing period")
        if not Decimal("0") <= self.tax_rate_percent <= HUNDRED:
            raise ValueError("Tax rate must be between 0 and 100")


@dataclass(frozen=True)
class Invoice:
    subscription_id: str
    currency: str
    subtotal: Decimal
    discount: Decimal
    taxable_amount: Decimal
    tax: Decimal
    total: Decimal


class BillingEngine:
    def __init__(self, plans: Iterable[Plan]) -> None:
        self._plans = {p.plan_id: p for p in plans}
        if not self._plans:
            raise ValueError("At least one plan is required")

    def get_plan(self, plan_id: str) -> Plan:
        try:
            return self._plans[plan_id]
        except KeyError as exc:
            raise ValueError(f"Unknown plan: {plan_id}") from exc

    @staticmethod
    def _remaining_fraction(start: date, end: date, effective: date) -> Decimal:
        if effective < start or effective >= end:
            raise ValueError("Effective date must be inside the billing period")
        total_days = Decimal((end - start).days)
        remaining_days = Decimal((end - effective).days)
        return remaining_days / total_days

    def preview_plan_change(
        self,
