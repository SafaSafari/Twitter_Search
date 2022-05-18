import requests, re, json
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
        temp_api = re.search(r'authorization:"Bearer ".concat\("(.*)"\),"content-type"', jjs).group(1)
        return temp_api

    def activate(self):
        return requests.post('https://api.twitter.com/1.1/guest/activate.json', headers={'Authorization': 'Bearer {}'.format(self.token)}).json()['guest_token']

    def search(self, query, page=''):
        params = {"q": query, "include_quote_count": True, "tweet_search_mode": "live"}
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
        for i in self.last['timeline']['instructions'][0]['addEntries']['entries'][::-1]:
            if i['entryId'] == 'sq-cursor-bottom':
                self.page = i['content']['operation']['cursor']['value']
                return self.get_page()

    def get_prev_page(self):
        for i in self.last['timeline']['instructions'][0]['addEntries']['entries']:
            if i['entryId'] == 'sq-cursor-top':
                self.page = i['content']['operation']['cursor']['value']
                return self.get_page()

tw = search("from:@safasafari3")
print(json.dumps(tw.get_page(), indent=4))