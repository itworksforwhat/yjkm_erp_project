# 🔄 세콤(SECOM) 시스템 연동 가이드

## 📋 개요

세콤 근태 시스템의 데이터를 급여관리 ERP로 자동으로 가져오는 기능입니다.

---

## 🎯 지원하는 데이터베이스

### 1. MS-SQL (가장 일반적)
- Windows 환경에서 가장 많이 사용
- ODBC Driver 17 for SQL Server 필요

### 2. MySQL
- 오픈소스 데이터베이스
- 별도 드라이버 설치 불필요

### 3. Oracle
- 대기업 환경에서 사용
- cx_Oracle 패키지 필요

### 4. ODBC
- 범용 데이터베이스 연결
- DSN 설정 필요

---

## 📦 설치 방법

### 기본 패키지 설치
```bash
pip install customtkinter pillow pandas openpyxl reportlab pyodbc pymysql
```

### Oracle 사용 시 (선택사항)
```bash
pip install cx-Oracle
```

### MS-SQL 사용 시 추가 설정 (Windows)

**ODBC Driver 설치:**
1. https://aka.ms/downloadmsodbcsql 방문
2. "ODBC Driver 17 for SQL Server" 다운로드
3. 설치 실행

---

## 🚀 세콤 연동 사용법

### 1단계: 세콤 서버 접속

**메뉴 경로:**
```
프로그램 실행 → 🔄 세콤 연동 → ERP 서버설정 탭
```

**입력 정보:**
```
Provider:   MS-SQL (드롭다운 선택)
SERVER IP:  세콤 서버 IP (예: 192.168.1.100)
PORT:       1433 (MS-SQL 기본 포트)
DB명.dbo:   SECOM.dbo (세콤 데이터베이스명)
USER:       세콤 DB 사용자명
PASSWORD:   세콤 DB 비밀번호
```

**접속 확인:**
- "접속확인" 버튼 클릭
- "✅ 연결 정상" 메시지 확인

---

### 2단계: 전송 설정

**메뉴 경로:**
```
🔄 세콤 연동 → 사용 전송설정 탭
```

**기간 설정:**
```
시작일자: 2026-01-01
종료일자: 2026-01-31
```

**사용자 쿼리 (고급):**
- 기본 쿼리 자동 사용
- 필요 시 커스텀 쿼리 작성 가능

---

### 3단계: 동기화 실행

**메뉴 경로:**
```
🔄 세콤 연동 → 동기화 탭
```

**실행:**
1. "🔄 근태 데이터 동기화" 버튼 클릭
2. 진행 상황 확인
3. 완료 메시지 확인

**결과 확인:**
```
동기화 완료!
성공: 150건
실패: 0건
```

---

## 🔧 세콤 데이터 구조

### 기본 근태 테이블 (예시)

```sql
-- 세콤 시스템의 일반적인 근태 테이블
CREATE TABLE attendance_log (
    emp_code VARCHAR(20),      -- 직원코드
    work_date DATE,            -- 근무일
    clock_in TIME,             -- 출근시간
    clock_out TIME,            -- 퇴근시간
    work_type VARCHAR(10)      -- 근무유형
)
```

### 필수 필드
```
✅ emp_code   : 직원 코드 (ERP 직원과 매칭)
✅ work_date  : 근무 날짜
✅ clock_in   : 출근 시간
✅ clock_out  : 퇴근 시간
```

---

## 📊 데이터 매핑

### ERP 직원과 세콤 직원 매칭

**방법 1: 직원코드로 매칭**
```
세콤: emp_code = "EMP001"
ERP:  emp_code = "EMP001"
→ 자동 매칭
```

**방법 2: 세콤 ID로 매칭**
```
세콤: emp_code = "SEC001"
ERP:  secom_employee_id = "SEC001"
→ 자동 매칭
```

**매칭 실패 시:**
- 로그에 "❌ 직원 없음: EMP001" 표시
- ERP에 해당 직원 먼저 등록 필요

---

## 🎯 실무 시나리오

### 시나리오 1: 월말 근태 동기화

**상황:**
- 매월 말일
- 세콤에서 한 달치 근태 가져오기

**단계:**
```
1. 세콤 연동 메뉴
2. 사용 전송설정
   - 시작일: 2026-01-01
   - 종료일: 2026-01-31
3. 동기화 탭
4. "근태 데이터 동기화" 클릭
5. 로그 확인
6. 근태 관리에서 데이터 확인
```

### 시나리오 2: 일일 자동 동기화

**상황:**
- 매일 아침 전날 근태 자동 가져오기

