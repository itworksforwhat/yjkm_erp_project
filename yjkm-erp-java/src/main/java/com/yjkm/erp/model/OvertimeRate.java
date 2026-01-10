package com.yjkm.erp.model;

import jakarta.persistence.*;
import lombok.*;

/**
 * 잔업 수당 계수 엔티티
 */
@Entity
@Table(name = "overtime_rates")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class OvertimeRate {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "rate_id")
    private Long rateId;

    @Column(name = "from_minutes", nullable = false)
    private Integer fromMinutes;  // 시작 분 (예: 0, 60, 120)

    @Column(name = "to_minutes")
    private Integer toMinutes;  // 종료 분 (null이면 무제한)

    @Column(name = "multiplier", nullable = false)
    private Double multiplier;  // 배율 (예: 0.5, 1.0, 1.5, 2.0)

    @Column(name = "description", length = 200)
    private String description;  // 설명

    @Column(name = "display_order")
    private Integer displayOrder;  // 표시 순서

    /**
     * 특정 잔업시간(분)이 이 구간에 속하는지 확인
     */
    public boolean isInRange(int overtimeMinutes) {
        if (toMinutes == null) {
            // 무제한 구간
            return overtimeMinutes >= fromMinutes;
        } else {
            return overtimeMinutes >= fromMinutes && overtimeMinutes < toMinutes;
        }
    }

    /**
     * 이 구간에서 적용 가능한 시간(분) 계산
     */
    public int getApplicableMinutes(int overtimeMinutes) {
        if (!isInRange(overtimeMinutes)) {
            return 0;
        }

        int start = Math.max(overtimeMinutes, fromMinutes);
        int end = toMinutes != null ? Math.min(overtimeMinutes, toMinutes) : overtimeMinutes;

        return Math.max(0, end - start);
    }

    /**
     * 구간 설명 자동 생성
     */
    public String getAutoDescription() {
        if (toMinutes == null) {
            return String.format("%d분 이상 (배율: %.1f)", fromMinutes, multiplier);
        } else {
            return String.format("%d~%d분 (배율: %.1f)", fromMinutes, toMinutes, multiplier);
        }
    }

    @PrePersist
    @PreUpdate
    protected void onSave() {
        if (description == null || description.isEmpty()) {
            description = getAutoDescription();
        }
    }
}
