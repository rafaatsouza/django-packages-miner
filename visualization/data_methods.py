def get_full_dataframe():
    import pandas as pd
    return pd.read_csv('../data/django-packages.csv', sep=';')


def get_valid_dataframe():
    import re

    df = get_full_dataframe()
    
    categories = ['apps', 'frameworks']

    df = df[df['dp_category'].isin(categories)]    
    df = df[(df['has_valid_repo_url']) & (df['has_valid_repo'])]    
    df = df[(df['repo_has_readme']) & (df['repo_has_installed_app_ref'])]
    
    # 'wagtail/wagtail' and 'django-fluent/django-fluent.org' are content management 
    # systems built on Django which have a lot of packages and extensions
    cms_reg = re.compile(r'.*((cms)|(wagtail)|((django)\-(fluent))|((django)\-(cms))).*', re.IGNORECASE)
    
    df = df[~df['repo_id'].str.match(cms_reg, na=False)]
    df = df[~df['dp_grids'].str.match(cms_reg, na=False)]
    df = df[~df['repo_topics'].str.match(cms_reg, na=False)]

    # removed_packages = [
    #     'wooey/Wooey', # Django app that creates automatic web UIs for Python scripts
    #     'django/django', # Django framework
    #     'gunthercox/ChatterBot', # ML conversational dialog engine for creating chatbots
    #     'mirumee/saleor', # ecommerce platform built on Django
    # ]
    # df = df[~df['repo_id'].isin(removed_packages)]
    
    starts_median = 100 # np.median(np.array(df['repo_stars'].values))
    
    df = df[df['repo_stars'] >= starts_median]
    
    return df
