"""
설정 관리 모듈 (Config Manager)
모든 시스템 설정을 데이터베이스에 영구 저장하고 관리
"""

import sqlite3
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import time

@dataclass
class WorkSchedule:
    """
    근무 스케줄 정의
    주간/야간/교대 등 다양한 근무 형태 지원
    """
    schedule_id: str                    # 스케줄 ID (예: DAY, NIGHT, SHIFT_2W)
    schedule_name: str                  # 스케줄 이름 (예: 주간근무, 야간근무)
    work_start_time: str               # 근무 시작 시간 (HH:MM)
    work_end_time: str                 # 근무 종료 시간 (HH:MM)
    break_time_minutes: int            # 휴게시간 (분)
    is_night_shift: bool               # 야간 근무 여부
    night_start_time: str              # 야간 시작 시간 (HH:MM)
    night_end_time: str                # 야간 종료 시간 (HH:MM)
    description: str = ""              # 설명

@dataclass
class OvertimeRate:
    """
    잔업 수당 계수 정의
    시간대별로 차등 적용 가능
    """
    tier_id: str                       # 구간 ID (예: TIER_1, TIER_2)
    tier_name: str                     # 구간 이름 (예: 1시간 이내, 2시간 이내)
    start_minutes: int                 # 시작 시간 (분 단위, 0부터 시작)
    end_minutes: Optional[int]         # 종료 시간 (분 단위, None이면 무제한)
    rate_multiplier: float             # 수당 배율 (0.5, 1.0, 1.5, 2.0 등)
    description: str = ""              # 설명

