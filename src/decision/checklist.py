"""
투자 의사결정 체크리스트
종목 분석 시 체계적으로 확인해야 할 항목들
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
from pathlib import Path
import logging


class DecisionChecklist:
    """투자 의사결정 체크리스트"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def create_checklist_template(self) -> Dict:
        """
        체크리스트 템플릿 생성

        Returns:
            체크리스트 딕셔너리
        """
        return {
            'ticker': '',
            'name': '',
            'date': datetime.now().strftime("%Y-%m-%d"),
            'decision': None,  # 'BUY', 'SELL', 'HOLD', 'PASS'

            # 1. 정량적 지표
            'quantitative': {
                'pbr': {
                    'value': None,
                    'target': '≤ 1.0, 밴드 하단',
                    'passed': None,
                    'note': ''
                },
                'per': {
                    'value': None,
                    'target': '10~15배',
                    'passed': None,
                    'note': ''
                },
                'volume': {
                    'value': None,
                    'target': '충분한 유동성',
                    'passed': None,
                    'note': ''
                },
                'market_cap': {
                    'value': None,
                    'target': '중소형주 우대',
                    'passed': None,
                    'note': ''
                },
                'roe': {
                    'value': None,
                    'target': '≥ 5%',
                    'passed': None,
                    'note': ''
                },
                'debt_ratio': {
                    'value': None,
                    'target': '≤ 200%',
                    'passed': None,
                    'note': ''
                }
            },

            # 2. 정성적 분석
            'qualitative': {
                'market_position': {
                    'is_leader': None,
                    'moat': None,
                    'competitive_advantage': [],
                    'note': ''
                },
                'sector_analysis': {
                    'sector': '',
                    'growth_potential': None,
                    'current_cycle': '',
                    'note': ''
                },
                'business_model': {
                    'clarity': None,
                    'sustainability': None,
                    'note': ''
                }
            },

            # 3. 기술적 분석
            'technical': {
                'price_adjustment': {
                    'completed': None,
                    'correction_pct': None,
                    'note': ''
                },
                'consolidation': {
                    'in_consolidation': None,
                    'days': None,
                    'note': ''
                },
                'support_level': {
                    'near_support': None,
                    'level': None,
                    'note': ''
                },
                'rsi': {
                    'value': None,
                    'signal': '',
                    'note': ''
                },
                'moving_averages': {
                    'position': '',
                    'support': None,
                    'note': ''
                }
            },

            # 4. 리스크 평가
            'risk': {
                'market_risk': {
                    'level': '',  # 'LOW', 'MEDIUM', 'HIGH'
                    'note': ''
                },
                'company_risk': {
                    'level': '',
                    'note': ''
                },
                'sector_risk': {
                    'level': '',
                    'note': ''
                },
                'overall_risk': {
                    'level': '',
                    'acceptable': None
                }
            },

            # 5. 투자 전략
            'strategy': {
                'entry_plan': {
                    'method': '',  # '일괄 매수', '분할 매수'
                    'price_targets': [],
                    'position_size': None,
                    'note': ''
                },
                'exit_plan': {
                    'target_return': None,  # %
                    'stop_loss': None,  # %
                    'holding_period': '',
                    'note': ''
                }
            },

            # 6. 종합 평가
            'summary': {
                'total_score': 0,
                'strengths': [],
                'weaknesses': [],
                'key_risks': [],
                'final_decision': '',
                'confidence_level': '',  # 'LOW', 'MEDIUM', 'HIGH'
                'notes': ''
            }
        }

    def evaluate_stock(self, stock_data: Dict, technical_signals: Dict,
                      market: str = 'KR') -> Dict:
        """
        종목 평가 및 체크리스트 자동 작성

        Args:
            stock_data: 종목 데이터
            technical_signals: 기술적 신호
            market: 시장 구분

        Returns:
            작성된 체크리스트
        """
        checklist = self.create_checklist_template()

        # 기본 정보
        checklist['ticker'] = stock_data.get('ticker', '')
        checklist['name'] = stock_data.get('name', '')

        # 1. 정량적 지표 평가
        self._evaluate_quantitative(checklist, stock_data)

        # 2. 기술적 분석 평가
        self._evaluate_technical(checklist, technical_signals)

        # 3. 종합 점수 계산
        self._calculate_total_score(checklist)

        # 4. 최종 의사결정
        self._make_final_decision(checklist)

        return checklist

    def _evaluate_quantitative(self, checklist: Dict, stock_data: Dict):
        """정량적 지표 평가"""
        quant = checklist['quantitative']

        # PBR
        pbr = stock_data.get('PBR') or stock_data.get('PB')
        if pbr:
            quant['pbr']['value'] = pbr
            quant['pbr']['passed'] = pbr <= 1.0

        # PER
        per = stock_data.get('PER') or stock_data.get('PE')
        if per:
            quant['per']['value'] = per
            quant['per']['passed'] = 10 <= per <= 15

        # 거래량
        volume_analysis = stock_data.get('volume_analysis', {})
        if volume_analysis:
            quant['volume']['value'] = volume_analysis.get('avg_daily_value')
            quant['volume']['passed'] = volume_analysis.get('has_sufficient_liquidity', False)

        # 시가총액
        market_cap = stock_data.get('market_cap')
        if market_cap:
            quant['market_cap']['value'] = market_cap
            quant['market_cap']['passed'] = True  # 범위 내 진입했으면 통과

        # ROE
        roe = stock_data.get('ROE')
        if roe:
            quant['roe']['value'] = roe
            quant['roe']['passed'] = roe >= 5.0

        # 부채비율
        debt_ratio = stock_data.get('debt_to_equity')
        if debt_ratio:
            quant['debt_ratio']['value'] = debt_ratio
            quant['debt_ratio']['passed'] = debt_ratio <= 200

    def _evaluate_technical(self, checklist: Dict, technical_signals: Dict):
        """기술적 분석 평가"""
        tech = checklist['technical']

        # 가격 조정
        if 'price_adjusted' in technical_signals:
            tech['price_adjustment']['completed'] = technical_signals['price_adjusted']

        # 횡보 구간
        if 'consolidating' in technical_signals:
            tech['consolidation']['in_consolidation'] = technical_signals['consolidating']

        # 지지선
        if 'near_support' in technical_signals:
            tech['support_level']['near_support'] = technical_signals['near_support']

        # RSI
        if 'rsi' in technical_signals:
            rsi = technical_signals['rsi']
            tech['rsi']['value'] = rsi
            if rsi < 30:
                tech['rsi']['signal'] = '과매도'
            elif rsi < 40:
                tech['rsi']['signal'] = '매수 고려'
            elif rsi > 70:
                tech['rsi']['signal'] = '과매수'
            else:
                tech['rsi']['signal'] = '중립'

    def _calculate_total_score(self, checklist: Dict):
        """종합 점수 계산"""
        score = 0
        passed_items = []
        failed_items = []

        # 정량적 지표 점수
        for key, item in checklist['quantitative'].items():
            if item['passed'] is True:
                score += 15
                passed_items.append(key.upper())
            elif item['passed'] is False:
                failed_items.append(key.upper())

        # 기술적 분석 점수
        tech = checklist['technical']
        if tech['price_adjustment']['completed']:
            score += 10
            passed_items.append('가격조정완료')

        if tech['consolidation']['in_consolidation']:
            score += 10
            passed_items.append('횡보구간')

        if tech['support_level']['near_support']:
            score += 15
            passed_items.append('지지선접근')

        rsi_value = tech['rsi']['value']
        if rsi_value and rsi_value < 40:
            score += 10
            passed_items.append('RSI과매도')

        checklist['summary']['total_score'] = score
        checklist['summary']['strengths'] = passed_items
        checklist['summary']['weaknesses'] = failed_items

    def _make_final_decision(self, checklist: Dict):
        """최종 의사결정"""
        score = checklist['summary']['total_score']

        if score >= 80:
            checklist['decision'] = 'BUY'
            checklist['summary']['final_decision'] = '매수 적극 추천'
            checklist['summary']['confidence_level'] = 'HIGH'
        elif score >= 60:
            checklist['decision'] = 'BUY'
            checklist['summary']['final_decision'] = '매수 고려'
            checklist['summary']['confidence_level'] = 'MEDIUM'
        elif score >= 40:
            checklist['decision'] = 'HOLD'
            checklist['summary']['final_decision'] = '관심 종목 등록'
            checklist['summary']['confidence_level'] = 'MEDIUM'
        else:
            checklist['decision'] = 'PASS'
            checklist['summary']['final_decision'] = '투자 제외'
            checklist['summary']['confidence_level'] = 'LOW'

    def _convert_to_json_serializable(self, obj: Any) -> Any:
        """
        객체를 JSON 직렬화 가능한 형태로 변환

        Args:
            obj: 변환할 객체

        Returns:
            JSON 직렬화 가능한 객체
        """
        if isinstance(obj, dict):
            return {key: self._convert_to_json_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_to_json_serializable(item) for item in obj]
        elif isinstance(obj, (np.integer, np.int64, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32)):
            return float(obj)
        elif isinstance(obj, (np.bool_)):
            return bool(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif pd.isna(obj):
            return None
        else:
            return obj

    def save_checklist(self, checklist: Dict, file_path: str = None):
        """
        체크리스트 저장

        Args:
            checklist: 체크리스트 딕셔너리
            file_path: 저장 경로
        """
        if file_path is None:
            data_dir = Path(__file__).parent.parent.parent / "data" / "checklists"
            data_dir.mkdir(parents=True, exist_ok=True)

            ticker = checklist['ticker']
            date = checklist['date'].replace('-', '')
            file_path = data_dir / f"{ticker}_{date}_checklist.json"

        try:
            # JSON 직렬화 가능한 형태로 변환
            serializable_checklist = self._convert_to_json_serializable(checklist)

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(serializable_checklist, f, ensure_ascii=False, indent=2)

            self.logger.info(f"체크리스트 저장 완료: {file_path}")

        except Exception as e:
            self.logger.error(f"체크리스트 저장 실패: {e}")

    def load_checklist(self, file_path: str) -> Dict:
        """
        체크리스트 불러오기

        Args:
            file_path: 파일 경로

        Returns:
            체크리스트 딕셔너리
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)

        except Exception as e:
            self.logger.error(f"체크리스트 로드 실패: {e}")
            return {}

    def print_checklist(self, checklist: Dict) -> str:
        """
        체크리스트 포맷팅 (출력용)

        Args:
            checklist: 체크리스트 딕셔너리

        Returns:
            포맷팅된 문자열
        """
        output = []
        output.append("=" * 60)
        output.append(f"투자 의사결정 체크리스트")
        output.append("=" * 60)
        output.append(f"종목: {checklist['name']} ({checklist['ticker']})")
        output.append(f"날짜: {checklist['date']}")
        output.append(f"최종 결정: {checklist['summary']['final_decision']}")
        output.append(f"신뢰도: {checklist['summary']['confidence_level']}")
        output.append(f"종합 점수: {checklist['summary']['total_score']}/100")
        output.append("")

        # 정량적 지표
        output.append("[ 정량적 지표 ]")
        for key, item in checklist['quantitative'].items():
            status = "✓" if item['passed'] else "✗" if item['passed'] is not None else "-"
            value = item['value'] if item['value'] is not None else 'N/A'
            output.append(f"  {status} {key.upper()}: {value} (목표: {item['target']})")

        output.append("")

        # 기술적 분석
        output.append("[ 기술적 분석 ]")
        tech = checklist['technical']

        status = "✓" if tech['price_adjustment']['completed'] else "✗"
        output.append(f"  {status} 가격 조정 완료")

        status = "✓" if tech['consolidation']['in_consolidation'] else "✗"
        output.append(f"  {status} 횡보 구간 (기간 조정)")

        status = "✓" if tech['support_level']['near_support'] else "✗"
        output.append(f"  {status} 지지선 접근")

        rsi_value = tech['rsi']['value']
        if rsi_value:
            output.append(f"  RSI: {rsi_value:.2f} ({tech['rsi']['signal']})")

        output.append("")

        # 강점/약점
        if checklist['summary']['strengths']:
            output.append("[ 강점 ]")
            for strength in checklist['summary']['strengths']:
                output.append(f"  + {strength}")
            output.append("")

        if checklist['summary']['weaknesses']:
            output.append("[ 약점 ]")
            for weakness in checklist['summary']['weaknesses']:
                output.append(f"  - {weakness}")
            output.append("")

        output.append("=" * 60)

        return "\n".join(output)
