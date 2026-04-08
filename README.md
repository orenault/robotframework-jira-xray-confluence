# robotframework-jira-xray-confluence

## 🚀 Overview

Unified Robot Framework library for Jira, Confluence and Xray (Cloud & Data Center).

---

## 🎯 Problem

Typical RF setups require:

- multiple libraries
- manual wrappers
- duplicated code
- incomplete Xray Cloud support

---

## 💡 Solution

Single unified library with:

- dynamic keyword exposure
- multi-system support
- session management
- Xray Cloud integration

---

## 💥 CORE FEATURE: Hybrid Dynamic Keywords (600+)

This library dynamically exposes 600+ keywords.

### 🔧 How it works

- introspects Python clients
- maps public methods → RF keywords
- injects them dynamically

### 🎯 Benefits

- no wrapper maintenance
- automatic updates
- massive coverage

---

## ⚡ Installation

```bash
pip install robotframework-jira-xray-confluence
```

---

## 🧪 Example

```robot
*** Settings ***
Library    robotframework_jira_xray_confluence.JiraXrayConfluence

*** Test Cases ***
Dynamic Keywords
    ${count}=    Count Atlassian Keywords
    Log To Console    ${count}
```

---

## 🔌 Connection Example

```robot
Connect To Xray Cloud    ${CLIENT_ID}    ${CLIENT_SECRET}
${tests}=    Get Tests With Test Plan    DEMO-123
```

---

## 🧱 Architecture

```
Robot Framework
   ↓
Dynamic Wrapper
   ↓
Python Clients
   ↓
Atlassian APIs
```

---

## 📊 Use Cases

- end-to-end automation
- CI/CD integration
- test orchestration
- reporting pipelines

---

## 🔐 Notes

- supports Cloud + DC
- minimal maintenance design

---

## 📄 License

MIT
