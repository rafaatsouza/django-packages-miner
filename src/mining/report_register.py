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
        'repo_size', 'repo_commits', 'repo_has_readme'
    ]

    @staticmethod
    def get_header_line():
        return (
            'dp_slug;dp_category;dp_grids;dp_usage_count;has_valid_repo_url;dp_repo_url;has_valid_repo;'
            'platform;repo_id;repo_stars;repo_last_modified;repo_forks;repo_open_issues;repo_topics;'
            'repo_size;repo_commits;repo_has_readme'
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
        self.repo_id = None


        if self.has_valid_repo_url:
            platform = Platform.get_platform(package['repo_url'])
            self.platform = platform.domain

            token = self._get_token(platform, tokens)
            repo_info = platform.get_repo_info(package['repo_url'], token, temp_path)

            if repo_info:
                self.has_valid_repo = True
                self.repo_id = repo_info['repo_id']
                self.repo_stars = repo_info['repo_stars']
                self.repo_last_modified = repo_info['repo_last_modified']
                self.repo_forks = repo_info['repo_forks']
                self.repo_open_issues = repo_info['repo_open_issues']
                self.repo_topics = repo_info['repo_topics']                
                self.repo_size = repo_info['repo_size']
                self.repo_commits = repo_info['repo_commits']
                self.repo_has_readme = repo_info['repo_has_readme']
            

    def get_line(self):
        line = '{};{};{};{};{};{};{}'.format(
            self.slug, 
            self.category, 
            self.grids, 
            self.usage_count, 
            self.has_valid_repo_url,
            self.repo_url,
            self.has_valid_repo
        )

        if not self.has_valid_repo_url:
            for _ in range(len(self._COLUMNS) - 7):
                line = '{};{}'.format(line, '')
            
            return line

        line = '{};{}'.format(line, self.platform)

        if not self.has_valid_repo:
            for _ in range(len(self._COLUMNS) - 9):
                line = '{};{}'.format(line, '')
          
            return '{};{}'.format(line, False)

        return '{};{};{};{};{};{};{};{};{};{}'.format(
            line, 
            self.repo_id, 
            self.repo_stars,     
            self.repo_last_modified, 
            self.repo_forks, 
            self.repo_open_issues, 
            self.repo_topics,
            self.repo_size,
            self.repo_commits,
            self.repo_has_readme
        )


    def _get_token(self, platform, tokens):
        if platform.value == Platform.GITHUB.value:
            return tokens['github']
        elif platform.value == Platform.GITLAB.value:
            return tokens['gitlab']
