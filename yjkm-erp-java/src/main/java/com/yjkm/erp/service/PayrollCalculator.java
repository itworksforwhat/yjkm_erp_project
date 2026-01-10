package com.yjkm.erp.service;

import com.yjkm.erp.model.*;
import com.yjkm.erp.util.DatabaseUtil;
import jakarta.persistence.EntityManager;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.LocalDate;
import java.time.YearMonth;
import java.util.List;

/**
 * 급여 계산 엔진
 */
public class PayrollCalculator {
    private static final Logger log = LoggerFactory.getLogger(PayrollCalculator.class);

    /**
     * 단정 월의 전체 직원 급여 계산
     */
    public int calculateMonthlyPayroll(int year, int month) {
        log.info("급여 계산 시작: {}년 {}월", year, month);

        return DatabaseUtil.executeInTransaction(em -> {
            // 모든 활성 직원 조회
            List<Employee> employees = em.createQuery(
                    "SELECT e FROM Employee e WHERE e.resignationDate IS NULL", Employee.class)
                    .getResultList();

            int count = 0;
            for (Employee employee : employees) {
                try {
                    calculateEmployeePayroll(em, employee, year, month);
                    count++;
                } catch (Exception e) {
                    log.error("직원 {} 급여 계산 실패", employee.getName(), e);
                }
            }

            log.info("급여 계산 완료: {}\uba85", count);
            return count;
        });
    }

    /**
     * 단정 직원의 월별 급여 계산
     */
    private void calculateEmployeePayroll(EntityManager em, Employee employee, int year, int month) {
        // 기존 급여 기록 확인
        List<Payroll> existing = em.createQuery(
                "SELECT p FROM Payroll p WHERE p.employee = :employee AND p.year = :year AND p.month = :month",
                Payroll.class)
                .setParameter("employee", employee)
                .setParameter("year", year)
                .setParameter("month", month)
                .getResultList();

        Payroll payroll;
        if (existing.isEmpty()) {
            payroll = new Payroll();
            payroll.setEmployee(employee);
            payroll.setYear(year);
            payroll.setMonth(month);
        } else {
            payroll = existing.get(0);
        }

        // 해당 월의 출쟱근 기록 조회
        YearMonth yearMonth = YearMonth.of(year, month);
        LocalDate startDate = yearMonth.atDay(1);
        LocalDate endDate = yearMonth.atEndOfMonth();

        List<Attendance> attendances = em.createQuery(
                "SELECT a FROM Attendance a WHERE a.employee = :employee " +
                        "AND a.workDate >= :start AND a.workDate <= :end",
                Attendance.class)
                .setParameter("employee", employee)
                .setParameter("start", startDate)
                .setParameter("end", endDate)
                .getResultList();

        // 근무 정보 쟑계
        int workDays = attendances.size();
        double totalWorkMinutes = 0;
        double totalOvertimeMinutes = 0;
        double totalNightMinutes = 0;
        double totalHolidayMinutes = 0;

        for (Attendance att : attendances) {
            if (att.getCheckIn() != null && att.getCheckOut() != null) {
                totalWorkMinutes += att.calculateTotalWorkMinutes();

                if (att.getOvertimeMinutes() != null) {
                    totalOvertimeMinutes += att.getOvertimeMinutes();
                }
                if (att.getNightWorkMinutes() != null) {
                    totalNightMinutes += att.getNightWorkMinutes();
                }
                if (att.getIsHoliday() != null && att.getIsHoliday()) {
                    totalHolidayMinutes += att.calculateTotalWorkMinutes();
                }
            }
        }

        payroll.setWorkDays(workDays);
        payroll.setWorkHours(totalWorkMinutes / 60.0);
        payroll.setOvertimeHours(totalOvertimeMinutes / 60.0);
        payroll.setNightWorkHours(totalNightMinutes / 60.0);
        payroll.setHolidayWorkHours(totalHolidayMinutes / 60.0);

        // 급여 계산
        int hourlyWage = employee.getHourlyWage();

        // 기본급
        int basePay = (int) (totalWorkMinutes / 60.0 * hourlyWage);
        payroll.setBasePay(basePay);

        // 잡업수당 (차등 계산)
        int overtimePay = calculateOvertimePay(em, (int) totalOvertimeMinutes, hourlyWage);
        payroll.setOvertimePay(overtimePay);

        // 야간수당 (1.5배)
        int nightPay = (int) (totalNightMinutes / 60.0 * hourlyWage * 1.5);
        payroll.setNightWorkPay(nightPay);

        // 휴일수당 (1.5배)
        int holidayPay = (int) (totalHolidayMinutes / 60.0 * hourlyWage * 1.5);
        payroll.setHolidayPay(holidayPay);

        // 총 지급액 및 공제액 계산
        payroll.calculateTotalPay();
        payroll.calculateNetPay();

        // 저장
        if (existing.isEmpty()) {
            em.persist(payroll);
        } else {
            em.merge(payroll);
        }

        log.debug("급여 계산 완료: {} - 실수령액: {}\uc6d0", employee.getName(), payroll.getNetPay());
    }

    /**
     * 잡업수당 차등 계산
     */
    private int calculateOvertimePay(EntityManager em, int overtimeMinutes, int hourlyWage) {
        if (overtimeMinutes <= 0) {
            return 0;
        }

        // 잡업 계수 조회
        List<OvertimeRate> rates = em.createQuery(
                "SELECT o FROM OvertimeRate o ORDER BY o.fromMinutes", OvertimeRate.class)
                .getResultList();

        if (rates.isEmpty()) {
            // 기본 계수 없으면 1.0배
            return (int) (overtimeMinutes / 60.0 * hourlyWage);
        }

        int totalPay = 0;

        for (OvertimeRate rate : rates) {
            int applicableMinutes = getApplicableMinutes(rate, overtimeMinutes);
            if (applicableMinutes > 0) {
                double pay = (applicableMinutes / 60.0) * hourlyWage * rate.getMultiplier();
                totalPay += (int) pay;

                log.trace("잡업구간: {}\ubd84 × {}배 = {}\uc6d0",
                        applicableMinutes, rate.getMultiplier(), (int) pay);
            }
        }

        return totalPay;
    }

    /**
     * 단정 구간에서 적용 가능한 시간 계산
     */
    private int getApplicableMinutes(OvertimeRate rate, int overtimeMinutes) {
        int fromMinutes = rate.getFromMinutes();
        Integer toMinutes = rate.getToMinutes();

        if (overtimeMinutes <= fromMinutes) {
            return 0;
        }

        if (toMinutes == null) {
            // 무제한 구간
            return overtimeMinutes - fromMinutes;
        }

        if (overtimeMinutes <= toMinutes) {
            return overtimeMinutes - fromMinutes;
        }

        return toMinutes - fromMinutes;
    }

    /**
     * 단정 직원의 단정 월 급여 조회
     */
    public Payroll getPayroll(Long employeeId, int year, int month) {
        return DatabaseUtil.executeInTransaction(em -> {
            Employee employee = em.find(Employee.class, employeeId);
            if (employee == null) {
                throw new IllegalArgumentException("직원을 찾을 수 없습니다: " + employeeId);
            }

            List<Payroll> payrolls = em.createQuery(
                    "SELECT p FROM Payroll p WHERE p.employee = :employee AND p.year = :year AND p.month = :month",
                    Payroll.class)
                    .setParameter("employee", employee)
                    .setParameter("year", year)
                    .setParameter("month", month)
                    .getResultList();

            return payrolls.isEmpty() ? null : payrolls.get(0);
        });
    }
}