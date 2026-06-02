# FreshShare AI Prototype

FreshShare는 1인 가구와 자취생이 남는 식재료를 소비기한 전에 나눔, 교환, 판매할 수 있도록 돕는 모바일 프로토타입입니다.

## 구성

- `freshshare_interactive.html`: 데이터셋과 연결된 7화면 인터랙티브 프로토타입
- `freshshare_mapping_report.html`: 강의교재 PDF와 프로토타입, 데이터셋, MCP 연결 매핑 보고서
- `data/freshshare_items.json`: GitHub 업로드용 원본 품목 데이터셋
- `data/freshshare_items.csv`: 엑셀/발표용 품목 데이터셋
- `data/freshshare_items.js`: HTML에서 바로 읽는 데이터 연결 파일
- `ocr_baseline.py`: EasyOCR/PaddleOCR 기반 영수증 OCR 베이스라인
- `OCR_BASELINE.md`: OCR 실행 설명
- `supabase_schema.sql`: 온라인 공유형 등록글/채팅을 위한 Supabase 테이블 스키마
- `config.example.js`: Supabase 연결 설정 예시
- `private_data/`: 개인정보성 데이터 스키마와 익명 샘플
- `outputs/freshshare_mapping/FreshShare_강의교재_데이터_MCP_매핑.xlsx`: 강의교재 매핑과 품목별 세부 데이터 엑셀

## 데이터셋 필드

품목별로 다음 데이터를 포함합니다.

- 품목명, 기준식품, 카테고리, 수량
- 거래방식, 가격, 위치, 거리
- 보관환경, 구매일, 소비기한일수, 남은일수, 소비기한
- 구매빈도
- 보관방법, 보관팁, 소비기한 근거, 출처 URL
- HTML/AI 활용 방식

## 실행 방법

로컬에서는 `freshshare_interactive.html`을 브라우저로 열면 됩니다.

현재 프로토타입 기능:

- 닉네임/동네 기반 로그인
- 상품 직접 등록
- 홈 피드에서 등록 상품 확인
- 상세 화면에서 소비기한/보관방법 확인
- 채팅 메시지 전송과 자동 응답
- 기본 저장 방식은 브라우저 `localStorage`

여러 사용자가 같은 등록글과 채팅을 보려면 Supabase를 연결합니다.

1. Supabase 프로젝트 생성
2. SQL Editor에서 `supabase_schema.sql` 실행
3. `config.example.js`를 `config.js`로 복사
4. `supabaseUrl`, `supabaseAnonKey` 입력
5. GitHub Pages에 함께 업로드

GitHub Pages에서 열려면 저장소에 파일을 업로드한 뒤:

1. GitHub 저장소 `Settings`로 이동
2. `Pages` 메뉴 선택
3. `Deploy from a branch`
4. Branch: `main`, Folder: `/root`
5. 저장 후 발급되는 URL에서 `freshshare_interactive.html` 접속

## GitHub 업로드 명령

PC에 Git이 설치되어 있고 GitHub 저장소를 먼저 만든 경우:

```powershell
git init
git add README.md .gitignore .nojekyll freshshare_interactive.html freshshare_mapping_report.html OCR_BASELINE.md ocr_baseline.py supabase_schema.sql config.example.js data private_data outputs/freshshare_mapping/FreshShare_강의교재_데이터_MCP_매핑.xlsx
git commit -m "feat: add FreshShare prototype dataset mapping"
git branch -M main
git remote add origin https://github.com/YOUR_ID/freshshare-ai.git
git push -u origin main
```

## Claude MCP 연결 메모

- File System MCP: 프로젝트 폴더만 허용 경로로 연결
- Context7 MCP: 최신 React/Tailwind 문서 확인용
- Figma MCP: 7개 화면 와이어프레임/디자인 토큰 생성
- Notion MCP: PRD와 페르소나 DB 저장
- GitHub MCP: README, 이슈, 저장소 관리 자동화

## 주의

소비기한은 제품 표시사항을 우선해야 하며, 이 데이터셋의 소비기한일수는 MVP 자동 추천을 위한 참고값입니다.
