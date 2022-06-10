# AC Backend Coding Test

## Installing

0. This requires Python 3.7 or later.
1. Fork this repo and clone it locally on your dev machine.
2. Install the necessary libraries with `pip install -r requirements.txt`. Use of a virtualenv or some other way of isolating library installations is strongly recommended.
2. Note that unlike a production Django repo, note that this comes with a local database checked in, `db.sqlite3`, with data already in it. There is no need to migrate or import any data.
3. Check that this runs OK with `./manage.py runserver`. A server should start on [http://localhost:8000/](http://localhost:8000/) and it should display "Hello, world" at that URL.

This app uses the Ariadne library for the graphql endpoint. If you are not familiar with it then check it out at [https://ariadnegraphql.org/](https://ariadnegraphql.org/) and familiarise yourself with how it works.

## The tasks

This Django app is a simple GraphQL API. The database is filled with data about countries of the world and their currencies. The structure of this data is detailed in `countries/models.py` and is quite simple.

If you open the database file `db.sqlite3` in a database editor, you will see the Country & Currency tables have been filled with data, as has the table for the many-to-many relation between them.

### Task 1

With the dev server running, go to: [http://localhost:8000/graphql/](http://localhost:8000/graphql/)

Enter the following query in the left hand panel:

```
query {
  countries {
    name
    symbol
    currencies {
      name
      symbol
    }
  }
}
```

And click the Play button. You should get a list of all countries currently in the database as a graphql response.

The function that resolves the query and produces this list is `resolve_countries` in `countries/schema.py`. It is relatively simple.

Now update the query to be:

```
query {
  countries(search:"aus") {
    name
    symbol
    currencies {
      name
      symbol
    }
  }
}
```

This will still, at the moment, provide a list of all countries. But we don't want that.

Task 1 is as follows: Update the code within `resolve_countries` so that, if a search term is provided, it optionally filters the list of countries to only include those with the search term in either its name _or_ its symbol. The search should be case-insensitive. If the search parameter is not provided, then list all countries.

So a search for `"aus"` should return a list containing Australia & Austria, while a search for `"gbr"` should return a list containing just the United Kingdom (symbol GBR) only:

![](/images/screenshot3.png)
![](/images/screenshot4.png)

### Task 2

The query for `resolve_countries` is inefficient: it is a classic case of the n+1 problem. If you check the terminal where your Django devserver process is running, you will see that we have the [nplusone](https://github.com/jmcarp/nplusone) monitor running and it is giving a lot of warnings like:

```
Potential n+1 query detected on `Country.currency_set`
```

Task 2 is as follows: Update the query within `resolve_countries` so that the n+1 problem is no longer an issue. The warnings in the log should disappear, and the total number of SQL queries made to the database should be constant no matter what the length of the list of countries returned is.

### Task 3

The data in the database is actually incomplete - it misses out a big chunk of countries (all those beginning with letters between M and T). It also contains a fictional country, Narnia, and its fictional currency, the Narnian Pound.

Luckily, there is an API with all the countries, and all the currencies, and the relation between them, in JSON format. The URLs are as follows:

* https://storage.googleapis.com/ac-dev-test-mock-api/countries.json
* https://storage.googleapis.com/ac-dev-test-mock-api/currencies.json

Open `countries/management/commands/syncdata.py` where the barebones of a function has been started. It can be run by running: `./manage.py syncdata` in the root project folder.

Task 3 is: write a function `sync_data` that queries the two endpoints above, and syncs the database table to the API so that:

1. Any currencies in the currencies API feed that are not in the currencies table, are added.
2. Any countries in the countries API feed that are not in the countries table, are added, and they are mapped to their currencies correctly.
3. Any countries & currencies not included in the feed - in this case Narnia & the Narnian pound - should be removed from the table.
4. Any countries or currencies in the API feeds that already exist in their respective table are updated, if the name has changed or a country's currencies have been added or removed.

Notes:

* You are permitted (and encouraged) to use third-party Python libraries for HTTP access if you prefer.
* Your code must handle the case where a temporary connection error or HTTP error means the API access fails. Ideally, it should log that an error has occurred, and return the correct exit code when run from the command line.

### Task 4

On the command line in a new terminal, run:

    pytest

This will call `countries/__tests__/test_graphql.py`, which runs a simple test of the graphql endpoint. It should pass.

However, the test needs completing. Firstly, the query given should have assertions on it to make sure the number of results returned is as expected, and the number of database queries is as efficient as possible.

Secondly, there should also be tests to make sure the filters work and are returning results for searching for `aus` and `gbr` (as illustrated above) correctly.

### Bonus tasks

I feel this should have taken up enough of your time, but if you wish to go further, you could add tests for the sync funciton in Task 3 as well to have the entire project's functionality covered.

You could also add capability to measure test coverage so that we know for sure every line of code has been tested, using a library of your choice.

### Finally

Save all you changes & push them to your forked version of this repository, and email us back the URL to your forked version. Do not file a pull request (or else other candidates will see your work).

# A quick note on my solution

## Structure

I have tried, as much as possible, to not change the structure that you have set up.
The only exceptions are as follows:

1. In the `Command` class of `syncdata.py`, I have added functions to allow different urls to be used. This was done so that I could send incorrect and blank urls in testing.
2. I did complete the bonus task and I've put the code for testing `syncdata.py` in a separate class in `test_syncdata.py`.

## pytest --cov

I did check that the coverage of my code was 100% with `pytest-cov`.
I have added this to requirements.txt, so once you are setup, you can check the coverage by running
`pytest --cov`.

## Notes

I have added notes throughout the code, which I hope will explain my thought process, as well as the function of the code.