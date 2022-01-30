from control_version import Platform


def _check_valid_repo_url(repo_url):
    import requests
    import re

    regex_domains = ''
    for domain in Platform.get_valid_domains():
        if regex_domains == '':
            regex_domains = domain
        else:
            regex_domains = '{}|{}'.format(regex_domains, domain)

    regex = re.compile(
        r'^(http(s){0,1}\:\/\/){0,1}((www\.){0,1})'
        r'((' + regex_domains + r')\.com\/)'
        r'([a-zA-Z0-9_.-]+\/([a-zA-Z0-9_.-]+\/)?[a-zA-Z0-9_.-]+)'
        r'((\/[a-zA-Z0-9_.-\/]+)|\Z)', re.IGNORECASE)

    if not re.match(regex, repo_url):
        return False

    try:
        test_response = requests.get(repo_url)
        test_response.raise_for_status()
    except requests.models.ConnectionError:
        return False
    except requests.models.HTTPError:
        return False
    
    return True


class ReportRegister():
    _COLUMNS = [
        'dp_slug', 'dp_category', 'dp_grids', 'dp_usage_count', 'has_valid_repo_url', 
        'dp_repo_url', 'has_valid_repo', 'platform', 'repo_id', 'repo_stars', 
        'repo_last_modified', 'repo_forks', 'repo_open_issues', 'repo_topics',
        'repo_size', 'repo_commits', 'repo_has_readme', 'repo_has_installed_app_ref'
    ]

    @staticmethod
    def get_header_line():
        return (
            'dp_slug;dp_category;dp_grids;dp_usage_count;has_valid_repo_url;dp_repo_url;has_valid_repo;'
            'platform;repo_id;repo_stars;repo_last_modified;repo_last_commit_date;repo_forks;repo_open_issues;'
            'repo_topics;repo_size;repo_commits;repo_has_readme;repo_has_installed_app_ref;has_used_by_count;used_by_count'
        )


    def __init__(self, package, tokens, temp_path):
        self.slug = package['slug']
        self.category = package['category']
        self.grids = package['grids']
        self.usage_count = package['usage_count'] or 0
        self.has_valid_repo_url = _check_valid_repo_url(package['repo_url'])
        self.repo_url = package['repo_url'] if self.has_valid_repo_url else ''
        self.has_valid_repo = False
        self.repo_has_readme = False
        self.repo_has_installed_app_ref = False
        self.repo_id = None
        self.repo_stars = None
        self.repo_last_modified = None
        self.repo_last_commit_date = None
        self.repo_forks = None
        self.repo_open_issues = None
        self.repo_topics = None
        self.repo_size = None
        self.repo_commits = None
        self.has_used_by_count = False
        self.used_by_count = None


        if self.has_valid_repo_url:
            platform = Platform.get_platform(package['repo_url'])
            self.platform = platform.domain

            token = self._get_token(platform, tokens)
            repo_info = platform.get_repo_info(package['repo_url'], token, temp_path)

            if repo_info:
                self.has_valid_repo = True
                self.repo_id = repo_info['repo_id']
                if 'repo_url' in repo_info and repo_info['repo_url']:
                    self.repo_url = repo_info['repo_url']
                self.repo_stars = repo_info['repo_stars']
                self.repo_last_modified = repo_info['repo_last_modified']
                self.repo_last_commit_date = repo_info['repo_last_commit_date']
                self.repo_forks = repo_info['repo_forks']
                self.repo_open_issues = repo_info['repo_open_issues']
                self.repo_topics = repo_info['repo_topics']                
                self.repo_size = repo_info['repo_size']
                self.repo_commits = repo_info['repo_commits']
                self.repo_has_readme = repo_info['repo_has_readme']
                self.repo_has_installed_app_ref = repo_info['repo_has_installed_app_ref']
                
                if 'has_used_by_count' in repo_info and repo_info['has_used_by_count']:
                    self.has_used_by_count = repo_info['has_used_by_count']
                    self.used_by_count = repo_info['used_by_count']
            

    def get_line(self):
        line = '"{}";"{}";"{}";{};"{}";"{}";"{}"'.format(
            self.slug, 
            self.category, 
            self.grids, 
            self.usage_count, 
            self.has_valid_repo_url,
            self.repo_url,
            self.has_valid_repo
        )

        if not self.has_valid_repo_url:
            return '{};"";"";;;;;;"";;;"False";"False";"False";'.format(line)

        return '{};"{}";{};{};{};{};{};{};{};{};{};"{}";"{}";"{}";{}'.format(
            line, 
            self.platform,
            '"{}"'.format(self.repo_id) if self.repo_id is not None else '', 
            self.repo_stars if self.repo_stars is not None else '',
            '"{}"'.format(self.repo_last_modified) if self.repo_last_modified is not None else '', 
            '"{}"'.format(self.repo_last_commit_date) if self.repo_last_commit_date is not None else '', 
            self.repo_forks if self.repo_forks is not None else '', 
            '"{}"'.format(self.repo_open_issues) if self.repo_open_issues is not None else '', 
            self.repo_topics or '',
            self.repo_size if self.repo_size is not None else '',
            self.repo_commits if self.repo_commits is not None else '',
            self.repo_has_readme,
            self.repo_has_installed_app_ref,
            self.has_used_by_count,
            self.used_by_count if self.used_by_count is not None else '',
        )


    def _get_token(self, platform, tokens):
        if platform.value == Platform.GITHUB.value:
            return tokens['github']
        elif platform.value == Platform.GITLAB.value:
            return tokens['gitlab']
