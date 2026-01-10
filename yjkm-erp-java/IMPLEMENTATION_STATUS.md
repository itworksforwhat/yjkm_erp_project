# 구현 상태 분석 및 추가 요구사항 매핑

## 📊 현재 구현 상태 (v2.0 - 2026-01-10)

### ✅ 완료된 기능

#### 1. 인사(HR) 기본
| 엔티티 | 구현 상태 | 주요 기능 | 비고 |
|--------|----------|----------|------|
| **Employee** | ✅ 완료 | 사원 기본정보, 연차 자동계산 | ⚠️ company_id 없음 |
| WorkSchedule | ✅ 완료 | 근무형태 정의 (주간/야간/2교대) | ⚠️ company_id 없음 |
| OvertimeRate | ✅ 완료 | 차등 잔업계수 (0.5x, 1.0x, 2.0x) | ⚠️ company_id 없음 |

**기존 Employee 필드:**
```java
- empCode (직원코드)
- name (이름)
- department (String) ⚠️ 단순 문자열
- position (직급)
- hireDate, resignationDate
- hourlyWage (시급)
- workSchedule (FK)
- secomCardNumber
- annualLeave, remainingLeave
```

**누락된 필드:**
- ❌ company_id
- ❌ resident_reg_no (주민번호)
- ❌ employment_status (재직/휴직/퇴직)
- ❌ employment_type (정규직/계약직)
- ❌ job_title (직책 vs 직급 분리)

---

#### 2. 근태 관리
| 엔티티 | 구현 상태 | 주요 기능 | 비고 |
|--------|----------|----------|------|
| **Attendance** | ✅ 완료 | 출퇴근 기록, 잔업/야간 자동계산 | 일 단위 집계 |
| ShiftSchedule | ✅ 완료 | 2교대 로테이션 관리 | 단순 로직 |
| **Leave** | ✅ 완료 | 휴가 신청/승인 | Leave.LeaveType enum |

**기존 Attendance 기능:**
```java
- 출퇴근 시간 기록
- 잔업시간 자동 계산 (총 근무시간 - 소정시간)
- 야간시간 자동 계산 (22:00~06:00)
- 근무유형 판단 (지각/조퇴/정상)
```

**누락된 기능:**
- ❌ employee_work_schedule (일별 스케줄 사전 배정)
- ❌ company_calendar (휴일 관리)
- ❌ 주 40시간 초과 계산
- ❌ 연장근로 vs 휴일근로 구분

---

#### 3. 급여 계산
| 엔티티 | 구현 상태 | 주요 기능 | 비고 |
|--------|----------|----------|------|
| **Payroll** | ✅ 완료 | 급여 계산, 4대보험, 소득세 | 단순 로직 |
| PayrollCalculator | ✅ 완료 | 월별 급여 계산 엔진 | Service 계층 |

**기존 Payroll 계산 로직:**
```java
- 기본급 = 근무시간 × 시급
- 잔업수당 = 차등 계산 (OvertimeRate)
- 야간수당 = 야간시간 × 시급 × 1.5
- 휴일수당 = 휴일시간 × 시급 × 1.5
- 4대보험 = 간단한 %
- 소득세 = 간이세액표 (단순)
```

**누락된 기능:**
- ❌ 통상시급 개념 (월급 → 통상시급 변환)
- ❌ 한국 근로기준법 정확한 연장/야간/휴일 가산
- ❌ 주 40시간 기준 연장근로 계산
- ❌ 수당/공제 코드화 (allowance_code, deduction_code)
- ❌ pay_period, pay_run (급여 회차 관리)
- ❌ 급여 상태 관리 (계산중/확정/지급)

---

#### 4. 데이터 Import
| 기능 | 구현 상태 | 주요 기능 | 비고 |
|------|----------|----------|------|
| **SECOM Import** | ✅ 완료 | S1/ERPExport.txt 파싱 | EUC-KR 지원 |
| SecomFileParser | ✅ 완료 | 19개 필드 파싱 | 직원 자동 생성 |

---

