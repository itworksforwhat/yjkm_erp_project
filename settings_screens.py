"""
설정 화면 모듈
근무 시간, 잔업 계수, 휴가 정책을 GUI에서 자유롭게 설정
"""

import customtkinter as ctk
from tkinter import messagebox, ttk
from config_manager import ConfigManager, WorkSchedule, OvertimeRate
from leave_manager import LeaveManager


class WorkScheduleSettingsFrame(ctk.CTkFrame):
    """근무 형태 설정 화면"""
    
    def __init__(self, parent, config: ConfigManager):
        super().__init__(parent)
        self.config = config
        self.create_widgets()
        self.refresh_list()
    
    def create_widgets(self):
        """위젯 생성"""
        # 제목
        title = ctk.CTkLabel(
            self,
            text="🔧 근무 형태 설정",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title.pack(pady=(25, 15), padx=35, anchor="w")
        
        # 설명
        desc = ctk.CTkLabel(
            self,
            text="근무 형태를 추가/수정하여 직원별로 다른 근무시간을 적용할 수 있습니다.",
            font=ctk.CTkFont(size=14),
            text_color=("gray50", "gray60")
        )
        desc.pack(pady=(0, 20), padx=35, anchor="w")
        
        # 버튼 영역
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=35, pady=(0, 15))
        
        add_btn = ctk.CTkButton(
            btn_frame,
            text="➕ 새 근무 형태 추가",
            command=self.add_schedule,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        add_btn.pack(side="left")
        
        refresh_btn = ctk.CTkButton(
            btn_frame,
            text="🔄 새로고침",
            command=self.refresh_list,
            height=40,
            width=120,
            fg_color=("gray70", "gray30")
        )
        refresh_btn.pack(side="left", padx=(10, 0))
        
        # 목록 테이블
        list_frame = ctk.CTkFrame(self)
        list_frame.pack(fill="both", expand=True, padx=35, pady=(0, 25))
        
        # Treeview
        columns = ("ID", "이름", "시작시간", "종료시간", "휴게시간", "야간여부", "야간시간대")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        widths = [100, 200, 100, 100, 100, 100, 150]
        for col, width in zip(columns, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="center")
        
        # 스크롤바
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 더블클릭 이벤트
        self.tree.bind("<Double-1>", self.edit_schedule)
    
    def refresh_list(self):
        """목록 새로고침"""
        # 기존 데이터 삭제
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 데이터 조회
        schedules = self.config.get_all_schedules()
        
        for s in schedules:
            night = "야간" if s['is_night_shift'] else "주간"
            night_time = f"{s['night_start_time']}~{s['night_end_time']}"
            
            self.tree.insert("", "end", values=(
                s['schedule_id'],
                s['schedule_name'],
                s['work_start_time'],
                s['work_end_time'],
                f"{s['break_time_minutes']}분",
                night,
                night_time
            ), tags=(s['schedule_id'],))
    
    def add_schedule(self):
        """근무 형태 추가"""
        dialog = ScheduleEditDialog(self, self.config, None)
        self.wait_window(dialog)
        self.refresh_list()
    
    def edit_schedule(self, event):
        """근무 형태 수정"""
        selection = self.tree.selection()
        if not selection:
            return
        
        schedule_id = self.tree.item(selection[0])['tags'][0]
        schedule = self.config.get_schedule(schedule_id)
        
        if schedule:
            dialog = ScheduleEditDialog(self, self.config, schedule)
            self.wait_window(dialog)
            self.refresh_list()


class ScheduleEditDialog(ctk.CTkToplevel):
    """근무 형태 편집 다이얼로그"""
    
    def __init__(self, parent, config: ConfigManager, schedule: dict = None):
        super().__init__(parent)
        
        self.config = config
        self.schedule = schedule
        self.is_edit = schedule is not None
        
        self.title("근무 형태 수정" if self.is_edit else "근무 형태 추가")
        self.geometry("600x700")
        self.transient(parent)
        self.grab_set()
        
        self.create_widgets()
    
    def create_widgets(self):
        """위젯 생성"""
        scroll = ctk.CTkScrollableFrame(self, width=550, height=600)
        scroll.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 기본 정보
        self.create_section_title(scroll, "📋 기본 정보", 0)
        
        if self.is_edit:
            # 수정 모드: ID 표시만
            id_label = ctk.CTkLabel(scroll, text="근무 형태 ID", font=ctk.CTkFont(size=14), anchor="w", width=150)
            id_label.grid(row=1, column=0, pady=8, padx=(20, 10), sticky="w")
            id_value = ctk.CTkLabel(scroll, text=self.schedule['schedule_id'], font=ctk.CTkFont(size=14, weight="bold"))
            id_value.grid(row=1, column=1, pady=8, padx=(10, 20), sticky="w")
            
            self.schedule_id = self.schedule['schedule_id']
            start_row = 2
        else:
            # 추가 모드: ID 입력
            self.id_entry = self.create_input(scroll, "* 근무 형태 ID", 1, "CUSTOM_001", "")
            start_row = 2
        
        self.name_entry = self.create_input(scroll, "* 이름", start_row, "오전근무", 
                                            self.schedule['schedule_name'] if self.is_edit else "")
        
        # 근무 시간
        self.create_section_title(scroll, "⏰ 근무 시간", start_row + 1)
        
        self.start_entry = self.create_input(scroll, "* 시작 시간", start_row + 2, "09:00",
                                             self.schedule['work_start_time'] if self.is_edit else "")
        self.end_entry = self.create_input(scroll, "* 종료 시간", start_row + 3, "18:00",
                                           self.schedule['work_end_time'] if self.is_edit else "")
        self.break_entry = self.create_input(scroll, "* 휴게시간 (분)", start_row + 4, "60",
                                             str(self.schedule['break_time_minutes']) if self.is_edit else "60")
        
        # 야간 근무
        self.create_section_title(scroll, "🌙 야간 근무 설정", start_row + 5)
        
        self.night_var = ctk.BooleanVar(value=self.schedule['is_night_shift'] if self.is_edit else False)
        night_check = ctk.CTkCheckBox(
            scroll,
            text="야간 근무 포함",
            variable=self.night_var,
            font=ctk.CTkFont(size=14),
            command=self.toggle_night_settings
        )
        night_check.grid(row=start_row + 6, column=0, columnspan=2, pady=10, padx=20, sticky="w")
        
        self.night_start_entry = self.create_input(scroll, "야간 시작", start_row + 7, "22:00",
                                                   self.schedule['night_start_time'] if self.is_edit else "22:00")
        self.night_end_entry = self.create_input(scroll, "야간 종료", start_row + 8, "06:00",
                                                 self.schedule['night_end_time'] if self.is_edit else "06:00")
        
        # 설명
        self.create_section_title(scroll, "📝 설명", start_row + 9)
        
        self.desc_text = ctk.CTkTextbox(scroll, height=80, font=ctk.CTkFont(size=14))
        self.desc_text.grid(row=start_row + 10, column=0, columnspan=2, pady=10, padx=20, sticky="ew")
        
        if self.is_edit and self.schedule.get('description'):
            self.desc_text.insert("1.0", self.schedule['description'])
        
        # 저장 버튼
        save_btn = ctk.CTkButton(
            scroll,
            text="💾 저장",
            command=self.save,
            height=45,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        save_btn.grid(row=start_row + 11, column=0, columnspan=2, pady=25, padx=20, sticky="ew")
        
        # 삭제 버튼 (수정 모드일 때만)
        if self.is_edit:
            delete_btn = ctk.CTkButton(
                scroll,
                text="🗑️ 삭제",
                command=self.delete,
                height=40,
                fg_color=("red", "darkred"),
                font=ctk.CTkFont(size=14)
            )
            delete_btn.grid(row=start_row + 12, column=0, columnspan=2, pady=(0, 20), padx=20, sticky="ew")
        
        scroll.grid_columnconfigure(1, weight=1)
        
        # 초기 야간 설정 토글
        self.toggle_night_settings()
    
    def create_section_title(self, parent, title: str, row: int):
        """섹션 제목"""
        label = ctk.CTkLabel(parent, text=title, font=ctk.CTkFont(size=18, weight="bold"), anchor="w")
        label.grid(row=row, column=0, columnspan=2, pady=(20, 10), padx=20, sticky="w")
    
    def create_input(self, parent, label_text: str, row: int, placeholder: str, default: str):
        """입력 필드"""
        label = ctk.CTkLabel(parent, text=label_text, font=ctk.CTkFont(size=14), anchor="w", width=150)
        label.grid(row=row, column=0, pady=8, padx=(20, 10), sticky="w")
        
        entry = ctk.CTkEntry(parent, placeholder_text=placeholder, height=35, font=ctk.CTkFont(size=14))
        entry.grid(row=row, column=1, pady=8, padx=(10, 20), sticky="ew")
        
        if default:
            entry.insert(0, default)
        
        return entry
    
    def toggle_night_settings(self):
        """야간 설정 토글"""
        state = "normal" if self.night_var.get() else "disabled"
        self.night_start_entry.configure(state=state)
        self.night_end_entry.configure(state=state)
    
    def save(self):
        """저장"""
        try:
            # 입력 검증
            if self.is_edit:
                schedule_id = self.schedule_id
            else:
                schedule_id = self.id_entry.get().strip()
                if not schedule_id:
                    messagebox.showerror("오류", "근무 형태 ID를 입력하세요")
                    return
            
            name = self.name_entry.get().strip()
            if not name:
                messagebox.showerror("오류", "이름을 입력하세요")
                return
            
            start_time = self.start_entry.get().strip()
            end_time = self.end_entry.get().strip()
            break_time = self.break_entry.get().strip()
            
            if not all([start_time, end_time, break_time]):
                messagebox.showerror("오류", "근무 시간을 모두 입력하세요")
                return
            
            # 데이터 구성
            schedule_data = WorkSchedule(
                schedule_id=schedule_id,
                schedule_name=name,
                work_start_time=start_time,
                work_end_time=end_time,
                break_time_minutes=int(break_time),
                is_night_shift=self.night_var.get(),
                night_start_time=self.night_start_entry.get().strip(),
                night_end_time=self.night_end_entry.get().strip(),
                description=self.desc_text.get("1.0", "end-1c").strip()
            )
            
            # 저장
            if self.is_edit:
                success = self.config.update_schedule(schedule_data)
                msg = "수정"
            else:
                success = self.config.add_schedule(schedule_data)
                msg = "추가"
            
            if success:
                messagebox.showinfo("성공", f"근무 형태가 {msg}되었습니다!")
                self.destroy()
            else:
                messagebox.showerror("오류", f"{msg} 실패")
        
        except ValueError:
            messagebox.showerror("오류", "숫자 형식이 올바르지 않습니다")
        except Exception as e:
            messagebox.showerror("오류", f"저장 오류:\n{e}")
    
    def delete(self):
        """삭제"""
        result = messagebox.askyesno(
            "확인",
            f"'{self.schedule['schedule_name']}' 근무 형태를 삭제하시겠습니까?\n\n"
            "이 근무 형태를 사용하는 직원이 있을 수 있습니다."
        )
        
        if result:
            # TODO: 실제 삭제 로직 구현
            messagebox.showinfo("안내", "삭제 기능은 곧 추가됩니다")


class OvertimeSettingsFrame(ctk.CTkFrame):
    """잔업 계수 설정 화면"""
    
    def __init__(self, parent, config: ConfigManager):
        super().__init__(parent)
        self.config = config
        self.create_widgets()
        self.refresh_list()
    
    def create_widgets(self):
        """위젯 생성"""
        # 제목
        title = ctk.CTkLabel(
            self,
            text="💸 잔업 수당 계수 설정",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title.pack(pady=(25, 15), padx=35, anchor="w")
        
        # 설명
        desc = ctk.CTkLabel(
            self,
            text="잔업 시간대별로 다른 수당 배율을 설정할 수 있습니다.\n"
                 "예: 0~60분 = 0.5배, 60~120분 = 1.0배, 120분 이상 = 2.0배",
            font=ctk.CTkFont(size=14),
            text_color=("gray50", "gray60"),
            justify="left"
        )
        desc.pack(pady=(0, 20), padx=35, anchor="w")
        
        # 새로고침 버튼
        refresh_btn = ctk.CTkButton(
            self,
            text="🔄 새로고침",
            command=self.refresh_list,
            height=40,
            width=120
        )
        refresh_btn.pack(padx=35, pady=(0, 15), anchor="w")
        
        # 목록 테이블
        list_frame = ctk.CTkFrame(self)
        list_frame.pack(fill="both", expand=True, padx=35, pady=(0, 25))
        
        # Treeview
        columns = ("구간", "이름", "시작(분)", "종료(분)", "배율", "설명")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        
        widths = [80, 150, 100, 100, 80, 250]
        for col, width in zip(columns, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="center")
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 더블클릭 이벤트
        self.tree.bind("<Double-1>", self.edit_rate)
        
        # 안내
        info = ctk.CTkLabel(
            self,
            text="💡 Tip: 항목을 더블클릭하면 수정할 수 있습니다",
            font=ctk.CTkFont(size=13),
            text_color=("blue", "lightblue")
        )
        info.pack(pady=10, padx=35, anchor="w")
    
    def refresh_list(self):
        """목록 새로고침"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        rates = self.config.get_all_overtime_rates()
        
        for r in rates:
            end = f"{r['end_minutes']}" if r['end_minutes'] else "무제한"
            
            self.tree.insert("", "end", values=(
                r['tier_id'],
                r['tier_name'],
                r['start_minutes'],
                end,
                f"{r['rate_multiplier']}배",
                r['description']
            ), tags=(r['tier_id'],))
    
    def edit_rate(self, event):
        """계수 수정"""
        selection = self.tree.selection()
        if not selection:
            return
        
        tier_id = self.tree.item(selection[0])['tags'][0]
        
        # 현재 값 조회
        rates = self.config.get_all_overtime_rates()
        current = None
        for r in rates:
            if r['tier_id'] == tier_id:
                current = r
                break
        
        if current:
            dialog = OvertimeRateEditDialog(self, self.config, current)
            self.wait_window(dialog)
            self.refresh_list()


class OvertimeRateEditDialog(ctk.CTkToplevel):
    """잔업 계수 편집 다이얼로그"""
    
    def __init__(self, parent, config: ConfigManager, rate: dict):
        super().__init__(parent)
        
        self.config = config
        self.rate = rate
        
        self.title(f"잔업 계수 수정 - {rate['tier_name']}")
        self.geometry("500x450")
        self.transient(parent)
        self.grab_set()
        
        self.create_widgets()
    
    def create_widgets(self):
        """위젯 생성"""
        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 구간 ID (표시만)
        label = ctk.CTkLabel(frame, text="구간 ID", font=ctk.CTkFont(size=14), anchor="w")
        label.grid(row=0, column=0, pady=10, padx=20, sticky="w")
        value = ctk.CTkLabel(frame, text=self.rate['tier_id'], font=ctk.CTkFont(size=14, weight="bold"))
        value.grid(row=0, column=1, pady=10, padx=20, sticky="w")
        
        # 이름
        self.name_entry = self.create_input(frame, "* 구간 이름", 1, self.rate['tier_name'])
        
        # 시작 시간
        self.start_entry = self.create_input(frame, "* 시작 (분)", 2, str(self.rate['start_minutes']))
        
        # 종료 시간
        end_val = str(self.rate['end_minutes']) if self.rate['end_minutes'] else ""
        self.end_entry = self.create_input(frame, "종료 (분)", 3, end_val)
        
        end_info = ctk.CTkLabel(
            frame,
            text="(비워두면 무제한)",
            font=ctk.CTkFont(size=12),
            text_color=("gray50", "gray60")
        )
        end_info.grid(row=4, column=1, pady=(0, 10), padx=20, sticky="w")
        
        # 배율
        self.rate_entry = self.create_input(frame, "* 수당 배율", 5, str(self.rate['rate_multiplier']))
        
        rate_info = ctk.CTkLabel(
            frame,
            text="예: 1.5 = 1.5배, 2.0 = 2배",
            font=ctk.CTkFont(size=12),
            text_color=("gray50", "gray60")
        )
        rate_info.grid(row=6, column=1, pady=(0, 10), padx=20, sticky="w")
        
        # 설명
        desc_label = ctk.CTkLabel(frame, text="설명", font=ctk.CTkFont(size=14), anchor="w")
        desc_label.grid(row=7, column=0, pady=10, padx=20, sticky="nw")
        
        self.desc_text = ctk.CTkTextbox(frame, height=80, font=ctk.CTkFont(size=14))
        self.desc_text.grid(row=7, column=1, pady=10, padx=20, sticky="ew")
        
        if self.rate.get('description'):
            self.desc_text.insert("1.0", self.rate['description'])
        
        # 저장 버튼
        save_btn = ctk.CTkButton(
            frame,
            text="💾 저장",
            command=self.save,
            height=45,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        save_btn.grid(row=8, column=0, columnspan=2, pady=20, padx=20, sticky="ew")
        
        frame.grid_columnconfigure(1, weight=1)
    
    def create_input(self, parent, label_text: str, row: int, default: str):
        """입력 필드"""
        label = ctk.CTkLabel(parent, text=label_text, font=ctk.CTkFont(size=14), anchor="w", width=120)
        label.grid(row=row, column=0, pady=10, padx=20, sticky="w")
        
        entry = ctk.CTkEntry(parent, height=35, font=ctk.CTkFont(size=14))
        entry.grid(row=row, column=1, pady=10, padx=20, sticky="ew")
        
        if default:
            entry.insert(0, default)
        
        return entry
    
    def save(self):
        """저장"""
        try:
            # 입력 검증
            name = self.name_entry.get().strip()
            start = self.start_entry.get().strip()
            end = self.end_entry.get().strip()
            rate_mult = self.rate_entry.get().strip()
            
            if not all([name, start, rate_mult]):
                messagebox.showerror("오류", "필수 항목을 모두 입력하세요")
                return
            
            # 데이터 구성
            rate_data = OvertimeRate(
                tier_id=self.rate['tier_id'],
                tier_name=name,
                start_minutes=int(start),
                end_minutes=int(end) if end else None,
                rate_multiplier=float(rate_mult),
                description=self.desc_text.get("1.0", "end-1c").strip()
            )
            
            # 저장
            success = self.config.update_overtime_rate(rate_data)
            
            if success:
                messagebox.showinfo("성공", "잔업 계수가 수정되었습니다!")
                self.destroy()
            else:
                messagebox.showerror("오류", "수정 실패")
        
        except ValueError:
            messagebox.showerror("오류", "숫자 형식이 올바르지 않습니다")
        except Exception as e:
            messagebox.showerror("오류", f"저장 오류:\n{e}")
