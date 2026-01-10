package com.yjkm.erp;

import com.yjkm.erp.service.PayrollCalculator;
import com.yjkm.erp.service.SecomImportService;
import com.yjkm.erp.util.DatabaseUtil;
import javafx.application.Application;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.Scene;
import javafx.scene.control.*;
import javafx.scene.layout.*;
import javafx.stage.Stage;
import lombok.extern.slf4j.Slf4j;

import java.io.File;
import java.time.LocalDate;

/**
 * YJKM ERP System - Main Application
 * 급여관리 ERP 시스템 Java Edition
 */
@Slf4j
public class Main extends Application {

    private final SecomImportService secomService = new SecomImportService();
    private final PayrollCalculator payrollCalculator = new PayrollCalculator();

    @Override
    public void start(Stage primaryStage) {
        log.info("ERP 시스템 시작...");

        // UI 구성
        VBox root = new VBox(20);
        root.setPadding(new Insets(30));
        root.setAlignment(Pos.TOP_CENTER);
        root.setStyle("-fx-background-color: #2b2b2b;");

        // 타이틀
        Label title = new Label("💼 YJKM 급여관리 ERP v2.0");
        title.setStyle("-fx-font-size: 32px; -fx-font-weight: bold; -fx-text-fill: #ffffff;");

        Label subtitle = new Label("Java Edition - Powered by JavaFX & Hibernate");
        subtitle.setStyle("-fx-font-size: 16px; -fx-text-fill: #aaaaaa;");

        // 정보 표시
        TextArea infoArea = new TextArea();
        infoArea.setEditable(false);
        infoArea.setPrefHeight(200);
        infoArea.setStyle("-fx-font-family: 'Monospaced'; -fx-font-size: 13px;");

        // 버튼 그리드
        GridPane buttonGrid = new GridPane();
        buttonGrid.setHgap(15);
        buttonGrid.setVgap(15);
        buttonGrid.setAlignment(Pos.CENTER);

        // SECOM Import 버튼
        Button secomBtn = createStyledButton("📥 SECOM 데이터 가져오기", "#4CAF50");
        secomBtn.setOnAction(e -> {
            importSecomData(infoArea);
        });

        // 급여 계산 버튼
        Button payrollBtn = createStyledButton("💰 급여 계산 (이번 달)", "#2196F3");
        payrollBtn.setOnAction(e -> {
            calculatePayroll(infoArea);
        });

        // 직원 통계 버튼
        Button statsBtn = createStyledButton("👥 직원 통계", "#FF9800");
        statsBtn.setOnAction(e -> {
            showEmployeeStats(infoArea);
        });

        // 데이터베이스 초기화 버튼
        Button initBtn = createStyledButton("🔄 데이터베이스 초기화", "#F44336");
        initBtn.setOnAction(e -> {
            initializeDatabase(infoArea);
        });

        buttonGrid.add(secomBtn, 0, 0);
        buttonGrid.add(payrollBtn, 1, 0);
        buttonGrid.add(statsBtn, 0, 1);
        buttonGrid.add(initBtn, 1, 1);

        // 레이아웃 구성
        root.getChildren().addAll(title, subtitle, new Separator(), buttonGrid, infoArea);

        Scene scene = new Scene(root, 900, 700);
        primaryStage.setScene(scene);
        primaryStage.setTitle("YJKM ERP System");
        primaryStage.setOnCloseRequest(e -> {
            DatabaseUtil.closeEntityManagerFactory();
            log.info("ERP 시스템 종료");
        });
        primaryStage.show();

        // 시작 메시지
        infoArea.appendText("=== YJKM 급여관리 ERP 시스템 v2.0 ===\n");
        infoArea.appendText("Java Edition - Modern & Optimized\n\n");
        infoArea.appendText("기능:\n");
        infoArea.appendText("• SECOM 출퇴근 데이터 자동 import\n");
        infoArea.appendText("• 차등 잔업 수당 계산\n");
        infoArea.appendText("• 교대 스케줄 관리\n");
        infoArea.appendText("• Excel/CSV 일괄 등록\n");
        infoArea.appendText("• 4대보험 자동 계산\n\n");
        infoArea.appendText("준비 완료! 위 버튼을 클릭하여 시작하세요.\n");
    }

