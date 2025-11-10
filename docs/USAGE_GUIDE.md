# 사용 가이드

## 개인화된 투자 의사 결정 시스템 (PIDS) 상세 가이드

이 문서는 시스템을 효과적으로 사용하는 방법을 단계별로 설명합니다.

---

## 목차

1. [설치 후 초기 설정](#설치-후-초기-설정)
2. [투자 전략 커스터마이징](#투자-전략-커스터마이징)
3. [종목 분석 워크플로우](#종목-분석-워크플로우)
4. [의사결정 체크리스트 활용](#의사결정-체크리스트-활용)
5. [백테스팅 수행](#백테스팅-수행)
6. [고급 사용법](#고급-사용법)

---

## 설치 후 초기 설정

### 1단계: 환경 확인

```bash
python --version  # Python 3.8 이상 확인
pip list | grep yfinance  # 패키지 설치 확인
```

### 2단계: 투자 프로필 작성

`config/investment_profile.yaml` 파일을 열어 자신의 투자 성향을 입력하세요.

```yaml
investor_profile:
  name: "홍길동의 투자 프로필"
  risk_tolerance: "moderate_aggressive"  # 자신의 위험 감수 성향
  investment_horizon: "medium_to_long"   # 투자 기간

investment_style:
  primary_styles:
    - "value_investing"      # 가치투자
    - "growth_investing"     # 성장투자

preferred_sectors:
  - "Technology"             # 관심 섹터 추가
  - "Semiconductors"
```

### 3단계: 투자 전략 설정

`config/strategy_config.yaml` 파일에서 스크리닝 기준을 수정하세요.

예시: PER 기준을 더 엄격하게 변경
```yaml
screening_criteria:
  per:
    enabled: true
    min_value: 8    # 기존 10에서 8로 변경
    max_value: 12   # 기존 15에서 12로 변경
```

---

## 투자 전략 커스터마이징

### 나만의 투자 기준 설정하기

#### 1. 밸류에이션 기준

```yaml
screening_criteria:
  pbr:
    max_value: 0.8        # PBR 0.8 이하만 선택
    band_percentile: 10   # 하위 10% 이하만

  per:
    min_value: 5
    max_value: 10
```

#### 2. 거래량 기준

유동성이 중요한 경우:

```yaml
volume:
  min_avg_daily_volume: 500000          # 50만주 이상
  min_avg_daily_value_krw: 5000000000  # 50억원 이상
```

#### 3. 매수/매도 전략

```yaml
technical_analysis:
  buy_signals:
    rsi_oversold: 25              # RSI 25 이하에서만 매수

  sell_signals:
    target_return_min: 150        # 최소 150% 수익 목표
    stop_loss:
      percentage: -15             # 손절 -15%
```

---

## 종목 분석 워크플로우

### 완전한 종목 분석 프로세스

#### Step 1: 프로그램 실행

```bash
python main.py
```

#### Step 2: 종목 분석 선택

```
메뉴 선택: 1
```

#### Step 3: 시장 및 종목 코드 입력

```
시장 선택: 1) 한국  2) 미국
선택: 1

종목 코드 입력: 005930
```

#### Step 4: 분석 결과 해석

시스템이 제공하는 체크리스트:

```
============================================================
투자 의사결정 체크리스트
============================================================
종목: 삼성전자 (005930)
최종 결정: 매수 고려
종합 점수: 65/100

[ 정량적 지표 ]
  ✓ PBR: 0.85 (목표: ≤ 1.0, 밴드 하단)      → 통과
  ✓ PER: 12.5 (목표: 10~15배)              → 통과
  ✗ 거래량: 부족                            → 미달

[ 기술적 분석 ]
  ✓ 가격 조정 완료                          → 통과
  ✗ 횡보 구간                               → 미달
  ✓ 지지선 접근                             → 통과
  RSI: 35 (과매도)                         → 양호
```

#### Step 5: 의사결정

점수 기준:
- **80점 이상**: 매수 적극 추천
- **60-79점**: 매수 고려 (추가 확인 필요)
- **40-59점**: 관심 종목 등록
- **40점 미만**: 투자 제외

---

## 의사결정 체크리스트 활용

### 체크리스트 항목별 설명

#### 1. 정량적 지표

| 항목 | 목표 | 의미 |
|------|------|------|
| PBR | ≤ 1.0 | 장부가치 대비 저평가 |
| PER | 10-15배 | 적정 수익 배수 |
| 거래량 | 충분한 유동성 | 매매 가능성 |
| 시가총액 | 중소형주 | 성장 잠재력 |
| ROE | ≥ 5% | 자본 효율성 |
| 부채비율 | ≤ 200% | 재무 건전성 |

#### 2. 정성적 분석

직접 조사해야 할 항목:
- 업계 내 경쟁 지위
- 기술적 해자 (진입 장벽)
- 비즈니스 모델의 지속 가능성
- 경영진 평판

#### 3. 기술적 분석

시스템이 자동으로 확인:
- 가격 조정 (10% 이상 조정 완료)
- 횡보 구간 (변동성 5% 이하)
- 지지선 접근 (±3% 이내)
- RSI 지표

### 체크리스트 저장 및 관리

분석 후 체크리스트를 저장하면:

```
data/checklists/005930_20241110_checklist.json
```

나중에 다시 확인하거나 비교 분석에 활용할 수 있습니다.

---

## 백테스팅 수행

### 전략 백테스트

자신의 전략이 과거에 어떤 성과를 냈는지 확인합니다.

#### 1. 백테스팅 설정

`config/strategy_config.yaml`에서:

```yaml
backtesting:
  start_date: "2020-01-01"
  initial_capital_krw: 100000000    # 1억원
  commission_rate: 0.003             # 수수료 0.3%
```

#### 2. 백테스트 실행

```
메뉴 선택: 5
```

#### 3. 결과 해석

```
백테스트 결과 리포트
============================================================
[ 수익률 ]
  초기 자본: 100,000,000원
  최종 자산: 185,000,000원
  총 수익률: 85.0%
  연간 수익률: 16.2%

[ 리스크 ]
  변동성 (연): 24.5%
  샤프 비율: 0.66
  최대 낙폭: -28.3%

[ 거래 통계 ]
  총 거래 횟수: 45
  승률: 62.5%
  평균 수익률: 18.7%
```

#### 해석 가이드:

- **샤프 비율 > 1.0**: 우수한 전략
- **샤프 비율 0.5-1.0**: 양호한 전략
- **샤프 비율 < 0.5**: 개선 필요

- **최대 낙폭 (MDD)**: 견딜 수 있는 수준인지 확인
  - -20% 이내: 낮은 리스크
  - -20% ~ -40%: 중간 리스크
  - -40% 이상: 높은 리스크

---

## 고급 사용법

### 1. Python 스크립트로 직접 사용

```python
from src.data import USStockData
from src.analysis import TechnicalAnalyzer
from src.screening import ValueScreener

# 데이터 수집
data = USStockData()
stock_info = data.get_stock_info("AAPL")
ohlcv = data.get_ohlcv("AAPL", "2023-01-01", "2024-01-01")

# 기술적 분석
analyzer = TechnicalAnalyzer()
ohlcv_with_indicators = analyzer.calculate_all_indicators(ohlcv)
signals = analyzer.generate_buy_signals(ohlcv_with_indicators)

print(signals)
```

### 2. 배치 스크리닝

여러 종목을 한번에 분석:

```python
from src.screening import ValueScreener

screener = ValueScreener()

# 관심 종목 리스트
tickers = ["AAPL", "MSFT", "GOOGL", "AMZN"]

results = []
for ticker in tickers:
    # 데이터 수집 및 스크리닝
    stock_data = collect_stock_data(ticker)
    result = screener.screen_stock(stock_data, market='US')
    results.append(result)

# 통과한 종목만 필터링
passed = [r for r in results if r['passed']]
```

### 3. 자동화 스크립트

cron이나 Task Scheduler로 매일 자동 실행:

```bash
# daily_screening.sh
python -c "
from src.screening import ValueScreener
# 스크리닝 로직
# 결과를 이메일이나 슬랙으로 전송
"
```

---

## 추천 워크플로우

### 일일 루틴

1. **아침**: 관심 종목 업데이트 확인
2. **장중**: 매수/매도 신호 모니터링
3. **장 마감 후**: 당일 체크리스트 작성
4. **주말**: 주간 포트폴리오 리뷰 및 전략 조정

### 주간 루틴

1. 새로운 종목 스크리닝
2. 관심 종목 재평가
3. 포트폴리오 리밸런싱 검토
4. 투자 일지 작성

### 월간 루틴

1. 월간 수익률 분석
2. 전략 백테스팅
3. 설정 파일 업데이트
4. 새로운 섹터 연구

---

## 문제 해결

### 자주 발생하는 오류

#### 1. 데이터 수집 실패

```
오류: 종목 데이터를 가져올 수 없습니다.
```

해결:
- 인터넷 연결 확인
- 종목 코드 확인
- API 제한 대기 (1분 후 재시도)

#### 2. 모듈 import 오류

```
ModuleNotFoundError: No module named 'pykrx'
```

해결:
```bash
pip install -r requirements.txt
```

#### 3. TA-Lib 설치 오류

시스템별로 TA-Lib 설치가 복잡할 수 있습니다.
설치 가이드: https://github.com/mrjbq7/ta-lib

---

## 팁과 트릭

### 1. 효율적인 종목 발굴

- 섹터별로 정리하여 순환 투자
- PBR/PER이 급격히 하락한 종목 모니터링
- 지표 이상 알림 설정

### 2. 리스크 관리

- 단일 종목 15% 이상 집중 금지
- 섹터 분산 (최소 3개 이상)
- 정기적인 손절 점검

### 3. 성과 향상

- 투자 일지 작성 (성공/실패 원인 분석)
- 백테스팅으로 전략 검증
- 시장 사이클에 맞게 전략 조정

---

## 참고 자료

- [Benjamin Graham - The Intelligent Investor](https://www.amazon.com/Intelligent-Investor-Definitive-Investing-Essentials/dp/0060555661)
- [Peter Lynch - One Up On Wall Street](https://www.amazon.com/One-Up-Wall-Street-Already/dp/0743200403)
- [한국 주식 투자 가이드](https://www.krx.co.kr)
- [야후 파이낸스](https://finance.yahoo.com)

---

질문이나 문제가 있다면 GitHub Issues에 등록해주세요!
