# > pega df
# > itera por cada repo
#   > itera por cada commit para obter lista de autores
# > salva novo df somente com infos de autores e repos
import pandas as pd

import sys
sys.path.append("../")
import visualization.data_methods as dm


def get_package_data(package_df_data: pd.Series):
    from git import Repo
    import uuid, shutil
    
    path = '{}{}/'.format('../data/', uuid.uuid4().hex)

    authors = {}
    result = ''
    base_line = '\n{};{};{};{}'.format(
        package_df_data['platform'],
        package_df_data['repo_id'],
        package_df_data['repo_stars'],
        package_df_data['repo_last_commit_date'],
    )

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
    
    for key, value in authors.items():
        result = '{}{};{};{};{}'.format(result, base_line, key, value['name'], value['commits'])
    
    return result


if __name__ == '__main__':
    output_file = '../data/django-packages-authors.csv'    
    df = dm.get_valid_dataframe()

    with open(output_file, 'a') as f:
        f.write('platform;repo_id;repo_stars;repo_last_commit_date;author_email;author_name;commits_count')

    for row in df.iterrows():
        with open(output_file, 'a') as f:
            f.write(get_package_data(row[1]))
        print('Done - {}'.format(row[1]['repo_id']))
