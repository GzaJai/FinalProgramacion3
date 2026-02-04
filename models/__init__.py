"""
This is the __init__.py file for the models package.

It imports all the models for easier access.
"""

# If these models are used in other files via this package,
# you can ignore the 'unused import' warning.
# Otherwise, remove the unused imports.
"""
This is the __init__.py file for the models package.

It imports all the models so SQLAlchemy can register all mappers.
"""

from models.user import User
from models.client import ClientModel
from models.category import CategoryModel
from models.product import ProductModel
from models.order import OrderModel
from models.order_detail import OrderDetailModel
from models.address import AddressModel
from models.review import ReviewModel
from models.bill import BillModel