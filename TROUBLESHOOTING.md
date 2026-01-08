# 문제 해결 가이드 (Troubleshooting Guide)

## 🚀 설치 및 실행 순서

### 1단계: 의존성 패키지 설치

```bash
pip install customtkinter pillow pandas openpyxl reportlab pyodbc pymysql
```

**주의사항:**
- `cx-Oracle`는 Oracle 데이터베이스를 사용할 때만 필요합니다
- Windows에서 pyodbc 사용 시 "ODBC Driver 17 for SQL Server"가 필요합니다

### 2단계: 시스템 초기화 (처음 한 번만)

```bash
python init_system_v2.py
```

이 명령은:
- `payroll.db` 데이터베이스 파일 생성
- 필요한 테이블 생성
- 기본 근무 형태 설정 (주간, 야간, 2교대)
- 기본 잔업 수당 계수 설정

### 3단계: 프로그램 실행

```bash
python main.py
```

---

## ❌ 자주 발생하는 오류

### 오류 1: ModuleNotFoundError: No module named 'pandas'

**원인:** 필수 패키지가 설치되지 않음

**해결:**
```bash
pip install pandas openpyxl
```

### 오류 2: ModuleNotFoundError: No module named 'customtkinter'

**원인:** GUI 라이브러리가 설치되지 않음

**해결:**
```bash
pip install customtkinter pillow
```

### 오류 3: ImportError: cannot import name 'SecomIntegration'

**원인:** (이미 수정됨) gui_complete_part1.py의 불필요한 import

**해결:** 최신 코드를 사용하면 이미 수정되어 있습니다

### 오류 4: pyodbc.Error: 데이터베이스 연결 실패

**원인:** SECOM 데이터베이스 연결 정보가 잘못됨

**해결:**
1. SERVER IP, PORT 확인
2. 데이터베이스 이름 확인
3. 사용자 ID/비밀번호 확인
4. 방화벽 설정 확인
5. ODBC 드라이버 설치 확인 (Windows)

---

## 🔧 기능별 문제 해결

### Excel 가져오기가 안 되는 경우

**증상:** "Excel 파일 읽기 오류"

**확인 사항:**
1. Excel 파일이 `.xlsx` 형식인지 확인
2. 파일이 열려있지 않은지 확인
3. 시트 이름이 "직원목록"인지 확인
4. pandas, openpyxl 패키지가 설치되어 있는지 확인

**해결:**
```bash
pip install pandas openpyxl
```

### SECOM 연동이 안 되는 경우

**증상:** "연결 실패" 또는 "접속 오류"

**확인 사항:**
1. **네트워크 연결:**
   - SECOM 서버 IP에 ping이 되는지 확인
   - 방화벽에서 포트가 열려있는지 확인

2. **데이터베이스 드라이버:**
   ```bash
   # MS-SQL용
   pip install pyodbc

   # MySQL용
   pip install pymysql

   # Oracle용 (선택)
   pip install cx-Oracle
   ```

3. **Windows ODBC 설정:**
   - "ODBC Driver 17 for SQL Server" 설치 확인
   - ODBC 데이터 원본 관리자에서 연결 테스트

### 교대 스케줄이 제대로 적용되지 않는 경우

**증상:** 교대 스케줄 할당 후에도 근무 형태가 바뀌지 않음

**원인:** 교대 스케줄은 향후 근태 입력 시 자동으로 적용됩니다

**확인 방법:**
1. 교대 관리 메뉴에서 스케줄 할당 확인
2. 근태 입력 시 해당 날짜의 근무 형태가 자동 계산됨
3. 급여 계산 시 야간 수당이 자동 반영됨

### GUI가 실행되지 않는 경우

**증상:** 프로그램 실행 시 창이 나타나지 않음

**확인 사항:**
1. customtkinter 설치 확인:
   ```bash
   pip install customtkinter pillow
   ```

2. Python 버전 확인 (3.8 이상 필요):
   ```bash
   python --version
   ```

3. 오류 메시지 확인:
   ```bash
   python main.py
   ```
   터미널에 표시되는 오류 메시지 확인

---

## 🧪 테스트 방법

### 기본 기능 테스트

```bash
# 1. 데이터베이스 초기화 테스트
python init_system_v2.py

# 2. 모듈 import 테스트
python -c "from main import PayrollERP; print('✅ Import 성공')"

# 3. Excel 템플릿 생성 테스트
python -c "from excel_import import ExcelEmployeeImporter; e = ExcelEmployeeImporter(); e.create_template()"
```

### 개별 모듈 테스트

```bash
# 데이터베이스 모듈
python database_v2.py

# 설정 관리자
python config_manager.py

# 교대 스케줄러
python shift_scheduler.py

# Excel import
python excel_import.py
```

---

## 💡 성능 최적화 팁

### 대량 직원 등록 시

1. **Excel 사용 권장** (100명 이상)
   - 템플릿 생성 → 정보 입력 → 일괄 가져오기
   - 직원 추가 다이얼로그보다 빠름

2. **중복 체크 자동화**
   - Excel 가져오기는 자동으로 중복 건너뜀
   - 오류 로그 확인 필수

### SECOM 동기화 시

1. **날짜 범위 최소화**
   - 한 번에 1개월씩 동기화 권장
   - 너무 긴 기간은 시간이 오래 걸림

2. **사용자 쿼리 활용**
   - 기본 쿼리가 느리면 직접 SQL 작성
   - 필요한 컬럼만 SELECT

---

## 📞 추가 지원

### 로그 확인

프로그램 실행 시 터미널에 표시되는 로그를 확인하세요:
```
시스템 초기화 중...
✅ 데이터베이스 테이블 생성 완료
✅ 설정 테이블 초기화 완료
...
```

### 오류 메시지 해석

**"초기화 오류"** → `init_system_v2.py` 먼저 실행
**"데이터베이스 오류"** → payroll.db 파일 권한 확인
**"Import 오류"** → 패키지 설치 확인
**"GUI 오류"** → customtkinter 버전 확인 (5.2.0 이상)

---

## 🔍 디버깅 모드

더 자세한 오류 정보가 필요하면:

```python
# main.py 실행 전에 디버깅 모드 활성화
import logging
logging.basicConfig(level=logging.DEBUG)

# 그 후 main.py 실행
python main.py
```

---

**업데이트:** 2026-01-08
**버전:** v2.0.0
