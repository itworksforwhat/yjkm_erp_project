# 기여 가이드라인

YJKM ERP 프로젝트에 기여해주셔서 감사합니다! 이 문서는 기여 프로세스를 설명합니다.

---

## 📋 기여 규칙

### 🟢 프로덕션 버전 (Java)

**적극적인 기여 환영합니다!**

- ✅ 새로운 기능 추가
- ✅ 버그 수정
- ✅ 성능 개선
- ✅ 문서 업데이트
- ✅ 테스트 추가

### 🔴 레거시 버전 (Python)

**중대한 버그 수정만 권장합니다.**

- ⚠️ 버그 수정 (심각한 경우에만)
- ❌ 새로운 기능 추가 (금지)
- ❌ 코드 리팩토링 (폐기 예정이므로 불필요)
- ✅ 문서 업데이트

---

## 🚀 기여 프로세스

### 1단계: 이슈 확인 또는 생성

```bash
# 이미 있는 이슈 확인
# https://github.com/itworksforwhat/yjkm_erp_project/issues

# 새 이슈 생성
제목: [Java] Payroll calculation bug for overtime
또는
제목: [Python] Database connection timeout (Legacy)
```

### 2단계: Fork 및 Branch 생성

```bash
# Fork the repository
git clone https://github.com/YOUR-USERNAME/yjkm_erp_project.git
cd yjkm_erp_project

# Create feature branch
# 규칙: feature/<issue-number>-<description>
git checkout -b feature/123-add-bonus-calculation

# 또는 버그 수정
git checkout -b bugfix/456-fix-overtime-calculation

# 또는 문서
git checkout -b docs/update-readme
```

### 3단계: 코드 작성

#### Java 코드 스타일

```java
// ✅ Good
public class PayrollCalculator {
    private static final double OVERTIME_RATE = 1.5;
    
    public double calculateOvertimePay(double baseSalary, int overtimeHours) {
        return baseSalary / 160 * OVERTIME_RATE * overtimeHours;
    }
}

// ❌ Bad
public class Payroll{
public static void calculate(){
// 주석 없음
```

**가이드라인:**
- 클래스명: PascalCase (예: `PayrollCalculator`)
- 메서드명: camelCase (예: `calculateOvertimePay`)
- 상수: UPPER_SNAKE_CASE (예: `OVERTIME_RATE`)
- 들여쓰기: 4 spaces
- 한 줄 최대 길이: 100자
- 공개 메서드에는 JavaDoc 작성

#### Python 코드 스타일 (레거시)

```python
# 기존 코드 스타일 유지
# PEP 8 표준 준수
```

### 4단계: 커밋

```bash
# 명확한 커밋 메시지
git commit -m "feat: Add bonus calculation for payroll"
git commit -m "fix: Correct overtime rate calculation"
git commit -m "docs: Update Java setup guide"

# 또는 자세한 메시지
git commit -m "feat: Add bonus calculation for payroll

- Implements bonus calculation for performance reviews
- Adds new BonusCalculator class
- Includes unit tests
- Updates database schema"
```

**커밋 메시지 규칙:**
```
<type>: <subject>

<body>

<footer>
```

**타입:**
- `feat`: 새로운 기능
- `fix`: 버그 수정
- `docs`: 문서 변경
- `style`: 코드 포맷팅 (로직 변경 없음)
- `refactor`: 코드 재구조화
- `perf`: 성능 개선
- `test`: 테스트 추가
- `chore`: 빌드, 의존성 업데이트 등

### 5단계: 테스트

#### Java 테스트

```bash
cd yjkm-erp-java

# 모든 테스트 실행
mvn test

# 특정 테스트 클래스
mvn test -Dtest=PayrollCalculatorTest

# 테스트 커버리지
mvn test jacoco:report
```

**새 기능에는 반드시 테스트 추가:**

```java
public class PayrollCalculatorTest {
    private PayrollCalculator calculator;
    
    @Before
    public void setUp() {
        calculator = new PayrollCalculator();
    }
    
    @Test
    public void testOvertimeCalculation() {
        double salary = 2000000; // 200만원
        int hours = 10;
        double expected = 2000000 / 160 * 1.5 * 10;
        
        assertEquals(expected, calculator.calculateOvertimePay(salary, hours), 0.01);
    }
}
```

#### Python 테스트 (레거시)

```bash
cd python
pytest tests/
```

### 6단계: Push 및 Pull Request

```bash
# 원격 저장소로 Push
git push origin feature/123-add-bonus-calculation

# GitHub에서 Pull Request 생성
# https://github.com/itworksforwhat/yjkm_erp_project/pulls
```

**Pull Request 템플릿:**

```markdown
## 📝 설명

어떤 변경을 했는지 간단히 설명해주세요.

## 🔗 관련 이슈

Fixes #123

## 📸 스크린샷 (해당하는 경우)

## ✅ 체크리스트

- [ ] 코드가 Java/Python 스타일 가이드를 따릅니다
- [ ] 테스트를 추가했습니다
- [ ] 문서를 업데이트했습니다
- [ ] 커밋 메시지가 명확합니다
- [ ] 로컬 테스트를 실행했습니다

## 🎯 타입

- [x] 버그 수정
- [ ] 새로운 기능
- [ ] 문서 업데이트
- [ ] 성능 개선
```

---

## 🔍 코드 리뷰

### 리뷰 기준

1. **코드 품질**
   - 가독성
   - 유지보수성
   - 성능
   - 보안

2. **테스트**
   - 테스트 커버리지
   - 엣지 케이스 처리
   - 통합 테스트

3. **문서**
   - JavaDoc / 주석
   - README 업데이트
   - 사용자 가이드

4. **규칙 준수**
   - 스타일 가이드
   - 커밋 메시지 규칙
   - 브랜치 명명 규칙

### 리뷰어에게

```markdown
# 좋은 리뷰
✅ 구체적인 피드백
✅ 개선 제안
✅ 칭찬과 격려
✅ 이유 설명

# 피해야 할 리뷰
❌ 막연한 지적
❌ 감정적 표현
❌ 상대방 비판
```

---

## 📚 커뮤니티 가이드

### 행동 규칙

우리는 다음을 약속합니다:

- 🤝 서로를 존중합니다
- 🛡️ 괴롭힘을 용납하지 않습니다
- 🤲 포용적인 환경을 만듭니다
- 📝 건설적인 피드백을 제공합니다

---

## 💬 질문이 있으신가요?

### 채널

- 📝 **이슈**: 버그 리포트 및 기능 제안
  https://github.com/itworksforwhat/yjkm_erp_project/issues

- 💬 **Discussions**: 질문 및 토론
  https://github.com/itworksforwhat/yjkm_erp_project/discussions

- 📧 **이메일**: support@yjkm.co.kr

---

## 🙏 감사합니다!

기여해주셔서 정말 감사합니다! 당신의 도움이 YJKM ERP를 더욱 좋게 만듭니다.

---

**마지막 업데이트**: 2026년 1월 11일
