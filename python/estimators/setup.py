from setuptools import setup


setup(name='estimators',
      version='0.1',
      packages=['models'],
      package_dir={'models': 'estimators/models'},
      install_requires=[
          # genetic
          'deap',
          # lint
          'flake8',
          'keras',
          # plotting
          'matplotlib',
          'numpy',
          # bayesian net
          'pomegranate',
          'pytest',
          'scipy',
          'scikit-learn',
          'sklearn-genetic',
          'tensorflow'],
      python_requires='>=3.5')
