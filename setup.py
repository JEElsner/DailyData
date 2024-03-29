import versioneer

from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as readme:
    long_description = readme.read()

setup(
    name='DailyData',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author='Jonathan Elsner',
    author_email='jeelsner@outlook.com',
    description='A package for recording and reviewing data about your day',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/JEElsner/DailyData/',
    packages=find_packages(),
    install_requires=['ConsoleQuestionPrompts',
                      'python-docx', 'pandas', 'numpy'],
    entry_points={
        'console_scripts': [
            'timelog=DailyData.time_management.timelog:timelog_entry_point',
            'dailydata=DailyData.__main__:take_args'
        ]
    },
    include_package_data=True,
    python_requires='>=3.6'
)
