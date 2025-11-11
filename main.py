#!/usr/bin/env python3
"""
개인화된 투자 의사 결정 시스템
Personal Investment Decision System
"""

import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta

# 로그 디렉토리 생성 (로깅 설정 전에 실행)
Path("logs").mkdir(exist_ok=True)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def print_banner():
    """프로그램 배너 출력"""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║       개인화된 투자 의사 결정 시스템                       ║
    ║   Personal Investment Decision System (PIDS)             ║
    ║                                                           ║
    ║   당신의 투자 철학을 시스템화하다                          ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_menu():
    """메인 메뉴 출력"""
    menu = """
    ═══════════════ 메인 메뉴 ═══════════════

    1. 종목 분석 (단일 종목)
    2. 종목 스크리닝 (조건 검색)
    3. 관심 종목 관리
    4. 포트폴리오 분석
    5. 백테스팅
    6. 설정 관리
    0. 종료

    ═══════════════════════════════════════
    """
    print(menu)


def analyze_single_stock():
    """단일 종목 분석"""
    from src.data import KoreaStockData, USStockData
    from src.analysis import TechnicalAnalyzer
    from src.decision import DecisionChecklist

    print("\n[ 종목 분석 ]")
    print("시장 선택: 1) 한국  2) 미국")
    market_choice = input("선택: ").strip()

    ticker = input("종목 코드 입력: ").strip().upper()

    if market_choice == '1':
        # 한국 주식
        data_fetcher = KoreaStockData()
        market = 'KR'

        print(f"\n{ticker} 데이터 수집 중...")

        # 기본 정보
        fundamental = data_fetcher.get_fundamental_data(ticker)
        if not fundamental:
            print("종목 데이터를 가져올 수 없습니다.")
            return

        # 주가 데이터 (최근 1년)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)

        ohlcv = data_fetcher.get_ohlcv(
            ticker,
            start_date.strftime("%Y%m%d"),
            end_date.strftime("%Y%m%d")
        )

        if ohlcv.empty:
            print("주가 데이터를 가져올 수 없습니다.")
            return

        # PBR 밴드
        pbr_band = data_fetcher.calculate_pbr_band(ticker)

        # 거래량 분석
        volume_analysis = data_fetcher.get_volume_analysis(ticker)

        # 종목 데이터 구성
        stock_data = {
            'ticker': ticker,
            'name': fundamental.get('티커', ticker),
            'PBR': fundamental.get('PBR'),
            'PER': fundamental.get('PER'),
            'market_cap': fundamental.get('market_cap'),
            'pbr_band': pbr_band,
            'volume_analysis': volume_analysis,
            **fundamental
        }

    elif market_choice == '2':
        # 미국 주식
        data_fetcher = USStockData()
        market = 'US'

        print(f"\n{ticker} 데이터 수집 중...")

        # 기본 정보
        stock_info = data_fetcher.get_stock_info(ticker)
        if not stock_info:
            print("종목 데이터를 가져올 수 없습니다.")
            return

        # 재무 데이터
        fundamental = data_fetcher.get_fundamental_data(ticker)

        # 주가 데이터
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)

        ohlcv = data_fetcher.get_ohlcv(
            ticker,
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d")
        )

        if ohlcv.empty:
            print("주가 데이터를 가져올 수 없습니다.")
            return

        # PBR 밴드
        pbr_band = data_fetcher.calculate_pbr_band(ticker)

        # 거래량 분석
        volume_analysis = data_fetcher.get_volume_analysis(ticker)

        # 종목 데이터 구성
        stock_data = {
            'ticker': ticker,
            'name': stock_info.get('name'),
            'sector': stock_info.get('sector'),
            'industry': stock_info.get('industry'),
            'pbr_band': pbr_band,
            'volume_analysis': volume_analysis,
            **fundamental
        }

    else:
        print("잘못된 선택입니다.")
        return

    # 기술적 분석
    print("\n기술적 분석 수행 중...")
    analyzer = TechnicalAnalyzer()
    ohlcv_with_indicators = analyzer.calculate_all_indicators(ohlcv)
    technical_signals = analyzer.generate_buy_signals(ohlcv_with_indicators)

    # 의사결정 체크리스트 생성
    print("\n체크리스트 생성 중...")
    checklist_manager = DecisionChecklist()
    checklist = checklist_manager.evaluate_stock(stock_data, technical_signals, market)

    # 결과 출력
    print("\n" + "="*60)
    print(checklist_manager.print_checklist(checklist))

    # 저장 여부
    save = input("\n체크리스트를 저장하시겠습니까? (y/n): ").strip().lower()
    if save == 'y':
        checklist_manager.save_checklist(checklist)
        print("저장 완료!")


