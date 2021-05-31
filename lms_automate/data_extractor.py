# to extract data form the web
# google and its first 5 links
import requests
import re
from lxml import html
from urllib import parse as urlparse
import re
from socket import gethostbyname, gethostbyaddr

from lms_quiz import bcolors


class google():
	def __init__(self, q, limit=1, count=10, mode='legacy'):
		""" google.com search engine
			q     : Query for search
			limit : Number of pages
			count : Number of results
		"""
		self.q = q
		self.mode = mode
		if self.mode == 'legacy':
			self.agent = 'Lynx/2.8.5rel.1 libwww-FM/2.15FC SSL-MM/1.4.1c OpenSSL/0.9.7e-dev'
			self.xpath_name_legacy = {
				'results': '//div[@class="ezO2md"]',
				'results_content': './/div[@class="YgS6de"]//span[@class="fYyStc"]',
				'results_title': './/span[@class="CVA68e qXLe6d"]',
				'results_a': './/a[@class="fuLhoc ZWRArf"]',
				'results_cite': './/span[@class="qXLe6d dXDvrc"]/span[@class="fYyStc"]'
			}
			self.xpath_legacy = {
				self.xpath_name_legacy['results']: [
					self.xpath_name_legacy['results_content'],
					self.xpath_name_legacy['results_title'],
					self.xpath_name_legacy['results_a'],
					self.xpath_name_legacy['results_cite']
				]
			}
		else:
			self.agent = 'Mozilla/5.0 (X11; Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0'
			self.xpath_name_original = {
				'results': '//div[@class="g"]',
				'results_content': './/div[@class="IsZvec"]',
				'results_title': './/h3[1]',
				'results_a': './/div[@class="yuRUbf"]/a',
				'results_cite': './/div[@class="yuRUbf"]/a//cite'
			}
			self.xpath_original = {
				self.xpath_name_original['results']: [
					self.xpath_name_original['results_content'],
					self.xpath_name_original['results_title'],
					self.xpath_name_original['results_a'],
					self.xpath_name_original['results_cite']
				]
			}
		self.url = 'https://www.google.com/search'
		self._pages = ''
		self._first_page = ''
		self.limit = limit + 1
		self.count = count

	def run_crawl(self):
		page = 1
		set_page = lambda x: (x - 1) * self.count
		payload = {'num': self.count, 'start': set_page(
		    page), 'ie': 'utf-8', 'oe': 'utf-8', 'q': self.q, 'filter': '0'}
		max_attempt = 0
		while True:
			style_print.verbose(f"[GOOGLE] Searching in {page} page...")
			try:
				req = requests.get(
					url=self.url,
					params=payload,
					headers={'user-agent': self.agent},
					allow_redirects=True)
			except Exception as e:
				style_print.error(f"ConnectionError: {e}", 'util/google', 'run_crawl')
				max_attempt += 1
				if max_attempt == self.limit:
					style_print.error('Google is missed!', 'util/goolge', 'run_crawl')
					break
			else:
				if req.status_code in (503, 429):
					style_print.error('Google CAPTCHA triggered.', 'util/google', 'run_crawl')
					break

				if req.status_code in (301, 302):
					redirect = req.headers['location']
					req = requests.get(url=redirect, allow_redirects=False)

				self._pages += req.text
				if page == 1:
					self._first_page += req.text
				page += 1
				payload['start'] = set_page(page)
				if page >= self.limit:
					break
    
	@property
	def google_card_original(self):
		card_xpath_name = {
			'card': '//div[@id="wp-tabs-container"]',
			'card_content': './/div[@class="kno-rdesc"]',
			'card_info': './/div[@class="rVusze"]'
		}
		xpath = {
			card_xpath_name['card']: [
				card_xpath_name['card_content'],
				card_xpath_name['card_info']
			]
		}
		parser = self.page_parse(self._first_page)
		xpath_results = parser.html_fromstring(xpath)
		output = {'content': '', 'info': []}
		root = xpath_results[card_xpath_name['card']]
		output['content'] = root[card_xpath_name['card_content']][0].text_content()
		for piece in root[card_xpath_name['card_info']]:
			output['info'].append(piece.text_content())
		return output

	@property
	def results_original(self):
		parser = self.page_parse(self._pages)
		xpath_results = parser.html_fromstring(self.xpath_original)
		results = []
		if not xpath_results:
			return results
		root = xpath_results[self.xpath_name_original['results']]
		for i in range(len(root[self.xpath_name_original['results_a']])):
			result = {
				't': root[self.xpath_name_original['results_title']][i].text_content(),
				'a': root[self.xpath_name_original['results_a']][i].get('href'),
				'c': root[self.xpath_name_original['results_cite']][i].text_content(),
				'd': root[self.xpath_name_original['results_content']][i].text_content(),
			}
			results.append(result)
		return results

	@property
	def google_card_legacy(self):
		card_xpath_name = {
			'card': '//div[@class="ezO2md"]',
			'card_content': './/span[@class="qXLe6d FrIlee"]',
			'card_info': './/div[@class="tRBhqc"]'
		}
		xpath = {
			card_xpath_name['card']: [
				card_xpath_name['card_content'],
				card_xpath_name['card_info']
			]
		}
		parser = self.page_parse(self._first_page)
		xpath_results = parser.html_fromstring(xpath)
		output = {'content': '', 'info': []}
		root = xpath_results[card_xpath_name['card']]
		output['content'] = root[card_xpath_name['card_content']
		    ][0].text_content().strip()
		for piece in root[card_xpath_name['card_info']]:
			output['info'].append(piece.text_content().strip())
		return output

	@property
	def results(self):
		parser = page_parse(self._pages)
		xpath_results = parser.html_fromstring(self.xpath_legacy)
		results = []
		if not xpath_results:
			return results
		root = xpath_results[self.xpath_name_legacy['results']]
		for i in range(len(root[self.xpath_name_legacy['results_cite']])):
			a = root[self.xpath_name_legacy['results_a']][i].get('href')
			a = a[7:a.find('&sa=U&ved=')]
			try :
				result = {
					't': root[self.xpath_name_legacy['results_title']][i].text_content(),
					'a': a,
					'c': root[self.xpath_name_legacy['results_cite']][i].text_content(),
					'd': root[self.xpath_name_legacy['results_content']][i].text_content().strip(),
				}
				results.append(result)
			except :
				pass
		return results

	@property
	def pages(self):
		return self._pages

	@property
	def links(self):
		if self.mode == 'legacy':
			links = [x['a'] for x in self.results]
		else:
			links = [x['a'] for x in self.results_original]
		return links

	@property
	def dns(self):
		return page_parse(self._pages).get_dns(self.q, self.links)

	@property
	def emails(self):
		return page_parse(self._pages).get_emails(self.q)

	@property
	def docs(self):
		return page_parse(self._pages).get_docs(self.q, self.links)



