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
      install_requires=["Flask>=1.0.2",
                        "Flask-RESTful>=0.3.7",
                        "Flask-SQLAlchemy>=2.3.2",
                        "SQLAlchemy>=1.3.1",
                        "Click>=7.0",
                        "jsonschema>=3.0.1",
                        "pytest>=5.4.1",
                        "pytest-cov>=2.8.1",
                        "ipython>=7.13.0",
                        "ipython-genutils>=0.2.0"
                        ]
      )
