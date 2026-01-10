package com.yjkm.erp;

import com.yjkm.erp.db.DatabaseUtil;
import com.yjkm.erp.service.SecomImportService;
import com.yjkm.erp.ui.MainWindow;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.File;

public class Main {
    private static final Logger log = LoggerFactory.getLogger(Main.class);

    public static void main(String[] args) {
        try {
            log.info("=== YJKM ERP System 시작 ===");
            log.info("Java 버전: {}", System.getProperty("java.version"));
            log.info("작업 디렉토리: {}", new File(".").getAbsolutePath());

            // 데이터베이스 초기화
            DatabaseUtil.initializeDatabase();
            log.info("데이터베이스 초기화 완료");

            // UI 시작
            log.info("UI 시작");
            MainWindow window = new MainWindow();
            window.show();

            log.info("=== YJKM ERP System 실행 완료 ===");
        } catch (Exception e) {
            log.error("YJKM ERP System 시작 중 오류 발생", e);
            System.exit(1);
        }
    }
}
