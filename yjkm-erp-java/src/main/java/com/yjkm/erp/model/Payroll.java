package com.yjkm.erp.model;

import jakarta.persistence.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.LocalDate;

/**
 * 급여 엔티티
 */
@Entity
@Table(name = "payrolls",
       uniqueConstraints = @UniqueConstraint(columnNames = {"employee_id", "year", "month"}))
public class Payroll {
    private static final Logger log = LoggerFactory.getLogger(Payroll.class);

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "payroll_id")
    private Long payrollId;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "employee_id", nullable = false)
    private Employee employee;

    @Column(name = "year", nullable = false)
    private Integer year;

    @Column(name = "month", nullable = false)
    private Integer month;

    @Column(name = "work_days")
    private Integer workDays;

    @Column(name = "work_hours")
    private Double workHours;

    @Column(name = "overtime_hours")
    private Double overtimeHours;

    @Column(name = "night_work_hours")
    private Double nightWorkHours;

    @Column(name = "holiday_work_hours")
    private Double holidayWorkHours;

    @Column(name = "base_pay")
    private Integer basePay;

    @Column(name = "overtime_pay")
    private Integer overtimePay;

    @Column(name = "night_work_pay")
    private Integer nightWorkPay;

    @Column(name = "holiday_pay")
    private Integer holidayPay;

    @Column(name = "bonus")
    private Integer bonus;

    @Column(name = "meal_allowance")
    private Integer mealAllowance;

    @Column(name = "total_pay")
    private Integer totalPay;

    @Column(name = "national_pension")
    private Integer nationalPension;

    @Column(name = "health_insurance")
    private Integer healthInsurance;

    @Column(name = "long_term_care")
    private Integer longTermCare;

    @Column(name = "employment_insurance")
    private Integer employmentInsurance;

    @Column(name = "income_tax")
    private Integer incomeTax;

    @Column(name = "local_tax")
    private Integer localTax;

    @Column(name = "total_deduction")
    private Integer totalDeduction;

    @Column(name = "net_pay")
    private Integer netPay;

    @Column(name = "notes", columnDefinition = "TEXT")
    private String notes;

    @Column(name = "calculated_at")
    private LocalDate calculatedAt;

    // 생성자
    public Payroll() {
    }

    public Payroll(Long payrollId, Employee employee, Integer year, Integer month, Integer workDays,
                   Double workHours, Double overtimeHours, Double nightWorkHours, Double holidayWorkHours,
                   Integer basePay, Integer overtimePay, Integer nightWorkPay, Integer holidayPay,
                   Integer bonus, Integer mealAllowance, Integer totalPay, Integer nationalPension,
                   Integer healthInsurance, Integer longTermCare, Integer employmentInsurance,
                   Integer incomeTax, Integer localTax, Integer totalDeduction, Integer netPay,
                   String notes, LocalDate calculatedAt) {
        this.payrollId = payrollId;
        this.employee = employee;
        this.year = year;
        this.month = month;
        this.workDays = workDays;
        this.workHours = workHours;
        this.overtimeHours = overtimeHours;
        this.nightWorkHours = nightWorkHours;
        this.holidayWorkHours = holidayWorkHours;
        this.basePay = basePay;
        this.overtimePay = overtimePay;
        this.nightWorkPay = nightWorkPay;
        this.holidayPay = holidayPay;
        this.bonus = bonus;
        this.mealAllowance = mealAllowance;
        this.totalPay = totalPay;
        this.nationalPension = nationalPension;
        this.healthInsurance = healthInsurance;
        this.longTermCare = longTermCare;
        this.employmentInsurance = employmentInsurance;
        this.incomeTax = incomeTax;
        this.localTax = localTax;
        this.totalDeduction = totalDeduction;
        this.netPay = netPay;
        this.notes = notes;
        this.calculatedAt = calculatedAt;
    }

    // Getter/Setter
    public Long getPayrollId() { return payrollId; }
    public void setPayrollId(Long payrollId) { this.payrollId = payrollId; }

    public Employee getEmployee() { return employee; }
    public void setEmployee(Employee employee) { this.employee = employee; }

    public Integer getYear() { return year; }
    public void setYear(Integer year) { this.year = year; }

    public Integer getMonth() { return month; }
    public void setMonth(Integer month) { this.month = month; }

    public Integer getWorkDays() { return workDays; }
    public void setWorkDays(Integer workDays) { this.workDays = workDays; }

    public Double getWorkHours() { return workHours; }
    public void setWorkHours(Double workHours) { this.workHours = workHours; }

    public Double getOvertimeHours() { return overtimeHours; }
    public void setOvertimeHours(Double overtimeHours) { this.overtimeHours = overtimeHours; }

    public Double getNightWorkHours() { return nightWorkHours; }
    public void setNightWorkHours(Double nightWorkHours) { this.nightWorkHours = nightWorkHours; }

    public Double getHolidayWorkHours() { return holidayWorkHours; }
    public void setHolidayWorkHours(Double holidayWorkHours) { this.holidayWorkHours = holidayWorkHours; }

    public Integer getBasePay() { return basePay; }
    public void setBasePay(Integer basePay) { this.basePay = basePay; }

    public Integer getOvertimePay() { return overtimePay; }
    public void setOvertimePay(Integer overtimePay) { this.overtimePay = overtimePay; }

    public Integer getNightWorkPay() { return nightWorkPay; }
    public void setNightWorkPay(Integer nightWorkPay) { this.nightWorkPay = nightWorkPay; }

    public Integer getHolidayPay() { return holidayPay; }
    public void setHolidayPay(Integer holidayPay) { this.holidayPay = holidayPay; }

    public Integer getBonus() { return bonus; }
    public void setBonus(Integer bonus) { this.bonus = bonus; }

    public Integer getMealAllowance() { return mealAllowance; }
    public void setMealAllowance(Integer mealAllowance) { this.mealAllowance = mealAllowance; }

    public Integer getTotalPay() { return totalPay; }
    public void setTotalPay(Integer totalPay) { this.totalPay = totalPay; }

    public Integer getNationalPension() { return nationalPension; }
    public void setNationalPension(Integer nationalPension) { this.nationalPension = nationalPension; }

    public Integer getHealthInsurance() { return healthInsurance; }
    public void setHealthInsurance(Integer healthInsurance) { this.healthInsurance = healthInsurance; }

    public Integer getLongTermCare() { return longTermCare; }
    public void setLongTermCare(Integer longTermCare) { this.longTermCare = longTermCare; }

    public Integer getEmploymentInsurance() { return employmentInsurance; }
    public void setEmploymentInsurance(Integer employmentInsurance) { this.employmentInsurance = employmentInsurance; }

    public Integer getIncomeTax() { return incomeTax; }
    public void setIncomeTax(Integer incomeTax) { this.incomeTax = incomeTax; }

    public Integer getLocalTax() { return localTax; }
    public void setLocalTax(Integer localTax) { this.localTax = localTax; }

    public Integer getTotalDeduction() { return totalDeduction; }
    public void setTotalDeduction(Integer totalDeduction) { this.totalDeduction = totalDeduction; }

    public Integer getNetPay() { return netPay; }
    public void setNetPay(Integer netPay) { this.netPay = netPay; }

    public String getNotes() { return notes; }
    public void setNotes(String notes) { this.notes = notes; }

    public LocalDate getCalculatedAt() { return calculatedAt; }
    public void setCalculatedAt(LocalDate calculatedAt) { this.calculatedAt = calculatedAt; }

    // 메서드
    public void calculateInsurance() {
        int pensionBase = Math.min(totalPay, 5_900_000);
        nationalPension = (int) (pensionBase * 0.045);
        healthInsurance = (int) (totalPay * 0.03545);
        longTermCare = (int) (healthInsurance * 0.1295);
        employmentInsurance = (int) (totalPay * 0.009);
    }

    public void calculateIncomeTax() {
        int taxableIncome = totalPay;

        if (taxableIncome < 1_060_000) {
            incomeTax = 0;
        } else if (taxableIncome < 2_100_000) {
            incomeTax = (int) ((taxableIncome - 1_060_000) * 0.06);
        } else if (taxableIncome < 3_460_000) {
            incomeTax = 62_400 + (int) ((taxableIncome - 2_100_000) * 0.15);
        } else if (taxableIncome < 7_090_000) {
            incomeTax = 266_400 + (int) ((taxableIncome - 3_460_000) * 0.24);
        } else {
            incomeTax = 1_137_600 + (int) ((taxableIncome - 7_090_000) * 0.35);
        }

        localTax = (int) (incomeTax * 0.1);
    }

    public void calculateNetPay() {
        calculateInsurance();
        calculateIncomeTax();
        totalDeduction = nationalPension + healthInsurance + longTermCare
                + employmentInsurance + incomeTax + localTax;
        netPay = totalPay - totalDeduction;
    }

    public void calculateTotalPay() {
        totalPay = basePay + overtimePay + nightWorkPay + holidayPay
                + (bonus != null ? bonus : 0)
                + (mealAllowance != null ? mealAllowance : 0);
    }

    @PrePersist
    @PreUpdate
    protected void onSave() {
        calculatedAt = LocalDate.now();
        if (bonus == null) bonus = 0;
        if (mealAllowance == null) mealAllowance = 0;
        calculateTotalPay();
        calculateNetPay();
    }
}
