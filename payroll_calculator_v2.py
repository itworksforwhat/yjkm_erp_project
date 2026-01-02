"""
급여 계산 엔진 v2.0
근무 형태별 계산, 차등 잔업 수당, 세콤 데이터 처리
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from config_manager import ConfigManager
from database_v2 import Database

class AdvancedPayrollCalculator:
    """
    고급 급여 계산 엔진
    - 근무 형태별 차등 계산
    - 시간대별 차등 잔업 수당
    - 세콤 데이터 자동 처리
    """
    
    def __init__(self, db_path: str = "payroll.db"):
        """
        계산 엔진 초기화
        
        Args:
            db_path: 데이터베이스 경로
        """
        self.db = Database(db_path)
        self.config = ConfigManager(db_path)
        
    def calculate_time_difference(self, start_time: str, end_time: str) -> float:
        """
        시간 차이 계산 (HH:MM 형식)
        
        Args:
            start_time: 시작 시간 "HH:MM"
            end_time: 종료 시간 "HH:MM"
            
        Returns:
            시간 차이 (시간 단위)
        """
        try:
            start = datetime.strptime(start_time, "%H:%M")
            end = datetime.strptime(end_time, "%H:%M")
            
            # 다음날로 넘어가는 경우
            if end < start:
                end += timedelta(days=1)
            
            diff = end - start
            hours = diff.total_seconds() / 3600
            
            return round(hours, 2)
        except:
            return 0
    
    def calculate_night_hours(self, clock_in: str, clock_out: str, 
                            night_start: str = "22:00", night_end: str = "06:00") -> float:
        """
        야간 근무 시간 계산
        
        Args:
            clock_in: 출근 시간
            clock_out: 퇴근 시간
            night_start: 야간 시작 시간
            night_end: 야간 종료 시간
            
        Returns:
            야간 근무 시간
        """
        try:
            # 시간 파싱
            work_start = datetime.strptime(clock_in, "%H:%M")
            work_end = datetime.strptime(clock_out, "%H:%M")
            
            # 다음날로 넘어가는 경우
            if work_end < work_start:
                work_end += timedelta(days=1)
            
            # 야간 시간대 설정
            night_start_time = datetime.strptime(night_start, "%H:%M")
            night_end_time = datetime.strptime(night_end, "%H:%M")
            
            # 야간 종료가 다음날인 경우
            if night_end_time < night_start_time:
                night_end_time += timedelta(days=1)
            
            night_hours = 0
            
            # 22:00 ~ 24:00 구간
            if work_start.hour < 22 or work_start.day != night_start_time.day:
                period1_start = max(work_start, night_start_time)
                period1_end = min(work_end, night_start_time + timedelta(hours=2))
                
                if period1_end > period1_start:
                    night_hours += (period1_end - period1_start).total_seconds() / 3600
            
            # 00:00 ~ 06:00 구간
            midnight = night_start_time + timedelta(hours=2)
            period2_start = max(work_start if work_start > midnight else midnight, midnight)
            period2_end = min(work_end, night_end_time)
            
            if period2_end > period2_start:
                night_hours += (period2_end - period2_start).total_seconds() / 3600
            
            return round(night_hours, 2)
            
        except Exception as e:
            print(f"야간시간 계산 오류: {e}")
            return 0
    
    def calculate_work_hours_by_schedule(self, emp_id: int, work_date: str,
                                        clock_in: str, clock_out: str) -> Dict:
        """
        근무 스케줄에 따른 근무시간 계산
        
        Args:
            emp_id: 직원 ID
            work_date: 근무일
            clock_in: 출근 시간
            clock_out: 퇴근 시간
            
        Returns:
            근무시간 상세 정보
        """
        # 직원 정보 조회
        employee = self.db.get_employee(emp_id)
        if not employee:
            return self._empty_work_hours()
        
        # 근무 스케줄 조회
        schedule_id = employee.get('work_schedule_id', 'DAY_SHIFT')
        schedule = self.config.get_schedule(schedule_id)
        
        if not schedule:
            return self._empty_work_hours()
        
        # 총 근무시간 계산
        total_work_hours = self.calculate_time_difference(clock_in, clock_out)
        
        # 휴게시간 차감
        break_hours = schedule['break_time_minutes'] / 60
        actual_work_hours = max(total_work_hours - break_hours, 0)
        
        # 정규 근무시간 (스케줄 기준)
        scheduled_hours = self.calculate_time_difference(
            schedule['work_start_time'],
            schedule['work_end_time']
        ) - break_hours
        
        # 정규/잔업 구분
        regular_hours = min(actual_work_hours, scheduled_hours)
        overtime_total_minutes = max((actual_work_hours - scheduled_hours) * 60, 0)
        
        # 잔업 시간대별 분류
        overtime_tiers = self._classify_overtime(overtime_total_minutes)
        
        # 야간 근무시간 계산
        night_hours = self.calculate_night_hours(
            clock_in, clock_out,
            schedule['night_start_time'],
            schedule['night_end_time']
        )
        
        return {
            'total_hours': total_work_hours,
            'break_hours': break_hours,
            'work_hours': actual_work_hours,
            'regular_hours': regular_hours,
            'overtime_hours': overtime_total_minutes / 60,
            'overtime_tier1_minutes': overtime_tiers['tier1'],
            'overtime_tier2_minutes': overtime_tiers['tier2'],
            'overtime_tier3_minutes': overtime_tiers['tier3'],
            'night_hours': night_hours,
            'schedule_id': schedule_id
        }
    
    def _classify_overtime(self, total_overtime_minutes: float) -> Dict:
        """
        잔업 시간을 구간별로 분류
        
        Args:
            total_overtime_minutes: 총 잔업 시간 (분)
            
        Returns:
            구간별 잔업 시간
        """
        rates = self.config.get_all_overtime_rates()
        
        tiers = {
            'tier1': 0,
            'tier2': 0,
            'tier3': 0
        }
        
        remaining = total_overtime_minutes
        
        for idx, rate in enumerate(rates):
            if remaining <= 0:
                break
            
            tier_start = rate['start_minutes']
            tier_end = rate['end_minutes'] if rate['end_minutes'] else 999999
            tier_range = tier_end - tier_start
            
            if total_overtime_minutes > tier_start:
                applicable = min(remaining, tier_range)
                
                tier_key = f"tier{idx + 1}"
                if tier_key in tiers:
                    tiers[tier_key] = applicable
                
                remaining -= applicable
        
        return tiers
    
    def _empty_work_hours(self) -> Dict:
        """빈 근무시간 데이터"""
        return {
            'total_hours': 0,
            'break_hours': 0,
            'work_hours': 0,
            'regular_hours': 0,
            'overtime_hours': 0,
            'overtime_tier1_minutes': 0,
            'overtime_tier2_minutes': 0,
            'overtime_tier3_minutes': 0,
            'night_hours': 0,
            'schedule_id': 'DAY_SHIFT'
        }
    
    def calculate_weekly_holiday_pay(self, emp_id: int, year: int, month: int, 
                                    hourly_wage: float) -> float:
        """
        주휴수당 계산
        
        Args:
            emp_id: 직원 ID
            year: 년도
            month: 월
            hourly_wage: 시급
            
        Returns:
            주휴수당
        """
        # 해당 월의 근태 기록 조회
        start_date = f"{year}-{month:02d}-01"
        
        # 월 마지막 날
        import calendar
        last_day = calendar.monthrange(year, month)[1]
        end_date = f"{year}-{month:02d}-{last_day:02d}"
        
        records = self.db.get_attendance_by_date_range(emp_id, start_date, end_date)
        
        # 주차별 근무시간 집계
        weekly_hours = {}
        
        for record in records:
            date_obj = datetime.strptime(record['work_date'], "%Y-%m-%d")
            iso_year, iso_week, _ = date_obj.isocalendar()
            week_key = f"{iso_year}-W{iso_week}"
            
            if week_key not in weekly_hours:
                weekly_hours[week_key] = 0
            
            weekly_hours[week_key] += record.get('work_hours', 0) or 0
        
        # 주 15시간 이상 근무한 주 개수
        eligible_weeks = sum(1 for hours in weekly_hours.values() if hours >= 15)
        
        # 주휴수당 = 적격 주수 × 8시간 × 시급
        weekly_holiday_pay = eligible_weeks * 8 * hourly_wage
        
        return round(weekly_holiday_pay, 0)
    
    def calculate_insurance(self, total_pay: float) -> Dict:
        """
        4대보험 계산
        
        Args:
            total_pay: 총 지급액
            
        Returns:
            4대보험 내역
        """
        np_rate = self.config.get_setting('national_pension_rate', 0.045)
        hi_rate = self.config.get_setting('health_insurance_rate', 0.03545)
        ltc_rate = self.config.get_setting('long_term_care_rate', 0.1295)
        ei_rate = self.config.get_setting('employment_insurance_rate', 0.009)
        
        national_pension = round(total_pay * np_rate)
        health_insurance = round(total_pay * hi_rate)
        long_term_care = round(health_insurance * ltc_rate)
        employment_insurance = round(total_pay * ei_rate)
        
        return {
            'national_pension': national_pension,
            'health_insurance': health_insurance,
            'long_term_care': long_term_care,
            'employment_insurance': employment_insurance
        }
    
    def calculate_income_tax(self, total_pay: float) -> Tuple[float, float]:
        """
        소득세 및 지방소득세 계산
        
        Args:
            total_pay: 총 급여액
            
        Returns:
            (소득세, 지방소득세)
        """
        monthly_pay = total_pay
        
        # 간이세액표 (단순화)
        if monthly_pay <= 1060000:
            income_tax = 0
        elif monthly_pay <= 2060000:
            income_tax = (monthly_pay - 1060000) * 0.06
        elif monthly_pay <= 4060000:
            income_tax = 60000 + (monthly_pay - 2060000) * 0.15
        elif monthly_pay <= 6060000:
            income_tax = 360000 + (monthly_pay - 4060000) * 0.24
        else:
            income_tax = 840000 + (monthly_pay - 6060000) * 0.35
        
        income_tax = round(income_tax)
        local_tax = round(income_tax * 0.1)
        
        return income_tax, local_tax
    
    def calculate_monthly_payroll(self, emp_id: int, year: int, month: int) -> Optional[Dict]:
        """
        월 급여 종합 계산
        
        Args:
            emp_id: 직원 ID
            year: 년도
            month: 월
            
        Returns:
            급여 계산 결과
        """
        # 직원 정보 조회
        employee = self.db.get_employee(emp_id)
        if not employee:
            print(f"❌ 직원 정보 없음: {emp_id}")
            return None
        
        hourly_wage = employee['hourly_wage']
        
        # 해당 월의 근태 기록 조회
        start_date = f"{year}-{month:02d}-01"
        import calendar
        last_day = calendar.monthrange(year, month)[1]
        end_date = f"{year}-{month:02d}-{last_day:02d}"
        
        records = self.db.get_attendance_by_date_range(emp_id, start_date, end_date)
        
        # 근무시간 집계
        total_work_days = len(records)
        regular_hours = sum(r.get('regular_hours', 0) or 0 for r in records)
        overtime_hours = sum(r.get('overtime_hours', 0) or 0 for r in records)
        night_hours = sum(r.get('night_hours', 0) or 0 for r in records)
        holiday_hours = sum(r.get('holiday_hours', 0) or 0 for r in records)
        
        # 잔업 시간대별 집계
        overtime_tier1 = sum(r.get('overtime_tier1_minutes', 0) or 0 for r in records)
        overtime_tier2 = sum(r.get('overtime_tier2_minutes', 0) or 0 for r in records)
        overtime_tier3 = sum(r.get('overtime_tier3_minutes', 0) or 0 for r in records)
        
        # 기본급 계산
        base_pay = round(regular_hours * hourly_wage)
        
        # 잔업 수당 계산 (차등 적용)
        overtime_pay = self.config.calculate_overtime_pay(
            overtime_tier1 + overtime_tier2 + overtime_tier3,
            hourly_wage
        )
        
        # 야간 수당
        night_pay = round(night_hours * hourly_wage * 0.5)
        
        # 휴일 수당
        holiday_pay = round(holiday_hours * hourly_wage * 1.5)
        
        # 주휴수당
        weekly_holiday_pay = self.calculate_weekly_holiday_pay(emp_id, year, month, hourly_wage)
        
        # 식대 조회
        self.db.connect()
        self.db.cursor.execute("""
            SELECT COALESCE(SUM(amount), 0)
            FROM meal_allowance
            WHERE emp_id = ?
            AND strftime('%Y', meal_date) = ?
            AND strftime('%m', meal_date) = ?
        """, (emp_id, str(year), str(month).zfill(2)))
        
        meal_allowance = self.db.cursor.fetchone()[0]
        self.db.close()
        
        # 총 지급액
        total_pay = (base_pay + overtime_pay + night_pay + holiday_pay + 
                    weekly_holiday_pay + meal_allowance)
        
        # 4대보험
        insurance = self.calculate_insurance(total_pay)
        
        # 소득세
        income_tax, local_tax = self.calculate_income_tax(total_pay)
        
        # 총 공제액
        total_deduction = (
            insurance['national_pension'] +
            insurance['health_insurance'] +
            insurance['long_term_care'] +
            insurance['employment_insurance'] +
            income_tax +
            local_tax
        )
        
        # 실수령액
        net_pay = total_pay - total_deduction
        
        return {
            'emp_id': emp_id,
            'emp_name': employee['name'],
            'pay_year': year,
            'pay_month': month,
            'hourly_wage': hourly_wage,
            
            # 근무 시간
            'total_work_days': total_work_days,
            'regular_hours': regular_hours,
            'overtime_hours': overtime_hours,
            'night_hours': night_hours,
            'holiday_hours': holiday_hours,
            
            # 잔업 시간대별
            'overtime_tier1_minutes': overtime_tier1,
            'overtime_tier2_minutes': overtime_tier2,
            'overtime_tier3_minutes': overtime_tier3,
            
            # 지급 항목
            'base_pay': base_pay,
            'overtime_pay': overtime_pay,
            'night_pay': night_pay,
            'holiday_pay': holiday_pay,
            'weekly_holiday_pay': weekly_holiday_pay,
            'meal_allowance': meal_allowance,
            'total_pay': total_pay,
            
            # 공제 항목
            'national_pension': insurance['national_pension'],
            'health_insurance': insurance['health_insurance'],
            'long_term_care': insurance['long_term_care'],
            'employment_insurance': insurance['employment_insurance'],
            'income_tax': income_tax,
            'local_tax': local_tax,
            'total_deduction': total_deduction,
            
            # 실수령액
            'net_pay': net_pay
        }
    
    def save_payroll(self, payroll_data: Dict) -> bool:
        """급여 데이터 저장"""
        return self.db.save_payroll(payroll_data)


# 테스트 코드
if __name__ == "__main__":
    print("=" * 60)
    print("급여 계산 엔진 v2.0 테스트")
    print("=" * 60)
    
    calc = AdvancedPayrollCalculator()
    
    print("\n🧮 차등 잔업 수당 계산 테스트:")
    test_cases = [30, 90, 150, 200]
    for minutes in test_cases:
        pay = calc.config.calculate_overtime_pay(minutes, 20000)
        print(f"  - {minutes}분 잔업 (시급 20,000원) = {pay:,.0f}원")
    
    print("\n✅ 급여 계산 엔진 준비 완료!")
