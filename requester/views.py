from django.shortcuts import render
from configure.models import Source

import requests
import re
import random

from bs4 import BeautifulSoup

from . import forms

from tools.myDataTools.NegativeWords import neg_wordlist
from tools.myDataTools.PositiveWords import pos_wordlist
from tools.myDataTools.KeyFilters import get_clean_article
from tools.myDataTools.Names import get_agent_names


def RequestView(request):
    # soup variables
    r = ''
    soup = ''
    results = ''
    base_url = ''
    search_string = ''

    # url extraction variables
    raw_urls_list = []
    spider_url_list = []

    # word score variables
    negative_list = []
    positive_list = []
    req_word_total = 0
    req_wordlist = []

    filtered_word_total = 0
    negative_word_total = 0
    positive_word_total = 0

    negative_word_perc = 0
    positive_word_perc = 0

    form = forms.requestForm()

    if request.method == 'POST':
        form = forms.requestForm(request.POST)

        if 'submit' in request.POST:

            # get all Source object urls in a list and initiate try:
            source_urls = list(Source.objects.filter().values_list('url', flat=True))
            source_keywords = list(Source.objects.filter().values_list('keyword', flat=True))

            for x,y in enumerate(source_urls):
                print("processing Source object", x, "with url: ", source_urls[x], "and keyword: ", source_keywords[x],
                      "\n")

                try:
                    base_url = str(source_urls[x])
                    user_keyword = str(source_keywords[x])

                    # remove / from end of base_url
                    if base_url.endswith('/'):
                        base_url = base_url[:-1]

                    # configure requests.py
                    try:
                        source = requests.get(base_url)
                        source.raise_for_status()

                    except UnicodeError:
                        print("UnicodeError: encoding with 'idna' codec failed (UnicodeError: label too long) FOR :: ",
                              base_url)
                    except requests.exceptions.InvalidSchema:
                        print("requests.exceptions.InvalidSchema: No connection adapters were found FOR :: '", base_url,
                              "'")
                    except requests.exceptions.InvalidURL:
                        print("requests.exceptions.InvalidURL: No schema supplied. Perhaps you meant http://", base_url,
                              "?")
                    except requests.exceptions.Timeout:
                        print("source request timeout error!")

                    # configure beautiful soup
                    soup = BeautifulSoup(source.text, 'html.parser')

                    # get all sub urls from links in soup
                    for item in soup.find_all("a"):
                        raw_urls_list.append(re.findall(r' href="(.*?)"', str(item)))

                    # filter out clean urls
                    flat_raw = [item for sublist in raw_urls_list for item in sublist]
                    url_set = set(flat_raw)

                    updated_list = list(url_set)
                    http_list = [x for x in updated_list if not x.startswith('/') and not x.startswith('#')\
                                 and not x.startswith('j') and not x.startswith('mailto') and not x.startswith('?')]
                    new_http_list = [x[0:] for x in http_list if not x.startswith('//')]
                    partial_url_list = [x for x in updated_list if not x.startswith('h') and not x.startswith('#')\
                                        and not x.startswith('j')]
                    new_partial_url_list = [x[0:] for x in partial_url_list if not x.startswith('//')]
                    combined_url_list = [base_url + x for x in new_partial_url_list if not x.startswith('{')]
                    spider_url_list = new_http_list + combined_url_list
                    final_spider_list = [x for x in spider_url_list if x]
                    # print("Final spider list: ", final_spider_list)
                    # print("base urls: ", http_list)
                    # print("partial urls: ", partial_url_list)
                    # print("combined urls: ", combined_url_list)


                    # extract words from soup, add them to main wordlist, and request all sublink soups
                    try:
                        results = soup.find('html').text.strip()
                    except AttributeError:
                        print("AttributeError: 'NoneType' object has no attribute 'text'")

                    req_wordlist += results.split()
                    agent_names = get_agent_names()

                    # start iterating through spider urls
                    for suburl in final_spider_list:
                        try:
                            if suburl:
                                agent_i = random.randint(1, len(agent_names)-1)
                                # print("Configuring agent: ", agent_names[agent_i])

                                subsource = requests.get(suburl, headers={'User-agent': agent_names[agent_i]})
                                subsource.raise_for_status()
                                    # print("Special exception for request: ", suburl, " of type: ", subsource.raise_for_status())

                                subsoup = BeautifulSoup(subsource.text, 'html.parser')
                                subresults = []

                                # implement KeyFilters
                                try:
                                    subresults = get_clean_article(user_keyword, subsoup)
                                    print("processing Source object", x, "from url:", y, "to", suburl, "with keyword: '", source_keywords[x], "' and User-agent: '", agent_names[agent_i], "'")
                                    # print("\n", subresults)

                                    # subresults = subsoup.find('html').text.strip()

                                    # adding words from subsoups to main wordlist
                                    req_wordlist += subresults

                                except AttributeError:
                                    print("AttributeError: ", type(subresults), "(Subresults) = 'NoneType' object and has \
                                    no attribute 'text' FOR :: ",
                                          suburl)

                        except UnicodeError:
                            print("UnicodeError: encoding with 'idna' codec failed (UnicodeError: label too long) FOR \
                            :: ", suburl)
                        except requests.exceptions.InvalidSchema:
                            print("requests.exceptions.InvalidSchema: No connection adapters were found FOR :: '",
                                  suburl, "'")
                        except requests.exceptions.InvalidURL:
                            print("requests.exceptions.InvalidURL: No schema supplied. Perhaps you meant http://",
                                  suburl, "?")
                        except requests.exceptions.ConnectionError as e:
                            print(e, "at: ", suburl)
                        except requests.exceptions.HTTPError as e:
                            print(e, "at: ", suburl)


                except Exception as e:
                    print(e)


            # append words to pos/neg lists
            for item in req_wordlist:
                for word in neg_wordlist:
                    if item == word:
                        negative_list.append(item)

            for item in req_wordlist:
                for word in pos_wordlist:
                    if item == word:
                        positive_list.append(item)

            # get word scores and percentages
            req_word_total = len(req_wordlist)
            filtered_word_total = (len(negative_list) + len(positive_list))

            negative_word_total = len(negative_list)
            positive_word_total = len(positive_list)

            def percentage(part, whole):
                return 100 * float(part) / float(whole)

            negative_word_perc = percentage(negative_word_total, filtered_word_total)
            positive_word_perc = percentage(positive_word_total, filtered_word_total)

    return render(request, 'requester/test.html', {'negative_list': negative_list, 'positive_list': positive_list,
                                                   'req_word_total': req_word_total,
                                                   'filtered_word_total': filtered_word_total,
                                                   'negative_word_total': negative_word_total,
                                                   'positive_word_total': positive_word_total,
                                                   'negative_word_perc': negative_word_perc,
                                                   'positive_word_perc': positive_word_perc,
                                                   'spider_url_list': spider_url_list, 'form': form})