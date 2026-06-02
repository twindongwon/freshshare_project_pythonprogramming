# FreshShare OCR 모델 베이스라인

영수증 이미지 또는 데모 텍스트에서 품목명을 추출하고, `data/freshshare_items.json`의 품목별 소비기한/보관방법 데이터와 매칭해 FreshShare 등록 데이터로 변환합니다.

## 실행

OCR 라이브러리 없이 데모 텍스트로 먼저 확인:

```powershell
python ocr_baseline.py --demo-text data/sample_receipt.txt
```

영수증 이미지로 실행하려면 EasyOCR 또는 PaddleOCR 설치 후:

```powershell
python ocr_baseline.py --image receipt.jpg
```

## 출력

결과는 기본적으로 `data/freshshare_ocr_result.json`에 저장됩니다.

포함 필드:

- `matchedFood`: 인식된 기준 품목
- `displayName`: FreshShare 표시 품목명
- `storageType`: 기본 보관환경
- `shelfLifeDays`: 소비기한 참고 일수
- `purchaseFrequency`: 구매빈도 기본값
- `storageMethod`: 보관방법
- `sourceUrl`: 데이터 근거 URL

## 발표에서 설명할 포인트

1. 영수증 OCR이 품목명과 구매일을 읽음
2. FreshShare 품목 데이터셋과 매칭
3. 소비기한/D-day/보관방법을 자동 완성
4. 등록 화면에서 사용자가 확인 후 나눔·교환·판매로 게시
