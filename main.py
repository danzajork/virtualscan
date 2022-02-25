#!/usr/bin/python3
import json
import sys
import os
import concurrent.futures
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

def make_request_host(url, host):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:96.0) Gecko/20100101 Firefox/96.0",
            "Host": host,
            "Accept": "*/*"
        }

        response = requests.get(url, headers=headers, timeout=5, allow_redirects=True, verify=False)
        length = len(response.content)

        return {
            "status_code": response.status_code,
            "length": length,
            "url": url,
            "host": host
        }
        
    except Exception as e:
        print(e)

def check_url_for_vhosts(hosts, url, num_threads = 20):
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        future_to_url = {executor.submit(make_request_host, url, host): host for host in hosts}
        for future in tqdm(concurrent.futures.as_completed(future_to_url), total=len(hosts), unit=" hosts"):
            sub_ns_sc = future_to_url[future]
            try:
                if future.result() is not None:
                    results.append(future.result())
            except Exception as e:
                print(e)
                raise
    return results

def scan(url, words, thread_default, out):
    host_list = build_wordlist(url, words)

    results = check_url_for_vhosts(host_list, url, thread_default)
    
    if out:
        with open(out, "w") as file:
            for final_resp in results:
                json_obj = json.dumps(final_resp)
                file.write(f"{json_obj}\n")
    else:
        for final_resp in results:

            status_code = final_resp["status_code"]
            length = final_resp["length"]
            host = final_resp["host"]
           
            print(f"[*] {status_code} : {length} : {url} : {host}")

def main():
    """
    Main program
    """
    parser = ArgumentParser()
    parser.add_argument("-u", "--url", dest="url", help="url to target")
    parser.add_argument("-w", "--word-list", dest="word_list", help="custom word list")
    parser.add_argument("-t", "--threads", dest="threads", help="number of threads")
    parser.add_argument("-o", "--out", dest="output", help="file to output json")

    args = parser.parse_args()

    if len(sys.argv) < 2:
        parser.print_help()
        exit(1)

    thread_default = 20 
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

    scan(args.url, words, thread_default, args.output)


if __name__ == "__main__":
    main()