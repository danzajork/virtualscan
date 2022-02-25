# virtualscan
This tool is a virtual host scanner that can be used to detect vhost hopping.



## virtualscan

### Requirements
```sh
Python 3
pip
```

### Installing Python Requirements
```sh
pip install -r requirements.txt
```

### Usage information

```console
% python3 main.py 
usage: main.py [-h] [-u URL] [-w WORD_LIST] [-t THREADS] [-o OUTPUT]

optional arguments:
  -h, --help            show this help message and exit
  -u URL, --url URL     url to target
  -w WORD_LIST, --word-list WORD_LIST
                        custom word list
  -t THREADS, --threads THREADS
                        number of threads
  -o OUTPUT, --out OUTPUT
                        file to output json
```