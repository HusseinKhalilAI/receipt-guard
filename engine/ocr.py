from PIL import Image, ImageDraw,ImageOps
from pillow_heif import register_heif_opener
import zxingcpp
import pathlib
import cv2
import numpy as np
from dataclasses import dataclass
from datetime import datetime,timedelta
from decimal import Decimal
import pandas as pd
from datetime import datetime
import re

from paddleocr import PaddleOCR
import base64
import time
import functools

register_heif_opener()


@dataclass
class OCR:
    text: str
    confidence: float
    box: list[tuple[int,int]]

@functools.lru_cache
def create_paddle_reader():

    return  PaddleOCR(
            lang="de",
            use_doc_orientation_classify=True,
            use_doc_unwarping=False,
            use_textline_orientation=False,
            )



def read_receipt_lines(img:Image.Image) -> list[OCR]:

    
    reader = create_paddle_reader()

    ocr_lines = []
   
    rec_img = img.copy()
    rec_img.thumbnail((2000, 2000))
    input_receipt = rec_img.convert("RGB")
    results_paddle = reader.predict(np.array(input_receipt))

    for page in results_paddle:
        for text, score, polys in zip(page["rec_texts"], page["rec_scores"],page["rec_polys"]):
            ocr_lines.append(OCR(text = text,confidence = float(score), box = [(int(point[0]), int(point[1])) for point in polys]))
            
    
    return ocr_lines


def get_center(box: list[tuple[int,int]])-> float:
    y_values = [y for x,y in box]
    return sum(y_values)/len(y_values)

def get_height(box: list[tuple[int,int]])-> int:
    y_values = [y for x,y in box]
    height = max(y_values) - min(y_values)
    return height


def group_into_rows(segments:list[OCR])->list[list[OCR]]:

    segments_center_sorted = sorted(segments,key=lambda seg:get_center(seg.box))

    lines = []
    current_line = []

    for segment in segments_center_sorted:
        if not current_line:
            current_line.append(segment)
            continue
        else:
            current_row_center = sum([get_center(row_segment.box) for row_segment in current_line])/len(current_line)
            gap = abs(get_center(segment.box) - current_row_center)
            if gap < get_height(segment.box)/2:
                current_line.append(segment)
            else:
                lines.append(current_line)
                current_line = [segment]
    if current_line:
        lines.append(current_line)

    horizontally_sorted = [sorted(row, key=lambda seg: min(x for x, y in seg.box)) for row in lines]

    return horizontally_sorted




    








