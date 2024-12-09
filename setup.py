from setuptools import setup, find_packages

setup(name='bokodapviewer',
      version='0.5.0',
      description='A simple OpenDAP data viewer based on the Bokeh visualisation library',
      author='Marcus Donnelly',
      author_email='marcus.k.donnelly@gmail.com',
      url='https://github.com/marcuskd/bokodapviewer',
      license='BSD 3-Clause',
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Science/Research',
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python :: 3',
                   'Topic :: Scientific/Engineering'
                   ],
      keywords=['OpenDAP',
                'Bokeh',
                'Environment',
                'Science'
                ],
      packages=find_packages(),
      install_requires=['numpy >= 1.23',
                        'bokeh >= 3',
                        'bokcolmaps >= 3',
                        'sodapclient >= 0.2.1'
                        ],
      include_package_data=True,
      )
