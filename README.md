# Time tracker

> Load and show your hours in [TimeTracker](https://timetracker.bairesdev.com) with just a command line.

## Install

    pip install timetracker-cli

## Config file

Edit configuration file in ~/.timetracker/config.toml

```toml
[credentials]
username = 'Homer.Simpson'
password = 'do.it.for.her'

[options]
project = 'Springfield Nuclear Power Plant'
assignment = 'Nuclear Safety Inspection'
focal = 'Mr. Burns'
hours = 6
```

## Usage

```bash
tt load [OPTIONS]
```

```
tt show [OPTIONS]
```

### Examples

* Load your today hours

```bash
$ tt load -t "I did something awesome today"
Success!
```

* Load hours from 3 days ago

```
$ tt load -t "I did something awesome" -d "3 days ago"
Success!
```

* Load 6.5 hours for last friday

```
$ tt load -t "I did something awesome" -d friday -h 6.5
Success!
```

* Show your current month loaded hours

```bash
$ tt show
Start: 01/05/2019, 02/05/2019
+------------+-----------------------------------------------------------------+
|    Date    |                           Description                           |
+------------+-----------------------------------------------------------------+
| 01/05/2019 |           BURNS-4765 I pressed a button in the board            |
+------------+-----------------------------------------------------------------+
| 02/05/2019 |              BURNS-4678 I slept all day long                    |
+------------+-----------------------------------------------------------------+
```

* Show your current month loaded hours with weekdays

```bash
$ tt show -w
Start: 01/05/2019, 02/05/2019
+---------+------------+-----------------------------------------------------------------+
| Weekday |    Date    |                           Description                           |
+---------+------------+-----------------------------------------------------------------+
|    W    | 01/05/2019 |           BURNS-4765 I pressed a button in the board            |
+---------+------------+-----------------------------------------------------------------+
|   TH    | 02/05/2019 |              BURNS-4678 I slept all day long                    |
+---------+------------+-----------------------------------------------------------------+
```

* Show your loaded hours from a range of time

```bash
$ tt show -s "4 days ago" -e yesterday
Start: 28/04/2019, 01/05/2019  
+------------+-----------------------------------------------------------------+
|    Date    |                           Description                           |
+------------+-----------------------------------------------------------------+
| 28/05/2019 |              BURNS-4210 I slept all day long                    |
+------------+-----------------------------------------------------------------+
| 29/04/2019                      BURNS-4283 I missed March                    |
+------------+-----------------------------------------------------------------+
| 30/04/2019 |       BURNS-4763 I actually stayed at Moe's Tabern but          |
+------------+-----------------------------------------------------------------+
| 01/05/2019 |           BURNS-4765 I pressed a button in the board            |
+------------+-----------------------------------------------------------------+
```