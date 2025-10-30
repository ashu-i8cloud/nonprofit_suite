import logging
_logger = logging.getLogger(__name__)
_logger.info("GMSS: models __init__ loaded")

from . import product
from . import partner
from . import birthday
from . import event_registration
from . import sale_order
from . import payment_transaction   # <-- ensure this line exists
from . import donation_report