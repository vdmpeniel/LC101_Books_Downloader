import http.client
import requests
import time
from bs4 import BeautifulSoup
import base64

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

    # if url in ['stash.html', 'tidy-repos.html']:
    #     url = 'git/' + url

    if 'https://' in url:
        url_path = url[:url.rfind('/') + 1]
        return url
    elif '../' in url:
        url = url.replace('../', '')
        if '/' in url:
            url_path = url_path[:url_path[:len(url_path) - 1].rfind('/') + 1] + url.split('/')[0] + '/'
            url = url.split('/')[1]
        else:
            url_path = url_path[:len(url_path) - 1]
            url_path = url_path[:url_path.rfind('/') + 1]

    elif 'https://' not in url and '/' in url:
        if '../' in url:
            url = url.replace('../', '')
            url_path = url_path[:len(url_path) - 1]
            url_path = url_path[:url_path.rfind('/') + 1]

        if '/' in url:
            url_path = url_path + url.split('/')[0] + '/'
            url = url.split('/')[1]




    url = url_path + url

    return url


def fetch_test(url, is_byte=False):
    response = requests.get(url)
    return response.content if is_byte else response.text


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
        <body>
            <div class='book'>
        """.replace('{title}', title)


def get_footer():
    return """    
        <p> LC101 April 2022 <p>'
        </div>
    </body></html>
    """


def parse_dom(html):
    return BeautifulSoup(html, 'html.parser')


def get_dom_from_url(url):
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


def load_images(dom):
    images = dom.findAll('img')
    # print(len(images))

    for image in images:
        original_source = image.get('src')
        if '.' not in original_source:
            continue

        if image.get('width') is not None:
            image['width'] = None
            image['height'] = None

        if 'lc-ed-logo.png' in original_source:
            source = 'http://stpeteedc.com/wp-content/uploads/2018/08/launchcode-01.png'
            image['style'] = 'display: block; max-width:30%; height:auto; display: -webkit-box; margin: 0 0 0 auto;'
        else:
            source = url_path.split("chapters")[0] + original_source.replace('../', '')
            image['style'] = 'display: block; max-width:100%; height:auto; margin-left: auto; margin-right: auto;'

        image_content = fetch_test(source, True)
        encoded_image = base64.b64encode(image_content)
        extension = original_source.replace('../', '').split('.')[1]
        encoded_source = f'data:image/{extension};base64,' + encoded_image.decode('utf-8')

        image['src'] = encoded_source
    # print(content)
    return dom


def clean_dom(dom):
    all_forms = dom.findAll('form')
    for form in all_forms:
        form.decompose()

    all_ps = dom.findAll('p', {'class': 'pull-right'})
    for p in all_ps:
        p.decompose()
    return dom


def add_content_from_url(url):
    global full_content
    dom = get_dom_from_url(url)
    dom = clean_dom(dom)
    dom = load_images(dom)
    full_content += '' if dom is None else dom.find('body').decode_contents()
    return dom


def scrap(index, first, last):
    global is_first_time
    global full_content
    print('Starting scrapping new document...')

    if is_first_time:
        is_first_time = False
        add_content_from_url(index)

    url = first
    step_counter = 0
    while True:
        # time.sleep(0.03)
        step_counter += 1
        url = correct_url(url)
        print(f'Step: {step_counter} : {url}')

        dom = add_content_from_url(url)

        if step_counter >= 1000 or url == last or url == '':
            if url == '':
                print('There was an error in the last step processed.')
            else:
                print('Scrapper found last page.')
            break

        next_anchor = dom.find("li", {"class": "next"})
        next_anchor = next_anchor.findChild() if next_anchor is not None else None
        url = '' if next_anchor is None else next_anchor.get('href')

    print("Finished scrapping document.")


def init():
    global is_first_time
    global url_path
    is_first_time = True
    url_path = ''


def save_intro_book():
    global full_content
    init()
    
    title = 'Introduction to Professional Web Development in JavaScript'
    full_content = get_header(title)

    print('\n\n' + title)
    index = 'https://education.launchcode.org/intro-to-professional-web-dev/index.html'
    first = 'https://education.launchcode.org/intro-to-professional-web-dev/chapters/introduction/index.html'
    last = 'https://education.launchcode.org/intro-to-professional-web-dev/chapters/booster-rockets/brainbreak.html'
    scrap(index, first, last)

    print('\n\nIntro-TextBook-Assignments')
    first = 'https://education.launchcode.org/intro-to-professional-web-dev/assignments/candidateQuiz.html'
    last = 'https://education.launchcode.org/intro-to-professional-web-dev/assignments/orbit-report/orbit-report.html'
    scrap(index, first, last)

    print('\n\nIntro-TextBook-Appendices')
    first = 'https://education.launchcode.org/intro-to-professional-web-dev/appendices/about-this-book.html'
    last = 'https://education.launchcode.org/intro-to-professional-web-dev/appendices/feedback.html'
    scrap(index, first, last)

    full_content += get_footer()
    save_as_pdf(full_content, title)


def save_java_book():
    global full_content
    init()

    title = 'Java Web Development'
    full_content = get_header(title)

    print('\n\n' + title)
    index = 'https://education.launchcode.org/java-web-development/index.html'
    first = 'https://education.launchcode.org/java-web-development/chapters/introduction-and-setup/index.html'
    last = 'https://education.launchcode.org/java-web-development/chapters/auth/index.html'
    scrap(index, first, last)

    print('\n\nJava Assignments')
    first = 'https://education.launchcode.org/java-web-development/assignments/hello-world.html'
    last = 'https://education.launchcode.org/java-web-development/assignments/tech-jobs-persistent.html'
    scrap(index, first, last)

    print('\n\nJava Appendices')
    first = 'https://education.launchcode.org/java-web-development/appendices/about-this-book.html'
    last = 'https://education.launchcode.org/java-web-development/appendices/exercise-solutions/orm-relationships.html'
    scrap(index, first, last)

    full_content += get_footer()
    save_as_pdf(full_content, title)


def main():
    save_intro_book()
    save_java_book()
    print('Enjoy!')


if __name__ == '__main__':
    main()
