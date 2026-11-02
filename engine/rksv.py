from PIL import Image
from pillow_heif import register_heif_opener
import zxingcpp
import pathlib
import cv2
import numpy as np
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
import pandas as pd
from datetime import datetime
import re


register_heif_opener()
#########################
def path2img(path)-> Image: # function for my own sanity, remove later######### -----------
    img = Image.open(path)
    return img
########################
def extract_rksv(img):

    decoded_qr = zxingcpp.read_barcodes(img)


    for qr in decoded_qr:
        if qr.text.startswith("_R1-AT"):
            return qr.text

    return None

def find_crop_qrcode(img:Image.Image, zoom_factor:float = 1.0):  # used in case zxingcpp cant't detect a QR code due to quality issues -> locate it and crop it using CV2
    img2array = np.array(img)
    opencv_detector = cv2.QRCodeDetector()
    qr_found, qr_corners  = opencv_detector.detect(img2array)
    if qr_found:
        x_min, y_min = qr_corners[0].min(axis=0)
        x_max, y_max = qr_corners[0].max(axis=0)
        margin = 50
        qr_crop = img2array[
            max(0, int(y_min) - margin) : int(y_max) + margin,
            max(0, int(x_min) - margin) : int(x_max) + margin,
        ]

        zoomed_crop = cv2.resize(qr_crop, None, fx=zoom_factor, fy=zoom_factor, interpolation=cv2.INTER_CUBIC)

        return zoomed_crop
  
    return None



def split_rksv(rksv_string: str) -> list[str]:

    return rksv_string.split("_")


def rksv_process(img: Image.Image) -> str | None:

    rksv = extract_rksv(img)

    if rksv is None:
        cropped = find_crop_qrcode(img,zoom_factor=1)
        if cropped is not None:
            rksv = extract_rksv(cropped)
            return rksv
        return None

    return rksv

        
def rksv_mass_process(data_path: str) -> pd.DataFrame:
    decoding_results = []

    for image_path in sorted(pathlib.Path(data_path).rglob("*.HEIC")):
        receipt_image = Image.open(image_path)
        decoding_results.append({
            "shop": image_path.parent.name,
            "file": image_path.name,
            "rksv_code": rksv_process(receipt_image),
        })

    results_table = pd.DataFrame(decoding_results)
    results_table["decoded"] = results_table["rksv_code"].notna()
    return results_table


def parse_amount(amount_text: str) -> Decimal:
    reformed = amount_text.replace(",",".")

    return Decimal(reformed)


def parse_issued_at(date_text: str) -> datetime:

    date_time = datetime.fromisoformat(date_text)
    return date_time


@dataclass
class RksvRecord:
    algorithm_and_provider: str
    register_id: str
    receipt_number: str
    issued_at: datetime
    amount_normal: Decimal
    amount_reduced_1: Decimal
    amount_reduced_2: Decimal
    amount_zero: Decimal
    amount_special: Decimal
    encrypted_turnover: str
    certificate_serial: str
    previous_receipt_signature: str
    signature: str


def validate_rksv(rksv_pieces):

    if len(rksv_pieces) != 14:
        raise ValueError(f"RKSV contains 14 pieces, got {len(rksv_pieces)}.")

    if rksv_pieces[0] != "": 
        raise ValueError(f"First piece is invalid: {rksv_pieces[0]}")

    if not rksv_pieces[1].startswith("R1-AT"):
        raise ValueError(f"Entry is not RKSV: {rksv_pieces[1]}")

    match_datetime = re.fullmatch(r"\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d" ,rksv_pieces[4])

    if match_datetime is None:
        raise ValueError(f"Date or time is invalid: {rksv_pieces[3]}")

    amounts = rksv_pieces[5:10]

    for piece in amounts:
        match_amount = re.fullmatch(r"-?\d+,\d\d",piece)
        if match_amount is None:
            raise ValueError(f"An amount is invalid: {piece}")

def parse_rksv(rksv_code: str) -> RksvRecord:

    rksv_pieces = split_rksv(rksv_code)
    validate_rksv(rksv_pieces)

    return RksvRecord(
        algorithm_and_provider = rksv_pieces[1], #code starts with _, starting at index 1 
        register_id = rksv_pieces[2], 
        receipt_number = rksv_pieces[3],
        issued_at = parse_issued_at(rksv_pieces[4]),
        amount_normal = parse_amount(rksv_pieces[5]),
        amount_reduced_1 = parse_amount(rksv_pieces[6]),
        amount_reduced_2 = parse_amount(rksv_pieces[7]),
        amount_zero = parse_amount(rksv_pieces[8]),
        amount_special = parse_amount(rksv_pieces[9]),
        encrypted_turnover = rksv_pieces[10],
        certificate_serial = rksv_pieces[11],
        previous_receipt_signature = rksv_pieces[12],
        signature = rksv_pieces[13]
        )





