# 🚀 YJKM ERP System v2.0.0 - 빌드 및 실행 가이드

## ⚡ 빠른 시작 (3단계)

```cmd
cd C:\Users\user\IdeaProjects\yjkm_erp_project\yjkm-erp-java

git pull origin main

mvn clean compile && mvn exec:java "-Dexec.mainClass=com.yjkm.erp.Main"
```

---

## 📋 사전 요구사항

✅ **Java 17 이상**
```cmd
java -version
```
→ `openjdk version "17"` 이상 확인

✅ **Maven 3.6 이상**
```cmd
mvn -version
```
→ `Apache Maven 3.6` 이상 확인

---

## 🛠️ 단계별 설치

### 1단계: 올바른 디렉토리 이동

```cmd
cd C:\Users\user\IdeaProjects\yjkm_erp_project\yjkm-erp-java
```

✅ **확인:**
```cmd
dir pom.xml
```
→ `pom.xml` 파일이 현재 디렉토리에 있는지 확인

### 2단계: 최신 코드 가져오기

```cmd
git pull origin main
```

### 3단계: 빌드

```cmd
mvn clean compile
```

✅ **결과:** `[INFO] BUILD SUCCESS`

### 4단계: 실행

```cmd
mvn exec:java "-Dexec.mainClass=com.yjkm.erp.Main"
```

✅ **예상 출력:**
```
╔════════════════════════════════════════════════════════════════════════════════╗
║       💼 YJKM ERP System v2.0.0                                               ║
║            급여 관리 시스템                                                   ║
╚════════════════════════════════════════════════════════════════════════════════╝

시스템 정보
  - Java 버전: 24.0.2
  - 운영체제: Windows 11 23H2
  - 파일 인코딩: UTF-8

데이터베이스 초기화 중...
  - SQLite 데이터베이스 연결 중...
  - 스키마 확인 중...
  - 기본 데이터 생성 중...
✅ 데이터베이스 초기화 완료

UI 준비 중...
  - JavaFX 초기화 중...
  - 메인 윈도우 생성 중...
  - 카트롤 엘리먼트 추가 중...
✅ UI 준비 완료

==================================================
시스템이 준비되었습니다!
==================================================

주요 기능:
  🔘 SECOM 데이터 가져오기 - S1/ERPExport.txt에서 직원 및 출퇴근 기록 import
  🔘 급여 계산 (이번 달) - 모든 직원의 급여를 자동으로 계산
  🔘 직원 통계 - 재직 직원, 출퇴근 기록, 급여 현황 조회
  🔘 데이터베이스 초기화 - 기본 근무형태 및 잔업 계수 생성
```

---

## 🎯 핵심 기능

### 1. 📥 SECOM 데이터 가져오기
- **파일:** `S1/ERPExport.txt`
- **기능:** 직원 정보 및 출퇴근 기록 자동 import
- **결과:** 직원 테이블에 자동 등록

### 2. 💰 급여 계산 (이번 달)
- **대상:** 모든 활성 직원
- **계산:**
  - ✅ 기본급 (시급 × 근무시간)
  - ✅ 차등 잔업 수당 (0.5배~2.0배)
  - ✅ 야간 수당 (1.5배)
  - ✅ 휴일 수당 (1.5배)
  - ✅ 4대보험 자동 계산
  - ✅ 소득세 자동 계산
- **결과:** 급여 기록 생성, 실수령액 표시

### 3. 👥 직원 통계
- 재직 중인 직원 수
- 출퇴근 기록 수
- 급여 기록 수

### 4. 🔄 데이터베이스 초기화
- 근무형태 생성 (주간/야간/2교대)
- 잔업 계수 생성 (0.5배, 1.0배, 1.5배, 2.0배)
- 기본 직원 데이터 생성

---

## 📦 프로젝트 구조

