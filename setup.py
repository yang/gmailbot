from setuptools import setup

setup(
    name='gmailbot',
    version='1.0',
    packages=['gmailbot'],
    url='https://github.com/yang/gmailbot',
    license='AGPL',
    author='yang',
    author_email='',
    entry_points={
      'console_scripts': [
        'gmailbot = gmailbot:main',
      ]
    },
    description='Gmail automation',
    install_requires=[
      # The 'security' extra is to deal with SSL errors.  See
      # <http://stackoverflow.com/a/30438722/43118>.
      'google-api-python-client==1.5.2',
  ]
)