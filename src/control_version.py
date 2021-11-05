from datetime import datetime
from time import mktime
from enum import Enum


class Platform(Enum):
    GITHUB = (
        'github',
        lambda repo_url, token: _get_github_repo_info(repo_url, token),
    )

    GITLAB = (
        'gitlab',
        lambda repo_url, token: _get_gitlab_repo_info(repo_url, token),
    )

    def __new__(cls, domain, get_repo_info=None):
        obj = object.__new__(cls)
        obj._value_ = domain
        obj._domain_ = domain
        obj._get_repo_info_ = get_repo_info
        return obj

    @property
    def domain(self):
        return self._domain_

    @property
    def get_repo_info(self):
        return self._get_repo_info_

    @staticmethod
    def get_platform(repo_url):
        repo_url = repo_url.lower()

        if Platform.GITHUB.value in repo_url:
            return Platform.GITHUB
        elif Platform.GITLAB.value in repo_url:
            return Platform.GITLAB


def get_org_repo_name_regex(domain, url):
    import re
    
    regex = re.compile(r'(.*)(' + domain + r'\.com\/)'
        r'([a-zA-Z0-9_.-]+\/[a-zA-Z0-9_.-]+)'
        r'((\/[a-zA-Z0-9_.-\/]+)|\Z)', re.IGNORECASE)

    return re.match(regex, url).groups()[2]


def _get_github_repo_info(repo_url, token):
    from github import Github

    org_repo_name = get_org_repo_name_regex(
        Platform.GITHUB.domain, repo_url
    )

    repo = (Github(token)).get_repo(org_repo_name)

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
    
    g = Gitlab('https://gitlab.com', private_token=token)

    org_repo_name = get_org_repo_name_regex(
        Platform.GITLAB.domain, repo_url
    )

    repo = g.projects.get(org_repo_name)

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
