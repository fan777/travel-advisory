# Capstone-1 : Travel Advisory

Demo @ https://travel-advisory.herokuapp.com/

---

## Table of Contents
- [1. About The Project](#about-the-project)
- [2. Objectives](#objectives)
- [3. Getting Started](#getting-started)
  * [Prerequisites](#prerequisites)
  * [Installation](#installation)
  * [Known Issues](#known-issues)
- [4. Schema](#schema)
- [5. User Flow](#user-flow)
- [6. Data](#data)
- [7. Additional Resources](#additional-resources)
- [8. Future Considerations](#future-considerations)

---

## About The Project

Global travel is not without perils.  This project aggregates data from a variety of APIs to construct a cohesive site presenting useful travel information (with up to date advisories and COVID trends) to help a visitor determine if a destination is safe.

## Objectives

* Allows a visitor to view country advisories for travel planning
* Allows an authenticated visitor to bookmark countries

## Getting Started

  * ### Prerequisites
    * Postgresql installation
    * Python 3.8.5
    * Create an account with [Tugo](https://developer.tugo.com/) to register for a free API Key
  * ### Installation
    * Clone the repository
    * Create empty database 'travel' and run seed.py
    * Set up venv and install dependencies from requirements.txt
  * ### Known Issues
    * The APIs used may occasionally go down or have such slow response triggering a timeout
    * The APIs used may not have data for all countries

## Schema

* Table for users containing username, password, and email
* Tables for countries, languages, and currencies
* Country + language mapping table (when a country has more than one widely used language)
* Country + currency mapping table (when a country has more than one widely used currency)

## User Flow

1. On the entry homepage, the user is presented with a list of countries.
2. The user may also search for a country from the navbar search box by typing in a country code or country name.
3. A valid country entry will direct the user to a page with travel advisories and COVID statistics.
4. Additional country information such as languages and currencies will also be presented.
5. A user may create an account or login with an existing account.
6. A valid account will present options to bookmark countries and show those countries on the entry homepage.

## Data

* [Tugo](https://developer.tugo.com/) - Travel Safe API
* [Travel-Advisory.info](https://www.travel-advisory.info/) - Advisory levels API
* [disease.sh](https://disease.sh/) - COVID data and historical counts
* [restcountries.eu](http://restcountries.eu/) - Global country list and basic data

## Additional Resources

* [Chart.js](https://www.chartjs.org/) - Generate graphs from data
* [Boostrap 5.0](https://getbootstrap.com/) - Layout and design
* [Font Awesome](https://fontawesome.com/) - Icons

## Future Considerations

Chart.js is useful and powerful however my implementation is kludging Javascript into HTML with Jinja variables.  To separate responsibilities, the script can be offloaded as a function in a JS file and the canvas can call the function on load, passing in the data as variables.  

Finally, since this project relies on so many external APIs with limited or inconsistent behavior, it may be worthwhile exercise to develop a scraper and gather the data directly from government sites (US state department, CIA world factbook, etc) to generate one's own set of data.