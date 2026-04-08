# robotframework-jira-xray-confluence

Robot Framework library for Jira, Confluence and Xray (Cloud & Data Center).

## Why this package exists

Teams using Robot Framework often end up with several disconnected approaches:

- one library for Jira
- another for Confluence
- a partial wrapper for Xray Server/DC
- custom scripts for Xray Cloud GraphQL
- manual code to map Jira keys to Xray internal IDs

This package unifies those needs into a single Robot Framework library.

## What this library covers

This package exposes, through one Robot Framework entry point:

- Jira
- Confluence
- Service Desk
- Xray Server / Data Center
- Xray Cloud through the dedicated `xray-cloud-for-jira` client

## Main design goals

- keep one Robot Framework library instead of several wrappers
- reuse the Python client layer for Xray Cloud
- support implicit active sessions
- avoid duplicating keywords
- keep Python and Robot Framework usages aligned

## 💥 CORE FEATURE: Hybrid Dynamic Keywords (600+)

This library dynamically exposes 600+ keywords (Jira/Confluence/Bitbucket/JSD/Jira Xray DC)

## 🔧 How it works
- introspects Python clients
- maps public methods → RF keywords
- injects them dynamically

## 🎯 Benefits

- no wrapper maintenance
- automatic updates
- massive coverage

## Installation

```bash
pip install robotframework-jira-xray-confluence
```

or with uv:

```bash
uv add robotframework-jira-xray-confluence
```

## Dependencies

This package depends on:

- `robotframework`
- `atlassian-python-api`
- `wrapt`
- `xray-cloud-for-jira`

## Package structure

```text
robotframework-jira-xray-confluence/
├── src/robotframework_jira_xray_confluence/
│   ├── __init__.py
│   └── JiraXrayConfluence.py
├── examples/
├── pyproject.toml
├── README.md
├── LICENSE
└── .gitignore
```

## How to import the library in Robot Framework

Recommended import:

```robot
Library    robotframework_jira_xray_confluence.JiraXrayConfluence
```

This form is explicit and works cleanly with the class-based implementation.

## Quick start

### Connect to Jira Cloud

```robot
*** Settings ***
Library    robotframework_jira_xray_confluence.JiraXrayConfluence

*** Test Cases ***
Connect To Jira Cloud
    ${jira}=    Connect To Jira
    ...    https://your-company.atlassian.net
    ...    username=your.email@company.com
    ...    password=${JIRA_API_TOKEN}
    ...    cloud=${True}
```

### Connect to Xray Cloud

```robot
*** Settings ***
Library    robotframework_jira_xray_confluence.JiraXrayConfluence

*** Test Cases ***
Connect To Xray Cloud
    ${xray}=    Connect To Xray Cloud
    ...    ${XRAY_CLIENT_ID}
    ...    ${XRAY_CLIENT_SECRET}
```

### Query tests from a Test Plan using the implicit active session

```robot
*** Settings ***
Library    robotframework_jira_xray_confluence.JiraXrayConfluence

*** Test Cases ***
Get Tests From Plan
    Connect To Xray Cloud    ${XRAY_CLIENT_ID}    ${XRAY_CLIENT_SECRET}
    ${tests}=    Get Tests With Test Plan    DEMO-10
    Log To Console    ${tests}
```

## Explicit session mode

You can also pass the session explicitly if needed:

```robot
*** Settings ***
Library    robotframework_jira_xray_confluence.JiraXrayConfluence

*** Test Cases ***
Explicit Session Example
    ${session}=    Connect To Xray Cloud    ${XRAY_CLIENT_ID}    ${XRAY_CLIENT_SECRET}
    ${tests}=    Get Tests With Test Plan    ${session}    DEMO-10
    Log To Console    ${tests}
```

## Xray GraphQL keyword

This keyword directly exposes GraphQL access for advanced use cases.

