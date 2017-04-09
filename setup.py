from setuptools import setup, find_packages


setup(
    name="void",
    packages=find_packages(exclude=["tests"]),
    version="0.0.0",
    license="MIT License",
    description="Render HTML content from Markdown source",
    author="Clay McClure <clay@daemons.net>",
    author_email="clay@daemons.net",
    url="https://github.com/claymation/void",
    keywords=["markup", "markdown"],
    entry_points={
        "console_scripts": [
            "void = void.void:main",
        ]
    },
    install_requires=[
        "awesome-slugify",
        "CommonMark",
        "Jinja2",
    ],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Documentation",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Documentation",
        "Topic :: Text Processing :: Markup",
        "Topic :: Utilities"])
