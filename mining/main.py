import os

from django_packages_provider_factory import DjangoPackagesProviderFactory
from report_register import ReportRegister


def get_logger(log_file_name):
    import logging
    
    logger = logging.getLogger(__name__)

    handler = logging.FileHandler(log_file_name)
    format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
    handler.setFormatter(format)
    handler.setLevel(logging.INFO)

    logger.addHandler(handler)

    return logger


def get_finished_slugs_and_packages(output_file):
    import pandas as pd
    df = pd.read_csv(output_file, sep=';')
    
    slugs = list(df['dp_slug'].values)
    packages = list(df[df['repo_id'].astype(str).str.len() > 0]['repo_id'].values)

    return slugs, packages


if __name__ == '__main__':
    data_path = '../data/'
    logger = get_logger('{}{}'.format(data_path, os.environ.get('LOG_FILE_NAME') or 'file.log'))
    
    tokens = {
        'github': os.environ['GITHUB_TOKEN'],
        'gitlab': os.environ['GITLAB_TOKEN'],
    }

    output_file = '{}{}'.format(data_path, os.environ.get('OUTPUT_FILE') or 'data.csv')
    finished_slugs = []
    finished_packages = []

    if not os.path.exists(output_file):
        with open(output_file, 'a') as f:
            f.write('{}\n'.format(ReportRegister.get_header_line()))
    else:
        finished_slugs, finished_packages = get_finished_slugs_and_packages(output_file)

    django_packages_provider = DjangoPackagesProviderFactory.build(
        '{}{}'.format(data_path, os.environ.get('DATAFRAME_FILE'))
    )
    failed_slugs = []
    packages_remaining = True
    next = None

    while packages_remaining:
        packages, next = django_packages_provider.get_packages(next)
        packages_remaining = next is not None
        for package in packages:
            if not (package['slug'] in finished_slugs):
                try:
                    register = ReportRegister(package, tokens, data_path)
                    if not register.repo_id or register.repo_id not in finished_packages:
                        with open(output_file, 'a') as f:
                            f.write(register.get_line() + '\n')
                        if register.repo_id:
                            finished_packages.append(register.repo_id)
                        print('{} done'.format(package['slug']))
                    else:
                        print('{} without ID or already in file'.format(package['slug']))
                    finished_slugs.append(package['slug'])
                except BaseException as error:
                    logger.exception('Unknown error at package {}'.format(package['slug']))
                    failed_slugs.append(package['slug'])
            else:
                print('{} already in output file'.format(package['slug']))

    for package_id in failed_slugs:
        package = django_packages_provider.get_package_by_id(package_id)
        try:
            register = ReportRegister(package, tokens, data_path)
            if not register.repo_id or register.repo_id not in finished_packages:
                with open(output_file, 'a') as f:
                    f.write(register.get_line() + '\n')
                if register.repo_id:
                    finished_packages.append(register.repo_id)
            finished_slugs.append(register.repo_id)                        
        except BaseException as error:
            logger.exception('Unknown error at package {}'.format(package['slug']))
