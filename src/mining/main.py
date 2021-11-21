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


def get_finished_packages(output_file):
    import pandas as pd
    df = pd.read_csv(output_file, sep=';')
    return list(df['dp_slug'].values)


if __name__ == '__main__':
    data_path = '../../data/'
    logger = get_logger('{}{}'.format(data_path, os.environ.get('LOG_FILE_NAME') or 'file.log'))
    
    tokens = {
        'github': os.environ['GITHUB_TOKEN'],
        'gitlab': os.environ['GITLAB_TOKEN'],
    }

    output_file = '{}{}'.format(data_path, os.environ.get('OUTPUT_FILE') or 'data.csv')
    finished_packages = []

    if not os.path.exists(output_file):
        with open(output_file, 'a') as f:
            f.write('{}\n'.format(ReportRegister.get_header_line()))
    else:
        finished_packages = get_finished_packages(output_file)

    django_packages_api = DjangoPackagesApi()
    failed_packages = []
    packages_remaining = True
    next = None

    while packages_remaining:
        packages, next = django_packages_api.get_packages(next)
        packages_remaining = len(next) > 0
        for package in packages:
            if not (package['slug'] in finished_packages):
                try:
                    register = ReportRegister(package, tokens, data_path)                
                    with open(output_file, 'a') as f:
                        f.write(register.get_line() + '\n')
                    finished_packages.append(package['slug'])
                except BaseException as error:
                    logger.exception('Unknown error at package {}'.format(package['slug']))
                    failed_packages.append(package['slug'])
            else:
                print('{} already in output file'.format(package['slug']))

    for package_id in failed_packages:
        package = django_packages_api.get_package(package_id)
        try:
            register = ReportRegister(package, tokens, data_path)
            if package['slug'] not in finished_packages:
                with open(output_file, 'a') as f:
                    f.write(register.get_line() + '\n')
                finished_packages.append(register.repo_id)                        
        except BaseException as error:
            logger.exception('Unknown error at package {}'.format(package['slug']))
