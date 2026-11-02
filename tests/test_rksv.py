from engine.rksv import parse_rksv
from decimal import Decimal
from datetime import datetime
import pytest

def test_rksv_validity():
    rksv_code = "_R1-AT1_303_31238_2026-10-20T14:33:34_4,60_0,00_0,00_0,00_0,00_7YUycWPgbRM=_51EE7939_sJePBFs6KwE=_Ffi3/ApQsH898x/hVu6FhGppmmmfBVc7yWUGQyA1ze9paszK2TfUBCehIUhF2SIbiUO7ZyVhTdChIcVT3FuzQQ=="
    rksv_record = parse_rksv(rksv_code)  

    assert rksv_record.register_id == "303"
    assert rksv_record.receipt_number == "31238"
    assert rksv_record.issued_at == datetime(2026, 10, 20, 14, 33, 34)
    assert rksv_record.amount_normal == Decimal("4.60")
    assert rksv_record.amount_reduced_1 == Decimal("0.00")





valid_rksv_code = "_R1-AT1_303_31238_2026-10-20T14:33:34_4,60_0,00_0,00_0,00_0,00_7YUycWPgbRM=_51EE7939_sJePBFs6KwE=_Ffi3/ApQsH898x/hVu6FhGppmmmfBVc7yWUGQyA1ze9paszK2TfUBCehIUhF2SIbiUO7ZyVhTdChIcVT3FuzQQ=="


def test_rksv_too_few_pieces():
    code_without_signature = valid_rksv_code.rsplit("_", 1)[0]
    with pytest.raises(ValueError):
        parse_rksv(code_without_signature)


def test_rksv_wrong_prefix():
    code_with_wrong_prefix = valid_rksv_code.replace("R1-AT1", "X1-AT1")
    with pytest.raises(ValueError):
        parse_rksv(code_with_wrong_prefix)


def test_rksv_invalid_amount():
    code_with_invalid_amount = valid_rksv_code.replace("_4,60_", "_4,6_")
    with pytest.raises(ValueError):
        parse_rksv(code_with_invalid_amount)


def test_rksv_invalid_date():
    code_with_invalid_date = valid_rksv_code.replace("2026-10-20T14:33:34", "2026-10-20 14:33:34")
    with pytest.raises(ValueError):
        parse_rksv(code_with_invalid_date)
