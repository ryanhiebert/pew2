from setuptools import setup

setup(
    name='pew',
    version='0.1',
    description='Tools to manage virtual environments',
    author='Ryan Hiebert',
    author_email='ryan@ryanhiebert.com',
    url='https://github.com/ryanhiebert/pew2',
    license='MIT License',
    py_modules=['pew'],
    install_requires=[
        'setuptools>=0.7',
        'click>=3',
        'pathlib>=1.0.1',
    ],
    entry_points={'console_scripts': ['pew = pew:pew']},
    classifiers=[
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
        'Environment :: Console',
        'Private :: Do Not Upload',
    ]
)
