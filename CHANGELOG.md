# Changelog

## [1.3.0] - 2021-02-16
- Add `tt load-csv` utility to load hours from a csv file.

## [1.2.0] - 2019-10-29
- Add `-d, --date` option for `tt show` command, in order to check just loaded hours for that date.
- Disable SSL warnings when timetracker's domain has certificate issues.
- Drop Python 3.4 support.

## [1.1.0] - 2019-05-31
- Add `-h, --hours` option to set hours using cli.    

## [1.0.0] - 2019-05-24
- `tt` is now the only one true command line that groups all utilities.
    - `tt load` is the new utility to load hours. It does pretty much the same as `load-tt` (which was deleted).
    - `tt show` is the new utility to shows loaded hours. It supports several params, please refer to `--help` for more information. 
- dd/mm/yyyy is the default date format to use.   

## [0.2.1] - 2019-02-19
- Change base url since timetracker.bairesdev.com is now using https protocol.  

## [0.2.0] - 2018-12-18
- Add pto and vacations support.
- Fix date bug for `today` and `yesterday` when timezone time is a day after utc time.

## [0.1.2] - 2018-11-23
- Fix some date parse stuff and update readme.

## [0.1.1] - 2018-10-29
- Drop support for dates with math notation `-d today-2`.
- Add human date support, now you can use `-d monday` for the last monday.

## [0.1.0] - 2018-03-01
- Basic timetracker with date and text support.
