import sys

sys.stdout.reconfigure(encoding="utf-8")


from config import API_KEY, API_SECRET
from auth import get_token
from api import search_properties
from display import print_results, inspect_photos

if __name__ == "__main__":
    token = get_token(API_KEY, API_SECRET)
    results = search_properties(token)
    print_results(results)
    inspect_photos(results)