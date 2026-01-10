package com.yjkm.erp.service;

import com.yjkm.erp.importer.SecomFileParser;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * SECOM 임포트 서비스 - 최소 버전
 */
public class SecomImportService {
    private static final Logger log = LoggerFactory.getLogger(SecomImportService.class);

    private final SecomFileParser secomFileParser;

    public SecomImportService() {
        this.secomFileParser = new SecomFileParser();
    }

    public void importFromSecom(String filePath) {
        log.info("SECOM 파일 임포트 시작: {}", filePath);

        try {
            SecomFileParser.SecomImportResult result = secomFileParser.parseFile(filePath);

            if (!result.isSuccess()) {
                log.warn("SECOM 임포트 실패: {}", result.getErrorMessage());
                return;
            }

            log.info("SECOM 임포트 완료");
        } catch (Exception e) {
            log.error("SECOM 임포트 중 오류 발생", e);
        }
    }
}
