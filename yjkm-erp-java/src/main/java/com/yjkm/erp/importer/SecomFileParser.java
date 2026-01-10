package com.yjkm.erp.importer;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * SECOM 파일 파서 - 최소 버전 (향후 확장 예정)
 */
public class SecomFileParser {
    private static final Logger log = LoggerFactory.getLogger(SecomFileParser.class);

    public static class SecomImportResult {
        private boolean success = false;
        private String errorMessage = "";

        public boolean isSuccess() {
            return success;
        }

        public void setSuccess(boolean success) {
            this.success = success;
        }

        public String getErrorMessage() {
            return errorMessage;
        }

        public void setErrorMessage(String errorMessage) {
            this.errorMessage = errorMessage;
        }
    }

    public SecomImportResult parseFile(String filePath) {
        log.info("SECOM 파일 파싱 요청: {}", filePath);

        SecomImportResult result = new SecomImportResult();
        result.setSuccess(false);
        result.setErrorMessage("SECOM 파서는 현재 비활성화 상태입니다.");

        log.info("SECOM 파일 파싱 완료 (비활성화 모드)");
        return result;
    }
}