#### 5. UI 및 인프라
| 항목 | 구현 상태 | 기술 | 비고 |
|------|----------|------|------|
| UI | ✅ JavaFX | Material Design | ⚠️ 요구사항: REST API |
| Database | ✅ Hibernate + SQLite | JPA | ⚠️ 요구사항: MySQL/PostgreSQL |
| 빌드 | ✅ Maven | pom.xml | ✅ 유지 |
| 로깅 | ✅ SLF4J + Logback | logback.xml | ✅ 유지 |

---

## 🆕 새로운 요구사항 분석

### 1. 공통/권한/회사 구조 (⭐ 최우선)

#### 추가 필요 엔티티:

| 엔티티 | 우선순위 | 설명 | 구현 복잡도 |
|--------|---------|------|------------|
| **Company** | 🔴 P0 | 다중 회사 관리 (법인/개인) | 중 |
| **Department** | 🔴 P0 | 조직 구조 (계층형) | 중 |
| **UserAccount** | 🟡 P1 | 로그인 사용자 | 높음 (Security) |
| Role, Permission | 🟡 P1 | RBAC 권한 | 높음 |
| CompanyUser | 🟡 P1 | 회사별 권한 | 중 |
| CommonCode | 🟢 P2 | 코드 관리 | 낮음 |
| AuditLog | 🟢 P2 | 변경 이력 | 낮음 |

**영향 범위:**
- 모든 기존 엔티티에 `company_id` 추가 필요
- Employee.department를 String → Department FK로 변경
- 데이터 마이그레이션 필요

---

### 2. 인사(HR) 고도화

#### 추가 필요 엔티티:

| 엔티티 | 우선순위 | 설명 | 기존 대응 |
|--------|---------|------|----------|
| **EmployeeContract** | 🔴 P0 | 계약 이력 관리 | ❌ 없음 |
| EmployeePaySetting | 🔴 P0 | 사원별 급여 기준 | ⚠️ Employee에 일부 |
| PayGrade | 🟡 P1 | 급여 그룹 | ❌ 없음 |
| AllowanceCode | 🔴 P0 | 수당 코드 마스터 | ❌ 없음 |
| DeductionCode | 🔴 P0 | 공제 코드 마스터 | ❌ 없음 |

**Employee 개선 필요:**
```java
// 추가 필드
+ Long companyId;
+ String residentRegNo;  // 암호화
+ String employmentStatus;  // 재직/휴직/퇴직
+ String employmentType;    // 정규직/계약직/일용직
+ String jobTitle;          // 직책
+ Long departmentId;        // FK

// 변경
- String department;  → Long departmentId
```

---

### 3. 근태 고도화

#### 추가 필요 엔티티:

| 엔티티 | 우선순위 | 설명 | 기존 대응 |
|--------|---------|------|----------|
| **EmployeeWorkSchedule** | 🔴 P0 | 일별 스케줄 배정 | ⚠️ ShiftSchedule (단순) |
| **CompanyCalendar** | 🔴 P0 | 휴일 관리 | ❌ 없음 |
| AttendanceDailySummary | 🟡 P1 | 일별 집계 | ⚠️ Attendance 자체 |

**Attendance 개선 필요:**
```java
// 추가 필드
+ Integer regularMinutes;     // 소정근로시간
+ Integer extendedMinutes;    // 연장근로 (1일 8h 초과)
+ Integer weeklyOvertimeMinutes; // 주 40h 초과
+ Boolean isWeeklyRest;       // 주휴일
+ String holidayType;         // 법정/약정 휴일
```

---

### 4. 급여 고도화

#### 추가 필요 엔티티:

| 엔티티 | 우선순위 | 설명 | 기존 대응 |
|--------|---------|------|----------|
| **PayPeriod** | 🔴 P0 | 급여 기간 관리 | ❌ 없음 |
| **PayRun** | 🔴 P0 | 급여 회차 | ❌ 없음 |
| **PayEmployeeResult** | 🔴 P0 | 급여 헤더 | ⚠️ Payroll 유사 |
| PayEmployeeAllowance | 🔴 P0 | 수당 상세 | ❌ 없음 |
| PayEmployeeDeduction | 🔴 P0 | 공제 상세 | ❌ 없음 |
| LaborLawParam | 🟡 P1 | 법정 가산율 파라미터 | ❌ 없음 |
| TaxTable | 🟡 P1 | 세금 테이블 | ❌ 없음 |
| SocialInsRate | 🟡 P1 | 4대보험율 | ❌ 없음 |

