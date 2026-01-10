package com.yjkm.erp.model;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDate;
import lombok.extern.slf4j.Slf4j;

@Slf4j
/**
 * 급여 엔티티
 */
@Entity
@Table(name = "payrolls",
       uniqueConstraints = @UniqueConstraint(columnNames = {"employee_id", "year", "month"}))
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Payroll {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "payroll_id")
    private Long payrollId;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "employee_id", nullable = false)
    private Employee employee;

    @Column(name = "year", nullable = false)
    private Integer year;  // 년도

    @Column(name = "month", nullable = false)
    private Integer month;  // 월

    // 근무 정보
    @Column(name = "work_days")
    private Integer workDays;  // 근무일수

    @Column(name = "work_hours")
    private Double workHours;  // 근무시간

    @Column(name = "overtime_hours")
    private Double overtimeHours;  // 잔업시간

    @Column(name = "night_work_hours")
    private Double nightWorkHours;  // 야간근무시간

    @Column(name = "holiday_work_hours")
    private Double holidayWorkHours;  // 휴일근무시간

    // 급여 항목
    @Column(name = "base_pay")
    private Integer basePay;  // 기본급 (시급 * 근무시간)

    @Column(name = "overtime_pay")
    private Integer overtimePay;  // 잔업수당

    @Column(name = "night_work_pay")
    private Integer nightWorkPay;  // 야간수당

    @Column(name = "holiday_pay")
    private Integer holidayPay;  // 휴일수당

    @Column(name = "bonus")
    private Integer bonus;  // 상여금

    @Column(name = "meal_allowance")
    private Integer mealAllowance;  // 식대

    @Column(name = "total_pay")
    private Integer totalPay;  // 총 지급액

    // 공제 항목
    @Column(name = "national_pension")
    private Integer nationalPension;  // 국민연금 (4.5%)

    @Column(name = "health_insurance")
    private Integer healthInsurance;  // 건강보험 (3.545%)

    @Column(name = "long_term_care")
    private Integer longTermCare;  // 장기요양 (건강보험 * 0.1295)

    @Column(name = "employment_insurance")
    private Integer employmentInsurance;  // 고용보험 (0.9%)

    @Column(name = "income_tax")
    private Integer incomeTax;  // 소득세

    @Column(name = "local_tax")
    private Integer localTax;  // 지방세 (소득세 * 0.1)

    @Column(name = "total_deduction")
    private Integer totalDeduction;  // 총 공제액

    @Column(name = "net_pay")
    private Integer netPay;  // 실수령액

    @Column(name = "notes", columnDefinition = "TEXT")
    private String notes;  // 비고

    @Column(name = "calculated_at")
    private LocalDate calculatedAt;  // 계산일

    /**
     * 4대보험 자동 계산
     */
    public void calculateInsurance() {
        // 국민연금: 4.5% (상한: 590만원)
        int pensionBase = Math.min(totalPay, 5_900_000);
        nationalPension = (int) (pensionBase * 0.045);

        // 건강보험: 3.545% (장기요양 포함)
        healthInsurance = (int) (totalPay * 0.03545);
        longTermCare = (int) (healthInsurance * 0.1295);

        // 고용보험: 0.9%
        employmentInsurance = (int) (totalPay * 0.009);
    }

    /**
     * 소득세 간이세액 계산 (간이세액표 기준)
     */
    public void calculateIncomeTax() {
        // 간단한 간이세액표 로직 (실제로는 더 복잡함)
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

        // 지방소득세: 소득세의 10%
        localTax = (int) (incomeTax * 0.1);
    }

    /**
     * 총 공제액 및 실수령액 계산
     */
    public void calculateNetPay() {
        calculateInsurance();
        calculateIncomeTax();

        totalDeduction = nationalPension + healthInsurance + longTermCare
                + employmentInsurance + incomeTax + localTax;

        netPay = totalPay - totalDeduction;
    }

    /**
     * 총 지급액 계산
     */
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