def screen_stocks():
    """종목 스크리닝"""
    from src.screening import ValueScreener

    print("\n[ 종목 스크리닝 ]")
    print("현재 설정된 조건으로 종목을 검색합니다.")
    print("(설정 변경은 config/strategy_config.yaml 파일을 수정하세요)")

    print("\n시장 선택: 1) 한국  2) 미국")
    market_choice = input("선택: ").strip()

    screener = ValueScreener()

    if market_choice == '1':
        print("\n한국 시장 스크리닝은 시간이 걸릴 수 있습니다...")
        print("(구현 중 - 대량의 종목 데이터 수집이 필요합니다)")
        # 실제 구현 시에는 모든 종목을 순회하며 스크리닝
    elif market_choice == '2':
        print("\n미국 시장 스크리닝은 별도의 종목 리스트가 필요합니다...")
        print("(구현 중 - S&P 500 또는 관심 종목 리스트 필요)")
    else:
        print("잘못된 선택입니다.")


def manage_watchlist():
    """관심 종목 관리"""
    print("\n[ 관심 종목 관리 ]")
    print("1. 관심 종목 보기")
    print("2. 종목 추가")
    print("3. 종목 삭제")
    print("0. 뒤로")

    choice = input("\n선택: ").strip()

    watchlist_file = Path("data/watchlist.json")

    if choice == '1':
        if watchlist_file.exists():
            import json
            with open(watchlist_file, 'r') as f:
                watchlist = json.load(f)
            print("\n관심 종목:")
            for item in watchlist:
                print(f"  - {item['ticker']}: {item['name']}")
        else:
            print("관심 종목이 없습니다.")

    elif choice == '2':
        print("(구현 중)")

    elif choice == '3':
        print("(구현 중)")


def analyze_portfolio():
    """포트폴리오 분석"""
    print("\n[ 포트폴리오 분석 ]")
    print("(구현 중)")


def run_backtest():
    """백테스팅"""
    from src.backtesting import BacktestEngine

    print("\n[ 백테스팅 ]")
    print("과거 데이터로 투자 전략을 검증합니다.")
    print("(구현 중 - 실제 백테스트는 대량의 과거 데이터가 필요합니다)")

    # 예제 백테스트
    engine = BacktestEngine(initial_capital=100_000_000)
    print(f"\n초기 자본: {engine.initial_capital:,}원")
    print(f"수수료율: {engine.commission_rate*100}%")
    print(f"슬리피지: {engine.slippage*100}%")


def manage_settings():
    """설정 관리"""
    print("\n[ 설정 관리 ]")
    print("1. 투자 프로필 보기")
    print("2. 투자 전략 보기")
    print("3. 설정 편집")
    print("0. 뒤로")

    choice = input("\n선택: ").strip()

    if choice == '1':
        config_file = Path("config/investment_profile.yaml")
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                print("\n" + f.read())

    elif choice == '2':
        config_file = Path("config/strategy_config.yaml")
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                print("\n" + f.read())

    elif choice == '3':
        print("\n설정 파일 위치:")
        print("  - 투자 프로필: config/investment_profile.yaml")
        print("  - 투자 전략: config/strategy_config.yaml")
        print("\n텍스트 에디터로 직접 수정하세요.")


def main():
    """메인 함수"""
    print_banner()

    # 로그 디렉토리 생성
    Path("logs").mkdir(exist_ok=True)
    Path("data/checklists").mkdir(parents=True, exist_ok=True)

    while True:
        print_menu()
        choice = input("메뉴 선택: ").strip()

        if choice == '1':
            analyze_single_stock()
        elif choice == '2':
            screen_stocks()
        elif choice == '3':
            manage_watchlist()
        elif choice == '4':
            analyze_portfolio()
        elif choice == '5':
            run_backtest()
        elif choice == '6':
            manage_settings()
        elif choice == '0':
            print("\n프로그램을 종료합니다.")
            sys.exit(0)
        else:
            print("\n잘못된 선택입니다. 다시 선택해주세요.")

        input("\nEnter를 눌러 계속...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n프로그램을 종료합니다.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"오류 발생: {e}", exc_info=True)
        print(f"\n오류가 발생했습니다: {e}")
        sys.exit(1)
