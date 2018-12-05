from setuptools import setup, find_packages


with open("requirements.txt") as f:
    requirements = f.read().splitlines()
with open("README.md") as f:
    long_description = f.read()


setup(
    name='base_astro_bot',
    version='1.2.2',
    description='Base bot class for Star Citizen players',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/Mirdalan/base_astro_bot',
    author='Michal Chrzanowski',
    author_email='michrzan@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',

        'Intended Audience :: Developers',
        'Topic :: Games/Entertainment',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='star citizen discord spectrum bot',
    install_requires=requirements,
    extras_require={
        ':sys_platform == "win32"': [
            'websocket-client==0.46.0'
        ],
        ':"linux" in sys_platform': [
            'websocket-client==0.44.0'
        ]
    },
    packages=find_packages(exclude=('tests',)),
    include_package_data=True,
    python_requires='~=3.5',
)
