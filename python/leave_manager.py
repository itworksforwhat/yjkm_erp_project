"""
연차 및 휴가 관리 모듈
연차, 반차, 병가, 특별휴가 등 모든 휴가 관리
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class LeaveType(Enum):
    """휴가 유형"""
    ANNUAL = "연차"
    HALF_DAY = "반차"
    SICK = "병가"
    SPECIAL = "특별휴가"
    MATERNITY = "출산휴가"
    PATERNITY = "배우자출산휴가"
    FAMILY_CARE = "가족돌봄휴가"
    BEREAVEMENT = "경조사휴가"
    UNPAID = "무급휴가"
    
class LeaveStatus(Enum):
    """휴가 상태"""
    PENDING = "대기중"
    APPROVED = "승인됨"
    REJECTED = "반려됨"
    CANCELLED = "취소됨"

@dataclass
class LeavePolicy:
    """휴가 정책 설정"""
    policy_id: str
    policy_name: str
    
    # 연차 발생 규칙
    annual_days_per_year: float          # 연간 기본 연차 일수 (15일)
    annual_increase_per_2years: float    # 2년마다 추가 연차 (1일)
    max_annual_days: int                 # 최대 연차 일수 (25일)
    
    # 월차 발생 (1년 미만 근무자)
    monthly_leave_enabled: bool          # 월차 사용 가능 여부
    monthly_leave_days: float            # 월 1일 (1/12)
    
    # 반차 규칙
    half_day_enabled: bool               # 반차 사용 가능
    half_day_hours: float                # 반차 시간 (4시간)
    
    # 병가
    sick_leave_enabled: bool             # 병가 사용 가능
    sick_leave_paid_days: int            # 유급 병가 일수
    sick_leave_unpaid_allowed: bool      # 무급 병가 허용
    
    # 특별휴가
    maternity_days: int                  # 출산휴가 일수 (90일)
    paternity_days: int                  # 배우자 출산휴가 (10일)
    bereavement_days: int                # 경조사휴가 (5일)
    
    # 기타
    carry_forward_enabled: bool          # 연차 이월 가능
    carry_forward_max_days: int          # 최대 이월 일수
    carry_forward_expire_months: int     # 이월 연차 소멸 월수
    
    description: str = ""

class LeaveManager:
    """
    휴가 관리 시스템
    """
    
    def __init__(self, db_path: str = "payroll.db"):
        """휴가 관리자 초기화"""
        import sqlite3
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """데이터베이스 연결"""
        import sqlite3
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        
    def close(self):
        """데이터베이스 연결 종료"""
        if self.conn:
            self.conn.close()
            
    def initialize_tables(self):
        """휴가 관련 테이블 초기화"""
        self.connect()
        
        # 1. 휴가 정책 테이블
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS leave_policies (
                policy_id TEXT PRIMARY KEY,
                policy_name TEXT NOT NULL,
                annual_days_per_year REAL DEFAULT 15,
                annual_increase_per_2years REAL DEFAULT 1,
                max_annual_days INTEGER DEFAULT 25,
                monthly_leave_enabled INTEGER DEFAULT 1,
                monthly_leave_days REAL DEFAULT 1,
                half_day_enabled INTEGER DEFAULT 1,
                half_day_hours REAL DEFAULT 4,
                sick_leave_enabled INTEGER DEFAULT 1,
                sick_leave_paid_days INTEGER DEFAULT 3,
                sick_leave_unpaid_allowed INTEGER DEFAULT 1,
                maternity_days INTEGER DEFAULT 90,
                paternity_days INTEGER DEFAULT 10,
                bereavement_days INTEGER DEFAULT 5,
                carry_forward_enabled INTEGER DEFAULT 1,
                carry_forward_max_days INTEGER DEFAULT 11,
                carry_forward_expire_months INTEGER DEFAULT 12,
                description TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 2. 직원별 연차 현황 테이블
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS employee_leave_balance (
                balance_id INTEGER PRIMARY KEY AUTOINCREMENT,
                emp_id INTEGER NOT NULL,
                year INTEGER NOT NULL,
                
                -- 연차 현황
                total_annual_days REAL DEFAULT 0,      -- 총 부여 연차
                used_annual_days REAL DEFAULT 0,       -- 사용한 연차
                remaining_annual_days REAL DEFAULT 0,  -- 남은 연차
                
                -- 이월 연차
                carried_forward_days REAL DEFAULT 0,   -- 이월 연차
                carried_forward_used REAL DEFAULT 0,   -- 사용한 이월 연차
                carried_forward_expire_date TEXT,      -- 이월 연차 소멸일
                
                -- 기타 휴가
                used_sick_days REAL DEFAULT 0,         -- 사용한 병가
                used_special_days REAL DEFAULT 0,      -- 사용한 특별휴가
                
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (emp_id) REFERENCES employees(emp_id),
                UNIQUE(emp_id, year)
            )
        """)
        
        # 3. 휴가 신청 테이블
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS leave_requests (
                request_id INTEGER PRIMARY KEY AUTOINCREMENT,
                emp_id INTEGER NOT NULL,
                
                -- 휴가 정보
                leave_type TEXT NOT NULL,              -- ANNUAL, HALF_DAY, SICK, etc.
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                total_days REAL NOT NULL,              -- 총 휴가 일수
                
                -- 반차 정보
                is_half_day INTEGER DEFAULT 0,
                half_day_period TEXT,                  -- AM, PM
                
                -- 신청 정보
                reason TEXT,
                request_date TEXT NOT NULL,
                
                -- 승인 정보
                status TEXT DEFAULT 'PENDING',         -- PENDING, APPROVED, REJECTED, CANCELLED
                approver_id INTEGER,                   -- 승인자 ID
                approved_date TEXT,
                reject_reason TEXT,
                
                -- 기타
                attachments TEXT,                      -- 첨부파일 경로 (JSON)
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (emp_id) REFERENCES employees(emp_id)
            )
        """)
        
        # 4. 휴가 사용 이력 테이블
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS leave_history (
                history_id INTEGER PRIMARY KEY AUTOINCREMENT,
                emp_id INTEGER NOT NULL,
                request_id INTEGER,
                
                leave_date TEXT NOT NULL,
                leave_type TEXT NOT NULL,
                days_used REAL NOT NULL,
                
                is_half_day INTEGER DEFAULT 0,
                half_day_period TEXT,
                
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (emp_id) REFERENCES employees(emp_id),
                FOREIGN KEY (request_id) REFERENCES leave_requests(request_id)
            )
        """)
        
        self.conn.commit()
        
        # 기본 휴가 정책 삽입
        self._insert_default_policy()
        
        self.close()
        
    def _insert_default_policy(self):
        """기본 휴가 정책 삽입"""
        default_policy = LeavePolicy(
            policy_id="DEFAULT",
            policy_name="표준 휴가 정책",
            annual_days_per_year=15,
            annual_increase_per_2years=1,
            max_annual_days=25,
            monthly_leave_enabled=True,
            monthly_leave_days=1,
            half_day_enabled=True,
            half_day_hours=4,
            sick_leave_enabled=True,
            sick_leave_paid_days=3,
            sick_leave_unpaid_allowed=True,
            maternity_days=90,
            paternity_days=10,
            bereavement_days=5,
            carry_forward_enabled=True,
            carry_forward_max_days=11,
            carry_forward_expire_months=12,
            description="근로기준법에 따른 표준 휴가 정책"
        )
        
        self.cursor.execute("""
            INSERT OR IGNORE INTO leave_policies (
                policy_id, policy_name, annual_days_per_year, 
                annual_increase_per_2years, max_annual_days,
                monthly_leave_enabled, monthly_leave_days,
                half_day_enabled, half_day_hours,
                sick_leave_enabled, sick_leave_paid_days, sick_leave_unpaid_allowed,
                maternity_days, paternity_days, bereavement_days,
                carry_forward_enabled, carry_forward_max_days, 
                carry_forward_expire_months, description
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            default_policy.policy_id,
            default_policy.policy_name,
            default_policy.annual_days_per_year,
            default_policy.annual_increase_per_2years,
            default_policy.max_annual_days,
            1 if default_policy.monthly_leave_enabled else 0,
            default_policy.monthly_leave_days,
            1 if default_policy.half_day_enabled else 0,
            default_policy.half_day_hours,
            1 if default_policy.sick_leave_enabled else 0,
            default_policy.sick_leave_paid_days,
            1 if default_policy.sick_leave_unpaid_allowed else 0,
            default_policy.maternity_days,
            default_policy.paternity_days,
            default_policy.bereavement_days,
            1 if default_policy.carry_forward_enabled else 0,
            default_policy.carry_forward_max_days,
            default_policy.carry_forward_expire_months,
            default_policy.description
        ))
        
        self.conn.commit()
        
    def calculate_annual_leave(self, hire_date: str, current_date: str = None) -> float:
        """
        근속년수에 따른 연차 일수 계산
        
        Args:
            hire_date: 입사일 (YYYY-MM-DD)
            current_date: 기준일 (기본값: 오늘)
            
        Returns:
            연차 일수
        """
        if current_date is None:
            current_date = datetime.now().strftime('%Y-%m-%d')
        
        hire_dt = datetime.strptime(hire_date, '%Y-%m-%d')
        current_dt = datetime.strptime(current_date, '%Y-%m-%d')
        
        # 근속 개월 수
        months_worked = (current_dt.year - hire_dt.year) * 12 + (current_dt.month - hire_dt.month)
        years_worked = months_worked / 12
        
        # 1년 미만: 월차 (월 1일)
        if years_worked < 1:
            return round(months_worked * (1/12), 1)
        
        # 1년 이상: 기본 15일 + 2년마다 1일 추가
        base_days = 15
        additional_years = int((years_worked - 1) / 2)
        total_days = base_days + additional_years
        
        # 최대 25일
        return min(total_days, 25)
    
    def initialize_employee_leave_balance(self, emp_id: int, hire_date: str, year: int) -> bool:
        """
        직원의 연차 현황 초기화
        
        Args:
            emp_id: 직원 ID
            hire_date: 입사일
            year: 년도
            
        Returns:
            성공 여부
        """
        try:
            self.connect()
            
            # 해당 년도 연차 계산
            annual_days = self.calculate_annual_leave(hire_date, f"{year}-12-31")
            
            self.cursor.execute("""
                INSERT OR REPLACE INTO employee_leave_balance (
                    emp_id, year, total_annual_days, remaining_annual_days
                ) VALUES (?, ?, ?, ?)
            """, (emp_id, year, annual_days, annual_days))
            
            self.conn.commit()
            self.close()
            
            return True
            
        except Exception as e:
            print(f"❌ 연차 초기화 오류: {e}")
            self.close()
            return False
    
    def submit_leave_request(self, request_data: Dict) -> Tuple[bool, Optional[int]]:
        """
        휴가 신청
        
        Args:
            request_data: 휴가 신청 데이터
            
        Returns:
            (성공 여부, 신청 ID)
        """
        try:
            self.connect()
            
            # 휴가 일수 계산
            start_date = datetime.strptime(request_data['start_date'], '%Y-%m-%d')
            end_date = datetime.strptime(request_data['end_date'], '%Y-%m-%d')
            
            # 반차인 경우
            if request_data.get('is_half_day', False):
                total_days = 0.5
            else:
                # 주말 제외 계산
                total_days = 0
                current = start_date
                while current <= end_date:
                    if current.weekday() < 5:  # 월~금
                        total_days += 1
                    current += timedelta(days=1)
            
            # 신청 저장
            self.cursor.execute("""
                INSERT INTO leave_requests (
                    emp_id, leave_type, start_date, end_date, total_days,
                    is_half_day, half_day_period, reason, request_date, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                request_data['emp_id'],
                request_data['leave_type'],
                request_data['start_date'],
                request_data['end_date'],
                total_days,
                1 if request_data.get('is_half_day', False) else 0,
                request_data.get('half_day_period', ''),
                request_data.get('reason', ''),
                datetime.now().strftime('%Y-%m-%d'),
                'PENDING'
            ))
            
            request_id = self.cursor.lastrowid
            self.conn.commit()
            self.close()
            
            return True, request_id
            
        except Exception as e:
            print(f"❌ 휴가 신청 오류: {e}")
            self.close()
            return False, None
    
    def approve_leave_request(self, request_id: int, approver_id: int = None) -> bool:
        """
        휴가 승인
        
        Args:
            request_id: 신청 ID
            approver_id: 승인자 ID
            
        Returns:
            성공 여부
        """
        try:
            self.connect()
            
            # 신청 정보 조회
            self.cursor.execute("""
                SELECT emp_id, leave_type, start_date, end_date, total_days,
                       is_half_day, half_day_period
                FROM leave_requests
                WHERE request_id = ?
            """, (request_id,))
            
            request = self.cursor.fetchone()
            if not request:
                self.close()
                return False
            
            request = dict(request)
            
            # 승인 처리
            self.cursor.execute("""
                UPDATE leave_requests
                SET status = 'APPROVED',
                    approver_id = ?,
                    approved_date = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE request_id = ?
            """, (approver_id, datetime.now().strftime('%Y-%m-%d'), request_id))
            
            # 연차 차감 (연차/반차인 경우)
            if request['leave_type'] in ['ANNUAL', 'HALF_DAY']:
                year = datetime.strptime(request['start_date'], '%Y-%m-%d').year
                
                self.cursor.execute("""
                    UPDATE employee_leave_balance
                    SET used_annual_days = used_annual_days + ?,
                        remaining_annual_days = remaining_annual_days - ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE emp_id = ? AND year = ?
                """, (
                    request['total_days'],
                    request['total_days'],
                    request['emp_id'],
                    year
                ))
            
            # 휴가 사용 이력 생성
            start_date = datetime.strptime(request['start_date'], '%Y-%m-%d')
            end_date = datetime.strptime(request['end_date'], '%Y-%m-%d')
            current = start_date
            
            while current <= end_date:
                if current.weekday() < 5:  # 월~금만
                    days = 0.5 if request['is_half_day'] else 1
                    
                    self.cursor.execute("""
                        INSERT INTO leave_history (
                            emp_id, request_id, leave_date, leave_type, days_used,
                            is_half_day, half_day_period
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        request['emp_id'],
                        request_id,
                        current.strftime('%Y-%m-%d'),
                        request['leave_type'],
                        days,
                        request['is_half_day'],
                        request.get('half_day_period', '')
                    ))
                
                current += timedelta(days=1)
            
            self.conn.commit()
            self.close()
            
            return True
            
        except Exception as e:
            print(f"❌ 휴가 승인 오류: {e}")
            self.close()
            return False
    
    def get_employee_leave_balance(self, emp_id: int, year: int) -> Optional[Dict]:
        """직원 연차 현황 조회"""
        self.connect()
        
        self.cursor.execute("""
            SELECT * FROM employee_leave_balance
            WHERE emp_id = ? AND year = ?
        """, (emp_id, year))
        
        balance = self.cursor.fetchone()
        self.close()
        
        if balance:
            return dict(balance)
        return None
    
    def get_leave_requests(self, emp_id: int = None, status: str = None) -> List[Dict]:
        """휴가 신청 내역 조회"""
        self.connect()
        
        query = "SELECT * FROM leave_requests WHERE 1=1"
        params = []
        
        if emp_id:
            query += " AND emp_id = ?"
            params.append(emp_id)
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        query += " ORDER BY request_date DESC"
        
        self.cursor.execute(query, params)
        
        requests = [dict(row) for row in self.cursor.fetchall()]
        self.close()
        
        return requests


# 테스트 코드
if __name__ == "__main__":
    print("=" * 60)
    print("휴가 관리 모듈 테스트")
    print("=" * 60)
    
    leave_mgr = LeaveManager()
    leave_mgr.initialize_tables()
    
    print("\n✅ 휴가 관리 시스템 준비 완료!")
    
    # 연차 계산 테스트
    print("\n📊 근속년수별 연차 계산:")
    test_dates = [
        ("2024-06-01", "6개월 근무"),
        ("2024-01-01", "1년 근무"),
        ("2022-01-01", "3년 근무"),
        ("2018-01-01", "7년 근무"),
    ]
    
    for hire_date, desc in test_dates:
        days = leave_mgr.calculate_annual_leave(hire_date, "2024-12-31")
        print(f"  - {desc} ({hire_date}): {days}일")
