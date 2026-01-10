package com.yjkm.erp.service;

import com.yjkm.erp.importer.SecomFileParser;
import com.yjkm.erp.model.Attendance;
import com.yjkm.erp.model.Employee;
import com.yjkm.erp.model.WorkSchedule;
import com.yjkm.erp.util.DatabaseUtil;
import jakarta.persistence.EntityManager;
import lombok.extern.slf4j.Slf4j;

import java.time.LocalDate;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * SECOM 데이터 Import 서비스
 */
@Slf4j
public class SecomImportService {

    private final SecomFileParser parser = new SecomFileParser();

    /**
     * S1/ERPExport.txt 파일을 데이터베이스에 Import
     */
    public ImportResult importFromFile(String filePath) {
        log.info("SECOM 파일 import 시작: {}", filePath);

        // 1. 파일 파싱
        SecomFileParser.SecomImportResult parseResult = parser.parseFile(filePath);

        if (!parseResult.isSuccess()) {
            log.error("파일 파싱 실패: {}", parseResult.getErrorMessage());
            return new ImportResult(false, parseResult.getErrorMessage(), 0, 0);
        }

        // 2. 데이터베이스에 저장
        return DatabaseUtil.executeInTransaction(em -> {
            // 근무형태 매핑 (이름 → WorkSchedule)
            Map<String, WorkSchedule> scheduleMap = loadWorkScheduleMap(em);

            // 직원 import
            int employeeCount = importEmployees(em, parseResult.getEmployees(), scheduleMap);

            // 출퇴근 기록 import
            int attendanceCount = importAttendances(em, parseResult.getAttendances());

            log.info("SECOM import 완료 - 직원: {}, 출퇴근: {}", employeeCount, attendanceCount);

            return new ImportResult(true, "성공", employeeCount, attendanceCount);
        });
    }

    /**
     * 근무형태 매핑 로드
     */
    private Map<String, WorkSchedule> loadWorkScheduleMap(EntityManager em) {
        List<WorkSchedule> schedules = em.createQuery(
                "SELECT w FROM WorkSchedule w", WorkSchedule.class).getResultList();

        Map<String, WorkSchedule> map = new HashMap<>();
        for (WorkSchedule schedule : schedules) {
            String name = schedule.getScheduleName();
            // "주간근무" 형태로 축약된 이름도 매칭
            String shortName = name.split("\\(")[0].trim();
            map.put(name, schedule);
            map.put(shortName, schedule);
        }

        return map;
    }

    /**
     * 직원 데이터 import
     */
    private int importEmployees(EntityManager em,
                                List<SecomFileParser.SecomEmployee> secomEmployees,
                                Map<String, WorkSchedule> scheduleMap) {
        int count = 0;

        for (SecomFileParser.SecomEmployee secomEmp : secomEmployees) {
            try {
                // 기존 직원 확인 (카드번호 기준)
                List<Employee> existing = em.createQuery(
                        "SELECT e FROM Employee e WHERE e.secomCardNumber = :cardNumber",
                        Employee.class)
                        .setParameter("cardNumber", secomEmp.getCardNumber())
                        .getResultList();

                if (existing.isEmpty()) {
                    // 신규 직원 생성
                    WorkSchedule schedule = findWorkSchedule(scheduleMap, secomEmp.getWorkScheduleName());

                    Employee employee = Employee.builder()
                            .empCode("EMP_" + secomEmp.getCardNumber())
                            .name(secomEmp.getName())
                            .department(secomEmp.getDepartment())
                            .position(secomEmp.getPosition())
                            .hireDate(secomEmp.getHireDate() != null ? secomEmp.getHireDate() : LocalDate.now())
                            .hourlyWage(10000)  // 기본 시급 (나중에 수정 필요)
                            .workSchedule(schedule)
                            .secomCardNumber(secomEmp.getCardNumber())
                            .build();

                    em.persist(employee);
                    count++;
                    log.debug("신규 직원 추가: {}", employee.getName());
                } else {
                    log.debug("기존 직원 건너뜀: {}", secomEmp.getName());
                }
            } catch (Exception e) {
                log.warn("직원 import 실패: {} - {}", secomEmp.getName(), e.getMessage());
            }
        }

        return count;
    }

