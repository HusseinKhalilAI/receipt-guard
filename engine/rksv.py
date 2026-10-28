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

register_heif_opener()


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





