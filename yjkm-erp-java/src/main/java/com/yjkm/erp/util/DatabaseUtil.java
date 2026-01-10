package com.yjkm.erp.util;

import jakarta.persistence.EntityManager;
import jakarta.persistence.EntityManagerFactory;
import jakarta.persistence.Persistence;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * 데이터베이스 유틸리틸 클래스
 * EntityManager 관리 및 트랜잭션 처리
 */
public class DatabaseUtil {
    private static final Logger log = LoggerFactory.getLogger(DatabaseUtil.class);

    private static final String PERSISTENCE_UNIT_NAME = "yjkm-erp-pu";
    private static EntityManagerFactory entityManagerFactory;

    static {
        try {
            log.info("EntityManagerFactory 초기화 중...");
            entityManagerFactory = Persistence.createEntityManagerFactory(PERSISTENCE_UNIT_NAME);
            log.info("EntityManagerFactory 초기화 완료");
        } catch (Exception e) {
            log.error("EntityManagerFactory 초기화 실패", e);
            throw new RuntimeException("데이터베이스 초기화 실패", e);
        }
    }

    /**
     * EntityManager 생성
     */
    public static EntityManager getEntityManager() {
        if (entityManagerFactory == null || !entityManagerFactory.isOpen()) {
            throw new IllegalStateException("EntityManagerFactory가 닫혀있습니다");
        }
        return entityManagerFactory.createEntityManager();
    }

    /**
     * 트랜잭션 내에서 작업 실패
     */
    public static <T> T executeInTransaction(TransactionCallback<T> callback) {
        EntityManager em = getEntityManager();
        try {
            em.getTransaction().begin();
            T result = callback.execute(em);
            em.getTransaction().commit();
            return result;
        } catch (Exception e) {
            if (em.getTransaction().isActive()) {
                em.getTransaction().rollback();
            }
            log.error("트랜잭션 실패", e);
            throw new RuntimeException("데이터베이스 작업 실패", e);
        } finally {
            em.close();
        }
    }

    /**
     * 트랜잭션 내에서 작업 실패 (반환값 없음)
     */
    public static void executeInTransaction(VoidTransactionCallback callback) {
        executeInTransaction(em -> {
            callback.execute(em);
            return null;
        });
    }

    /**
     * EntityManagerFactory 종료
     */
    public static void closeEntityManagerFactory() {
        if (entityManagerFactory != null && entityManagerFactory.isOpen()) {
            log.info("EntityManagerFactory 종료 중...");
            entityManagerFactory.close();
            log.info("EntityManagerFactory 종료 완료");
        }
    }

    /**
     * 데이터베이스 초기화
     * 기본 데이터 설정
     */
    public static void initializeDatabase() {
        executeInTransaction(em -> {
            // 기본 근무형태 설정
            createDefaultWorkSchedules(em);

            // 기본 잡업 계수 설정
            createDefaultOvertimeRates(em);

            log.info("데이터베이스 초기화 완료");
            return null;
        });
    }

    private static void createDefaultWorkSchedules(EntityManager em) {
        // 기조 근무형태 확인
        long count = em.createQuery("SELECT COUNT(w) FROM WorkSchedule w", Long.class)
                .getSingleResult();

        if (count == 0) {
            log.info("기본 근무형태 생성 중...");

            // 주간근무
            com.yjkm.erp.model.WorkSchedule dayShift = new com.yjkm.erp.model.WorkSchedule();
            dayShift.setScheduleName("주간근무 (09:00~18:00)");
            dayShift.setStartTime(java.time.LocalTime.of(9, 0));
            dayShift.setEndTime(java.time.LocalTime.of(18, 0));
            dayShift.setBreakMinutes(60);
            dayShift.setIsDefault(true);
            em.persist(dayShift);

            // 야간근무
            com.yjkm.erp.model.WorkSchedule nightShift = new com.yjkm.erp.model.WorkSchedule();
            nightShift.setScheduleName("야간근무 (21:00~06:00)");
            nightShift.setStartTime(java.time.LocalTime.of(21, 0));
            nightShift.setEndTime(java.time.LocalTime.of(6, 0));
            nightShift.setBreakMinutes(60);
            em.persist(nightShift);

            // 2교대(주간)
            com.yjkm.erp.model.WorkSchedule twoShiftDay = new com.yjkm.erp.model.WorkSchedule();
            twoShiftDay.setScheduleName("2교대(주간) (06:00~18:00)");
            twoShiftDay.setStartTime(java.time.LocalTime.of(6, 0));
            twoShiftDay.setEndTime(java.time.LocalTime.of(18, 0));
            twoShiftDay.setBreakMinutes(60);
            em.persist(twoShiftDay);

            // 2교대(야간)
            com.yjkm.erp.model.WorkSchedule twoShiftNight = new com.yjkm.erp.model.WorkSchedule();
            twoShiftNight.setScheduleName("2교대(야간) (18:00~06:00)");
            twoShiftNight.setStartTime(java.time.LocalTime.of(18, 0));
            twoShiftNight.setEndTime(java.time.LocalTime.of(6, 0));
            twoShiftNight.setBreakMinutes(60);
            em.persist(twoShiftNight);

            log.info("기본 근무형태 4개 생성 완료");
        }
    }

    private static void createDefaultOvertimeRates(EntityManager em) {
        // 기조 잡업 계수 확인
        long count = em.createQuery("SELECT COUNT(o) FROM OvertimeRate o", Long.class)
                .getSingleResult();

        if (count == 0) {
            log.info("기본 잡업 계수 생성 중...");

            // 0~60분: 0.5배
            com.yjkm.erp.model.OvertimeRate rate1 = new com.yjkm.erp.model.OvertimeRate();
            rate1.setFromMinutes(0);
            rate1.setToMinutes(60);
            rate1.setMultiplier(0.5);
            rate1.setDescription("0~60분: 0.5배");
            rate1.setDisplayOrder(1);
            em.persist(rate1);

            // 60~120분: 1.0배
            com.yjkm.erp.model.OvertimeRate rate2 = new com.yjkm.erp.model.OvertimeRate();
            rate2.setFromMinutes(60);
            rate2.setToMinutes(120);
            rate2.setMultiplier(1.0);
            rate2.setDescription("60~120분: 1.0배");
            rate2.setDisplayOrder(2);
            em.persist(rate2);

            // 120분 이상: 2.0배
            com.yjkm.erp.model.OvertimeRate rate3 = new com.yjkm.erp.model.OvertimeRate();
            rate3.setFromMinutes(120);
            rate3.setToMinutes(null);  // 무제한
            rate3.setMultiplier(2.0);
            rate3.setDescription("120분 이상: 2.0배");
            rate3.setDisplayOrder(3);
            em.persist(rate3);

            log.info("기본 잡업 계수 3개 생성 완료");
        }
    }

    /**
     * 트랜잭션 콜백 인터페이스
     */
    @FunctionalInterface
    public interface TransactionCallback<T> {
        T execute(EntityManager em) throws Exception;
    }

    /**
     * Void 트랜잭션 콜백 인터페이스
     */
    @FunctionalInterface
    public interface VoidTransactionCallback {
        void execute(EntityManager em) throws Exception;
    }
}