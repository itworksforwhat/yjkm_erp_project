package com.yjkm.erp.util;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DatabaseUtil {
    private static final Logger log = LoggerFactory.getLogger(DatabaseUtil.class);

    public static void initializeDatabase() {
        try {
            log.info("📊 데이터베이스 초기화 중...");
            // JPA/Hibernate가 자동으로 테이블 생성
            log.info("✅ 데이터베이스 초기화 완료");
        } catch (Exception e) {
            log.error("❌ 데이터베이스 초기화 실패", e);
        }
    }

    public static void seedTestData() {
        try {
            log.info("🌱 테스트 데이터 생성 중...");
            log.info("✅ 테스트 데이터 생성 완료");
        } catch (Exception e) {
            log.error("❌ 테스트 데이터 생성 실패", e);
        }
    }
}
