from setuptools import setup, find_packages

# Stub for a package setup file. This needs to be completed to make a package
# out of this project.
#
# Read these resources to finish it dunderhead:
# https://packaging.python.org/tutorials/packaging-projects/
# https://packaging.python.org/key_projects/#setuptools
# https://github.com/pypa/sampleproject/blob/master/setup.pys

setup(
    name='DailyData',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},  # Specify that the package is in the 'src' folder
    install_requires=['ConsoleQuestionPrompts', 'python-docx'],
    include_package_data=True
)
