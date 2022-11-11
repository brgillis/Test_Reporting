from distutils.core import setup

name = "Test_Reporting"

setup(name=name,
      version="1.0",
      description="Project for publishing report pages related to validation tests.",
      url="https://gitlab.euclid-sgs.uk/bgilles/test_reporting",
      author="Bryan R. Gillis",
      author_email="bgillis@roe.ac.uk",
      copyright="Copyright (C) 2012-2020 Euclid Science Ground Segment",
      packages=[name, f"{name}.specializations", f"{name}.testing", f"{name}.utility"],
      package_dir={name: "python",
                   f"{name}.specializations": "python/specializations",
                   f"{name}.testing": "python/testing",
                   f"{name}.utility": "python/utility", },
      zip_safe=False,
      setup_requires=['setuptools',
                      'numpy==1.20.3'],
      install_requires=['numpy==1.20.3'],
      )
