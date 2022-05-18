import os

from django_packages_api import DjangoPackagesApiProvider
from django_packages_dataframe import DjangoPackagesDataFrameProvider
from django_packages import DjangoPackagesProvider

class DjangoPackagesProviderFactory:

    @staticmethod
    def build(file_path=None) -> DjangoPackagesProvider:
        return (
            DjangoPackagesDataFrameProvider(file_path) 
            if file_path and os.path.exists(file_path) 
            else DjangoPackagesApiProvider()
        )
