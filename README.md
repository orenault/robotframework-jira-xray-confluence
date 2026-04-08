# robotframework-jira-xray-confluence

Robot Framework library for Jira, Confluence and Xray (Cloud & Data Center).

## Key Feature: Hybrid Dynamic Keywords

This library dynamically exposes **600+ Robot Framework keywords** from underlying Python clients.

- no need to maintain hundreds of wrappers
- automatically adapts when client evolves
- very broad coverage

## Example

```robot
*** Settings ***
Library    robotframework_jira_xray_confluence.JiraXrayConfluence

*** Test Cases ***
Example
    ${count}=    Count Atlassian Keywords
    Log    ${count}
```

## License

MIT
