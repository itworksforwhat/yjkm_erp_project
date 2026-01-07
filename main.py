"""
급여관리 ERP v2.0 - 최종 완성판
Professional Payroll Management System

Author: AI Assistant
Date: 2025-01-02
Version: 2.0.0
"""

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
import sys

# 핵심 모듈
from config_manager import ConfigManager
from database_v2 import Database
from payroll_calculator_v2 import AdvancedPayrollCalculator
from secom_integration import SecomIntegration
from leave_manager import LeaveManager

# GUI 모듈
from gui_complete_part1 import ERPGuiHelper, AttendanceDialog, LeaveRequestDialog
from settings_screens import WorkScheduleSettingsFrame, OvertimeSettingsFrame
from payroll_screens import PayrollCalculationFrame
from list_screens import AttendanceListFrame, LeaveListFrame

# 테마 설정
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class PayrollERP(ctk.CTk):
    """급여관리 ERP 메인 애플리케이션"""
    
    VERSION = "2.0.0"
    TITLE = "💼 급여관리 ERP v2.0 - Complete Edition"
    
    def __init__(self):
        super().__init__()
        
        # 윈도우 설정
        self.title(self.TITLE)
        self.geometry("1600x900")
        self.minsize(1400, 800)
        
        # 모듈 초기화
        self._initialize_modules()
        
        # UI 구성
        self._create_ui()
        
        # 초기 화면
        self.show_dashboard()
        
        print(f"✅ {self.TITLE} 시작 완료!")
    
    def _initialize_modules(self):
        """모듈 초기화"""
        try:
            print("시스템 초기화 중...")
            self.db = Database()
            self.config = ConfigManager()
            self.calculator = AdvancedPayrollCalculator()
            self.secom = SecomIntegration()
            self.leave_mgr = LeaveManager()
            
            # 테이블 생성
            self.db.create_tables()
            self.config.initialize_tables()
            self.leave_mgr.initialize_tables()
            
        except Exception as e:
            messagebox.showerror("초기화 오류", f"시스템 초기화 실패:\n{e}")
            sys.exit(1)
    
    def _create_ui(self):
        """UI 구성"""
        # 네비게이션 바
        self._create_navigation()
        
        # 컨텐츠 영역
        self.content_frame = ctk.CTkFrame(self, corner_radius=10)
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        # 그리드 설정
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
    
    def _create_navigation(self):
        """네비게이션 바 생성"""
        self.nav_frame = ctk.CTkFrame(
            self, 
            corner_radius=0, 
            width=220, 
            fg_color=("gray90", "gray20")
        )
        self.nav_frame.grid(row=0, column=0, sticky="nsew")
        self.nav_frame.grid_rowconfigure(15, weight=1)
        
        # 로고
        ctk.CTkLabel(
            self.nav_frame,
            text="💼 급여관리 ERP",
            font=ctk.CTkFont(size=22, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=(25, 35))
        
        # 메인 메뉴
        main_menus = [
            ("📊 대시보드", self.show_dashboard, 1),
            ("👥 직원 관리", self.show_employee_management, 2),
            ("⏰ 근태 관리", self.show_attendance_list, 3),
            ("🏖️ 휴가 관리", self.show_leave_list, 4),
            ("💰 급여 계산", self.show_payroll_calculation, 5),
            ("🔄 세콤 연동", self.show_secom_integration, 6),
        ]
        
        for text, command, row in main_menus:
            self._create_nav_button(text, command, row)
        
        # 구분선
        ctk.CTkFrame(
            self.nav_frame, 
            height=2, 
            fg_color=("gray70", "gray30")
        ).grid(row=7, column=0, sticky="ew", padx=20, pady=15)
        
        # 설정 메뉴
        setting_menus = [
            ("🔧 근무 설정", self.show_work_schedule_settings, 8),
            ("💸 잔업 설정", self.show_overtime_settings, 9),
        ]
        
        for text, command, row in setting_menus:
            self._create_nav_button(text, command, row)
        
        # 버전 정보
        ctk.CTkLabel(
            self.nav_frame,
            text=f"v{self.VERSION}\n{datetime.now().strftime('%Y-%m-%d')}",
            font=ctk.CTkFont(size=10),
            text_color=("gray50", "gray60")
        ).grid(row=16, column=0, padx=20, pady=(10, 25))
    
    def _create_nav_button(self, text: str, command, row: int):
        """네비게이션 버튼 생성"""
        ctk.CTkButton(
            self.nav_frame,
            text=text,
            command=command,
            font=ctk.CTkFont(size=14),
            height=42,
            corner_radius=8,
            anchor="w",
            fg_color="transparent",
            hover_color=("gray80", "gray25")
        ).grid(row=row, column=0, padx=15, pady=6, sticky="ew")
    
    def _clear_content(self):
        """컨텐츠 영역 초기화"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    # ==================== 화면 표시 메서드 ====================
    
    def show_dashboard(self):
        """대시보드"""
        self._clear_content()
        
        # 제목
        ctk.CTkLabel(
            self.content_frame,
            text="📊 대시보드",
            font=ctk.CTkFont(size=32, weight="bold")
        ).pack(pady=25, padx=35, anchor="w")
        
        # 통계 카드
        self._create_statistics_section()
        
        # 빠른 작업
        self._create_quick_actions()
    
    def _create_statistics_section(self):
        """통계 섹션"""
        stats_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        stats_frame.pack(fill="x", padx=35, pady=(0, 25))
        
        # 데이터 조회
        employees = self.db.get_all_employees(include_resigned=False)
        emp_count = len(employees)
        
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        self.db.connect()
        self.db.cursor.execute("""
            SELECT 
                COUNT(*) as processed,
                COALESCE(SUM(net_pay), 0) as total_pay
            FROM payroll
            WHERE pay_year = ? AND pay_month = ?
        """, (current_year, current_month))
        
        result = self.db.cursor.fetchone()
        payroll_stats = dict(result) if result else {'processed': 0, 'total_pay': 0}
        self.db.close()
        
        # 카드 생성
        self._create_stat_card(stats_frame, "👥 재직 인원", f"{emp_count}명", 0)
        self._create_stat_card(stats_frame, "💰 이번달 급여", 
                               f"{payroll_stats['total_pay']:,.0f}원", 1)
        self._create_stat_card(stats_frame, "📋 급여 처리", 
                               f"{payroll_stats['processed']}/{emp_count}", 2)
    
    def _create_stat_card(self, parent, title: str, value: str, column: int):
        """통계 카드"""
        card = ctk.CTkFrame(parent, height=110, corner_radius=10)
        card.grid(row=0, column=column, padx=10, pady=0, sticky="nsew")
        
        ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=15),
            text_color=("gray50", "gray70")
        ).pack(pady=(20, 8))
        
        ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=28, weight="bold")
        ).pack(pady=(0, 20))
        
        parent.grid_columnconfigure(column, weight=1)
    
    def _create_quick_actions(self):
        """빠른 작업 섹션"""
        quick_frame = ctk.CTkFrame(self.content_frame)
        quick_frame.pack(fill="both", expand=True, padx=35, pady=(0, 25))
        
        ctk.CTkLabel(
            quick_frame,
            text="⚡ 빠른 작업",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=20, anchor="w", padx=25)
        
        # 버튼 컨테이너
        btn_container = ctk.CTkFrame(quick_frame, fg_color="transparent")
        btn_container.pack(fill="both", expand=True, padx=25, pady=(0, 25))
        
        actions = [
            ("➕ 직원 추가", self._add_employee_dialog, 0, 0),
            ("⏰ 근태 입력", self._add_attendance_dialog, 0, 1),
            ("🏖️ 휴가 신청", self._add_leave_dialog, 0, 2),
            ("💰 급여 계산", self.show_payroll_calculation, 1, 0),
            ("🔧 근무 설정", self.show_work_schedule_settings, 1, 1),
            ("💸 잔업 설정", self.show_overtime_settings, 1, 2),
        ]
        
        for text, cmd, r, c in actions:
            ctk.CTkButton(
                btn_container,
                text=text,
                command=cmd,
                height=90,
                font=ctk.CTkFont(size=16, weight="bold"),
                corner_radius=10
            ).grid(row=r, column=c, padx=10, pady=10, sticky="nsew")
        
        # 그리드 설정
        for i in range(2):
            btn_container.grid_rowconfigure(i, weight=1)
        for i in range(3):
            btn_container.grid_columnconfigure(i, weight=1)
    
    def show_employee_management(self):
        """직원 관리"""
        from tkinter import ttk
        
        self._clear_content()
        
        # 헤더
        header = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        header.pack(fill="x", padx=35, pady=(25, 15))
        
        ctk.CTkLabel(
            header,
            text="👥 직원 관리",
            font=ctk.CTkFont(size=32, weight="bold")
        ).pack(side="left")
        
        ctk.CTkButton(
            header,
            text="➕ 직원 추가",
            command=self._add_employee_dialog,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="right")
        
        # 목록
        list_frame = ctk.CTkFrame(self.content_frame)
        list_frame.pack(fill="both", expand=True, padx=35, pady=(0, 25))
        
        columns = ("코드", "이름", "부서", "직급", "근무형태", "시급", "입사일", "상태")
        tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=20)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor="center")
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 데이터 로드
        employees = self.db.get_all_employees(include_resigned=True)
        
        for emp in employees:
            schedule = self.config.get_schedule(emp.get('work_schedule_id', 'DAY_SHIFT'))
            schedule_name = schedule['schedule_name'] if schedule else '-'
            status = "퇴사" if emp.get('resignation_date') else "재직"
            
            tree.insert("", "end", values=(
                emp['emp_code'],
                emp['name'],
                emp.get('department', '-'),
                emp.get('position', '-'),
                schedule_name,
                f"{emp['hourly_wage']:,}원",
                emp['hire_date'],
                status
            ))
    
    def show_attendance_list(self):
        """근태 목록"""
        self._clear_content()
        frame = AttendanceListFrame(self.content_frame, self.db, self.calculator)
        frame.pack(fill="both", expand=True)
    
    def show_leave_list(self):
        """휴가 목록"""
        self._clear_content()
        frame = LeaveListFrame(self.content_frame, self.db, self.leave_mgr)
        frame.pack(fill="both", expand=True)
    
    def show_payroll_calculation(self):
        """급여 계산"""
        self._clear_content()
        frame = PayrollCalculationFrame(self.content_frame, self.db, self.calculator)
        frame.pack(fill="both", expand=True)
    
    def show_work_schedule_settings(self):
        """근무 설정"""
        self._clear_content()
        frame = WorkScheduleSettingsFrame(self.content_frame, self.config)
        frame.pack(fill="both", expand=True)
    
    def show_overtime_settings(self):
        """잔업 설정"""
        self._clear_content()
        frame = OvertimeSettingsFrame(self.content_frame, self.config)
        frame.pack(fill="both", expand=True)
    
    def show_secom_integration(self):
        """세콤 연동"""
        from secom_system_complete import SecomIntegrationFrame
        self._clear_content()
        frame = SecomIntegrationFrame(self.content_frame, self.db)
        frame.pack(fill="both", expand=True)
    
    # ==================== 다이얼로그 ====================
    
    def _add_employee_dialog(self):
        """직원 추가 다이얼로그"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("직원 추가")
        dialog.geometry("700x900")
        dialog.transient(self)
        dialog.grab_set()
        
        scroll = ctk.CTkScrollableFrame(dialog, width=650, height=800)
        scroll.pack(fill="both", expand=True, padx=20, pady=20)
        
        fields = {}
        
        # 기본 정보
        ERPGuiHelper.create_section_title(scroll, "📋 기본 정보", 0)
        fields['emp_code'] = ERPGuiHelper.create_input_field(scroll, "* 직원코드", 1, "EMP001")
        fields['name'] = ERPGuiHelper.create_input_field(scroll, "* 이름", 2, "홍길동")
        fields['department'] = ERPGuiHelper.create_input_field(scroll, "부서", 3, "생산팀")
        fields['position'] = ERPGuiHelper.create_input_field(scroll, "직급", 4, "대리")
        
        # 근무 정보
        ERPGuiHelper.create_section_title(scroll, "⏰ 근무 정보", 5)
        fields['hire_date'] = ERPGuiHelper.create_date_picker(scroll, "* 입사일", 6)
        fields['hourly_wage'] = ERPGuiHelper.create_input_field(scroll, "* 시급", 7, "20000")
        
        schedules = self.config.get_all_schedules()
        schedule_names = [s['schedule_name'] for s in schedules]
        fields['work_schedule'] = ERPGuiHelper.create_dropdown_field(
            scroll, "* 근무 형태", 8, schedule_names
        )
        
        # 연락처
        ERPGuiHelper.create_section_title(scroll, "📞 연락처", 9)
        fields['phone'] = ERPGuiHelper.create_input_field(scroll, "전화번호", 10, "010-1234-5678")
        fields['email'] = ERPGuiHelper.create_input_field(scroll, "이메일", 11, "hong@company.com")
        
        # 은행 정보
        ERPGuiHelper.create_section_title(scroll, "🏦 은행 정보", 12)
        fields['bank_name'] = ERPGuiHelper.create_input_field(scroll, "은행명", 13, "KB국민은행")
        fields['account_number'] = ERPGuiHelper.create_input_field(scroll, "계좌번호", 14)
        
        # 세콤 정보
        ERPGuiHelper.create_section_title(scroll, "🔄 세콤 정보", 15)
        fields['secom_id'] = ERPGuiHelper.create_input_field(scroll, "세콤 직원ID", 16)
        fields['secom_card'] = ERPGuiHelper.create_input_field(scroll, "세콤 카드번호", 17)
        
        # 저장 버튼
        ctk.CTkButton(
            scroll,
            text="💾 저장",
            command=lambda: self._save_employee(dialog, fields, schedules),
            height=45,
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=18, column=0, columnspan=2, pady=25, padx=20, sticky="ew")
    
    def _save_employee(self, dialog, fields: dict, schedules: list):
        """직원 저장"""
        try:
            # 필수 검증
            if not all([fields['emp_code'].get(), fields['name'].get(), 
                       fields['hourly_wage'].get()]):
                messagebox.showerror("오류", "필수 항목을 입력하세요")
                return
            
            # 근무 형태 ID
            selected = fields['work_schedule'].get()
            schedule_id = 'DAY_SHIFT'
            for s in schedules:
                if s['schedule_name'] == selected:
                    schedule_id = s['schedule_id']
                    break
            
            # 데이터 구성
            emp_data = {
                'emp_code': fields['emp_code'].get(),
                'name': fields['name'].get(),
                'department': fields['department'].get(),
                'position': fields['position'].get(),
                'hire_date': fields['hire_date'].get() or datetime.now().strftime('%Y-%m-%d'),
                'hourly_wage': float(fields['hourly_wage'].get()),
                'work_schedule_id': schedule_id,
                'phone': fields['phone'].get(),
                'email': fields['email'].get(),
                'bank_name': fields['bank_name'].get(),
                'account_number': fields['account_number'].get(),
                'secom_employee_id': fields['secom_id'].get(),
                'secom_card_number': fields['secom_card'].get()
            }
            
            # 저장
            success, emp_id = self.db.add_employee(emp_data)
            
            if success:
                # 연차 초기화
                self.leave_mgr.initialize_employee_leave_balance(
                    emp_id,
                    emp_data['hire_date'],
                    datetime.now().year
                )
                
                messagebox.showinfo("성공", f"{emp_data['name']} 직원이 추가되었습니다!")
                dialog.destroy()
                self.show_employee_management()
            else:
                messagebox.showerror("오류", "저장 실패")
        
        except ValueError:
            messagebox.showerror("오류", "시급은 숫자로 입력하세요")
        except Exception as e:
            messagebox.showerror("오류", f"저장 오류:\n{e}")
    
    def _add_attendance_dialog(self):
        """근태 입력 다이얼로그"""
        AttendanceDialog(self, self.db, self.config, self.calculator)
    
    def _add_leave_dialog(self):
        """휴가 신청 다이얼로그"""
        LeaveRequestDialog(self, self.db, self.leave_mgr)


def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("💼 급여관리 ERP v2.0 - Complete Edition")
    print("=" * 60)
    print()
    
    app = PayrollERP()
    app.mainloop()


if __name__ == "__main__":
    main()
