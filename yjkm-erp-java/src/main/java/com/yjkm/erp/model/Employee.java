package com.yjkm.erp.model;

import jakarta.persistence.*;
import java.time.LocalDate;

/**
 * 직원 엔티티
 */
@Entity
@Table(name = "employees")
public class Employee {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "employee_id")
    private Long employeeId;

    @Column(name = "emp_code", nullable = false, unique = true, length = 50)
    private String empCode;  // 직원코드

    @Column(name = "name", nullable = false, length = 100)
    private String name;  // 이름

    @Column(name = "department", length = 100)
    private String department;  // 부서

    @Column(name = "position", length = 50)
    private String position;  // 직급

    @Column(name = "hire_date", nullable = false)
    private LocalDate hireDate;  // 입사일

    @Column(name = "resignation_date")
    private LocalDate resignationDate;  // 퇴사일

    @Column(name = "hourly_wage", nullable = false)
    private Integer hourlyWage;  // 시급

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "schedule_id")
    private WorkSchedule workSchedule;  // 근무형태

    @Column(name = "phone", length = 20)
    private String phone;  // 전화번호

    @Column(name = "email", length = 100)
    private String email;  // 이메일

    @Column(name = "bank_name", length = 50)
    private String bankName;  // 은행명

    @Column(name = "account_number", length = 50)
    private String accountNumber;  // 계좌번호

    @Column(name = "secom_employee_id", length = 50)
    private String secomEmployeeId;  // 세콤직원ID

    @Column(name = "secom_card_number", length = 50)
    private String secomCardNumber;  // 세콤카드번호

    @Column(name = "annual_leave")
    private Integer annualLeave;  // 연차일수

    @Column(name = "remaining_leave")
    private Double remainingLeave;  // 잔여연차

    @Column(name = "notes", columnDefinition = "TEXT")
    private String notes;  // 비고

    @Column(name = "created_at")
    private LocalDate createdAt;

    @Column(name = "updated_at")
    private LocalDate updatedAt;

    // ===== 생성자 =====
    public Employee() {}

    public Employee(Long employeeId, String empCode, String name, String department, String position, LocalDate hireDate, LocalDate resignationDate, Integer hourlyWage, WorkSchedule workSchedule, String phone, String email, String bankName, String accountNumber, String secomEmployeeId, String secomCardNumber, Integer annualLeave, Double remainingLeave, String notes, LocalDate createdAt, LocalDate updatedAt) {
        this.employeeId = employeeId;
        this.empCode = empCode;
        this.name = name;
        this.department = department;
        this.position = position;
        this.hireDate = hireDate;
        this.resignationDate = resignationDate;
        this.hourlyWage = hourlyWage;
        this.workSchedule = workSchedule;
        this.phone = phone;
        this.email = email;
        this.bankName = bankName;
        this.accountNumber = accountNumber;
        this.secomEmployeeId = secomEmployeeId;
        this.secomCardNumber = secomCardNumber;
        this.annualLeave = annualLeave;
        this.remainingLeave = remainingLeave;
        this.notes = notes;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
    }

    // ===== Getter/Setter =====
    public Long getEmployeeId() { return employeeId; }
    public void setEmployeeId(Long employeeId) { this.employeeId = employeeId; }

    public String getEmpCode() { return empCode; }
    public void setEmpCode(String empCode) { this.empCode = empCode; }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public String getDepartment() { return department; }
    public void setDepartment(String department) { this.department = department; }

    public String getPosition() { return position; }
    public void setPosition(String position) { this.position = position; }

    public LocalDate getHireDate() { return hireDate; }
    public void setHireDate(LocalDate hireDate) { this.hireDate = hireDate; }

    public LocalDate getResignationDate() { return resignationDate; }
    public void setResignationDate(LocalDate resignationDate) { this.resignationDate = resignationDate; }

    public Integer getHourlyWage() { return hourlyWage; }
    public void setHourlyWage(Integer hourlyWage) { this.hourlyWage = hourlyWage; }

    public WorkSchedule getWorkSchedule() { return workSchedule; }
    public void setWorkSchedule(WorkSchedule workSchedule) { this.workSchedule = workSchedule; }

    public String getPhone() { return phone; }
    public void setPhone(String phone) { this.phone = phone; }

    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }

    public String getBankName() { return bankName; }
    public void setBankName(String bankName) { this.bankName = bankName; }

    public String getAccountNumber() { return accountNumber; }
    public void setAccountNumber(String accountNumber) { this.accountNumber = accountNumber; }

    public String getSecomEmployeeId() { return secomEmployeeId; }
    public void setSecomEmployeeId(String secomEmployeeId) { this.secomEmployeeId = secomEmployeeId; }

    public String getSecomCardNumber() { return secomCardNumber; }
    public void setSecomCardNumber(String secomCardNumber) { this.secomCardNumber = secomCardNumber; }

    public Integer getAnnualLeave() { return annualLeave; }
    public void setAnnualLeave(Integer annualLeave) { this.annualLeave = annualLeave; }

    public Double getRemainingLeave() { return remainingLeave; }
    public void setRemainingLeave(Double remainingLeave) { this.remainingLeave = remainingLeave; }

    public String getNotes() { return notes; }
    public void setNotes(String notes) { this.notes = notes; }

    public LocalDate getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDate createdAt) { this.createdAt = createdAt; }

    public LocalDate getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(LocalDate updatedAt) { this.updatedAt = updatedAt; }

    // ===== 비즈니스 로직 =====
    /**
     * 퇴사 여부 확인
     */
    public boolean isResigned() {
        return resignationDate != null;
    }

    /**
     * 근속년수 계산
     */
    public int getYearsOfService() {
        LocalDate endDate = isResigned() ? resignationDate : LocalDate.now();
        return endDate.getYear() - hireDate.getYear();
    }

    /**
     * 연차 자동 계산 (근속년수 기준)
     */
    public int calculateAnnualLeave() {
        int years = getYearsOfService();

        if (years < 1) {
            // 1년 미만: 월차 (입사월 기준)
            long months = java.time.temporal.ChronoUnit.MONTHS.between(hireDate, LocalDate.now());
            return (int) months;
        } else if (years == 1) {
            return 15;
        } else if (years == 2) {
            return 15;
        } else if (years == 3) {
            return 16;
        } else if (years < 5) {
            return 17;
        } else if (years < 7) {
            return 18;
        } else if (years < 9) {
            return 19;
        } else if (years < 11) {
            return 20;
        } else {
            // 11년 이상: 2년마다 +1일, 최대 25일
            int additionalDays = (years - 11) / 2 + 1;
            return Math.min(25, 20 + additionalDays);
        }
    }

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDate.now();
        updatedAt = LocalDate.now();
        if (annualLeave == null) {
            annualLeave = calculateAnnualLeave();
            remainingLeave = annualLeave.doubleValue();
        }
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDate.now();
    }
}