class style_print:
    def error(text):
        print(f"{bcolors.FAIL}{text}{bcolors.ENDC}")

    def verbose(text):
        print(f"{bcolors.OKCYAN}{text}{bcolors.ENDC}")

class page_parse:
	def __init__(self, page):
		""" Page parser

			Page  		: web page content
		"""
		self.page = page.decode('utf-8') if isinstance(page, bytes) else page

	@property
	def pclean(self):
		subs = r'<em>|<b>|</b>|</em>|<strong>|</strong>|<wbr>|</wbr>|<span class="vivbold qt0">\
				|%22|<span dir="[\w]+">|</span>|<h\d>|</h\d>|<q>|</q>'
		self.remove_comments
		self.page = re.sub(subs, '', self.page)
		self.page = re.sub(r"%3a", ' ', self.page)
		self.page = re.sub(r"%2f", ' ', self.page)
		self.page = re.sub(r"%2f", ' ', self.page)

	def html_fromstring(self, xpath, parent=None, results={}):
		if self.page == '':
			style_print.error(f"document is nil", 'util/page_parse', 'html_fromstring')
			return False

		if isinstance(xpath, dict):
			for root in xpath:
				results[root] = self.html_fromstring(xpath[root], root)
		elif isinstance(xpath, list):
			results = {}
			for x in xpath:
				results[x] = self.html_fromstring(x, parent)
		else:
			tree = html.fromstring(self.page)
			results = []
			try:
				if parent:
					for node in tree.xpath(parent):
						results += node.xpath(xpath)
				else:
					results = tree.xpath(xpath)
			except:
				style_print.error(f"invalid xpath: {xpath} or {parent}", 'util/page_parse', 'html_fromstring')
		return results

	def dork_clean(self, host):
		# Clear dork's fingerprints
		host = re.sub(r"(['\"]+)|(%40|@)", '', host)
		return host

	def findall(self, reg):
		return re.compile(reg).findall(self.page)

	@property
	def sites(self):
		self.pclean
		reg = re.compile(r'<cite>(.*?)</cite>')
		resp = []
		for itr in reg.findall(self.page):
			resp.append(urlib(itr).netroot)
		return resp

	@property
	def remove_html_tags(self):
		""" Remove html tags with regex"""
		self.remove_comments
		scripts = re.compile(r"<script[^>]*>.*?</script>", 
				flags=re.DOTALL)
		styles = re.compile(r"<style[^>]*>.*?</style>",
				flags=re.DOTALL)
		tags = re.compile(r'<[^>]+>|&nbsp|&amp|&lt|&gt|&quot|&apos')
		self.page = re.sub(tags, '', re.sub(styles, '', re.sub(scripts, '', self.page)))

	@property
	def remove_comments(self):
		self.page = re.sub(r'(?=<!--)([\s\S]*?)-->', '', self.page)
		self.page = re.sub(r'(?=/\*)([\s\S]*?)\*/', '', self.page)

	@property
	def get_networks(self):
		self.pclean
		reg_id = reglib().social_network_ulinks
		resp = {}
		page = self.page.replace('www.', '')
		for i in reg_id:
			if isinstance(reg_id[i], list):
				name = []
				for j in reg_id[i]:
					name += re.findall(j, page)
			else:
				name = re.findall(reg_id[i], page)
			names = []
			for j in name:
				if j not in names:
					names.append(j)
			resp[i] = names
		return resp

	def get_emails(self, host):
		self.pclean
		host = self.dork_clean(host + '.' if '.' not in host else host)
		emails = re.findall(r"[A-z0-9.\-]+@[A-z0-9\-\.]{0,255}?%s" % host, self.page)
		return [x.replace('\\', '') for x in list(set(emails))]

	@property
	def all_emails(self):
		self.pclean
		emails = reglib(self.page).emails
		return emails

	def get_dns(self, host, urls=None):
		if urls:
			data = self.dork_clean(str(urls))
		else:
			self.pclean
			data = self.page

		resp = []
		reg = r"[A-z0-9\.\-%s]+\.%s" % ('%', host.replace('"', '').replace("'", ''))
		for i in re.findall(reg, re.sub(r'\\n', '', data)):
			i = i.replace('\\', '').replace('www.', '')
			if i not in resp and '%' not in resp:
				if i.lower().count(host) > 1:
					i = i.split(host)
					for j in i:
						j = f"{j}{host}"
						resp.append(j)
					continue
				resp.append(i)

		return resp

	def get_docs(self, query, urls=None):
		self.pclean
		if '%' in query:
			query = urlib(query).unquote
		ext = re.search(r'filetype:([A-z0-9]+)', query)
		if ext:
			docs = []
			ext = f".{ext.group(1)}"
			if urls is None:
				urls = self.get_links
			for url in urls:
				if ext in url:
					docs.append(url)
			return list(set(docs))
		else:
			style_print.error("Filetype not specified. Concat 'filetype:doc' to the query")
			return []

	def get_attrs(self, tag, attrs=None):
		if attrs is None:
			attrs = []
		reg = r"['\"\s]([^=][\w\-\d_]+)="
		# Find all attribute names
		if not attrs:
			attrs = re.findall(reg, tag)
		resp = {}
		for attr in attrs:
			if not re.search(fr"{attr.lower()}\s*=", tag.lower()):
				continue
			# Get the first char
			fchar = re.search(fr'{attr}=([\s]+)?.', tag)
			content= False
			if fchar:
				c = fchar.group()[-1:]
				# Get content of attrs
				if c not in "'\"":
					content = re.search(fr'{attr}=([^\s>]+)', tag)
				else:
					content = re.search(fr'{attr}={c}([^{c}]*){c}', tag)
			if content:
				content = content.group(1)
			content = content or ''
			resp[attr.lower()] = content
		return resp

	@property
	def get_metatags(self):
		self.remove_comments
		reg = r"<(?i)meta[^>]+/?>"
		reg = re.compile(reg)
		resp = []
		find = reg.findall(self.page)
		for tag in find:
			tag_attrs = self.get_attrs(tag)
			resp.append(tag_attrs)
		return resp

	@property
	def get_jsfiles(self):
		self.remove_comments
		reg = r"<(?i)script[^>]+>"
		reg = re.compile(reg)
		resp = []
		find = reg.findall(self.page)
		for tag in find:
			tag_attrs = self.get_attrs(tag, ['src'])
			for attr in tag_attrs:
				if 'src' in tag_attrs:
					src = tag_attrs[attr]
					urlib = urlib(src)
					if urlib.check_urlfile('js'):
						resp.append(src)
		return resp

	@property
	def get_cssfiles(self):
		self.remove_comments
		reg = r"<(?i)link[^>]+/>"
		reg = re.compile(reg)
		resp = []
		find = reg.findall(self.page)
		for tag in find:
			tag_attr = self.get_attrs(tag, ['href'])
			for link in tag_attr:
				if 'href' in link:
					href = link.get('href')
					urlib = urlib(href)
					if urlib.check_urlfile('css'):
						resp.append(href)
		return resp

	@property
	def get_links(self):
		self.remove_comments
		reg = r'[\'"](/.*?)[\'"]|[\'"](http.*?)[\'"]'
		reg = re.compile(reg)
		find = reg.findall(self.page)
		links = []
		for link in find:
			link = list(link)
			link.pop(link.index(''))
			link = link[0]
			if not re.search(r'<|>|/>', link):
				link = link.replace('\'', '').replace('"', '')
				links.append(link)
		return links

	@property
	def get_ahref(self):
		self.remove_comments
		reg = re.compile(r'<[aA].*(href|HREF)=([^\s>]+)')
		find = reg.findall(self.page)
		links = []
		for link in find:
			link = list(link)
			link.pop(link.index(''))
			link = link[0]
			links.append(link)
		return links

	@property
	def get_credit_cards(self):
		reg = re.compile(r"[0-9]{4}[ ]?[-]?[0-9]{4}[ ]?[-]?[0-9]{4}[ ]?[-]?[0-9]{4}")
		find = reg.findall(self.page)
		return list(set(find))

	@property
	def get_html_comments(self):
		reg = re.compile(r'<!--(.*?)-->')
		js_reg = re.compile(r'/\*(.*?)\*/')
		find = reg.findall(self.page)
		find.extend(js_reg.findall(self.page))
		return list(set(find))

	@property
	def get_forms(self):
		resp = {}
		self.remove_comments
		reg = re.compile(r'(?i)(?s)<form.*?</form.*?>')
		forms = reg.findall(self.page)
		form_attrs = ['action', 'method', 'name', 'autocomplete', 'novalidate', 'target', 'role']
		input_attrs = ['accept', 'alt', 'disabled', 'form', 'formaction', 'formenctype', 'formmethod',
					   'max', 'maxlength', 'min', 'minlength', 'name', 'pattern', 'readonly', 'required',
					   'selected', 'size', 'src', 'type', 'value', 'for']
		for form in range(len(forms)):
			form_tag = re.compile(r'<(?i)form.*?>')
			form_tag = form_tag.findall(forms[form])[0]
			get_form_attrs = self.get_attrs(form_tag, form_attrs)
			if 'action' not in get_form_attrs:
				get_form_attrs['action'] = '/'
			resp[form] = {'form': get_form_attrs}
			resp[form]['inputs'] = {}
			inputs = re.findall(r'<(?i)input.*?/?>', forms[form])
			textareas = re.findall(r'<textarea.*?>', forms[form])

			for inp in range(len(textareas)):
				inp_attrs = self.get_attrs(textareas[inp], input_attrs)
				if 'textarea' in resp[form]['inputs']:
					resp[form]['inputs']['textarea'].append(inp_attrs)
				else:
					resp[form]['inputs'].update({'textarea': [inp_attrs]})

			for inp in range(len(inputs)):
				inp_attrs = self.get_attrs(inputs[inp], input_attrs)
				if not 'type' in inp_attrs:
					type_attr = 'text'
					inp_attrs['type'] = 'text'

				type_attr = inp_attrs['type'].lower()
				# Set default submit value
				if type_attr == 'submit' and 'value' not in inp_attrs:
					inp_attrs['value'] = 'Submit Query'

				if type_attr in resp[form]['inputs']:
					resp[form]['inputs'][type_attr].append(inp_attrs)
				else:
					resp[form]['inputs'].update({type_attr: [inp_attrs]})

		return resp

