import pandas as pd

from django_packages import DjangoPackagesProvider

class DjangoPackagesDataFrameProvider(DjangoPackagesProvider):

    _OFFSET = 5

    def __init__(self, dataframe_file_path):
        self.dataframe = pd.read_csv(dataframe_file_path, sep=';')
        self.size = len(self.dataframe)


    def get_packages(self, next=None):
        range_start = 0 if not next else next - self._OFFSET
        range_end = min(self._OFFSET if not next else next, self.size)
        
        rows = self.dataframe.iloc[range_start:range_end]
        packages = [self.__get_package_info_by_series(r[1]) for r in rows.iterrows()]

        return packages, (range_end + self._OFFSET if range_end < self.size else None)


    def get_package_by_id(self, id):
        df = self.dataframe
        row = df[df['repo_id'] == id][:1]
        return [self.__get_package_info_by_series(r[1]) for r in row.iterrows()][0]


    def __get_package_info_by_series(self, series: pd.Series):
        return {
            'slug': series['dp_slug'] if not pd.isna(series['dp_slug']) else '',
            'category': series['dp_category'] if not pd.isna(series['dp_category']) else '',
            'grids': series['dp_grids'] if not pd.isna(series['dp_grids']) else '',
            'repo_url': series['dp_repo_url'] if not pd.isna(series['dp_repo_url']) else '',
            'usage_count': series['dp_usage_count'] if not pd.isna(series['dp_usage_count']) else 0
        }
