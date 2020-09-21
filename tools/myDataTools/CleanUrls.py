

# filter out clean urls
def cleanup_urls(flat_raw):

    flat_raw = [item for sublist in raw_urls_list for item in sublist]
    url_set = set(flat_raw)

    updated_list = list(url_set)
    http_list = [x for x in updated_list if not x.startswith('/') and not x.startswith('#') \
                 and not x.startswith('j') and not x.startswith('mailto') and not x.startswith('?')]
    new_http_list = [x[0:] for x in http_list if not x.startswith('{')]
    partial_url_list = [x for x in updated_list if not x.startswith('h') and not x.startswith('#') \
                        and not x.startswith('j')]
    new_partial_url_list = [x[0:] for x in partial_url_list if not x.startswith('//')]
    combined_url_list = [base_url + x for x in new_partial_url_list]
    spider_url_list = new_http_list + combined_url_list
    final_spider_list = [x for x in spider_url_list if x]

    return final_spider_list
