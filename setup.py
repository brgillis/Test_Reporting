from distutils.core import setup

name = "Test_Reporting"

setup(name=name,
      version="1.0",
      description="Project for publishing report pages related to validation tests.",
      url="https://gitlab.euclid-sgs.uk/bgilles/test_reporting",
      author="Bryan R. Gillis",
      author_email="bgillis@roe.ac.uk",
      packages=[name, f"{name}.specializations", f"{name}.testing", f"{name}.utility"],
      package_dir={name: "python",
                   f"{name}.specializations": "python/specializations",
                   f"{name}.testing": "python/testing",
                   f"{name}.utility": "python/utility", },
      )
