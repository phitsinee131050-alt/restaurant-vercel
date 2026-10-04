import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app.services.billing_service import calc, split
def test_calc():
    c = calc(140, 10)
    assert (c["service"], c["vat"], c["total"]) == (13.0, 10.01, 153.01)
    assert split(153.01, 3) == 51.0
