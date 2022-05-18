import requests

from django_packages import DjangoPackagesProvider


class DjangoPackagesApiProvider(DjangoPackagesProvider):
    _DJANGO_PACKAGES_BASE_URL = 'https://djangopackages.org'
    _PACKAGES_ROUTE = '/api/v3/packages'
    _OFFSET = 100

    def get_packages(self, next=None):

        next = next or '/?limit={}&offset=0'.format(self._OFFSET)

        url = '{}{}{}'.format(self._DJANGO_PACKAGES_BASE_URL, self._PACKAGES_ROUTE, next)

        packages_response = requests.get(url)
        packages_response.raise_for_status()
        
        json_response = packages_response.json()

        packages = [self.__get_package_info_by_obj(pkg) for pkg in json_response['objects']]
        next_request = json_response['meta'].get('next')
        
        return (
            packages, 
            (next_request.replace(self._PACKAGES_ROUTE, '') if next_request else None)
        )


    def get_package_by_id(self, id):

        url = '{}{}/{}'.format(self._DJANGO_PACKAGES_BASE_URL, self._PACKAGES_ROUTE, id)
        
        package_response = requests.get(url)
        package_response.raise_for_status()
        
        return self.__get_package_info_by_obj(package_response.json())


    def __get_package_info_by_obj(self, obj):
        return {
            'slug': obj['slug'] if obj['slug'] else '',
            'category': self._treat_category(obj['category']) if obj['category'] else '',
            'grids': self._treat_grids(obj['grids']) if obj['grids'] else '',
            'repo_url': obj['repo_url'] if obj['repo_url'] else '',
            'usage_count': obj['usage_count'] if obj['usage_count'] else 0
        }


    def _treat_grids(self, grids):
        if not grids:
            return ''
        grid_value = ''
        for grid in grids:
            if grid_value == '':
                grid_value = grid.replace('/api/v3/grids/', '').replace('/', '')
            else:
                grid_value = '{},{}'.format(grid_value, grid.replace('/api/v3/grids/', '').replace('/', ''))
        return grid_value


    def _treat_category(self, category):
        if not category:
            return ''
        return category.replace('/api/v3/categories/', '').replace('/','')
