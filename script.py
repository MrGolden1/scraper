import requests
import json
import pandas as pd
import threading
import queue
import time

journals_api = "https://search-app.prod.ecommerce.elsevier.com/api/search?labels=journals&page={}&in-publication=true&locale=global"
journal_info_api = "https://www.journals.elsevier.com/_next/data/OohGP-kM0hfp4_xLmWgAq/{}.json"

keyword = "Your Paper Your Way"
target_journals = []

total_pages = None
current_page = 1

lock = threading.Lock()
html_queue = queue.Queue()

# dummy request to get total number of pages
r = requests.get(journals_api.format(current_page))
if r.status_code == 200:
    total_pages = json.loads(r.text)["pagination"]["totalNumberOfPages"]
else:
    print("Error: {}".format(r.status_code))
    exit(1)
    

def get_html():
    global current_page
    while True:
        with lock:
            i = current_page
            current_page += 1
        if i > total_pages:
            break
        
        print("Page {}/{}".format(i, total_pages))
        r = requests.get(journals_api.format(i))
        if r.status_code == 200:
            journals = json.loads(r.text)["hits"]
        else:
            print("Error: {}".format(r.status_code))
            exit(1)
            
        for journal in journals:
            url = journal["url"]
            name_id = url.split("/")[-1]
            title = journal["title"]
            
            info_r = requests.get(journal_info_api.format(name_id))
            if info_r.status_code == 200:
                info = json.loads(info_r.text)
                has_guide = info["pageProps"]["publishingOptions"]["show_guide_for_authors"]
                if not has_guide:
                    continue
                guide_for_authors_url = info["pageProps"]["publishingOptions"]["guide_for_authors_url"]
                html = requests.get(guide_for_authors_url).text
                html_queue.put((title, guide_for_authors_url, html))
    
def check_keyword():
    while True:
        item = html_queue.get()
        if item is None:
            break
        
        title, guide_for_authors_url, html = item

        if keyword in html:
            target_journals.append((title, guide_for_authors_url))

start_time = time.time()
THREAD_NUM = 25
threads = []
for i in range(THREAD_NUM):
    t = threading.Thread(target=get_html)
    threads.append(t)
    t.start()
    
check_keyword_thread = threading.Thread(target=check_keyword)
check_keyword_thread.start()

for t in threads:
    t.join()
    
html_queue.put(None)

duration = time.time() - start_time
print("-------------------------------------------------------")
print("Duration: {:.2f}s".format(duration))
    
df = pd.DataFrame(target_journals, columns=["title", "guide_for_authors_url"])
df.to_excel("result.xlsx", index=False)
print("Done")