    /**
     * 출퇴근 기록 import
     */
    private int importAttendances(EntityManager em,
                                  List<SecomFileParser.SecomAttendance> secomAttendances) {
        int count = 0;

        for (SecomFileParser.SecomAttendance secomAtt : secomAttendances) {
            try {
                // 직원 찾기
                List<Employee> employees = em.createQuery(
                        "SELECT e FROM Employee e WHERE e.secomCardNumber = :cardNumber",
                        Employee.class)
                        .setParameter("cardNumber", secomAtt.getCardNumber())
                        .getResultList();

                if (employees.isEmpty()) {
                    log.warn("직원을 찾을 수 없음: {}", secomAtt.getCardNumber());
                    continue;
                }

                Employee employee = employees.get(0);

                // 기존 출퇴근 기록 확인
                List<Attendance> existing = em.createQuery(
                        "SELECT a FROM Attendance a WHERE a.employee = :employee AND a.workDate = :date",
                        Attendance.class)
                        .setParameter("employee", employee)
                        .setParameter("date", secomAtt.getWorkDate())
                        .getResultList();

                if (existing.isEmpty()) {
                    // 신규 출퇴근 기록
                    Attendance attendance = Attendance.builder()
                            .employee(employee)
                            .workDate(secomAtt.getWorkDate())
                            .checkIn(secomAtt.getCheckIn())
                            .checkOut(secomAtt.getCheckOut())
                            .build();

                    // 자동 계산
                    attendance.updateOvertimeMinutes(employee.getWorkSchedule());
                    attendance.updateNightWorkMinutes(employee.getWorkSchedule());
                    attendance.determineWorkType(employee.getWorkSchedule());

                    em.persist(attendance);
                    count++;
                } else {
                    // 기존 기록 업데이트
                    Attendance attendance = existing.get(0);
                    if (secomAtt.getCheckIn() != null) {
                        attendance.setCheckIn(secomAtt.getCheckIn());
                    }
                    if (secomAtt.getCheckOut() != null) {
                        attendance.setCheckOut(secomAtt.getCheckOut());
                    }

                    attendance.updateOvertimeMinutes(employee.getWorkSchedule());
                    attendance.updateNightWorkMinutes(employee.getWorkSchedule());
                    attendance.determineWorkType(employee.getWorkSchedule());

                    em.merge(attendance);
                }
            } catch (Exception e) {
                log.warn("출퇴근 기록 import 실패: {} - {}", secomAtt.getCardNumber(), e.getMessage());
            }
        }

        return count;
    }

    /**
     * 근무형태 찾기 (매칭 로직)
     */
    private WorkSchedule findWorkSchedule(Map<String, WorkSchedule> scheduleMap, String scheduleName) {
        if (scheduleName == null || scheduleName.isEmpty()) {
            // 기본 근무형태 반환
            return scheduleMap.values().stream()
                    .filter(s -> s.getIsDefault() != null && s.getIsDefault())
                    .findFirst()
                    .orElse(scheduleMap.values().iterator().next());
        }

        // 정확한 이름으로 찾기
        WorkSchedule schedule = scheduleMap.get(scheduleName);
        if (schedule != null) {
            return schedule;
        }

        // 부분 매칭 (예: "주간" → "주간근무 (09:00~18:00)")
        for (Map.Entry<String, WorkSchedule> entry : scheduleMap.entrySet()) {
            if (entry.getKey().contains(scheduleName) || scheduleName.contains(entry.getKey())) {
                return entry.getValue();
            }
        }

        // 기본값 반환
        return scheduleMap.values().iterator().next();
    }

    /**
     * Import 결과
     */
    public record ImportResult(
            boolean success,
            String message,
            int employeeCount,
            int attendanceCount
    ) {}
}
