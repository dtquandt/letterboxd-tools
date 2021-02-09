import letterboxd
import requests
import pandas as pd

def get_credentials(path='credentials.txt'):
    with open(path, 'r') as f:
        credentials = f.read().split('\n')
    return credentials

def api_request(path):
    key, secret = get_credentials()
    api_base = 'https://api.letterboxd.com/api/v0'
    
    return letterboxd.api.API(api_base=api_base, api_key=key, api_secret=secret).api_call(path)

def get_id_from_username(member_name):

    head_request = requests.head(f'https://letterboxd.com/{member_name}/')
    status_code = head_request.status_code
    if status_code != 200:
        raise ValueError(f'Request failed when looking up member {member_name}.\
                           Status code: {status_code}')
    res_headers = head_request.headers

    if 'X-Letterboxd-Identifier' not in res_headers:
        raise KeyError(f'Page headers did not include Letterboxd Identifier. Possible change on their side?')
    member_id = res_headers['X-Letterboxd-Identifier']
    
    return member_id


def get_member_watchlist(member_name='', member_id=None):
    
    if not member_id:
        member_id = get_id_from_username(member_name)
        
    full_results = []
    
    def paginate_watchlist(cursor='start=0'):    
        wl_response = api_request(f'member/{member_id}/watchlist?perPage=100&cursor={cursor}')
        wl_response_status = wl_response.status_code
        if wl_response_status != 200:
            raise ValueError(f'Request failed when pulling watchlist for member ID {member_id}.\
                               Status code: {wl_response_status}')
        wl_json = wl_response.json()
        full_results.extend(wl_json['items'])
        if 'next' in wl_json.keys():
            paginate_watchlist(cursor=wl_json['next'])
    
    paginate_watchlist(full_results)
    
    return pd.DataFrame(full_results)

def get_combined_watchlists(members):
    
    watchlists = []
    
    for member in members:
        watchlist = get_member_watchlist(member)
        watchlists.append(watchlist)
    
    combined_watchlist = pd.concat(watchlists)
    
    return combined_watchlist


def get_user_ratings(member):
    
    cursor = 'start=0'
    results = {'next':None}
    all_ratings = []

    while True:
        response = api_request(
            f'films/?perPage=100&member={member}&memberRelationship=Watched&sort=MemberRatingHighToLow&cursor={cursor}')
        results = response.json()
        for item in results['items']:
            entry = {'member': member}
            entry['film'] = item.get('id')
            relationships = item.get('relationships')
            if relationships:
                relationship = relationships[0].get('relationship')
                if relationship:
                    entry['rating'] = relationship.get('rating')
            all_ratings.append(entry)
        if 'next' not in results:
            break
        else:
            cursor = results['next']
        
    return pd.DataFrame(all_ratings)


def threaded_api_request(url_list, max_retries=15, max_threads=50, print_every=1000):
    
    from concurrent.futures import ThreadPoolExecutor, as_completed

    all_results = []
    missing_urls = []
    failed_urls = []

    def error_handler(url):

        retry_count = 0

        while True:
            try:
                res = api_request(url)
                return res.json()
            except Exception as e:
                if str(e)[0:3] == '404':
                    missing_urls.append(url)
                    return None
                retry_count += 1
                if retry_count > max_retries:
                    failed_urls.append(url)
                    print('Url failed after 15 retries.')
                    return None

    def runner(url_list):
        count = 0
        threads = [] 
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            for url in url_list:
                threads.append(executor.submit(error_handler, url))
            for task in as_completed(threads):
                entry = task.result()
                if entry:
                    all_results.append(entry)
                count += 1
                if count % print_every == 0:
                    print(f'{count} URLs processed so far.')

    print('Running scraper...')
    runner(url_list)
    
    return all_results, missing_urls, failed_urls