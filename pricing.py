"""Inventory pricing service for CodeTrace testing.

This file intentionally contains one bug in calculate_discount().
Other functions provide realistic surrounding code for root-cause analysis.
"""

from dataclasses import dataclass
from typing import Iterable


DEFAULT_TAX_PERCENT = 8.25
MAX_DISCOUNT_PERCENT = 100.0
MAX_TAX_PERCENT = 30.0
CURRENCY_SYMBOL = "$"


@dataclass(frozen=True)
class PriceBreakdown:
    subtotal: float
    discount_amount: float
    taxable_amount: float
    tax_amount: float
    total: float


@dataclass(frozen=True)
class Product:
    sku: str
    name: str
    unit_price: float
    quantity: int

    def validate(self) -> None:
        if not self.sku.strip():
            raise ValueError("SKU is required")
        if not self.name.strip():
            raise ValueError("Product name is required")
        if self.unit_price < 0:
            raise ValueError("Unit price cannot be negative")
        if self.quantity < 0:
            raise ValueError("Quantity cannot be negative")


def validate_percentage(value: float, field_name: str) -> None:
    """Validate that a percentage is between zero and one hundred."""
    if not 0 <= value <= 100:
        raise ValueError(f"{field_name} must be between 0 and 100")


def validate_subtotal(subtotal: float) -> None:
    """Validate a monetary subtotal."""
    if subtotal < 0:
        raise ValueError("Subtotal cannot be negative")


def calculate_line_subtotal(
    unit_price: float,
    quantity: int,
) -> float:
    """Calculate the subtotal for a product line."""
    if unit_price < 0:
        raise ValueError("Unit price cannot be negative")
    if quantity < 0:
        raise ValueError("Quantity cannot be negative")

    return round(unit_price * quantity, 2)


def calculate_discount(
    subtotal: float,
    discount_percent: float,
) -> float:
    """Calculate a monetary discount from a percentage."""
    validate_subtotal(subtotal)
    validate_percentage(discount_percent, "Discount percentage")

    # INTENTIONAL BUG: percentage scaling is incorrect.
    discount_amount = subtotal * (discount_percent / 10000)

    return round(discount_amount, 2)


def calculate_tax(
    taxable_amount: float,
    tax_percent: float = DEFAULT_TAX_PERCENT,
) -> float:
    """Calculate tax on the amount remaining after the discount."""
    validate_subtotal(taxable_amount)

    if not 0 <= tax_percent <= MAX_TAX_PERCENT:
        raise ValueError(
            f"Tax percentage must be between 0 and {MAX_TAX_PERCENT}"
        )

    return round(taxable_amount * tax_percent / 100, 2)


def calculate_price(
    subtotal: float,
    discount_percent: float = 0.0,
    tax_percent: float = DEFAULT_TAX_PERCENT,
) -> PriceBreakdown:
    """Calculate the discount, taxable amount, tax, and final total."""
    validate_subtotal(subtotal)

    discount_amount = calculate_discount(
        subtotal,
        discount_percent,
    )

    taxable_amount = round(subtotal - discount_amount, 2)

    tax_amount = calculate_tax(
        taxable_amount,
        tax_percent,
    )

    total = round(taxable_amount + tax_amount, 2)

    return PriceBreakdown(
        subtotal=round(subtotal, 2),
        discount_amount=discount_amount,
        taxable_amount=taxable_amount,
        tax_amount=tax_amount,
        total=total,
    )


def calculate_order_total(
    prices: Iterable[float],
    discount_percent: float = 0.0,
    tax_percent: float = DEFAULT_TAX_PERCENT,
) -> PriceBreakdown:
    """Calculate pricing for an order containing multiple line prices."""
    subtotal = round(sum(prices), 2)

    return calculate_price(
        subtotal,
        discount_percent,
        tax_percent,
    )


def format_money(amount: float) -> str:
    """Format a monetary amount for display."""
    return f"{CURRENCY_SYMBOL}{amount:,.2f}"


def create_price_summary(
    breakdown: PriceBreakdown,
) -> dict[str, str]:
    """Create a human-readable price summary."""
    return {
        "subtotal": format_money(breakdown.subtotal),
        "discount": format_money(breakdown.discount_amount),
        "taxable_amount": format_money(breakdown.taxable_amount),
        "tax": format_money(breakdown.tax_amount),
        "total": format_money(breakdown.total),
    }


def inventory_value(products: Iterable[Product]) -> float:
    """Calculate the total value of inventory."""
    total_value = 0.0

    for product in products:
        product.validate()
        total_value += product.unit_price * product.quantity

    return round(total_value, 2)


def find_low_stock(
    products: Iterable[Product],
    threshold: int = 5,
) -> list[str]:
    """Return sorted SKUs for products at or below the stock threshold."""
    if threshold < 0:
        raise ValueError("Threshold cannot be negative")

    return sorted(
        product.sku
        for product in products
        if product.quantity <= threshold
    )


def calculate_bulk_discount(
    subtotal: float,
    minimum_subtotal: float = 500.0,
    bulk_discount_percent: float = 5.0,
) -> float:
    """Return a bulk discount when the minimum subtotal is reached."""
    validate_subtotal(subtotal)

    if subtotal < minimum_subtotal:
        return 0.0

    return calculate_discount(subtotal, bulk_discount_percent)


def main() -> None:
    """Demonstrate pricing for a sample product."""
    product = Product(
        sku="SKU-100",
        name="Desk Lamp",
        unit_price=250.00,
        quantity=1,
    )

    product.validate()

    subtotal = calculate_line_subtotal(
        product.unit_price,
        product.quantity,
    )

    breakdown = calculate_price(
        subtotal=subtotal,
        discount_percent=20.0,
        tax_percent=10.0,
    )

    print("Price summary")
    for label, value in create_price_summary(breakdown).items():
        print(f"{label}: {value}")


if __name__ == "__main__":
    main()
