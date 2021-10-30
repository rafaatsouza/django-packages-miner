def get_packages(next):
    import requests
    next = next or '/?limit=100&offset=0'
    DJANGO_PACKAGES_BASE_URL = 'https://djangopackages.org'
    PACKAGES_ROUTE = '/api/v3/packages'

    url = '{}{}{}'.format(DJANGO_PACKAGES_BASE_URL, PACKAGES_ROUTE, next)

    offset = ' to offset {}'.format(next[next.rfind('=')+1:])
    print('Requesting packages{}...'.format(offset))
    packages_response = requests.get(url)
    packages_response.raise_for_status()
    print('Packages request successfully\n-----------')

    json_response = packages_response.json()

    objects = json_response['objects']
    next_request = json_response['meta'].get('next') or ''
    
    return objects, next_request.replace(PACKAGES_ROUTE, '')


def treat_grids(grids):
    if not grids:
        return ''
    grid_value = ''
    for grid in grids:
        grid_value = '{},{}'.format(grid_value, grid.replace('/api/v3/grids/', '').replace('/', ''))
    return grid_value


def treat_category(category):
    if not category:
        return ''
    return category.replace('/api/v3/categories/', '').replace('/','')


def get_csv_line_by_package(package):
    line_template = '{};{};{};{};{};{};{};{};{};{}'

    return line_template.format(package['created'],
        package['modified'] if package['modified'] else '',
        package['slug'] if package['slug'] else '',
        package['title'] if package['title'] else '',
        treat_category(package['category']),
        package['documentation_url'] if package['documentation_url'] else '',
        treat_grids(package['grids']),
        package['repo_url'] if package['repo_url'] else '',
        package['repo_watchers'] if package['repo_watchers'] else '',
        package['usage_count'] if package['usage_count'] else ''
    )


if __name__ == '__main__':
    import os

    with open('django-packages.csv', 'a') as f:
        f.write('created;modified;slug;title;category;documentation_url;grids;repo_url;repo_watchers;usage_count\n')

    packages_remaining = True
    next = None

    while packages_remaining:
        packages, next = get_packages(next)
        packages_remaining = len(next) > 0
        with open('django-packages.csv', 'a') as f:
            for package in packages:
                f.write(get_csv_line_by_package(package) + '\n')