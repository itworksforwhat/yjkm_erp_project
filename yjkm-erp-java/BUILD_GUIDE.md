# YJKM ERP System - 빌드 및 실행 가이드

## 🚀 빠른 시작

### 1단계: 올바른 디렉토리로 이동

```powershell
cd C:\Users\user\IdeaProjects\yjkm_erp_project\yjkm-erp-java
```

⚠️ **중요:** 반드시 `yjkm-erp-java` 디렉토리로 이동해야 합니다!
   - ❌ 잘못: `C:\Users\user\IdeaProjects\yjkm_erp_project`
   - ✅ 맞음: `C:\Users\user\IdeaProjects\yjkm_erp_project\yjkm-erp-java`

### 2단계: 빌드

```powershell
mvn clean verify
```

### 3단계: 실행

```powershell
mvn exec:java "-Dexec.mainClass=com.yjkm.erp.Main"
```

## 🎯 정상 실행 확인

컴파일 성공 후 JavaFX 창이 뜨면 성공입니다:
- 💼 "YJKM 급여관리 ERP v2.0" 윈도우 창이 표시
- 4개의 기능 버튼이 보임 (SECOM, 급여 계산, 통계, DB 초기화)
- 하단 TextArea에 로그가 출력됨

## 🔧 문제 해결

### 문제 1: "MissingProjectException - pom.xml을 찾을 수 없음"

**원인:** 부모 디렉토리에서 Maven을 실행함

**해결:**
```powershell
cd yjkm-erp-java
ls pom.xml  # pom.xml이 현재 디렉토리에 있는지 확인
mvn clean verify
```

### 문제 2: "cannot find symbol" - log 변수를 찾을 수 없음

**원인:** Lombok Annotation Processor가 활성화되지 않음

**해결:**
1. IntelliJ IDEA 열기
2. Settings → Build, Execution, Deployment → Annotation Processors
3. ✅ "Enable annotation processing" 체크
4. IDE 재시작 또는 `mvn clean compile` 재실행

### 문제 3: exec:java 명령어 인식 안 됨

**대안 실행 방법:**
```powershell
mvn clean package
java -cp target/erp-system-2.0.0.jar com.yjkm.erp.Main
```

### 문제 4: "JavaFX 라이브러리 로드 실패"

**해결:**
```powershell
# pom.xml 확인 - JavaFX 의존성이 있어야 함
mvn dependency:tree | grep javafx
```

## ✅ 체크리스트

- [ ] PowerShell 현재 디렉토리: `yjkm-erp-java` 확인
- [ ] `pom.xml` 파일이 현재 디렉토리에 있는지 확인
- [ ] `mvn --version` 실행하여 Maven 설치 확인
- [ ] `mvn clean compile` 컴파일 성공
- [ ] Lombok Annotation Processor 활성화 확인
- [ ] `mvn exec:java` 실행 후 JavaFX 창이 뜸

## 📋 프로젝트 구조

```
yjkm-erp-java/
├── pom.xml                           # Maven 설정
├── BUILD_GUIDE.md                    # 이 파일
└── src/main/java/com/yjkm/erp/
    ├── Main.java                     # JavaFX UI 메인 클래스
    ├── importer/
    │   └── SecomFileParser.java      # SECOM 파일 파서 (비활성화 중)
    ├── service/
    │   ├── PayrollCalculator.java    # 급여 계산 엔진
    │   └── SecomImportService.java   # SECOM 임포트 서비스 (비활성화 중)
    ├── model/                        # JPA 엔티티 모델
    ├── util/                         # 유틸리티
    └── resources/                    # 리소스 파일
```

## 🎨 주요 기능

### 1. 💰 급여 계산
- 월별 근무 시간 집계
- 차등 잔업 수당 계산
- 야간 수당, 휴일 수당 계산
- 4대보험 공제
- 실수령액 산출

### 2. 👥 직원 통계
- 재직 직원 수
- 출퇴근 기록 조회
- 급여 기록 조회

### 3. 🔄 데이터베이스 초기화
- 기본 근무형태 4개 생성
- 기본 잔업 계수 3개 생성
- 초기 데이터 세팅

### 4. 📥 SECOM 임포트 (향후 지원)
- 현재 비활성화 상태
- 다음 버전에서 활성화 예정

## 📚 추가 정보

- **Java 버전:** 17+
- **Maven:** 3.6+
- **데이터베이스:** H2 (내장)
- **ORM:** Hibernate + JPA
- **UI Framework:** JavaFX 21
- **로깅:** SLF4J + Logback
- **빌드 도구:** Maven

## 🤝 기여

코드 리뷰 및 개선 사항은 [CODE_REVIEW.md](./CODE_REVIEW.md) 참고

---

**작성일:** 2026-01-11
**버전:** 2.0.0 (Java Edition)