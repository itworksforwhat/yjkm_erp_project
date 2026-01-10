# YJKM ERP System - 빌드 및 실행 가이드

## 🚀 빠른 시작

```cmd
cd C:\Users\user\IdeaProjects\yjkm_erp_project\yjkm-erp-java

mvn clean compile

mvn exec:java "-Dexec.mainClass=com.yjkm.erp.Main"
```

---

## 📋 단계별 가이드

### 1단계: 올바른 디렉토리 이동

```cmd
cd C:\Users\user\IdeaProjects\yjkm_erp_project\yjkm-erp-java
```

✅ **필수 확인 사항:**
- 현재 디렉토리: `yjkm-erp-java`
- `pom.xml` 파일이 현재 디렉토리에 있는지 확인

```cmd
dir pom.xml
```

### 2단계: Maven 설치 확인

```cmd
mvn --version
```

✅ Maven 3.6+, Java 17+ 필요

### 3단계: 빌드

```cmd
mvn clean compile
```

✅ **[INFO] BUILD SUCCESS** 메시지 확인

### 4단계: 실행

```cmd
mvn exec:java "-Dexec.mainClass=com.yjkm.erp.Main"
```

---

## ✅ 성공 시 콘솔 출력

```
[INFO] ====================================="
[INFO] YJKM ERP System v2.0.0
[INFO] Java: 17.0.x
[INFO] ====================================="
[INFO] ✅ 시스템이 정상적으로 시작되었습니다!
[INFO] ✅ 데이터베이스 연결 준비 완료
[INFO] ✅ UI 준비 완료
[INFO]
[INFO] ▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
[INFO] 시스템이 준비되었습니다!
[INFO] ▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
```

---

## 🔧 시스템 구조

```
src/main/java/com/yjkm/erp/
├── Main.java                  # 시작점
├── model/                      # 데이터 모델
│   ├── Employee.java
│   ├── Payroll.java
│   ├── Attendance.java
│   └── ...
├── service/                    # 비즈니스 로직
│   ├── PayrollService.java
│   ├── SecomImportService.java
│   └── ...
├── importer/                   # 파일 임포터
│   └── SecomFileParser.java
└── util/                       # 유틸리티
    └── DatabaseUtil.java
```

---

## ❓ 자주 나는 오류 및 해결

### 오류: "MissingProjectException"

**원인:** 잘못된 디렉토리에서 실행

**해결:**
```cmd
cd C:\Users\user\IdeaProjects\yjkm_erp_project\yjkm-erp-java
dir pom.xml  # pom.xml 파일 확인
```

### 오류: "cannot find symbol"

**원인:** 클래스 파일이 없거나 패키지 오류

**해결:**
```cmd
mvn clean
mvn compile
```

### 오류: "Compilation failure"

**원인:** 소스 코드에 오류가 있음

**해결:**
1. GitHub에서 최신 코드 가져오기
   ```cmd
   git pull origin main
   ```
2. 다시 컴파일
   ```cmd
   mvn clean compile
   ```

---

## 📦 최종 확인 체크리스트

- [ ] PowerShell에서 현재 디렉토리: `yjkm-erp-java`
- [ ] `pom.xml` 파일이 현재 디렉토리에 있는지 확인
- [ ] `mvn --version` 실행하여 Maven 설치 확인
- [ ] `mvn clean compile` 성공 여부 확인
- [ ] `mvn exec:java "-Dexec.mainClass=com.yjkm.erp.Main"` 성공

---

## 📝 GitHub 최신 변경사항

✅ **Main.java** - 단순화된 버전
✅ **PayrollService.java** - 급여 계산 로직
✅ **SecomImportService.java** - SECOM 임포트
✅ **DatabaseUtil.java** - 데이터베이스 유틸
✅ **모든 Model 클래스** - Lombok 완전 제거

모든 파일이 정상적으로 GitHub에 커밋되어 있습니다.

---

**준비 완료!** 🎉
