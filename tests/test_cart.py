from unittest.mock import Mock

import pytest

from shop.cart import Cart, Item


def test_add_item_success(empty_cart: Cart) -> None:
    empty_cart.add("laptop", price=15000.0, qty=1)
    assert empty_cart.items_count() == 1


# Підказка з методички: що буде, якщо додати той самий товар з іншою ціною?
# Фіксуємо рішення: ціна має оновитися на нову.
def test_add_existing_item_updates_price(empty_cart: Cart) -> None:
    empty_cart.add("book", price=100.0, qty=1)
    empty_cart.add("book", price=150.0, qty=2)
    assert empty_cart._items["book"].price == 150.0
    assert empty_cart.items_count() == 3


def test_remove_item_success(cart_with_items: Cart) -> None:
    cart_with_items.remove("pen")
    assert cart_with_items.items_count() == 2


def test_remove_nonexistent_item_raises(empty_cart: Cart) -> None:
    with pytest.raises(KeyError):
        empty_cart.remove("phone")


def test_add_negative_price_raises(empty_cart: Cart) -> None:
    with pytest.raises(ValueError, match="price"):
        empty_cart.add("notebook", price=-50.0, qty=1)


def test_add_zero_or_negative_qty_raises(empty_cart: Cart) -> None:
    with pytest.raises(ValueError, match="qty"):
        empty_cart.add("pencil", price=10.0, qty=0)


# Параметризований тест із граничними значеннями
@pytest.mark.parametrize(
    ("discount", "expected"), [(0, 460.0), (10, 414.0), (50, 230.0), (100, 0.0)]
)
def test_total_with_various_discounts(
    cart_with_items: Cart, discount: float, expected: float
) -> None:
    assert cart_with_items.total(discount_percent=discount) == pytest.approx(expected)


@pytest.mark.parametrize("invalid_discount", [-5.0, 105.0])
def test_invalid_discount_raises(cart_with_items: Cart, invalid_discount: float) -> None:
    with pytest.raises(ValueError, match="discount_percent"):
        cart_with_items.total(discount_percent=invalid_discount)


def test_total_in_currency_with_mock(cart_with_items: Cart) -> None:
    rates_mock = Mock()
    rates_mock.get_rate.return_value = 40.0
    assert cart_with_items.total_in("USD", rates_mock) == pytest.approx(11.5)
    rates_mock.get_rate.assert_called_once_with("USD")


def test_total_in_invalid_rate_raises(cart_with_items: Cart) -> None:
    rates_mock = Mock()
    rates_mock.get_rate.return_value = 0.0
    with pytest.raises(ValueError, match="rate"):
        cart_with_items.total_in("EUR", rates_mock)


# TDD: тести для методу, якого ще немає
def test_most_expensive_empty_cart(empty_cart: Cart) -> None:
    assert empty_cart.most_expensive() is None


def test_most_expensive_cart_with_items(cart_with_items: Cart) -> None:
    assert cart_with_items.most_expensive() == Item(name="book", price=200.0, qty=2)
