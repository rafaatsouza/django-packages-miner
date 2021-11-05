import requests

class DjangoPackagesApi:
    _DJANGO_PACKAGES_BASE_URL = 'https://djangopackages.org'
    _PACKAGES_ROUTE = '/api/v3/packages'

    def _get_packages_by_response(self, json_response):
        objects = json_response['objects']
        packages = []

        for pkg in objects:
            packages.append({
                'created': pkg['created'] if pkg['created'] else '',
                'slug': pkg['slug'] if pkg['slug'] else '',
                'title': pkg['title'] if pkg['title'] else '',
                'category': _treat_category(pkg['category']) if pkg['category'] else '',
                'documentation_url': pkg['documentation_url'] if pkg['documentation_url'] else '',
                'grids': _treat_grids(pkg['grids']) if pkg['grids'] else '',
                'repo_url': pkg['repo_url'] if pkg['repo_url'] else '',
                'repo_watchers': pkg['repo_watchers'] if pkg['repo_watchers'] else '',
                'usage_count': pkg['usage_count'] if pkg['usage_count'] else 0
            })
        
        return packages


    def get_packages(self, next, logger=None):

        next = next or '/?limit=100&offset=0'

        url = '{}{}{}'.format(self._DJANGO_PACKAGES_BASE_URL, self._PACKAGES_ROUTE, next)

        offset = ' to offset {}'.format(next[next.rfind('=')+1:])
        
        if logger:
            logger.info('Requesting packages for offset {}...'.format(offset))

        packages_response = requests.get(url)
        packages_response.raise_for_status()
        
        if logger:
            logger.info('Packages request successfully for offset {}.'.format(offset))

        json_response = packages_response.json()

        packages = self._get_packages_by_response(json_response)
        next_request = json_response['meta'].get('next') or ''
        
        return packages, next_request.replace(PACKAGES_ROUTE, '')


    def get_package(self, id_package, logger=None):

        url = '{}{}/{}'.format(self._DJANGO_PACKAGES_BASE_URL, self._PACKAGES_ROUTE, id_package)
        
        if logger:
            logger.info('Requesting package {}...'.format(id_package))

        package_response = requests.get(url)
        package_response.raise_for_status()
        
        if logger:
            logger.info('Package {} request successfully.'.format(id_package))

        pkg = package_response.json()

        return {
            'created': pkg['created'] if pkg['created'] else '',
            'slug': pkg['slug'] if pkg['slug'] else '',
            'title': pkg['title'] if pkg['title'] else '',
            'category': _treat_category(pkg['category']) if pkg['category'] else '',
            'documentation_url': pkg['documentation_url'] if pkg['documentation_url'] else '',
            'grids': _treat_grids(pkg['grids']) if pkg['grids'] else '',
            'repo_url': pkg['repo_url'] if pkg['repo_url'] else '',
            'repo_watchers': pkg['repo_watchers'] if pkg['repo_watchers'] else '',
            'usage_count': pkg['usage_count'] if pkg['usage_count'] else 0
        }


def _treat_grids(grids):
    if not grids:
        return ''
    grid_value = ''
    for grid in grids:
        if grid_value == '':
            grid_value = grid.replace('/api/v3/grids/', '').replace('/', '')
        else:
            grid_value = '{},{}'.format(grid_value, grid.replace('/api/v3/grids/', '').replace('/', ''))
    return grid_value


def _treat_category(category):
    if not category:
        return ''
    return category.replace('/api/v3/categories/', '').replace('/','')