```
yjkm-erp-java/
├── pom.xml                                    # Maven 설정
├── BUILD_GUIDE.md                            # 이 파일
├── src/
│   ├── main/
│   │   ├── java/com/yjkm/erp/
│   │   │   ├── Main.java                    # ⭐ 시작점
│   │   │   ├── model/                       # 데이터 모델 (Entity)
│   │   │   │   ├── Employee.java            # 직원
│   │   │   │   ├── Attendance.java          # 출퇴근
│   │   │   │   ├── Payroll.java             # 급여
│   │   │   │   ├── Leave.java               # 휴가
│   │   │   │   └── ...
│   │   │   ├── service/                     # 비즈니스 로직
│   │   │   │   ├── PayrollCalculator.java   # 급여 계산
│   │   │   │   └── SecomImportService.java  # SECOM import
│   │   │   ├── importer/                    # 파일 import
│   │   │   │   └── SecomFileParser.java     # SECOM 파서
│   │   │   └── util/                        # 유틸리티
│   │   │       └── DatabaseUtil.java        # DB 유틸
│   │   └── resources/
│   │       ├── logback.xml                  # 로깅 설정 (UTF-8)
│   │       └── persistence.xml              # Hibernate 설정
│   └── test/
│       └── java/                            # 단위 테스트
├── S1/
│   └── ERPExport.txt                        # SECOM 출퇴근 데이터
└── payroll.db                                # SQLite 데이터베이스
```

---

## 🔧 트러블슈팅

### ❌ 문제: "[INFO] BUILD FAILURE"

**해결:**
1. 올바른 디렉토리 확인
   ```cmd
   cd C:\Users\user\IdeaProjects\yjkm_erp_project\yjkm-erp-java
   dir pom.xml
   ```

2. 최신 코드 가져오기
   ```cmd
   git pull origin main
   ```

3. 캐시 제거 후 재빌드
   ```cmd
   mvn clean
   mvn compile
   ```

### ❌ 문제: "캡스처 인코딩" (한글이 깨침)

**해결:** 이미 수정됨 ✅
- `logback.xml`에 UTF-8 인코딩 명시
- `Main.java`에 UTF-8 시스템 프로퍼티 설정
- Windows Console에서 UTF-8 출력 강제

### ❌ 문제: "port already in use"

**해결:**
```cmd
# 기존 프로세스 종료
taskkill /im java.exe /f

# 다시 실행
mvn exec:java "-Dexec.mainClass=com.yjkm.erp.Main"
```

### ❌ 문제: "Cannot find symbol"

**해결:**
```cmd
mvn clean install -DskipTests
```

---

## ✅ 최종 확인 체크리스트

- [ ] Java 17+ 설치 확인
- [ ] Maven 3.6+ 설치 확인
- [ ] 올바른 디렉토리 (`yjkm-erp-java`)
- [ ] `git pull origin main` 성공
- [ ] `mvn clean compile` 성공
- [ ] `mvn exec:java` 실행
- [ ] 한글 로그 정상 출력
- [ ] 시스템 준비 완료 메시지 확인

---

## 🚀 다음 단계

1. **SECOM 데이터 준비**
   - `S1/ERPExport.txt` 파일 준비
   - 프로그램 실행 시 자동 import

2. **직원 정보 등록**
   - SECOM 데이터 import
   - 추가 정보 입력 (시급, 부서 등)

3. **급여 계산**
   - "급여 계산" 버튼 클릭
   - 자동으로 모든 직원 급여 계산

4. **결과 확인**
   - 급여명세서 출력
   - Excel로 내보내기

---

## 📞 지원

문제가 발생하면:

1. GitHub Issues에 보고: [Issues](https://github.com/itworksforwhat/yjkm_erp_project/issues)
2. 로그 파일 확인: `logs/erp-system.log`
3. 디버그 로그 활성화:
   ```cmd
   mvn -X exec:java "-Dexec.mainClass=com.yjkm.erp.Main"
   ```

---

**업데이트:** 2026년 1월 11일 07:23 KST  
**상태:** ✅ 프로덕션 준비 완료  
**라이선스:** MIT
