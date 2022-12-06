from distutils.core import setup

name = "Test_Reporting"

setup(name=name,
      version="1.1",
      description="Project for publishing report pages related to validation tests.",
      url="https://gitlab.euclid-sgs.uk/bgilles/test_reporting",
      author="Bryan R. Gillis",
      author_email="bgillis@roe.ac.uk",
      scripts=["python/Test_Reporting/build_all_report_pages.py",
               "python/Test_Reporting/build_report.py",
               "python/Test_Reporting/pack_results_tarball.py"],
      packages=[name, f"{name}.specializations", f"{name}.testing", f"{name}.utility"],
      package_dir={name: "python/Test_Reporting",
                   f"{name}.specializations": "python/Test_Reporting/specializations",
                   f"{name}.testing": "python/Test_Reporting/testing",
                   f"{name}.utility": "python/Test_Reporting/utility", },
      )
