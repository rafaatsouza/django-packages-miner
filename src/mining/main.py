import os

from django_packages import DjangoPackagesApi
from report_register import ReportRegister
from control_version import Platform


def get_logger(log_file_name):
    import logging
    
    logger = logging.getLogger(__name__)

    handler = logging.FileHandler(log_file_name)
    format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
    handler.setFormatter(format)
    handler.setLevel(logging.INFO)

    logger.addHandler(handler)

    return logger


if __name__ == '__main__':
    logger = get_logger('../../data/{}'.format(os.environ.get('LOG_FILE_NAME') or 'file.log'))
    
    tokens = {
        'github': os.environ['GITHUB_TOKEN'],
        'gitlab': os.environ['GITLAB_TOKEN'],
    }

    output_file = '../../data/{}'.format(os.environ.get('OUTPUT_FILE') or 'data.csv')

    with open(output_file, 'a') as f:
        f.write('{}\n'.format(ReportRegister.get_header_line()))

    django_packages_api = DjangoPackagesApi()
    succeded_packages = {
        Platform.GITHUB.domain: [],
        Platform.GITLAB.domain: [],
    }
    failed_packages = []
    packages_remaining = True
    next = None

    while packages_remaining:
        packages, next = django_packages_api.get_packages(next)
        packages_remaining = len(next) > 0
        for package in packages:
            try:
                register = ReportRegister(package, tokens)
                if not register.has_valid_repo or register.repo_id not in succeded_packages[register.platform]:
                    with open(output_file, 'a') as f:
                        f.write(register.get_line() + '\n')
                    if register.has_valid_repo and register.repo_id not in succeded_packages[register.platform]:
                        succeded_packages[register.platform].append(register.repo_id)
            except BaseException as error:
                logger.exception('Unknown error at package {}'.format(package['slug']))
                failed_packages.append(package['slug'])

    for package_id in failed_packages:
        package = django_packages_api.get_package(package_id)
        try:
            register = ReportRegister(package, tokens)
            if not register.has_valid_repo or register.repo_id not in succeded_packages[register.platform]:
                with open(output_file, 'a') as f:
                    f.write(register.get_line() + '\n')
                if register.has_valid_repo and register.repo_id not in succeded_packages[register.platform]:
                        succeded_packages[register.platform].append(register.repo_id)
        except BaseException as error:
            logger.exception('Unknown error at package {}'.format(package['slug']))
