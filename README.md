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

## Load hours

```bash
tt load [OPTIONS]
```

or

```bash
tt load-csv [OPTIONS] CSV_FILE
```

### Examples

* Load your today hours

```bash
$ tt load -t "I did something awesome today"
Success!
```

* Load hours from 3 days ago

```bash
$ tt load -t "I did something awesome" -d "3 days ago"
Success!
```

* Load 6.5 hours for last friday

```bash
$ tt load -t "I did something awesome" -d friday -h 6.5
Success!
```

* Load hours from a csv file

```bash
$ tt load-csv hours_to_load.csv
Success!
```

## Show loaded hours

```bash
tt show [OPTIONS]
```

### Examples 

* Show your current month loaded hours

```bash
$ tt show
Start: 01/05/2019, End: 02/05/2019
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
Start: 01/05/2019, End: 02/05/2019
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
Start: 28/04/2019, End: 01/05/2019  
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

* Show your loaded hours from a single date. Several languages supported.

```bash
$ tt show -d martes
Start: 28/04/2019, End: 28/04/2019  
+------------+-----------------------------------------------------------------+
|    Date    |                           Description                           |
+------------+-----------------------------------------------------------------+
| 28/05/2019 |              BURNS-4210 I slept all day long                    |
+------------+-----------------------------------------------------------------+

$ tt show -w -d quarta-feira
Start: 29/04/2019, End: 29/04/2019  
+------------+-----------------------------------------------------------------+
|    Date    |                           Description                           |
+------------+-----------------------------------------------------------------+
| 29/04/2019                      BURNS-4283 I missed March                    |
+------------+-----------------------------------------------------------------+
```
