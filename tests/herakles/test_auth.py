from unittest.mock import patch

import herakles.auth as under_test

NS = "herakles.auth"


def ns(module):
    return f"{NS}.{module}"


class TestJiraAuthBasic:
    def test_auth_type(self):
        auth = under_test.JiraAuthBasic("username", "password")

        assert auth.auth_type() == under_test.AuthType.BASIC


class TestJiraAuthOAuth:
    def test_auth_type(self):
        auth = under_test.JiraAuthOAuth("token", "secret", "key", "cert")

        assert auth.auth_type() == under_test.AuthType.OAUTH

    def test_create_from_dict(self):
        auth_dict = {
            "access_token": "token",
            "access_token_secret": "secret",
            "consumer_key": "key",
            "key_certificate": "cert",
        }

        auth = under_test.JiraAuthOAuth.from_dict(auth_dict)

        assert auth.access_token == auth_dict["access_token"]
        assert auth.access_token_secret == auth_dict["access_token_secret"]
        assert auth.consumer_key == auth_dict["consumer_key"]
        assert auth.key_cert == auth_dict["key_certificate"]

    @patch(ns("read_yaml_file"))
    def test_create_from_yaml_file(self, read_file_mock):
        auth_dict = {
            "access_token": "token",
            "access_token_secret": "secret",
            "consumer_key": "key",
            "key_certificate": "cert",
        }
        auth_file = {"jira_key": auth_dict}

        read_file_mock.return_value = auth_file

        auth = under_test.JiraAuthOAuth.from_yaml_file("file.yml", "jira_key")

        assert auth.access_token == auth_dict["access_token"]
        assert auth.access_token_secret == auth_dict["access_token_secret"]
        assert auth.consumer_key == auth_dict["consumer_key"]
        assert auth.key_cert == auth_dict["key_certificate"]
