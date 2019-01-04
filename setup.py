import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="webscrap",
    version="0.1.0",
    author="Yoram de Langen",
    author_email="yoramdelangen@gmail.com",
    description="A configurable webscraper",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yoramdelangen/webscrap",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
