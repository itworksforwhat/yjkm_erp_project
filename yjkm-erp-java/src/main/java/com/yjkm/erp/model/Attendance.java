package com.yjkm.erp.model;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDate;
import java.time.LocalTime;
import java.time.temporal.ChronoUnit;
import lombok.extern.slf4j.Slf4j;

@Slf4j

/**
 * 근태 엔티티
 */
@Entity
@Table(name = "attendance",
       uniqueConstraints = @UniqueConstraint(columnNames = {"employee_id", "work_date"}))
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Attendance {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "attendance_id")
    private Long attendanceId;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "employee_id", nullable = false)
    private Employee employee;

    @Column(name = "work_date", nullable = false)
    private LocalDate workDate;  // 근무일자

    @Column(name = "check_in")
    private LocalTime checkIn;  // 출근시간

    @Column(name = "check_out")
    private LocalTime checkOut;  // 퇴근시간

    @Column(name = "overtime_minutes")
    private Integer overtimeMinutes;  // 잔업시간 (분)

    @Column(name = "night_work_minutes")
    private Integer nightWorkMinutes;  // 야간근무시간 (분)

    @Column(name = "work_type", length = 20)
    private String workType;  // 근무유형 (정상/지각/조퇴/결근)

    @Column(name = "is_holiday")
    private Boolean isHoliday;  // 휴일근무 여부

    @Column(name = "holiday_rate")
    private Double holidayRate;  // 휴일수당 배율

    @Column(name = "notes", columnDefinition = "TEXT")
    private String notes;  // 비고

    @Column(name = "created_at")
    private LocalDate createdAt;

    @Column(name = "updated_at")
    private LocalDate updatedAt;

    /**
     * 총 근무시간 계산 (분)
     */
    public long calculateTotalWorkMinutes() {
        if (checkIn == null || checkOut == null) {
            return 0;
        }

        long totalMinutes;
        if (checkOut.isAfter(checkIn)) {
            totalMinutes = ChronoUnit.MINUTES.between(checkIn, checkOut);
        } else {
            // 날짜 넘김
            totalMinutes = ChronoUnit.MINUTES.between(checkIn, LocalTime.MAX) + 1
                    + ChronoUnit.MINUTES.between(LocalTime.MIN, checkOut);
        }

        return totalMinutes;
    }

    /**
     * 정상 근무시간 계산 (분)
     */
    public long calculateRegularWorkMinutes(WorkSchedule schedule) {
        if (schedule == null) {
            return calculateTotalWorkMinutes();
        }

        long scheduledMinutes = schedule.calculateWorkingMinutes();
        long actualMinutes = calculateTotalWorkMinutes();

        return Math.min(scheduledMinutes, actualMinutes);
    }

    /**
     * 잔업 시간 자동 계산 및 업데이트
     */
    public void updateOvertimeMinutes(WorkSchedule schedule) {
        if (schedule == null || checkIn == null || checkOut == null) {
            overtimeMinutes = 0;
            return;
        }

        long scheduledMinutes = schedule.calculateWorkingMinutes();
        long actualMinutes = calculateTotalWorkMinutes();

        overtimeMinutes = (int) Math.max(0, actualMinutes - scheduledMinutes);
    }

    /**
     * 야간근무 시간 자동 계산 및 업데이트
     */
    public void updateNightWorkMinutes(WorkSchedule schedule) {
        if (schedule == null || checkIn == null || checkOut == null) {
            nightWorkMinutes = 0;
            return;
        }

        // 근무 시간대와 야간 시간대 (22:00~06:00)의 겹치는 부분 계산
        LocalTime nightStart = schedule.getNightStart();  // 22:00
        LocalTime nightEnd = schedule.getNightEnd();      // 06:00

        long nightMinutes = 0;

        // Case 1: 저녁 야간 (22:00 ~ 자정)
        if (!checkOut.isBefore(nightStart)) {
            LocalTime overlapStart = checkIn.isAfter(nightStart) ? checkIn : nightStart;
            LocalTime overlapEnd = checkOut;
            if (overlapEnd.isAfter(overlapStart)) {
                nightMinutes += ChronoUnit.MINUTES.between(overlapStart, overlapEnd);
            }
        }

        // Case 2: 새벽 야간 (자정 ~ 06:00)
        if (checkOut.isBefore(checkIn) || checkOut.isBefore(nightEnd)) {
            LocalTime overlapStart = LocalTime.MIN;
            LocalTime overlapEnd = checkOut.isBefore(nightEnd) ? checkOut : nightEnd;
            if (overlapEnd.isAfter(overlapStart)) {
                nightMinutes += ChronoUnit.MINUTES.between(overlapStart, overlapEnd);
            }
        }

        nightWorkMinutes = (int) nightMinutes;
    }

    /**
     * 근무 유형 자동 판단
     */
    public void determineWorkType(WorkSchedule schedule) {
        if (checkIn == null || checkOut == null) {
            workType = "결근";
            return;
        }

        if (schedule == null) {
            workType = "정상";
            return;
        }

        boolean isLate = checkIn.isAfter(schedule.getStartTime().plusMinutes(10));
        boolean isEarlyLeave = checkOut.isBefore(schedule.getEndTime().minusMinutes(10));

        if (isLate && isEarlyLeave) {
            workType = "지각/조퇴";
        } else if (isLate) {
            workType = "지각";
        } else if (isEarlyLeave) {
            workType = "조퇴";
        } else {
            workType = "정상";
        }
    }

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDate.now();
        updatedAt = LocalDate.now();
        if (isHoliday == null) {
            isHoliday = false;
        }
        if (holidayRate == null) {
            holidayRate = 1.5;
        }
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDate.now();
    }
}
