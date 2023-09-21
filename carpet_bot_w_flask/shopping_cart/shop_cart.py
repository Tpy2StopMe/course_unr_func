# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
from typing import Dict


class ShoppingCart:
    """
    ShoppingCart is a simple class to manage a shopping cart.

    Attributes:
    items (Dict[str, int]): A dictionary to hold products as keys
    and their quantities as values.
    """

    def __init__(self) -> None:
        """Initializes an empty shopping cart."""
        self.items: Dict[str, int] = {}

    def contains(self, product_name):
        """Check is product."""
        return product_name in self.items

    def add(self, product_name: str, quantity: int) -> None:
        """
        Add a product to the cart or update its quantity.

        Args:
            product_name (str): The name of the product to be added.
            quantity (int): The quantity of the product to be added.
        """
        self.items[product_name] = self.items.get(product_name, 0) + quantity

    def remove(self, product_name: str, quantity: int) -> None:
        """
        Remove a product or reduce its quantity in the cart.

        Args:
            product_name (str): The name of the product to be removed.
            quantity (int): The quantity of the product to be removed.
        """
        if product_name in self.items:
            self.items[product_name] -= quantity
            if self.items[product_name] <= 0:
                del self.items[product_name]

    def total_cost(self, products):
        """
        Calculates the total cost of items in the cart.

        Args:
            products (Dict): Dictionary containing product details.

        Returns:
            float: Total cost of items in the cart.
        """
        total_price = 0
        for product, quantity in self.items.items():
            product_price = products[product]['price']

            # Попробуйте преобразовать строковую цену в число
            if isinstance(product_price, str):
                try:
                    product_price = float(product_price)
                except ValueError:
                    continue

            if isinstance(product_price, (int, float)):
                total_price += product_price * quantity

        return total_price

    def summary(self, products):
        total_price = self.total_cost(products)
        summary_str = ''
        products_with_str_price = []

        for product, quantity in self.items.items():
            product_price = products[product]['price']

            if isinstance(product_price, str):
                try:
                    product_price_val = float(product_price)
                except ValueError:
                    products_with_str_price.append(product)
                    summary_str += (f"{product}: {quantity} шт."
                                    f"- {product_price}\n")
                    continue
            else:
                product_price_val = product_price

            summary_str += (f"{product}: {quantity} шт. - "
                            f"{product_price_val * quantity} грн\n")

        if total_price > 0 and products_with_str_price:
            str_products = ([f"\"{product}\"" for product
                             in products_with_str_price])
            summary_str += (
                f"\nЗагальна вартість: {total_price} грн., не включаючи" +
                f" {', '.join(str_products)}.")
        elif total_price > 0:
            summary_str += f"\nЗагальна вартість: {total_price} грн."

        return summary_str

    def get(self, product_name: str) -> int:
        """
        Get the quantity of a product in the cart.

        Args:
            product_name (str): The name of the product.

        Returns:
            int: The quantity of the product in the cart, 0 if not found.
        """
        return self.items.get(product_name, "")

    def is_empty(self) -> bool:
        """
        Checks if the cart is empty.

        Returns:
            bool: True if the cart is empty, False otherwise.
        """
        return not bool(self.items)