**급여 계산 로직 개선:**
```java
// 기존: 단순 계산
basePay = workHours * hourlyWage;
overtimePay = overtimeHours * hourlyWage * multiplier;

// 개선: 한국 근로기준법 기반
통상시급 = 월급 / (주소정근로시간 × 4.345);
연장수당 = 연장시간 × 통상시급 × 1.5;
야간가산 = 야간시간 × 통상시급 × 0.5;
휴일수당 = 휴일근로시간 × 통상시급 × 1.5;
```

---

### 5. 회계 모듈 (🆕 완전히 새로운 영역)

#### 추가 필요 엔티티:

| 엔티티 | 우선순위 | 설명 | 복잡도 |
|--------|---------|------|--------|
| **Account** | 🔴 P0 | 계정과목 | 중 |
| **JournalEntry** | 🔴 P0 | 전표 헤더 | 높음 |
| **JournalEntryLine** | 🔴 P0 | 전표 라인 (차변/대변) | 높음 |
| PayrollAccountMapping | 🟡 P1 | 급여→회계 매핑 | 중 |
| FiscalPeriod | 🟡 P1 | 회계연도/월 | 낮음 |
| AccountingUnit | 🟢 P2 | 회계단위 | 낮음 |

**급여 전표 자동 생성 로직:**
```
급여 확정 → PayrollAccountMapping 기준 →
차변: 급여/복리후생비
대변: 보통예금, 예수금(세금), 미지급금(보험)
→ JournalEntry 생성
```

---

## 🔄 아키텍처 전환 이슈

### 현재: JavaFX 단일 애플리케이션
```
JavaFX UI → Service → Entity → Repository → SQLite
```

### 요구사항: Spring Boot REST API
```
React/Vue 등 → REST Controller → Service → Entity → Repository → MySQL/PostgreSQL
```

### 전환 전략:

#### Option 1: 점진적 전환 (권장)
1. **Phase 1**: Spring Boot 프로젝트 신규 생성
   - JavaFX 코드는 유지 (레거시)
   - Spring Boot로 새로운 API 개발
   - 동일한 Entity/Repository 재사용

2. **Phase 2**: Entity 리팩토링
   - company_id 추가
   - 새 엔티티 추가
   - 데이터 마이그레이션

3. **Phase 3**: 완전 전환
   - JavaFX 제거 또는 별도 클라이언트로 분리

#### Option 2: 일괄 전환
- 현재 코드 폐기
- Spring Boot로 처음부터 재작성
- ⚠️ 시간 소요 큰, 리스크 높음

---

## 📋 우선순위별 구현 계획

### 🔴 Phase 1: 핵심 인프라 (P0)
**목표**: 다중 회사 + 조직 + 계약 관리

#### 1.1 Company & Department
```java
@Entity
public class Company {
    @Id @GeneratedValue
    private Long id;
    private String companyCode;
    private String name;
    private String businessType;  // CORP, SOLE
    private String bizRegNo;
    private String ownerName;
    private LocalDate startDate;
    private String currency;
    private Boolean isActive;
}

@Entity
public class Department {
    @Id @GeneratedValue
    private Long id;

    @ManyToOne
    private Company company;

    private String deptCode;
    private String deptName;

    @ManyToOne
    @JoinColumn(name = "parent_dept_id")
    private Department parentDept;

    private String deptType;  // HQ, PLANT, LINE
}
```

#### 1.2 Employee 리팩토링
```java
@Entity
public class Employee {
    // 기존 필드 유지 +

    @ManyToOne
    private Company company;  // 🆕

    @ManyToOne
    private Department department;  // 🆕 (기존 String에서 변경)

    private String residentRegNo;  // 🆕 암호화
    private String employmentStatus;  // 🆕
    private String employmentType;  // 🆕
    private String jobTitle;  // 🆕
}
```

