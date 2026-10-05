from setuptools import setup, find_packages

setup(
    name="nao_eddy_mean_flow_feedback",
    version="1.0.0",
    packages=find_packages(include=["src", "src.*"]),
    python_requires=">=3.12",
)
