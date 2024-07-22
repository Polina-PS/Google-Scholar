import re
from transliterate import translit
from datetime import date
from serpapi import GoogleSearch
from to_html import HtmlTable

API_KEY = "f3e66094ba741182a8ee80b1b9f6a021898aab97cfb9e5b1bb0fdb5cbd493fc0"

#êîë-âî àâòîðîâ è ëåò
count_authors = 1
count_years = 1

token = ""
def id_author(token):
    params_all_authors = {
        "engine": "google_scholar_profiles",
        "mauthors": "Ñàíêò-Ïåòåðáóðãñêèé ãîðíûé óíèâåðñèòåò",
        "api_key": API_KEY,
        "after_author": token
        }
    search = GoogleSearch(params_all_authors)
    result_all_authors = search.get_dict()
    return result_all_authors

def Next_Page(st, params):
    params["start"] = st*100
    search = GoogleSearch(params)
    result_page = search.get_dict()
    return result_page

def article(citation_id):
    params_articles = {
    "engine": "google_scholar_author",
    "view_op": "view_citation",
    "citation_id": citation_id,
    "api_key": API_KEY
        }
    search = GoogleSearch(params_articles)
    result_article = search.get_dict()
    return result_article

def info_author(author_id):
    params_author = {
        "engine": "google_scholar_author", 
        "author_id": author_id,
        "api_key": API_KEY,
        "sort": "pubdate",
        "num": 100
        }
    search = GoogleSearch(params_author)
    result_author = search.get_dict()

    #ÈÌß
    name = result_author["author"]["name"]
    name_ru = ' '.join(re.findall(r"\b([à-ÿÀ-ß¸¨]+)\b", name))
    name_en = ' '.join(re.findall(r"\b([a-zA-Z]+)\b", name))

    if len(name_ru) == 0:
        name_ru = translit(name_en, "ru")
    if len(name_en) == 0:
        name_en = translit(name_ru, language_code = "ru", reversed = True)
        name_en = re.sub(r'[^\w\s]','', name_en)

    all_name = name_ru.split(" ") + name_en.split(" ")
    #EMAIL
    email = result_author["author"]["email"]
    
    #íà÷àëüíûå çíà÷åíèÿ
    today = date.today()
    today_year = today.year

    articles = {}
    cit = {}
    articles["Âñåãî"] = 0
    cit["Âñåãî"] = 0
    for i in range(count_years):
        articles[int(today_year - i)] = 0
        cit[int(today_year - i)] = 0

    co_authors = 0
    author_1 = 0
    author_first = 0
    without_author = 0
    
        
    if int(result_author["articles"][0]["year"]) <= int(today_year - count_years):
        return(name_ru, name_en, email, articles, cit, co_authors, author_1, author_first, without_author)
    #ÊÎË-ÂÎ ÑÒÀÒÅÉ È ÖÈÒÈÐÎÂÀÍÈÉ    
    all_year = []
    start = 0
    y = today_year

    while True:
        for year in result_author["articles"]:
            if year["year"] != "":
                y = int(year["year"])
                if y > (today_year - count_years):
                    all_year.append(year) #âñÿ èíô çà îïðåäåëåííûå ãîäà
                    articles[y] += 1      #êîë-âî ñòàòåé
                    if year["cited_by"]["value"]:
                        cit[y] += int(year["cited_by"]["value"])   #êîë-âî öèòèðîâàíèé
        if y > (today_year - count_years):
            start += 1
            result_author = Next_Page(start, params_author)  #ïåðåõîä íà ñëåä ñòðàíèöó
        else:
            break
        
    for i in articles:
        articles["Âñåãî"] += int(articles[i])
        cit["Âñåãî"] += int(cit[i])

    #ÀÂÒÎÐ È ÑÎÀÂÒÎÐÛ
    all_authors = []

    for author in all_year:
        if author["year"] != "":
            string = author["authors"]
            if ", ..." in string:
                citation_id = author["citation_id"]
                result_article = article(citation_id)
                all_authors.append(result_article["citation"]["authors"])
            else:
                all_authors.append(author["authors"])  #âñå àâòîðû
        
    all_au = []
    all_sn = []
    all_surname = ""

    for string in all_authors:
        all_au.append(string.lower().title())

    for string in all_au:
        if "," in string:
            st = string.split(",")
            all_surname = ""
            for s in st:
                surname = ' '.join(s.split()[-1:])
                all_surname += surname + " "
            all_sn.append(all_surname)     #òîëüêî ôàìèëèè
        else:
            surname = ' '.join(string.split()[-1:])
            all_sn.append(surname)
            for n in all_name:
                if n == surname:
                    author_1 += 1   #ýòîò àâòîð ÿâëÿåòñÿ åäèíñòâåííûì àâòîðîì ñòàòüè
        
    str_surname = []
    author_f = 0
    au = 0

    for name in all_sn:
        n = name.split()
        for s in n:
            str_surname.append(s)
            if s in all_name:
                au += 1
                if n[0] == s:
                    author_f += 1

    if articles["Âñåãî"] >= au:             #àâòîðà íåò â ñïèñêå àâòîðîâ ñòàòüè
        without_author = articles["Âñåãî"] - au

    author_first = author_f - author_1      #àâòîð çàïèñàí ïåðâûé ñðåäè ñîàâòîðîâ
        
    list_not_author = []
    ln_author = []
        
    for word in str_surname:
        count_name = 0
        count = 0
        for fragment in all_name:
            count_name += 1 
            if fragment != word:
                count += 1
        if count == count_name:
            list_not_author.append(word)
        
    for word in list_not_author:
        word_en = translit(word, language_code='ru', reversed=True)
        if word_en not in ln_author:
            ln_author.append(word_en)
    co_authors = len(ln_author)    #êîë-âî ñîàâòîðîâ
       
    return(name_ru, name_en, email, articles, cit, co_authors, author_1, author_first, without_author)


#çàïèñü âñåõ id
all_id = []

while len(all_id) < count_authors:
    result_all_authors = id_author(token)
    for a_id in result_all_authors["profiles"]:
        if len(all_id) < count_authors:
            all_id.append(a_id["author_id"])
    token = result_all_authors["pagination"]["next_page_token"]

#html
headers = ["Èìÿ íà ðóññêîì", "Èìÿ íà àíãëèéñêîì", "Email", "Êîë-âî ñòàòåé", "Êîë-âî öèòèðîâàíèé", "Êîë-âî ñîàâòîðîâ", "Êîë-âî ñòàòåé, ãäå àâòîð åäèíñòâåííûé", "Êîë-âî ñòàòåé, ãäå àâòîð ïåðâûé â ñïèñêå", "Êîë-âî ñòàòåé, ãäå íåò àâòîðà"]
table = HtmlTable(headers)

for a_id in all_id:
    author_id = [a_id]
    info = info_author(author_id)
    table.to_table(info)

h1 = "<h1>Ñòàòèñòèêà ïî äàííûì àâòîðîâ Ñàíêò-Ïåòåðáóðãñêîãî ãîðíîãî óíèâåðñèòåòà</h1>"
h2 = "<h2>Èñòî÷íèê äàííûõ: <a href='https://scholar.google.ru/schhp?hl=ru'>Google Àêàäåìèÿ</a></h2>"
out = "<link rel='stylesheet' href='style.css'>" + h1 + h2 + table.get_table()
f = open('table.html', 'w')
f.write(out)
f.close()

