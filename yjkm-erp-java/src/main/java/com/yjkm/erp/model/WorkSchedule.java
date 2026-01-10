package com.yjkm.erp.model;

import jakarta.persistence.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.LocalTime;

@Entity
@Table(name = "work_schedules")
public class WorkSchedule {
    private static final Logger log = LoggerFactory.getLogger(WorkSchedule.class);

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "schedule_id")
    private Long scheduleId;

    @Column(name = "schedule_name", nullable = false)
    private String scheduleName;

    @Column(name = "start_time", nullable = false)
    private LocalTime startTime;

    @Column(name = "end_time", nullable = false)
    private LocalTime endTime;

    @Column(name = "break_minutes", nullable = false)
    private Integer breakMinutes;

    @Column(name = "is_default")
    private Boolean isDefault;

    // 생성자
    public WorkSchedule() {
    }

    public WorkSchedule(Long scheduleId, String scheduleName, LocalTime startTime, LocalTime endTime,
                        Integer breakMinutes, Boolean isDefault) {
        this.scheduleId = scheduleId;
        this.scheduleName = scheduleName;
        this.startTime = startTime;
        this.endTime = endTime;
        this.breakMinutes = breakMinutes;
        this.isDefault = isDefault;
    }

    // Getter/Setter
    public Long getScheduleId() { return scheduleId; }
    public void setScheduleId(Long scheduleId) { this.scheduleId = scheduleId; }

    public String getScheduleName() { return scheduleName; }
    public void setScheduleName(String scheduleName) { this.scheduleName = scheduleName; }

    public LocalTime getStartTime() { return startTime; }
    public void setStartTime(LocalTime startTime) { this.startTime = startTime; }

    public LocalTime getEndTime() { return endTime; }
    public void setEndTime(LocalTime endTime) { this.endTime = endTime; }

    public Integer getBreakMinutes() { return breakMinutes; }
    public void setBreakMinutes(Integer breakMinutes) { this.breakMinutes = breakMinutes; }

    public Boolean getIsDefault() { return isDefault; }
    public void setIsDefault(Boolean isDefault) { this.isDefault = isDefault; }
}
