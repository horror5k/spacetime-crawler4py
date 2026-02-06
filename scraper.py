import re
import json
import os
from urllib.parse import urlparse, urljoin, urldefrag
from bs4 import BeautifulSoup
from tokenizer import tokenize_text
from collections import defaultdict

REPORT_FILE = 'report_data.json'

def load_report():
    if os.path.exists(REPORT_FILE):
        with open(REPORT_FILE, 'r') as f:
            data = json.load(f)
            data['unique_pages'] = set(data['unique_pages'])
            data['subdomains'] = defaultdict(int, data['subdomains'])
            return data
    return {
        'unique_pages': set(),
        'longest_page': {'url': '', 'word_count': 0},
        'word_counts': {},
        'subdomains': defaultdict(int)
    }

def update_report():
    save_data = dict(report)
    save_data['unique_pages'] = list(report['unique_pages'])
    save_data['unique_pages_count'] = len(report['unique_pages'])
    save_data['word_counts'] = dict(sorted(report['word_counts'].items(), key=lambda x: x[1], reverse=True)[:50])
    save_data['subdomains'] = dict(sorted(report['subdomains'].items()))
    with open(REPORT_FILE, 'w') as f:
        json.dump(save_data, f)

report = load_report()


STOP_WORDS = {
    'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', 
    'aren\'t', 'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 
    'but', 'by', 'can\'t', 'cannot', 'could', 'couldn\'t', 'did', 'didn\'t', 'do', 'does', 'doesn\'t', 
    'doing', 'don\'t', 'down', 'during', 'each', 'few', 'for', 'from', 'further', 'had', 'hadn\'t', 
    'has', 'hasn\'t', 'have', 'haven\'t', 'having', 'he', 'he\'d', 'he\'ll', 'he\'s', 'her', 'here', 
    'here\'s', 'hers', 'herself', 'him', 'himself', 'his', 'how', 'how\'s', 'i', 'i\'d', 'i\'ll', 
    'i\'m', 'i\'ve', 'if', 'in', 'into', 'is', 'isn\'t', 'it', 'it\'s', 'its', 'itself', 'let\'s', 
    'me', 'more', 'most', 'mustn\'t', 'my', 'myself', 'no', 'nor', 'not', 'of', 'off', 'on', 'once', 
    'only', 'or', 'other', 'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same', 'shan\'t', 
    'she', 'she\'d', 'she\'ll', 'she\'s', 'should', 'shouldn\'t', 'so', 'some', 'such', 'than', 'that', 
    'that\'s', 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', 'there\'s', 'these', 
    'they', 'they\'d', 'they\'ll', 'they\'re', 'they\'ve', 'this', 'those', 'through', 'to', 'too', 
    'under', 'until', 'up', 'very', 'was', 'wasn\'t', 'we', 'we\'d', 'we\'ll', 'we\'re', 'we\'ve', 
    'were', 'weren\'t', 'what', 'what\'s', 'when', 'when\'s', 'where', 'where\'s', 'which', 'while', 
    'who', 'who\'s', 'whom', 'why', 'why\'s', 'with', 'won\'t', 'would', 'wouldn\'t', 'you', 'you\'d', 
    'you\'ll', 'you\'re', 'you\'ve', 'your', 'yours', 'yourself', 'yourselves'
}


def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]


def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    
    if resp.status != 200:
        return []
    
    if not resp.raw_response or not resp.raw_response.content:
        return[]
    
    try:
        content = resp.raw_response.content
        
        if len(content) > 1048576000:
            return[]
        
        if isinstance(content, bytes):
            content = content.decode('utf-8', errors='ignore')
            
        soup = BeautifulSoup(content, 'lxml')
        text = soup.get_text()
        tokens = tokenize_text(text)
        
        if len(tokens) < 100:
            return []
        
        
        """START REPORT"""
        
        # 1. Unique Pages
        cleaned_url, _ = urldefrag(resp.url)
        report['unique_pages'].add(cleaned_url)
        
        # 2. Longest Page
        word_count = len(tokens)
        if word_count > report['longest_page']['word_count']:
            report['longest_page']['url'] = cleaned_url
            report['longest_page']['word_count'] = word_count
        
        # 3. Word Frequencies
        for token in tokens:
            if token not in STOP_WORDS and len(token) > 1:
                report['word_counts'][token] = report['word_counts'].get(token, 0) + 1
        
        # 4. Subdomains
        parsed = urlparse(cleaned_url)
        hostname = parsed.hostname
        if hostname and 'uci.edu' in hostname:
            report['subdomains'][hostname] += 1
        
        # Save
        update_report()
        
        """END REPORT"""

        links = []
        for a_tags in soup.find_all('a', href=True):
            href = a_tags['href']
            full_url = urljoin(resp.url, href)
            defrag_url, _ = urldefrag(full_url)
            
            if defrag_url:
                links.append(defrag_url)
        
        return links
    
    except Exception as e:
        print(f"{url}: {e}")
        return []


def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        
        hostname = parsed.hostname
        if not hostname:
            return False
        hostname = hostname.lower()
        
        domains = ['ics.uci.edu', 'cs.uci.edu', 'informatics.uci.edu', 'stat.uci.edu']
        if not any(hostname == d or hostname.endswith('.' + d) for d in domains):
            return False
        
        if '/wp-content/uploads/' in parsed.path.lower():
            return False
        
        if 'wp-login.php' in parsed.path.lower():
            return False        
        
        if re.search(r'/day/\d{4}-\d{2}-\d{2}', parsed.path):
            return False
        if re.search(r'/week/\d{4}-\d{2}-\d{2}', parsed.path):
            return False
        if re.search(r'/events/\d{4}-\d{2}-\d{2}', parsed.path):
            return False
        if re.search(r'/events/month/\d{4}-\d{2}', parsed.path):
            return False
        if re.search(r'/events/category/.+/\d{4}-\d{2}', parsed.path):
            return False
        if re.search(r'/events/category/.+/(today|month|list)', parsed.path):
            return False
        if 'eventdisplay' in parsed.query.lower():
            return False
        if 'tribe-bar-date' in parsed.query.lower():
            return False
        if 'tribe__ecp_custom' in parsed.query.lower():
            return False
        if 'eventdate' in parsed.query.lower():
            return False

        if 'share=' in parsed.query.lower():
            return False
        
        if 'grape' in hostname and ('/wiki/' in parsed.path.lower() or '/timeline' in parsed.path.lower()):
            return False      

        if 'ical' in parsed.query.lower():
            return False
        
        if 'archive' in hostname and 'keywords' in parsed.query.lower():
            return False
        
        if 'doku.php' in parsed.path.lower():
            return False
        
        if hostname.startswith('netreg'):
            return False
        
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1|apk"
            + r"|thmx|mso|arff|rtf|jar"
            + r"|csv|txt|pyc|pyo|bib|py|c|m|ma|ppsx" #new
            + r"|pps|odc|z|scm|lsp|rkt|nb|lif|sh|sql|sas|pov|ff|rss|ss|shtml" #new
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise
