"""
급여관리 ERP v2.0 - 시스템 초기화 및 테스트
모든 모듈을 초기화하고 샘플 데이터로 테스트
"""

from datetime import datetime, timedelta
import random

from config_manager import ConfigManager, WorkSchedule, OvertimeRate
from database_v2 import Database
from payroll_calculator_v2 import AdvancedPayrollCalculator
from secom_integration import SecomIntegration


def initialize_system():
    """시스템 초기화"""
    print("=" * 70)
    print("🚀 급여관리 ERP v2.0 시스템 초기화")
    print("=" * 70)
    
    # 1. 설정 관리자 초기화
    print("\n1️⃣ 설정 관리자 초기화...")
    config = ConfigManager()
    config.initialize_tables()
    print("   ✅ 근무 스케줄, 잔업 계수, 시스템 설정 초기화 완료")
    
    # 2. 데이터베이스 초기화
    print("\n2️⃣ 데이터베이스 초기화...")
    db = Database()
    db.create_tables()
    print("   ✅ 직원, 근태, 급여, 세콤 로그 테이블 생성 완료")
    
    # 3. 세콤 템플릿 생성
    print("\n3️⃣ 세콤 CSV 템플릿 생성...")
    secom = SecomIntegration()
    secom.create_secom_csv_template("secom_template.csv")
    print("   ✅ 세콤 템플릿 생성 완료")
    
    print("\n" + "=" * 70)
    print("✅ 시스템 초기화 완료!")
    print("=" * 70)


