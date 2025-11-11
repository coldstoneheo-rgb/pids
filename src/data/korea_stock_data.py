"""
한국 주식 데이터 수집 모듈
pykrx와 FinanceDataReader를 사용하여 KOSPI/KOSDAQ 데이터 수집
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

try:
    from pykrx import stock
    import FinanceDataReader as fdr
    MODULES_AVAILABLE = True
except ImportError:
    MODULES_AVAILABLE = False
    logging.warning("pykrx 또는 FinanceDataReader가 설치되지 않았습니다. 설치: pip install pykrx FinanceDataReader")


class KoreaStockData:
    """한국 주식 데이터 수집 클래스"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        if not MODULES_AVAILABLE:
            self.logger.warning("필수 모듈이 설치되지 않았습니다.")
        self._ticker_cache = {}  # 종목명-코드 캐시

    def get_stock_list(self, market: str = "ALL") -> pd.DataFrame:
        """
        주식 종목 리스트 조회

        Args:
            market: "KOSPI", "KOSDAQ", "ALL"

        Returns:
            종목 리스트 DataFrame
        """
        if not MODULES_AVAILABLE:
            return pd.DataFrame()

        try:
            today = datetime.now().strftime("%Y%m%d")

            if market == "ALL":
                kospi = stock.get_market_ticker_list(today, market="KOSPI")
                kosdaq = stock.get_market_ticker_list(today, market="KOSDAQ")
                tickers = kospi + kosdaq
            else:
                tickers = stock.get_market_ticker_list(today, market=market)

            # 종목 정보 수집
            stock_list = []
            for ticker in tickers:
                try:
                    name = stock.get_market_ticker_name(ticker)
                    stock_list.append({
                        'ticker': ticker,
                        'name': name,
                        'market': self._get_market_type(ticker)
                    })
                except Exception as e:
                    self.logger.debug(f"종목 {ticker} 정보 수집 실패: {e}")
                    continue

            return pd.DataFrame(stock_list)

        except Exception as e:
            self.logger.error(f"주식 리스트 조회 실패: {e}")
            return pd.DataFrame()

    def get_ticker_by_name(self, stock_name: str) -> Optional[str]:
        """
        종목명으로 종목 코드 검색

        Args:
            stock_name: 종목명 (예: "삼성전자", "SK텔레콤")

        Returns:
            종목 코드 또는 None
        """
        if not MODULES_AVAILABLE:
            return None

        try:
            # 캐시 확인
            if stock_name in self._ticker_cache:
                return self._ticker_cache[stock_name]

            today = datetime.now().strftime("%Y%m%d")

            # KOSPI + KOSDAQ 전체 종목 검색
            for market in ["KOSPI", "KOSDAQ"]:
                try:
                    tickers = stock.get_market_ticker_list(today, market=market)

                    for ticker in tickers:
                        try:
                            name = stock.get_market_ticker_name(ticker)
                            # 캐시에 저장
                            self._ticker_cache[name] = ticker

                            # 정확히 일치하는 경우
                            if name == stock_name:
                                return ticker
                        except:
                            continue

                except Exception as e:
                    self.logger.debug(f"{market} 검색 중 오류: {e}")
                    continue

            # 부분 일치 검색 (정확한 일치가 없는 경우)
            for name, ticker in self._ticker_cache.items():
                if stock_name in name or name in stock_name:
                    self.logger.info(f"부분 일치 발견: '{stock_name}' -> '{name}' ({ticker})")
                    return ticker

            return None

        except Exception as e:
            self.logger.error(f"종목 코드 검색 실패 ({stock_name}): {e}")
            return None

    def _get_market_type(self, ticker: str) -> str:
        """종목 코드로 시장 구분"""
        try:
            ohlcv = stock.get_market_ohlcv_by_date(
                (datetime.now() - timedelta(days=7)).strftime("%Y%m%d"),
                datetime.now().strftime("%Y%m%d"),
                ticker
            )
            return "KOSDAQ" if len(ticker) == 6 and ticker.startswith("A") else "KOSPI"
        except:
            return "UNKNOWN"

    def get_ohlcv(self, ticker: str, start_date: str, end_date: str = None) -> pd.DataFrame:
        """
        주가 데이터(OHLCV) 조회

        Args:
            ticker: 종목 코드
            start_date: 시작일 (YYYYMMDD 또는 YYYY-MM-DD)
            end_date: 종료일 (기본값: 오늘)

        Returns:
            OHLCV DataFrame
        """
        if not MODULES_AVAILABLE:
            return pd.DataFrame()

        try:
            if end_date is None:
                end_date = datetime.now().strftime("%Y%m%d")

            # 날짜 포맷 통일
            start_date = start_date.replace("-", "")
            end_date = end_date.replace("-", "")

            df = stock.get_market_ohlcv_by_date(start_date, end_date, ticker)
            df.index.name = 'Date'

            # 컬럼명 영문으로 변경
            df.columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'Change']

            return df

        except Exception as e:
            self.logger.error(f"OHLCV 데이터 조회 실패 ({ticker}): {e}")
            return pd.DataFrame()

    def get_fundamental_data(self, ticker: str, date: str = None) -> Dict:
        """
        재무 데이터 조회 (PER, PBR, EPS, BPS 등)

        Args:
            ticker: 종목 코드
            date: 조회일 (YYYYMMDD, 기본값: 오늘)

        Returns:
            재무 데이터 딕셔너리
        """
        if not MODULES_AVAILABLE:
            return {}

        try:
            if date is None:
                date = datetime.now().strftime("%Y%m%d")
            else:
                date = date.replace("-", "")

            # 기본 시장 데이터
            fundamental = stock.get_market_fundamental(date, date, ticker)

            if fundamental.empty:
                return {}

            data = fundamental.iloc[0].to_dict()

            # 추가 정보
            try:
                cap = stock.get_market_cap_by_date(date, date, ticker)
                if not cap.empty:
                    data['market_cap'] = cap.iloc[0]['시가총액']
                    data['outstanding_shares'] = cap.iloc[0]['상장주식수']
            except:
                pass

            return data

        except Exception as e:
            self.logger.error(f"재무 데이터 조회 실패 ({ticker}): {e}")
            return {}

    def get_financial_statement(self, ticker: str, year: int = None) -> Dict:
        """
        재무제표 조회

        Args:
            ticker: 종목 코드
            year: 회계연도 (기본값: 최근 연도)

        Returns:
            재무제표 딕셔너리
        """
        # 이 기능은 pykrx에서 직접 지원하지 않으므로
        # 추후 다른 API(Open DART 등) 연동 필요
        self.logger.info("재무제표 조회는 추후 Open DART API 연동 예정")
        return {}

    def calculate_pbr_band(self, ticker: str, period_years: int = 5) -> Dict:
        """
        PBR 밴드 계산

        Args:
            ticker: 종목 코드
            period_years: 분석 기간 (년)

        Returns:
            PBR 밴드 정보 (현재값, 상단, 중간, 하단)
        """
        if not MODULES_AVAILABLE:
            return {}

        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_years*365)

            # 기간 동안의 PBR 데이터 수집
            pbr_data = []
            current_date = start_date

            while current_date <= end_date:
                date_str = current_date.strftime("%Y%m%d")
                try:
                    fundamental = stock.get_market_fundamental(date_str, date_str, ticker)
                    if not fundamental.empty and 'PBR' in fundamental.columns:
                        pbr = fundamental.iloc[0]['PBR']
                        if pbr > 0:  # 유효한 PBR만
                            pbr_data.append(pbr)
                except:
                    pass

                current_date += timedelta(days=30)  # 월 단위 샘플링

            if not pbr_data:
                return {}

            pbr_array = np.array(pbr_data)

            return {
                'current_pbr': pbr_data[-1] if pbr_data else None,
                'upper_band': np.percentile(pbr_array, 80),
                'middle_band': np.percentile(pbr_array, 50),
                'lower_band': np.percentile(pbr_array, 20),
                'mean': np.mean(pbr_array),
                'std': np.std(pbr_array),
                'percentile': self._get_percentile(pbr_data[-1], pbr_array) if pbr_data else None
            }

        except Exception as e:
            self.logger.error(f"PBR 밴드 계산 실패 ({ticker}): {e}")
            return {}

    def _get_percentile(self, value: float, array: np.ndarray) -> float:
        """값이 배열에서 몇 퍼센타일인지 계산"""
        return (np.sum(array < value) / len(array)) * 100

    def get_volume_analysis(self, ticker: str, days: int = 60) -> Dict:
        """
        거래량 분석

        Args:
            ticker: 종목 코드
            days: 분석 기간 (일)

        Returns:
            거래량 분석 결과
        """
        if not MODULES_AVAILABLE:
            return {}

        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            df = self.get_ohlcv(
                ticker,
                start_date.strftime("%Y%m%d"),
                end_date.strftime("%Y%m%d")
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
                'has_sufficient_liquidity': avg_value > 1_000_000_000  # 10억원 이상
            }

        except Exception as e:
            self.logger.error(f"거래량 분석 실패 ({ticker}): {e}")
            return {}

    def get_sector_industry(self, ticker: str) -> Dict:
        """
        업종 정보 조회

        Args:
            ticker: 종목 코드

        Returns:
            업종 정보
        """
        # pykrx에서는 업종 정보가 제한적이므로
        # FinanceDataReader 또는 크롤링 필요
        try:
            df_krx = fdr.StockListing('KRX')
            stock_info = df_krx[df_krx['Code'] == ticker]

            if not stock_info.empty:
                return {
                    'sector': stock_info.iloc[0].get('Sector', ''),
                    'industry': stock_info.iloc[0].get('Industry', ''),
                }
        except:
            pass

        return {'sector': '', 'industry': ''}
