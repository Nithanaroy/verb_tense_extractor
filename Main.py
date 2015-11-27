#!/usr/bin/env python
# -*- coding: latin-1 -*-

from bs4 import BeautifulSoup
import os
import re
import urllib2
import json
import sys, traceback
import codecs
import time
import datetime
import urllib
import base64


class Main:
    def __init__(self):
        self.eng_verbs = []
        self.german_verbs = []

    def get_english_verbs(self, cached=True):
        """
        Fetches the list of verbs from https://verbs.colorado.edu/propbank/framesets-english/
        Sets the member variable, eng_verbs, with all english verbs
        :param cached: Uses saved verbs file
        :return:
        """
        if cached:
            f = open(os.path.abspath("verbs.txt"))  # Has one verb per line
            self.eng_verbs = [w.strip() for w in f.read().splitlines()]
            f.close()
        else:
            url = os.path.abspath("propbank.html")
            f = open(url)
            html = f.read()
            f.close()
            soup = BeautifulSoup(html, 'html.parser')
            for link in soup.find_all('a'):  # time consuming task
                link_text = link.get_text()
                verb = re.match(r'(.+)-v.html', link_text)
                if verb:
                    self.eng_verbs.append(verb.groups()[0].strip())

    def get_german_words(self, cached=True):
        if cached:
            f = codecs.open(os.path.abspath('german_verbs.de'), 'r', 'utf-8')
            for line in f.read().splitlines():
                t, s = line.split("##########")
                translations = []
                syn_translations = []
                if len(t) > 0:
                    translations = t.split(',')
                if len(s) > 0:
                    syn_translations = s.split(',')
                translations.append(syn_translations)
                self.german_verbs.append(translations)
            f.close()
        else:
            url_base = 'https://dictionary.yandex.net/api/v1/dicservice.json/lookup?key=dict.1.1.20151025T082334Z.d1c51ebb15e03fc9.b9f5b9c541bd619e3a4fe3ffbb2823fd23fa2c81&lang=en-de&text='
            f = codecs.open(os.path.abspath('german_verbs.de'), 'w', 'utf-8')
            total_verbs = len(self.eng_verbs)
            for i, w in enumerate(self.eng_verbs):
                translations = []
                syn_translations = []
                reqd_pos = 'verb'
                self.get_german_for_word(f, reqd_pos, syn_translations, translations, url_base, w)
                time.sleep(0.3)  # sleep for 300ms before making another GET request
                self.status_log(i, w, total_verbs)
            f.close()

    def status_log(self, i, w, total):
        if i % 10 == 0:
            # print '{}: {} of {}. Completed {}'.format(datetime.datetime.utcnow(), i, total, u'' + w)
            print '{}: {} of {}'.format(datetime.datetime.utcnow(), i, total)

    def log_for_verbix(self, word, form, tense):
        # print '{}: Word: {}. Form: {}. Tense: {}'.format(datetime.datetime.utcnow(), u'' + word, form, tense)
        print '{}: Form: {}. Tense: {}'.format(datetime.datetime.utcnow(), form, tense)

    def log_for_create_json(self, word):
        # print '{}: Word: {}'.format(datetime.datetime.utcnow(), u'' + word)
        print '{} A word failed in Create JSON'.format(datetime.datetime.utcnow())

    def get_german_for_word(self, f, reqd_pos, syn_translations, translations, url_base, w):
        try:
            t = json.loads(urllib2.urlopen(url_base + w).read())
            for d in t['def']:
                if 'tr' in d:
                    for tr in d['tr']:
                        if 'pos' in tr and tr['pos'] == reqd_pos:
                            translations.append(tr['text'])
                        if 'syn' in tr:
                            for s in tr['syn']:
                                if 'pos' in s and s['pos'] == reqd_pos:
                                    syn_translations.append(s['text'])
        except:
            traceback.print_exc(file=sys.stdout)
        f.write(','.join(translations))
        f.write('##########')
        f.write(','.join(syn_translations))
        f.write('\r\n')
        translations.append(syn_translations)
        self.german_verbs.append(translations)

    def create_json_for_german(self):
        # flatten the german verbs from [[w1, w2, [w3, w4]], [w5, w6, []]] to [w1, w2, w3, w4, w5, w6]
        verbs = []
        for w in self.german_verbs:
            for verb in w[:-1]:
                verbs.append(verb)
            for verb in w[-1]:
                verbs.append(verb)
        total = len(verbs)
        for i, w in enumerate(verbs):
            try:
                safe_filename = base64.urlsafe_b64encode(w.encode('utf-8'))
                safe_url = w.encode('iso-8859-1')
                json_filepath = os.path.abspath('./german_verbs_jsons/' + safe_filename + ".json")  # output json path
                filepath = os.path.abspath('./german_verbs_htmls/' + safe_filename + ".html")  # output html path
                url = 'http://www.verbix.com/webverbix/German/' + safe_url + '.html'  # verbix URL
                urllib.urlretrieve(url, filepath)

                # read from saved HTML
                file = codecs.open(filepath, 'r', 'utf-8')
                json_out = self.get_json_for_german(file.read(), w)
                file.close()

                # save extracted JSON
                f = codecs.open(json_filepath, 'w', 'utf-8')
                f.write(json.dumps(json_out))
                f.close()

                self.status_log(i, w, total)
                time.sleep(0.3)  # sleep for 300ms before making another GET request
            except NameError:
                pass
            except:
                print
                traceback.print_exc(file=sys.stdout)
                print
                # self.log_for_create_json(w)
        print('Done')

    def get_json_for_german(self, html, w):
        soup = BeautifulSoup(html, 'html.parser')
        try:
            div = soup.select('#main >  div.verbcontent > div.pure-g', limit=1)[0]
        except:
            raise NameError("Not a verb error")
        forms = div.select('div.pure-u-1-1')  # <= 5
        json = {'word': w}

        def extract_tense(t, form, tense):
            res = {}
            try:
                for fo in t.p.select('font'):
                    value = fo.next_sibling.text  # Risk: assuming next sibling is always the german word for <font /> tag
                    for s in fo.select('span'):
                        res[s.text.strip()] = value
            except:
                self.log_for_verbix(w, form, tense)
            return res

        def extract_tenses(f, form):
            res = {}
            for t in f.select('div.pure-u-1-2'):
                tense = t.h3.text.strip()
                res[tense] = extract_tense(t, form, tense)
            return res

        def extract_nominal(f):
            res = {}
            try:
                keys = f.p.select('b')
                values = f.p.select('span')
                if len(keys) != len(values):
                    return None
                for i in range(len(keys)):
                    key = keys[i].text.strip()[:-1]  # remove : at the end
                    value = values[i].text.strip()
                    res[key] = value
            except:
                self.log_for_verbix(w, 'Nominal', None)
            return res

        def extract_conjunctive(f):
            return extract_tenses(f, 'Conjunctive')

        def extract_imperative(f):
            return extract_tense(f, 'Imperative', None)

        def extract_indicative(f):
            return extract_tenses(f, 'Indicative')

        def extract_conditional(f):
            return extract_tenses(f, 'Conditional')

        switch = {
            'Nominal Forms': extract_nominal,
            'Indicative': extract_indicative,
            'Conjunctive I and II': extract_conjunctive,
            'Conditional': extract_conditional,
            'Imperative': extract_imperative
        }
        for form in forms:
            key = form.h2.text.strip()
            json[key] = switch[key](form)
        return json


if __name__ == '__main__':
    m = Main()
    m.get_english_verbs()
    m.get_german_words()
    m.create_json_for_german()
