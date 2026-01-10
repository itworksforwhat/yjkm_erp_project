"""
급여 계산 화면 모듈
월별 급여 일괄 계산, 상세 보기, 명세서 출력
"""

import customtkinter as ctk
from tkinter import messagebox, ttk
from datetime import datetime
import calendar
from payroll_calculator_v2 import AdvancedPayrollCalculator
from database_v2 import Database


class PayrollCalculationFrame(ctk.CTkFrame):
    """급여 계산 화면"""
    
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
            text="💰 급여 계산",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title.pack(pady=(25, 15), padx=35, anchor="w")
        
        # 상단 컨트롤
        control_frame = ctk.CTkFrame(self, fg_color="transparent")
        control_frame.pack(fill="x", padx=35, pady=(0, 20))
        
        # 년/월 선택
        year_month_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        year_month_frame.pack(side="left")
        
        ctk.CTkLabel(
            year_month_frame,
            text="계산 년월:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=(0, 10))
        
        # 년도
        current_year = datetime.now().year
        years = [str(y) for y in range(current_year - 5, current_year + 2)]
        self.year_combo = ctk.CTkComboBox(
            year_month_frame,
            values=years,
            width=100,
            state="readonly"
        )
        self.year_combo.set(str(current_year))
        self.year_combo.pack(side="left", padx=5)
        
        ctk.CTkLabel(year_month_frame, text="년").pack(side="left", padx=(0, 10))
        
        # 월
        months = [str(m) for m in range(1, 13)]
        self.month_combo = ctk.CTkComboBox(
            year_month_frame,
            values=months,
            width=80,
            state="readonly"
        )
        self.month_combo.set(str(datetime.now().month))
        self.month_combo.pack(side="left", padx=5)
        
        ctk.CTkLabel(year_month_frame, text="월").pack(side="left")
        
        # 버튼들
        btn_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        btn_frame.pack(side="right")
        
        calc_all_btn = ctk.CTkButton(
            btn_frame,
            text="💰 전체 직원 계산",
            command=self.calculate_all,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("green", "darkgreen")
        )
        calc_all_btn.pack(side="left", padx=5)
        
        refresh_btn = ctk.CTkButton(
            btn_frame,
            text="🔄 새로고침",
            command=self.refresh_list,
            height=40,
            width=120
        )
        refresh_btn.pack(side="left", padx=5)
        
        # 급여 목록
        list_frame = ctk.CTkFrame(self)
        list_frame.pack(fill="both", expand=True, padx=35, pady=(0, 20))
        
        # Treeview
        columns = ("직원코드", "이름", "근무일수", "기본급", "잔업수당", "야간수당", 
                  "주휴수당", "총지급액", "총공제액", "실수령액", "상태")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        widths = [80, 100, 80, 100, 100, 100, 100, 120, 100, 120, 80]
        for col, width in zip(columns, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="center")
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 더블클릭 이벤트
        self.tree.bind("<Double-1>", self.show_detail)
        
        # 하단 정보
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.pack(fill="x", padx=35, pady=(0, 25))
        
        ctk.CTkLabel(
            info_frame,
            text="💡 Tip: 항목을 더블클릭하면 상세 내역을 볼 수 있습니다",
            font=ctk.CTkFont(size=13),
            text_color=("blue", "lightblue")
        ).pack(side="left")
        
        # 자동 로드
        self.refresh_list()
    
    def calculate_all(self):
        """전체 직원 급여 계산"""
        result = messagebox.askyesno(
            "확인",
            f"{self.year_combo.get()}년 {self.month_combo.get()}월 전체 직원 급여를 계산하시겠습니까?"
        )
        
        if not result:
            return
        
        try:
            year = int(self.year_combo.get())
            month = int(self.month_combo.get())
            
            # 재직 중인 직원 조회
            employees = self.db.get_all_employees(include_resigned=False)
            
            if not employees:
                messagebox.showwarning("경고", "재직 중인 직원이 없습니다")
                return
            
            success_count = 0
            error_count = 0
            errors = []
            
            # 진행 상황 표시 (간단 버전)
            for emp in employees:
                try:
                    # 급여 계산
                    payroll = self.calculator.calculate_monthly_payroll(
                        emp['emp_id'], year, month
                    )
                    
                    if payroll:
                        # 저장
                        if self.calculator.save_payroll(payroll):
                            success_count += 1
                        else:
                            error_count += 1
                            errors.append(f"{emp['name']}: 저장 실패")
                    else:
                        error_count += 1
                        errors.append(f"{emp['name']}: 계산 실패")
                
                except Exception as e:
                    error_count += 1
                    errors.append(f"{emp['name']}: {str(e)}")
            
            # 결과 표시
            msg = f"급여 계산 완료!\n\n"
            msg += f"성공: {success_count}명\n"
            msg += f"실패: {error_count}명"
            
            if errors:
                msg += f"\n\n오류 내역:\n" + "\n".join(errors[:5])
                if len(errors) > 5:
                    msg += f"\n... 외 {len(errors) - 5}건"
            
            messagebox.showinfo("완료", msg)
            
            # 목록 새로고침
            self.refresh_list()
        
        except Exception as e:
            messagebox.showerror("오류", f"계산 중 오류:\n{e}")
    
    def refresh_list(self):
        """목록 새로고침"""
        # 기존 데이터 삭제
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            year = int(self.year_combo.get())
            month = int(self.month_combo.get())
            
            # 직원별 급여 조회
            employees = self.db.get_all_employees(include_resigned=False)
            
            for emp in employees:
                payroll = self.db.get_payroll(emp['emp_id'], year, month)
                
                if payroll:
                    status = "✅ 완료"
                    values = (
                        emp['emp_code'],
                        emp['name'],
                        f"{payroll['total_work_days']:.1f}일",
                        f"{payroll['base_pay']:,.0f}",
                        f"{payroll['overtime_pay']:,.0f}",
                        f"{payroll['night_pay']:,.0f}",
                        f"{payroll['weekly_holiday_pay']:,.0f}",
                        f"{payroll['total_pay']:,.0f}",
                        f"{payroll['total_deduction']:,.0f}",
                        f"{payroll['net_pay']:,.0f}",
                        status
                    )
                else:
                    status = "❌ 미계산"
                    values = (
                        emp['emp_code'],
                        emp['name'],
                        "-", "-", "-", "-", "-", "-", "-", "-",
                        status
                    )
                
                self.tree.insert("", "end", values=values, tags=(emp['emp_id'],))
        
        except Exception as e:
            messagebox.showerror("오류", f"목록 조회 오류:\n{e}")
    
    def show_detail(self, event):
        """급여 상세 보기"""
        selection = self.tree.selection()
        if not selection:
            return
        
        emp_id = int(self.tree.item(selection[0])['tags'][0])
        year = int(self.year_combo.get())
        month = int(self.month_combo.get())
        
        # 급여 데이터 조회
        payroll = self.db.get_payroll(emp_id, year, month)
        
        if not payroll:
            messagebox.showwarning("경고", "급여 데이터가 없습니다.\n먼저 급여를 계산하세요.")
            return
        
        # 상세 다이얼로그 표시
        PayrollDetailDialog(self, payroll, self.db)


class PayrollDetailDialog(ctk.CTkToplevel):
    """급여 상세 다이얼로그"""
    
    def __init__(self, parent, payroll: dict, db: Database):
        super().__init__(parent)
        
        self.payroll = payroll
        self.db = db
        
        # 직원 정보 조회
        employee = db.get_employee(payroll['emp_id'])
        
        self.title(f"급여 명세서 - {employee['name']} ({payroll['pay_year']}년 {payroll['pay_month']}월)")
        self.geometry("700x900")
        self.transient(parent)
        self.grab_set()
        
        self.create_widgets(employee)
    
    def create_widgets(self, employee: dict):
        """위젯 생성"""
        scroll = ctk.CTkScrollableFrame(self, width=650, height=800)
        scroll.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 헤더
        header = ctk.CTkFrame(scroll, fg_color=("gray80", "gray25"), corner_radius=10)
        header.pack(fill="x", padx=10, pady=(10, 20))
        
        ctk.CTkLabel(
            header,
            text="💰 급여 명세서",
            font=ctk.CTkFont(size=28, weight="bold")
        ).pack(pady=15)
        
        ctk.CTkLabel(
            header,
            text=f"{self.payroll['pay_year']}년 {self.payroll['pay_month']}월",
            font=ctk.CTkFont(size=18)
        ).pack(pady=(0, 15))
        
        # 직원 정보
        self.create_section(scroll, "👤 직원 정보", [
            ("직원코드", employee['emp_code']),
            ("이름", employee['name']),
            ("부서", employee.get('department', '-')),
            ("직급", employee.get('position', '-')),
            ("시급", f"{employee['hourly_wage']:,.0f}원")
        ])
        
        # 근무 시간
        self.create_section(scroll, "⏰ 근무 시간", [
            ("총 근무일수", f"{self.payroll['total_work_days']:.1f}일"),
            ("정규 근무시간", f"{self.payroll['regular_hours']:.1f}시간"),
            ("잔업 시간", f"{self.payroll['overtime_hours']:.1f}시간"),
            ("  └ 1구간", f"{self.payroll['overtime_tier1_minutes']:.0f}분"),
            ("  └ 2구간", f"{self.payroll['overtime_tier2_minutes']:.0f}분"),
            ("  └ 3구간", f"{self.payroll['overtime_tier3_minutes']:.0f}분"),
            ("야간 근무시간", f"{self.payroll['night_hours']:.1f}시간"),
            ("휴일 근무시간", f"{self.payroll['holiday_hours']:.1f}시간")
        ])
        
        # 지급 내역
        self.create_section(scroll, "💵 지급 내역", [
            ("기본급", f"{self.payroll['base_pay']:,.0f}원"),
            ("잔업 수당", f"{self.payroll['overtime_pay']:,.0f}원"),
            ("야간 수당", f"{self.payroll['night_pay']:,.0f}원"),
            ("휴일 수당", f"{self.payroll['holiday_pay']:,.0f}원"),
            ("주휴 수당", f"{self.payroll['weekly_holiday_pay']:,.0f}원"),
            ("식대", f"{self.payroll['meal_allowance']:,.0f}원"),
            ("기타 수당", f"{self.payroll.get('other_allowance', 0):,.0f}원")
        ], highlight_last=True, last_label="총 지급액", last_value=f"{self.payroll['total_pay']:,.0f}원")
        
        # 공제 내역
        self.create_section(scroll, "➖ 공제 내역", [
            ("국민연금", f"{self.payroll['national_pension']:,.0f}원"),
            ("건강보험", f"{self.payroll['health_insurance']:,.0f}원"),
            ("장기요양보험", f"{self.payroll['long_term_care']:,.0f}원"),
            ("고용보험", f"{self.payroll['employment_insurance']:,.0f}원"),
            ("소득세", f"{self.payroll['income_tax']:,.0f}원"),
            ("지방소득세", f"{self.payroll['local_tax']:,.0f}원"),
            ("기타 공제", f"{self.payroll.get('other_deduction', 0):,.0f}원")
        ], highlight_last=True, last_label="총 공제액", last_value=f"{self.payroll['total_deduction']:,.0f}원")
        
        # 실수령액
        net_frame = ctk.CTkFrame(scroll, fg_color=("blue", "darkblue"), corner_radius=10)
        net_frame.pack(fill="x", padx=10, pady=20)
        
        ctk.CTkLabel(
            net_frame,
            text="실수령액",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        ).pack(side="left", padx=30, pady=20)
        
        ctk.CTkLabel(
            net_frame,
            text=f"{self.payroll['net_pay']:,.0f}원",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="white"
        ).pack(side="right", padx=30, pady=20)
        
        # 버튼들
        btn_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=20)
        
        print_btn = ctk.CTkButton(
            btn_frame,
            text="🖨️ 인쇄/저장",
            command=self.print_payslip,
            height=45,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        print_btn.pack(fill="x", pady=5)
        
        close_btn = ctk.CTkButton(
            btn_frame,
            text="닫기",
            command=self.destroy,
            height=40,
            fg_color=("gray70", "gray30")
        )
        close_btn.pack(fill="x", pady=5)
    
    def create_section(self, parent, title: str, items: list, 
                      highlight_last: bool = False, last_label: str = "", last_value: str = ""):
        """섹션 생성"""
        section = ctk.CTkFrame(parent, fg_color=("gray85", "gray20"), corner_radius=10)
        section.pack(fill="x", padx=10, pady=10)
        
        # 제목
        ctk.CTkLabel(
            section,
            text=title,
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(15, 10), padx=20, anchor="w")
        
        # 항목들
        for label, value in items:
            item_frame = ctk.CTkFrame(section, fg_color="transparent")
            item_frame.pack(fill="x", padx=20, pady=3)
            
            ctk.CTkLabel(
                item_frame,
                text=label,
                font=ctk.CTkFont(size=14),
                anchor="w"
            ).pack(side="left")
            
            ctk.CTkLabel(
                item_frame,
                text=value,
                font=ctk.CTkFont(size=14, weight="bold"),
                anchor="e"
            ).pack(side="right")
        
        # 하이라이트 항목
        if highlight_last:
            separator = ctk.CTkFrame(section, height=2, fg_color=("gray70", "gray40"))
            separator.pack(fill="x", padx=20, pady=10)
            
            total_frame = ctk.CTkFrame(section, fg_color="transparent")
            total_frame.pack(fill="x", padx=20, pady=(5, 15))
            
            ctk.CTkLabel(
                total_frame,
                text=last_label,
                font=ctk.CTkFont(size=16, weight="bold"),
                anchor="w"
            ).pack(side="left")
            
            ctk.CTkLabel(
                total_frame,
                text=last_value,
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color=("blue", "lightblue"),
                anchor="e"
            ).pack(side="right")
        else:
            ctk.CTkLabel(section, text="").pack(pady=5)  # 여백
    
    def print_payslip(self):
        """급여명세서 인쇄/저장"""
        messagebox.showinfo("안내", "급여명세서 PDF/Excel 저장 기능은 곧 추가됩니다")
