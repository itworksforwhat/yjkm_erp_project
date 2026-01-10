package com.yjkm.erp.model;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDate;

/**
 * 휴가 엔티티
 */
@Entity
@Table(name = "leaves")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Leave {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "leave_id")
    private Long leaveId;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "employee_id", nullable = false)
    private Employee employee;

    @Enumerated(EnumType.STRING)
    @Column(name = "leave_type", nullable = false, length = 20)
    private LeaveType leaveType;  // 휴가 유형

    @Column(name = "start_date", nullable = false)
    private LocalDate startDate;  // 시작일

    @Column(name = "end_date", nullable = false)
    private LocalDate endDate;  // 종료일

    @Column(name = "days")
    private Double days;  // 휴가일수 (0.5 = 반차)

    @Enumerated(EnumType.STRING)
    @Column(name = "status", length = 20)
    private LeaveStatus status;  // 상태 (대기/승인/거절)

    @Column(name = "reason", columnDefinition = "TEXT")
    private String reason;  // 신청사유

    @Column(name = "reject_reason", columnDefinition = "TEXT")
    private String rejectReason;  // 거절사유

    @Column(name = "applied_at")
    private LocalDate appliedAt;  // 신청일

    @Column(name = "approved_at")
    private LocalDate approvedAt;  // 승인일

    @Column(name = "approved_by", length = 100)
    private String approvedBy;  // 승인자

    /**
     * 휴가 승인
     */
    public void approve(String approver) {
        this.status = LeaveStatus.APPROVED;
        this.approvedAt = LocalDate.now();
        this.approvedBy = approver;
    }

    /**
     * 휴가 거절
     */
    public void reject(String reason) {
        this.status = LeaveStatus.REJECTED;
        this.rejectReason = reason;
    }

    @PrePersist
    protected void onCreate() {
        appliedAt = LocalDate.now();
        if (status == null) {
            status = LeaveStatus.PENDING;
        }
        if (days == null) {
            days = calculateDays();
        }
    }

    /**
     * 휴가일수 자동 계산
     */
    private Double calculateDays() {
        if (startDate == null || endDate == null) {
            return 0.0;
        }

        long daysBetween = java.time.temporal.ChronoUnit.DAYS.between(startDate, endDate) + 1;

        // 반차 처리
        if (leaveType == LeaveType.HALF_DAY) {
            return 0.5;
        }

        return (double) daysBetween;
    }

    /**
     * 휴가 유형 Enum
     */
    public enum LeaveType {
        ANNUAL("연차"),
        HALF_DAY("반차"),
        SICK("병가"),
        SPECIAL("특별휴가"),
        UNPAID("무급휴가");

        private final String description;

        LeaveType(String description) {
            this.description = description;
        }

        public String getDescription() {
            return description;
        }
    }

    /**
     * 휴가 상태 Enum
     */
    public enum LeaveStatus {
        PENDING("대기"),
        APPROVED("승인"),
        REJECTED("거절"),
        CANCELLED("취소");

        private final String description;

        LeaveStatus(String description) {
            this.description = description;
        }

        public String getDescription() {
            return description;
        }
    }
}
