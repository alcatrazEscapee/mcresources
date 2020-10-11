#  Part of mcresources by Alex O'Neill
#  Work under copyright. Licensed under MIT
#  For more information see the project LICENSE file

import os

import setuptools

# Read README.md into the setuptools long description
with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Obtain version from environment variable
version = os.environ['VERSION']

setuptools.setup(
    name='mcresources',
    packages=['mcresources'],
    version=version,
    license='MIT',
    description='A Python Data Generator for Minecraft Modding',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Alex O\'Neill',
    author_email='alex@molleroneill.com',
    url='https://github.com/alcatrazEscapee/mcresources',
    keywords=['python', 'minecraft', 'resources', 'modding', 'forge'],
    install_requires=[],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',  # Define that your audience are developers
        'License :: OSI Approved :: MIT License',  # Again, pick a license
        'Programming Language :: Python :: 3.7',
    ],
)
