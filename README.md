# djattendance

[![Build Status](https://travis-ci.org/attendanceproject/djattendance.svg?branch=dev)](https://travis-ci.org/attendanceproject/djattendance) [![Coverage Status](https://coveralls.io/repos/attendanceproject/djattendance/badge.png?branch=dev)](https://coveralls.io/r/attendanceproject/djattendance?branch=dev)

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)


## Summary
djattendance is a rewrite of the original PHP attendanceproj in Python/Django. It supports many internal functions of the [FTTA](ftta.org), for both trainees and administrators, such as:
* Attendance
* Service Scheduling
* Life-studies
* Class Syllabi
* Exams & Grading
* Room Reservations
* etc.

## Architecture
The original attendance server was based on a traditional LAMPstack. The new version is written in Python using the Django web framework with a PostgreSQL backend. On the front-end we use Bootstrap and in some places, ReactJS.

### Apps (modules)
Django modularizes a projects components into 'apps' which allow users to separate different aspects or features of their application. Logically distinct features are contained within their own app and namespace (e.g. `attendance`, `leaveslips`, `lifestudies`), but we also have several 'core' apps that comprise the basic data model shared across the whole project (e.g. `accounts`, `houses`, `teams`, etc.).

### Third-party packages
We rely on a number of third-party Django apps to provide major functionality. Most notably: [django-suit](djangosuit.com/) (to skin the admin site), and [django rest framework](http://www.django-rest-framework.org/) (for API creation).

## Contributing
We welcome any contributions. Please get in touch with the [project owners](https://github.com/orgs/attendanceproject/teams/owners) and also review the [Contributor Guidelines](https://github.com/attendanceproject/djattendance/wiki/Contributor-Guidelines) page on the wiki.

### Bootstrapping
A more detailed guide to running djattendance on your local machine can be found in the [wiki](https://github.com/attendanceproject/djattendance/wiki/Development-Environment). A Unix environment is preferred (OS X, Ubuntu), and for Windows users, [Vagrant]() is the most ideal option.
