package com.yjkm.erp.model;

import jakarta.persistence.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.LocalDate;
import java.time.LocalTime;
import java.time.temporal.ChronoUnit;

@Entity
@Table(name = "attendance",
       uniqueConstraints = @UniqueConstraint(columnNames = {"employee_id", "work_date"}))
public class Attendance {
    private static final Logger log = LoggerFactory.getLogger(Attendance.class);

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "attendance_id")
    private Long attendanceId;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "employee_id", nullable = false)
    private Employee employee;

    @Column(name = "work_date", nullable = false)
    private LocalDate workDate;

    @Column(name = "check_in")
    private LocalTime checkIn;

    @Column(name = "check_out")
    private LocalTime checkOut;

    @Column(name = "overtime_minutes")
    private Integer overtimeMinutes;

    @Column(name = "night_work_minutes")
    private Integer nightWorkMinutes;

    @Column(name = "work_type", length = 20)
    private String workType;

    @Column(name = "is_holiday")
    private Boolean isHoliday;

    @Column(name = "holiday_rate")
    private Double holidayRate;

    @Column(name = "notes", columnDefinition = "TEXT")
    private String notes;

    @Column(name = "created_at")
    private LocalDate createdAt;

    @Column(name = "updated_at")
    private LocalDate updatedAt;

    // 생성자
    public Attendance() {
    }

    public Attendance(Long attendanceId, Employee employee, LocalDate workDate, LocalTime checkIn,
                      LocalTime checkOut, Integer overtimeMinutes, Integer nightWorkMinutes, String workType,
                      Boolean isHoliday, Double holidayRate, String notes, LocalDate createdAt, LocalDate updatedAt) {
        this.attendanceId = attendanceId;
        this.employee = employee;
        this.workDate = workDate;
        this.checkIn = checkIn;
        this.checkOut = checkOut;
        this.overtimeMinutes = overtimeMinutes;
        this.nightWorkMinutes = nightWorkMinutes;
        this.workType = workType;
        this.isHoliday = isHoliday;
        this.holidayRate = holidayRate;
        this.notes = notes;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
    }

    // Getter/Setter
    public Long getAttendanceId() { return attendanceId; }
    public void setAttendanceId(Long attendanceId) { this.attendanceId = attendanceId; }

    public Employee getEmployee() { return employee; }
    public void setEmployee(Employee employee) { this.employee = employee; }

    public LocalDate getWorkDate() { return workDate; }
    public void setWorkDate(LocalDate workDate) { this.workDate = workDate; }

    public LocalTime getCheckIn() { return checkIn; }
    public void setCheckIn(LocalTime checkIn) { this.checkIn = checkIn; }

    public LocalTime getCheckOut() { return checkOut; }
    public void setCheckOut(LocalTime checkOut) { this.checkOut = checkOut; }

    public Integer getOvertimeMinutes() { return overtimeMinutes; }
    public void setOvertimeMinutes(Integer overtimeMinutes) { this.overtimeMinutes = overtimeMinutes; }

    public Integer getNightWorkMinutes() { return nightWorkMinutes; }
    public void setNightWorkMinutes(Integer nightWorkMinutes) { this.nightWorkMinutes = nightWorkMinutes; }

    public String getWorkType() { return workType; }
    public void setWorkType(String workType) { this.workType = workType; }

    public Boolean getIsHoliday() { return isHoliday; }
    public void setIsHoliday(Boolean isHoliday) { this.isHoliday = isHoliday; }

    public Double getHolidayRate() { return holidayRate; }
    public void setHolidayRate(Double holidayRate) { this.holidayRate = holidayRate; }

    public String getNotes() { return notes; }
    public void setNotes(String notes) { this.notes = notes; }

    public LocalDate getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDate createdAt) { this.createdAt = createdAt; }

    public LocalDate getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(LocalDate updatedAt) { this.updatedAt = updatedAt; }

    // 메서드
    public long calculateTotalWorkMinutes() {
        if (checkIn == null || checkOut == null) {
            return 0;
        }

        long totalMinutes;
        if (checkOut.isAfter(checkIn)) {
            totalMinutes = ChronoUnit.MINUTES.between(checkIn, checkOut);
        } else {
            totalMinutes = ChronoUnit.MINUTES.between(checkIn, LocalTime.MAX) + 1
                    + ChronoUnit.MINUTES.between(LocalTime.MIN, checkOut);
        }

        return totalMinutes;
    }

    public long calculateRegularWorkMinutes(WorkSchedule schedule) {
        if (schedule == null) {
            return calculateTotalWorkMinutes();
        }

        long scheduledMinutes = schedule.calculateWorkingMinutes();
        long actualMinutes = calculateTotalWorkMinutes();

        return Math.min(scheduledMinutes, actualMinutes);
    }

    public void updateOvertimeMinutes(WorkSchedule schedule) {
        if (schedule == null || checkIn == null || checkOut == null) {
            overtimeMinutes = 0;
            return;
        }

        long scheduledMinutes = schedule.calculateWorkingMinutes();
        long actualMinutes = calculateTotalWorkMinutes();

        overtimeMinutes = (int) Math.max(0, actualMinutes - scheduledMinutes);
    }

    public void updateNightWorkMinutes(WorkSchedule schedule) {
        if (schedule == null || checkIn == null || checkOut == null) {
            nightWorkMinutes = 0;
            return;
        }

        LocalTime nightStart = LocalTime.of(22, 0);
        LocalTime nightEnd = LocalTime.of(6, 0);

        long nightMinutes = 0;

        if (!checkOut.isBefore(nightStart)) {
            LocalTime overlapStart = checkIn.isAfter(nightStart) ? checkIn : nightStart;
            LocalTime overlapEnd = checkOut;
            if (overlapEnd.isAfter(overlapStart)) {
                nightMinutes += ChronoUnit.MINUTES.between(overlapStart, overlapEnd);
            }
        }

        if (checkOut.isBefore(checkIn) || checkOut.isBefore(nightEnd)) {
            LocalTime overlapStart = LocalTime.MIN;
            LocalTime overlapEnd = checkOut.isBefore(nightEnd) ? checkOut : nightEnd;
            if (overlapEnd.isAfter(overlapStart)) {
                nightMinutes += ChronoUnit.MINUTES.between(overlapStart, overlapEnd);
            }
        }

        nightWorkMinutes = (int) nightMinutes;
    }

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
            workType = "지각/조턇";
        } else if (isLate) {
            workType = "지각";
        } else if (isEarlyLeave) {
            workType = "조턇";
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
