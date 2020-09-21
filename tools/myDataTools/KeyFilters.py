
def get_clean_article(user_str, soup):

    import re
    key_inp = user_str
    result = soup.find("p", string=re.compile(key_inp))
    str_result = str(result)
    str_result = str_result.lower()

    new_result = ''
    update_result = ''

    if str_result.endswith('>'):
        new_result = str_result[:-4]

    if new_result.startswith('<'):
        update_result = new_result[3:]

    clean_article_list = update_result.split()
    print(clean_article_list)
    return clean_article_list