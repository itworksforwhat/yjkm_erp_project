"""
근태 및 휴가 목록 화면
조회, 수정, 삭제 기능 포함
"""

import customtkinter as ctk
from tkinter import messagebox, ttk
from datetime import datetime, timedelta
from database_v2 import Database
from payroll_calculator_v2 import AdvancedPayrollCalculator
from leave_manager import LeaveManager


class AttendanceListFrame(ctk.CTkFrame):
    """근태 목록 화면"""
    
    def __init__(self, parent, db: Database, calculator: AdvancedPayrollCalculator):
        super().__init__(parent)
        self.db = db
        self.calculator = calculator
        self.create_widgets()
    
    def create_widgets(self):
        """위젯 생성"""
        # 제목
        title = ctk.CTkLabel(
            self,
            text="⏰ 근태 목록",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title.pack(pady=(25, 15), padx=35, anchor="w")
        
        # 필터 영역
        filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        filter_frame.pack(fill="x", padx=35, pady=(0, 15))
        
        # 직원 선택
        ctk.CTkLabel(
            filter_frame,
            text="직원:",
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=(0, 10))
        
        employees = self.db.get_all_employees()
        emp_list = ["전체"] + [f"{e['emp_code']} - {e['name']}" for e in employees]
        
        self.emp_combo = ctk.CTkComboBox(
            filter_frame,
            values=emp_list,
            width=200,
            state="readonly"
        )
        self.emp_combo.set("전체")
        self.emp_combo.pack(side="left", padx=5)
        
        # 기간 선택
        ctk.CTkLabel(
            filter_frame,
            text="기간:",
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=(20, 10))
        
        # 시작일
        self.start_entry = ctk.CTkEntry(filter_frame, width=120, placeholder_text="YYYY-MM-DD")
        self.start_entry.insert(0, datetime.now().strftime("%Y-%m-01"))
        self.start_entry.pack(side="left", padx=5)
        
        ctk.CTkLabel(filter_frame, text="~").pack(side="left", padx=5)
        
        # 종료일
        self.end_entry = ctk.CTkEntry(filter_frame, width=120, placeholder_text="YYYY-MM-DD")
        self.end_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.end_entry.pack(side="left", padx=5)
        
        # 검색 버튼
        search_btn = ctk.CTkButton(
            filter_frame,
            text="🔍 검색",
            command=self.search,
            width=100,
            height=35
        )
        search_btn.pack(side="left", padx=(10, 0))
        
        # 목록 테이블
        list_frame = ctk.CTkFrame(self)
        list_frame.pack(fill="both", expand=True, padx=35, pady=(0, 20))
        
        # Treeview
        columns = ("날짜", "직원", "출근", "퇴근", "총시간", "정규", "잔업", 
                  "야간", "휴일", "상태")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=18)
        
        widths = [100, 120, 80, 80, 80, 80, 80, 80, 60, 80]
        for col, width in zip(columns, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="center")
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 컨텍스트 메뉴
        self.tree.bind("<Button-3>", self.show_context_menu)
        self.tree.bind("<Double-1>", self.edit_attendance)
        
        # 안내
        info = ctk.CTkLabel(
            self,
            text="💡 Tip: 우클릭으로 메뉴, 더블클릭으로 수정",
            font=ctk.CTkFont(size=13),
            text_color=("blue", "lightblue")
        )
        info.pack(pady=10, padx=35, anchor="w")
        
        # 초기 검색
        self.search()
    
    def search(self):
        """검색"""
        # 기존 데이터 삭제
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            # 필터 조건
            emp_selection = self.emp_combo.get()
            emp_id = None
            
            if emp_selection != "전체":
                emp_code = emp_selection.split(" - ")[0]
                employees = self.db.get_all_employees()
                for e in employees:
                    if e['emp_code'] == emp_code:
                        emp_id = e['emp_id']
                        break
            
            start_date = self.start_entry.get()
            end_date = self.end_entry.get()
            
            # 데이터 조회
            if emp_id:
                # 특정 직원
                records = self.db.get_attendance_by_date_range(emp_id, start_date, end_date)
                
                # 직원 이름
                emp = self.db.get_employee(emp_id)
                emp_name = emp['name'] if emp else "Unknown"
                
                for rec in records:
                    self.insert_record(rec, emp_name)
            else:
                # 전체 직원
                employees = self.db.get_all_employees()
                for emp in employees:
                    records = self.db.get_attendance_by_date_range(
                        emp['emp_id'], start_date, end_date
                    )
                    for rec in records:
                        self.insert_record(rec, emp['name'])
        
        except Exception as e:
            messagebox.showerror("오류", f"검색 오류:\n{e}")
    
    def insert_record(self, rec: dict, emp_name: str):
        """레코드 삽입"""
        status = "정상" if rec.get('attendance_type') == 'normal' else rec.get('attendance_type', '-')
        holiday = "✓" if rec.get('is_holiday') else ""
        
        self.tree.insert("", "end", values=(
            rec['work_date'],
            emp_name,
            rec.get('clock_in', '-'),
            rec.get('clock_out', '-'),
            f"{rec.get('work_hours', 0):.1f}h",
            f"{rec.get('regular_hours', 0):.1f}h",
            f"{rec.get('overtime_hours', 0):.1f}h",
            f"{rec.get('night_hours', 0):.1f}h",
            holiday,
            status
        ), tags=(rec.get('attendance_id'),))
    
    def show_context_menu(self, event):
        """컨텍스트 메뉴"""
        # TODO: 컨텍스트 메뉴 구현
        pass
    
    def edit_attendance(self, event):
        """근태 수정"""
        selection = self.tree.selection()
        if not selection:
            return
        
        messagebox.showinfo("안내", "근태 수정 기능은 곧 추가됩니다")


