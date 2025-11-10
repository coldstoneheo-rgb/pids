"""
기술적 분석 모듈
차트 분석, 지지/저항선, 매매 시그널 생성
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging


class TechnicalAnalyzer:
    """기술적 분석 클래스"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def calculate_moving_averages(self, df: pd.DataFrame,
                                   periods: List[int] = [5, 20, 60, 120, 200]) -> pd.DataFrame:
        """
        이동평균선 계산

        Args:
            df: OHLCV DataFrame
            periods: 이동평균 기간 리스트

        Returns:
            이동평균이 추가된 DataFrame
        """
        result = df.copy()

        for period in periods:
            result[f'MA{period}'] = result['Close'].rolling(window=period).mean()

        return result

    def calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        RSI(Relative Strength Index) 계산

        Args:
            df: OHLCV DataFrame
            period: RSI 기간

        Returns:
            RSI가 추가된 DataFrame
        """
        result = df.copy()

        delta = result['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        result['RSI'] = 100 - (100 / (1 + rs))

        return result

    def calculate_macd(self, df: pd.DataFrame,
                       fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
        """
        MACD 계산

        Args:
            df: OHLCV DataFrame
            fast: 빠른 EMA 기간
            slow: 느린 EMA 기간
            signal: 시그널선 기간

        Returns:
            MACD가 추가된 DataFrame
        """
        result = df.copy()

        exp1 = result['Close'].ewm(span=fast, adjust=False).mean()
        exp2 = result['Close'].ewm(span=slow, adjust=False).mean()

        result['MACD'] = exp1 - exp2
        result['MACD_Signal'] = result['MACD'].ewm(span=signal, adjust=False).mean()
        result['MACD_Hist'] = result['MACD'] - result['MACD_Signal']

        return result

    def calculate_bollinger_bands(self, df: pd.DataFrame,
                                   period: int = 20, std_dev: int = 2) -> pd.DataFrame:
        """
        볼린저 밴드 계산

        Args:
            df: OHLCV DataFrame
            period: 기간
            std_dev: 표준편차 배수

        Returns:
            볼린저 밴드가 추가된 DataFrame
        """
        result = df.copy()

        result['BB_Middle'] = result['Close'].rolling(window=period).mean()
        std = result['Close'].rolling(window=period).std()

        result['BB_Upper'] = result['BB_Middle'] + (std * std_dev)
        result['BB_Lower'] = result['BB_Middle'] - (std * std_dev)

        return result

    def find_support_resistance(self, df: pd.DataFrame,
                                 window: int = 20) -> Dict[str, List[float]]:
        """
        지지선/저항선 찾기

        Args:
            df: OHLCV DataFrame
            window: 탐색 윈도우

        Returns:
            지지선/저항선 딕셔너리
        """
        highs = df['High'].values
        lows = df['Low'].values

        resistance_levels = []
        support_levels = []

        # 고점 찾기 (저항선)
        for i in range(window, len(highs) - window):
            if highs[i] == max(highs[i-window:i+window+1]):
                resistance_levels.append(highs[i])

        # 저점 찾기 (지지선)
        for i in range(window, len(lows) - window):
            if lows[i] == min(lows[i-window:i+window+1]):
                support_levels.append(lows[i])

        # 중복 제거 및 클러스터링
        resistance_levels = self._cluster_levels(resistance_levels)
        support_levels = self._cluster_levels(support_levels)

        return {
            'resistance': sorted(resistance_levels, reverse=True),
            'support': sorted(support_levels)
        }

    def _cluster_levels(self, levels: List[float], threshold: float = 0.02) -> List[float]:
        """
        가격 레벨 클러스터링 (유사한 가격대 통합)

        Args:
            levels: 가격 레벨 리스트
            threshold: 클러스터링 임계값 (2%)

        Returns:
            클러스터링된 레벨 리스트
        """
        if not levels:
            return []

        levels = sorted(levels)
        clustered = [levels[0]]

        for level in levels[1:]:
            if abs(level - clustered[-1]) / clustered[-1] > threshold:
                clustered.append(level)

        return clustered

    def detect_price_adjustment(self, df: pd.DataFrame,
                                 min_correction: float = 0.10) -> Dict:
        """
        가격 조정 여부 감지

        Args:
            df: OHLCV DataFrame
            min_correction: 최소 조정 비율 (10%)

        Returns:
            조정 정보 딕셔너리
        """
        if len(df) < 60:
            return {'adjusted': False, 'reason': '데이터 부족'}

        # 최근 고점 찾기
        recent_high = df['High'].iloc[-60:].max()
        current_price = df['Close'].iloc[-1]

        # 조정 비율 계산
        correction = (recent_high - current_price) / recent_high

        adjusted = correction >= min_correction

        return {
            'adjusted': adjusted,
            'correction_ratio': correction * 100,
            'recent_high': recent_high,
            'current_price': current_price,
            'from_high': correction * 100
        }

    def detect_consolidation(self, df: pd.DataFrame, period: int = 30,
                            volatility_threshold: float = 0.05) -> Dict:
        """
        횡보 구간(조정 기간) 감지

        Args:
            df: OHLCV DataFrame
            period: 분석 기간
            volatility_threshold: 변동성 임계값 (5%)

        Returns:
            횡보 정보 딕셔너리
        """
        if len(df) < period:
            return {'consolidating': False, 'reason': '데이터 부족'}

        recent = df.iloc[-period:]

        # 변동성 계산 (고가-저가 평균 / 종가 평균)
        volatility = ((recent['High'] - recent['Low']) / recent['Close']).mean()

        consolidating = volatility <= volatility_threshold

        # 가격 범위
        price_range = (recent['High'].max() - recent['Low'].min()) / recent['Close'].mean()

        return {
            'consolidating': consolidating,
            'volatility': volatility * 100,
            'price_range': price_range * 100,
            'days': period
        }

    def check_support_approach(self, df: pd.DataFrame, tolerance: float = 0.03) -> Dict:
        """
        지지선 접근 여부 체크 (전저점 하단)

        Args:
            df: OHLCV DataFrame
            tolerance: 허용 오차 (3%)

        Returns:
            지지선 접근 정보
        """
        support_resistance = self.find_support_resistance(df)
        support_levels = support_resistance.get('support', [])

        if not support_levels:
            return {'approaching_support': False, 'reason': '지지선 없음'}

        current_price = df['Close'].iloc[-1]

        # 가장 가까운 지지선 찾기
        closest_support = None
        min_distance = float('inf')

        for support in support_levels:
            if support < current_price:
                distance = (current_price - support) / support
                if distance < min_distance:
                    min_distance = distance
                    closest_support = support

        approaching = (closest_support is not None and min_distance <= tolerance)

        return {
            'approaching_support': approaching,
            'closest_support': closest_support,
            'current_price': current_price,
            'distance_pct': min_distance * 100 if closest_support else None
        }

    def generate_buy_signals(self, df: pd.DataFrame) -> Dict:
        """
        매수 신호 생성

        조건:
        1. 가격 조정 완료
        2. 횡보 구간 (기간 조정)
        3. 지지선 접근
        4. RSI 과매도 구간
        5. 이동평균선 지지

        Args:
            df: 기술적 지표가 포함된 DataFrame

        Returns:
            매수 신호 정보
        """
        signals = {}
        score = 0

        # 1. 가격 조정 체크
        adjustment = self.detect_price_adjustment(df)
        signals['price_adjusted'] = adjustment['adjusted']
        if adjustment['adjusted']:
            score += 20

        # 2. 횡보 구간 체크
        consolidation = self.detect_consolidation(df)
        signals['consolidating'] = consolidation['consolidating']
        if consolidation['consolidating']:
            score += 20

        # 3. 지지선 접근 체크
        support = self.check_support_approach(df)
        signals['near_support'] = support['approaching_support']
        if support['approaching_support']:
            score += 25

        # 4. RSI 체크
        if 'RSI' in df.columns:
            current_rsi = df['RSI'].iloc[-1]
            signals['rsi'] = current_rsi
            if current_rsi < 30:
                score += 20
            elif current_rsi < 40:
                score += 10

        # 5. 이동평균선 지지 체크
        if 'MA20' in df.columns:
            current_price = df['Close'].iloc[-1]
            ma20 = df['MA20'].iloc[-1]

            # 20일선 근처 (±3%)
            if abs(current_price - ma20) / ma20 <= 0.03:
                signals['near_ma20'] = True
                score += 15
            else:
                signals['near_ma20'] = False

        signals['buy_score'] = score
        signals['buy_signal'] = score >= 60  # 60점 이상이면 매수 신호

        return signals

    def generate_sell_signals(self, df: pd.DataFrame,
                             entry_price: float,
                             target_return: float = 100) -> Dict:
        """
        매도 신호 생성

        Args:
            df: 기술적 지표가 포함된 DataFrame
            entry_price: 진입 가격
            target_return: 목표 수익률 (%)

        Returns:
            매도 신호 정보
        """
        signals = {}
        current_price = df['Close'].iloc[-1]

        # 수익률 계산
        return_pct = ((current_price - entry_price) / entry_price) * 100
        signals['return_pct'] = return_pct

        # 목표 수익률 달성
        if return_pct >= target_return:
            signals['target_reached'] = True
            signals['sell_signal'] = True
            signals['reason'] = f'목표 수익률 {target_return}% 달성'
            return signals

        # 손절 체크 (-20%)
        if return_pct <= -20:
            signals['stop_loss'] = True
            signals['sell_signal'] = True
            signals['reason'] = '손절 기준 도달 (-20%)'
            return signals

        # 저항선 도달 체크
        support_resistance = self.find_support_resistance(df)
        resistance_levels = support_resistance.get('resistance', [])

        for resistance in resistance_levels:
            if abs(current_price - resistance) / resistance <= 0.02:
                signals['near_resistance'] = True
                if return_pct > 50:  # 50% 이상 수익이면 분할 매도 고려
                    signals['partial_sell_signal'] = True
                    signals['reason'] = '저항선 도달 + 수익 발생'
                break

        signals['sell_signal'] = signals.get('sell_signal', False)

        return signals

    def calculate_all_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        모든 기술적 지표 한번에 계산

        Args:
            df: OHLCV DataFrame

        Returns:
            모든 지표가 포함된 DataFrame
        """
        result = df.copy()

        # 이동평균
        result = self.calculate_moving_averages(result)

        # RSI
        result = self.calculate_rsi(result)

        # MACD
        result = self.calculate_macd(result)

        # 볼린저 밴드
        result = self.calculate_bollinger_bands(result)

        return result
