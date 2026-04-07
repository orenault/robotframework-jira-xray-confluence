*** Settings ***
Library    robotframework_jira_xray_confluence.JiraXrayConfluence

*** Test Cases ***
Basic Unified Example
    Connect To Xray Cloud    ${XRAY_CLIENT_ID}    ${XRAY_CLIENT_SECRET}
    ${tests}=    Get Tests With Test Plan    HHELIA-10
    Log To Console    ${tests}
