# Import Splinter, BeautifulSoup, and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt

def scrape_all():
   # Initiate headless driver for deployment
   browser = Browser("chrome", executable_path="chromedriver", headless=True)

   news_title, news_paragraph = mars_news(browser)
   # Run all scraping functions and store results in dictionary
   data = {
    "news_title": news_title,
    "news_paragraph": news_paragraph,
    "featured_image": featured_image(browser),
    "facts": mars_facts(),
    "last_modified": dt.datetime.now(),
    "hemisphere_data": hemisphere_data(browser)
   }
    # Stop webdriver and return data
   browser.quit()
   return data


def mars_news(browser):
    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    try:
        slide_elem = news_soup.select_one('ul.item_list li.slide')
        # Use the parent element to find the first a tag and save it as `news_title`
        news_title = slide_elem.find("div", class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_="article_teaser_body").get_text()

    except AttributeError:
        return None, None
    
    return news_title, news_p

### JPL Space Images Featured Image

# Visit URL

def featured_image(browser):

    url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    try:
        # find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
    
    except AttributeError:
        return None
   

    # Use the base url to create an absolute url
    img_url = f'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/{img_url_rel}'

    return img_url
    

    ### Mars Facts

def mars_facts(): 
    try:
        df = pd.read_html('http://space-facts.com/mars/')[0]
    
    except BaseException:
        return None
    
    df.columns=['Description', 'Mars']
    df.set_index('Description', inplace=True)

    
    return df.to_html(classes="table table-striped")


def hemisphere_data(browser):
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    hemisphers_html = browser.html
    hemisphere_soup = soup(hemisphers_html, 'html.parser')

    hemisphere_image_urls = []

    hemispheres = hemisphere_soup.select_one('div', class_='collapsible-results')

    try:
        for hemisphere in hemispheres: 
    
            browser.is_element_present_by_text('Enhanced', wait_time=1)
            image_link = browser.links.find_by_partial_text('Enhanced')
            image_link.click()

            title = hemisphere_soup.find('h2', class_= 'title').text

            wide_image = hemisphere_soup.find('img', class_='wide-image')['src']
    
            image_url = f'https://astrogeology.usgs.gov/{wide_image}'

            hemisphere_image_urls.append({"Title": title, "Image": image_url})

    except AttributeError:
        return None

    return hemisphere_image_urls

    
    
if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())