def create_test_data():
    """테스트 데이터 생성"""
    print("\n" + "=" * 70)
    print("📊 테스트 데이터 생성")
    print("=" * 70)
    
    db = Database()
    calc = AdvancedPayrollCalculator()
    
    # 1. 직원 데이터 생성
    print("\n1️⃣ 직원 정보 생성...")
    
    test_employees = [
        {
            'emp_code': 'EMP001',
            'name': '김주간',
            'department': '생산1팀',
            'position': '팀장',
            'hire_date': '2023-01-01',
            'hourly_wage': 25000,
            'work_schedule_id': 'DAY_SHIFT',
            'phone': '010-1111-1111',
            'bank_name': 'KB국민은행',
            'account_number': '123-456-789',
            'secom_employee_id': 'SEC001',
            'secom_card_number': 'CARD001'
        },
        {
            'emp_code': 'EMP002',
            'name': '이야간',
            'department': '생산1팀',
            'position': '대리',
            'hire_date': '2023-03-01',
            'hourly_wage': 23000,
            'work_schedule_id': 'NIGHT_SHIFT',
            'phone': '010-2222-2222',
            'bank_name': '신한은행',
            'account_number': '234-567-890',
            'secom_employee_id': 'SEC002',
            'secom_card_number': 'CARD002'
        },
        {
            'emp_code': 'EMP003',
            'name': '박2교대',
            'department': '생산2팀',
            'position': '사원',
            'hire_date': '2024-01-01',
            'hourly_wage': 20000,
            'work_schedule_id': 'SHIFT_2W_DAY',
            'phone': '010-3333-3333',
            'bank_name': '우리은행',
            'account_number': '345-678-901',
            'secom_employee_id': 'SEC003',
            'secom_card_number': 'CARD003'
        },
        {
            'emp_code': 'EMP004',
            'name': '최야간교대',
            'department': '생산2팀',
            'position': '사원',
            'hire_date': '2024-01-01',
            'hourly_wage': 20000,
            'work_schedule_id': 'SHIFT_2W_NIGHT',
            'phone': '010-4444-4444',
            'bank_name': 'NH농협',
            'account_number': '456-789-012',
            'secom_employee_id': 'SEC004',
            'secom_card_number': 'CARD004'
        },
    ]
    
    emp_ids = []
    for emp_data in test_employees:
        success, emp_id = db.add_employee(emp_data)
        if success:
            emp_ids.append(emp_id)
            schedule_name = emp_data['work_schedule_id']
            print(f"   ✅ {emp_data['name']} ({schedule_name}) - 시급 {emp_data['hourly_wage']:,}원")
        else:
            print(f"   ⚠️ {emp_data['name']} 추가 실패 (이미 존재할 수 있음)")
    
    # 2. 근태 데이터 생성 (12월 한 달)
    print("\n2️⃣ 근태 기록 생성 (2024년 12월)...")
    
    attendance_count = 0
    
    # 12월 1일부터 31일까지
    for day in range(1, 32):
        work_date = f"2024-12-{day:02d}"
        date_obj = datetime(2024, 12, day)
        
        # 주말 제외
        if date_obj.weekday() >= 5:
            continue
        
        # 각 직원별 근태 생성
        for emp_data in test_employees:
            # 80% 확률로 출근
            if random.random() < 0.8:
                # 직원 ID 찾기
                db.connect()
                db.cursor.execute("SELECT emp_id FROM employees WHERE emp_code = ?", 
                                (emp_data['emp_code'],))
                result = db.cursor.fetchone()
                db.close()
                
                if not result:
                    continue
                
                emp_id = result['emp_id']
                schedule_id = emp_data['work_schedule_id']
                
                # 근무 스케줄에 따른 출퇴근 시간
                config = ConfigManager()
                schedule = config.get_schedule(schedule_id)
                
                if not schedule:
                    continue
                
                # 기본 출퇴근 시간
                base_in = schedule['work_start_time']
                base_out = schedule['work_end_time']
                
                # 약간의 변동 (±10분)
                in_variation = random.randint(-10, 10)
                out_variation = random.randint(-10, 30)  # 퇴근은 최대 30분 늦게
                
                # 잔업 (20% 확률)
                if random.random() < 0.2:
                    overtime_minutes = random.randint(30, 180)
                    out_variation += overtime_minutes
                
                # 시간 계산
                in_time = datetime.strptime(base_in, "%H:%M")
                in_time += timedelta(minutes=in_variation)
                clock_in = in_time.strftime("%H:%M")
                
                out_time = datetime.strptime(base_out, "%H:%M")
                out_time += timedelta(minutes=out_variation)
                clock_out = out_time.strftime("%H:%M")
                
                # 근무시간 계산
                work_info = calc.calculate_work_hours_by_schedule(
                    emp_id, work_date, clock_in, clock_out
                )
                
                # 근태 저장
                attendance_data = {
                    'emp_id': emp_id,
                    'work_date': work_date,
                    'clock_in': clock_in,
                    'clock_out': clock_out,
                    'actual_clock_in': clock_in,
                    'actual_clock_out': clock_out,
                    'work_hours': work_info['work_hours'],
                    'regular_hours': work_info['regular_hours'],
                    'break_hours': work_info['break_hours'],
                    'overtime_hours': work_info['overtime_hours'],
                    'night_hours': work_info['night_hours'],
                    'overtime_tier1_minutes': work_info['overtime_tier1_minutes'],
                    'overtime_tier2_minutes': work_info['overtime_tier2_minutes'],
                    'overtime_tier3_minutes': work_info['overtime_tier3_minutes'],
                    'work_schedule_id': schedule_id,
                    'secom_sync': 1,
                    'secom_sync_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                success, _ = db.add_attendance(attendance_data)
                if success:
                    attendance_count += 1
    
    print(f"   ✅ 총 {attendance_count}건의 근태 기록 생성")
    
    # 3. 식대 데이터 생성
    print("\n3️⃣ 식대 기록 생성...")
    
    meal_count = 0
    for emp_data in test_employees:
        db.connect()
        db.cursor.execute("SELECT emp_id FROM employees WHERE emp_code = ?", 
                        (emp_data['emp_code'],))
        result = db.cursor.fetchone()
        
        if result:
            emp_id = result['emp_id']
            
            # 해당 직원의 12월 근무일 조회
            db.cursor.execute("""
                SELECT work_date FROM attendance 
                WHERE emp_id = ? AND strftime('%Y-%m', work_date) = '2024-12'
            """, (emp_id,))
            
            work_dates = db.cursor.fetchall()
            db.close()
            
            for row in work_dates:
                work_date = row['work_date']
                
                # 식대 추가
                db.connect()
                db.cursor.execute("""
                    INSERT OR IGNORE INTO meal_allowance (emp_id, meal_date, meal_type, amount)
                    VALUES (?, ?, ?, ?)
                """, (emp_id, work_date, 'lunch', 10000))
                db.conn.commit()
                db.close()
                
                meal_count += 1
    
    print(f"   ✅ 총 {meal_count}건의 식대 기록 생성")
    
    # 4. 급여 계산
    print("\n4️⃣ 12월 급여 계산...")
    
    employees = db.get_all_employees()
    
    for emp in employees:
        payroll = calc.calculate_monthly_payroll(emp['emp_id'], 2024, 12)
        
        if payroll:
            calc.save_payroll(payroll)
            print(f"   ✅ {emp['name']}: 실수령액 {payroll['net_pay']:,.0f}원")
            print(f"      - 기본급: {payroll['base_pay']:,.0f}원")
            print(f"      - 잔업수당: {payroll['overtime_pay']:,.0f}원")
            print(f"      - 야간수당: {payroll['night_pay']:,.0f}원")
            print(f"      - 주휴수당: {payroll['weekly_holiday_pay']:,.0f}원")
    
    print("\n" + "=" * 70)
    print("✅ 테스트 데이터 생성 완료!")
    print("=" * 70)


def show_statistics():
    """통계 표시"""
    print("\n" + "=" * 70)
    print("📈 시스템 통계")
    print("=" * 70)
    
    config = ConfigManager()
    db = Database()
    
    # 1. 근무 스케줄
    print("\n📋 등록된 근무 스케줄:")
    schedules = config.get_all_schedules()
    for s in schedules:
        print(f"   - {s['schedule_name']}: {s['work_start_time']}~{s['work_end_time']}")
    
    # 2. 잔업 계수
    print("\n💰 잔업 수당 계수:")
    rates = config.get_all_overtime_rates()
    for r in rates:
        end = f"{r['end_minutes']}분" if r['end_minutes'] else "무제한"
        print(f"   - {r['tier_name']}: {r['start_minutes']}~{end} = {r['rate_multiplier']}배")
    
    # 3. 직원 통계
    db.connect()
    db.cursor.execute("SELECT COUNT(*) FROM employees WHERE resignation_date IS NULL")
    emp_count = db.cursor.fetchone()[0]
    print(f"\n👥 재직 직원: {emp_count}명")
    
    # 4. 근태 통계
    db.cursor.execute("SELECT COUNT(*) FROM attendance WHERE strftime('%Y-%m', work_date) = '2024-12'")
    att_count = db.cursor.fetchone()[0]
    print(f"⏰ 12월 근태 기록: {att_count}건")
    
    # 5. 급여 통계
    db.cursor.execute("""
        SELECT 
            COUNT(*) as payroll_count,
            SUM(total_pay) as total_payment,
            SUM(net_pay) as total_net_pay
        FROM payroll 
        WHERE pay_year = 2024 AND pay_month = 12
    """)
    payroll_stats = db.cursor.fetchone()
    db.close()
    
    print(f"💰 12월 급여:")
    print(f"   - 처리 완료: {payroll_stats['payroll_count']}명")
    print(f"   - 총 지급액: {payroll_stats['total_payment']:,.0f}원")
    print(f"   - 실수령액 합계: {payroll_stats['total_net_pay']:,.0f}원")
    
    print("\n" + "=" * 70)


def main():
    """메인 실행"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  💼 급여관리 ERP v2.0 - 시스템 초기화 & 테스트".center(80) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")
    
    # 1. 시스템 초기화
    initialize_system()
    
    # 2. 테스트 데이터 생성
    create_test_data()
    
    # 3. 통계 표시
    show_statistics()
    
    # 4. 완료 메시지
    print("\n" + "🎉" * 35)
    print("\n✅ 모든 초기화가 완료되었습니다!")
    print("\n📝 다음 단계:")
    print("   1. python main_app_v2.py 실행")
    print("   2. 대시보드에서 데이터 확인")
    print("   3. 각 기능 테스트")
    print("\n" + "🎉" * 35)
    print()


if __name__ == "__main__":
    main()
