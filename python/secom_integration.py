"""
세콤 출퇴근 시스템 연동 모듈
세콤 데이터 가져오기, 파싱, 자동 근태 입력
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import csv
from pathlib import Path

from database_v2 import Database
from payroll_calculator_v2 import AdvancedPayrollCalculator
from config_manager import ConfigManager


class SecomIntegration:
    """
    세콤 출퇴근 시스템 연동
    
    지원 형식:
    1. CSV 파일 Import
    2. JSON 파일 Import
    3. API 연동 (추후 확장)
    """
    
    def __init__(self, db_path: str = "payroll.db"):
        """
        세콤 연동 초기화
        
        Args:
            db_path: 데이터베이스 경로
        """
        self.db = Database(db_path)
        self.calculator = AdvancedPayrollCalculator(db_path)
        self.config = ConfigManager(db_path)
        
    def import_from_csv(self, csv_file_path: str) -> Tuple[int, int, List[str]]:
        """
        세콤 CSV 파일에서 출퇴근 데이터 가져오기
        
        CSV 형식:
        - employee_id: 직원 ID (세콤)
        - card_number: 카드 번호
        - event_date: 날짜 (YYYY-MM-DD)
        - event_time: 시간 (HH:MM:SS 또는 HH:MM)
        - event_type: 이벤트 타입 (IN/OUT)
        
        Args:
            csv_file_path: CSV 파일 경로
            
        Returns:
            (성공 건수, 실패 건수, 오류 메시지 리스트)
        """
        success_count = 0
        error_count = 0
        errors = []
        
        try:
            with open(csv_file_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                
                # 데이터를 날짜-직원별로 그룹화
                grouped_data = {}
                
                for row in reader:
                    try:
                        emp_id = self._find_employee_by_secom_id(
                            row.get('employee_id', ''),
                            row.get('card_number', '')
                        )
                        
                        if not emp_id:
                            errors.append(f"직원을 찾을 수 없음: {row.get('employee_id', 'N/A')}")
                            error_count += 1
                            continue
                        
                        event_date = row.get('event_date', '')
                        event_time = row.get('event_time', '')[:5]  # HH:MM만 추출
                        event_type = row.get('event_type', '').upper()
                        
                        key = (emp_id, event_date)
                        
                        if key not in grouped_data:
                            grouped_data[key] = {
                                'emp_id': emp_id,
                                'date': event_date,
                                'clock_in': None,
                                'clock_out': None,
                                'raw_data': []
                            }
                        
                        grouped_data[key]['raw_data'].append(row)
                        
                        # IN/OUT 판단
                        if event_type == 'IN':
                            if not grouped_data[key]['clock_in']:
                                grouped_data[key]['clock_in'] = event_time
                        elif event_type == 'OUT':
                            grouped_data[key]['clock_out'] = event_time
                        
                    except Exception as e:
                        errors.append(f"데이터 파싱 오류: {str(e)}")
                        error_count += 1
                
                # 그룹화된 데이터를 근태로 저장
                for key, data in grouped_data.items():
                    try:
                        if data['clock_in'] and data['clock_out']:
                            result = self._save_attendance_from_secom(data)
                            if result:
                                success_count += 1
                            else:
                                error_count += 1
                                errors.append(f"저장 실패: {data['date']}, 직원 {data['emp_id']}")
                        else:
                            error_count += 1
                            errors.append(f"불완전한 데이터: {data['date']}, 직원 {data['emp_id']}")
                    
                    except Exception as e:
                        error_count += 1
                        errors.append(f"저장 오류: {str(e)}")
            
            # 동기화 로그 저장
            self.db.add_secom_sync_log({
                'sync_date': datetime.now().strftime('%Y-%m-%d'),
                'sync_time': datetime.now().strftime('%H:%M:%S'),
                'sync_type': 'csv_import',
                'total_records': success_count + error_count,
                'success_count': success_count,
                'error_count': error_count,
                'error_details': json.dumps(errors[:10], ensure_ascii=False)
            })
            
        except Exception as e:
            errors.append(f"파일 읽기 오류: {str(e)}")
            error_count += 1
        
        return success_count, error_count, errors
    
    def _find_employee_by_secom_id(self, secom_emp_id: str, card_number: str) -> Optional[int]:
        """
        세콤 직원 ID 또는 카드번호로 직원 찾기
        
        Args:
            secom_emp_id: 세콤 직원 ID
            card_number: 세콤 카드 번호
            
        Returns:
            직원 ID (없으면 None)
        """
        self.db.connect()
        
        # 세콤 직원 ID로 검색
        self.db.cursor.execute("""
            SELECT emp_id FROM employees
            WHERE secom_employee_id = ? OR secom_card_number = ?
            LIMIT 1
        """, (secom_emp_id, card_number))
        
        result = self.db.cursor.fetchone()
        self.db.close()
        
        if result:
            return result['emp_id']
        return None
    
    def _save_attendance_from_secom(self, secom_data: Dict) -> bool:
        """
        세콤 데이터를 근태로 변환하여 저장
        
        Args:
            secom_data: 세콤 데이터
            
        Returns:
            성공 여부
        """
        emp_id = secom_data['emp_id']
        work_date = secom_data['date']
        clock_in = secom_data['clock_in']
        clock_out = secom_data['clock_out']
        
        # 근무시간 계산
        work_hours_info = self.calculator.calculate_work_hours_by_schedule(
            emp_id, work_date, clock_in, clock_out
        )
        
        # 근태 데이터 구성
        attendance_data = {
            'emp_id': emp_id,
            'work_date': work_date,
            'clock_in': clock_in,
            'clock_out': clock_out,
            'actual_clock_in': clock_in,
            'actual_clock_out': clock_out,
            'work_hours': work_hours_info['work_hours'],
            'regular_hours': work_hours_info['regular_hours'],
            'break_hours': work_hours_info['break_hours'],
            'overtime_hours': work_hours_info['overtime_hours'],
            'night_hours': work_hours_info['night_hours'],
            'overtime_tier1_minutes': work_hours_info['overtime_tier1_minutes'],
            'overtime_tier2_minutes': work_hours_info['overtime_tier2_minutes'],
            'overtime_tier3_minutes': work_hours_info['overtime_tier3_minutes'],
            'work_schedule_id': work_hours_info['schedule_id'],
            'secom_sync': 1,
            'secom_sync_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'secom_raw_data': json.dumps(secom_data['raw_data'], ensure_ascii=False)
        }
        
        success, _ = self.db.add_attendance(attendance_data)
        return success
    
    def create_secom_csv_template(self, output_path: str = "secom_template.csv"):
        """
        세콤 CSV 템플릿 생성
        
        Args:
            output_path: 출력 파일 경로
        """
        headers = ['employee_id', 'card_number', 'event_date', 'event_time', 'event_type']
        
        sample_data = [
            ['EMP001', 'CARD001', '2024-12-01', '09:00', 'IN'],
            ['EMP001', 'CARD001', '2024-12-01', '18:00', 'OUT'],
            ['EMP002', 'CARD002', '2024-12-01', '09:05', 'IN'],
            ['EMP002', 'CARD002', '2024-12-01', '22:30', 'OUT'],
        ]
        
        with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(sample_data)
        
        print(f"✅ 세콤 CSV 템플릿 생성: {output_path}")
    
    def import_from_json(self, json_file_path: str) -> Tuple[int, int, List[str]]:
        """
        세콤 JSON 파일에서 데이터 가져오기
        
        JSON 형식:
        {
            "records": [
                {
                    "employee_id": "EMP001",
                    "date": "2024-12-01",
                    "clock_in": "09:00",
                    "clock_out": "18:00"
                }
            ]
        }
        
        Args:
            json_file_path: JSON 파일 경로
            
        Returns:
            (성공 건수, 실패 건수, 오류 메시지 리스트)
        """
        success_count = 0
        error_count = 0
        errors = []
        
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                records = data.get('records', [])
                
                for record in records:
                    try:
                        emp_id = self._find_employee_by_secom_id(
                            record.get('employee_id', ''),
                            record.get('card_number', '')
                        )
                        
                        if not emp_id:
                            errors.append(f"직원 없음: {record.get('employee_id', 'N/A')}")
                            error_count += 1
                            continue
                        
                        secom_data = {
                            'emp_id': emp_id,
                            'date': record.get('date'),
                            'clock_in': record.get('clock_in'),
                            'clock_out': record.get('clock_out'),
                            'raw_data': [record]
                        }
                        
                        if self._save_attendance_from_secom(secom_data):
                            success_count += 1
                        else:
                            error_count += 1
                            errors.append(f"저장 실패: {record}")
                    
                    except Exception as e:
                        error_count += 1
                        errors.append(f"처리 오류: {str(e)}")
            
            # 동기화 로그 저장
            self.db.add_secom_sync_log({
                'sync_date': datetime.now().strftime('%Y-%m-%d'),
                'sync_time': datetime.now().strftime('%H:%M:%S'),
                'sync_type': 'json_import',
                'total_records': success_count + error_count,
                'success_count': success_count,
                'error_count': error_count,
                'error_details': json.dumps(errors[:10], ensure_ascii=False)
            })
            
        except Exception as e:
            errors.append(f"파일 읽기 오류: {str(e)}")
            error_count += 1
        
        return success_count, error_count, errors
    
    def export_to_secom_format(self, start_date: str, end_date: str, 
                               output_path: str = "secom_export.csv"):
        """
        근태 데이터를 세콤 형식으로 내보내기
        
        Args:
            start_date: 시작일
            end_date: 종료일
            output_path: 출력 파일 경로
        """
        self.db.connect()
        
        self.db.cursor.execute("""
            SELECT 
                e.secom_employee_id,
                e.secom_card_number,
                a.work_date,
                a.clock_in,
                a.clock_out
            FROM attendance a
            JOIN employees e ON a.emp_id = e.emp_id
            WHERE a.work_date BETWEEN ? AND ?
            AND a.secom_sync = 1
            ORDER BY a.work_date, e.emp_code
        """, (start_date, end_date))
        
        records = self.db.cursor.fetchall()
        self.db.close()
        
        with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(['employee_id', 'card_number', 'event_date', 'event_time', 'event_type'])
            
            for record in records:
                emp_id = record['secom_employee_id']
                card = record['secom_card_number']
                date = record['work_date']
                
                # IN 이벤트
                writer.writerow([emp_id, card, date, record['clock_in'], 'IN'])
                
                # OUT 이벤트
                writer.writerow([emp_id, card, date, record['clock_out'], 'OUT'])
        
        print(f"✅ 세콤 형식 내보내기 완료: {output_path}")
    
    def get_sync_statistics(self, days: int = 30) -> Dict:
        """
        세콤 동기화 통계
        
        Args:
            days: 조회 기간 (일)
            
        Returns:
            동기화 통계
        """
        self.db.connect()
        
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        self.db.cursor.execute("""
            SELECT 
                COUNT(*) as total_syncs,
                SUM(total_records) as total_records,
                SUM(success_count) as total_success,
                SUM(error_count) as total_errors
            FROM secom_sync_log
            WHERE sync_date >= ?
        """, (cutoff_date,))
        
        stats = dict(self.db.cursor.fetchone())
        self.db.close()
        
        return stats


# 테스트 코드
if __name__ == "__main__":
    print("=" * 60)
    print("세콤 연동 모듈 테스트")
    print("=" * 60)
    
    secom = SecomIntegration()
    
    # CSV 템플릿 생성
    print("\n📝 세콤 CSV 템플릿 생성:")
    secom.create_secom_csv_template()
    
    print("\n✅ 세콤 연동 모듈 준비 완료!")
