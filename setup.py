from setuptools import find_packages, setup

setup(
    name='Invoice_Extraction_app',
    version='0.0.1',
    author='coker richard',
    author_email='richardaypdeji91@gmail.com',
    install_requires=['openai','langchain','streamlt','python-dotenv','PyPDF2'],
    packages=find_packages()
    )