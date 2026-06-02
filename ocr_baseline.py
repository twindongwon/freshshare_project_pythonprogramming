import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ITEMS_PATH = ROOT / "data" / "freshshare_items.json"
OUT_PATH = ROOT / "data" / "freshshare_ocr_result.json"


def load_text_from_image(image_path: str) -> str:
    """Try EasyOCR first, then PaddleOCR. If neither is installed, fail softly."""
    try:
        import easyocr

        reader = easyocr.Reader(["ko", "en"], gpu=False)
        rows = reader.readtext(image_path, detail=0, paragraph=False)
        return "\n".join(rows)
    except Exception as easy_error:
        try:
            from paddleocr import PaddleOCR

            ocr = PaddleOCR(use_angle_cls=True, lang="korean")
            result = ocr.ocr(image_path, cls=True)
            lines = []
            for page in result or []:
                for row in page or []:
                    if len(row) >= 2 and row[1]:
                        lines.append(str(row[1][0]))
            return "\n".join(lines)
        except Exception as paddle_error:
            raise RuntimeError(
                "EasyOCR/PaddleOCR이 설치되어 있지 않거나 이미지 인식에 실패했습니다. "
                "데모 실행은 --demo-text 옵션을 사용하세요.\n"
                f"EasyOCR error: {easy_error}\nPaddleOCR error: {paddle_error}"
            )


def normalize(text: str) -> str:
    return re.sub(r"[^0-9A-Za-z가-힣]+", " ", text).strip().lower()


def extract_purchase_date(text: str) -> str | None:
    patterns = [
        r"(20\d{2})[./-](\d{1,2})[./-](\d{1,2})",
        r"(\d{1,2})[./-](\d{1,2})",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match and len(match.groups()) == 3:
            y, m, d = match.groups()
            return f"{int(y):04d}-{int(m):02d}-{int(d):02d}"
        if match and len(match.groups()) == 2:
            m, d = match.groups()
            return f"2026-{int(m):02d}-{int(d):02d}"
    return None


def extract_price(line: str) -> int | None:
    matches = re.findall(r"\d{1,3}(?:,\d{3})+|\d{3,6}", line)
    if not matches:
        return None
    return int(matches[-1].replace(",", ""))


def match_items(receipt_text: str, item_db: list[dict]) -> list[dict]:
    normalized_receipt = normalize(receipt_text)
    found = []
    for item in item_db:
        names = {item["baseFood"], item["itemName"].split()[0]}
        for name in names:
            if normalize(name) and normalize(name) in normalized_receipt:
                source_line = next((line for line in receipt_text.splitlines() if name in line), "")
                found.append(
                    {
                        "matchedFood": item["baseFood"],
                        "displayName": item["itemName"],
                        "category": item["category"],
                        "storageType": item["storageType"],
                        "shelfLifeDays": item["shelfLifeDays"],
                        "purchaseFrequency": item["purchaseFrequency"],
                        "priceKrw": extract_price(source_line) or item.get("priceKrw", 0),
                        "freshshareItemId": item["id"],
                        "confidenceRule": "품목명 포함 규칙 매칭",
                        "storageMethod": item["preservationMethod"],
                        "sourceUrl": item["sourceUrl"],
                    }
                )
                break
    return found


def main():
    parser = argparse.ArgumentParser(description="FreshShare receipt OCR baseline")
    parser.add_argument("--image", help="영수증 이미지 경로")
    parser.add_argument("--demo-text", help="OCR 없이 사용할 영수증 텍스트 파일")
    parser.add_argument("--out", default=str(OUT_PATH), help="FreshShare 등록 JSON 출력 경로")
    args = parser.parse_args()

    if not args.image and not args.demo_text:
        raise SystemExit("--image 또는 --demo-text 중 하나를 입력하세요.")

    if args.demo_text:
        receipt_text = Path(args.demo_text).read_text(encoding="utf-8")
        ocr_engine = "demo-text"
    else:
        receipt_text = load_text_from_image(args.image)
        ocr_engine = "easyocr-or-paddleocr"

    item_db = json.loads(ITEMS_PATH.read_text(encoding="utf-8"))
    purchase_date = extract_purchase_date(receipt_text)
    matched = match_items(receipt_text, item_db)

    payload = {
        "ocrEngine": ocr_engine,
        "purchaseDate": purchase_date,
        "rawText": receipt_text,
        "freshshareRegisterItems": matched,
        "nextAction": "freshshare_interactive.html의 등록 화면에서 품목명, 구매일, 보관환경, 소비기한을 자동 채움",
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"out": str(out_path), "matched": len(matched), "purchaseDate": purchase_date}, ensure_ascii=False))


if __name__ == "__main__":
    main()
