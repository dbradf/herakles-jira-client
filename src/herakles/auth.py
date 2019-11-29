"""Authentication information."""
import abc
from enum import Enum, auto
from typing import Dict, Tuple, ClassVar

from jira import JIRA

from herakles.util.file_utils import read_yaml_file

DEFAULT_AUTH_KEY = "jira"


class AuthType(Enum):
    """Type of authentication to use."""

    BASIC = auto()
    OAUTH = auto()


class JiraAuth(abc.ABC):
    """Container for Jira authentication."""

    @abc.abstractmethod
    def auth_type(self) -> AuthType:
        """Get the type of authentication to use."""

    @abc.abstractmethod
    def _connect(self, cls: ClassVar, options: Dict, timeout: int):
        """
        Connect to the specified jira instance.

        :param cls: JiraWrapper class constructor.
        :param options: options to connect to.
        :param timeout: Network timeout.
        :return: Jira Wrapper.
        """


class JiraAuthBasic(JiraAuth):
    """Basic Authentication for Jira."""

    def __init__(self, username: str, password: str = None):
        super(JiraAuthBasic).__init__()
        self.username = username
        self.password = password

    def auth_type(self) -> AuthType:
        """Get the type of authentication to use."""
        return AuthType.BASIC

    def _basic_auth(self) -> Tuple[str, str]:
        """Return a user, password tuple that can be used to configure JIRA basic auth."""
        return self.username, self.password

    def _connect(self, cls: ClassVar, options: Dict, timeout: int):
        self._jira = JIRA(
            options=options, basic_auth=self._basic_auth(), validate=True, timeout=timeout
        )


class JiraAuthOAuth(JiraAuth):
    """OAuth configuration for Jira."""

    def __init__(
        self, access_token: str, access_token_secret: str, consumer_key: str, key_cert: str
    ):
        super(JiraAuthOAuth).__init__()
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.consumer_key = consumer_key
        self.key_cert = key_cert

    @classmethod
    def from_dict(cls, auth_config: Dict):
        """
        Create a JiraAuth object for OAuth from a dictionary.

        The dictionary should contain the following: 'access_token', 'access_token_secret',
        'consumer_key', and 'key_cert'.

        :param auth_config: Dictionary containing authentication information.
        :return: JiraAuth object for OAuth.
        """
        return cls(
            auth_config["access_token"],
            auth_config["access_token_secret"],
            auth_config["consumer_key"],
            auth_config["key_certificate"],
        )

    @classmethod
    def from_yaml_file(cls, yaml_file: str, config_key: str = DEFAULT_AUTH_KEY):
        """
        Create a JiraAuth object for OAuth from a yaml file.

        The file should contain the following under the specified key: 'access_token',
        'access_token_secret', 'consumer_key', and 'key_certificate'.

        :param yaml_file: Path to yaml file.
        :param config_key: Top level configuration key.
        :return: JiraAuth object.
        """
        config = read_yaml_file(yaml_file)
        return cls.from_dict(config[config_key])

    def auth_type(self) -> AuthType:
        """Get the type of authentication to use."""
        return AuthType.OAUTH

    def _get_oauth(self) -> Dict:
        """Return a dictionary that can be used to configure JIRA oauth."""
        return {
            "access_token": self.access_token,
            "access_token_secret": self.access_token_secret,
            "consumer_key": self.consumer_key,
            "key_cert": self.key_cert,
        }

    def _connect(self, cls: ClassVar, options: Dict, timeout: int):
        return cls(JIRA(options=options, oauth=self._get_oauth(), validate=True, timeout=timeout))
