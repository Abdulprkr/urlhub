import argparse
import concurrent.futures
import requests
import sys

# define command line arguments
parser = argparse.ArgumentParser(description='Check the status of URLs in a file.')
parser.add_argument('file', help='the file containing the list of URLs')
parser.add_argument("-r", "--request_rate", type=int, help="set number of requests per second")
parser.add_argument("-rc", "--response_code", type=int, help="filter responses by code")
parser.add_argument("-o", "--output", action="store_true", help="output without HTTP status code")
parser.add_argument("-e", "--ext", help="only include URLs with the specified file extension")
args = parser.parse_args()

def check_url(url):
  try:
    r = requests.get(url)
    return r.status_code
  except:
    return "Error"

# read file passed as command line argument
with open(args.file, 'r') as f:
  # read each line of the file (assume each line is a URL)
  with concurrent.futures.ThreadPoolExecutor() as executor:
    future_to_url = {executor.submit(check_url, line.strip()): line.strip() for line in f}
    for future in concurrent.futures.as_completed(future_to_url):
      url = future_to_url[future]
      status_code = future.result()

      # filter responses by code if -rc option is set
      if args.response_code and status_code != args.response_code:
        continue

      # filter URLs by file extension if -e option is set
      if args.ext and not url.endswith(args.ext):
        continue

      # output without HTTP status code if -o option is set
      if args.output:
        print(url)
      else:
        # format status code with color
        if status_code == 200:
          print(f"{url}: \033[92m{status_code}\033[0m")  # green
        elif status_code == 403:
          print(f"{url}: \033[35m{status_code}\033[0m")  # purple
        elif status_code == 404:
          print(f"{url}: \033[34m{status_code}\033[0m")  # blue
        elif status_code == "Error":
          print(f"{url}: \033[31m{status_code}\033[0m")  # red
        else:
          print(f"{url}: \033[37m{status_code}\033[0m")  # white
