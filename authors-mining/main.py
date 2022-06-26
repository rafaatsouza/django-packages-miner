import pandas as pd

import sys
sys.path.append("../")
import visualization.data_methods as dm

def is_real_author(author_email):
    return (
        author_email and 'dependabot' not in author_email
        and 'noreply' not in author_email and 'no.reply' not in author_email
        and 'no-reply' not in author_email and 'github' not in author_email
        and author_email.strip().lower() != 'no author' and author_email.strip().lower() != 'none'
    )

def get_key_by_date(dt):
    return dt.strftime("%Y-%m")


def get_package_data(package_df_data: pd.Series):
    from git import Repo
    import uuid, shutil
    
    path = '{}{}/'.format('../data/', uuid.uuid4().hex)

    authors, authors_by_month, authors_by_year = {}, {}, {}
    Repo.clone_from(package_df_data['dp_repo_url'], path)
    repo = Repo(path)
    all_commits = repo.iter_commits()

    while True:
        try:
            current = next(all_commits)
            valid = (
                current and current.author and current.author.email 
                and is_real_author(current.author.email) and current.authored_datetime
            )
            if valid:
                email = current.author.email
                if current.authored_datetime.year >= 2021:
                    if email in authors:
                        authors[email]['commits'] = authors[email]['commits'] + 1
                    else:
                        authors[email] = {
                            'commits': 1,
                            'name': current.author.name or email[0:email.find('@')]
                        }
                if (
                    current.authored_datetime.year >= 2014 
                    and (current.authored_datetime.year < 2022 or current.authored_datetime.month < 6)
                ):
                    key_by_month = current.authored_datetime.strftime("%Y-%m")
                    if key_by_month in authors_by_month and email not in authors_by_month[key_by_month]['emails']:
                        authors_by_month[key_by_month]['emails'].append(email)
                    elif key_by_month not in authors_by_month:
                        authors_by_month[key_by_month] = {
                            'emails': [email]
                        }
                if current.authored_datetime.year >= 2014 and current.authored_datetime.year <= 2021:
                    key_by_year = current.authored_datetime.strftime("%Y")
                    if key_by_year in authors_by_year and email not in authors_by_year[key_by_year]['emails']:
                        authors_by_year[key_by_year]['emails'].append(email)
                    elif key_by_year not in authors_by_year:
                        authors_by_year[key_by_year] = {
                            'emails': [email]
                        }
        except StopIteration:
            break

    shutil.rmtree(path)

    result, result_by_month, result_by_year = '', '', ''
    base_line = '\n{};{};{};{};{};{};{}'.format(
        package_df_data['platform'],
        package_df_data['repo_id'],
        package_df_data['dp_grids'] if not pd.isna(package_df_data['dp_grids']) else '',
        package_df_data['repo_topics'] if not pd.isna(package_df_data['repo_topics']) else '',
        package_df_data['repo_stars'],
        len(authors.keys()),
        package_df_data['repo_last_commit_date'],
    )

    base_line_by_date = '\n{};{};{};{};{}'.format(
        package_df_data['platform'],
        package_df_data['repo_id'],
        package_df_data['dp_grids'] if not pd.isna(package_df_data['dp_grids']) else '',
        package_df_data['repo_topics'] if not pd.isna(package_df_data['repo_topics']) else '',
        package_df_data['repo_last_commit_date'],
    )
    
    for key, value in authors.items():
        result = '{}{};{};{};{}'.format(result, base_line, key, value['name'], value['commits'])

    for key in sorted(authors_by_month):
        result_by_month = '{}{};{};{}'.format(
            result_by_month, base_line_by_date, key, len(authors_by_month[key]['emails'])
        )

    for key in sorted(authors_by_year):
        result_by_year = '{}{};{};{}'.format(
            result_by_year, base_line_by_date, key, len(authors_by_year[key]['emails'])
        )
    
    return result, result_by_month, result_by_year


if __name__ == '__main__':
    output_file = '../data/django-packages-authors.csv'
    output_file_month = '../data/django-packages-authors-by-month.csv'
    output_file_year = '../data/django-packages-authors-by-year.csv'
    df = dm.get_valid_dataframe()
    df = df[df['repo_last_modified'] >= '2021-01-01T00:00:00:000']
    size = len(df)
    current = 0

    with open(output_file, 'a') as f:
        f.write('platform;repo_id;grids;topics;repo_stars;repo_authors;repo_last_commit_date;author_email;author_name;commits_count')
    
    with open(output_file_month, 'a') as f:
        f.write('platform;repo_id;grids;topics;repo_last_commit_date;month;authors_count')

    with open(output_file_year, 'a') as f:
        f.write('platform;repo_id;grids;topics;repo_last_commit_date;year;authors_count')

    for row in df.iterrows():
        data, data_by_month, data_by_year = get_package_data(row[1])
        with open(output_file, 'a') as f:
            f.write(data)
        with open(output_file_month, 'a') as f:
            f.write(data_by_month)
        with open(output_file_year, 'a') as f:
            f.write(data_by_year)
        current = current + 1
        print('{} done - {}'.format(row[1]['repo_id'], '{0:.2f}%'.format((current/size) * 100)))
