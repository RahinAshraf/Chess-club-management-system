# Team Navy-R Small Group project

## Team members
The members of the team are:
- Name: Rahin Ashraf, ID: 20034059
- Name: Shmeelok Chakraborty, ID: 20040611
- Name: Avner Bensoussan, ID: 20013502
- Name: Adnan Salah, ID: 19066445
- Name: Xufeng Bai, ID: 20058729

*Add any further information about the team here, such as absent team members.*

## Project structure
The project is called `system`.  It currently consists of a single app `clubs`.

## Deployed version of the application
The deployed version of the application can be found at [https://powerful-ravine-37174.herokuapp.com](https://powerful-ravine-37174.herokuapp.com).

## Installation instructions
To install the software and use it in your local development environment, you must first set up and activate a local development environment.  From the root of the project:

```
$ virtualenv venv
$ source venv/bin/activate
```

Install all required packages:

```
$ pip3 install -r requirements.txt
```

Migrate the database:

```
$ python3 manage.py migrate
```

Seed the development database with (If a unique constraint occurs, unseed and then seed once again):

```
$ python3 manage.py seed
```

Run all tests with:
```
$ python3 manage.py test
```

*The above instructions should work in your version of the application.  If there are deviations, declare those here in bold.  Otherwise, remove this line.*

## Sources
The packages used by this application are specified in `requirements.txt`

*Declare are other sources here.*
