import http.client
import requests
import time
from bs4 import BeautifulSoup
import base64
import PyPDF2
import pyttsx3
from gtts import gTTS
import os
os.add_dll_directory(r"C:\Program Files\GTK3-Runtime Win64\bin")
from weasyprint import HTML, CSS


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
        <body>
            <div class='book'>
        """.replace('{title}', title)


def get_css():
    return """
            body {
                width: 90%;
                background-color: rgba(255, 255, 255, 0);                
                font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
                text-align: left !important;
                margin: 0px auto 0px auto !important;
            }
            
            .container { 
                margin: 50px auto 40px auto; 
                width: 100%; 
                text-align: center; 
            }    
            a { color: #4183c4; text-decoration: none; }
            a:hover { text-decoration: underline; }
    
            h1 { 
                width: 90%; 
                text-align: center !important; 
                letter-spacing: -1px; 
                line-height: 1.7em; 
                font-size: 1.8em; 
                font-weight: bold; 
                margin: 200px 0 40px 0 !important; 
                text-shadow: 0 1px 0 #fff; 
            }
            
            h2 { 
                width: 90%; 
                text-align: left !important; 
                letter-spacing: -1px; 
                line-height: 15px; 
                font-size: 1.5em; 
                font-weight: 100; 
                margin: 80px 0 20px 0; 
                text-shadow: 0 1px 0 #fff; 
            }
            
            p {
                text-align: justify !important;                  
                margin: 20px 0; 
                line-height: 1.6; 
                font-size: 1em; 
                color: #606060;
            }
            
            ul { 
                list-style: none; 
                margin: 5px 0; 
                padding: 0; 
                line-height: 1.3em;
            }
            
            ol { 
                margin: 5px 0; 
                padding: 0; 
                line-height: 1.3em;
            }    
                                
            div.toctree-wrapper ol{ list-style: none; } 
            
            li { 
                text-align: left; 
                font-weight: bold;                 
            }  
            
            ol.arabic li {                  
                margin: 15px 0 0 40px;
            }  
                     
            .logo { display: inline-block; margin-top: 10px; }
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
            
            a::after {
                content: " (" attr(alt) ") ";
            }
            
            pre {
                white-space: pre-wrap;
            }
            
            img{
                z-index: 1000 !important;
                filter: contrast(120%);
                filter: contrast(120%);
            }
            img[src~="png"]{                
            }
            
            @page {
                padding: 0 !important;
                margin: 60px 10px 30px 10px !important;
                size: Letter;
                @top-right {
                    content: 'launch_code';
                    display: block;
                    position: absolute;
                    top: 20px;
                    right: 10px;
                    margin: 10px 10px;
                    color: #505633;
                }
                @bottom-right {
                    content: counter(page);
                    position: absolute !important;
                    right: 100px !important;
                    bottom: 50px !important;
                    font-size: 0.6em !important;
                    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
                }
            }
            
            @page :first {
                @top-right {
                    content: "";
                }
            }
            
            tr:nth-child(odd){
                background: #fffff1;
            }
            
            #java-naming-conventions table.docutils {
                display: table;
                width: 100% !important;
                border-collapse: collapse;                
                border-style: none;
                border-width: 20px;
                border: none;                
                font-size: 0.9;                
                text-align: start;                
                border-color: transparent; 
            }
            
            #java-naming-conventions table.docutils th, 
            #java-naming-conventions table.docutils td{
                padding: 20px 30px !important;
                
            }
            #java-naming-conventions table.docutils td{                
                overflow: hidden; 
                width: 33.3% !important; 
            }            
            .last-copy-right{
                text-align: center;
            }
    """


def get_footer():
    return """    
        <p class='last-copy-right'> LC101 April 2022 <p>'
        </div>
    </body></html>
    """


def parse_dom(html):
    return BeautifulSoup(html, 'html.parser')


def get_dom_from_html(html_code):
    try:
        dom = parse_dom(html_code)
        return dom
    except:
        return None


def save(title, extension, data):
    if extension == 'pdf':
        open(f'downloads/{title}.{extension}', 'wb').write(data)
    else:
        open(f'downloads/{title}.{extension}', 'w', encoding="utf-8").write(data)
    print(f'PDF file: {title}.{extension} was saved.')


def save_as_html(html, title):
    save(title, 'html', html)


def save_as_pdf(html, title):
    print('Saving PDF (Sorry this is slow)...')
    css = CSS(string=get_css())
    pdf = HTML(string=html).write_pdf(stylesheets=[css])
    save(title, 'pdf', pdf)


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
            image.decompose()
            continue
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


def clean_content():
    global full_content
    dom = get_dom_from_html(full_content)

    tag_types_to_decompose = [
        dom.findAll('form'),
        dom.findAll('p', {'class': 'pull-right'}),
        dom.findAll('a', {'class': 'navbar-brand'}),
        dom.findAll('li', {'class': 'previous'}),
        dom.findAll('li', {'class': 'next'}),
        dom.findAll('button', {'class': 'navbar-toggle'}),
        dom.findAll('a', {'class': 'headerlink'}),
        dom.findAll('a', {'class': 'pagination-sm'}),
        dom.findAll('nav', {'id': 'toc-toggle'})
    ]
    for tag_list in tag_types_to_decompose:
        for tag in tag_list:
            tag.decompose()

    full_content = dom.decode_contents()


def add_content_from_url(url):
    global full_content
    dom = get_dom_from_html(fetch_test(url))
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


def test_all_voices(engine):
    voices = engine.getProperty('voices')
    for voice in voices:
        engine.setProperty('voice', voice.id)
        engine.say('Amazing grace, how sweet the sound that saved a wretch like me...')
        engine.runAndWait()


def google_text_to_speach(text, title):
    print(f'Creating audio book from pdf.')
    tts = gTTS(text=text, lang='en')
    tts.save(f'downloads/{title}.mp3')
    print(f'Done.')


def python_text_to_speach(title):
    if not os.path.exists(f'downloads/{title}.pdf'):
        print(f'Document downloads/{title}.pdf not found.')
        return

    print(f'Creating audio book from pdf.')
    engine = pyttsx3.init(driverName='sapi5')
    engine.setProperty('rate', 180)
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)

    print(f'Loading pdf file {title}.pdf ...')
    pdf_reader = PyPDF2.PdfFileReader(open(f'downloads/{title}.pdf', 'rb'))
    text = ''
    total_pages = pdf_reader.numPages

    chunk_size = 100
    chunks = int(total_pages / chunk_size)
    chunks = chunks if chunks % 100 == 0 else chunks + 1
    for chunk in range(chunks):
        text = ''
        start_page = chunk * chunk_size
        end_page = (chunk + 1) * chunk_size
        end_page = end_page if end_page < total_pages else total_pages
        print(f'Processing pages {start_page} - {end_page}...')
        for page_num in range(start_page, end_page):
            if page_num > total_pages: break
            text += (pdf_reader.getPage(page_num).extractText())

            percentage = int(100 * page_num / total_pages)
            arrow = '=' * percentage + '>'
            blank_space = ' ' * (100 - len(arrow))
            print(f'Loading... {arrow}{blank_space} [{percentage}%]', end='\r')
        print(f'Done Loading.')

        modified_title = title.replace(' ', '_')
        print(f'Saving audio book {modified_title}_{chunk}.mp3 ...')
        create_folder(f'downloads/{modified_title}')
        engine.save_to_file(text, f'downloads/{modified_title}/{modified_title}_{chunk}.mp3')
        engine.runAndWait()
        print(f'Done Saving audiobook part {chunk}.')
    engine.stop()


def create_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)


def create_audio_book(title):
    time.sleep(1)
    python_text_to_speach(title)


def init():
    global is_first_time
    global url_path
    is_first_time = True
    url_path = ''


def save_intro_book(make_audiobook=False):
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
    clean_content()
    #save_as_html(full_content, title)
    save_as_pdf(full_content, title)
    if make_audiobook:
        create_audio_book(title)


def save_java_book(make_audiobook=False):
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
    clean_content()
    # save_as_html(full_content, title)
    save_as_pdf(full_content, title)
    if make_audiobook:
        create_audio_book(title)


def truncate(n, decimals=0):
    multiplier = 10 ** decimals
    return int(n * multiplier) / multiplier


def seconds_to_time(seconds):
    milliseconds = int(truncate(seconds - int(seconds), 3) * 1000)
    minutes = int(seconds / 60)
    hours = int(minutes / 60)
    minutes = minutes % 60
    seconds = int(seconds % 60)
    return f'{str(hours).zfill(2)}h:{str(minutes).zfill(2)}mm:{str(seconds).zfill(2)}secs:{str(milliseconds).zfill(3)}millis'


def main():
    save_intro_book(make_audiobook=True)
    save_java_book(make_audiobook=True)
    print('Enjoy!')


if __name__ == '__main__':
    start_time = time.time()
    main()
    print("--- Execution time: %s ---" % (seconds_to_time(time.time() - start_time)))