#### 1.3 EmployeeContract
```java
@Entity
public class EmployeeContract {
    @Id @GeneratedValue
    private Long id;

    @ManyToOne
    private Employee employee;

    private LocalDate startDate;
    private LocalDate endDate;
    private String contractType;
    private Integer weeklyHours;
    private Integer dailyHours;
    private String basePayType;  // MONTHLY, HOURLY
    private BigDecimal baseSalaryAmount;
    private Boolean overtimeAllowed;
}
```

**예상 기간**: 2-3일

---

### 🟡 Phase 2: 급여 고도화 (P1)
**목표**: 한국 근로기준법 기반 정확한 급여 계산

#### 2.1 수당/공제 코드화
```java
@Entity
public class AllowanceCode {
    @Id @GeneratedValue
    private Long id;

    @ManyToOne
    private Company company;

    private String code;
    private String name;
    private String calcType;  // HOUR_RATE, FIXED, PERCENT
    private BigDecimal rate;  // 0.5 (50%), 1.5 (150%)
    private Boolean isTaxable;
}

@Entity
public class DeductionCode {
    // 유사 구조
}
```

#### 2.2 PayPeriod & PayRun
```java
@Entity
public class PayPeriod {
    @Id @GeneratedValue
    private Long id;

    @ManyToOne
    private Company company;

    private Integer periodYear;
    private Integer periodMonth;
    private String payType;  // MONTHLY, BONUS
    private LocalDate workStartDate;
    private LocalDate workEndDate;
    private LocalDate payDate;
    private String status;  // PLANNED, CALCULATING, CONFIRMED
}

@Entity
public class PayRun {
    @Id @GeneratedValue
    private Long id;

    @ManyToOne
    private PayPeriod payPeriod;

    private Integer runNo;
    private String description;
    private String status;
}
```

#### 2.3 급여 계산 개선
```java
public class KoreanLaborLawCalculator {

    // 통상시급 계산
    public BigDecimal calculateOrdinaryHourlyWage(
        BigDecimal monthlySalary,
        Integer weeklyHours
    ) {
        return monthlySalary.divide(
            weeklyHours * 4.345,
            2,
            RoundingMode.HALF_UP
        );
    }

    // 연장수당 (1.5배)
    public BigDecimal calculateOvertimePay(
        Integer overtimeMinutes,
        BigDecimal ordinaryHourlyWage
    ) {
        BigDecimal hours = new BigDecimal(overtimeMinutes).divide(new BigDecimal(60));
        return hours.multiply(ordinaryHourlyWage).multiply(new BigDecimal("1.5"));
    }

    // 야간가산 (0.5배)
    public BigDecimal calculateNightAllowance(
        Integer nightMinutes,
        BigDecimal ordinaryHourlyWage
    ) {
        BigDecimal hours = new BigDecimal(nightMinutes).divide(new BigDecimal(60));
        return hours.multiply(ordinaryHourlyWage).multiply(new BigDecimal("0.5"));
    }
}
```

**예상 기간**: 3-4일

---

### 🟢 Phase 3: 회계 모듈 (P2)
**목표**: 급여 전표 자동 생성

#### 3.1 Account & JournalEntry
```java
@Entity
public class Account {
    @Id @GeneratedValue
    private Long id;

    @ManyToOne
    private Company company;

    private String accountCode;
    private String accountName;
    private String accountType;  // ASSET, LIABILITY, EQUITY, REVENUE, EXPENSE

    @ManyToOne
    private Account parentAccount;

    private Boolean isLeaf;
}

@Entity
public class JournalEntry {
    @Id @GeneratedValue
    private Long id;

    @ManyToOne
    private Company company;

    private String voucherNo;
    private LocalDate voucherDate;
    private String sourceModule;  // PAYROLL, MANUAL
    private Long sourceId;  // pay_run_id
    private String description;
    private String status;  // DRAFT, APPROVED, CLOSED
}

@Entity
public class JournalEntryLine {
    @Id @GeneratedValue
    private Long id;

    @ManyToOne
    private JournalEntry journalEntry;

    private Integer lineNo;

    @ManyToOne
    private Account account;

    private BigDecimal debitAmount;
    private BigDecimal creditAmount;

    @ManyToOne
    private Department department;

    @ManyToOne
    private Employee employee;
}
```

