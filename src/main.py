from urllib import request
from bs4 import BeautifulSoup
import re
import csv
from functional import seq

def parse_details(details):
    details.strip(' ')
    split_ind = details.find(',')

    org = details[:split_ind].strip(' \,\.')
    address = details[split_ind:].strip(' \,\.')
    return (org, address)


def get_phone(info):
    pattern = re.compile(".*?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).*?")
    match = re.match(pattern, info)

    try:
        return (match.group(0).strip(' '))

    except:
        return None


def is_email(arg):
    if arg == None:
        return False

    if arg.find('@') != -1:
        return True

    return False


def parse_info(arg):
    if arg == None: return None

    start = arg.find('>')
    end = arg.find('<', start)

    return arg[start + 1:end]


def get_info(info):
    info_ind = info.find('<a')
    link, contact = None, None

    if info_ind == -1:
        return None, None

    split_info = info[info_ind:].split(',')

    try:
        arg1, arg2 = split_info[0], split_info[1]
    except:
        arg1, arg2 = split_info[0], None

    arg1 = parse_info(arg1)
    arg2 = parse_info(arg2)

    if is_email(arg1):
        link, contact = arg2, arg1

    else:
        link, contact = arg1, arg2

    return (link, contact)


# we are converting from cleaned paragraph strings to lists here
def parse_paragraph(paragraph):
    org, org_link, contact, phone, address = None, None, None, None, None

    para_split = paragraph.split('Information:')

    # real lazy right here
    try:
        details, info = para_split[0], para_split[1]
    except:
        details, info = para_split[0], None

    org, address = parse_details(details)

    if info != None:
        org_link, contact = get_info(info)
        phone = get_phone(info)

    return [org, org_link, contact, phone, address]


# for cleaning this awful looking paragraphs
def convert_paragraph(paragraph):
    line = str(paragraph).strip('\n \<p>\</p>')
    line = line.strip('.')

    if line.find('Return to top') != -1:
        return False

    return parse_paragraph(line)


def scrape(url):
    with open('exported_details.csv', 'w') as csvfile:
        fieldnames = ['Organization', 'Organization Link', 'Contact', 'Phone', 'Address']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        page = request.urlopen(url)
        soup = BeautifulSoup(page, 'html.parser')

        all_paragraphs = soup.find_all('p')
        organization_info = (all_paragraphs[:253] + all_paragraphs[266:])[1:]

        results = seq(organization_info) \
            .map(convert_paragraph) \
            .filter(lambda line: line != False)

        for result in results:
            writer.writerow(dict(zip(fieldnames, result)))


def test():
    info = '443-764-5525, <a href="http://www.uproarchurch.org" target="_blank">www.uproarchurch.org</a>, <a href="mailto:uproarchurch1@gmail.com">uproarchurch1@gmail.com</a>'
    print(get_info(info))


if __name__ == "__main__":
    # test()

    scrape_page = 'http://www.carrollcountytimes.com/carrollliving/ph-cc-living-religion-20170622-story.html'
    scrape(scrape_page)
