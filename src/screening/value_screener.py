"""
가치 투자 스크리닝 모듈
PBR, PER, 거래량 등 정량적 지표 기반 종목 필터링
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging
import yaml
from pathlib import Path


class ValueScreener:
    """가치 투자 기반 종목 스크리너"""

    def __init__(self, config_path: str = None):
        """
        Args:
            config_path: 전략 설정 파일 경로
        """
        self.logger = logging.getLogger(__name__)

        # 설정 파일 로드
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "strategy_config.yaml"

        self.config = self._load_config(config_path)
        self.screening_criteria = self.config.get('screening_criteria', {})

    def _load_config(self, config_path: Path) -> Dict:
        """설정 파일 로드"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"설정 파일 로드 실패: {e}")
            return {}

    def screen_by_pbr(self, stock_data: Dict) -> bool:
        """
        PBR 기준 스크리닝

        Args:
            stock_data: 종목 데이터 딕셔너리

        Returns:
            통과 여부
        """
        pbr_config = self.screening_criteria.get('pbr', {})

        if not pbr_config.get('enabled', True):
            return True

        pbr = stock_data.get('PBR') or stock_data.get('PB')

        if pbr is None or pbr <= 0:
            return False

        # 최대값 체크
        max_pbr = pbr_config.get('max_value', 1.0)
        if pbr > max_pbr:
            return False

        # PBR 밴드 하단 선호
        if pbr_config.get('prefer_lower_band', False):
            pbr_band = stock_data.get('pbr_band', {})
            percentile = pbr_band.get('percentile')

            if percentile is not None:
                band_percentile = pbr_config.get('band_percentile', 20)
                if percentile > band_percentile:
                    return False

        return True

    def screen_by_per(self, stock_data: Dict) -> bool:
        """
        PER 기준 스크리닝

        Args:
            stock_data: 종목 데이터 딕셔너리

        Returns:
            통과 여부
        """
        per_config = self.screening_criteria.get('per', {})

        if not per_config.get('enabled', True):
            return True

        per = stock_data.get('PER') or stock_data.get('PE')

        if per is None or per <= 0:
            return False

        min_per = per_config.get('min_value', 10)
        max_per = per_config.get('max_value', 15)

        if per < min_per or per > max_per:
            return False

        return True

    def screen_by_volume(self, stock_data: Dict, market: str = 'KR') -> bool:
        """
        거래량 기준 스크리닝

        Args:
            stock_data: 종목 데이터 딕셔너리
            market: 시장 구분 ('KR' 또는 'US')

        Returns:
            통과 여부
        """
        volume_config = self.screening_criteria.get('volume', {})

        if not volume_config.get('enabled', True):
            return True

        volume_analysis = stock_data.get('volume_analysis', {})

        # 최소 거래량 체크
        min_volume = volume_config.get('min_avg_daily_volume', 100000)
        avg_volume = volume_analysis.get('avg_daily_volume', 0)

        if avg_volume < min_volume:
            return False

        # 최소 거래대금 체크
        avg_value = volume_analysis.get('avg_daily_value', 0)

        if market == 'KR':
            min_value = volume_config.get('min_avg_daily_value_krw', 1_000_000_000)
        else:
            min_value = volume_config.get('min_avg_daily_value_usd', 1_000_000)

        if avg_value < min_value:
            return False

        # 유동성 체크
        if volume_config.get('liquidity_check', True):
            if not volume_analysis.get('has_sufficient_liquidity', False):
                return False

        return True

    def screen_by_market_cap(self, stock_data: Dict, market: str = 'KR') -> bool:
        """
        시가총액 기준 스크리닝

        Args:
            stock_data: 종목 데이터 딕셔너리
            market: 시장 구분

        Returns:
            통과 여부
        """
        cap_config = self.screening_criteria.get('market_cap', {})

        market_cap = stock_data.get('market_cap', 0)

        if market_cap <= 0:
            return False

        # 최소 시가총액 체크
        if market == 'KR':
            min_cap = cap_config.get('min_market_cap_krw', 10_000_000_000)
        else:
            min_cap = cap_config.get('min_market_cap_usd', 10_000_000)

        if market_cap < min_cap:
            return False

        return True

    def screen_by_financial_health(self, stock_data: Dict) -> bool:
        """
        재무 건전성 스크리닝

        Args:
            stock_data: 종목 데이터 딕셔너리

        Returns:
            통과 여부
        """
        financial_config = self.screening_criteria.get('financial_health', {})

        # ROE 체크
        min_roe = financial_config.get('min_roe', 5.0)
        roe = stock_data.get('ROE', 0)

        if roe and roe < min_roe:
            return False

        # 부채비율 체크
        max_debt_ratio = financial_config.get('max_debt_ratio', 200)
        debt_ratio = stock_data.get('debt_to_equity')

        if debt_ratio and debt_ratio > max_debt_ratio:
            return False

        # 영업이익 흑자 체크
        if financial_config.get('positive_operating_profit', True):
            operating_margin = stock_data.get('operating_margin')
            if operating_margin is not None and operating_margin < 0:
                return False

        return True

    def screen_stock(self, stock_data: Dict, market: str = 'KR') -> Dict:
        """
        종목 스크리닝 (모든 기준 적용)

        Args:
            stock_data: 종목 데이터 딕셔너리
            market: 시장 구분

        Returns:
            스크리닝 결과 (통과 여부 및 상세)
        """
        results = {
            'ticker': stock_data.get('ticker'),
            'name': stock_data.get('name'),
            'passed': True,
            'reasons': [],
            'scores': {}
        }

        # PBR 체크
        if not self.screen_by_pbr(stock_data):
            results['passed'] = False
            results['reasons'].append('PBR 기준 미달')
        else:
            results['scores']['pbr'] = 'PASS'

        # PER 체크
        if not self.screen_by_per(stock_data):
            results['passed'] = False
            results['reasons'].append('PER 기준 미달')
        else:
            results['scores']['per'] = 'PASS'

        # 거래량 체크
        if not self.screen_by_volume(stock_data, market):
            results['passed'] = False
            results['reasons'].append('거래량 기준 미달')
        else:
            results['scores']['volume'] = 'PASS'

        # 시가총액 체크
        if not self.screen_by_market_cap(stock_data, market):
            results['passed'] = False
            results['reasons'].append('시가총액 기준 미달')
        else:
            results['scores']['market_cap'] = 'PASS'

        # 재무 건전성 체크
        if not self.screen_by_financial_health(stock_data):
            results['passed'] = False
            results['reasons'].append('재무 건전성 기준 미달')
        else:
            results['scores']['financial_health'] = 'PASS'

        return results

    def screen_multiple_stocks(self, stocks_data: List[Dict], market: str = 'KR') -> pd.DataFrame:
        """
        여러 종목 동시 스크리닝

        Args:
            stocks_data: 종목 데이터 리스트
            market: 시장 구분

        Returns:
            스크리닝 결과 DataFrame
        """
        results = []

        for stock_data in stocks_data:
            result = self.screen_stock(stock_data, market)
            results.append(result)

        df = pd.DataFrame(results)

        # 통과한 종목만 필터링
        if not df.empty:
            passed_df = df[df['passed'] == True].copy()
            return passed_df
        else:
            return pd.DataFrame()

    def rank_stocks(self, stocks_data: List[Dict], market: str = 'KR') -> pd.DataFrame:
        """
        종목 순위 매기기 (스코어링)

        Args:
            stocks_data: 종목 데이터 리스트
            market: 시장 구분

        Returns:
            순위가 매겨진 DataFrame
        """
        scored_stocks = []

        for stock_data in stocks_data:
            score = 0
            details = {}

            # PBR 점수 (낮을수록 좋음)
            pbr = stock_data.get('PBR') or stock_data.get('PB')
            if pbr and pbr > 0:
                pbr_score = max(0, 100 - pbr * 50)  # PBR 2.0이면 0점
                score += pbr_score
                details['pbr_score'] = pbr_score

            # PER 점수 (10-15 범위 내에서 중간값에 가까울수록 좋음)
            per = stock_data.get('PER') or stock_data.get('PE')
            if per and 10 <= per <= 15:
                per_score = 100 - abs(per - 12.5) * 8
                score += per_score
                details['per_score'] = per_score

            # 거래량 점수
            volume_analysis = stock_data.get('volume_analysis', {})
            if volume_analysis.get('has_sufficient_liquidity', False):
                score += 100
                details['volume_score'] = 100

            # ROE 점수
            roe = stock_data.get('ROE')
            if roe and roe > 0:
                roe_score = min(100, roe * 5)
                score += roe_score
                details['roe_score'] = roe_score

            scored_stocks.append({
                'ticker': stock_data.get('ticker'),
                'name': stock_data.get('name'),
                'total_score': score,
                **details,
                **stock_data
            })

        df = pd.DataFrame(scored_stocks)

        if not df.empty:
            df = df.sort_values('total_score', ascending=False)

        return df
