import pandas as pd

import sys
sys.path.append("../")
import visualization.data_methods as dm


def get_package_data(package_df_data: pd.Series):
    from git import Repo
    import uuid, shutil
    
    path = '{}{}/'.format('../data/', uuid.uuid4().hex)

    authors = {}
    Repo.clone_from(package_df_data['dp_repo_url'], path)
    repo = Repo(path)
    all_commits = repo.iter_commits()

    while True:
        try:
            current = next(all_commits)
            if current and current.author and current.author.email:
                if current.author.email in authors:
                    authors[current.author.email]['commits'] = authors[current.author.email]['commits'] + 1
                else:
                    authors[current.author.email] = {
                        'commits': 1,
                        'name': current.author.name or current.author.email[0:current.author.email.find('@')]
                    }
        except StopIteration:
            break

    shutil.rmtree(path)

    result = ''
    base_line = '\n{};{};{};{};{};{};{}'.format(
        package_df_data['platform'],
        package_df_data['repo_id'],
        package_df_data['dp_grids'] if not pd.isna(package_df_data['dp_grids']) else '',
        package_df_data['repo_topics'] if not pd.isna(package_df_data['repo_topics']) else '',
        package_df_data['repo_stars'],
        len(authors.keys()),
        package_df_data['repo_last_commit_date'],
    )
    
    for key, value in authors.items():
        result = '{}{};{};{};{}'.format(result, base_line, key, value['name'], value['commits'])
    
    return result


if __name__ == '__main__':
    output_file = '../data/django-packages-authors.csv'    
    df = dm.get_valid_dataframe()
    df = df[df['repo_last_modified'] >= '2021-01-01T00:00:00:000']
    size = len(df)
    current = 0

    with open(output_file, 'a') as f:
        f.write('platform;repo_id;grids;topics;repo_stars;repo_authors;repo_last_commit_date;author_email;author_name;commits_count')

    for row in df.iterrows():
        with open(output_file, 'a') as f:
            f.write(get_package_data(row[1]))
        current = current + 1
        print('{} done - {}'.format(row[1]['repo_id'], '{0:.2f}%'.format((current/size) * 100)))
