import io, re, numpy as np
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import easyocr

app = FastAPI(title="FreshShare EasyOCR API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

MODEL_NAME = "easyocr-korean"
print("[FreshShare] EasyOCR loading...")
reader = easyocr.Reader(["ko", "en"], gpu=True)
print("[FreshShare] EasyOCR loaded")

def run_ocr(image):
    img_array = np.array(image)
    results = reader.readtext(img_array)
    tokens = []
    for box, text, conf in results:
        ys = [p[1] for p in box]; xs = [p[0] for p in box]
        tokens.append({"text": text, "conf": float(conf), "x": sum(xs)/len(xs), "y": sum(ys)/len(ys)})
    return tokens

def parse_price(text):
    digits = re.sub(r"[^0-9]", "", text)
    return int(digits) if digits else 0

def to_freshshare(tokens):
    tokens = sorted(tokens, key=lambda t: t["y"])
    rows = []
    for tk in tokens:
        placed = False
        for row in rows:
            if abs(row["y"] - tk["y"]) < 15:
                row["tokens"].append(tk); placed = True; break
        if not placed:
            rows.append({"y": tk["y"], "tokens": [tk]})
    SKIP = ["합계","합 계","결제대상","부가세","과세","면세","총액","단가","수량","금액","상품명","POS","구 매","구매","교환","환불","영수증","신선","물품","상 금","대 상","부 가","면 품","새 물","제 대"]
    items, total_price, raw_lines = [], 0, []
    for row in rows:
        toks = sorted(row["tokens"], key=lambda t: t["x"])
        line_text = " ".join(t["text"] for t in toks)
        raw_lines.append(line_text)
        if any(k in line_text for k in ["합계","합 계","결제대상"]):
            nums = [parse_price(t["text"]) for t in toks if re.search(r"[0-9]", t["text"])]
            if nums: total_price = max(nums)
            continue
        if any(k in line_text for k in SKIP):
            continue
        price_toks = [t for t in toks if re.fullmatch(r"[0-9,]{2,}", t["text"].strip())]
        name_toks = [t for t in toks if not re.fullmatch(r"[0-9,./*]+", t["text"].strip())]
        name = re.sub(r"^[0-9*\s]+", "", " ".join(t["text"] for t in name_toks)).strip()
        if price_toks and name and len(name) >= 2:
            hangul = re.findall(r"[가-힣]", name)
            if len(hangul) >= 2:
                price = parse_price(price_toks[-1]["text"])
                if price > 0:
                    items.append({"name": name, "priceKrw": price})
    return {"items": items, "totalPrice": str(total_price) if total_price else "", "raw": raw_lines}

@app.get("/")
def health():
    return {"status": "ok", "model": MODEL_NAME}

@app.post("/ocr")
async def ocr(file: UploadFile = File(...)):
    content = await file.read()
    image = Image.open(io.BytesIO(content)).convert("RGB")
    tokens = run_ocr(image)
    return to_freshshare(tokens)