class LeaveListFrame(ctk.CTkFrame):
    """휴가 목록 화면"""
    
    def __init__(self, parent, db: Database, leave_mgr: LeaveManager):
        super().__init__(parent)
        self.db = db
        self.leave_mgr = leave_mgr
        self.create_widgets()
    
    def create_widgets(self):
        """위젯 생성"""
        # 제목
        title = ctk.CTkLabel(
            self,
            text="🏖️ 휴가 목록",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title.pack(pady=(25, 15), padx=35, anchor="w")
        
        # 필터 영역
        filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        filter_frame.pack(fill="x", padx=35, pady=(0, 15))
        
        # 직원 선택
        ctk.CTkLabel(
            filter_frame,
            text="직원:",
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=(0, 10))
        
        employees = self.db.get_all_employees()
        emp_list = ["전체"] + [f"{e['emp_code']} - {e['name']}" for e in employees]
        
        self.emp_combo = ctk.CTkComboBox(
            filter_frame,
            values=emp_list,
            width=200,
            state="readonly"
        )
        self.emp_combo.set("전체")
        self.emp_combo.pack(side="left", padx=5)
        
        # 상태 선택
        ctk.CTkLabel(
            filter_frame,
            text="상태:",
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=(20, 10))
        
        self.status_combo = ctk.CTkComboBox(
            filter_frame,
            values=["전체", "대기중", "승인됨", "반려됨"],
            width=120,
            state="readonly"
        )
        self.status_combo.set("전체")
        self.status_combo.pack(side="left", padx=5)
        
        # 검색 버튼
        search_btn = ctk.CTkButton(
            filter_frame,
            text="🔍 검색",
            command=self.search,
            width=100,
            height=35
        )
        search_btn.pack(side="left", padx=(10, 0))
        
        # 목록 테이블
        list_frame = ctk.CTkFrame(self)
        list_frame.pack(fill="both", expand=True, padx=35, pady=(0, 20))
        
        # Treeview
        columns = ("신청번호", "직원", "휴가종류", "시작일", "종료일", 
                  "일수", "신청일", "상태", "승인자")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=18)
        
        widths = [80, 100, 100, 100, 100, 60, 100, 80, 80]
        for col, width in zip(columns, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="center")
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 더블클릭 이벤트
        self.tree.bind("<Double-1>", self.show_detail)
        
        # 안내
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.pack(fill="x", padx=35, pady=10)
        
        ctk.CTkLabel(
            info_frame,
            text="💡 Tip: 더블클릭으로 상세 보기",
            font=ctk.CTkFont(size=13),
            text_color=("blue", "lightblue")
        ).pack(side="left")
        
        # 연차 현황 버튼
        balance_btn = ctk.CTkButton(
            info_frame,
            text="📊 연차 현황 보기",
            command=self.show_balance,
            height=35,
            width=140
        )
        balance_btn.pack(side="right")
        
        # 초기 검색
        self.search()
    
    def search(self):
        """검색"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            # 필터 조건
            emp_selection = self.emp_combo.get()
            status_filter = self.status_combo.get()
            
            emp_id = None
            if emp_selection != "전체":
                emp_code = emp_selection.split(" - ")[0]
                employees = self.db.get_all_employees()
                for e in employees:
                    if e['emp_code'] == emp_code:
                        emp_id = e['emp_id']
                        break
            
            status = None
            if status_filter == "대기중":
                status = "PENDING"
            elif status_filter == "승인됨":
                status = "APPROVED"
            elif status_filter == "반려됨":
                status = "REJECTED"
            
            # 데이터 조회
            requests = self.leave_mgr.get_leave_requests(emp_id, status)
            
            # 직원 이름 매핑
            employees = {e['emp_id']: e['name'] for e in self.db.get_all_employees()}
            
            # 표시
            for req in requests:
                emp_name = employees.get(req['emp_id'], 'Unknown')
                
                # 휴가 종류 한글 변환
                leave_types = {
                    'ANNUAL': '연차',
                    'HALF_DAY': '반차',
                    'SICK': '병가',
                    'SPECIAL': '특별휴가',
                    'UNPAID': '무급휴가'
                }
                leave_type = leave_types.get(req['leave_type'], req['leave_type'])
                
                # 상태 한글 변환
                statuses = {
                    'PENDING': '대기중',
                    'APPROVED': '승인됨',
                    'REJECTED': '반려됨',
                    'CANCELLED': '취소됨'
                }
                status_text = statuses.get(req['status'], req['status'])
                
                self.tree.insert("", "end", values=(
                    req['request_id'],
                    emp_name,
                    leave_type,
                    req['start_date'],
                    req['end_date'],
                    f"{req['total_days']:.1f}일",
                    req['request_date'],
                    status_text,
                    "-"
                ), tags=(req['request_id'],))
        
        except Exception as e:
            messagebox.showerror("오류", f"검색 오류:\n{e}")
    
    def show_detail(self, event):
        """상세 보기"""
        selection = self.tree.selection()
        if not selection:
            return
        
        messagebox.showinfo("안내", "휴가 상세 보기 기능은 곧 추가됩니다")
    
    def show_balance(self):
        """연차 현황 보기"""
        LeaveBalanceDialog(self, self.db, self.leave_mgr)


class LeaveBalanceDialog(ctk.CTkToplevel):
    """연차 현황 다이얼로그"""
    
    def __init__(self, parent, db: Database, leave_mgr: LeaveManager):
        super().__init__(parent)
        
        self.db = db
        self.leave_mgr = leave_mgr
        
        self.title("연차 현황")
        self.geometry("900x600")
        self.transient(parent)
        self.grab_set()
        
        self.create_widgets()
    
    def create_widgets(self):
        """위젯 생성"""
        # 제목
        title = ctk.CTkLabel(
            self,
            text="📊 직원별 연차 현황",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)
        
        # 년도 선택
        year_frame = ctk.CTkFrame(self, fg_color="transparent")
        year_frame.pack(pady=10)
        
        ctk.CTkLabel(year_frame, text="년도:", font=ctk.CTkFont(size=14)).pack(side="left", padx=10)
        
        current_year = datetime.now().year
        years = [str(y) for y in range(current_year - 2, current_year + 2)]
        
        self.year_combo = ctk.CTkComboBox(
            year_frame,
            values=years,
            width=100,
            state="readonly",
            command=self.refresh
        )
        self.year_combo.set(str(current_year))
        self.year_combo.pack(side="left")
        
        # 목록
        list_frame = ctk.CTkFrame(self)
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        columns = ("직원코드", "이름", "부서", "입사일", "총부여", "사용", "남은연차", "이월")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        widths = [80, 100, 100, 100, 80, 80, 80, 80]
        for col, width in zip(columns, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="center")
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 닫기 버튼
        close_btn = ctk.CTkButton(
            self,
            text="닫기",
            command=self.destroy,
            height=40,
            width=120
        )
        close_btn.pack(pady=20)
        
        # 초기 로드
        self.refresh()
    
    def refresh(self, *args):
        """새로고침"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            year = int(self.year_combo.get())
            employees = self.db.get_all_employees()
            
            for emp in employees:
                balance = self.leave_mgr.get_employee_leave_balance(emp['emp_id'], year)
                
                if balance:
                    self.tree.insert("", "end", values=(
                        emp['emp_code'],
                        emp['name'],
                        emp.get('department', '-'),
                        emp['hire_date'],
                        f"{balance['total_annual_days']:.1f}",
                        f"{balance['used_annual_days']:.1f}",
                        f"{balance['remaining_annual_days']:.1f}",
                        f"{balance.get('carried_forward_days', 0):.1f}"
                    ))
                else:
                    # 연차 없음
                    self.tree.insert("", "end", values=(
                        emp['emp_code'],
                        emp['name'],
                        emp.get('department', '-'),
                        emp['hire_date'],
                        "-", "-", "-", "-"
                    ))
        
        except Exception as e:
            messagebox.showerror("오류", f"조회 오류:\n{e}")
