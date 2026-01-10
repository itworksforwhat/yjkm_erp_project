package com.yjkm.erp.service;

import lombok.extern.slf4j.Slf4j;

/**
 * SECOM 임포트 서비스 - 최소 버전 (향후 확장 예정)
 */
@Slf4j
public class SecomImportService {

    public record ImportResult(
            boolean success,
            int employeeCount,
            int attendanceCount,
            String message
    ) {}

    /**
     * 파일에서 SECOM 데이터를 임포트합니다.
     * 현재는 최소 버전으로, 실제 파싱은 비활성화되어 있습니다.
     */
    public ImportResult importFromFile(String filePath) {
        log.info("SECOM 임포트 요청 (파일: {})", filePath);
        log.info("SECOM 기능은 현재 비활성화 상태입니다. 추후 업데이트될 예정입니다.");

        return new ImportResult(
                false,
                0,
                0,
                "SECOM 기능은 현재 비활성화 상태입니다. 다음 버전에서 지원 예정입니다."
        );
    }
}
