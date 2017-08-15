from setuptools import setup, find_packages

setup(name = 'bokodapviewer',
      version = '0.1.2',
      description = 'A simple OpenDAP data viewer based on the Bokeh visualisation library',
      author = 'Systems Engineering & Assessment Ltd.',
      author_email = 'Marcus.Donnelly@sea.co.uk',
      url = 'https://bitbucket.org/sea_dev/bokodapviewer',
      license = 'MIT',
      classifiers = ['Development Status :: 3 - Alpha',
                     'Intended Audience :: Science/Research',
                     'License :: OSI Approved :: MIT License',
                     'Programming Language :: Python :: 3',
                     'Topic :: Scientific/Engineering'
                     ],
      keywords = ['OpenDAP',
                  'Bokeh',
                  'Environment',
                  'Science'
                  ],
      packages = find_packages(),
      install_requires = ['numpy >= 1.13',
                          'tornado == 4.5',
                          'bokeh >= 0.12.6',
                          'sodapclient >= 0.1.0',
                          'bokcolmaps >= 0.3.0'
                          ],
      package_data = {'bokodapviewer':['Config.xml'],
                      },
      )
