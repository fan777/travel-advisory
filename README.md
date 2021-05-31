# Capstone-1 : Travel Advisory

Demo @ https://travel-advisory.herokuapp.com/

## Table of Contents
- [1. About The Project](#about-the-project)
- [2. Objectives](#objectives)
- [3. Getting Started](#getting-started)
  * [Prerequisites](#prerequisites)
  * [Known Issues](#known-issues)
- [4. Schema](#schema)
- [5. User Flow](#user-flow)


## About The Project

Global travel is not without perils.  This project aggregates data from a variety of APIs to construct a cohesive site presenting useful travel information (with up to date advisories and COVID trends) to help a visitor determine if a destination is safe.

## Objectives

* Allows a visitor to view country advisories for travel planning
* Allows an authenticated visitor to bookmark countries

## Getting Started
* Prerequisites

* 

## Known Issues

* The APIs used may occasionaly be down or slow response may trigger timeout

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

# 