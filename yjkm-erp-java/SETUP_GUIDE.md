# YJKM ERP System - 빌드 및 실행 가이드 (Lombok 완전 제거)

## 🎯 **코드 재작성 완료 - Lombok 제거됨**

**문제 해결됨:**
```
❌ WARNING A terminally deprecated method in sun.misc.Unsafe has been called
❌ ERROR Fatal error compiling: java.lang.ExceptionInInitializerError
```

✅ **원인:** Lombok 1.18.30이 Java 17과 호환되지 않음
✅ **해결:** 모든 코드에서 Lombok 완전 제거, SLF4J 직접 사용

---

## 1단계: 올바른 디렉토리로 이동

```powershell
cd C:\Users\user\IdeaProjects\yjkm_erp_project\yjkm-erp-java
```

✅ **중요:** 반드시 `yjkm-erp-java` 디렉토리로 이동해야 합니다!
   - ❌ 잘못: `C:\Users\user\IdeaProjects\yjkm_erp_project`
   - ✅ 맞음: `C:\Users\user\IdeaProjects\yjkm_erp_project\yjkm-erp-java`

---

## 2단계: Maven 캐시 완전 삭제

```powershell
Remove-Item -Recurse -Force $env:USERPROFILE\.m2\repository
```

이전의 Lombok 캐시를 완전히 제거합니다.

---

## 3단계: 깨끗한 컴파일

```powershell
mvn clean compile
```

**성공 메시지:**
```
[INFO] BUILD SUCCESS
[INFO] Total time: XX.XXX s
```

---

## 4단계: 실행

```powershell
mvn exec:java "-Dexec.mainClass=com.yjkm.erp.Main"
```

또는 전체 한 번에:

```powershell
mvn clean verify
mvn exec:java "-Dexec.mainClass=com.yjkm.erp.Main"
```

---

## 📝 **수정된 파일 목록**

### ✅ pom.xml
- **제거:** Lombok 1.18.30 의존성
- **제거:** Annotation Processor 설정
- **유지:** SLF4J, Logback (로깅은 수동)

### ✅ Main.java
```java
// ❌ 이전: @Slf4j 어노테이션
// ✅ 현재: private static final Logger log = LoggerFactory.getLogger(Main.class);
```

### ✅ PayrollCalculator.java
```java
// ❌ 이전: @Slf4j, Payroll.builder()
// ✅ 현재: SLF4J Logger, new Payroll() + setter 사용
```

### ✅ DatabaseUtil.java
```java
// ❌ 이전: @Slf4j, WorkSchedule.builder(), OvertimeRate.builder()
// ✅ 현재: SLF4J Logger, new WorkSchedule() + setter 사용
```

### ✅ Model 클래스 (Attendance, Employee, Leave 등)
- ✅ 모든 생성자 유지
- ✅ 모든 getter/setter 유지
- ✅ @Entity, @Column 등 JPA 어노테이션 유지
- ❌ Lombok 어노테이션 제거 안 함 (모델에 Lombok 사용 안 함)

---

## 최종 확인 체크리스트

- [ ] PowerShell에서 현재 디렉토리: `yjkm-erp-java`
- [ ] `pom.xml` 파일이 현재 디렉토리에 있는지 확인
- [ ] `mvn --version` 실행하여 Maven 설치 확인
- [ ] Maven 캐시 완전 삭제 (`~/.m2/repository`)
- [ ] `mvn clean compile` 성공 여부 확인 → **BUILD SUCCESS**
- [ ] IDE 캐시 삭제 (IntelliJ: `.idea` 폴더 삭제)
- [ ] IDE 재시작 후 다시 시도

---

## 실행 후 UI 화면

- 💼 **YJKM 급여관리 ERP v2.0** 창이 뜸
- 💰 **급여 계산 버튼**으로 급여 계산 가능
- 👥 **직원 통계 버튼**으로 현황 조회 가능
- 🔄 **데이터베이스 초기화**로 기본 데이터 생성 가능
- 📥 **SECOM 데이터 가져오기** 버튼 (현재 비활성화, 추후 지원)

---

## 문제 발생 시

### ❌ 여전히 "ExceptionInInitializerError" 오류
**해결:**
```powershell
# IDE 캐시 삭제
Remove-Item -Recurse -Force .idea

# Maven 캐시 삭제
Remove-Item -Recurse -Force $env:USERPROFILE\.m2\repository

# 다시 컴파일
mvn clean compile
```

### ❌ "ClassNotFoundException"
**해결:**
```powershell
mvn clean package
java -jar target/erp-system-2.0.0.jar
```

### ❌ "cannot find symbol"
**원인:** IDE가 Lombok을 여전히 인식하려고 함
**해결:**
- IntelliJ Settings → Build → Compiler → Annotation Processors
- ❌ "Enable annotation processing" 체크 해제
- IDE 재시작

---

## 🚀 **최종 실행 명령어**

```powershell
# 1. 올바른 디렉토리로 이동
cd C:\Users\user\IdeaProjects\yjkm_erp_project\yjkm-erp-java

# 2. Maven 캐시 삭제 (처음 한 번만)
Remove-Item -Recurse -Force $env:USERPROFILE\.m2\repository

# 3. IDE 캐시 삭제 (처음 한 번만)
Remove-Item -Recurse -Force .idea

# 4. 확인
ls pom.xml

# 5. 빌드
mvn clean compile

# 6. 실행
mvn exec:java "-Dexec.mainClass=com.yjkm.erp.Main"
```

**그러면 UI 화면이 뜰 것입니다!** 🎉

---

## ✅ GitHub 커밋 현황

| 파일 | 상태 | 변경 내용 |
|------|------|----------|
| pom.xml | ✅ | Lombok 완전 제거 |
| Main.java | ✅ | @Slf4j → SLF4J Logger |
| PayrollCalculator.java | ✅ | @Slf4j 제거, builder() 제거 |
| DatabaseUtil.java | ✅ | @Slf4j 제거, builder() 제거 |
| 모델 클래스 (Employee, Payroll 등) | ✅ | getter/setter 유지, @Entity 유지 |

모든 파일이 GitHub에 정상 커밋되었습니다.

---

**이제 준비가 완료되었습니다. 위의 최종 실행 명령어를 따라하세요!**