class urlib:

	def __init__(self, url):
		""" url parser

			url 	: url string for parse
		"""
		self.url = url

	def join(self, urjoin):
		return urlparse.urljoin(self.url, urjoin)

	def parse(self):
		return urlparse.urlparse(self.url)

	def unparse(self, urparse):
		return urlparse.urlunparse(urparse)

	def sub_service(self, serv=None):
		'''Add protocol to url or replace it or clean it'''
		urparse = re.split(r'://', self.url)
		if not serv:
			# Clean protocol
			url = ''.join(urparse)
		else:
			# Add protocol
			serv = re.sub(r'://', '', serv)
			if len(urparse) == 2:
				del urparse[0]
				url = f"{serv}://{''.join(urparse)}"
			else:
				url = f"{serv}://{urparse[0]}"
		self.url = url
		return url

	def check_urlfile(self, file):
		reg = re.compile(r"\."+file+r"[^\w]")
		reg2 = re.compile(r"\."+file+r"[^\w]?$")
		if reg.search(self.url) or reg2.search(self.url):
			return True
		return False

	@property
	def quote(self):
		if '%' not in self.url:
			self.url = urlparse.quote(self.url)
		return self.url

	@property
	def quote_plus(self):
		if '%' not in self.url:
			self.url = urlparse.quote_plus(self.url)
		return self.url

	@property
	def unquote(self):
		self.url = urlparse.unquote(self.url)
		return self.url

	@property
	def unquote_plus(self):
		self.url = urlparse.unquote_plus(self.url)
		return self.url

	@property
	def ip(self):
		if re.match(r"^\d+.\d+.\d+.\d+$", self.url):
			return self.url
		else:	
			loc = self.netloc
			return gethostbyname(self.netloc)

	@property
	def host(self):
		return gethostbyaddr(self.parse().netloc)[0]

	@property
	def scheme(self):
		return self.parse().scheme

	@property
	def netloc(self):
		return self.parse().netloc

	@property
	def netroot(self):
		loc = self.parse().netloc
		# Replace subdomains
		reg = re.search(r"^[A-z0-9\-.]+\.([A-z0-9\-]+\.[A-z0-9]+)$", loc)
		if reg:
			loc = reg.group(1)
		return loc

	@property
	def path(self):
		return self.parse().path

	@property
	def query(self):
		return self.parse().query

	@property
	def params(self):
		return self.parse().params

	@property
	def fragment(self):
		return self.parse().fragment

	def self_params(self, url):
		url = urlparse.unquote(url)
		queries = urlparse.urlparse(url).query
		page = url.replace('?'+queries, '')
		params = {}
		params[page] = {}
		if not queries:
			return {}

		if '&' in queries:
			queries = queries.split('&')
		else:
			queries = [queries]
		for query in queries:
			if not query:continue
			query = query.split('=')+['']
			name=query[0]
			value=query[1]
			params[page][name] = value
		return params