class ConfigManager:
    """
    설정 관리자
    모든 시스템 설정을 데이터베이스에서 관리
    """
    
    def __init__(self, db_path: str = "payroll.db"):
        """
        설정 관리자 초기화
        
        Args:
            db_path: 데이터베이스 파일 경로
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """데이터베이스 연결"""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        
    def close(self):
        """데이터베이스 연결 종료"""
        if self.conn:
            self.conn.close()
            
    def initialize_tables(self):
        """
        설정 관련 테이블 초기화
        """
        self.connect()
        
        # 1. 근무 스케줄 테이블
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS work_schedules (
                schedule_id TEXT PRIMARY KEY,
                schedule_name TEXT NOT NULL,
                work_start_time TEXT NOT NULL,
                work_end_time TEXT NOT NULL,
                break_time_minutes INTEGER DEFAULT 60,
                is_night_shift INTEGER DEFAULT 0,
                night_start_time TEXT DEFAULT '22:00',
                night_end_time TEXT DEFAULT '06:00',
                description TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 2. 잔업 수당 계수 테이블
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS overtime_rates (
                tier_id TEXT PRIMARY KEY,
                tier_name TEXT NOT NULL,
                start_minutes INTEGER NOT NULL,
                end_minutes INTEGER,
                rate_multiplier REAL NOT NULL,
                description TEXT,
                display_order INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 3. 시스템 설정 테이블
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_settings (
                setting_key TEXT PRIMARY KEY,
                setting_value TEXT,
                setting_type TEXT DEFAULT 'string',
                description TEXT,
                category TEXT DEFAULT 'general',
                is_editable INTEGER DEFAULT 1,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.conn.commit()
        
        # 기본 데이터 삽입
        self._insert_default_schedules()
        self._insert_default_overtime_rates()
        self._insert_default_settings()
        
        self.close()
        
    def _insert_default_schedules(self):
        """
        기본 근무 스케줄 삽입
        """
        default_schedules = [
            WorkSchedule(
                schedule_id="DAY_SHIFT",
                schedule_name="주간근무 (09:00~18:00)",
                work_start_time="09:00",
                work_end_time="18:00",
                break_time_minutes=60,
                is_night_shift=False,
                night_start_time="22:00",
                night_end_time="06:00",
                description="일반적인 주간 근무"
            ),
            WorkSchedule(
                schedule_id="NIGHT_SHIFT",
                schedule_name="야간근무 (21:00~06:00)",
                work_start_time="21:00",
                work_end_time="06:00",
                break_time_minutes=60,
                is_night_shift=True,
                night_start_time="22:00",
                night_end_time="06:00",
                description="야간 전담 근무"
            ),
            WorkSchedule(
                schedule_id="SHIFT_2W_DAY",
                schedule_name="2교대(주간) (06:00~18:00)",
                work_start_time="06:00",
                work_end_time="18:00",
                break_time_minutes=60,
                is_night_shift=False,
                night_start_time="22:00",
                night_end_time="06:00",
                description="2교대 주간 근무"
            ),
            WorkSchedule(
                schedule_id="SHIFT_2W_NIGHT",
                schedule_name="2교대(야간) (18:00~06:00)",
                work_start_time="18:00",
                work_end_time="06:00",
                break_time_minutes=60,
                is_night_shift=True,
                night_start_time="22:00",
                night_end_time="06:00",
                description="2교대 야간 근무"
            ),
        ]
        
        for schedule in default_schedules:
            self.cursor.execute("""
                INSERT OR IGNORE INTO work_schedules (
                    schedule_id, schedule_name, work_start_time, work_end_time,
                    break_time_minutes, is_night_shift, night_start_time, 
                    night_end_time, description
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                schedule.schedule_id,
                schedule.schedule_name,
                schedule.work_start_time,
                schedule.work_end_time,
                schedule.break_time_minutes,
                1 if schedule.is_night_shift else 0,
                schedule.night_start_time,
                schedule.night_end_time,
                schedule.description
            ))
        
        self.conn.commit()
        
    def _insert_default_overtime_rates(self):
        """
        기본 잔업 수당 계수 삽입
        예: 0~60분 = 0.5배, 60~120분 = 1.0배, 120분 이상 = 2.0배
        """
        default_rates = [
            OvertimeRate(
                tier_id="TIER_1",
                tier_name="1시간 이내",
                start_minutes=0,
                end_minutes=60,
                rate_multiplier=0.5,
                description="첫 1시간 이내 잔업"
            ),
            OvertimeRate(
                tier_id="TIER_2",
                tier_name="1~2시간",
                start_minutes=60,
                end_minutes=120,
                rate_multiplier=1.0,
                description="1시간 초과 2시간 이내"
            ),
            OvertimeRate(
                tier_id="TIER_3",
                tier_name="2시간 초과",
                start_minutes=120,
                end_minutes=None,
                rate_multiplier=2.0,
                description="2시간 초과 잔업"
            ),
        ]
        
        for idx, rate in enumerate(default_rates):
            self.cursor.execute("""
                INSERT OR IGNORE INTO overtime_rates (
                    tier_id, tier_name, start_minutes, end_minutes,
                    rate_multiplier, description, display_order
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                rate.tier_id,
                rate.tier_name,
                rate.start_minutes,
                rate.end_minutes,
                rate.rate_multiplier,
                rate.description,
                idx
            ))
        
        self.conn.commit()
        
    def _insert_default_settings(self):
        """
        기본 시스템 설정 삽입
        """
        default_settings = [
            # 4대보험 요율
            ('national_pension_rate', '0.045', 'float', '국민연금 요율', 'insurance', 1),
            ('health_insurance_rate', '0.03545', 'float', '건강보험 요율', 'insurance', 1),
            ('long_term_care_rate', '0.1295', 'float', '장기요양보험 요율 (건강보험 대비)', 'insurance', 1),
            ('employment_insurance_rate', '0.009', 'float', '고용보험 요율', 'insurance', 1),
            
            # 급여 관련
            ('payday', '25', 'int', '급여 지급일', 'payroll', 1),
            ('default_meal_allowance', '10000', 'int', '기본 식대 (1회)', 'payroll', 1),
            
            # 회사 정보
            ('company_name', '회사명', 'string', '회사 이름', 'company', 1),
            ('company_registration', '', 'string', '사업자등록번호', 'company', 1),
            ('company_address', '', 'string', '회사 주소', 'company', 1),
            
            # 세콤 연동 설정
            ('secom_integration_enabled', 'false', 'bool', '세콤 연동 활성화', 'integration', 1),
            ('secom_api_url', '', 'string', '세콤 API URL', 'integration', 1),
            ('secom_api_key', '', 'string', '세콤 API 키', 'integration', 1),
            ('secom_sync_time', '08:00', 'string', '세콤 동기화 시간', 'integration', 1),
        ]
        
        for key, value, s_type, desc, category, editable in default_settings:
            self.cursor.execute("""
                INSERT OR IGNORE INTO system_settings (
                    setting_key, setting_value, setting_type, description, category, is_editable
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (key, value, s_type, desc, category, editable))
        
        self.conn.commit()
        
    # ========== 근무 스케줄 관리 ==========
    
    def get_all_schedules(self) -> List[Dict]:
        """모든 근무 스케줄 조회"""
        self.connect()
        self.cursor.execute("""
            SELECT schedule_id, schedule_name, work_start_time, work_end_time,
                   break_time_minutes, is_night_shift, night_start_time, 
                   night_end_time, description
            FROM work_schedules
            ORDER BY schedule_id
        """)
        
        schedules = []
        for row in self.cursor.fetchall():
            schedules.append({
                'schedule_id': row[0],
                'schedule_name': row[1],
                'work_start_time': row[2],
                'work_end_time': row[3],
                'break_time_minutes': row[4],
                'is_night_shift': bool(row[5]),
                'night_start_time': row[6],
                'night_end_time': row[7],
                'description': row[8]
            })
        
        self.close()
        return schedules
    
    def get_schedule(self, schedule_id: str) -> Optional[Dict]:
        """특정 근무 스케줄 조회"""
        schedules = self.get_all_schedules()
        for schedule in schedules:
            if schedule['schedule_id'] == schedule_id:
                return schedule
        return None
    
    def add_schedule(self, schedule: WorkSchedule) -> bool:
        """근무 스케줄 추가"""
        try:
            self.connect()
            self.cursor.execute("""
                INSERT INTO work_schedules (
                    schedule_id, schedule_name, work_start_time, work_end_time,
                    break_time_minutes, is_night_shift, night_start_time,
                    night_end_time, description
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                schedule.schedule_id,
                schedule.schedule_name,
                schedule.work_start_time,
                schedule.work_end_time,
                schedule.break_time_minutes,
                1 if schedule.is_night_shift else 0,
                schedule.night_start_time,
                schedule.night_end_time,
                schedule.description
            ))
            self.conn.commit()
            self.close()
            return True
        except Exception as e:
            print(f"❌ 스케줄 추가 오류: {e}")
            self.close()
            return False
    
    def update_schedule(self, schedule: WorkSchedule) -> bool:
        """근무 스케줄 수정"""
        try:
            self.connect()
            self.cursor.execute("""
                UPDATE work_schedules
                SET schedule_name = ?,
                    work_start_time = ?,
                    work_end_time = ?,
                    break_time_minutes = ?,
                    is_night_shift = ?,
                    night_start_time = ?,
                    night_end_time = ?,
                    description = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE schedule_id = ?
            """, (
                schedule.schedule_name,
                schedule.work_start_time,
                schedule.work_end_time,
                schedule.break_time_minutes,
                1 if schedule.is_night_shift else 0,
                schedule.night_start_time,
                schedule.night_end_time,
                schedule.description,
                schedule.schedule_id
            ))
            self.conn.commit()
            self.close()
            return True
        except Exception as e:
            print(f"❌ 스케줄 수정 오류: {e}")
            self.close()
            return False
    
    # ========== 잔업 수당 계수 관리 ==========
    
    def get_all_overtime_rates(self) -> List[Dict]:
        """모든 잔업 수당 계수 조회"""
        self.connect()
        self.cursor.execute("""
            SELECT tier_id, tier_name, start_minutes, end_minutes,
                   rate_multiplier, description
            FROM overtime_rates
            ORDER BY display_order, start_minutes
        """)
        
        rates = []
        for row in self.cursor.fetchall():
            rates.append({
                'tier_id': row[0],
                'tier_name': row[1],
                'start_minutes': row[2],
                'end_minutes': row[3],
                'rate_multiplier': row[4],
                'description': row[5]
            })
        
        self.close()
        return rates
    
    def calculate_overtime_pay(self, overtime_minutes: float, hourly_wage: float) -> float:
        """
        잔업 수당 계산 (시간대별 차등 적용)
        
        Args:
            overtime_minutes: 잔업 시간 (분)
            hourly_wage: 시급
            
        Returns:
            잔업 수당 총액
        """
        if overtime_minutes <= 0:
            return 0
        
        rates = self.get_all_overtime_rates()
        total_pay = 0
        remaining_minutes = overtime_minutes
        
        for rate in rates:
            if remaining_minutes <= 0:
                break
            
            # 이 구간에서 적용할 시간 계산
            tier_start = rate['start_minutes']
            tier_end = rate['end_minutes'] if rate['end_minutes'] else 999999
            
            # 해당 구간에 해당하는 시간
            if overtime_minutes > tier_start:
                applicable_minutes = min(
                    remaining_minutes,
                    tier_end - tier_start
                )
                
                # 수당 계산
                applicable_hours = applicable_minutes / 60
                tier_pay = applicable_hours * hourly_wage * rate['rate_multiplier']
                total_pay += tier_pay
                
                remaining_minutes -= applicable_minutes
        
        return round(total_pay, 0)
    
    def update_overtime_rate(self, rate: OvertimeRate) -> bool:
        """잔업 수당 계수 수정"""
        try:
            self.connect()
            self.cursor.execute("""
                UPDATE overtime_rates
                SET tier_name = ?,
                    start_minutes = ?,
                    end_minutes = ?,
                    rate_multiplier = ?,
                    description = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE tier_id = ?
            """, (
                rate.tier_name,
                rate.start_minutes,
                rate.end_minutes,
                rate.rate_multiplier,
                rate.description,
                rate.tier_id
            ))
            self.conn.commit()
            self.close()
            return True
        except Exception as e:
            print(f"❌ 잔업 계수 수정 오류: {e}")
            self.close()
            return False
    
    # ========== 시스템 설정 관리 ==========
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """설정값 조회"""
        self.connect()
        self.cursor.execute("""
            SELECT setting_value, setting_type 
            FROM system_settings 
            WHERE setting_key = ?
        """, (key,))
        
        result = self.cursor.fetchone()
        self.close()
        
        if not result:
            return default
        
        value, s_type = result
        
        # 타입 변환
        if s_type == 'int':
            return int(value)
        elif s_type == 'float':
            return float(value)
        elif s_type == 'bool':
            return value.lower() == 'true'
        else:
            return value
    
    def set_setting(self, key: str, value: Any) -> bool:
        """설정값 저장"""
        try:
            self.connect()
            
            # 문자열로 변환
            if isinstance(value, bool):
                str_value = 'true' if value else 'false'
            else:
                str_value = str(value)
            
            self.cursor.execute("""
                UPDATE system_settings 
                SET setting_value = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE setting_key = ?
            """, (str_value, key))
            
            self.conn.commit()
            self.close()
            return True
        except Exception as e:
            print(f"❌ 설정 저장 오류: {e}")
            self.close()
            return False
    
    def get_all_settings(self, category: Optional[str] = None) -> Dict[str, Any]:
        """모든 설정 조회"""
        self.connect()
        
        if category:
            self.cursor.execute("""
                SELECT setting_key, setting_value, setting_type, description, is_editable
                FROM system_settings
                WHERE category = ?
                ORDER BY setting_key
            """, (category,))
        else:
            self.cursor.execute("""
                SELECT setting_key, setting_value, setting_type, description, is_editable
                FROM system_settings
                ORDER BY category, setting_key
            """)
        
        settings = {}
        for row in self.cursor.fetchall():
            key, value, s_type, desc, editable = row
            
            # 타입 변환
            if s_type == 'int':
                converted_value = int(value)
            elif s_type == 'float':
                converted_value = float(value)
            elif s_type == 'bool':
                converted_value = value.lower() == 'true'
            else:
                converted_value = value
            
            settings[key] = {
                'value': converted_value,
                'type': s_type,
                'description': desc,
                'editable': bool(editable)
            }
        
        self.close()
        return settings


# 테스트 코드
if __name__ == "__main__":
    print("=" * 60)
    print("설정 관리 모듈 테스트")
    print("=" * 60)
    
    config = ConfigManager()
    config.initialize_tables()
    
    print("\n📋 근무 스케줄 목록:")
    schedules = config.get_all_schedules()
    for s in schedules:
        print(f"  - {s['schedule_name']}: {s['work_start_time']}~{s['work_end_time']}")
    
    print("\n💰 잔업 수당 계수:")
    rates = config.get_all_overtime_rates()
    for r in rates:
        end = f"{r['end_minutes']}분" if r['end_minutes'] else "무제한"
        print(f"  - {r['tier_name']}: {r['start_minutes']}~{end} = {r['rate_multiplier']}배")
    
    print("\n🧮 잔업 수당 계산 테스트 (시급 20,000원):")
    test_cases = [30, 90, 150]
    for minutes in test_cases:
        pay = config.calculate_overtime_pay(minutes, 20000)
        print(f"  - {minutes}분 잔업 = {pay:,.0f}원")
    
    print("\n⚙️ 시스템 설정:")
    settings = config.get_all_settings('insurance')
    for key, info in settings.items():
        print(f"  - {info['description']}: {info['value']}")
    
    print("\n✅ 설정 관리 모듈 준비 완료!")
