# 세콤(SECOM) 연동 오류 해결 가이드

## 🔴 발생한 오류

### 오류 1: ODBC 드라이버 관리자 오류
```
[IM002] [Microsoft][ODBC 드라이버 관리자]
데이터 원본 이름을 찾고 기본 드라이버를 지정하지 않았습니다.
```

### 오류 2: SQL Server 연결 실패
```
[DBNETLIB][ConnectionOpen (Connect()).]
SQL Server가 없거나 액세스가 거부되었습니다.
```

---

## ✅ 해결 방법 (순서대로 진행)

### 1단계: ODBC 드라이버 설치 (필수!)

#### Windows 사용자

**다운로드 및 설치:**
1. Microsoft 공식 사이트에서 다운로드:
   - [ODBC Driver 17 for SQL Server](https://docs.microsoft.com/ko-kr/sql/connect/odbc/download-odbc-driver-for-sql-server)
   - 또는 [ODBC Driver 18 for SQL Server](https://go.microsoft.com/fwlink/?linkid=2223300) (최신 버전)

2. 다운로드한 파일 실행:
   - `msodbcsql.msi` 파일 실행
   - "동의" 클릭하여 설치 진행
   - 설치 완료 후 재부팅 (권장)

**설치 확인 방법:**
1. `제어판` → `관리 도구` → `ODBC 데이터 원본 (64비트)` 실행
2. `드라이버` 탭 클릭
3. 다음 중 하나가 있는지 확인:
   - ODBC Driver 18 for SQL Server
   - ODBC Driver 17 for SQL Server
   - ODBC Driver 13 for SQL Server

없으면 위 설치 과정을 다시 진행하세요.

---

### 2단계: SQL Server 연결 정보 확인

#### 세콤 시스템 담당자에게 확인해야 할 정보:

1. **SERVER IP (서버 주소)**
   - 예: `192.168.1.100` 또는 `secom-server.company.com`
   - `127.0.0.1`은 로컬 테스트용이므로 실제 서버 IP를 입력하세요

2. **PORT (포트 번호)**
   - 기본값: `1433` (MS-SQL 기본 포트)
   - 세콤 시스템에서 다른 포트를 사용할 수 있음

3. **DATABASE (데이터베이스 이름)**
   - 예: `SECOM.dbo` 또는 `SecomDB`
   - 정확한 이름을 확인하세요

4. **USER (사용자 ID)**
   - 예: `sa`, `secomuser`, `admin`
   - SQL Server 인증 계정

5. **PASSWORD (비밀번호)**
   - 해당 계정의 비밀번호

---

### 3단계: 네트워크 및 방화벽 확인

#### 1. 서버 연결 테스트 (CMD에서 실행)

```cmd
ping 192.168.1.100
```
- 응답이 오면: 네트워크 연결 정상 ✅
- 응답 없으면: 네트워크 문제 또는 서버 꺼짐 ❌

#### 2. 포트 열림 확인 (CMD에서 실행)

```cmd
telnet 192.168.1.100 1433
```

**telnet이 없다는 오류가 나면:**
1. `제어판` → `프로그램` → `Windows 기능 켜기/끄기`
2. `Telnet 클라이언트` 체크
3. 확인 후 다시 시도

**결과:**
- 빈 화면이 나오면: 포트 열림 ✅
- 연결 실패 메시지: 방화벽 차단 또는 SQL Server 꺼짐 ❌

#### 3. 방화벽 설정 확인

**Windows 방화벽:**
1. `제어판` → `Windows Defender 방화벽`
2. `고급 설정` 클릭
3. `아웃바운드 규칙` → `새 규칙`
4. 포트 1433 허용 규칙 추가

**회사 방화벽:**
- IT 담당자에게 세콤 서버 접근 권한 요청

---

### 4단계: SQL Server 서비스 확인 (서버 관리자용)

SQL Server가 설치된 서버에서:

1. `서비스` 앱 실행 (Win + R → `services.msc`)
2. 다음 서비스 확인:
   - **SQL Server (인스턴스명)** → 실행 중이어야 함
   - **SQL Server Browser** → 실행 중 권장

3. 중지되어 있으면 마우스 우클릭 → `시작`

---

### 5단계: 프로그램에서 다시 연결 시도

#### 올바른 입력 예시:

```
Provider: MS-SQL
SERVER IP: 192.168.1.100
PORT: 1433
DB명.dbo: SECOM
USER: secomuser
PASSWORD: ********
```

#### 주의사항:

1. **IP 주소는 정확히**
   - `127.0.0.1`은 테스트용 (실제 서버 IP 입력)
   - 공백이나 특수문자 없이 입력

2. **포트 번호 확인**
   - 비워두면 기본값 1433 사용
   - 다른 포트 사용 시 정확히 입력

3. **데이터베이스 이름**
   - `.dbo`는 제거하고 입력해도 됨
   - 예: `SECOM` 또는 `SECOM.dbo` 모두 가능

4. **인증 정보**
   - SQL Server 인증 모드 사용
   - Windows 인증은 현재 미지원

---

## 🔧 코드 수정 사항

**최신 코드 업데이트 완료!**

이제 프로그램이 다음과 같이 개선되었습니다:

1. ✅ **여러 ODBC 드라이버 자동 시도**
   - ODBC Driver 18, 17, 13, 11 순서대로 시도
   - SQL Server Native Client도 지원
   - 일반 SQL Server 드라이버도 시도

2. ✅ **SSL 인증서 문제 우회**
   - `TrustServerCertificate=yes` 추가
   - 자체 서명된 인증서도 허용

3. ✅ **명확한 오류 메시지**
   - 어떤 드라이버를 사용했는지 표시
   - 해결 방법 안내 포함

---

## 📋 체크리스트

연결 전에 다음을 확인하세요:

- [ ] ODBC Driver 17 이상 설치됨
- [ ] 세콤 서버 IP 주소 확인
- [ ] 포트 번호 확인 (기본: 1433)
- [ ] 데이터베이스 이름 확인
- [ ] 사용자 ID/비밀번호 확인
- [ ] 서버 ping 응답 확인
- [ ] 방화벽 포트 1433 개방
- [ ] SQL Server 서비스 실행 중

---

## 💡 자주 묻는 질문

### Q1: "드라이버를 찾을 수 없습니다" 오류

**A:** ODBC 드라이버가 설치되지 않았습니다.
```
해결: 1단계 ODBC 드라이버 설치 진행
```

### Q2: "SQL Server가 없거나 액세스가 거부되었습니다"

**A:** 서버에 연결할 수 없습니다.
```
원인 가능성:
1. 잘못된 IP 주소
2. SQL Server가 실행 중이 아님
3. 방화벽 차단
4. 네트워크 문제

해결: 3단계 네트워크 확인 진행
```

### Q3: "로그인 실패" 오류

**A:** 사용자 ID 또는 비밀번호가 틀렸습니다.
```
해결: 세콤 시스템 담당자에게 인증 정보 재확인
```

### Q4: ODBC 드라이버가 여러 개 설치되어 있으면?

**A:** 문제없습니다! 프로그램이 자동으로 최신 버전을 우선 사용합니다.
```
우선순위:
1. ODBC Driver 18 (최신)
2. ODBC Driver 17
3. ODBC Driver 13
...
```

### Q5: MySQL이나 Oracle을 사용하는 경우?

**A:** Provider를 변경하면 됩니다.
```
MySQL: pymysql 설치 필요
  pip install pymysql

Oracle: cx-Oracle 설치 필요
  pip install cx-Oracle
```

---

## 🎯 여전히 안 되는 경우

### 로그 수집 방법

오류 메시지를 정확히 기록하세요:

1. 프로그램 실행
2. 세콤 연동 → ERP 서버설정
3. 접속확인 버튼 클릭
4. 나타나는 오류 메시지 **전체**를 복사
5. 스크린샷 촬영

### IT 담당자에게 요청할 내용

```
1. 세콤 데이터베이스 서버 IP와 포트
2. 데이터베이스 이름
3. 접근 가능한 SQL Server 계정
4. 방화벽 예외 설정 (포트 1433)
5. SQL Server 버전 정보
```

---

## 📞 추가 지원

**관련 문서:**
- `SECOM_GUIDE.md` - 세콤 연동 전체 가이드
- `TROUBLESHOOTING.md` - 일반 오류 해결
- `NEW_FEATURES_GUIDE.md` - 신규 기능 사용법

**업데이트:** 2026-01-08
**버전:** v2.0.1
