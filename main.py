#!/usr/bin/python3
import sys
import os
import tldextract
import requests
from tqdm import tqdm
from argparse import ArgumentParser

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BUILT_IN_WORD_LIST = "wordlist/list.txt"

def build_wordlist(url, words):
    word_list = []

    extracted_result = tldextract.extract(url)
    full_domain = f"{extracted_result.subdomain}.{extracted_result.domain}.{extracted_result.suffix}"
    apex_domain = f"{extracted_result.domain}.{extracted_result.suffix}"

    for word in words:
        if "%s" in word:
            final_word = word.replace("%s", apex_domain)
            word_list.append(final_word)
        else:
            word_list.append(f"{word}.{full_domain}")

    return word_list

def scan(url, words):

    word_list = build_wordlist(url, words)

    for host in word_list:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:96.0) Gecko/20100101 Firefox/96.0",
            "Host": host,
            "Accept": "*/*"
        }

        try:
            response = requests.get(url, headers=headers, timeout=5, allow_redirects=True, verify=False)
            length = len(response.content)
            print(str(f"[*] {response.status_code} : {length} : {url} : {host}"))
        except Exception as e:
            pass

def main():
    """
    Main program
    """
    parser = ArgumentParser()
    parser.add_argument("-u", "--url", dest="url", help="url to target")
    parser.add_argument("-w", "--word-list", dest="word_list", help="custom word list")
    parser.add_argument("-t", "--threads", dest="threads", help="number of threads")

    args = parser.parse_args()

    if len(sys.argv) < 2:
        parser.print_help()
        exit(1)

    thread_default = 40 
    if args.threads:
        thread_default = int(args.threads)

    if args.word_list:
        if not os.path.exists(args.word_list):
            print("[!] No word list specified.")
            exit(1)
        else:
            with open(args.word_list, "r") as file:
                words = file.readlines()
    else:
        if not os.path.exists(BUILT_IN_WORD_LIST):
            print("[!] No word list specified.")
            exit(1)
        else:
            with open(BUILT_IN_WORD_LIST, "r") as file:
                words = [line.rstrip() for line in file]

    scan(args.url, words)


if __name__ == "__main__":
    main()