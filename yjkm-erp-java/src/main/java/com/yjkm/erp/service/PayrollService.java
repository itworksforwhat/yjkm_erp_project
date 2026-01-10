package com.yjkm.erp.service;

import com.yjkm.erp.model.Payroll;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.LocalDate;

public class PayrollService {
    private static final Logger log = LoggerFactory.getLogger(PayrollService.class);

    public Payroll calculatePayroll(Payroll payroll) {
        log.info("급여 계산 시작: Employee={}, Year={}, Month={}",
                payroll.getEmployee().getEmployeeId(), payroll.getYear(), payroll.getMonth());

        // 기본급 계산
        if (payroll.getWorkHours() != null) {
            int hourlyRate = 10000; // 시급
            payroll.setBasePay((int) (payroll.getWorkHours() * hourlyRate));
        }

        // 총 급여 계산
        payroll.calculateTotalPay();

        // 공제액 계산
        payroll.calculateNetPay();

        payroll.setCalculatedAt(LocalDate.now());

        log.info("급여 계산 완료: Total={}, Deduction={}, Net={}",
                payroll.getTotalPay(), payroll.getTotalDeduction(), payroll.getNetPay());

        return payroll;
    }
}
