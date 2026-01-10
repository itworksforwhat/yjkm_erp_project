"""
데이터베이스 관리 모듈 v2.0
전문가급 ERP를 위한 개선된 데이터베이스 구조
"""

import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import json

class Database:
    """
    SQLite 데이터베이스 관리 클래스
    근무 형태별 관리, 세콤 연동, 영구 데이터 저장
    """
    
    def __init__(self, db_path: str = "payroll.db"):
        """
        데이터베이스 초기화
        
        Args:
            db_path: 데이터베이스 파일 경로
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """데이터베이스 연결"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Dict 형태로 결과 반환
        self.cursor = self.conn.cursor()
        
    def close(self):
        """데이터베이스 연결 종료"""
        if self.conn:
            self.conn.close()
            
    def create_tables(self):
        """
        모든 테이블 생성
        """
        self.connect()
        
        # 1. 직원 정보 테이블 (근무 형태 추가)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                emp_id INTEGER PRIMARY KEY AUTOINCREMENT,
                emp_code TEXT UNIQUE NOT NULL,              -- 직원 코드
                name TEXT NOT NULL,                          -- 이름
                department TEXT,                             -- 부서
                position TEXT,                               -- 직급
                hire_date TEXT NOT NULL,                     -- 입사일
                resignation_date TEXT,                       -- 퇴사일
                
                -- 급여 정보
                hourly_wage REAL NOT NULL,                   -- 시급
                work_schedule_id TEXT DEFAULT 'DAY_SHIFT',   -- 근무 형태 (FK)
                
                -- 개인 정보
                phone TEXT,
                email TEXT,
                address TEXT,
                
                -- 은행 정보
                bank_name TEXT,
                account_number TEXT,
                
                -- 세콤 정보
                secom_employee_id TEXT,                      -- 세콤 직원 ID
                secom_card_number TEXT,                      -- 세콤 카드 번호
                
                -- 기타
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (work_schedule_id) REFERENCES work_schedules(schedule_id)
            )
        """)
        
        # 2. 근태 기록 테이블 (세콤 연동 정보 추가)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
                emp_id INTEGER NOT NULL,
                work_date TEXT NOT NULL,
                
                -- 출퇴근 시간
                clock_in TEXT,                               -- 출근 시간 (HH:MM)
                clock_out TEXT,                              -- 퇴근 시간 (HH:MM)
                actual_clock_in TEXT,                        -- 실제 출근 시간 (세콤)
                actual_clock_out TEXT,                       -- 실제 퇴근 시간 (세콤)
                
                -- 근무 시간 (자동 계산)
                work_hours REAL DEFAULT 0,                   -- 총 근무 시간
                regular_hours REAL DEFAULT 0,                -- 정규 근무 시간
                break_hours REAL DEFAULT 0,                  -- 휴게 시간
                overtime_hours REAL DEFAULT 0,               -- 잔업 시간 (총합)
                night_hours REAL DEFAULT 0,                  -- 야간 근무 시간
                holiday_hours REAL DEFAULT 0,                -- 휴일 근무 시간
                
                -- 잔업 시간대별 분류 (분 단위로 저장)
                overtime_tier1_minutes REAL DEFAULT 0,       -- 1구간 잔업 시간
                overtime_tier2_minutes REAL DEFAULT 0,       -- 2구간 잔업 시간
                overtime_tier3_minutes REAL DEFAULT 0,       -- 3구간 잔업 시간
                
                -- 근무 유형
                is_holiday INTEGER DEFAULT 0,                -- 휴일 여부
                work_schedule_id TEXT,                       -- 해당일 근무 형태
                attendance_type TEXT DEFAULT 'normal',       -- 근태 유형 (normal, leave, absent, halfday)
                
                -- 세콤 연동
                secom_sync INTEGER DEFAULT 0,                -- 세콤 동기화 여부
                secom_sync_time TEXT,                        -- 세콤 동기화 시간
                secom_raw_data TEXT,                         -- 세콤 원본 데이터 (JSON)
                
                -- 기타
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (emp_id) REFERENCES employees(emp_id),
                FOREIGN KEY (work_schedule_id) REFERENCES work_schedules(schedule_id),
                UNIQUE(emp_id, work_date)
            )
        """)
        
        # 3. 식대 기록 테이블
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS meal_allowance (
                meal_id INTEGER PRIMARY KEY AUTOINCREMENT,
                emp_id INTEGER NOT NULL,
                meal_date TEXT NOT NULL,
                meal_type TEXT DEFAULT 'lunch',              -- breakfast, lunch, dinner
                amount REAL NOT NULL,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (emp_id) REFERENCES employees(emp_id)
            )
        """)
        
        # 4. 급여 대장 테이블
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS payroll (
                payroll_id INTEGER PRIMARY KEY AUTOINCREMENT,
                emp_id INTEGER NOT NULL,
                pay_year INTEGER NOT NULL,
                pay_month INTEGER NOT NULL,
                
                -- 근무 시간
                total_work_days REAL DEFAULT 0,
                regular_hours REAL DEFAULT 0,
                overtime_hours REAL DEFAULT 0,               -- 총 잔업 시간
                night_hours REAL DEFAULT 0,
                holiday_hours REAL DEFAULT 0,
                
                -- 잔업 시간대별
                overtime_tier1_minutes REAL DEFAULT 0,
                overtime_tier2_minutes REAL DEFAULT 0,
                overtime_tier3_minutes REAL DEFAULT 0,
                
                -- 지급 항목
                base_pay REAL DEFAULT 0,                     -- 기본급
                overtime_pay REAL DEFAULT 0,                 -- 잔업 수당 (차등 적용)
                night_pay REAL DEFAULT 0,                    -- 야간 수당
                holiday_pay REAL DEFAULT 0,                  -- 휴일 수당
                weekly_holiday_pay REAL DEFAULT 0,           -- 주휴수당
                meal_allowance REAL DEFAULT 0,               -- 식대
                other_allowance REAL DEFAULT 0,              -- 기타 수당
                total_pay REAL DEFAULT 0,                    -- 총 지급액
                
                -- 공제 항목
                national_pension REAL DEFAULT 0,
                health_insurance REAL DEFAULT 0,
                long_term_care REAL DEFAULT 0,
                employment_insurance REAL DEFAULT 0,
                income_tax REAL DEFAULT 0,
                local_tax REAL DEFAULT 0,
                other_deduction REAL DEFAULT 0,
                total_deduction REAL DEFAULT 0,
                
                -- 실지급액
                net_pay REAL DEFAULT 0,
                
                -- 상태
                payment_date TEXT,
                payment_status TEXT DEFAULT 'pending',       -- pending, paid, cancelled
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (emp_id) REFERENCES employees(emp_id),
                UNIQUE(emp_id, pay_year, pay_month)
            )
        """)
        
        # 5. 세콤 동기화 로그 테이블
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS secom_sync_log (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                sync_date TEXT NOT NULL,
                sync_time TEXT NOT NULL,
                sync_type TEXT DEFAULT 'auto',               -- auto, manual
                total_records INTEGER DEFAULT 0,
                success_count INTEGER DEFAULT 0,
                error_count INTEGER DEFAULT 0,
                error_details TEXT,                          -- JSON 형태의 오류 상세
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 인덱스 생성 (성능 향상)
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_attendance_date 
            ON attendance(work_date)
        """)
        
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_attendance_emp_date 
            ON attendance(emp_id, work_date)
        """)
        
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_payroll_year_month 
            ON payroll(pay_year, pay_month)
        """)
        
        self.conn.commit()
        self.close()
        
        print("✅ 데이터베이스 테이블 생성 완료")
    
    # ========== 직원 관리 ==========
    
    def add_employee(self, emp_data: Dict) -> Tuple[bool, Optional[int]]:
        """
        직원 추가
        
        Args:
            emp_data: 직원 정보 딕셔너리
            
        Returns:
            (성공 여부, 직원 ID)
        """
        try:
            self.connect()
            
            self.cursor.execute("""
                INSERT INTO employees (
                    emp_code, name, department, position, hire_date,
                    hourly_wage, work_schedule_id,
                    phone, email, address,
                    bank_name, account_number,
                    secom_employee_id, secom_card_number,
                    notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                emp_data.get('emp_code'),
                emp_data.get('name'),
                emp_data.get('department', ''),
                emp_data.get('position', ''),
                emp_data.get('hire_date'),
                emp_data.get('hourly_wage'),
                emp_data.get('work_schedule_id', 'DAY_SHIFT'),
                emp_data.get('phone', ''),
                emp_data.get('email', ''),
                emp_data.get('address', ''),
                emp_data.get('bank_name', ''),
                emp_data.get('account_number', ''),
                emp_data.get('secom_employee_id', ''),
                emp_data.get('secom_card_number', ''),
                emp_data.get('notes', '')
            ))
            
            emp_id = self.cursor.lastrowid
            self.conn.commit()
            self.close()
            
            return True, emp_id
            
        except Exception as e:
            print(f"❌ 직원 추가 오류: {e}")
            self.close()
            return False, None
    
    def get_employee(self, emp_id: int) -> Optional[Dict]:
        """직원 정보 조회"""
        self.connect()
        
        self.cursor.execute("""
            SELECT * FROM employees WHERE emp_id = ?
        """, (emp_id,))
        
        row = self.cursor.fetchone()
        self.close()
        
        if row:
            return dict(row)
        return None
    
    def get_all_employees(self, include_resigned: bool = False) -> List[Dict]:
        """모든 직원 조회"""
        self.connect()
        
        if include_resigned:
            query = "SELECT * FROM employees ORDER BY emp_code"
        else:
            query = "SELECT * FROM employees WHERE resignation_date IS NULL ORDER BY emp_code"
        
        self.cursor.execute(query)
        
        employees = [dict(row) for row in self.cursor.fetchall()]
        self.close()
        
        return employees
    
    def update_employee(self, emp_id: int, emp_data: Dict) -> bool:
        """직원 정보 수정"""
        try:
            self.connect()
            
            # 동적 쿼리 생성
            update_fields = []
            values = []
            
            for key, value in emp_data.items():
                if key != 'emp_id':
                    update_fields.append(f"{key} = ?")
                    values.append(value)
            
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            values.append(emp_id)
            
            query = f"""
                UPDATE employees 
                SET {', '.join(update_fields)}
                WHERE emp_id = ?
            """
            
            self.cursor.execute(query, values)
            self.conn.commit()
            self.close()
            
            return True
            
        except Exception as e:
            print(f"❌ 직원 수정 오류: {e}")
            self.close()
            return False
    
    # ========== 근태 관리 ==========
    
    def add_attendance(self, attendance_data: Dict) -> Tuple[bool, Optional[int]]:
        """근태 기록 추가"""
        try:
            self.connect()
            
            self.cursor.execute("""
                INSERT OR REPLACE INTO attendance (
                    emp_id, work_date, clock_in, clock_out,
                    actual_clock_in, actual_clock_out,
                    work_hours, regular_hours, break_hours, overtime_hours,
                    night_hours, holiday_hours,
                    overtime_tier1_minutes, overtime_tier2_minutes, overtime_tier3_minutes,
                    is_holiday, work_schedule_id, attendance_type,
                    secom_sync, secom_sync_time, secom_raw_data,
                    notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                attendance_data.get('emp_id'),
                attendance_data.get('work_date'),
                attendance_data.get('clock_in', ''),
                attendance_data.get('clock_out', ''),
                attendance_data.get('actual_clock_in', ''),
                attendance_data.get('actual_clock_out', ''),
                attendance_data.get('work_hours', 0),
                attendance_data.get('regular_hours', 0),
                attendance_data.get('break_hours', 0),
                attendance_data.get('overtime_hours', 0),
                attendance_data.get('night_hours', 0),
                attendance_data.get('holiday_hours', 0),
                attendance_data.get('overtime_tier1_minutes', 0),
                attendance_data.get('overtime_tier2_minutes', 0),
                attendance_data.get('overtime_tier3_minutes', 0),
                attendance_data.get('is_holiday', 0),
                attendance_data.get('work_schedule_id', 'DAY_SHIFT'),
                attendance_data.get('attendance_type', 'normal'),
                attendance_data.get('secom_sync', 0),
                attendance_data.get('secom_sync_time', ''),
                attendance_data.get('secom_raw_data', ''),
                attendance_data.get('notes', '')
            ))
            
            att_id = self.cursor.lastrowid
            self.conn.commit()
            self.close()
            
            return True, att_id
            
        except Exception as e:
            print(f"❌ 근태 추가 오류: {e}")
            self.close()
            return False, None
    
    def get_attendance_by_date_range(self, emp_id: int, start_date: str, end_date: str) -> List[Dict]:
        """기간별 근태 조회"""
        self.connect()
        
        self.cursor.execute("""
            SELECT * FROM attendance
            WHERE emp_id = ?
            AND work_date BETWEEN ? AND ?
            ORDER BY work_date
        """, (emp_id, start_date, end_date))
        
        records = [dict(row) for row in self.cursor.fetchall()]
        self.close()
        
        return records
    
    # ========== 급여 관리 ==========
    
    def save_payroll(self, payroll_data: Dict) -> bool:
        """급여 데이터 저장"""
        try:
            self.connect()
            
            self.cursor.execute("""
                INSERT OR REPLACE INTO payroll (
                    emp_id, pay_year, pay_month,
                    total_work_days, regular_hours, overtime_hours, night_hours, holiday_hours,
                    overtime_tier1_minutes, overtime_tier2_minutes, overtime_tier3_minutes,
                    base_pay, overtime_pay, night_pay, holiday_pay, weekly_holiday_pay,
                    meal_allowance, other_allowance, total_pay,
                    national_pension, health_insurance, long_term_care, employment_insurance,
                    income_tax, local_tax, other_deduction, total_deduction,
                    net_pay, payment_status, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                payroll_data.get('emp_id'),
                payroll_data.get('pay_year'),
                payroll_data.get('pay_month'),
                payroll_data.get('total_work_days', 0),
                payroll_data.get('regular_hours', 0),
                payroll_data.get('overtime_hours', 0),
                payroll_data.get('night_hours', 0),
                payroll_data.get('holiday_hours', 0),
                payroll_data.get('overtime_tier1_minutes', 0),
                payroll_data.get('overtime_tier2_minutes', 0),
                payroll_data.get('overtime_tier3_minutes', 0),
                payroll_data.get('base_pay', 0),
                payroll_data.get('overtime_pay', 0),
                payroll_data.get('night_pay', 0),
                payroll_data.get('holiday_pay', 0),
                payroll_data.get('weekly_holiday_pay', 0),
                payroll_data.get('meal_allowance', 0),
                payroll_data.get('other_allowance', 0),
                payroll_data.get('total_pay', 0),
                payroll_data.get('national_pension', 0),
                payroll_data.get('health_insurance', 0),
                payroll_data.get('long_term_care', 0),
                payroll_data.get('employment_insurance', 0),
                payroll_data.get('income_tax', 0),
                payroll_data.get('local_tax', 0),
                payroll_data.get('other_deduction', 0),
                payroll_data.get('total_deduction', 0),
                payroll_data.get('net_pay', 0),
                payroll_data.get('payment_status', 'pending'),
                payroll_data.get('notes', '')
            ))
            
            self.conn.commit()
            self.close()
            return True
            
        except Exception as e:
            print(f"❌ 급여 저장 오류: {e}")
            self.close()
            return False
    
    def get_payroll(self, emp_id: int, year: int, month: int) -> Optional[Dict]:
        """급여 정보 조회"""
        self.connect()
        
        self.cursor.execute("""
            SELECT * FROM payroll
            WHERE emp_id = ? AND pay_year = ? AND pay_month = ?
        """, (emp_id, year, month))
        
        row = self.cursor.fetchone()
        self.close()
        
        if row:
            return dict(row)
        return None
    
    # ========== 세콤 동기화 로그 ==========
    
    def add_secom_sync_log(self, log_data: Dict) -> bool:
        """세콤 동기화 로그 추가"""
        try:
            self.connect()
            
            self.cursor.execute("""
                INSERT INTO secom_sync_log (
                    sync_date, sync_time, sync_type,
                    total_records, success_count, error_count, error_details
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                log_data.get('sync_date'),
                log_data.get('sync_time'),
                log_data.get('sync_type', 'auto'),
                log_data.get('total_records', 0),
                log_data.get('success_count', 0),
                log_data.get('error_count', 0),
                log_data.get('error_details', '')
            ))
            
            self.conn.commit()
            self.close()
            return True
            
        except Exception as e:
            print(f"❌ 로그 저장 오류: {e}")
            self.close()
            return False
    
    def backup_database(self, backup_path: Optional[str] = None) -> str:
        """데이터베이스 백업"""
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"payroll_backup_{timestamp}.db"
        
        import shutil
        shutil.copy2(self.db_path, backup_path)
        print(f"✅ 데이터베이스 백업 완료: {backup_path}")
        return backup_path


# 테스트 코드
if __name__ == "__main__":
    print("=" * 60)
    print("데이터베이스 모듈 v2.0 테스트")
    print("=" * 60)
    
    db = Database()
    db.create_tables()
    
    print("\n✅ 데이터베이스 준비 완료!")
