package com.yjkm.erp.importer;

import com.yjkm.erp.model.Attendance;
import com.yjkm.erp.model.Employee;
import com.yjkm.erp.model.WorkSchedule;
import lombok.Data;
import lombok.extern.slf4j.Slf4j;

import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.InputStreamReader;
import java.nio.charset.Charset;
import java.time.LocalDate;
import java.time.LocalTime;
import java.time.format.DateTimeFormatter;
import java.util.*;

/**
 * SECOM ERPExport.txt 파일 파서
 * S1 폴더의 출퇴근 데이터를 파싱하여 Employee와 Attendance 생성
 */
@Slf4j
public class SecomFileParser {

    private static final DateTimeFormatter DATE_FORMATTER = DateTimeFormatter.ofPattern("yyyyMMdd");
    private static final DateTimeFormatter TIME_FORMATTER = DateTimeFormatter.ofPattern("HHmmss");

    /**
     * S1/ERPExport.txt 파일 파싱
     */
    public SecomImportResult parseFile(String filePath) {
        SecomImportResult result = new SecomImportResult();
        Map<String, SecomEmployee> employeeMap = new HashMap<>();
        List<SecomAttendance> attendances = new ArrayList<>();

        try (BufferedReader reader = new BufferedReader(
                new InputStreamReader(new FileInputStream(filePath), Charset.forName("EUC-KR")))) {

            String line;
            int lineNumber = 0;

            while ((line = reader.readLine()) != null) {
                lineNumber++;
                try {
                    SecomRecord record = parseLine(line);
                    if (record != null) {
                        // 직원 정보 수집
                        String cardNumber = record.getCardNumber();
                        if (!employeeMap.containsKey(cardNumber)) {
                            SecomEmployee emp = new SecomEmployee();
                            emp.setCardNumber(cardNumber);
                            emp.setName(record.getName());
                            emp.setDepartment(record.getDepartment());
                            emp.setPosition(record.getPosition());
                            emp.setWorkScheduleName(record.getWorkScheduleName());
                            emp.setHireDate(record.getHireDate());
                            employeeMap.put(cardNumber, emp);
                        }

                        // 출퇴근 기록 수집
                        SecomAttendance attendance = new SecomAttendance();
                        attendance.setCardNumber(cardNumber);
                        attendance.setWorkDate(record.getWorkDate());
                        attendance.setTime(record.getTime());
                        attendance.setCheckType(record.getCheckType());
                        attendances.add(attendance);
                    }
                } catch (Exception e) {
                    log.warn("라인 {} 파싱 실패: {}", lineNumber, e.getMessage());
                    result.addError(lineNumber, line, e.getMessage());
                }
            }

            result.setEmployees(new ArrayList<>(employeeMap.values()));
            result.setAttendances(groupAttendances(attendances));
            result.setSuccess(true);

            log.info("SECOM 파일 파싱 완료 - 직원: {}, 출퇴근 기록: {}",
                    result.getEmployees().size(), result.getAttendances().size());

        } catch (Exception e) {
            log.error("SECOM 파일 읽기 실패: {}", filePath, e);
            result.setSuccess(false);
            result.setErrorMessage(e.getMessage());
        }

        return result;
    }

    /**
     * 한 라인 파싱
     * 포맷: 날짜(8) | 시간(6) | 카드번호 | 이름 | 구분(1/4) | 부서 | 직급 | ... | 근무형태 | ... | 입사일
     */
    private SecomRecord parseLine(String line) {
        String[] fields = line.split("\t");

        if (fields.length < 14) {
            log.warn("필드 개수 부족: {}", fields.length);
            return null;
        }

        SecomRecord record = new SecomRecord();

        try {
            // 날짜 파싱 (필드 0)
            record.setWorkDate(LocalDate.parse(fields[0].trim(), DATE_FORMATTER));

            // 시간 파싱 (필드 1)
            record.setTime(LocalTime.parse(fields[1].trim(), TIME_FORMATTER));

            // 카드번호 (필드 2)
            record.setCardNumber(fields[2].trim());

            // 이름 (필드 3)
            record.setName(fields[3].trim());

            // 출퇴근 구분 (필드 4: 1=출근, 4=퇴근)
            String checkType = fields[4].trim();
            record.setCheckType("1".equals(checkType) ? "IN" : "OUT");

            // 부서 (필드 5)
            record.setDepartment(fields[5].trim());

            // 직급 (필드 6)
            record.setPosition(fields[6].trim());

            // 근무형태 (필드 9)
            record.setWorkScheduleName(fields[9].trim());

            // 입사일 (필드 13)
            if (fields.length > 13 && !fields[13].trim().isEmpty()) {
                record.setHireDate(LocalDate.parse(fields[13].trim(), DATE_FORMATTER));
            }

        } catch (Exception e) {
            log.warn("레코드 파싱 실패: {}", e.getMessage());
            return null;
        }

        return record;
    }

    /**
     * 출퇴근 기록 그룹핑 (같은 날짜별로)
     */
    private List<SecomAttendance> groupAttendances(List<SecomAttendance> records) {
        Map<String, SecomAttendance> grouped = new HashMap<>();

        for (SecomAttendance record : records) {
            String key = record.getCardNumber() + "_" + record.getWorkDate();

            if (!grouped.containsKey(key)) {
                grouped.put(key, record);
            } else {
                SecomAttendance existing = grouped.get(key);
                if ("IN".equals(record.getCheckType())) {
                    existing.setCheckIn(record.getTime());
                } else {
                    existing.setCheckOut(record.getTime());
                }
            }
        }

        return new ArrayList<>(grouped.values());
    }

    /**
     * SECOM 레코드 (한 라인)
     */
    @Data
    private static class SecomRecord {
        private LocalDate workDate;
        private LocalTime time;
        private String cardNumber;
        private String name;
        private String checkType;  // IN/OUT
        private String department;
        private String position;
        private String workScheduleName;
        private LocalDate hireDate;
    }

    /**
     * SECOM 직원 정보
     */
    @Data
    public static class SecomEmployee {
        private String cardNumber;
        private String name;
        private String department;
        private String position;
        private String workScheduleName;
        private LocalDate hireDate;
    }

    /**
     * SECOM 출퇴근 기록
     */
    @Data
    public static class SecomAttendance {
        private String cardNumber;
        private LocalDate workDate;
        private LocalTime time;
        private String checkType;  // IN/OUT
        private LocalTime checkIn;
        private LocalTime checkOut;
    }

    /**
     * Import 결과
     */
    @Data
    public static class SecomImportResult {
        private boolean success;
        private String errorMessage;
        private List<SecomEmployee> employees = new ArrayList<>();
        private List<SecomAttendance> attendances = new ArrayList<>();
        private List<ImportError> errors = new ArrayList<>();

        public void addError(int lineNumber, String line, String message) {
            errors.add(new ImportError(lineNumber, line, message));
        }
    }

    /**
     * Import 오류
     */
    @Data
    @lombok.AllArgsConstructor
    public static class ImportError {
        private int lineNumber;
        private String line;
        private String message;
    }
}
