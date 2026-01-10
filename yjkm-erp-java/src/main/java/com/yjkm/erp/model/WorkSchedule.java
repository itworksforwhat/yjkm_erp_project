package com.yjkm.erp.model;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalTime;
import java.time.temporal.ChronoUnit;
import lombok.extern.slf4j.Slf4j;

@Slf4j
/**
 * 근무형태 엔티티
 */
@Entity
@Table(name = "work_schedules")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class WorkSchedule {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "schedule_id")
    private Long scheduleId;

    @Column(name = "schedule_name", nullable = false, unique = true, length = 100)
    private String scheduleName;  // 근무형태 이름 (예: "주간근무 (09:00~18:00)")

    @Column(name = "start_time", nullable = false)
    private LocalTime startTime;  // 시작시간

    @Column(name = "end_time", nullable = false)
    private LocalTime endTime;  // 종료시간

    @Column(name = "break_minutes")
    private Integer breakMinutes;  // 휴게시간 (분)

    @Column(name = "night_start")
    private LocalTime nightStart;  // 야간시작시간 (기본: 22:00)

    @Column(name = "night_end")
    private LocalTime nightEnd;  // 야간종료시간 (기본: 06:00)

    @Column(name = "night_rate")
    private Double nightRate;  // 야간수당 배율 (기본: 1.5)

    @Column(name = "is_default")
    private Boolean isDefault;  // 기본 근무형태 여부

    @Column(name = "notes", columnDefinition = "TEXT")
    private String notes;  // 비고

    /**
     * 실 근무시간 계산 (분)
     */
    public long calculateWorkingMinutes() {
        long totalMinutes;

        if (endTime.isAfter(startTime)) {
            // 같은 날 (예: 09:00 ~ 18:00)
            totalMinutes = ChronoUnit.MINUTES.between(startTime, endTime);
        } else {
            // 날짜 넘김 (예: 22:00 ~ 06:00)
            totalMinutes = ChronoUnit.MINUTES.between(startTime, LocalTime.MAX) + 1
                    + ChronoUnit.MINUTES.between(LocalTime.MIN, endTime);
        }

        // 휴게시간 제외
        if (breakMinutes != null && breakMinutes > 0) {
            totalMinutes -= breakMinutes;
        }

        return totalMinutes;
    }

    /**
     * 실 근무시간 계산 (시간)
     */
    public double calculateWorkingHours() {
        return calculateWorkingMinutes() / 60.0;
    }

    /**
     * 야간근무 시간 계산 (분)
     */
    public long calculateNightMinutes() {
        if (nightStart == null || nightEnd == null) {
            return 0;
        }

        LocalTime workStart = startTime;
        LocalTime workEnd = endTime;
        LocalTime nightS = nightStart;  // 기본: 22:00
        LocalTime nightE = nightEnd;    // 기본: 06:00

        // 야간시간대와 근무시간의 겹치는 부분 계산
        long nightMinutes = 0;

        // Case 1: 야간 시작 ~ 자정
        if (workStart.isBefore(LocalTime.MAX) && workEnd.isAfter(nightS)) {
            LocalTime overlapStart = workStart.isAfter(nightS) ? workStart : nightS;
            LocalTime overlapEnd = workEnd.isBefore(LocalTime.MAX) ? workEnd : LocalTime.MAX;
            if (overlapEnd.isAfter(overlapStart)) {
                nightMinutes += ChronoUnit.MINUTES.between(overlapStart, overlapEnd);
            }
        }

        // Case 2: 자정 ~ 야간 종료
        if (workEnd.isBefore(workStart)) {  // 날짜 넘김
            LocalTime overlapStart = LocalTime.MIN;
            LocalTime overlapEnd = workEnd.isBefore(nightE) ? workEnd : nightE;
            if (overlapEnd.isAfter(overlapStart)) {
                nightMinutes += ChronoUnit.MINUTES.between(overlapStart, overlapEnd);
            }
        }

        return nightMinutes;
    }

    /**
     * 야간근무 시간 계산 (시간)
     */
    public double calculateNightHours() {
        return calculateNightMinutes() / 60.0;
    }

    @PrePersist
    @PreUpdate
    protected void setDefaults() {
        if (breakMinutes == null) {
            breakMinutes = 60;  // 기본 휴게시간: 60분
        }
        if (nightStart == null) {
            nightStart = LocalTime.of(22, 0);  // 기본 야간시작: 22:00
        }
        if (nightEnd == null) {
            nightEnd = LocalTime.of(6, 0);  // 기본 야간종료: 06:00
        }
        if (nightRate == null) {
            nightRate = 1.5;  // 기본 야간수당 배율: 1.5
        }
        if (isDefault == null) {
            isDefault = false;
        }
    }
}
