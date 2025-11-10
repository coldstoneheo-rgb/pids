# 개인화된 투자 의사 결정 시스템 - 시작 튜토리얼

## 초보자를 위한 완벽 가이드

이 튜토리얼은 프로그래밍 경험이 적은 분들도 쉽게 따라할 수 있도록 작성되었습니다.

---

## 📋 목차

1. [시작하기 전에](#시작하기-전에)
2. [Step 1: Python 설치](#step-1-python-설치)
3. [Step 2: 프로젝트 다운로드](#step-2-프로젝트-다운로드)
4. [Step 3: 필수 라이브러리 설치](#step-3-필수-라이브러리-설치)
5. [Step 4: 투자 전략 설정](#step-4-투자-전략-설정)
6. [Step 5: 첫 종목 분석](#step-5-첫-종목-분석)
7. [Step 6: 결과 해석하기](#step-6-결과-해석하기)
8. [자주 발생하는 오류 해결](#자주-발생하는-오류-해결)

---

## 시작하기 전에

### 필요한 것들

- ✅ 컴퓨터 (Windows, macOS, Linux 모두 가능)
- ✅ 인터넷 연결
- ✅ 약 30분의 시간
- ✅ Python 3.8 이상 (설치 방법은 아래 참고)

### 예상 소요 시간

- 설치: 15-20분
- 설정: 10분
- 첫 분석: 5분

---

## Step 1: Python 설치

### Python이 이미 설치되어 있는지 확인

#### Windows

1. **Windows 키 + R** 누르기
2. `cmd` 입력 후 Enter
3. 다음 명령어 입력:

```bash
python --version
```

#### macOS/Linux

1. **터미널** 열기
2. 다음 명령어 입력:

```bash
python3 --version
```

### 결과 확인

```
Python 3.10.5
```

이런 식으로 `Python 3.8` 이상의 버전이 표시되면 **설치 완료**입니다! ✅

Step 2로 바로 이동하세요.

---

### Python이 없거나 버전이 낮은 경우

#### Windows 설치

1. https://www.python.org/downloads/ 접속
2. **Download Python 3.x.x** 버튼 클릭 (최신 버전)
3. 다운로드한 파일 실행
4. ⚠️ **중요**: 설치 화면에서 **"Add Python to PATH"** 체크 ✅
5. **Install Now** 클릭
6. 설치 완료 후 컴퓨터 재부팅

#### macOS 설치

**방법 1: Homebrew 사용 (권장)**

```bash
# Homebrew 설치 (없는 경우)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Python 설치
brew install python3
```

**방법 2: 공식 설치 파일**

1. https://www.python.org/downloads/macos/ 접속
2. 최신 macOS installer 다운로드
3. 설치 파일 실행

#### Linux (Ubuntu/Debian) 설치

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

---

## Step 2: 프로젝트 다운로드

### 방법 1: Git 사용 (권장)

```bash
# 프로젝트 클론
git clone https://github.com/coldstoneheo-rgb/math-learning-analyzer.git

# 프로젝트 폴더로 이동
cd math-learning-analyzer
```

### 방법 2: ZIP 다운로드

1. https://github.com/coldstoneheo-rgb/math-learning-analyzer 접속
2. 초록색 **Code** 버튼 클릭
3. **Download ZIP** 선택
4. 다운로드한 파일 압축 해제
5. 터미널/명령 프롬프트에서 해당 폴더로 이동:

```bash
cd 다운로드/math-learning-analyzer
```

### 확인

폴더 내용 확인:

```bash
# Windows
dir

# macOS/Linux
ls
```

다음 파일들이 보여야 합니다:
```
config/
src/
main.py
requirements.txt
README.md
```

---

## Step 3: 필수 라이브러리 설치

### 3.1 가상환경 생성 (선택사항이지만 강력 권장)

가상환경은 프로젝트별로 독립된 Python 환경을 만들어줍니다.

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

활성화되면 프롬프트 앞에 `(venv)`가 표시됩니다:
```
(venv) C:\Users\YourName\math-learning-analyzer>
```

#### macOS/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

활성화되면:
```
(venv) user@computer:~/math-learning-analyzer$
```

### 3.2 pip 업그레이드

```bash
pip install --upgrade pip
```

### 3.3 프로젝트 라이브러리 설치

```bash
pip install -r requirements.txt
```

**예상 소요 시간**: 5-10분

설치 중 다음과 같은 메시지가 계속 나타납니다:
```
Collecting yfinance>=0.2.38
  Downloading yfinance-0.2.38-py2.py3-none-any.whl
Installing collected packages: yfinance, pandas, ...
Successfully installed ...
```

### 3.4 TA-Lib 설치 (기술적 분석용)

⚠️ 이 부분이 가장 까다로울 수 있습니다.

#### macOS (가장 쉬움)

```bash
# Homebrew로 설치
brew install ta-lib

# Python 패키지 설치
pip install ta-lib
```

#### Ubuntu/Debian Linux

```bash
# 시스템 패키지 설치
sudo apt-get update
sudo apt-get install libta-lib-dev

# Python 패키지 설치
pip install ta-lib
```

#### Windows (복잡함)

**방법 1: 미리 컴파일된 바이너리 사용 (권장)**

1. https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib 접속
2. 자신의 Python 버전과 시스템에 맞는 파일 다운로드
   - Python 3.10, 64비트: `TA_Lib‑0.4.28‑cp310‑cp310‑win_amd64.whl`
   - Python 3.11, 64비트: `TA_Lib‑0.4.28‑cp311‑cp311‑win_amd64.whl`
3. 다운로드한 폴더에서:

```bash
pip install TA_Lib‑0.4.28‑cp310‑cp310‑win_amd64.whl
```

**방법 2: TA-Lib 없이 사용**

TA-Lib 설치가 안 되면, `pandas-ta`로 대체 가능:

```bash
pip install pandas-ta
```

> 📝 **참고**: TA-Lib 없이도 대부분의 기능이 작동하지만, 일부 기술적 지표는 사용할 수 없을 수 있습니다.

### 3.5 설치 확인

```bash
python -c "import yfinance, pandas, numpy; print('설치 성공!')"
```

출력:
```
설치 성공!
```

---

## Step 4: 투자 전략 설정

이제 시스템을 당신의 투자 스타일에 맞게 설정합니다.

### 4.1 투자 프로필 설정

파일 열기:
```bash
# Windows - 메모장으로 열기
notepad config\investment_profile.yaml

# macOS
open -e config/investment_profile.yaml

# Linux
nano config/investment_profile.yaml
```

### 4.2 기본 정보 입력

```yaml
investor_profile:
  name: "나의 투자 프로필"  # 👈 이름 변경
  risk_tolerance: "moderate_aggressive"  # 👈 아래 참고
  investment_horizon: "medium_to_long"   # 👈 아래 참고
```

**위험 감수 성향 선택:**
- `conservative`: 보수적 (안정성 중시)
- `moderate`: 중립적 (균형 추구)
- `moderate_aggressive`: 중립-공격적 (성장+안정)
- `aggressive`: 공격적 (고위험 고수익)

**투자 기간 선택:**
- `short`: 단기 (6개월 미만)
- `medium`: 중기 (6개월-2년)
- `long`: 장기 (2년 이상)
- `medium_to_long`: 중장기

### 4.3 관심 섹터 추가

```yaml
preferred_sectors:
  - "Technology"          # 기술
  - "Semiconductors"      # 반도체
  - "AI/ML"              # 인공지능
  - "Biotechnology"      # 바이오
  - "Electric Vehicles"  # 전기차
  # 👆 원하는 섹터 추가/삭제
```

### 4.4 투자 전략 설정 (고급)

**이미 당신의 전략이 반영되어 있습니다!**

`config/strategy_config.yaml` 파일에는:
- PBR ≤ 1.0
- PER 10-15배
- 거래량 충분
- 매수: 가격조정 후, 전저점 접근
- 매도: 100-200% 수익, 손절 -20%

변경하고 싶으면 같은 방법으로 파일을 열어 수정하세요.

---

## Step 5: 첫 종목 분석

드디어! 실제로 종목을 분석해봅시다.

### 5.1 프로그램 실행

```bash
python main.py
```

### 5.2 화면 출력

```
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║       개인화된 투자 의사 결정 시스템                       ║
    ║   Personal Investment Decision System (PIDS)             ║
    ║                                                           ║
    ║   당신의 투자 철학을 시스템화하다                          ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝


    ═══════════════ 메인 메뉴 ═══════════════

    1. 종목 분석 (단일 종목)
    2. 종목 스크리닝 (조건 검색)
    3. 관심 종목 관리
    4. 포트폴리오 분석
    5. 백테스팅
    6. 설정 관리
    0. 종료

    ═══════════════════════════════════════

메뉴 선택:
```

### 5.3 종목 분석 선택

```
메뉴 선택: 1  [Enter]
```

### 5.4 시장 선택

```
[ 종목 분석 ]
시장 선택: 1) 한국  2) 미국
선택: 1  [Enter]
```

### 5.5 종목 코드 입력

**한국 주식 예시:**
```
종목 코드 입력: 005930  [Enter]
```

- 삼성전자: 005930
- SK하이닉스: 000660
- NAVER: 035420
- 카카오: 035720

**미국 주식 예시:**
```
종목 코드 입력: AAPL  [Enter]
```

- Apple: AAPL
- Microsoft: MSFT
- Google: GOOGL
- Tesla: TSLA

### 5.6 분석 진행

```
005930 데이터 수집 중...
  ✓ 기본 정보 수집 완료
  ✓ 재무 데이터 수집 완료
  ✓ 주가 데이터 수집 완료 (365일)
  ✓ PBR 밴드 계산 완료
  ✓ 거래량 분석 완료

기술적 분석 수행 중...
  ✓ 이동평균선 계산 완료
  ✓ RSI 계산 완료
  ✓ MACD 계산 완료
  ✓ 지지/저항선 탐지 완료
  ✓ 매수 신호 생성 완료

체크리스트 생성 중...
  ✓ 정량적 지표 평가 완료
  ✓ 기술적 분석 평가 완료
  ✓ 종합 점수 계산 완료
```

⏳ **소요 시간**: 약 10-30초

---

## Step 6: 결과 해석하기

### 6.1 체크리스트 출력

```
============================================================
투자 의사결정 체크리스트
============================================================
종목: 삼성전자 (005930)
날짜: 2024-11-10
최종 결정: 매수 고려
신뢰도: MEDIUM
종합 점수: 65/100

[ 정량적 지표 ]
  ✓ PBR: 0.85 (목표: ≤ 1.0, 밴드 하단)
  ✓ PER: 12.5 (목표: 10~15배)
  ✓ VOLUME: 충분한 유동성
  ✓ MARKET_CAP: 적정 시가총액
  ✓ ROE: 8.5% (목표: ≥ 5%)
  ✗ DEBT_RATIO: 250% (목표: ≤ 200%)

[ 기술적 분석 ]
  ✓ 가격 조정 완료
  ✗ 횡보 구간 (기간 조정)
  ✓ 지지선 접근
  RSI: 35.2 (과매도)

[ 강점 ]
  + PBR
  + PER
  + VOLUME
  + 가격조정완료
  + 지지선접근
  + RSI과매도

[ 약점 ]
  - DEBT_RATIO

============================================================

체크리스트를 저장하시겠습니까? (y/n):
```

### 6.2 점수 의미

| 점수 | 의사결정 | 의미 |
|------|---------|------|
| **80-100점** | 매수 적극 추천 | 거의 모든 조건 만족 |
| **60-79점** | 매수 고려 | 대부분 조건 만족, 추가 검토 필요 |
| **40-59점** | 관심 종목 등록 | 일부 조건 만족, 지켜볼 필요 |
| **0-39점** | 투자 제외 | 조건 대부분 미달 |

### 6.3 신뢰도 의미

- **HIGH**: 데이터 충분, 신호 명확
- **MEDIUM**: 일부 불확실성 존재
- **LOW**: 데이터 부족 또는 신호 불명확

### 6.4 체크리스트 저장

```
체크리스트를 저장하시겠습니까? (y/n): y  [Enter]

저장 완료!
위치: data/checklists/005930_20241110_checklist.json
```

---

## 자주 발생하는 오류 해결

### 오류 1: "python을 찾을 수 없습니다"

**Windows:**
```
'python'은(는) 내부 또는 외부 명령, 실행할 수 있는 프로그램, 또는 배치 파일이 아닙니다.
```

**해결책:**
1. Python 재설치 (PATH에 추가 체크)
2. 또는 `python3` 명령어 사용
3. 또는 전체 경로 사용: `C:\Python310\python.exe main.py`

---

### 오류 2: "ModuleNotFoundError: No module named 'yfinance'"

```
ModuleNotFoundError: No module named 'yfinance'
```

**해결책:**
```bash
pip install -r requirements.txt
```

가상환경을 사용 중이라면 먼저 활성화:
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

---

### 오류 3: "종목 데이터를 가져올 수 없습니다"

```
종목 데이터를 가져올 수 없습니다.
```

**원인:**
- 잘못된 종목 코드
- 인터넷 연결 문제
- API 제한 (너무 많은 요청)

**해결책:**
1. 종목 코드 확인 (한국: 6자리, 미국: 대문자 심볼)
2. 인터넷 연결 확인
3. 1분 후 다시 시도
4. 다른 종목으로 테스트

---

### 오류 4: TA-Lib 관련 오류

```
ImportError: DLL load failed while importing _ta_lib
```

**해결책:**
1. TA-Lib 재설치 (위의 Step 3.4 참고)
2. 또는 시스템을 TA-Lib 없이 사용
3. `requirements.txt`에서 `ta-lib` 줄을 삭제하고 재설치

---

### 오류 5: 권한 오류 (Permission Denied)

```
PermissionError: [Errno 13] Permission denied: 'logs/app.log'
```

**해결책:**
```bash
# Windows - 관리자 권한으로 실행
# 또는 폴더 권한 확인

# macOS/Linux
chmod -R 755 .
```

---

## 다음 단계

### 🎯 연습 과제

1. **3-5개 종목 분석하기**
   - 본인이 관심있는 종목 선택
   - 체크리스트 비교
   - 점수가 가장 높은 종목 찾기

2. **설정 변경해보기**
   - `config/strategy_config.yaml` 파일 수정
   - PER 범위를 5-10으로 변경
   - 동일 종목 재분석 후 차이 확인

3. **관심 종목 관리**
   - 메뉴에서 "3. 관심 종목 관리" 선택
   - 좋은 점수를 받은 종목 추가

### 📚 추가 학습

- [상세 가이드](USAGE_GUIDE.md) 읽기
- [투자 전략 커스터마이징](USAGE_GUIDE.md#투자-전략-커스터마이징)
- [백테스팅 수행](USAGE_GUIDE.md#백테스팅-수행)

---

## 지원

### 문제 해결이 안 될 때

1. **GitHub Issues**: 버그나 문제 보고
2. **Discussion**: 질문 및 아이디어 공유
3. **README.md**: FAQ 확인

### 커뮤니티

- 이슈 등록: https://github.com/coldstoneheo-rgb/math-learning-analyzer/issues
- 토론: https://github.com/coldstoneheo-rgb/math-learning-analyzer/discussions

---

## 중요한 알림

⚠️ **투자 유의사항**

1. 이 시스템은 **의사결정 지원 도구**입니다
2. 최종 투자 결정은 **본인의 판단과 책임**입니다
3. 과거 데이터가 미래를 보장하지 않습니다
4. 충분한 검증 후 소액부터 시작하세요
5. 분산투자를 권장합니다

---

## 체크리스트

설치 및 설정이 완료되었는지 확인하세요:

- [ ] Python 3.8 이상 설치
- [ ] 프로젝트 다운로드
- [ ] 가상환경 생성 및 활성화
- [ ] 라이브러리 설치 (`pip install -r requirements.txt`)
- [ ] TA-Lib 설치 (선택)
- [ ] 투자 프로필 설정
- [ ] 첫 종목 분석 완료
- [ ] 체크리스트 저장 확인

모두 체크되었다면 축하합니다! 🎉

이제 체계적인 투자 의사결정을 시작할 수 있습니다.

---

**"작은 시작이 큰 변화를 만듭니다. 행운을 빕니다!"** 🚀