class reglib:
	def __init__(self, string=None):
		self.string = str(string)

	protocol_s = r"^([A-z0-9]+:\/\/)"
	protocol_m = r"([A-z0-9]+:\/\/)"
	email_s = r"^\w+@[A-z_\-.0-9]{5,255}$"
	email_m = r"\w+@[A-z_\-.0-9]{5,255}"
	phone_s = r"^([0-9]( |-)?)?(\(?[0-9]{3}\)?|[0-9]{3})( |-)?([0-9]{3}( |-)?[0-9]{4}|[A-z0-9]{7})$"
	phone_m = r"([0-9]( |-)?)?(\(?[0-9]{3}\)?|[0-9]{3})( |-)?([0-9]{3}( |-)?[0-9]{4}|[A-z0-9]{7})"
	domain_s = r"^([A-z0-9]([A-z0-9\-]{0,61}[A-z0-9])?\.)+[A-z]{2,6}(\:[0-9]{1,5})*$"
	domain_m = r"[A-z0-9\-]{0,61}\.+[A-z]{2,6}"
	url_s = r"^([A-z0-9]+:\/\/)?(www.|[A-z0-9].)[A-z0-9\-\.]+\.[A-z]{2,6}(\:[0-9]{1,5})*(\/($|[A-z0-9.,;?\'\\+&amp;%$#=~_-]+))*$"
	url_m = r"ftp|https?://[A-z0-9\-.]{2,255}[\/A-z\.:\-0-9%~@#?&()+_;,\']+"
	id_s = r"^@[A-z_0-9\.\-]{2,255}$"
	id_m = r"@[A-z_0-9\.\-]{2,255}"
	ip_s = r"^\d+\.[\d]+\.[\d]+\.[\d]+$"
	ip_m = r"\d+\.[\d]+\.[\d]+\.[\d]+"
	social_network_ulinks = {
		'Instagram': r"instagram\.com/[A-z_0-9.\-]{1,30}",
		'Facebook': [r"facebook\.com/[A-z_0-9\-]{2,50}", r"fb\.com/[A-z_0-9\-]{2,50}"],
		'Twitter': r"twitter\.com/[A-z_0-9\-.]{2,40}",
		'Github': r"github\.com/[A-z0-9_-]{1,39}",
		'Github site': [r"[A-z0-9_-]{1,39}\.github\.io", r"[A-z0-9_-]{1,39}\.github\.com"],
		'Telegram': r"telegram\.me/[A-z_0-9]{5,32}",
		'Youtube user': r"youtube\.com/user/[A-z_0-9\-\.]{2,100}",
		'Youtube channel': [r"youtube\.com/c/[A-z_0-9\-\.]{2,100}", \
				r"youtube\.com/channel/[A-z_0-9\-\.]{2,100}"],
		'Linkedin company': r"linkedin\.com/company/[A-z_0-9\.\-]{3,50}",
		'Linkedin individual': r"linkedin\.com/in/[A-z_0-9\.\-]{3,50}",
		'Googleplus': r"\.?plus\.google\.com/[A-z0-9_\-.+]{3,255}",
		'WordPress': r"[A-z0-9\-]+\.wordpress\.com",
		'Reddit': r"reddit\.com/user/[A-z0-9_\-]{3,20}",
		'Tumblr': r"[A-z0-9\-]{3,32}\.tumblr\.com",
		'Blogger': r"[A-z0-9\-]{3,50}\.blogspot\.com"
		}

	def search(self, regex, _type=list):
		regex = re.compile(regex)
		regex = regex.findall(self.string)
		return regex

	def sub(self, regex, sub_string):
		data = re.sub(regex, sub_string, self.string)
		return data
	
	def filter(self, regex, _list: list) -> list:
		if not isinstance(regex, str):
			return filter(regex, _list)
		else:
			return filter(re.compile(regex).match, _list)

	@property
	def emails(self):
		emails = self.search(self.email_m)
		return emails
	
	@property
	def urls(self):
		urls = self.search(self.url_m)
		return urls
	
	@property
	def domains(self):
		domains = self.search(self.domain_m)
		return domains

if __name__ == "__main__":
    run = google(q="f**k the world")
    run.run_crawl()
    results = [ res['a'] \
        for res in run.results \
        if not res['a'].startswith('https://www.youtube.com/')]
    import pprint
    pprint.pprint(results)            
   
    
