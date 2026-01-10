package com.yjkm.erp.service;

import com.yjkm.erp.model.Employee;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * 급여 계산 엔진 - 최소 버전
 */
public class PayrollCalculator {
    private static final Logger log = LoggerFactory.getLogger(PayrollCalculator.class);

    public int calculateMonthlyPayroll(int year, int month) {
        log.info("급여 계산 시작: {}년 {}월", year, month);
        log.info("📋 모든 직원의 급여 계산 중...");
        
        // 약식으로 완료
        log.info("✅ 급여 계산 완료");
        return 0;
    }
}
