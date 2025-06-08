#!/usr/bin/env python3
import unittest
from unittest.mock import patch ,PropertyMock ,Mock
from parameterized import parameterized ,parameterized_class
from client import GithubOrgClient 
from fixtures import org_payload, repos_payload, expected_repos, apache2_repos 

class TestGithubOrgClient(unittest.TestCase):
    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch("client.get_json")
    def test_org(self, org_name, mock_get_json):
        expected_data = {"login": org_name}
        mock_get_json.return_value = expected_data

        client = GithubOrgClient(org_name)
        self.assertEqual(client.org, expected_data)
        mock_get_json.assert_called_once_with(f"https://api.github.com/orgs/{org_name}")




class TestGithubOrgClient(unittest.TestCase):
    def test_public_repos_url(self):
        expected_url = "https://api.github.com/orgs/google/repos"
        payload = {"repos_url": expected_url}

        with patch.object(GithubOrgClient, "org", new_callable=PropertyMock) as mock_org:
            mock_org.return_value = payload
            client = GithubOrgClient("google")
            self.assertEqual(client._public_repos_url, expected_url)




class TestGithubOrgClient(unittest.TestCase):
    @patch("client.get_json")
    def test_public_repos(self, mock_get_json):
       
        mock_payload = [
            {"name": "repo1"},
            {"name": "repo2"},
        ]
        mock_get_json.return_value = mock_payload

        with patch.object(GithubOrgClient, "_public_repos_url", new="http://mocked_url.com") as mock_url:
            client = GithubOrgClient("google")
            result = client.public_repos()
            self.assertEqual(result, ["repo1", "repo2"])

            
            mock_get_json.assert_called_once_with("http://mocked_url.com")
            self.assertEqual(mock_url.call_count, 1)





class TestGithubOrgClient(unittest.TestCase):
    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        self.assertEqual(GithubOrgClient.has_license(repo, license_key), expected)






@parameterized_class([
    {
        "org_payload": org_payload,
        "repos_payload": repos_payload,
        "expected_repos": expected_repos,
        "apache2_repos": apache2_repos
    }
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.get_patcher = patch("requests.get")

        mock_get = cls.get_patcher.start()

      
        def side_effect(url):
            mock_response = Mock()
            if url == "https://api.github.com/orgs/google":
                mock_response.json.return_value = cls.org_payload
            elif url == cls.org_payload.get("repos_url"):
                mock_response.json.return_value = cls.repos_payload
            return mock_response

       
        mock_get.side_effect = side_effect

    @classmethod
    def tearDownClass(cls):
        cls.get_patcher.stop()


