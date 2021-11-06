import re

from datetime import datetime
from enum import Enum


class Platform(Enum):
    GITHUB = (
        'github',
        lambda repo_url, token: _get_github_repo_info(repo_url, token),
        re.compile(r'(.*)(github\.com\/)'
            r'([a-zA-Z0-9_.-]+\/[a-zA-Z0-9_.-]+)'
            r'((\/[a-zA-Z0-9_.-\/]+)|\Z)', re.IGNORECASE)
    )

    GITLAB = (
        'gitlab',
        lambda repo_url, token: _get_gitlab_repo_info(repo_url, token),
        re.compile(r'(.*)(gitlab\.com\/)'
            r'([a-zA-Z0-9_.-]+\/([a-zA-Z0-9_.-]+\/)?[a-zA-Z0-9_.-]+)'
            r'((\/[a-zA-Z0-9_.-\/]+)|\Z)', re.IGNORECASE)
    )

    def __new__(cls, domain, get_repo_info, get_id_regex):
        obj = object.__new__(cls)
        obj._value_ = domain
        obj._domain_ = domain
        obj._get_repo_info_ = get_repo_info
        obj._get_id_regex_ = get_id_regex
        return obj

    @property
    def domain(self):
        return self._domain_

    @property
    def get_id_regex(self):
        return self._get_id_regex_

    @property
    def get_repo_info(self):
        return self._get_repo_info_

    @staticmethod
    def get_valid_domains():
        return [
            Platform.GITHUB.domain,
            Platform.GITLAB.domain,
        ]

    @staticmethod
    def get_platform(repo_url):
        repo_url = repo_url.lower()

        if Platform.GITHUB.value in repo_url:
            return Platform.GITHUB
        elif Platform.GITLAB.value in repo_url:
            return Platform.GITLAB


def _get_github_repo_info(repo_url, token):
    from github import Github, GithubException

    org_repo_name = re.match(Platform.GITHUB.get_id_regex, repo_url).groups()[2]
    
    try:
        repo = (Github(token)).get_repo(org_repo_name)
    except GithubException as err:
        if err._GithubException__status == 404:
            return None
        else:
            raise err

    if not repo:
        return None
    
    last_modified = datetime.strptime(repo.last_modified, '%a, %d %b %Y %H:%M:%S %Z')

    topics = ''
    for topic in repo.get_topics():
        if topics == '':
            topics = topic
        else:
            topics = '{},{}'.format(topics, topic)

    return {
        'repo_id': org_repo_name, 
        'repo_stars': repo.stargazers_count or 0, 
        'repo_last_modified': (
            '{}:000'.format(datetime.strftime(last_modified, '%Y-%m-%dT%H:%M:%S'))
        ), 
        'repo_forks': repo.forks_count, 
        'repo_open_issues': repo.open_issues_count, 
        'repo_topics': topics
    }


def _get_gitlab_repo_info(repo_url, token):
    from gitlab import Gitlab
    from gitlab.exceptions import GitlabGetError
    
    g = Gitlab('https://gitlab.com', private_token=token)

    org_repo_name = re.match(Platform.GITLAB.get_id_regex, repo_url).groups()[2]

    try:
        repo = g.projects.get(org_repo_name)
    except GitlabGetError as err:
        if err.response_code == 404:
            return None
        raise err

    if not repo:
        return None

    last_modified = repo.last_activity_at[:(repo.last_activity_at.rfind('.'))]

    topics = ''
    for topic in repo.topics:
        if topics == '':
            topics = topic
        else:
            topics = '{},{}'.format(topics, topic)

    return {
        'repo_id': org_repo_name, 
        'repo_stars': repo.star_count,
        'repo_last_modified': '{}:000'.format(last_modified), 
        'repo_forks': repo.forks_count, 
        'repo_open_issues': repo.open_issues_count, 
        'repo_topics': topics
    }
