import os, re

from datetime import datetime
from enum import Enum


class Platform(Enum):
    GITHUB = (
        'github',
        'https://github.com/',
        lambda repo_url, token, temp_path: _get_github_repo_info(repo_url, token, temp_path),
        re.compile(r'(.*)(github\.com\/)'
            r'([a-zA-Z0-9_.-]+\/[a-zA-Z0-9_.-]+)'
            r'((\/[a-zA-Z0-9_.-\/]+)|\Z)', re.IGNORECASE)
    )

    GITLAB = (
        'gitlab',
        'https://gitlab.com/',
        lambda repo_url, token, temp_path: _get_gitlab_repo_info(repo_url, token, temp_path),
        re.compile(r'(.*)(gitlab\.com\/)'
            r'([a-zA-Z0-9_.-]+\/([a-zA-Z0-9_.-]+\/)?[a-zA-Z0-9_.-]+)'
            r'((\/[a-zA-Z0-9_.-\/]+)|\Z)', re.IGNORECASE)
    )

    def __new__(cls, domain, address, get_repo_info, get_id_regex):
        obj = object.__new__(cls)
        obj._value_ = domain
        obj._domain_ = domain
        obj._address_ = address
        obj._get_repo_info_ = get_repo_info
        obj._get_id_regex_ = get_id_regex
        return obj

    @property
    def domain(self):
        return self._domain_

    @property
    def address(self):
        return self._address_

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


def _get_github_repo_info(repo_url, token, temp_path):
    from github import Github, GithubException

    org_repo_name = re.match(Platform.GITHUB.get_id_regex, repo_url).groups()[2]

    try:
        repo = (Github(token)).get_repo(org_repo_name)
        _ = repo.get_contents('/') # check if repo is empty
    except GithubException as err:
        status = err._GithubException__status
        message = err._GithubException__data['message']

        if status == 404:
            return None
        elif status == 403 and message.startswith('API rate limit exceeded for'):
            try:
                repo = (Github()).get_repo(org_repo_name)
            except GithubException as error:
                if error._GithubException__status == 404:
                    return None
                else:
                    raise error
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

    repo_size, repo_commits, last_commit_date, repo_has_readme, repo_has_installed_app_ref = (
        _get_repo_folder_info('{}{}'.format(Platform.GITHUB.address, org_repo_name), temp_path)
    )

    used_by_count = _get_github_used_by(repo.full_name, repo.html_url)

    return {
        'repo_id': repo.full_name, 
        'repo_url': repo.html_url,
        'repo_stars': repo.stargazers_count or 0, 
        'repo_last_modified': (
            '{}:000'.format(datetime.strftime(last_modified, '%Y-%m-%dT%H:%M:%S'))
        ), 
        'repo_last_commit_date': (
            '{}:000'.format(datetime.strftime(last_commit_date, '%Y-%m-%dT%H:%M:%S')) if last_commit_date else None
        ),
        'repo_forks': repo.forks_count, 
        'repo_open_issues': repo.open_issues_count, 
        'repo_topics': topics,
        'repo_size': repo_size,
        'repo_commits': repo_commits,
        'repo_has_readme': repo_has_readme,
        'repo_has_installed_app_ref': repo_has_installed_app_ref,
        'has_used_by_count': used_by_count is not None,
        'used_by_count': used_by_count,
    }


def _get_gitlab_repo_info(repo_url, token, temp_path):
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

    repo_size, repo_commits, last_commit_date, repo_has_readme, repo_has_installed_app_ref = (
        _get_repo_folder_info('{}{}'.format(Platform.GITLAB.address, org_repo_name), temp_path)
    )

    return {
        'repo_id': org_repo_name, 
        'repo_url': repo.web_url,
        'repo_stars': repo.star_count,
        'repo_last_modified': '{}:000'.format(last_modified), 
        'repo_last_commit_date': (
            '{}:000'.format(datetime.strftime(last_commit_date, '%Y-%m-%dT%H:%M:%S')) if last_commit_date else None
        ),
        'repo_forks': repo.forks_count, 
        'repo_open_issues': repo.open_issues_count, 
        'repo_topics': topics,
        'repo_size': repo_size,
        'repo_commits': repo_commits,
        'repo_has_readme': repo_has_readme,
        'repo_has_installed_app_ref': repo_has_installed_app_ref,
    }


def _get_repo_folder_info(repo_url, temp_path):
    import uuid, shutil
    from git import Repo

    path = '{}{}{}/'.format(temp_path, '' if temp_path.endswith('/') else '/', uuid.uuid4().hex)

    Repo.clone_from(repo_url, path)

    size = _get_folder_size(path)
    total_commits, last_commit_date = _get_total_and_last_date_commits(Repo(path))
    has_readme, has_installed_apps_ref = _check_readme(path)

    shutil.rmtree(path)
    return size, total_commits, last_commit_date, has_readme, has_installed_apps_ref


def _check_readme(path):
    installed_apps_reg = re.compile(r'.*(INSTALLED)\_(APPS).*', re.IGNORECASE)
    readme_reg = re.compile(r'^(README)((\..+)|\Z)', re.IGNORECASE)
    readme_files = [f for f in os.listdir(path) if re.match(readme_reg, f)]
    has_readme = len(readme_files) > 0
    
    if has_readme:
        for readme_file in readme_files:
            fp = os.path.join(path, readme_file)
            if __check_regex_in_file(installed_apps_reg, fp):
                return has_readme, True

    for folder in ['doc', 'docs']:
        doc_path = os.path.join(path, folder)
        if os.path.exists(doc_path): 
            doc_files = [f for f in os.listdir(doc_path) if f.endswith('.rst') or f.endswith('.md')]
            for doc_file in doc_files:
                fp = os.path.join(doc_path, doc_file)
                if __check_regex_in_file(installed_apps_reg, fp):
                    return has_readme, True

    return has_readme, False


def __check_regex_in_file(reg, file):
    if not os.path.islink(file):
        with open(file) as f:
            for line in f:
                if re.match(reg, line):
                    return True
    
    return False


def _get_total_and_last_date_commits(repo):
    last_date = None
    all_commits = repo.iter_commits()
    commits = 0
    while True:
        try:
            current = next(all_commits)
            commits = commits + 1
            if current.authored_datetime and (not last_date or last_date < current.authored_datetime):
                last_date = current.authored_datetime            
        except StopIteration:
            break
    return commits, last_date


def _get_folder_size(folder_path):
    size = 0
    for path, _, files in os.walk(folder_path):
        if not os.path.islink(path):
            for f in files:
                fp = os.path.join(path, f)
                if not os.path.islink(fp):
                    size += os.path.getsize(fp)
    return size


def _get_github_used_by(repo_id, repo_url):
    import requests
    from bs4 import BeautifulSoup

    html_text = requests.get(repo_url).text
    soup = BeautifulSoup(html_text, 'html.parser')
    counters = soup.findAll('span', class_='Counter')

    if counters and len(counters) > 0:
        for i in range(len(counters)):
            title = counters[i].get('title')
            if title and counters[i].parent:
                title = title.replace(',','').strip()
                href = counters[i].parent.get('href')
                correct_href = href and '{}/network/dependents'.format(repo_id) in href

                if title and title.isnumeric() and correct_href:
                    return int(title)