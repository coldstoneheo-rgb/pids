"""
백테스팅 엔진
과거 데이터로 투자 전략 검증
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import logging


class BacktestEngine:
    """백테스팅 엔진"""

    def __init__(self, initial_capital: float = 100_000_000,
                 commission_rate: float = 0.003,
                 slippage: float = 0.001):
        """
        Args:
            initial_capital: 초기 자본
            commission_rate: 수수료율 (0.3%)
            slippage: 슬리피지 (0.1%)
        """
        self.initial_capital = initial_capital
        self.commission_rate = commission_rate
        self.slippage = slippage
        self.logger = logging.getLogger(__name__)

    def run_simple_backtest(self, df: pd.DataFrame,
                           buy_signals: pd.Series,
                           sell_signals: pd.Series,
                           position_size: float = 1.0) -> Dict:
        """
        단순 백테스트 실행 (단일 종목)

        Args:
            df: OHLCV DataFrame
            buy_signals: 매수 신호 (True/False)
            sell_signals: 매도 신호 (True/False)
            position_size: 포지션 크기 (1.0 = 100%)

        Returns:
            백테스트 결과
        """
        capital = self.initial_capital
        position = 0  # 보유 주식 수
        entry_price = 0
        trades = []
        equity_curve = []

        for i in range(len(df)):
            date = df.index[i]
            price = df['Close'].iloc[i]

            # 현재 자산
            current_equity = capital + (position * price)
            equity_curve.append({
                'date': date,
                'equity': current_equity,
                'cash': capital,
                'position_value': position * price
            })

            # 매수 신호
            if buy_signals.iloc[i] and position == 0:
                # 매수 가능 금액
                buy_amount = capital * position_size

                # 슬리피지 적용
                buy_price = price * (1 + self.slippage)

                # 수수료 포함 매수
                shares = buy_amount / (buy_price * (1 + self.commission_rate))
                cost = shares * buy_price * (1 + self.commission_rate)

                if cost <= capital:
                    position = shares
                    entry_price = buy_price
                    capital -= cost

                    trades.append({
                        'date': date,
                        'type': 'BUY',
                        'price': buy_price,
                        'shares': shares,
                        'cost': cost,
                        'commission': cost * self.commission_rate
                    })

            # 매도 신호
            elif sell_signals.iloc[i] and position > 0:
                # 슬리피지 적용
                sell_price = price * (1 - self.slippage)

                # 수수료 차감 매도
                proceeds = position * sell_price * (1 - self.commission_rate)
                capital += proceeds

                # 수익률 계산
                profit_pct = ((sell_price - entry_price) / entry_price) * 100

                trades.append({
                    'date': date,
                    'type': 'SELL',
                    'price': sell_price,
                    'shares': position,
                    'proceeds': proceeds,
                    'commission': proceeds * self.commission_rate,
                    'profit_pct': profit_pct
                })

                position = 0
                entry_price = 0

        # 결과 계산
        equity_df = pd.DataFrame(equity_curve)
        trades_df = pd.DataFrame(trades)

        return self._calculate_performance(equity_df, trades_df)

    def run_strategy_backtest(self, historical_data: Dict[str, pd.DataFrame],
                             screener,
                             analyzer,
                             start_date: str,
                             end_date: str) -> Dict:
        """
        전략 백테스트 (여러 종목, 리밸런싱)

        Args:
            historical_data: {ticker: OHLCV DataFrame} 딕셔너리
            screener: 스크리너 객체
            analyzer: 분석기 객체
            start_date: 시작일
            end_date: 종료일

        Returns:
            백테스트 결과
        """
        # 리밸런싱 주기 (월말)
        rebalance_dates = pd.date_range(start=start_date, end=end_date, freq='M')

        capital = self.initial_capital
        portfolio = {}  # {ticker: shares}
        equity_curve = []
        trades = []

        for rebalance_date in rebalance_dates:
            # 현재 포트폴리오 가치
            portfolio_value = capital
            for ticker, shares in portfolio.items():
                if ticker in historical_data:
                    df = historical_data[ticker]
                    price_data = df[df.index <= rebalance_date]
                    if not price_data.empty:
                        current_price = price_data['Close'].iloc[-1]
                        portfolio_value += shares * current_price

            equity_curve.append({
                'date': rebalance_date,
                'equity': portfolio_value
            })

            # 스크리닝 (생략 - 복잡도 때문에 간략화)
            # 실제로는 각 날짜에 스크리닝 수행

        equity_df = pd.DataFrame(equity_curve)
        trades_df = pd.DataFrame(trades)

        return self._calculate_performance(equity_df, trades_df)

    def _calculate_performance(self, equity_df: pd.DataFrame,
                               trades_df: pd.DataFrame) -> Dict:
        """
        성과 지표 계산

        Args:
            equity_df: 자산 곡선 DataFrame
            trades_df: 거래 내역 DataFrame

        Returns:
            성과 지표 딕셔너리
        """
        if equity_df.empty:
            return {}

        final_equity = equity_df['equity'].iloc[-1]
        total_return = ((final_equity - self.initial_capital) / self.initial_capital) * 100

        # 수익률 계산
        equity_df['returns'] = equity_df['equity'].pct_change()

        # 연간 수익률
        days = (equity_df['date'].iloc[-1] - equity_df['date'].iloc[0]).days
        years = days / 365.25
        annual_return = ((final_equity / self.initial_capital) ** (1 / years) - 1) * 100 if years > 0 else 0

        # 변동성 (연율화)
        volatility = equity_df['returns'].std() * np.sqrt(252) * 100

        # 샤프 비율 (무위험 수익률 0% 가정)
        sharpe_ratio = (annual_return / volatility) if volatility > 0 else 0

        # 최대 낙폭 (MDD)
        equity_df['cummax'] = equity_df['equity'].cummax()
        equity_df['drawdown'] = (equity_df['equity'] - equity_df['cummax']) / equity_df['cummax'] * 100
        max_drawdown = equity_df['drawdown'].min()

        # 거래 통계
        if not trades_df.empty:
            num_trades = len(trades_df)
            buy_trades = trades_df[trades_df['type'] == 'BUY']
            sell_trades = trades_df[trades_df['type'] == 'SELL']

            if not sell_trades.empty:
                winning_trades = len(sell_trades[sell_trades['profit_pct'] > 0])
                win_rate = (winning_trades / len(sell_trades)) * 100
                avg_profit = sell_trades['profit_pct'].mean()
            else:
                win_rate = 0
                avg_profit = 0
        else:
            num_trades = 0
            win_rate = 0
            avg_profit = 0

        return {
            'initial_capital': self.initial_capital,
            'final_equity': final_equity,
            'total_return': total_return,
            'annual_return': annual_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'num_trades': num_trades,
            'win_rate': win_rate,
            'avg_profit': avg_profit,
            'equity_curve': equity_df,
            'trades': trades_df
        }

    def generate_backtest_report(self, results: Dict) -> str:
        """
        백테스트 리포트 생성

        Args:
            results: 백테스트 결과

        Returns:
            리포트 문자열
        """
        report = []
        report.append("=" * 60)
        report.append("백테스트 결과 리포트")
        report.append("=" * 60)
        report.append("")

        report.append("[ 수익률 ]")
        report.append(f"  초기 자본: {results['initial_capital']:,.0f}원")
        report.append(f"  최종 자산: {results['final_equity']:,.0f}원")
        report.append(f"  총 수익률: {results['total_return']:.2f}%")
        report.append(f"  연간 수익률: {results['annual_return']:.2f}%")
        report.append("")

        report.append("[ 리스크 ]")
        report.append(f"  변동성 (연): {results['volatility']:.2f}%")
        report.append(f"  샤프 비율: {results['sharpe_ratio']:.2f}")
        report.append(f"  최대 낙폭: {results['max_drawdown']:.2f}%")
        report.append("")

        report.append("[ 거래 통계 ]")
        report.append(f"  총 거래 횟수: {results['num_trades']}")
        report.append(f"  승률: {results['win_rate']:.2f}%")
        report.append(f"  평균 수익률: {results['avg_profit']:.2f}%")
        report.append("")

        report.append("=" * 60)

        return "\n".join(report)

    def compare_with_benchmark(self, strategy_results: Dict,
                               benchmark_df: pd.DataFrame) -> Dict:
        """
        벤치마크와 비교

        Args:
            strategy_results: 전략 백테스트 결과
            benchmark_df: 벤치마크 OHLCV DataFrame

        Returns:
            비교 결과
        """
        # 벤치마크 수익률 계산
        benchmark_start = benchmark_df['Close'].iloc[0]
        benchmark_end = benchmark_df['Close'].iloc[-1]
        benchmark_return = ((benchmark_end - benchmark_start) / benchmark_start) * 100

        # 초과 수익률
        alpha = strategy_results['total_return'] - benchmark_return

        return {
            'strategy_return': strategy_results['total_return'],
            'benchmark_return': benchmark_return,
            'alpha': alpha,
            'outperformed': alpha > 0
        }