    private Button createStyledButton(String text, String color) {
        Button btn = new Button(text);
        btn.setPrefWidth(250);
        btn.setPrefHeight(60);
        btn.setStyle(String.format(
                "-fx-background-color: %s; -fx-text-fill: white; " +
                "-fx-font-size: 14px; -fx-font-weight: bold; " +
                "-fx-background-radius: 8px; -fx-cursor: hand;",
                color
        ));
        btn.setOnMouseEntered(e -> btn.setStyle(btn.getStyle() + "-fx-opacity: 0.8;"));
        btn.setOnMouseExited(e -> btn.setStyle(btn.getStyle() + "-fx-opacity: 1.0;"));
        return btn;
    }

    private void importSecomData(TextArea infoArea) {
        infoArea.appendText("\n[알림] SECOM 임포트 기능은 현재 비활성화되어 있습니다.\n");
        infoArea.appendText("다음 버전에서 지원 예정입니다.\n");
        log.info("SECOM 임포트 기능은 현재 비활성화 상태입니다.");
    }


    private void calculatePayroll(TextArea infoArea) {
        LocalDate now = LocalDate.now();
        int year = now.getYear();
        int month = now.getMonthValue();

        infoArea.appendText(String.format("\n[급여 계산] %d년 %d월...\n", year, month));

        try {
            int count = payrollCalculator.calculateMonthlyPayroll(year, month);
            infoArea.appendText(String.format("✅ 성공: %d명의 급여 계산 완료\n", count));
        } catch (Exception e) {
            log.error("급여 계산 실패", e);
            infoArea.appendText("❌ 오류: " + e.getMessage() + "\n");
        }
    }

    private void showEmployeeStats(TextArea infoArea) {
        infoArea.appendText("\n[직원 통계]\n");

        DatabaseUtil.executeInTransaction(em -> {
            long totalEmployees = em.createQuery(
                    "SELECT COUNT(e) FROM Employee e WHERE e.resignationDate IS NULL", Long.class)
                    .getSingleResult();

            long totalAttendances = em.createQuery(
                    "SELECT COUNT(a) FROM Attendance a", Long.class)
                    .getSingleResult();

            long totalPayrolls = em.createQuery(
                    "SELECT COUNT(p) FROM Payroll p", Long.class)
                    .getSingleResult();

            infoArea.appendText(String.format("• 재직 직원: %d명\n", totalEmployees));
            infoArea.appendText(String.format("• 출퇴근 기록: %d건\n", totalAttendances));
            infoArea.appendText(String.format("• 급여 기록: %d건\n", totalPayrolls));

            return null;
        });
    }

    private void initializeDatabase(TextArea infoArea) {
        infoArea.appendText("\n[데이터베이스 초기화] 시작...\n");

        try {
            DatabaseUtil.initializeDatabase();
            infoArea.appendText("✅ 데이터베이스 초기화 완료\n");
            infoArea.appendText("   • 기본 근무형태 4개 생성\n");
            infoArea.appendText("   • 기본 잔업 계수 3개 생성\n");
        } catch (Exception e) {
            log.error("데이터베이스 초기화 실패", e);
            infoArea.appendText("❌ 오류: " + e.getMessage() + "\n");
        }
    }

    @Override
    public void init() {
        log.info("애플리케이션 초기화 중...");

        try {
            // 데이터베이스 초기화
            DatabaseUtil.initializeDatabase();
            log.info("데이터베이스 초기화 완료");

            // SECOM 자동 임포트는 현재 비활성화
            // (추후 필요시 활성화)

        } catch (Exception e) {
            log.error("초기화 실패", e);
            e.printStackTrace();
        }
    }


    public static void main(String[] args) {
        log.info("=== YJKM ERP System v2.0 ===");
        log.info("Java Edition - Starting...");
        launch(args);
    }
}
