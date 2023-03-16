import requests
import re
import json
import itertools
from urllib.parse import urlencode


class twitter:
    def __init__(self):
        self.token = self.register_temporary()
        self.guest_id = self.activate()

    def register_temporary(self):
        jsha = requests.get('https://twitter.com/sw.js').text
        for js in re.findall(r'"(https:\/\/.*?)"', jsha):
            if 'serviceworker' in js:
                break
        jjs = requests.get(js).text
        temp_api = re.search(
            r'authorization:"Bearer ".concat\("(.*)"\),Accept', jjs).group(1)
        return temp_api

    def activate(self):
        return requests.post('https://api.twitter.com/1.1/guest/activate.json', headers={'Authorization': 'Bearer {}'.format(self.token)}).json()['guest_token']

    def search(self, query, page=''):
        params = {"include_profile_interstitial_type": 1,
                  "include_blocking": 1,
                  "include_blocked_by": 1,
                  "include_followed_by": 1,
                  "include_want_retweets": 1,
                  "include_mute_edge": 1,
                  "include_can_dm": 1,
                  "include_can_media_tag": 1,
                  "include_ext_has_nft_avatar": 1,
                  "include_ext_is_blue_verified": 1,
                  "include_ext_verified_type": 1,
                  "skip_status": 1,
                  "cards_platform": "Web-12",
                  "include_cards": 1,
                  "include_ext_alt_text": True,
                  "include_ext_limited_action_results": False,
                  "include_quote_count": True,
                  "include_reply_count": 1,
                  "tweet_mode": "extended",
                  "include_ext_views": True,
                  "include_entities": True,
                  "include_user_entities": True,
                  "include_ext_media_color": True,
                  "include_ext_media_availability": True,
                  "include_ext_sensitive_media_warning": True,
                  "include_ext_trusted_friends_metadata": True,
                  "send_error_codes": True,
                  "simple_quoted_tweet": True,
                  "q": query,
                  "tweet_search_mode": "live",
                  "query_source": "typed_query",
                  "count": 20,
                  "requestContext": "launch",
                  "pc": 1,
                  "spelling_corrections": 1,
                  "include_ext_edit_control": True, }
        if page:
            params['cursor'] = page
        return requests.get('https://twitter.com/i/api/2/search/adaptive.json?{}'.format(urlencode(params)), headers={'Authorization': 'Bearer {}'.format(self.token), "X-Guest-Token": self.guest_id}).json()


class search(twitter):
    def __init__(self, query, page=''):
        super().__init__()
        self.query = query
        self.page = page

    def get_page(self):
        self.last = self.search(self.query, self.page)
        return self.last

    def get_next_page(self):
        for i in itertools.chain(*[entries['addEntries']['entries'] if entries.get('addEntries') else [entries.get('replaceEntry').get('entry')] for entries in self.last['timeline']['instructions']]):
            if i['entryId'] == 'sq-cursor-bottom':
                self.page = i['content']['operation']['cursor']['value']
                return self.get_page()

    def get_prev_page(self):
        for i in itertools.chain(*[entries['addEntries']['entries'] if entries.get('addEntries') else [entries.get('replaceEntry').get('entry')] for entries in self.last['timeline']['instructions']]):
            if i['entryId'] == 'sq-cursor-top':
                self.page = i['content']['operation']['cursor']['value']
                return self.get_page()
