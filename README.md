# sz_log_parser
Parse a Senzing log with SQL debug logging enable and output stats

## Usage

```
$ ./sz_log_parser.py -h
usage: sz_log_parser.py [-h] [-t] file [file ...]

positional arguments:
  file

options:
  -h, --help        show this help message and exit
  -t, --debugTrace  output debug trace information
```

```
$ find /tmp/qa/ -name "*stdout*" | xargs ./sz_log_parser.py
```

