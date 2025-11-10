"""
미국 주식 데이터 수집 모듈
yfinance를 사용하여 NYSE/NASDAQ 데이터 수집
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    logging.warning("yfinance가 설치되지 않았습니다. 설치: pip install yfinance")


class USStockData:
    """미국 주식 데이터 수집 클래스"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        if not YFINANCE_AVAILABLE:
            self.logger.warning("yfinance 모듈이 설치되지 않았습니다.")

    def get_stock_info(self, ticker: str) -> Dict:
        """
        종목 기본 정보 조회

        Args:
            ticker: 티커 심볼 (예: AAPL, MSFT)

        Returns:
            종목 정보 딕셔너리
        """
        if not YFINANCE_AVAILABLE:
            return {}

        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            return {
                'ticker': ticker,
                'name': info.get('longName', ''),
                'sector': info.get('sector', ''),
                'industry': info.get('industry', ''),
                'market_cap': info.get('marketCap', 0),
                'exchange': info.get('exchange', ''),
                'currency': info.get('currency', 'USD')
            }

        except Exception as e:
            self.logger.error(f"종목 정보 조회 실패 ({ticker}): {e}")
            return {}

    def get_ohlcv(self, ticker: str, start_date: str, end_date: str = None,
                   interval: str = '1d') -> pd.DataFrame:
        """
        주가 데이터(OHLCV) 조회

        Args:
            ticker: 티커 심볼
            start_date: 시작일 (YYYY-MM-DD)
            end_date: 종료일 (기본값: 오늘)
            interval: 데이터 간격 (1d, 1wk, 1mo 등)

        Returns:
            OHLCV DataFrame
        """
        if not YFINANCE_AVAILABLE:
            return pd.DataFrame()

        try:
            if end_date is None:
                end_date = datetime.now().strftime("%Y-%m-%d")

            stock = yf.Ticker(ticker)
            df = stock.history(start=start_date, end=end_date, interval=interval)

            if df.empty:
                self.logger.warning(f"데이터 없음: {ticker}")
                return pd.DataFrame()

            # 컬럼 정리
            df.index.name = 'Date'

            return df

        except Exception as e:
            self.logger.error(f"OHLCV 데이터 조회 실패 ({ticker}): {e}")
            return pd.DataFrame()

    def get_fundamental_data(self, ticker: str) -> Dict:
        """
        재무 데이터 조회 (PER, PBR, EPS 등)

        Args:
            ticker: 티커 심볼

        Returns:
            재무 데이터 딕셔너리
        """
        if not YFINANCE_AVAILABLE:
            return {}

        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            return {
                'ticker': ticker,
                # 밸류에이션
                'PE': info.get('trailingPE', None),
                'forward_PE': info.get('forwardPE', None),
                'PEG': info.get('pegRatio', None),
                'PB': info.get('priceToBook', None),
                'PS': info.get('priceToSalesTrailing12Months', None),

                # 수익성
                'profit_margin': info.get('profitMargins', None),
                'operating_margin': info.get('operatingMargins', None),
                'ROE': info.get('returnOnEquity', None),
                'ROA': info.get('returnOnAssets', None),

                # 재무 건전성
                'debt_to_equity': info.get('debtToEquity', None),
                'current_ratio': info.get('currentRatio', None),
                'quick_ratio': info.get('quickRatio', None),

                # EPS
                'EPS': info.get('trailingEps', None),
                'forward_EPS': info.get('forwardEps', None),

                # 성장률
                'earnings_growth': info.get('earningsGrowth', None),
                'revenue_growth': info.get('revenueGrowth', None),

                # 시가총액
                'market_cap': info.get('marketCap', None),

                # 배당
                'dividend_yield': info.get('dividendYield', None),
                'payout_ratio': info.get('payoutRatio', None),
            }

        except Exception as e:
            self.logger.error(f"재무 데이터 조회 실패 ({ticker}): {e}")
            return {}

    def get_financial_statements(self, ticker: str) -> Dict[str, pd.DataFrame]:
        """
        재무제표 조회 (손익계산서, 대차대조표, 현금흐름표)

        Args:
            ticker: 티커 심볼

        Returns:
            재무제표 딕셔너리 (income_stmt, balance_sheet, cash_flow)
        """
        if not YFINANCE_AVAILABLE:
            return {}

        try:
            stock = yf.Ticker(ticker)

            return {
                'income_statement': stock.financials,
                'balance_sheet': stock.balance_sheet,
                'cash_flow': stock.cashflow,
                'quarterly_income': stock.quarterly_financials,
                'quarterly_balance': stock.quarterly_balance_sheet,
                'quarterly_cashflow': stock.quarterly_cashflow,
            }

        except Exception as e:
            self.logger.error(f"재무제표 조회 실패 ({ticker}): {e}")
            return {}

    def calculate_pbr_band(self, ticker: str, period_years: int = 5) -> Dict:
        """
        PBR 밴드 계산

        Args:
            ticker: 티커 심볼
            period_years: 분석 기간 (년)

        Returns:
            PBR 밴드 정보
        """
        if not YFINANCE_AVAILABLE:
            return {}

        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_years*365)

            stock = yf.Ticker(ticker)

            # 과거 주가 데이터
            hist = stock.history(
                start=start_date.strftime("%Y-%m-%d"),
                end=end_date.strftime("%Y-%m-%d")
            )

            if hist.empty:
                return {}

            # BPS (Book Value Per Share) 가져오기
            info = stock.info
            book_value = info.get('bookValue', None)
            current_pb = info.get('priceToBook', None)

            if book_value is None or current_pb is None:
                return {}

            # 과거 PBR 계산 (주가 / BPS)
            pbr_series = hist['Close'] / book_value
            pbr_series = pbr_series[pbr_series > 0]  # 양수만

            if len(pbr_series) == 0:
                return {}

            return {
                'current_pbr': current_pb,
                'upper_band': pbr_series.quantile(0.8),
                'middle_band': pbr_series.quantile(0.5),
                'lower_band': pbr_series.quantile(0.2),
                'mean': pbr_series.mean(),
                'std': pbr_series.std(),
                'percentile': (pbr_series < current_pb).sum() / len(pbr_series) * 100
            }

        except Exception as e:
            self.logger.error(f"PBR 밴드 계산 실패 ({ticker}): {e}")
            return {}

    def get_volume_analysis(self, ticker: str, days: int = 60) -> Dict:
        """
        거래량 분석

        Args:
            ticker: 티커 심볼
            days: 분석 기간 (일)

        Returns:
            거래량 분석 결과
        """
        if not YFINANCE_AVAILABLE:
            return {}

        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            df = self.get_ohlcv(
                ticker,
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d")
            )

            if df.empty:
                return {}

            avg_volume = df['Volume'].mean()
            avg_value = (df['Close'] * df['Volume']).mean()

            return {
                'avg_daily_volume': avg_volume,
                'avg_daily_value': avg_value,
                'recent_volume': df['Volume'].iloc[-1] if len(df) > 0 else 0,
                'volume_trend': df['Volume'].iloc[-5:].mean() / avg_volume if avg_volume > 0 else 0,
                'has_sufficient_liquidity': avg_value > 1_000_000  # $1M 이상
            }

        except Exception as e:
            self.logger.error(f"거래량 분석 실패 ({ticker}): {e}")
            return {}

    def get_analyst_info(self, ticker: str) -> Dict:
        """
        애널리스트 의견 및 목표가 조회

        Args:
            ticker: 티커 심볼

        Returns:
            애널리스트 정보
        """
        if not YFINANCE_AVAILABLE:
            return {}

        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            return {
                'target_mean_price': info.get('targetMeanPrice', None),
                'target_high_price': info.get('targetHighPrice', None),
                'target_low_price': info.get('targetLowPrice', None),
                'recommendation': info.get('recommendationKey', None),
                'number_of_analysts': info.get('numberOfAnalystOpinions', None),
            }

        except Exception as e:
            self.logger.error(f"애널리스트 정보 조회 실패 ({ticker}): {e}")
            return {}

    def get_earnings_dates(self, ticker: str) -> pd.DataFrame:
        """
        실적 발표 일정 조회

        Args:
            ticker: 티커 심볼

        Returns:
            실적 발표 일정 DataFrame
        """
        if not YFINANCE_AVAILABLE:
            return pd.DataFrame()

        try:
            stock = yf.Ticker(ticker)
            return stock.earnings_dates

        except Exception as e:
            self.logger.error(f"실적 발표 일정 조회 실패 ({ticker}): {e}")
            return pd.DataFrame()

    def search_stocks(self, query: str) -> List[Dict]:
        """
        종목 검색 (제한적 - yfinance는 검색 기능이 없음)

        Args:
            query: 검색어

        Returns:
            검색 결과 리스트
        """
        # yfinance는 직접 검색 기능이 없으므로
        # 별도의 API나 스크래핑 필요
        self.logger.info("종목 검색은 외부 API 연동 필요")
        return []

    def get_company_officers(self, ticker: str) -> List[Dict]:
        """
        경영진 정보 조회

        Args:
            ticker: 티커 심볼

        Returns:
            경영진 정보 리스트
        """
        if not YFINANCE_AVAILABLE:
            return []

        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            officers = info.get('companyOfficers', [])
            return officers

        except Exception as e:
            self.logger.error(f"경영진 정보 조회 실패 ({ticker}): {e}")
            return []