#### 3.2 급여 → 전표 매핑
```java
@Service
public class PayrollJournalService {

    public void generateJournalFromPayroll(Long payRunId) {
        PayRun payRun = payRunRepository.findById(payRunId);

        // 1. 급여 집계
        List<PayEmployeeResult> results = payEmployeeResultRepository
            .findByPayRun(payRun);

        BigDecimal totalBaseSalary = ...;
        BigDecimal totalTax = ...;
        BigDecimal totalSocialIns = ...;

        // 2. 전표 생성
        JournalEntry entry = new JournalEntry();
        entry.setSourceModule("PAYROLL");
        entry.setSourceId(payRunId);

        // 3. 라인 생성
        // 차변: 급여
        JournalEntryLine debit1 = new JournalEntryLine();
        debit1.setAccount(급여계정);
        debit1.setDebitAmount(totalBaseSalary);

        // 대변: 보통예금, 예수금 등
        // ...
    }
}
```

**예상 기간**: 4-5일

---

## ⚠️ 설계 괴리 해결 방안

### 1. UI 프레임워크 차이
- **현재**: JavaFX
- **요구**: REST API (Spring Boot)

**해결책**:
```
yjkm-erp-backend/   ← Spring Boot (새로 생성)
  ├── controller/   (REST API)
  ├── service/
  ├── entity/       ← 기존 코드 이관
  ├── repository/
  └── dto/

yjkm-erp-javafx/    ← 기존 JavaFX (유지 또는 폐기)
```

### 2. 데이터베이스 차이
- **현재**: SQLite
- **요구**: MySQL/PostgreSQL

**해결책**:
```yaml
# application.yml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/erp_db
    driver-class-name: com.mysql.cj.jdbc.Driver
  jpa:
    hibernate:
      ddl-auto: update
    properties:
      hibernate:
        dialect: org.hibernate.dialect.MySQLDialect
```

### 3. 보안 요구사항
- **현재**: 없음
- **요구**: Spring Security + JWT

**해결책**:
```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) {
        http
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/public/**").permitAll()
                .requestMatchers("/api/hr/**").hasRole("HR")
                .requestMatchers("/api/payroll/**").hasRole("PAYROLL")
                .requestMatchers("/api/accounting/**").hasRole("ACCOUNTING")
                .anyRequest().authenticated()
            )
            .oauth2ResourceServer().jwt();
        return http.build();
    }
}
```

---

## 📅 전체 구현 타임라인

| Phase | 기간 | 주요 작업 | 완료 기준 |
|-------|------|----------|----------|
| **Phase 0** | 1일 | Spring Boot 프로젝트 생성 | REST API 기본 구조 |
| **Phase 1** | 3일 | Company, Department, Contract | 다중 회사 지원 |
| **Phase 2** | 4일 | 급여 고도화 (한국법 기준) | 정확한 급여 계산 |
| **Phase 3** | 5일 | 회계 모듈 | 전표 자동 생성 |
| **Phase 4** | 3일 | Spring Security | 권한 관리 |
| **Total** | **16일** | | |

---

## 🎯 다음 단계

### 즉시 시작:
1. ✅ Spring Boot 프로젝트 생성
2. ✅ Company, Department Entity 추가
3. ✅ Employee 리팩토링 (company_id 추가)
4. ✅ EmployeeContract Entity 추가

### 순차 진행:
5. PayPeriod, PayRun 추가
6. AllowanceCode, DeductionCode 추가
7. 급여 계산 로직 개선
8. Account, JournalEntry 추가
9. 전표 자동 생성

---

**작성일**: 2026-01-10
**버전**: Analysis v1.0
