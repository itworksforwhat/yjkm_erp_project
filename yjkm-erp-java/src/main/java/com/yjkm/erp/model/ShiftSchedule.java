package com.yjkm.erp.model;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDate;

/**
 * 교대 스케줄 엔티티
 * 2교대제 주간/야간 로테이션 관리
 */
@Entity
@Table(name = "shift_schedules",
       uniqueConstraints = @UniqueConstraint(columnNames = {"employee_id", "start_date"}))
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ShiftSchedule {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "schedule_id")
    private Long scheduleId;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "employee_id", nullable = false)
    private Employee employee;

    @Enumerated(EnumType.STRING)
    @Column(name = "shift_type", nullable = false, length = 20)
    private ShiftType shiftType;  // 교대 유형 (주간/야간)

    @Enumerated(EnumType.STRING)
    @Column(name = "rotation_pattern", length = 20)
    private RotationPattern rotationPattern;  // 로테이션 패턴

    @Column(name = "start_date", nullable = false)
    private LocalDate startDate;  // 시작일

    @Column(name = "end_date")
    private LocalDate endDate;  // 종료일 (null이면 계속)

    @Column(name = "rotation_weeks")
    private Integer rotationWeeks;  // 로테이션 주기 (주 단위, 기본: 2주)

    @Column(name = "notes", columnDefinition = "TEXT")
    private String notes;  // 비고

    @Column(name = "created_at")
    private LocalDate createdAt;

    /**
     * 특정 날짜의 교대 유형 계산
     */
    public ShiftType getShiftTypeForDate(LocalDate date) {
        if (date.isBefore(startDate) || (endDate != null && date.isAfter(endDate))) {
            return null;
        }

        if (rotationPattern == RotationPattern.FIXED) {
            // 고정 교대
            return shiftType;
        }

        // 로테이션 교대
        long weeksSinceStart = java.time.temporal.ChronoUnit.WEEKS.between(startDate, date);
        int rotationCycle = rotationWeeks != null ? rotationWeeks : 2;

        int cyclePosition = (int) (weeksSinceStart / rotationCycle) % 2;

        if (cyclePosition == 0) {
            return shiftType;
        } else {
            // 로테이션: 주간 ↔ 야간 교체
            return shiftType == ShiftType.DAY ? ShiftType.NIGHT : ShiftType.DAY;
        }
    }

    /**
     * 특정 날짜가 이 스케줄에 포함되는지 확인
     */
    public boolean isActiveOn(LocalDate date) {
        if (date.isBefore(startDate)) {
            return false;
        }
        return endDate == null || !date.isAfter(endDate);
    }

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDate.now();
        if (rotationWeeks == null) {
            rotationWeeks = 2;  // 기본: 2주 로테이션
        }
        if (rotationPattern == null) {
            rotationPattern = RotationPattern.ROTATING;
        }
    }

    /**
     * 교대 유형 Enum
     */
    public enum ShiftType {
        DAY("주간"),
        NIGHT("야간"),
        TWO_SHIFT_DAY("2교대(주간)"),
        TWO_SHIFT_NIGHT("2교대(야간)");

        private final String description;

        ShiftType(String description) {
            this.description = description;
        }

        public String getDescription() {
            return description;
        }
    }

    /**
     * 로테이션 패턴 Enum
     */
    public enum RotationPattern {
        FIXED("고정"),
        ROTATING("로테이션"),
        WEEKLY("주간 로테이션"),
        BIWEEKLY("격주 로테이션");

        private final String description;

        RotationPattern(String description) {
            this.description = description;
        }

        public String getDescription() {
            return description;
        }
    }
}
