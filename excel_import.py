"""
Excel 파일을 이용한 직원 데이터 일괄 Import
엑셀 템플릿 생성 및 대량 직원 추가 기능
"""

import pandas as pd
from datetime import datetime
from typing import Tuple, List, Dict
from pathlib import Path

from database_v2 import Database
from config_manager import ConfigManager
from leave_manager import LeaveManager


class ExcelEmployeeImporter:
    """
    Excel 파일로부터 직원 데이터를 가져와 시스템에 등록
    """

    def __init__(self, db_path: str = "payroll.db"):
        """
        Excel Importer 초기화

        Args:
            db_path: 데이터베이스 경로
        """
        self.db = Database(db_path)
        self.config = ConfigManager(db_path)
        self.leave_mgr = LeaveManager(db_path)

    def create_template(self, output_path: str = "직원_가져오기_템플릿.xlsx"):
        """
        직원 등록용 Excel 템플릿 생성

        Args:
            output_path: 출력 파일 경로
        """
        # 근무 형태 목록 조회
        schedules = self.config.get_all_schedules()
        schedule_options = ", ".join([s['schedule_name'] for s in schedules])

        # 템플릿 데이터
        template_data = {
            '직원코드*': ['EMP001', 'EMP002', 'EMP003'],
            '이름*': ['홍길동', '김철수', '이영희'],
            '부서': ['생산팀', '관리팀', '생산팀'],
            '직급': ['대리', '과장', '사원'],
            '입사일*': ['2024-01-15', '2023-05-20', '2024-03-10'],
            '시급*': [20000, 25000, 18000],
            '근무형태*': ['주간근무 (09:00~18:00)', '주간근무 (09:00~18:00)', '2교대(주간) (06:00~18:00)'],
            '전화번호': ['010-1234-5678', '010-2345-6789', '010-3456-7890'],
            '이메일': ['hong@company.com', 'kim@company.com', 'lee@company.com'],
            '은행명': ['KB국민은행', '신한은행', '우리은행'],
            '계좌번호': ['123-456-789', '234-567-890', '345-678-901'],
            '세콤직원ID': ['SECOM001', 'SECOM002', 'SECOM003'],
            '세콤카드번호': ['CARD001', 'CARD002', 'CARD003'],
            '비고': ['', '', '']
        }

        df = pd.DataFrame(template_data)

        # Excel 저장
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='직원목록', index=False)

            # 가이드 시트 추가
            guide_data = {
                '항목': [
                    '직원코드*',
                    '이름*',
                    '부서',
                    '직급',
                    '입사일*',
                    '시급*',
                    '근무형태*',
                    '전화번호',
                    '이메일',
                    '은행명',
                    '계좌번호',
                    '세콤직원ID',
                    '세콤카드번호',
                    '비고'
                ],
                '필수여부': [
                    '필수',
                    '필수',
                    '선택',
                    '선택',
                    '필수',
                    '필수',
                    '필수',
                    '선택',
                    '선택',
                    '선택',
                    '선택',
                    '선택 (세콤 연동시)',
                    '선택 (세콤 연동시)',
                    '선택'
                ],
                '설명': [
                    '중복되지 않는 고유한 직원 코드 (예: EMP001)',
                    '직원 이름',
                    '소속 부서명',
                    '직급 (사원, 대리, 과장, 부장 등)',
                    '입사일자 (YYYY-MM-DD 형식)',
                    '시급 (숫자만 입력, 원 단위)',
                    f'근무 형태 선택 ({schedule_options})',
                    '전화번호 (예: 010-1234-5678)',
                    '이메일 주소',
                    '급여 수령 은행명',
                    '급여 계좌번호',
                    '세콤 시스템에서 사용하는 직원 ID',
                    '세콤 출퇴근 카드 번호',
                    '기타 메모사항'
                ]
            }

            guide_df = pd.DataFrame(guide_data)
            guide_df.to_excel(writer, sheet_name='작성가이드', index=False)

        print(f"✅ Excel 템플릿 생성 완료: {output_path}")
        print(f"   - 직원목록 시트: 직원 정보 입력")
        print(f"   - 작성가이드 시트: 항목별 설명")

        return output_path

    def import_from_excel(self, excel_path: str, skip_duplicates: bool = True) -> Tuple[int, int, List[str]]:
        """
        Excel 파일에서 직원 데이터 가져오기

        Args:
            excel_path: Excel 파일 경로
            skip_duplicates: 중복 직원코드 건너뛰기 여부

        Returns:
            (성공 건수, 실패 건수, 오류 메시지 리스트)
        """
        success_count = 0
        error_count = 0
        errors = []

        try:
            # Excel 파일 읽기
            df = pd.read_excel(excel_path, sheet_name='직원목록')

            # 근무 형태 맵핑
            schedules = self.config.get_all_schedules()
            schedule_map = {s['schedule_name']: s['schedule_id'] for s in schedules}

            # 기존 직원 코드 조회 (중복 체크용)
            existing_employees = self.db.get_all_employees(include_resigned=True)
            existing_codes = {emp['emp_code'] for emp in existing_employees}

            # 각 행 처리
            for idx, row in df.iterrows():
                try:
                    # 필수 항목 검증
                    emp_code = str(row.get('직원코드*', '')).strip()
                    name = str(row.get('이름*', '')).strip()
                    hire_date = row.get('입사일*', '')
                    hourly_wage = row.get('시급*', 0)
                    work_schedule_name = str(row.get('근무형태*', '')).strip()

                    # 필수 항목 체크
                    if not all([emp_code, name, hire_date, hourly_wage, work_schedule_name]):
                        errors.append(f"행 {idx + 2}: 필수 항목 누락 (직원코드: {emp_code})")
                        error_count += 1
                        continue

                    # 중복 체크
                    if emp_code in existing_codes:
                        if skip_duplicates:
                            errors.append(f"행 {idx + 2}: 중복된 직원코드 건너뜀 ({emp_code})")
                            error_count += 1
                            continue
                        else:
                            errors.append(f"행 {idx + 2}: 중복된 직원코드 ({emp_code})")
                            error_count += 1
                            continue

                    # 근무 형태 ID 찾기
                    schedule_id = schedule_map.get(work_schedule_name, 'DAY_SHIFT')
                    if work_schedule_name not in schedule_map:
                        errors.append(f"행 {idx + 2}: 알 수 없는 근무형태 ({work_schedule_name}), 주간근무로 설정됨")

                    # 입사일 포맷 변환
                    if isinstance(hire_date, pd.Timestamp):
                        hire_date = hire_date.strftime('%Y-%m-%d')
                    else:
                        hire_date = str(hire_date)

                    # 직원 데이터 구성
                    emp_data = {
                        'emp_code': emp_code,
                        'name': name,
                        'department': str(row.get('부서', '')).strip(),
                        'position': str(row.get('직급', '')).strip(),
                        'hire_date': hire_date,
                        'hourly_wage': float(hourly_wage),
                        'work_schedule_id': schedule_id,
                        'phone': str(row.get('전화번호', '')).strip(),
                        'email': str(row.get('이메일', '')).strip(),
                        'bank_name': str(row.get('은행명', '')).strip(),
                        'account_number': str(row.get('계좌번호', '')).strip(),
                        'secom_employee_id': str(row.get('세콤직원ID', '')).strip(),
                        'secom_card_number': str(row.get('세콤카드번호', '')).strip(),
                        'notes': str(row.get('비고', '')).strip()
                    }

                    # 데이터베이스에 저장
                    success, emp_id = self.db.add_employee(emp_data)

                    if success:
                        # 연차 초기화
                        current_year = datetime.now().year
                        self.leave_mgr.initialize_employee_leave_balance(
                            emp_id,
                            hire_date,
                            current_year
                        )

                        success_count += 1
                        existing_codes.add(emp_code)  # 중복 체크용 업데이트
                    else:
                        errors.append(f"행 {idx + 2}: 저장 실패 ({emp_code} - {name})")
                        error_count += 1

                except Exception as e:
                    errors.append(f"행 {idx + 2}: 처리 오류 - {str(e)}")
                    error_count += 1

            print(f"✅ Excel 가져오기 완료")
            print(f"   성공: {success_count}건")
            print(f"   실패: {error_count}건")

            if errors:
                print(f"\n오류 상세:")
                for err in errors[:10]:  # 최대 10개만 출력
                    print(f"   - {err}")
                if len(errors) > 10:
                    print(f"   ... 외 {len(errors) - 10}건")

        except FileNotFoundError:
            errors.append(f"파일을 찾을 수 없습니다: {excel_path}")
            error_count += 1

        except Exception as e:
            errors.append(f"Excel 파일 읽기 오류: {str(e)}")
            error_count += 1

        return success_count, error_count, errors

    def export_to_excel(self, output_path: str = "직원목록_내보내기.xlsx",
                       include_resigned: bool = False):
        """
        현재 직원 목록을 Excel로 내보내기

        Args:
            output_path: 출력 파일 경로
            include_resigned: 퇴사자 포함 여부
        """
        try:
            # 직원 목록 조회
            employees = self.db.get_all_employees(include_resigned=include_resigned)

            # 근무 형태 맵핑
            schedules = self.config.get_all_schedules()
            schedule_map = {s['schedule_id']: s['schedule_name'] for s in schedules}

            # DataFrame 구성
            export_data = []
            for emp in employees:
                export_data.append({
                    '직원코드': emp['emp_code'],
                    '이름': emp['name'],
                    '부서': emp.get('department', ''),
                    '직급': emp.get('position', ''),
                    '입사일': emp['hire_date'],
                    '퇴사일': emp.get('resignation_date', ''),
                    '시급': emp['hourly_wage'],
                    '근무형태': schedule_map.get(emp.get('work_schedule_id', ''), ''),
                    '전화번호': emp.get('phone', ''),
                    '이메일': emp.get('email', ''),
                    '은행명': emp.get('bank_name', ''),
                    '계좌번호': emp.get('account_number', ''),
                    '세콤직원ID': emp.get('secom_employee_id', ''),
                    '세콤카드번호': emp.get('secom_card_number', ''),
                    '비고': emp.get('notes', '')
                })

            df = pd.DataFrame(export_data)

            # Excel 저장
            df.to_excel(output_path, sheet_name='직원목록', index=False, engine='openpyxl')

            print(f"✅ Excel 내보내기 완료: {output_path}")
            print(f"   총 {len(employees)}명의 직원 정보 저장")

            return output_path

        except Exception as e:
            print(f"❌ Excel 내보내기 오류: {e}")
            return None


# 테스트 코드
if __name__ == "__main__":
    print("=" * 60)
    print("Excel 직원 Import/Export 모듈 테스트")
    print("=" * 60)

    importer = ExcelEmployeeImporter()

    # 템플릿 생성
    print("\n📝 Excel 템플릿 생성:")
    template_path = importer.create_template()

    print("\n✅ Excel Import/Export 모듈 준비 완료!")
    print(f"\n사용 방법:")
    print(f"1. '{template_path}' 파일을 열어서 직원 정보 입력")
    print(f"2. importer.import_from_excel('{template_path}')로 가져오기")
    print(f"3. importer.export_to_excel()로 현재 직원 목록 내보내기")
