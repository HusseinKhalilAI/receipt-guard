from engine.rksv import parse_rksv, rksv_detection_layer
from decimal import Decimal
from datetime import datetime
import pytest
import qrcode
from PIL import Image
import base64
from engine.rksv import valid_rksv_flags

valid_rksv_code = "_R1-AT1_303_31238_2026-10-20T14:33:34_4,60_0,00_0,00_0,00_0,00_7YUycWPgbRM=_51EE7939_sJePBFs6KwE=_Ffi3/ApQsH898x/hVu6FhGppmmmfBVc7yWUGQyA1ze9paszK2TfUBCehIUhF2SIbiUO7ZyVhTdChIcVT3FuzQQ=="

######################################################################### validity test

def test_rksv_validity():
    
    rksv_record = parse_rksv(valid_rksv_code)  

    assert rksv_record.register_id == "303"
    assert rksv_record.receipt_number == "31238"
    assert rksv_record.issued_at == datetime(2026, 10, 20, 14, 33, 34)
    assert rksv_record.amount_normal == Decimal("4.60")
    assert rksv_record.amount_reduced_1 == Decimal("0.00")


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

################################################################################## layer tests

def test_rksv_layer_valid():
    valid_qrcode = qrcode.make(valid_rksv_code).convert("RGB")
    result = rksv_detection_layer(valid_qrcode)
    assert result.status == "valid"
    assert result.record.register_id == "303"



def test_rksv_layer_invalid():
    invalid_qrcode = qrcode.make(valid_rksv_code.replace("_4,60_", "_4,6_")).convert("RGB")
    result = rksv_detection_layer(invalid_qrcode)
    assert result.status == "malformed"
    assert result.record == None


def test_rksv_layer_notavailable():
    blank_img= Image.new("RGB", (200, 200), "white")
    result = rksv_detection_layer(blank_img)
    assert result.status == "not_available"
    assert result.record == None
####################################################################################### flags test

def test_rksv_flags_clean_receipt():
    rksv_record = parse_rksv(valid_rksv_code)
    assert valid_rksv_flags(rksv_record) == []


def test_rksv_flags_date_in_future():
    future_code = valid_rksv_code.replace("2026-10-20T14:33:34", "2030-10-20T14:33:34")
    rksv_record = parse_rksv(future_code)
    assert "date_in_future" in valid_rksv_flags(rksv_record)


def test_rksv_flags_before_rksv_date():
    old_code = valid_rksv_code.replace("2026-10-20T14:33:34", "2016-10-20T14:33:34")
    rksv_record = parse_rksv(old_code)
    assert "before_rksv_date" in valid_rksv_flags(rksv_record)


def test_rksv_flags_training_receipt():
    training_code = valid_rksv_code.replace("7YUycWPgbRM=", "VFJB")
    rksv_record = parse_rksv(training_code)
    assert "training_receipt" in valid_rksv_flags(rksv_record)


def test_rksv_flags_voided_receipt():
    voided_code = valid_rksv_code.replace("7YUycWPgbRM=", "U1RP")
    rksv_record = parse_rksv(voided_code)
    assert "voided_receipt" in valid_rksv_flags(rksv_record)


def test_rksv_flags_signature_device_failed():
    failed_signature = base64.b64encode("Sicherheitseinrichtung ausgefallen".encode()).decode()
    code_without_signature = valid_rksv_code.rsplit("_", 1)[0]
    failed_device_code = f"{code_without_signature}_{failed_signature}"
    rksv_record = parse_rksv(failed_device_code)
    assert "signature_device_failed" in valid_rksv_flags(rksv_record)





    
    

