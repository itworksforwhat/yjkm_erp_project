"""
교대 근무 스케줄 관리
주/야간 2교대 스케줄 자동 할당 및 관리
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json

from database_v2 import Database
from config_manager import ConfigManager


class ShiftScheduler:
    """
    교대 근무 스케줄러
    2교대 주/야간 교대 근무 자동 할당
    """

    def __init__(self, db_path: str = "payroll.db"):
        """
        스케줄러 초기화

        Args:
            db_path: 데이터베이스 경로
        """
        self.db = Database(db_path)
        self.config = ConfigManager(db_path)

    def assign_biweekly_shift(self, emp_id: int, start_date: str,
                              rotation_weeks: int = 2,
                              start_with_day: bool = True) -> bool:
        """
        직원에게 2교대 스케줄 할당

        Args:
            emp_id: 직원 ID
            start_date: 시작일 (YYYY-MM-DD)
            rotation_weeks: 교대 주기 (주 단위, 기본 2주)
            start_with_day: 주간 근무부터 시작 여부

        Returns:
            성공 여부
        """
        try:
            # 직원의 근무 형태 저장
            shift_config = {
                'emp_id': emp_id,
                'start_date': start_date,
                'rotation_weeks': rotation_weeks,
                'start_with_day': start_with_day,
                'current_shift': 'SHIFT_2W_DAY' if start_with_day else 'SHIFT_2W_NIGHT'
            }

            # 직원 정보 업데이트 (메타 데이터로 저장)
            self.db.connect()
            self.db.cursor.execute("""
                UPDATE employees
                SET notes = ?
                WHERE emp_id = ?
            """, (json.dumps(shift_config, ensure_ascii=False), emp_id))

            self.db.conn.commit()
            self.db.close()

            print(f"✅ 직원 {emp_id}에게 2교대 스케줄 할당 완료")
            return True

        except Exception as e:
            print(f"❌ 스케줄 할당 오류: {e}")
            return False

    def get_shift_for_date(self, emp_id: int, target_date: str) -> Optional[str]:
        """
        특정 날짜의 직원 근무 형태 조회

        Args:
            emp_id: 직원 ID
            target_date: 대상 날짜 (YYYY-MM-DD)

        Returns:
            근무 형태 ID (SHIFT_2W_DAY 또는 SHIFT_2W_NIGHT)
        """
        try:
            # 직원 정보 조회
            emp = self.db.get_employee(emp_id)
            if not emp:
                return None

            # 메타 데이터 파싱
            notes = emp.get('notes', '')
            if not notes:
                # 기본 근무 형태 반환
                return emp.get('work_schedule_id', 'DAY_SHIFT')

            try:
                shift_config = json.loads(notes)
            except:
                # JSON 파싱 실패 시 기본값
                return emp.get('work_schedule_id', 'DAY_SHIFT')

            # 교대 근무 설정이 아닌 경우
            if 'rotation_weeks' not in shift_config:
                return emp.get('work_schedule_id', 'DAY_SHIFT')

            # 시작일부터 경과한 주 수 계산
            start_date = datetime.strptime(shift_config['start_date'], '%Y-%m-%d')
            target = datetime.strptime(target_date, '%Y-%m-%d')

            delta = target - start_date
            weeks_passed = delta.days // 7

            # 교대 주기에 따라 현재 근무 형태 결정
            rotation_weeks = shift_config['rotation_weeks']
            cycle_position = (weeks_passed // rotation_weeks) % 2

            # 시작이 주간이면: 0=주간, 1=야간
            # 시작이 야간이면: 0=야간, 1=주간
            start_with_day = shift_config.get('start_with_day', True)

            if start_with_day:
                return 'SHIFT_2W_DAY' if cycle_position == 0 else 'SHIFT_2W_NIGHT'
            else:
                return 'SHIFT_2W_NIGHT' if cycle_position == 0 else 'SHIFT_2W_DAY'

        except Exception as e:
            print(f"❌ 근무 형태 조회 오류: {e}")
            return None

    def generate_monthly_schedule(self, emp_id: int, year: int, month: int) -> List[Dict]:
        """
        월간 교대 근무 스케줄 생성

        Args:
            emp_id: 직원 ID
            year: 년도
            month: 월

        Returns:
            일별 스케줄 목록
        """
        schedule = []

        # 해당 월의 일 수 계산
        if month == 12:
            next_month = datetime(year + 1, 1, 1)
        else:
            next_month = datetime(year, month + 1, 1)

        current_month = datetime(year, month, 1)
        days_in_month = (next_month - current_month).days

        # 각 날짜별 근무 형태 조회
        for day in range(1, days_in_month + 1):
            date_str = f"{year:04d}-{month:02d}-{day:02d}"
            shift_id = self.get_shift_for_date(emp_id, date_str)

            shift_info = self.config.get_schedule(shift_id) if shift_id else None

            schedule.append({
                'date': date_str,
                'shift_id': shift_id,
                'shift_name': shift_info['schedule_name'] if shift_info else '미지정',
                'work_start': shift_info['work_start_time'] if shift_info else '',
                'work_end': shift_info['work_end_time'] if shift_info else '',
                'is_night': shift_info['is_night_shift'] if shift_info else False
            })

        return schedule

    def get_shift_employees(self, shift_id: str) -> List[Dict]:
        """
        특정 근무 형태에 할당된 직원 목록 조회

        Args:
            shift_id: 근무 형태 ID

        Returns:
            직원 목록
        """
        employees = self.db.get_all_employees(include_resigned=False)

        shift_employees = []
        for emp in employees:
            # 현재 날짜 기준으로 근무 형태 확인
            today = datetime.now().strftime('%Y-%m-%d')
            current_shift = self.get_shift_for_date(emp['emp_id'], today)

            if current_shift == shift_id:
                shift_employees.append(emp)

        return shift_employees

    def bulk_assign_shifts(self, employee_ids: List[int], start_date: str,
                          rotation_weeks: int = 2) -> Tuple[int, int]:
        """
        여러 직원에게 교대 근무 일괄 할당

        Args:
            employee_ids: 직원 ID 리스트
            start_date: 시작일
            rotation_weeks: 교대 주기

        Returns:
            (성공 건수, 실패 건수)
        """
        success_count = 0
        error_count = 0

        for idx, emp_id in enumerate(employee_ids):
            # 짝수 인덱스는 주간, 홀수 인덱스는 야간으로 시작
            start_with_day = (idx % 2 == 0)

            if self.assign_biweekly_shift(emp_id, start_date, rotation_weeks, start_with_day):
                success_count += 1
            else:
                error_count += 1

        return success_count, error_count

    def get_shift_statistics(self, year: int, month: int) -> Dict:
        """
        월별 교대 근무 통계

        Args:
            year: 년도
            month: 월

        Returns:
            통계 정보
        """
        employees = self.db.get_all_employees(include_resigned=False)

        stats = {
            'total_employees': len(employees),
            'day_shift_count': 0,
            'night_shift_count': 0,
            'fixed_schedule_count': 0,
            'shift_distribution': {}
        }

        # 해당 월 1일 기준으로 통계
        first_day = f"{year:04d}-{month:02d}-01"

        for emp in employees:
            shift_id = self.get_shift_for_date(emp['emp_id'], first_day)

            if shift_id:
                if shift_id not in stats['shift_distribution']:
                    stats['shift_distribution'][shift_id] = 0
                stats['shift_distribution'][shift_id] += 1

                if shift_id == 'SHIFT_2W_DAY':
                    stats['day_shift_count'] += 1
                elif shift_id == 'SHIFT_2W_NIGHT':
                    stats['night_shift_count'] += 1
                else:
                    stats['fixed_schedule_count'] += 1

        return stats

    def export_schedule_to_dict(self, year: int, month: int) -> Dict:
        """
        월간 전체 직원 스케줄 딕셔너리로 내보내기

        Args:
            year: 년도
            month: 월

        Returns:
            직원별 스케줄 딕셔너리
        """
        employees = self.db.get_all_employees(include_resigned=False)

        schedule_data = {
            'year': year,
            'month': month,
            'employees': []
        }

        for emp in employees:
            emp_schedule = self.generate_monthly_schedule(emp['emp_id'], year, month)

            schedule_data['employees'].append({
                'emp_id': emp['emp_id'],
                'emp_code': emp['emp_code'],
                'name': emp['name'],
                'department': emp.get('department', ''),
                'schedule': emp_schedule
            })

        return schedule_data


# 테스트 코드
if __name__ == "__main__":
    print("=" * 60)
    print("교대 근무 스케줄러 테스트")
    print("=" * 60)

    scheduler = ShiftScheduler()

    # 예시: 직원 1번에게 2교대 스케줄 할당
    print("\n📋 2교대 스케줄 할당 테스트:")
    start_date = datetime.now().strftime('%Y-%m-01')
    result = scheduler.assign_biweekly_shift(
        emp_id=1,
        start_date=start_date,
        rotation_weeks=2,
        start_with_day=True
    )

    if result:
        print(f"   ✅ 직원 1번에게 2교대 스케줄 할당 완료")

        # 이번 달 스케줄 조회
        now = datetime.now()
        monthly_schedule = scheduler.generate_monthly_schedule(1, now.year, now.month)

        print(f"\n📅 {now.year}년 {now.month}월 스케줄:")
        for day_info in monthly_schedule[:7]:  # 첫 주만 출력
            print(f"   {day_info['date']}: {day_info['shift_name']}")

    print("\n✅ 교대 근무 스케줄러 준비 완료!")
