"""
급여관리 ERP v2.0 - 완전한 GUI 구현 Part 1
직원 관리, 근태 관리, 휴가 관리
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog, ttk
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import calendar

from config_manager import ConfigManager, WorkSchedule, OvertimeRate
from database_v2 import Database
from payroll_calculator_v2 import AdvancedPayrollCalculator
from leave_manager import LeaveManager, LeaveType, LeaveStatus

# CustomTkinter 설정
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class ERPGuiHelper:
    """GUI 헬퍼 함수들"""
    
    @staticmethod
    def create_section_title(parent, title: str, row: int):
        """섹션 제목"""
        label = ctk.CTkLabel(
            parent,
            text=title,
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w"
        )
        label.grid(row=row, column=0, columnspan=2, pady=(20, 10), padx=20, sticky="w")
        return label
    
    @staticmethod
    def create_input_field(parent, label_text: str, row: int, placeholder: str = "", default_value: str = ""):
        """입력 필드"""
        label = ctk.CTkLabel(
            parent,
            text=label_text,
            font=ctk.CTkFont(size=14),
            anchor="w",
            width=150
        )
        label.grid(row=row, column=0, pady=8, padx=(20, 10), sticky="w")
        
        entry = ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
            height=35,
            font=ctk.CTkFont(size=14)
        )
        entry.grid(row=row, column=1, pady=8, padx=(10, 20), sticky="ew")
        
        if default_value:
            entry.insert(0, default_value)
        
        parent.grid_columnconfigure(1, weight=1)
        return entry
    
    @staticmethod
    def create_dropdown_field(parent, label_text: str, row: int, values: list, default_index: int = 0):
        """드롭다운 필드"""
        label = ctk.CTkLabel(
            parent,
            text=label_text,
            font=ctk.CTkFont(size=14),
            anchor="w",
            width=150
        )
        label.grid(row=row, column=0, pady=8, padx=(20, 10), sticky="w")
        
        # 값이 비어있으면 기본값 제공
        if not values:
            values = ["없음"]
        
        dropdown = ctk.CTkComboBox(
            parent,
            values=values,
            height=35,
            font=ctk.CTkFont(size=14),
            state="readonly"
        )
        dropdown.grid(row=row, column=1, pady=8, padx=(10, 20), sticky="ew")
        
        # 기본값 설정
        if values and 0 <= default_index < len(values):
            dropdown.set(values[default_index])
        
        return dropdown
    
    @staticmethod
    def create_date_picker(parent, label_text: str, row: int, default_date: str = ""):
        """날짜 선택 필드"""
        if not default_date:
            default_date = datetime.now().strftime("%Y-%m-%d")
        
        return ERPGuiHelper.create_input_field(parent, label_text, row, "YYYY-MM-DD", default_date)
    
    @staticmethod
    def create_time_picker(parent, label_text: str, row: int, default_time: str = ""):
        """시간 선택 필드"""
        if not default_time:
            default_time = "09:00"
        
        return ERPGuiHelper.create_input_field(parent, label_text, row, "HH:MM", default_time)


class AttendanceDialog(ctk.CTkToplevel):
    """근태 입력 다이얼로그"""
    
    def __init__(self, parent, db: Database, config: ConfigManager, calculator: AdvancedPayrollCalculator):
        super().__init__(parent)
        
        self.db = db
        self.config = config
        self.calculator = calculator
        
        self.title("근태 입력")
        self.geometry("700x700")
        self.transient(parent)
        self.grab_set()
        
        self.create_widgets()
    
    def create_widgets(self):
        """위젯 생성"""
        scroll_frame = ctk.CTkScrollableFrame(self, width=650, height=600)
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 직원 선택
        ERPGuiHelper.create_section_title(scroll_frame, "👤 직원 선택", 0)
        
        employees = self.db.get_all_employees()
        emp_names = [f"{e['emp_code']} - {e['name']}" for e in employees]
        self.emp_dropdown = ERPGuiHelper.create_dropdown_field(
            scroll_frame, "* 직원", 1, emp_names
        )
        
        # 근무일
        ERPGuiHelper.create_section_title(scroll_frame, "📅 근무 정보", 2)
        
        self.date_entry = ERPGuiHelper.create_date_picker(scroll_frame, "* 근무일", 3)
        
        # 출퇴근 시간
        self.clock_in_entry = ERPGuiHelper.create_time_picker(scroll_frame, "* 출근 시간", 4)
        self.clock_out_entry = ERPGuiHelper.create_time_picker(scroll_frame, "* 퇴근 시간", 5, "18:00")
        
        # 휴일 여부
        self.holiday_var = ctk.BooleanVar()
        holiday_check = ctk.CTkCheckBox(
            scroll_frame,
            text="휴일 근무",
            variable=self.holiday_var,
            font=ctk.CTkFont(size=14)
        )
        holiday_check.grid(row=6, column=1, pady=10, padx=(10, 20), sticky="w")
        
        # 근태 유형
        attendance_types = ["정상출근", "연차", "반차", "결근", "병가"]
        self.type_dropdown = ERPGuiHelper.create_dropdown_field(
            scroll_frame, "근태 유형", 7, attendance_types
        )
        
        # 비고
        ERPGuiHelper.create_section_title(scroll_frame, "📝 비고", 8)
        
        self.notes_text = ctk.CTkTextbox(scroll_frame, height=100, font=ctk.CTkFont(size=14))
        self.notes_text.grid(row=9, column=0, columnspan=2, pady=10, padx=20, sticky="ew")
        
        # 계산 미리보기
        ERPGuiHelper.create_section_title(scroll_frame, "🧮 자동 계산", 10)
        
        self.preview_label = ctk.CTkLabel(
            scroll_frame,
            text="출퇴근 시간을 입력하면 자동 계산됩니다",
            font=ctk.CTkFont(size=13),
            text_color=("gray50", "gray60"),
            justify="left"
        )
        self.preview_label.grid(row=11, column=0, columnspan=2, pady=10, padx=20, sticky="w")
        
        # 계산 버튼
        calc_btn = ctk.CTkButton(
            scroll_frame,
            text="🧮 근무시간 계산",
            command=self.calculate_preview,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        calc_btn.grid(row=12, column=0, columnspan=2, pady=10, padx=20, sticky="ew")
        
        # 저장 버튼
        save_btn = ctk.CTkButton(
            scroll_frame,
            text="💾 저장",
            command=self.save_attendance,
            height=45,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        save_btn.grid(row=13, column=0, columnspan=2, pady=20, padx=20, sticky="ew")
    
    def calculate_preview(self):
        """근무시간 미리 계산"""
        try:
            # 직원 선택 확인
            emp_selection = self.emp_dropdown.get()
            if not emp_selection or emp_selection == "없음":
                messagebox.showwarning("경고", "직원을 선택하세요")
                return
            
            emp_code = emp_selection.split(" - ")[0]
            
            # 직원 정보 조회
            employees = self.db.get_all_employees()
            emp_id = None
            for e in employees:
                if e['emp_code'] == emp_code:
                    emp_id = e['emp_id']
                    break
            
            if not emp_id:
                messagebox.showerror("오류", "직원 정보를 찾을 수 없습니다")
                return
            
            # 시간 입력 확인
            clock_in = self.clock_in_entry.get()
            clock_out = self.clock_out_entry.get()
            work_date = self.date_entry.get()
            
            if not clock_in or not clock_out:
                messagebox.showwarning("경고", "출퇴근 시간을 입력하세요")
                return
            
            # 근무시간 계산
            work_info = self.calculator.calculate_work_hours_by_schedule(
                emp_id, work_date, clock_in, clock_out
            )
            
            # 결과 표시
            preview_text = f"""
