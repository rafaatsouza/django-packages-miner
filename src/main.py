import requests
import re
import os

from control_version import Platform
from django_packages import DjangoPackagesApi

def check_valid_repo_url(repo_url):
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


def get_token(platform, tokens):
    if platform.value == Platform.GITHUB.value:
        return tokens['github']
    elif platform.value == Platform.GITLAB.value:
        return tokens['gitlab']


def get_csv_line_by_package(columns, package, tokens):
    valid_repo_url = check_valid_repo_url(package['repo_url'])
    line = '{};{};{};{}'.format(
        package['slug'],
        package['category'],
        package['grids'],
        package['usage_count'] or 0
    )

    if not valid_repo_url:
        line = '{};{};{};{}'.format(line, False, '', False)

        for _ in range(len(columns) - 7):
            line = '{};{}'.format(line, '')
        
        return line


    platform = Platform.get_platform(package['repo_url'])
    token = get_token(platform, tokens)
    repo_info = platform.get_repo_info(package['repo_url'], token)

    if not repo_info:
        line = '{};{};{};{};{}'.format(
            line, 
            True, 
            package['repo_url'], 
            False, 
            platform.domain
        )

        for _ in range(len(columns) - 8):
            line = '{};{}'.format(line, '')
        
        return line

    line = '{};{};{};{};{};{};{};{};{};{};{}'.format(
        line, 
        True, 
        package['repo_url'], 
        True, 
        platform.domain,
        repo_info['repo_id'], 
        repo_info['repo_stars'],     
        repo_info['repo_last_modified'], 
        repo_info['repo_forks'], 
        repo_info['repo_open_issues'], 
        repo_info['repo_topics']
    )
    
    return line


def write_package_csv_line(output_file, package, columns, tokens, logger):
    with open(output_file, 'a') as f:
        try:
            f.write(get_csv_line_by_package(columns, package, tokens) + '\n')
        except BaseException as error:
            logger.error('Unknown error at package {}'.format(package['slug']), error)
            return False

    return True


def get_logger(log_file_name):
    import logging
    
    logger = logging.getLogger(__name__)

    handler = logging.FileHandler(log_file_name)
    format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
    handler.setFormatter(format)
    handler.setLevel(logging.INFO)

    logger.addHandler(handler)

    return logger


def get_header_line(columns):
    line = ''
    for column in columns:
        if line == '':
            line = column
        else:
            line = '{};{}'.format(line, column)
    return line


if __name__ == '__main__':
    logger = get_logger('../data/{}'.format(os.environ.get('LOG_FILE_NAME') or 'file.log'))
    
    tokens = {
        'github': os.environ['GITHUB_TOKEN'],
        'gitlab': os.environ['GITLAB_TOKEN'],
    }

    output_file = '../data/{}'.format(os.environ.get('OUTPUT_FILE') or 'data.csv')

    # TODO: add language
    columns = [
        'dp_slug', 'dp_category', 'dp_grids', 'dp_usage_count', 'has_valid_repo_url', 
        'dp_repo_url', 'has_valid_repo', 'platform', 'repo_id', 'repo_stars', 
        'repo_last_modified', 'repo_forks', 'repo_open_issues', 'repo_topics'
    ]

    with open(output_file, 'a') as f:
        f.write('{}\n'.format(get_header_line(columns)))

    django_packages_api = DjangoPackagesApi()
    failed_packages = []
    packages_remaining = True
    next = None

    while packages_remaining:
        packages, next = django_packages_api.get_packages(next)
        packages_remaining = len(next) > 0
        for package in packages:
            if not write_package_csv_line(output_file, package, columns, tokens, logger):
                failed_packages.append(package['slug'])

    for package_id in failed_packages:
        package = django_packages_api.get_package(package_id)
        write_package_csv_line(output_file, package, columns, tokens, logger)
