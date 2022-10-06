import http.client
import requests
import time
from bs4 import BeautifulSoup

import os

os.add_dll_directory(r"C:\Program Files\GTK3-Runtime Win64\bin")
from weasyprint import HTML


def fetch_old(url):
    host = url.replace('https://', '').split("/")[0]
    print(f'Clean URL: {host}')
    connection = http.client.HTTPSConnection(host=host, port=443, timeout=50)

    endpoint = url.replace('https://', '').replace(host, '')
    connection.request('GET', endpoint)
    response = connection.getresponse()
    print('Status: {} and reason: {}'.format(response.status, response.reason))
    connection.close()
    return response.read().decode()


url_path = ''


def correct_url(url):
    global url_path
    if url == '':
        return ''
    url = url.replace(' ', '')

    if url in ['stash.html', 'tidy-repos.html']:
        url = 'git/' + url

    if 'https://' not in url and 'index.html' in url and '/' in url:
        if '../' in url:
            url = url.replace('../', '')
            url_path = url_path[:len(url_path) - 1]
            url_path = url_path[:url_path.rfind('/') + 1]

        url_path = url_path + url.split('/')[0] + '/'
        url = url.split('/')[1]

    elif 'https://' in url:
        url_path = url[:url.rfind('/') + 1]
        return url
    elif '../' in url:
        url = url.replace('../', '')
        if 'feedback.html' in url:
            url_path = url_path[:len(url_path) - 1]
            url_path = url_path[:url_path.rfind('/') + 1]
        elif '/' in url:
            url_path = url_path[:url_path[:len(url_path) - 1].rfind('/') + 1] + url.split('/')[0] + '/'
            url = url.split('/')[1]

    url = url_path + url

    return url


def fetch_test(url):
    response = requests.get(url)
    return response.text


def get_header(title):
    return """
    <html>
        <head>
            <title>{title}</title>
        </head>
        <style type=\"text/css\" media=\"screen\">
            body {
                background-color: #f1f1f1;
                margin: 0;
                font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
            }
            .container { margin: 50px auto 40px auto; width: 600px; text-align: center; }
    
            a { color: #4183c4; text-decoration: none; }
            a:hover { text-decoration: underline; }
    
            h1 { width: 800px; position:relative; left: -100px; letter-spacing: -1px; line-height: 60px; font-size: 60px; font-weight: 100; margin: 0px 0 50px 0; text-shadow: 0 1px 0 #fff; }
            p { color: rgba(0, 0, 0, 0.5); margin: 20px 0; line-height: 1.6; }
            
            ul { list-style: none; margin: 25px 0; padding: 0; }
            li { display: table-cell; font-weight: bold; width: 1%; }
            
            .logo { display: inline-block; margin-top: 35px; }
            .logo-img-2x { display: none; }
          
            #suggestions {
                margin-top: 35px;
                color: #ccc;
            }
            #suggestions a {
                color: #666666;
                font-weight: 200;
                font-size: 14px;
                margin: 0 10px;
            }    
        </style>
        <body>""".replace('{title}', title)


def get_footer():
    return """    
    <p> LC101 April 2022 <p>'
    </body></html>
    """


def parse_dom(html):
    return BeautifulSoup(html, 'html.parser')


def process_url(url):
    try:
        html_code = fetch_test(url)
        dom = parse_dom(html_code)
        return dom
    except:
        return None


def save_as_pdf(html, title):
    print('Saving PDF (Sorry this is slow)...')
    pdf = HTML(string=html).write_pdf()
    open(title + '.pdf', 'wb').write(pdf)
    print(f'PDF file: {title}.pdf was saved.')


is_first_time = True
full_content = ''


def load_images(dom, content):
    return content


def scrap(index, first, last):
    global is_first_time
    global full_content
    print('Starting scrapping new document...')

    if is_first_time:
        is_first_time = False
        dom = process_url(index)
        full_content += dom.find('body').decode_contents()

    url = first
    step_counter = 0
    while True:
        # time.sleep(0.03)
        step_counter += 1
        url = correct_url(url)
        print(f'Step: {step_counter} : {url}')

        dom = process_url(url)
        content = dom.find('body').decode_contents()
        content = load_images(dom, content)
        full_content += '' if dom is None else content

        if step_counter >= 2000 or url == last or url == '':
            if url == '':
                print('There was an error in the last step processed.')
            else:
                print('Scrapper found last page.')
            break

        next_anchor = dom.find("li", {"class": "next"})
        next_anchor = next_anchor.findChild() if next_anchor is not None else None
        url = '' if next_anchor is None else next_anchor.get('href')

    print("Finished scrapping document.")


def saveIntroBook():
    global full_content
    title = 'Introduction to Professional Web Development in JavaScript'
    full_content = get_header(title)

    index = 'https://education.launchcode.org/intro-to-professional-web-dev/index.html'
    first = 'https://education.launchcode.org/intro-to-professional-web-dev/chapters/introduction/index.html'
    last = 'https://education.launchcode.org/intro-to-professional-web-dev/chapters/booster-rockets/brainbreak.html'
    scrap(index, first, last)

    # Intro-TextBook-Studios
    # first = 'https://education.launchcode.org/intro-to-professional-web-dev/chapters/data-and-variables/studio.html'
    # last = 'https://education.launchcode.org/intro-to-professional-web-dev/chapters/angular-lsn3/studio.html'
    # scrap(index, first, last)
    #
    # # Intro-TextBook-Assignments
    # first = 'https://education.launchcode.org/intro-to-professional-web-dev/assignments/candidateQuiz.html'
    # last = 'https://education.launchcode.org/intro-to-professional-web-dev/assignments/orbit-report/orbit-report.html'
    # scrap(index, first, last)
    #
    # # Intro-TextBook-Appendices
    # first = 'https://education.launchcode.org/intro-to-professional-web-dev/appendices/about-this-book.html'
    # last = 'https://education.launchcode.org/intro-to-professional-web-dev/appendices/feedback.html'
    # scrap(index, first, last)

    full_content += get_footer()
    # print(full_content)
    save_as_pdf(full_content, title)


def saveJavaBook():
    pass


def main():
    saveIntroBook()
    saveJavaBook()
    print('Enjoy!')


if __name__ == '__main__':
    main()