📊 계산 결과:
━━━━━━━━━━━━━━━━━━━━
총 근무시간: {work_info['work_hours']:.2f}시간
휴게시간: {work_info['break_hours']:.2f}시간
실 근무시간: {work_info['work_hours'] - work_info['break_hours']:.2f}시간

정규시간: {work_info['regular_hours']:.2f}시간
잔업시간: {work_info['overtime_hours']:.2f}시간
야간시간: {work_info['night_hours']:.2f}시간

잔업 구간별:
  - 1구간: {work_info['overtime_tier1_minutes']:.0f}분
  - 2구간: {work_info['overtime_tier2_minutes']:.0f}분
  - 3구간: {work_info['overtime_tier3_minutes']:.0f}분
            """
            
            self.preview_label.configure(
                text=preview_text,
                text_color=("green", "lightgreen")
            )
            
        except Exception as e:
            messagebox.showerror("오류", f"계산 중 오류 발생:\n{e}")
    
    def save_attendance(self):
        """근태 저장"""
        try:
            # 직원 선택 확인
            emp_selection = self.emp_dropdown.get()
            if not emp_selection or emp_selection == "없음":
                messagebox.showwarning("경고", "직원을 선택하세요")
                return
            
            emp_code = emp_selection.split(" - ")[0]
            
            # 직원 ID 조회
            employees = self.db.get_all_employees()
            emp_id = None
            for e in employees:
                if e['emp_code'] == emp_code:
                    emp_id = e['emp_id']
                    break
            
            if not emp_id:
                messagebox.showerror("오류", "직원 정보를 찾을 수 없습니다")
                return
            
            # 입력값 검증
            work_date = self.date_entry.get()
            clock_in = self.clock_in_entry.get()
            clock_out = self.clock_out_entry.get()
            
            if not all([work_date, clock_in, clock_out]):
                messagebox.showwarning("경고", "필수 항목을 모두 입력하세요")
                return
            
            # 근무시간 계산
            work_info = self.calculator.calculate_work_hours_by_schedule(
                emp_id, work_date, clock_in, clock_out
            )
            
            # 근태 데이터 구성
            attendance_data = {
                'emp_id': emp_id,
                'work_date': work_date,
                'clock_in': clock_in,
                'clock_out': clock_out,
                'work_hours': work_info['work_hours'],
                'regular_hours': work_info['regular_hours'],
                'break_hours': work_info['break_hours'],
                'overtime_hours': work_info['overtime_hours'],
                'night_hours': work_info['night_hours'],
                'overtime_tier1_minutes': work_info['overtime_tier1_minutes'],
                'overtime_tier2_minutes': work_info['overtime_tier2_minutes'],
                'overtime_tier3_minutes': work_info['overtime_tier3_minutes'],
                'is_holiday': 1 if self.holiday_var.get() else 0,
                'work_schedule_id': work_info['schedule_id'],
                'attendance_type': 'normal',
                'notes': self.notes_text.get("1.0", "end-1c")
            }
            
            # 저장
            success, _ = self.db.add_attendance(attendance_data)
            
            if success:
                messagebox.showinfo("성공", "근태가 저장되었습니다!")
                self.destroy()
            else:
                messagebox.showerror("오류", "근태 저장에 실패했습니다")
                
        except Exception as e:
            messagebox.showerror("오류", f"저장 중 오류 발생:\n{e}")


class LeaveRequestDialog(ctk.CTkToplevel):
    """휴가 신청 다이얼로그"""
    
    def __init__(self, parent, db: Database, leave_mgr: LeaveManager):
        super().__init__(parent)
        
        self.db = db
        self.leave_mgr = leave_mgr
        
        self.title("휴가 신청")
        self.geometry("700x800")
        self.transient(parent)
        self.grab_set()
        
        self.create_widgets()
    
    def create_widgets(self):
        """위젯 생성"""
        scroll_frame = ctk.CTkScrollableFrame(self, width=650, height=700)
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 직원 선택
        ERPGuiHelper.create_section_title(scroll_frame, "👤 직원 선택", 0)
        
        employees = self.db.get_all_employees()
        emp_names = [f"{e['emp_code']} - {e['name']}" for e in employees]
        self.emp_dropdown = ERPGuiHelper.create_dropdown_field(
            scroll_frame, "* 직원", 1, emp_names
        )
        
        # 연차 현황 표시
        self.balance_label = ctk.CTkLabel(
            scroll_frame,
            text="직원을 선택하면 연차 현황이 표시됩니다",
            font=ctk.CTkFont(size=13),
            text_color=("gray50", "gray60")
        )
        self.balance_label.grid(row=2, column=0, columnspan=2, pady=10, padx=20, sticky="w")
        
        # 연차 확인 버튼
        check_btn = ctk.CTkButton(
            scroll_frame,
            text="📊 연차 확인",
            command=self.check_leave_balance,
            height=35,
            font=ctk.CTkFont(size=14)
        )
        check_btn.grid(row=3, column=0, columnspan=2, pady=5, padx=20, sticky="ew")
        
        # 휴가 정보
        ERPGuiHelper.create_section_title(scroll_frame, "🏖️ 휴가 정보", 4)
        
        # 휴가 종류
        leave_types = ["연차", "반차(오전)", "반차(오후)", "병가", "특별휴가", "무급휴가"]
        self.type_dropdown = ERPGuiHelper.create_dropdown_field(
            scroll_frame, "* 휴가 종류", 5, leave_types
        )
        
        # 시작일
        self.start_date_entry = ERPGuiHelper.create_date_picker(scroll_frame, "* 시작일", 6)
        
        # 종료일
        self.end_date_entry = ERPGuiHelper.create_date_picker(scroll_frame, "* 종료일", 7)
        
        # 사유
        ERPGuiHelper.create_section_title(scroll_frame, "📝 사유", 8)
        
        self.reason_text = ctk.CTkTextbox(scroll_frame, height=100, font=ctk.CTkFont(size=14))
        self.reason_text.grid(row=9, column=0, columnspan=2, pady=10, padx=20, sticky="ew")
        
        # 신청 버튼
        submit_btn = ctk.CTkButton(
            scroll_frame,
            text="📩 신청",
            command=self.submit_request,
            height=45,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        submit_btn.grid(row=10, column=0, columnspan=2, pady=20, padx=20, sticky="ew")
    
    def check_leave_balance(self):
        """연차 현황 확인"""
        try:
            emp_selection = self.emp_dropdown.get()
            if not emp_selection or emp_selection == "없음":
                messagebox.showwarning("경고", "직원을 선택하세요")
                return
            
            emp_code = emp_selection.split(" - ")[0]
            
            # 직원 ID 조회
            employees = self.db.get_all_employees()
            emp_id = None
            for e in employees:
                if e['emp_code'] == emp_code:
                    emp_id = e['emp_id']
                    break
            
            if not emp_id:
                return
            
            # 연차 현황 조회
            current_year = datetime.now().year
            balance = self.leave_mgr.get_employee_leave_balance(emp_id, current_year)
            
            if balance:
                balance_text = f"""
