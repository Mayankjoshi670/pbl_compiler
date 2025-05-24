from setuptools import setup, find_packages

# Read the contents of your README file
with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name="gehu",
    version="1.3.1",  # Increment this if you're making changes and want to re-upload
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'gehu=gehu:main',
        ],
    },
    description="A simple Python package that helps you find and execute commands using AI.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="Pim Verleg",
    author_email="pim_iets@hotmail.com",
    license="MIT",
    install_requires=[
        'google-generativeai>=0.3.0',
        'python-dotenv>=0.19.0',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
