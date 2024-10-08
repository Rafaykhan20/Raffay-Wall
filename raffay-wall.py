import requests
import os
import re
import time
import json
from itertools import cycle
from requests.exceptions import RequestException

# Function to clear the terminal screen in a cross-platform manner
def clear_screen():
    if os.name == 'nt':  # For Windows
        os.system('cls')
    else:  # For Linux/macOS
        os.system('clear')

# Function to set up multiple cookies from a TXT file
def set_cookies():
    file_path = input("\033[1;36mEnter Cookie File Path (.txt) :: ")
    cookies = {}
    try:
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()  # Remove leading/trailing whitespace
                if line and '=' in line:  # Ensure the line contains a valid cookie format
                    cookie_name, cookie_value = line.split('=', 1)  # Split on the first '=' only
                    cookies[cookie_name.strip()] = cookie_value.strip()
        if cookies:
            return cookies
        else:
            print("\033[1;31m[!] No valid cookies found in the file.")
            return None
    except FileNotFoundError:
        print("\033[1;31m[!] Cookie file not found. Please check the file path and try again.")
        return None
    except Exception as e:
        print("\033[1;31m[!] An error occurred while reading the cookie file:", e)
        return None

def get_commenter_name():
    return input("\033[1;36mEnter Hater Name :: ")

# Function to make HTTP GET requests
def make_request(url, headers, cookies):
    try:
        response = requests.get(url, headers=headers, cookies=cookies).text
        return response
    except RequestException as e:
        print("\033[1;31m[!] Error making request:", e)
        return None

# Function to make HTTP POST requests with error handling
def handle_request(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except RequestException as e:
        print("\033[1;31m[!] Network error:", e)
        return None

# Function to print colored text
def colored_text(text, color_code):
    return f"\033[{color_code}m{text}\033[0m"

# Clear the screen
clear_screen()

# Display the logo
logo = """\033[1;32m
██████╗  █████╗ ███████╗ █████╗ ██╗   ██╗
██╔══██╗██╔══██╗██╔════╝██╔══██╗╚██╗ ██╔╝
██████╔╝███████║█████╗  ███████║ ╚████╔╝ 
██╔══██╗██╔══██║██╔══╝  ██╔══██║  ╚██╔╝  
██║  ██║██║  ██║██║     ██║  ██║   ██║   
╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝  ╚═╝   ╚═╝   
                                         
"""
print(logo)

# Start time
print("\033[1;36mStart Time:", time.strftime("%Y-%m-%d %H:%M:%S"))

# Main loop
while True:
    try:
        print()
        cookies = set_cookies()  # Read cookies from a .txt file

        if cookies is None:
            break

        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 11; RMX2144 Build/RKQ1.201217.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/103.0.5060.71 Mobile Safari/537.36 [FB_IAB/FB4A;FBAV/375.1.0.28.111;]'
        }

        # Validate if the cookies are working by making a request
        response = make_request('https://business.facebook.com/business_locations', headers=headers, cookies=cookies)
        if response and 'EAAG' in response:
            token_eaag = re.search('(EAAG\w+)', response).group(1)
            print(f"\033[1;32mValid EAAG token found: {token_eaag}")
        else:
            print("\033[1;31m[!] No valid EAAG token found.")
            break

        try:
            id_post = int(input("\033[1;36mEnter Post Id :: "))
        except ValueError:
            print("\033[1;31m[!] Invalid Post Id. Please enter a valid number.")
            continue

        commenter_name = get_commenter_name()
        try:
            delay = int(input("\033[1;36mEnter Delay (Seconds) :: "))
        except ValueError:
            print("\033[1;31m[!] Invalid Delay. Please enter a valid number.")
            continue

        comment_file_path = input("\033[1;36mEnter Your Comment File Path :: ")
        try:
            with open(comment_file_path, 'r') as file:
                comments = file.readlines()
        except FileNotFoundError:
            print("\033[1;31m[!] Comment file not found.")
            continue

        # Prepare for round-robin handling of comments and requests
        valid_cookies_cycle = cycle([cookies])  # Using the same cookies since we support one set from the .txt file
        x = 0  # Index for comments
        y = 0  # Failure count

        print()

        while True:
            try:
                time.sleep(delay)
                teks = comments[x].strip()  # Get comment text and strip whitespace
                comment_with_name = f"{commenter_name}: {teks}"

                # Get the current cookies from the cycle (although we are using the same set of cookies)
                current_cookie = next(valid_cookies_cycle)

                data = {
                    'message': comment_with_name,
                    'access_token': token_eaag
                }

                response2 = handle_request(requests.post, f'https://graph.facebook.com/{id_post}/comments/', data=data, cookies=current_cookie)

                if response2 and 'id' in response2:
                    print(colored_text(f"Post id :: {id_post}", "1;32"))
                    print(colored_text(f"Date time :: {time.strftime('%Y-%m-%d %H:%M:%S')}", "1;32"))
                    print(colored_text(f"Comment sent :: {comment_with_name}", "1;32"))
                    print(colored_text('──────────────────────────────────────────────────────────────', '97'))  # Bright white
                    x = (x + 1) % len(comments)  # Move to the next comment
                else:
                    y += 1
                    print(colored_text(f"[{y}] Status : Failure", "1;31"))
                    print(colored_text(f"[/] Link : https://m.basic.facebook.com//{id_post}", "1;31"))
                    print(colored_text(f"[/] Comments : {comment_with_name}", "1;31"))
                    continue

            except RequestException as e:
                print(colored_text("[!] Error making request:", "1;31"), e)
                time.sleep(5.5)
                continue

    except Exception as e:
        print(colored_text("[!] An unexpected error occurred:", "1;31"), e)
        break
