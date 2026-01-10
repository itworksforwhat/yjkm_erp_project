# YJKM ERP System

YJKM 급여 및 인사관리 ERP 시스템

> **주의**: 이 저장소는 현재 유지보수 중인 Java 기반 프로덕션 버전과 레거시 Python 버전을 포함합니다.

---

## 📦 프로젝트 구조

```
yjkm_erp_project/
├── yjkm-erp-java/        ← 🟢 현재 프로덕션 버전 (적극 유지보수)
│   ├── src/              Java 소스 코드
│   ├── pom.xml           Maven 설정
│   └── README.md          상세 Java 가이드
│
├── python/               ← 🔴 레거시 버전 (폐기됨, 참고용)
│   ├── docs/             가이드 및 문서
│   ├── src/              Python 소스 (이전 사용)
│   └── README.md          Python 버전 문서
│
├── S1/                   차세대 모듈 (개발 중)
├── docs/                 공유 문서
└── README.md             이 파일
```

---

## 🎯 주요 기능

### 🟢 Java 버전 (프로덕션)

**현재 운영 중인 ERP 시스템입니다.**

- ✅ 급여 관리 및 계산
- ✅ 인사 관리 (직원 정보, 조직도)
- ✅ 휴가 관리 및 승인
- ✅ 근무 일정 관리
- ✅ SECOM 통합 (보안 시스템)
- ✅ 다양한 데이터 포맷 지원 (Excel, CSV, TXT)
- ✅ 데이터베이스 자동 백업

자세한 내용은 [`yjkm-erp-java/README.md`](./yjkm-erp-java/README.md) 참조

### 🔴 Python 버전 (레거시)

**이전에 사용되던 Tkinter 기반 데스크탑 애플리케이션입니다.**
- 더 이상 유지보수되지 않음
- 참고 자료로만 보관됨
- 새로운 개발은 Java 버전으로 진행

자세한 내용은 [`python/README.md`](./python/README.md) 참조

---

## 🚀 빠른 시작

### Java 버전 설치 및 실행

```bash
# 저장소 클론
git clone https://github.com/itworksforwhat/yjkm_erp_project.git
cd yjkm_erp_project/yjkm-erp-java

# 빌드
mvn clean install

# 실행
java -jar target/yjkm-erp-java-1.0.jar
```

**더 상세한 가이드**: [Java 설치 가이드](./yjkm-erp-java/README.md#설치)

---

## 📚 문서

### 🟢 프로덕션 (Java)
- [Java README](./yjkm-erp-java/README.md) - 프로덕션 버전 상세 가이드
- [사용자 가이드 (한글)](./yjkm-erp-java/사용자_가이드.md) - 최종 사용자용 매뉴얼

### 🔴 레거시 (Python)
- [Python README](./python/README.md) - 폐기된 버전 (참고용)
- [가이드 문서](./python/GUIDE.md) - 구 버전 사용 설명서
- [트러블슈팅](./python/TROUBLESHOOTING.md) - 구 버전 문제 해결

---

## 🛠️ 기술 스택

### 프로덕션 (Java)
- **언어**: Java 11+
- **빌드**: Maven
- **데이터베이스**: SQLite / PostgreSQL
- **GUI**: JavaFX / Swing
- **프레임워크**: Spring Boot (선택사항)

### 레거시 (Python)
- **언어**: Python 3.8+
- **GUI**: Tkinter
- **데이터베이스**: SQLite
- **라이브러리**: Pandas, Openpyxl, PyODBC

---

## 🔄 마이그레이션 정보

Python 버전에서 Java 버전으로 마이그레이션하려면:

1. Java 버전 환경 설정
2. 기존 데이터베이스에서 데이터 내보내기 (CSV/Excel)
3. Java 버전으로 데이터 임포트
4. 사용자 교육 및 점진적 전환

자세한 마이그레이션 가이드는 [`MIGRATION.md`](./docs/MIGRATION.md)를 참조하세요.

---

## 📝 기여 방법

### 현재 상태

- **프로덕션 버전 (Java)**: 적극 유지보수 ✅
- **레거시 버전 (Python)**: 버그 수정만 수용 ❌

### 기여 규칙

1. 버그 수정은 항상 환영합니다
2. 새로운 기능은 Java 버전에만 추가해주세요
3. Pull Request 전에 [CONTRIBUTING.md](./CONTRIBUTING.md) 읽기

```bash
# 기여 프로세스
1. Fork the repository
2. Create feature branch (git checkout -b feature/amazing-feature)
3. Commit changes (git commit -m 'Add amazing feature')
4. Push to branch (git push origin feature/amazing-feature)
5. Open Pull Request
```

---

## 🐛 버그 신고

버그를 발견했다면:

1. [GitHub Issues](https://github.com/itworksforwhat/yjkm_erp_project/issues)에서 중복 확인
2. 명확한 제목과 설명으로 이슈 작성
3. 버전 정보와 재현 단계 포함

**제목 예시**:
```
[Java] Payroll calculation incorrect for overtime hours
[Python] GUI freezes when importing large Excel files
```

---

## 💾 데이터 백업

### 중요!

중요한 데이터가 포함되어 있으므로:

- ✅ 정기적인 백업 수행
- ✅ 데이터베이스 파일 별도 보관
- ✅ 프로덕션 환경에서는 자동 백업 설정

백업 방법은 각 버전의 README 참조

---

## 📞 지원

문제나 질문이 있으시면:

- 📧 이메일: support@yjkm.co.kr
- 🐛 버그 리포트: [GitHub Issues](https://github.com/itworksforwhat/yjkm_erp_project/issues)
- 💬 토론: [GitHub Discussions](https://github.com/itworksforwhat/yjkm_erp_project/discussions)

---

## 📋 라이선스

이 프로젝트는 YJKM 소유입니다. 자세한 내용은 [LICENSE](./LICENSE) 참조

---

## 📈 버전 히스토리

### v2.0+ (Java 버전)
- 현재 프로덕션 버전
- 정기적으로 업데이트됨

### v1.0 (Python 버전)
- 초기 프로토타입
- 2024년 폐기됨
- 참고 자료로만 보관

자세한 변경 이력은 [CHANGELOG.md](./CHANGELOG.md) 참조

---

**마지막 업데이트**: 2026년 1월 11일  
**유지보수**: YJKM 개발팀
