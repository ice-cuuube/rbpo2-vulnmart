# VulnMart-Lab Security Dataset

## Назначение

Датасет содержит результаты статического и динамического анализа учебного комплекса VulnMart-Lab.

## Проекты

### Python

Flask-приложение с намеренно встроенными:

* SQL Injection;
* Stored XSS;
* Incorrect Authorization;
* Hard-coded Credentials.

### C++

Программа с:

* Buffer Overflow;
* Format String;
* OS Command Injection.

### JavaScript

Node.js/Express-приложение с:

* SQL Injection;
* XSS;
* OS Command Injection.

Для реализации SQLite в JavaScript используется sql.js.

## Структура

* `vulnerabilities.csv` — основной датасет;
* `vulnerabilities.json` — JSON-версия;
* `cwe_mapping.csv` — сопоставление CWE;
* `raw/sast/` — результаты SAST;
* `raw/dast/` — результаты DAST;
* `report/expert_assessment.md` — экспертная оценка;
* `report/sources.md` — источники.

## Инструменты

* Bandit;
* Cppcheck;
* ESLint;
* eslint-plugin-security;
* OWASP ZAP;
* GCC/G++;
* Node.js;
* sql.js;
* Flask.

## Область исследования

Все тесты проводились в локальной лабораторной среде на собственной виртуальной машине.

Внешние информационные источники использовались для классификации CWE, поиска реальных CVE и проверки CVSS.
