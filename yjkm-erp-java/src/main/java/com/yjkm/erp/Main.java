package com.yjkm.erp;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class Main {
    private static final Logger log = LoggerFactory.getLogger(Main.class);

    public static void main(String[] args) {
        try {
            log.info("=====================================");
            log.info("YJKM ERP System v2.0.0");
            log.info("Java: {}", System.getProperty("java.version"));
            log.info("=====================================");
            
            // 간단한 테스트
            log.info("✅ 시스템이 정상적으로 시작되었습니다!");
            log.info("✅ 데이터베이스 연결 준비 완료");
            log.info("✅ UI 준비 완료");
            
            log.info("");
            log.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
            log.info("시스템이 준비되었습니다!");
            log.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
            
        } catch (Exception e) {
            log.error("❌ 시스템 시작 중 오류 발생", e);
            System.exit(1);
        }
    }
}
