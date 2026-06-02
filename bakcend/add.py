# backend/app.py
# FreshShare 백엔드: Donut 모델로 영수증 이미지를 JSON으로 파싱
# 실행: uvicorn app:app --host 0.0.0.0 --port 8000
import io
import re
import torch
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from transformers import DonutProcessor, VisionEncoderDecoderModel

app = FastAPI(title="FreshShare Donut OCR API")

# CORS: Netlify 프론트에서 호출할 수 있게 허용 (배포 후 도메인으로 좁히세요)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # 예: ["https://your-site.netlify.app"]
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_NAME = "naver-clova-ix/donut-base-finetuned-cord-v2"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

print(f"[FreshShare] 모델 로딩 중... ({MODEL_NAME}) device={DEVICE}")
processor = DonutProcessor.from_pretrained(MODEL_NAME)
model = VisionEncoderDecoderModel.from_pretrained(MODEL_NAME).to(DEVICE)
model.eval()
print("[FreshShare] 모델 로딩 완료")


def run_donut(image: Image.Image) -> dict:
    """영수증 이미지를 Donut으로 파싱해 dict로 반환"""
    task_prompt = "<s_cord-v2>"
    decoder_input_ids = processor.tokenizer(
        task_prompt, add_special_tokens=False, return_tensors="pt"
    ).input_ids.to(DEVICE)

    pixel_values = processor(image, return_tensors="pt").pixel_values.to(DEVICE)

    with torch.no_grad():
        outputs = model.generate(
            pixel_values,
            decoder_input_ids=decoder_input_ids,
            max_length=model.decoder.config.max_position_embeddings,
            pad_token_id=processor.tokenizer.pad_token_id,
            eos_token_id=processor.tokenizer.eos_token_id,
            use_cache=True,
            bad_words_ids=[[processor.tokenizer.unk_token_id]],
            return_dict_in_generate=True,
        )

    seq = processor.batch_decode(outputs.sequences)[0]
    seq = seq.replace(processor.tokenizer.eos_token, "").replace(
        processor.tokenizer.pad_token, ""
    )
    seq = re.sub(r"<.*?>", "", seq, count=1).strip()
    return processor.token2json(seq)


def to_freshshare(parsed: dict) -> dict:
    """Donut 결과(CORD 포맷)를 프론트가 쓰기 쉬운 형태로 변환"""
    items = []
    menu = parsed.get("menu", [])
    if isinstance(menu, dict):
        menu = [menu]
    for m in menu:
        name = m.get("nm", "")
        price = m.get("price", "")
        price_num = int(re.sub(r"[^0-9]", "", str(price)) or 0)
        items.append({"name": name, "priceKrw": price_num})

    total = parsed.get("total", {})
    total_price = ""
    if isinstance(total, dict):
        total_price = total.get("total_price", "")

    return {
        "items": items,
        "totalPrice": re.sub(r"[^0-9]", "", str(total_price)) or "",
        "raw": parsed,
    }


@app.get("/")
def health():
    return {"status": "ok", "model": MODEL_NAME, "device": DEVICE}


@app.post("/ocr")
async def ocr(file: UploadFile = File(...)):
    content = await file.read()
    image = Image.open(io.BytesIO(content)).convert("RGB")
    parsed = run_donut(image)
    return to_freshshare(parsed)
