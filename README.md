# Time tracker

> Load your hours in [TimeTracker](http://timetracker.bairesdev.com) with just a command line.

## Install

    pip install --no-binary -e .

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
load-tt [OPTIONS]
```

### Examples

* Load your today hours

```bash
load-tt -t "I did something awesome today"
```

* Load hours from yesterday

```bash
load-tt -t "I did something awesome" -d yesterday
```

* Load hours from 3 days ago

```bash
load-tt -t "I did something awesome" -d "3 days ago"
```

* Load hours for last monday

```bash
load-tt -t "I did something awesome" -d monday
```
