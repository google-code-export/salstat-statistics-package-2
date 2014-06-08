from distutils.core import setup
setup(name='imagenes',
      version= '0.1',
      py_modules=['imagenes'],
      description='Images library',
      author='Sebastian Lopez, S2 Team',
      author_email='selobu@gmail.com',
      url='http://code.google.com/p/salstat-statistics-package-2',
      packages=['imagenes',],
      requires=['wx (>=2.9.4)','numpy (>=1.6.0)','sqlalchemy (>=0.7.9)'],
      )
