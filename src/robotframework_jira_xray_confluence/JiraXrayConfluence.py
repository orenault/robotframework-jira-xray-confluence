#
#  (c)  Olivier RENAULT    2026
#

from __future__ import annotations

import ast
from typing import Any, Optional

import wrapt
from atlassian import Confluence, Jira, ServiceDesk, Xray
from robot.api import logger
from robot.api.deco import keyword

from xray_cloud_for_jira import XrayCloudClient


def _str_to_data(string: Any) -> Any:
    try:
        return ast.literal_eval(str(string).strip())
    except Exception:
        return string


@wrapt.decorator
def _str_vars_to_data(function, instance, args, kwargs):
    args = [_str_to_data(arg) for arg in args]
    kwargs = {arg_name: _str_to_data(arg) for arg_name, arg in kwargs.items()}
    return function(*args, **kwargs)


class JiraXrayConfluence:
    """Unified Robot Framework library for Jira, Confluence and Xray."""

    ROBOT_LIBRARY_SCOPE = "GLOBAL"

    def __init__(self):
        self._jira = Jira
        self._confluence = Confluence
        self._xray = Xray
        self._servicedesk = ServiceDesk
        self._xray_cloud = XrayCloudClient

        self._jira_session = None
        self._confluence_session = None
        self._xray_session = None
        self._servicedesk_session = None
        self._xray_cloud_session = None

    def _xray_cloud_public_methods(self):
        return {
            name
            for name in dir(self._xray_cloud)
            if not name.startswith("_") and callable(getattr(self._xray_cloud, name, None))
        }

    def _call_with_optional_session(self, session_attr, session_type, method_name, *args, **kwargs):
        if args and isinstance(args[0], session_type):
            session = args[0]
            args = args[1:]
        else:
            session = getattr(self, session_attr)

        if session is None:
            raise RuntimeError(
                f"No active session available for keyword '{method_name}'. "
                f"Call the corresponding Connect keyword first or pass the session explicitly."
            )

        args = [_str_to_data(arg) for arg in args]
        kwargs = {k: _str_to_data(v) for k, v in kwargs.items()}

        method = getattr(session, method_name)
        return method(*args, **kwargs)

    def get_keyword_names(self):
        keywords = [
            name
            for name, function in self._jira.__dict__.items()
            if hasattr(function, "__call__")
        ]

        keywords.extend(
            [
                "list_atlassian_keywords",
                "count_atlassian_keywords",
                "list_xray_cloud_keywords",
                "count_xray_cloud_keywords",
                "connect_to_jira",
                "connect_to_confluence",
                "connect_to_servicedesk",
                "connect_to_xray",
                "connect_to_xray_cloud",
                "xray_graphql",
            ]
        )

        keywords.extend(
            [
                name
                for name, function in self._confluence.__dict__.items()
                if hasattr(function, "__call__")
            ]
        )

        xray_cloud_methods = self._xray_cloud_public_methods()
        keywords.extend(
            [
                name
                for name, function in self._xray.__dict__.items()
                if hasattr(function, "__call__") and name not in xray_cloud_methods
            ]
        )

        keywords.extend(
            [
                name
                for name, function in self._servicedesk.__dict__.items()
                if hasattr(function, "__call__")
            ]
        )

        keywords.extend(sorted(xray_cloud_methods))

        if "__init__" in keywords:
            keywords.remove("__init__")

        if "get_issue_remote_links" in keywords:
            keywords.remove("get_issue_remote_links")

        return list(dict.fromkeys(keywords))

    def __getattr__(self, name):
        if hasattr(self._xray_cloud, name) and not name.startswith("_"):
            return lambda *args, **kwargs: self._call_with_optional_session(
                "_xray_cloud_session", XrayCloudClient, name, *args, **kwargs
            )

        if hasattr(self._jira, name):
            return lambda *args, **kwargs: self._call_with_optional_session(
                "_jira_session", Jira, name, *args, **kwargs
            )

        if hasattr(self._confluence, name):
            return lambda *args, **kwargs: self._call_with_optional_session(
                "_confluence_session", Confluence, name, *args, **kwargs
            )

        if hasattr(self._xray, name):
            return lambda *args, **kwargs: self._call_with_optional_session(
                "_xray_session", Xray, name, *args, **kwargs
            )

        if hasattr(self._servicedesk, name):
            return lambda *args, **kwargs: self._call_with_optional_session(
                "_servicedesk_session", ServiceDesk, name, *args, **kwargs
            )

        raise AttributeError("Non-existing keyword " + name)

    @keyword("List Atlassian Keywords")
    def list_atlassian_keywords(self):
        return self.get_keyword_names()

    @keyword("Count Atlassian Keywords")
    def count_atlassian_keywords(self):
        return len(self.get_keyword_names())

    @keyword("List Xray Cloud Keywords")
    def list_xray_cloud_keywords(self):
        return sorted(self._xray_cloud_public_methods())

    @keyword("Count Xray Cloud Keywords")
    def count_xray_cloud_keywords(self):
        return len(self._xray_cloud_public_methods())

    @keyword("Xray GraphQL")
    def xray_graphql(self, session_or_query, query=None, variables=None):
        if isinstance(session_or_query, XrayCloudClient):
            session = session_or_query
            if query is None:
                raise ValueError("Query is required when passing an explicit Xray Cloud session.")
            return session.graphql(
                _str_to_data(query),
                _str_to_data(variables) if variables is not None else None,
            )

        if self._xray_cloud_session is None:
            raise RuntimeError(
                "No active Xray Cloud session available for keyword 'Xray GraphQL'. "
                "Call 'Connect To Xray Cloud' first or pass the session explicitly."
            )

        return self._xray_cloud_session.graphql(
            _str_to_data(session_or_query),
            _str_to_data(query) if query is not None else None,
        )

    @keyword("Connect To Jira")
    def connect_to_jira(
        self,
        url: Optional[str] = None,
        token: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        cloud: bool = False,
        **kwargs,
    ):
        if cloud:
            if not username or not password:
                raise ValueError(
                    "For Jira Cloud you must provide username=<email>, "
                    "password=<api_token>, cloud=True"
                )
            self._jira_session = Jira(
                url=url,
                username=username,
                password=password,
                cloud=True,
                **kwargs,
            )
            logger.debug("Connected to JIRA CLOUD")
            print("Connected to JIRA CLOUD")
        else:
            self._jira_session = Jira(url=url, token=token, **kwargs)
            logger.debug("Connected to JIRA SERVER/DC")
            print("Connected to JIRA SERVER/DC")
        return self._jira_session

    @keyword("Connect To Confluence")
    def connect_to_confluence(
        self,
        url: Optional[str] = None,
        token: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        cloud: bool = False,
        **kwargs,
    ):
        if cloud:
            if not username or not password:
                raise ValueError(
                    "For Confluence Cloud provide username=<email>, "
                    "password=<api_token>, cloud=True"
                )
            self._confluence_session = Confluence(
                url=url,
                username=username,
                password=password,
                cloud=True,
                **kwargs,
            )
            logger.debug("Connected to CONFLUENCE CLOUD")
            print("Connected to CONFLUENCE CLOUD")
        else:
            self._confluence_session = Confluence(url=url, token=token, **kwargs)
            logger.debug("Connected to CONFLUENCE SERVER/DC")
            print("Connected to CONFLUENCE SERVER/DC")
        return self._confluence_session

    @keyword("Connect To Xray")
    def connect_to_xray(
        self,
        url: Optional[str] = None,
        token: Optional[str] = None,
        cloud: bool = False,
        **kwargs,
    ):
        if cloud:
            raise ValueError(
                "Xray Cloud is not supported via atlassian.Xray. "
                "Use 'Connect To Xray Cloud'."
            )
        self._xray_session = Xray(url=url, token=token, **kwargs)
        logger.debug("Connected to XRAY SERVER/DC")
        print("Connected to XRAY SERVER/DC")
        return self._xray_session

    @keyword("Connect To Xray Cloud")
    def connect_to_xray_cloud(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        base_url: str = "https://xray.cloud.getxray.app",
        verify_ssl: bool = False,
        timeout: int = 30,
        debug: bool = False,
    ):
        self._xray_cloud_session = XrayCloudClient(
            client_id=client_id,
            client_secret=client_secret,
            base_url=base_url,
            verify_ssl=verify_ssl,
            timeout=timeout,
            debug=debug,
        )
        logger.debug("Connected to XRAY CLOUD")
        print("Connected to XRAY CLOUD")
        return self._xray_cloud_session

    @keyword("Connect To Service Desk")
    def connect_to_servicedesk(
        self,
        url: Optional[str] = None,
        token: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        cloud: bool = False,
        **kwargs,
    ):
        if cloud:
            if not username or not password:
                raise ValueError(
                    "For Service Desk Cloud provide username=<email>, "
                    "password=<api_token>, cloud=True"
                )
            self._servicedesk_session = ServiceDesk(
                url=url,
                username=username,
                password=password,
                cloud=True,
                **kwargs,
            )
            logger.debug("Connected to SERVICE DESK CLOUD")
            print("Connected to SERVICE DESK CLOUD")
        else:
            self._servicedesk_session = ServiceDesk(url=url, token=token, **kwargs)
            logger.debug("Connected to SERVICE DESK SERVER/DC")
            print("Connected to SERVICE DESK SERVER/DC")
        return self._servicedesk_session


# Backward compatibility alias if an older internal name is still referenced.
RF_Atlassian_Cloud = JiraXrayConfluence
