import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="medley",
    version="1.0.2",
    author="Garret Bolthouse",
    author_email="garret@illumineinteractive.com",
    description="A simple, lightweight Python Dependency Injection Container (IOC), inspired by Pimple",
    long_description=long_description,
    url="https://github.com/illumine-interactive/medley",
    packages=['medley'],
    install_requires=['six'],
    python_requires='>=2.7',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
)