```robot
*** Settings ***
Library    robotframework_jira_xray_confluence.JiraXrayConfluence

*** Test Cases ***
Use Raw GraphQL
    Connect To Xray Cloud    ${XRAY_CLIENT_ID}    ${XRAY_CLIENT_SECRET}
    ${query}=    Catenate    SEPARATOR=\n
    ...    query($issueId: String!) {
    ...      getTest(issueId: $issueId) {
    ...        issueId
    ...        jira(fields:["key","summary"])
    ...      }
    ...    }
    ${result}=    Xray GraphQL    ${query}    {"issueId": "66925"}
    Log To Console    ${result}
```

## Available connection keywords

- `Connect To Jira`
- `Connect To Confluence`
- `Connect To Xray`
- `Connect To Xray Cloud`
- `Connect To Service Desk`

## Introspection keywords

- `List Atlassian Keywords`
- `Count Atlassian Keywords`
- `List Xray Cloud Keywords`
- `Count Xray Cloud Keywords`

## Xray Cloud keywords exposed automatically

The library dynamically exposes the public methods of `XrayCloudClient`, including:

- `Get Test`
- `Get Test Id`
- `Get Test Plan Id`
- `Get Test Execution Id`
- `Get Tests By Jql`
- `Get Test Plans By Jql`
- `Get Test Executions By Jql`
- `Get Tests With Test Plan`
- `Get Tests With Test Execution`
- `Get Test Runs`
- `Create Test Execution`
- `Add Tests To Test Plan`
- `Update Test Run Status`
- `Import Robot Results`
- `Import Junit Results`
- `Import Cucumber Results`
- `Add Evidence To Test Run`

The names above follow Robot Framework keyword rendering rules based on the Python method names.

## Why the Xray Cloud part is separate

`atlassian-python-api` is very useful, but it does not cover the full Xray Cloud GraphQL use case the way this project needs it.

That is why this library imports and reuses the dedicated package:

- `xray-cloud-for-jira`

This lets the Robot Framework layer stay thin while the Xray Cloud logic lives in a reusable Python package.

## Session behavior

This library supports two modes:

### 1. Implicit session mode

Once you call a `Connect To ...` keyword, the session is stored internally and reused automatically by the following keywords.

### 2. Explicit session mode

If you pass a session object as the first argument, that session is used instead.

This design keeps test cases short, while still allowing advanced flows.

## Cloud and Data Center coverage

### Jira
- Cloud through email + API token
- Server/DC through token-based usage supported by `atlassian-python-api`

### Confluence
- Cloud through email + API token
- Server/DC through token-based usage supported by `atlassian-python-api`

### Xray
- Server/DC through `atlassian.Xray`
- Cloud through `xray-cloud-for-jira`

### Service Desk
- Cloud and Server/DC via `atlassian-python-api`

## Example: mixed usage in one suite

```robot
*** Settings ***
Library    robotframework_jira_xray_confluence.JiraXrayConfluence

*** Test Cases ***
Unified Example
    Connect To Jira
    ...    https://your-company.atlassian.net
    ...    username=your.email@company.com
    ...    password=${JIRA_API_TOKEN}
    ...    cloud=${True}

    Connect To Xray Cloud    ${XRAY_CLIENT_ID}    ${XRAY_CLIENT_SECRET}

    ${issue}=    Get Issue    DEMO-6
    ${tests}=    Get Tests With Test Plan    DEMO-10

    Log To Console    ${issue}
    Log To Console    ${tests}
```

## Development install

Clone both repositories locally if you want to work on both packages together.

### Install the core Xray package first

```bash
git clone https://github.com/orenault/xray-cloud-for-jira.git
cd xray-cloud-for-jira
pip install -e .
```

### Then install the Robot Framework package

```bash
git clone https://github.com/orenault/robotframework-jira-xray-confluence.git
cd robotframework-jira-xray-confluence
pip install -e .
```

or with uv:

```bash
uv sync
```

## Build

```bash
uv build
```

## License

MIT
