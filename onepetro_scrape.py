# Version 0.1 - pilot

# Import dependencies
from bs4 import BeautifulSoup
import requests
import pandas as pd


class Scraper():

    def __init__(self):
        """Initialize Scraper object"""

        # queryflag attribute for mandatory query method activation
        self.queryflag = False
        return None

    
    def query(self, **kwargs):
        """
		Mandatory query method.

		Parameters:
		-----------
			search : string
				Main subject search query
			published_from_year : string
				Search from defined year
			published_to_year : string
				Search until defined year
			verbose : boolean
				Display result summary text. Default is True.

		Attributes:
		-----------
			Scraper.published_from_year
			Scraper.published_to_year
			Scraper.url
			Scraper.total_results
        """
        
        self.queryflag = True
        # read search query with exception handling
        try:
            self.search = kwargs.pop('search').replace(' ', '+')
        except KeyError as err:
            print("KeyError : {}. Please enter search query.".format(err))
        # read other search parameters
        self.published_from_year = kwargs.pop('published_from_year', '')
        self.published_to_year = kwargs.pop('published_to_year', '')
        self.published_between = 'on' if (self.published_from_year!='' or self.published_to_year!='') else ''
        # request search query to https://www.onepetro.org/
        self.url = 'https://www.onepetro.org/search?q='+self.search \
                    +'&peer_reviewed=&published_between='+self.published_between \
                    +'&from_year='+str(self.published_from_year) \
                    +'&to_year='+str(self.published_to_year) #\
        self.total_results = int(BeautifulSoup(requests.get(self.url).text, 'lxml')\
                             .find('h2').getText().split()[-2].replace(',', ''))
        # search result verbose 
        if kwargs.pop('verbose', True):
            if self.published_between == '':
                print(('Search results: Your search for {} '
                      + 'has returned {} results.')\
                      .format(self.search,
                              self.total_results))
            else:
                print(('Search results: Your search for {}, '
                      + 'published between {} and {} '
                      + 'has returned {} results.')\
                      .format(self.search,
                              self.published_from_year, self.published_to_year,
                              self.total_results))

                
    def extract(self, rows=100, verbose=True):
        """
		Extract paper details.

		Parameters:
		-----------
			rows : integer
				Define the quantity of papers to be extracted.
				Sorted by onepetro default (most relevant)
			verbose : boolean
				Display progress status. Default is True.

		Attributes:
		-----------
			Scraper.papers
        """
        
        if self.queryflag: # manual exception handling for queryflag attribute error
            # request the papers for detail extraction
            rows = self.total_results if rows=='all' else rows
            self.url += '&rows='+str(rows)
            bs = BeautifulSoup(requests.get(self.url).text, 'lxml')
            # begin extraction
            self.papers = []
            for count,a in enumerate(bs.find_all('h3', {'class':'book-title'})):
                print('Extracting {} of {}'.format(count+1, rows)) if verbose else None
                url = a.find('a')['href']
                bs_paper = BeautifulSoup(requests.get(url).text, 'lxml')
                title = bs_paper.find('h1', {'class':'document-title'}).getText().strip()
                div = bs_paper.find('div', {'class':'highlighted'})
                div = bs_paper.find('div', {'class':'indent-main-section'}) if div==None else div
                headers = [x.getText() for x in div.find_all('dl')[0].find_all('dt')]
                details = [x.getText() for x in div.find_all('dl')[0].find_all('dd')]
                details_edited = []
                for item in map(lambda x: x.split(), details):
                    details_edited.append(' '.join(item).split('|'))
                series = pd.Series(title, index=['Title'])
                for i,head in enumerate(headers):
                    series[head] = details_edited[i]
                self.papers.append(series)
            print('Extraction complete')
        else:
            raise AttributeError("'Scrap' object has no attribute 'query'")
        