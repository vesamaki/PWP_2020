from setuptools import find_packages, setup

setup(
    name="cyequ",
    version="0.1.0",
    # package_dir must be included with 'src' superfolder for package
    # Courtesy of https://github.com/pypa/setuptools/issues/1571
    package_dir={'': 'src'}, 
    # Include where='src' to find packages under src-folder
    packages=find_packages(where='src'), 
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "flask",
        "flask-restful",
        "flask-sqlalchemy",
        "SQLAlchemy",
    ]


