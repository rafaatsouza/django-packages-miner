import pandas as pd
import networkx as nx

def get_dataframe():
    filepath = '../data/django-packages-authors.csv'
    df = pd.read_csv(filepath, sep=';')
    df = df[df['author_email'].str.contains('dependabot') == False]
    df = df[df['author_email'].str.contains('noreply') == False]
    df = df[df['author_email'].str.contains('no.reply') == False]
    df = df[df['author_email'].str.contains('no-reply') == False]
    df = df[df['author_email'].str.contains('no author') == False]
    return df[df['author_email'].str.contains('github') == False]


def get_common_authors(df):
    g = df.groupby(['author_email'], as_index = False).agg({'repo_id': '<>'.join})
    g[g['repo_id'].str.contains('<>')]

    authors = {}
    for row in g.iterrows():
        package = row[1]
        repos = package['repo_id'].split('<>')
        if package['author_email'] in authors:
            authors[package['author_email']] = authors[package['author_email']] + repos
        else:
            authors[package['author_email']] = repos

    return authors


if __name__ == '__main__':
    df = get_dataframe()
    authors = get_common_authors(df)
    g = nx.Graph()

    for row in df.iterrows():
        package = row[1]
        if package['repo_id'] not in g.nodes:
            g.add_nodes_from([
                (package['repo_id'], {
                    'platform': package['platform'], 
                    'stars': int(package['repo_stars']),
                    'last_commit_date': package['repo_last_commit_date']
                })])
    
    for _, repos in authors.items():
        if len(repos) >= 2:
            for i in range(len(repos)):
                for j in range(i + 1, len(repos)):
                    g.add_edge(repos[i], repos[j])

    nx.draw(g)
    
