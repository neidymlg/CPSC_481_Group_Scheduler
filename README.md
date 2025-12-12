
---

# Group Chore Scheduler

This program uses Simulated Annealing to create a fair schedule of chores for a group of individuals based on their preferences. 

---

## Table of Contents

* [Overview](#overview)
* [Tech Stack](#tech-stack)
* [Features](#features)
* [Installation](#installation)
* [Running the Application](#running-the-application)
* [Project Structure](#project-structure)
* [Usage](#usage)
* [Troubleshooting](#troubleshooting)
* [License](#license)

---

## Overview

Dividing household chores fairly is a common challenge that often leads to imbalance or frustration among members, especially when schedules and preferences vary. Manually creating and maintaining a chore schedule is time-consuming and prone to inconsistency. This project addresses that problem by developing a system that collects member names, chore lists, availability and individual preferences to generate a balanced assignment automatically

---

## Tech Stack

* Python 3.8+
* Flask
* CSS
* Java Script

---

## Installation

### 1. Install Python

Ensure Python 3.8+ is installed:

```
python --version
```

### 2. Install Dependencies

Install Flask:

```
pip install flask
```

### 3. Clone the Repository

```
git clone <https://github.com/neidymlg/CPSC_481_Group_Scheduler.git>
```

To update an existing clone:

```
git pull
```

---

## Running the Application

### Start the Flask App

From the project root directory, run:

```
python api.py
```

(or `python3 api.py` depending on your environment)

### View the App in Your Browser

Once running, open:

```
http://127.0.0.1:5000/
```

### Stop the Server

Press:

```
Ctrl + C
```

in the terminal where the server is running.

---

## Project Structure

Example structure (update with your actual file names):

```
project/
│── static/
    |──index.html
    |──script.js
    |──style.css
|── api.pi
|──Group_Chore_Scheduler.py
│── README.md
|──unit_test.py
```

---

## Usage


Once the website is running, you should be able to:

* Enter inputs in the form (Name, capacity, chores, etc.)
* Click “Generate Schedule”
* View results on the output page

---

## Troubleshooting

Common issues and solutions:

* **Flask not found**: Reinstall using `pip install flask`
* **Port already in use**: Stop other running apps or change the port
* **Python not recognized**: Add Python to your system PATH

