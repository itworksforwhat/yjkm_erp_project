package com.yjkm.erp.model;

import jakarta.persistence.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Entity
@Table(name = "overtime_rates")
public class OvertimeRate {
    private static final Logger log = LoggerFactory.getLogger(OvertimeRate.class);

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "rate_id")
    private Long rateId;

    @Column(name = "from_minutes", nullable = false)
    private Integer fromMinutes;

    @Column(name = "to_minutes")
    private Integer toMinutes;

    @Column(name = "multiplier", nullable = false)
    private Double multiplier;

    @Column(name = "description")
    private String description;

    @Column(name = "display_order")
    private Integer displayOrder;

    // 생성자
    public OvertimeRate() {
    }

    public OvertimeRate(Long rateId, Integer fromMinutes, Integer toMinutes, Double multiplier,
                        String description, Integer displayOrder) {
        this.rateId = rateId;
        this.fromMinutes = fromMinutes;
        this.toMinutes = toMinutes;
        this.multiplier = multiplier;
        this.description = description;
        this.displayOrder = displayOrder;
    }

    // Getter/Setter
    public Long getRateId() { return rateId; }
    public void setRateId(Long rateId) { this.rateId = rateId; }

    public Integer getFromMinutes() { return fromMinutes; }
    public void setFromMinutes(Integer fromMinutes) { this.fromMinutes = fromMinutes; }

    public Integer getToMinutes() { return toMinutes; }
    public void setToMinutes(Integer toMinutes) { this.toMinutes = toMinutes; }

    public Double getMultiplier() { return multiplier; }
    public void setMultiplier(Double multiplier) { this.multiplier = multiplier; }

    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }

    public Integer getDisplayOrder() { return displayOrder; }
    public void setDisplayOrder(Integer displayOrder) { this.displayOrder = displayOrder; }
}