**설정:**
```
시작일자: 전날 (예: 2026-01-06)
종료일자: 전날 (예: 2026-01-06)
```

### 시나리오 3: 특정 직원만 동기화

**커스텀 쿼리 사용:**
```sql
SELECT emp_code, work_date, clock_in, clock_out
FROM attendance_log
WHERE work_date BETWEEN '2026-01-01' AND '2026-01-31'
  AND emp_code IN ('EMP001', 'EMP002', 'EMP003')
```

---

## 🔍 문제 해결

### 1. 접속 실패

**증상:**
```
❌ MS-SQL 연결 실패: [ODBC Driver Manager] 데이터 원본 이름을 찾을 수 없습니다
```

**해결:**
```
1. ODBC Driver 17 설치 확인
2. SERVER IP 확인 (Ping 테스트)
3. PORT 확인 (1433)
4. 방화벽 확인
```

### 2. 인증 실패

**증상:**
```
❌ MS-SQL 연결 실패: Login failed for user 'username'
```

**해결:**
```
1. USER/PASSWORD 확인
2. SQL Server 인증 모드 확인
3. 사용자 권한 확인
```

### 3. 데이터베이스 없음

**증상:**
```
❌ MS-SQL 연결 실패: Cannot open database "SECOM"
```

**해결:**
```
1. DB명 확인 (대소문자 구분)
2. 데이터베이스 존재 확인
3. 접근 권한 확인
```

### 4. 직원 매칭 실패

**증상:**
```
동기화 완료!
성공: 0건
실패: 150건

로그:
❌ 직원 없음: EMP001
❌ 직원 없음: EMP002
```

**해결:**
```
1. ERP에 직원 먼저 등록
2. 직원코드 일치 확인
3. 세콤 ID 설정 확인
```

---

## 💡 Pro Tips

### 1. 초기 설정
```
✅ 테스트 환경에서 먼저 테스트
✅ 1~2일치 데이터로 시작
✅ 로그 확인 후 전체 동기화
```

### 2. 정기 동기화
```
✅ 매일 아침 전날 데이터 동기화
✅ 월말에 전체 재확인
✅ 로그 정기적으로 확인
```

### 3. 데이터 검증
```
✅ 동기화 후 근태 관리에서 확인
✅ 이상한 데이터 수정
✅ 급여 계산 전 최종 확인
```

---

## 🔐 보안 주의사항

### 데이터베이스 접속 정보
```
⚠️ PASSWORD는 안전하게 관리
⚠️ 읽기 전용 계정 사용 권장
⚠️ VPN 환경에서 접속 권장
```

### 데이터 백업
```
✅ 동기화 전 ERP 데이터 백업
✅ 세콤 원본 데이터는 수정 안 함
✅ 정기적인 백업 수행
```

---

## 📞 세콤 시스템 정보

### 일반적인 세콤 설정

**MS-SQL 기본 포트:**
```
1433 (기본)
```

**데이터베이스 이름:**
```
SECOM
SECOM.dbo
SecomDB
```

**테이블 이름 (예시):**
```
attendance_log
employee_master
time_clock_data
```

---

## 🎓 추가 학습

### 커스텀 쿼리 예시

**1. 특정 부서만:**
```sql
SELECT a.emp_code, a.work_date, a.clock_in, a.clock_out
FROM attendance_log a
JOIN employee_master e ON a.emp_code = e.emp_code
WHERE a.work_date BETWEEN '2026-01-01' AND '2026-01-31'
  AND e.department = '생산팀'
```

**2. 야간 근무만:**
```sql
SELECT emp_code, work_date, clock_in, clock_out
FROM attendance_log
WHERE work_date BETWEEN '2026-01-01' AND '2026-01-31'
  AND work_type = 'NIGHT'
```

**3. 잔업 있는 데이터만:**
```sql
SELECT emp_code, work_date, clock_in, clock_out
FROM attendance_log
WHERE work_date BETWEEN '2026-01-01' AND '2026-01-31'
  AND DATEDIFF(HOUR, clock_in, clock_out) > 9
```

---

## ✅ 체크리스트

### 초기 설정
- [ ] 세콤 서버 정보 확인
- [ ] ODBC Driver 설치 (MS-SQL)
- [ ] 접속 테스트 성공
- [ ] 테스트 데이터 동기화

### 정기 운영
- [ ] 일일 동기화 실행
- [ ] 로그 확인
- [ ] 데이터 검증
- [ ] 월말 전체 확인

---

**세콤 연동으로 근태 입력을 자동화하세요!** ⚡
