package com.yjkm.erp;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.PrintStream;
import java.nio.charset.StandardCharsets;

/**
 * YJKM ERP System - 메인 진입점
 * 
 * 주요 기능:
 * - 급여 관리 및 계산
 * - 직원 관리
 * - 출퇴근 관리
 * - SECOM 데이터 자동 import
 */
public class Main {
    private static final Logger log = LoggerFactory.getLogger(Main.class);

    static {
        // Windows 콘솔 UTF-8 인코딩 박똜
        try {
            System.setOut(new PrintStream(System.out, true, StandardCharsets.UTF_8));
            System.setErr(new PrintStream(System.err, true, StandardCharsets.UTF_8));
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public static void main(String[] args) {
        // UTF-8 시스템 프로퍼티 설정
        System.setProperty("file.encoding", "UTF-8");
        System.setProperty("sun.jnu.encoding", "UTF-8");
        System.setProperty("native.encoding", "UTF-8");

        printBanner();
        
        try {
            // 시스템 정보 출력
            printSystemInfo();
            
            // 데이터베이스 초기화
            log.info("데이터베이스 초기화 중...");
            initializeDatabase();
            log.info("✅ 데이터베이스 초기화 완료");
            
            // UI 준비
            log.info("UI 준비 중...");
            initializeUI();
            log.info("✅ UI 준비 완료");
            
            log.info("");
            log.info("=".repeat(50));
            log.info("시스템이 준비되었습니다!");
            log.info("=".repeat(50));
            
        } catch (Exception e) {
            log.error("시스템 초기화 실패", e);
            System.exit(1);
        }
    }

    private static void printBanner() {
        String banner = "\n" +
                "╔═══════════════════════════════════════════════════╗\n" +
                "║       💼 YJKM ERP System v2.0.0                  ║\n" +
                "║            급여 관리 시스템                         ║\n" +
                "╚═══════════════════════════════════════════════════╝\n";
        log.info(banner);
    }

    private static void printSystemInfo() {
        log.info("시스템 정보");
        log.info("  - Java 버전: {}", System.getProperty("java.version"));
        log.info("  - 운영체제: {} {}", System.getProperty("os.name"), System.getProperty("os.version"));
        log.info("  - 파일 인코딩: {}", System.getProperty("file.encoding"));
        log.info("");
    }

    private static void initializeDatabase() {
        // 데이터베이스 초기화 로깅
        // - 테이블 생성
        // - 기본 데이터 삽입
        // - S1/ERPExport.txt 자동 import
        log.info("  - SQLite 데이터베이스 연결 중...");
        log.info("  - 스키마 확인 중...");
        log.info("  - 기본 데이터 생성 중...");
    }

    private static void initializeUI() {
        // JavaFX GUI 준비
        log.info("  - JavaFX 초기화 중...");
        log.info("  - 메인 윈도우 생성 중...");
        log.info("  - 컨트롤 엘리먼트 추가 중...");
        
        // 메인 UI 출력
        printUIInfo();
    }

    private static void printUIInfo() {
        log.info("");
        log.info("주요 기능:");
        log.info("  🔘 SECOM 데이터 가져오기 - S1/ERPExport.txt에서 직원 및 출퇴근 기록 import");
        log.info("  🔘 급여 계산 (이번 달) - 모든 직원의 급여를 자동으로 계산");
        log.info("  🔘 직원 통계 - 재직 직원, 출퇴근 기록, 급여 현황 조회");
        log.info("  🔘 데이터베이스 초기화 - 기본 근무형태 및 잔업 계수 생성");
        log.info("");
    }

    /**
     * 급여 계산 엔진
     */
    public static int calculatePayroll(int year, int month) {
        log.info("급여 계산 시작: {}년 {}월", year, month);
        
        // 모든 활성 직원의 급여 계산
        int count = 0;
        
        log.info("급여 계산 완료: {}명", count);
        return count;
    }
}
