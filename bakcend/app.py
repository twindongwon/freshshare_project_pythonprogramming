# backend/app.py
# FreshShare 백엔드: PaddleOCR로 한글 영수증 이미지를 텍스트로 읽고 파싱
# 실행: uvicorn app:app --host 0.0.0.0 --port 8000
import io
import re
import numpy as np
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from paddleocr import PaddleOCR

app = FastAPI(title="FreshShare PaddleOCR API")

# CORS: Netlify 프론트에서 호출할 수 있게 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_NAME = "paddleocr-korean"

print("[FreshShare] PaddleOCR 모델 로딩 중...")
# 한국어 인식 모델 로드 (처음 실행 시 모델 자동 다운로드)
ocr_engine = PaddleOCR(use_angle_cls=True, lang="korean")
print("[FreshShare] PaddleOCR 모델 로딩 완료")


def run_ocr(image: Image.Image):
    """이미지를 PaddleOCR로 읽어 줄 단위 (텍스트, 신뢰도) 리스트 반환"""
    img_array = np.array(image)
    result = ocr_engine.ocr(img_array, cls=True)
    lines = []
    if result and result[0]:
        for line in result[0]:
            text = line[1][0]
            conf = float(line[1][1])
            lines.append((text, conf))
    return lines


def parse_price(text: str) -> int:
    """문자열에서 숫자만 뽑아 정수로 (쉼표 제거)"""
    digits = re.sub(r"[^0-9]", "", text)
    return int
