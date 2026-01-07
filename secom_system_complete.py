"""
세콤(SECOM) 시스템 완전 연동
DB 연결, 데이터 동기화, GUI 포함
"""

import customtkinter as ctk
from tkinter import messagebox, ttk
import pyodbc
import pymysql
import cx_Oracle
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import json

from database_v2 import Database
from config_manager import ConfigManager


class SecomDatabaseConnector:
    """세콤 데이터베이스 연결 관리"""
    
    PROVIDERS = {
        'MS-SQL': 'mssql',
        'ORACLE': 'oracle',
        'ODBC': 'odbc',
        'MYSQL': 'mysql',
        'WhoIs': 'whois'
    }
    
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.provider = None
        self.config = {}
    
    def connect(self, provider: str, server_ip: str, port: str, 
                database: str, user: str, password: str) -> tuple:
        """세콤 DB 연결"""
        try:
            self.provider = provider
            self.config = {
                'server_ip': server_ip,
                'port': port,
                'database': database,
                'user': user,
                'password': password
            }
            
            if provider == 'MS-SQL':
                return self._connect_mssql(server_ip, port, database, user, password)
            elif provider == 'MYSQL':
                return self._connect_mysql(server_ip, port, database, user, password)
            elif provider == 'ORACLE':
                return self._connect_oracle(server_ip, port, database, user, password)
            elif provider == 'ODBC':
                return self._connect_odbc(database, user, password)
            else:
                return False, f"지원하지 않는 Provider: {provider}"
        
        except Exception as e:
            return False, f"연결 실패: {e}"
    
    def _connect_mssql(self, server_ip: str, port: str, database: str, 
                       user: str, password: str) -> tuple:
        """MS-SQL 연결"""
        try:
            # 연결 문자열 구성
            if port:
                server = f"{server_ip},{port}"
            else:
                server = server_ip
            
            conn_str = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={server};"
                f"DATABASE={database};"
                f"UID={user};"
                f"PWD={password}"
            )
            
            self.connection = pyodbc.connect(conn_str, timeout=10)
            self.cursor = self.connection.cursor()
            
            return True, "MS-SQL 연결 성공"
        
        except pyodbc.Error as e:
            return False, f"MS-SQL 연결 실패: {e}"
    
    def _connect_mysql(self, server_ip: str, port: str, database: str,
                       user: str, password: str) -> tuple:
        """MySQL 연결"""
        try:
            self.connection = pymysql.connect(
                host=server_ip,
                port=int(port) if port else 3306,
                database=database,
                user=user,
                password=password,
                charset='utf8mb4',
                connect_timeout=10
            )
            self.cursor = self.connection.cursor()
            
            return True, "MySQL 연결 성공"
        
        except pymysql.Error as e:
            return False, f"MySQL 연결 실패: {e}"
    
    def _connect_oracle(self, server_ip: str, port: str, database: str,
                        user: str, password: str) -> tuple:
        """Oracle 연결"""
        try:
            # DSN 구성
            dsn = cx_Oracle.makedsn(
                server_ip,
                port if port else '1521',
                service_name=database
            )
            
            self.connection = cx_Oracle.connect(
                user=user,
                password=password,
                dsn=dsn
            )
            self.cursor = self.connection.cursor()
            
            return True, "Oracle 연결 성공"
        
        except cx_Oracle.Error as e:
            return False, f"Oracle 연결 실패: {e}"
    
    def _connect_odbc(self, dsn: str, user: str, password: str) -> tuple:
        """ODBC 연결"""
        try:
            conn_str = f"DSN={dsn};UID={user};PWD={password}"
            self.connection = pyodbc.connect(conn_str, timeout=10)
            self.cursor = self.connection.cursor()
            
            return True, "ODBC 연결 성공"
        
        except pyodbc.Error as e:
            return False, f"ODBC 연결 실패: {e}"
    
    def test_connection(self) -> tuple:
        """연결 테스트"""
        if not self.connection:
            return False, "연결되지 않음"
        
        try:
            if self.provider == 'MS-SQL' or self.provider == 'ODBC':
                self.cursor.execute("SELECT 1")
            elif self.provider == 'MYSQL':
                self.cursor.execute("SELECT 1")
            elif self.provider == 'ORACLE':
                self.cursor.execute("SELECT 1 FROM DUAL")
            
            result = self.cursor.fetchone()
            return True, "연결 정상"
        
        except Exception as e:
            return False, f"연결 테스트 실패: {e}"
    
    def execute_query(self, query: str) -> tuple:
        """쿼리 실행"""
        try:
            self.cursor.execute(query)
            
            # SELECT 쿼리인 경우
            if query.strip().upper().startswith('SELECT'):
                columns = [desc[0] for desc in self.cursor.description]
                rows = self.cursor.fetchall()
                
                # 딕셔너리 리스트로 변환
                results = []
                for row in rows:
                    results.append(dict(zip(columns, row)))
                
                return True, results
            else:
                # INSERT, UPDATE, DELETE
                self.connection.commit()
                return True, f"{self.cursor.rowcount}행 영향받음"
        
        except Exception as e:
            return False, f"쿼리 실행 실패: {e}"
    
    def disconnect(self):
        """연결 종료"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        
        self.connection = None
        self.cursor = None


class SecomDataSync:
    """세콤 데이터 동기화"""
    
    def __init__(self, secom_db: SecomDatabaseConnector, erp_db: Database):
        self.secom_db = secom_db
        self.erp_db = erp_db
        self.sync_log = []
    
    def sync_attendance(self, start_date: str, end_date: str, 
                       custom_query: Optional[str] = None) -> tuple:
        """근태 데이터 동기화"""
        try:
            # 기본 쿼리 또는 사용자 쿼리
            if custom_query:
                query = custom_query
            else:
                # 기본 근태 쿼리 (세콤 표준)
                query = f"""
                    SELECT 
                        emp_code,
                        work_date,
                        clock_in,
                        clock_out,
                        work_type
                    FROM attendance_log
                    WHERE work_date BETWEEN '{start_date}' AND '{end_date}'
                    ORDER BY work_date, emp_code
                """
            
            # 세콤 DB에서 데이터 조회
            success, result = self.secom_db.execute_query(query)
            
            if not success:
                return False, result
            
            if not result:
                return True, "동기화할 데이터가 없습니다"
            
            # ERP DB로 데이터 삽입
            sync_count = 0
            error_count = 0
            
            for row in result:
                try:
                    # 직원 조회 (세콤 직원코드로)
                    self.erp_db.connect()
                    self.erp_db.cursor.execute("""
                        SELECT emp_id FROM employees 
                        WHERE secom_employee_id = ? OR emp_code = ?
                    """, (row.get('emp_code'), row.get('emp_code')))
                    
                    emp_result = self.erp_db.cursor.fetchone()
                    
                    if not emp_result:
                        self.sync_log.append(f"❌ 직원 없음: {row.get('emp_code')}")
                        error_count += 1
                        continue
                    
                    emp_id = emp_result['emp_id']
                    
                    # 근태 데이터 구성
                    attendance_data = {
                        'emp_id': emp_id,
                        'work_date': row.get('work_date'),
                        'clock_in': row.get('clock_in'),
                        'clock_out': row.get('clock_out'),
                        'attendance_type': 'normal'
                    }
                    
                    # 중복 체크
                    self.erp_db.cursor.execute("""
                        SELECT COUNT(*) as cnt FROM attendance
                        WHERE emp_id = ? AND work_date = ?
                    """, (emp_id, row.get('work_date')))
                    
                    exists = self.erp_db.cursor.fetchone()['cnt'] > 0
                    
                    if exists:
                        # 업데이트
                        self.erp_db.cursor.execute("""
                            UPDATE attendance
                            SET clock_in = ?, clock_out = ?
                            WHERE emp_id = ? AND work_date = ?
                        """, (row.get('clock_in'), row.get('clock_out'),
                              emp_id, row.get('work_date')))
                    else:
                        # 삽입
                        self.erp_db.add_attendance(attendance_data)
                    
                    sync_count += 1
                    self.sync_log.append(
                        f"✅ {row.get('emp_code')} - {row.get('work_date')}"
                    )
                
                except Exception as e:
                    error_count += 1
                    self.sync_log.append(f"❌ 오류: {e}")
                
                finally:
                    self.erp_db.close()
            
            # 결과 반환
            msg = f"동기화 완료!\n성공: {sync_count}건\n실패: {error_count}건"
            return True, msg
        
        except Exception as e:
            return False, f"동기화 실패: {e}"
    
    def get_sync_log(self) -> List[str]:
        """동기화 로그 반환"""
        return self.sync_log
    
    def clear_log(self):
        """로그 초기화"""
        self.sync_log = []


class SecomIntegrationFrame(ctk.CTkFrame):
    """세콤 연동 GUI"""
    
    def __init__(self, parent, erp_db: Database):
        super().__init__(parent)
        
        self.erp_db = erp_db
        self.secom_connector = SecomDatabaseConnector()
        self.secom_sync = SecomDataSync(self.secom_connector, erp_db)
        
        self.create_widgets()
    
    def create_widgets(self):
        """위젯 생성"""
        # 제목
        ctk.CTkLabel(
            self,
            text="🔄 세콤 시스템 연동",
            font=ctk.CTkFont(size=32, weight="bold")
        ).pack(pady=25, padx=35, anchor="w")
        
        # 탭뷰
        tabview = ctk.CTkTabview(self)
        tabview.pack(fill="both", expand=True, padx=35, pady=(0, 25))
        
        # 탭 생성
        tabview.add("ERP 서버설정")
        tabview.add("사용 전송설정")
        tabview.add("동기화")
        
        # 각 탭 구성
        self.create_server_settings_tab(tabview.tab("ERP 서버설정"))
        self.create_sync_settings_tab(tabview.tab("사용 전송설정"))
        self.create_sync_tab(tabview.tab("동기화"))
    
    def create_server_settings_tab(self, parent):
        """서버 설정 탭"""
        # 좌우 분할
        left_frame = ctk.CTkFrame(parent)
        left_frame.pack(side="left", fill="both", expand=True, padx=(10, 5), pady=10)
        
        right_frame = ctk.CTkFrame(parent)
        right_frame.pack(side="right", fill="both", expand=True, padx=(5, 10), pady=10)
        
        # === 좌측: ERP 서버설정 ===
        ctk.CTkLabel(
            left_frame,
            text="ERP 서버설정",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(15, 10), padx=20, anchor="w")
        
        # Provider
        self.create_field(left_frame, "Provider", 0)
        self.provider_combo = ctk.CTkComboBox(
            left_frame,
            values=list(SecomDatabaseConnector.PROVIDERS.keys()),
            width=300,
            state="readonly"
        )
        self.provider_combo.set("MS-SQL")
        self.provider_combo.pack(padx=20, pady=5)
        
        # SERVER IP
        self.create_field(left_frame, "SERVER IP", 1)
        self.server_ip_entry = ctk.CTkEntry(left_frame, width=300, placeholder_text="127.0.0.1")
        self.server_ip_entry.pack(padx=20, pady=5)
        
        # PORT
        self.create_field(left_frame, "PORT", 2)
        self.port_entry = ctk.CTkEntry(left_frame, width=300, placeholder_text="1433")
        self.port_entry.pack(padx=20, pady=5)
        
        # DB명.dbo
        self.create_field(left_frame, "DB명.dbo", 3)
        self.database_entry = ctk.CTkEntry(left_frame, width=300, placeholder_text="SECOM.dbo")
        self.database_entry.pack(padx=20, pady=5)
        
        # USER
        self.create_field(left_frame, "USER", 4)
        self.user_entry = ctk.CTkEntry(left_frame, width=300)
        self.user_entry.pack(padx=20, pady=5)
        
        # PASSWORD
        self.create_field(left_frame, "PASSWORD", 5)
        self.password_entry = ctk.CTkEntry(left_frame, width=300, show="*")
        self.password_entry.pack(padx=20, pady=5)
        
        # 접속확인 버튼
        ctk.CTkButton(
            left_frame,
            text="접속확인",
            command=self.test_connection,
            height=40,
            width=300
        ).pack(padx=20, pady=20)
        
        # === 우측: ERP 데이터 설정 ===
        ctk.CTkLabel(
            right_frame,
            text="ERP 데이터 근태(시설관리)설정",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(15, 10), padx=20, anchor="w")
        
        # 체크박스 옵션들
        options_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        options_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.galman_var = ctk.BooleanVar(value=True)
        self.geuntae_var = ctk.BooleanVar(value=True)
        self.siksa_var = ctk.BooleanVar()
        self.sawon_var = ctk.BooleanVar()
        
        ctk.CTkCheckBox(options_frame, text="갈망", variable=self.galman_var).pack(anchor="w", pady=5)
        ctk.CTkCheckBox(options_frame, text="근태", variable=self.geuntae_var).pack(anchor="w", pady=5)
        ctk.CTkCheckBox(options_frame, text="식사", variable=self.siksa_var).pack(anchor="w", pady=5)
        ctk.CTkCheckBox(options_frame, text="사원", variable=self.sawon_var).pack(anchor="w", pady=5)
        
        # 근태(시설관리)
        self.geuntae_facility_var = ctk.BooleanVar(value=True)
        self.sawon_facility_var = ctk.BooleanVar()
        
        ctk.CTkCheckBox(options_frame, text="근태(시설관리)", 
                       variable=self.geuntae_facility_var).pack(anchor="w", pady=5)
        ctk.CTkCheckBox(options_frame, text="사원(시설관리)", 
                       variable=self.sawon_facility_var).pack(anchor="w", pady=5)
        
        # 테이블 생성 버튼
        ctk.CTkButton(
            right_frame,
            text="테이블 생성",
            command=self.create_tables,
            height=40,
            width=200
        ).pack(padx=20, pady=20)
    
    def create_sync_settings_tab(self, parent):
        """전송 설정 탭"""
        settings_frame = ctk.CTkFrame(parent)
        settings_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 수동 전송
        ctk.CTkLabel(
            settings_frame,
            text="수동 전송",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(15, 10), anchor="w", padx=20)
        
        # 최종 전송 시각
        ctk.CTkLabel(settings_frame, text="최종 전송 시각", 
                    font=ctk.CTkFont(size=14)).pack(pady=5, anchor="w", padx=20)
        self.last_sync_label = ctk.CTkLabel(
            settings_frame,
            text="동기화 이력 없음",
            font=ctk.CTkFont(size=14),
            text_color=("gray50", "gray60")
        )
        self.last_sync_label.pack(pady=5, anchor="w", padx=40)
        
        # 시작일자
        date_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        date_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(date_frame, text="시작일자:", width=100).pack(side="left")
        self.start_date_entry = ctk.CTkEntry(date_frame, width=200, 
                                             placeholder_text="2026-01-01")
        self.start_date_entry.insert(0, datetime.now().strftime("%Y-%m-01"))
        self.start_date_entry.pack(side="left", padx=10)
        
        # 종료일자
        date_frame2 = ctk.CTkFrame(settings_frame, fg_color="transparent")
        date_frame2.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(date_frame2, text="종료일자:", width=100).pack(side="left")
        self.end_date_entry = ctk.CTkEntry(date_frame2, width=200,
                                           placeholder_text="2026-01-31")
        self.end_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.end_date_entry.pack(side="left", padx=10)
        
        # 사용자 쿼리
        ctk.CTkLabel(
            settings_frame,
            text="사용자 쿼리 (선택사항)",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(20, 5), anchor="w", padx=20)
        
        self.custom_query_text = ctk.CTkTextbox(settings_frame, height=150)
        self.custom_query_text.pack(fill="x", padx=20, pady=10)
        self.custom_query_text.insert("1.0", 
            "-- 예시 쿼리\n"
            "SELECT emp_code, work_date, clock_in, clock_out\n"
            "FROM attendance_log\n"
            "WHERE work_date BETWEEN '2026-01-01' AND '2026-01-31'"
        )
    
    def create_sync_tab(self, parent):
        """동기화 탭"""
        sync_frame = ctk.CTkFrame(parent)
        sync_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 동기화 버튼
        btn_frame = ctk.CTkFrame(sync_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=20)
        
        ctk.CTkButton(
            btn_frame,
            text="🔄 근태 데이터 동기화",
            command=self.sync_attendance,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=("green", "darkgreen")
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            btn_frame,
            text="🗑️ 로그 초기화",
            command=self.clear_log,
            height=50,
            width=150
        ).pack(side="left", padx=10)
        
        # 로그 표시
        ctk.CTkLabel(
            sync_frame,
            text="📋 동기화 로그",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10, anchor="w")
        
        self.log_text = ctk.CTkTextbox(sync_frame, height=400)
        self.log_text.pack(fill="both", expand=True, pady=(0, 10))
    
    def create_field(self, parent, label: str, row: int):
        """필드 라벨 생성"""
        ctk.CTkLabel(
            parent,
            text=label,
            font=ctk.CTkFont(size=14)
        ).pack(pady=(10, 0), padx=20, anchor="w")
    
    def test_connection(self):
        """접속 테스트"""
        provider = self.provider_combo.get()
        server_ip = self.server_ip_entry.get()
        port = self.port_entry.get()
        database = self.database_entry.get()
        user = self.user_entry.get()
        password = self.password_entry.get()
        
        if not all([server_ip, database, user, password]):
            messagebox.showwarning("경고", "필수 항목을 모두 입력하세요")
            return
        
        # 연결 시도
        success, message = self.secom_connector.connect(
            provider, server_ip, port, database, user, password
        )
        
        if success:
            # 연결 테스트
            test_success, test_message = self.secom_connector.test_connection()
            
            if test_success:
                messagebox.showinfo("성공", f"✅ {message}\n✅ {test_message}")
            else:
                messagebox.showerror("오류", f"✅ {message}\n❌ {test_message}")
        else:
            messagebox.showerror("오류", message)
    
    def create_tables(self):
        """테이블 생성"""
        messagebox.showinfo("안내", "테이블 생성 기능은 세콤 시스템에서 자동으로 관리됩니다")
    
    def sync_attendance(self):
        """근태 동기화 실행"""
        # 연결 확인
        if not self.secom_connector.connection:
            messagebox.showwarning("경고", "먼저 세콤 서버에 접속하세요")
            return
        
        # 날짜 확인
        start_date = self.start_date_entry.get()
        end_date = self.end_date_entry.get()
        
        if not start_date or not end_date:
            messagebox.showwarning("경고", "시작일자와 종료일자를 입력하세요")
            return
        
        # 사용자 쿼리
        custom_query = self.custom_query_text.get("1.0", "end-1c").strip()
        if custom_query.startswith("--"):
            custom_query = None
        
        # 동기화 실행
        self.log_text.delete("1.0", "end")
        self.log_text.insert("1.0", f"🔄 동기화 시작...\n기간: {start_date} ~ {end_date}\n\n")
        
        success, message = self.secom_sync.sync_attendance(
            start_date, end_date, custom_query
        )
        
        if success:
            # 로그 표시
            logs = self.secom_sync.get_sync_log()
            for log in logs:
                self.log_text.insert("end", f"{log}\n")
            
            self.log_text.insert("end", f"\n{message}")
            
            # 최종 전송 시각 업데이트
            self.last_sync_label.configure(
                text=f"{datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')}"
            )
            
            messagebox.showinfo("성공", message)
        else:
            self.log_text.insert("end", f"❌ {message}")
            messagebox.showerror("오류", message)
    
    def clear_log(self):
        """로그 초기화"""
        self.secom_sync.clear_log()
        self.log_text.delete("1.0", "end")
        self.log_text.insert("1.0", "로그가 초기화되었습니다.\n")
