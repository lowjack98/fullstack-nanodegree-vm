# Item Catalog Project:

This is a Python web application that provides a list of items within a
variety of categories and integrates Google+ Auth user registration and
authentication. Authenticated users have the ability to post, edit, and
delete their own items. It also uses an SQLite database to keep
track of all categories and items.

## Products
- [SQLite database][1]

## Language
- [Python][2]

## Dependencies
- [flask][3]
- [Google+ Auth][4]
- [httplib2][5]
- [oauth2client][6]
- [sqlalchemy][7]
-


[1]: https://www.sqlite.org
[2]: https://python.org
[3]: http://flask.pocoo.org
[4]: https://developers.google.com/identity/protocols/OAuth2
[5]: https://pypi.python.org/pypi/httplib2
[6]: https://oauth2client.readthedocs.io/en/latest/
[7]: http://docs.sqlalchemy.org



# Setup

- Fork to 'https://github.com/lowjack98/fullstack-nanodegree-vm.git', so that
you have a version of your own within your Github account

- Next, clone to your local server running python.

- To setup and add initial data to the database
 run: `python initialize_db.py` from the catalog folder.

- Finally to run the application
 run: `python application.py` from the catalog folder.

- Access and test your application by visiting http://localhost:5000 locally on your browser.
