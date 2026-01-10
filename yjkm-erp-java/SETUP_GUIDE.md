# YJKM ERP System - 빌드 및 실행 가이드

## 🔴 **이전 문제 - 해결됨**

```
❌ ERROR: Fatal error compiling: java.lang.ExceptionInInitializerError
❌ WARNING: A terminally deprecated method in sun.misc.Unsafe has been called
```

**원인:** Lombok 1.18.30이 Java 17과 호환되지 않음
**해결:** Lombok 완전 제거 및 모든 코드 재작성 ✅

---

## 1단계: 올바른 디렉토리로 이동

```powershell
cd C:\Users\user\IdeaProjects\yjkm_erp_project\yjkm-erp-java
```

✅ **중요:** 반드시 `yjkm-erp-java` 디렉토리로 이동해야 합니다!
   - ❌ 잘못: `C:\Users\user\IdeaProjects\yjkm_erp_project`
   - ✅ 맞음: `C:\Users\user\IdeaProjects\yjkm_erp_project\yjkm-erp-java`

---

## 2단계: Maven 캐시 삭제 (처음 한 번만)

```powershell
Remove-Item -Recurse -Force $env:USERPROFILE\.m2\repository
```

Lombok 제거 후 처음 실행할 때만 필요합니다.

---

## 3단계: 깨끗한 컴파일

```powershell
mvn clean compile
```

**성공 메시지:**
```
[INFO] BUILD SUCCESS
[INFO] Total time: X.XXX s
[INFO] Finished at: 2026-01-11T06:XX:XX+09:00
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

## 자주 발생하는 오류 해결

### 오류 1: "MissingProjectException" - pom.xml을 찾을 수 없음
**원인:** 잘못된 디렉토리에서 실행
**해결:** 반드시 `yjkm-erp-java` 디렉토리로 이동

```powershell
ls pom.xml  # 파일이 보여야 함
```

### 오류 2: "Cannot find symbol" - 컴파일 오류
**원인:** Maven 캐시가 오래됨
**해결:** 
```powershell
# Maven 캐시 완전 삭제
Remove-Item -Recurse -Force $env:USERPROFILE\.m2\repository

# 다시 컴파일
mvn clean compile
```

### 오류 3: `exec:java` 명령어 인식 못함
**원인:** Maven 플러그인 설정 부족 (매우 드문 경우)
**해결:** 
```powershell
# 대신 이렇게 실행:
mvn clean package
java -jar target/erp-system-2.0.0.jar
```

### 오류 4: "ExceptionInInitializerError" 여전히 발생
**원인:** IDE 캐시가 오래 Lombok 정보 보유
**해결:**
```powershell
# IDE 재시작 (IntelliJ 종료 후 재시작)
# 또는 전체 IDE 캐시 삭제
Remove-Item -Recurse -Force $env:LOCALAPPDATA\JetBrains\IntelliJIdea*\caches
```

---

## 최종 확인 체크리스트

- [ ] PowerShell에서 현재 디렉토리: `yjkm-erp-java`
- [ ] `ls pom.xml` 실행하여 파일 확인
- [ ] `mvn --version` 실행하여 Maven 설치 확인
- [ ] Maven 캐시 삭제 완료
- [ ] `mvn clean compile` 성공 (BUILD SUCCESS)
- [ ] `mvn exec:java` 실행 가능

---

## 실행 후 UI 화면

- 💼 **YJKM 급여관리 ERP v2.0** 창이 뜸
- 💰 **급여 계산** 버튼으로 급여 계산 가능
- 👥 **직원 통계** 버튼으로 현황 조회 가능
- 🔄 **데이터베이스 초기화** 버튼으로 기본 데이터 생성 가능
- 📥 **SECOM 데이터 가져오기** (현재 비활성화, 향후 지원)

---

## 📝 **GitHub 최신 변경사항**

### ✅ 완성된 파일

| 파일 | 변경 사항 | 상태 |
|------|----------|------|
| **pom.xml** | Lombok 의존성 제거 | ✅ 완료 |
| **Main.java** | `@Slf4j` → SLF4J Logger | ✅ 완료 |
| **PayrollCalculator.java** | `builder()` 제거 | ✅ 완료 |
| **DatabaseUtil.java** | `builder()` 제거 | ✅ 완료 |
| **모든 Model 클래스** | getter/setter 유지 | ✅ 완료 |
| **SETUP_GUIDE.md** | 설치 가이드 | ✅ 완료 |

모든 파일이 정상적으로 GitHub에 커밋되어 있습니다.

---

## 🚀 **최종 실행 명령어**

```powershell
# 1. 올바른 디렉토리로 이동
cd C:\Users\user\IdeaProjects\yjkm_erp_project\yjkm-erp-java

# 2. Maven 캐시 삭제 (처음만)
Remove-Item -Recurse -Force $env:USERPROFILE\.m2\repository

# 3. 확인
ls pom.xml
mvn --version

# 4. 빌드
mvn clean compile

# 5. 실행
mvn exec:java "-Dexec.mainClass=com.yjkm.erp.Main"
```

**그러면 UI 화면이 뜰 것입니다!** 🎉

---

## 📚 **추가 정보**

### Lombok 제거 이유
- Java 17과 Lombok 1.18.30의 호환성 문제
- Lombok이 Java 내부 deprecated API 사용
- 간단한 setter/getter는 수동 구현이 더 명확함

### 사용된 기술
- **Java 17** - 최신 LTS 버전
- **JavaFX 21.0.1** - 현대적 UI
- **Hibernate 6.4.1** - ORM
- **SQLite** - 경량 데이터베이스
- **SLF4J + Logback** - 로깅
- **Maven 3.9+** - 빌드 도구

---

**문제 발생 시 위의 "자주 발생하는 오류 해결" 섹션을 참고하세요!**