📊 {current_year}년 연차 현황:
━━━━━━━━━━━━━━━━━━━━
총 부여 연차: {balance['total_annual_days']:.1f}일
사용한 연차: {balance['used_annual_days']:.1f}일
남은 연차: {balance['remaining_annual_days']:.1f}일
                """
                self.balance_label.configure(
                    text=balance_text,
                    text_color=("blue", "lightblue")
                )
            else:
                self.balance_label.configure(
                    text="연차 정보가 없습니다",
                    text_color=("red", "orange")
                )
                
        except Exception as e:
            messagebox.showerror("오류", f"연차 조회 오류:\n{e}")
    
    def submit_request(self):
        """휴가 신청"""
        try:
            # 직원 확인
            emp_selection = self.emp_dropdown.get()
            if not emp_selection or emp_selection == "없음":
                messagebox.showwarning("경고", "직원을 선택하세요")
                return
            
            emp_code = emp_selection.split(" - ")[0]
            
            employees = self.db.get_all_employees()
            emp_id = None
            for e in employees:
                if e['emp_code'] == emp_code:
                    emp_id = e['emp_id']
                    break
            
            if not emp_id:
                messagebox.showerror("오류", "직원 정보를 찾을 수 없습니다")
                return
            
            # 입력값 검증
            leave_type = self.type_dropdown.get()
            start_date = self.start_date_entry.get()
            end_date = self.end_date_entry.get()
            reason = self.reason_text.get("1.0", "end-1c")
            
            if not all([leave_type, start_date, end_date]):
                messagebox.showwarning("경고", "필수 항목을 모두 입력하세요")
                return
            
            # 휴가 종류 변환
            is_half_day = False
            half_day_period = ""
            
            if "반차(오전)" in leave_type:
                is_half_day = True
                half_day_period = "AM"
                leave_type_code = "HALF_DAY"
            elif "반차(오후)" in leave_type:
                is_half_day = True
                half_day_period = "PM"
                leave_type_code = "HALF_DAY"
            elif "연차" in leave_type:
                leave_type_code = "ANNUAL"
            elif "병가" in leave_type:
                leave_type_code = "SICK"
            elif "특별휴가" in leave_type:
                leave_type_code = "SPECIAL"
            else:
                leave_type_code = "UNPAID"
            
            # 신청 데이터 구성
            request_data = {
                'emp_id': emp_id,
                'leave_type': leave_type_code,
                'start_date': start_date,
                'end_date': end_date,
                'is_half_day': is_half_day,
                'half_day_period': half_day_period,
                'reason': reason
            }
            
            # 신청
            success, request_id = self.leave_mgr.submit_leave_request(request_data)
            
            if success:
                # 자동 승인 (테스트용)
                self.leave_mgr.approve_leave_request(request_id)
                messagebox.showinfo("성공", f"휴가가 신청되었습니다!\n신청번호: {request_id}")
                self.destroy()
            else:
                messagebox.showerror("오류", "휴가 신청에 실패했습니다")
                
        except Exception as e:
            messagebox.showerror("오류", f"신청 중 오류 발생:\n{e}")


# 계속 Part 2에서...
