import requests, json, os, argparse
from bs4 import BeautifulSoup

url = 'https://registration.boun.edu.tr/scripts/sch.asp?donem={year}/{year_plus_1}-{term}&kisaadi={short_name}&bolum={dept}'

parser = argparse.ArgumentParser()
parser.add_argument('--year', type=int, default=2013)
parser.add_argument('--short-name', type=str)
parser.add_argument('--dept', type=str)
args = parser.parse_args()

year = 2013
year_plus_1 = year + 1
short_name = args.short_name.upper()
dept = args.dept.upper()
dept_url = dept.replace(' ', '+')
term = 1

filepath = 'course_l.json'
if os.path.exists(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        course_l = json.load(f)
else:
    course_l = list()

def get_d(tr):
    td_l = tr.find_all('td')
    course_code = td_l[code_index].text.replace(' ', '').strip()
    course_name = td_l[name_index].text.strip()
    instructor = td_l[instructor_index].text.strip()
    d_t = {'course_code': course_code, 'course_name': course_name, 'instructor': instructor, 'dept': dept, 'semester': semester}
    if d_t in course_l or course_code == '': # already exists or no course code
        return -1
    else:
        return d_t

while year < 2023:
    r = requests.get(url.format(year=year, year_plus_1=year_plus_1, short_name=short_name, term=term, dept=dept_url))
    semester = f'{year}/{year_plus_1}-{term}'
    content_t = r.content
    soup = BeautifulSoup(content_t, 'html.parser')
    tr_title_l = soup.find_all('tr', {'class': 'schtitle'})
    code_index, name_index, instructor_index = 0, 0, 0
    for tr_title in tr_title_l:
        td_title_l = tr_title.find_all('td')
        for i, td_title in enumerate(td_title_l):
            if 'code' in td_title.text.lower():
                code_index = i
            elif 'name' in td_title.text.lower():
                name_index = i
            elif 'instr' in td_title.text.lower():
                instructor_index = i
    tr_grey_l = soup.find_all('tr', {'class': 'schtd2'})
    tr_white_l = soup.find_all('tr', {'class': 'schtd'})
    course_cnt = len(tr_grey_l) + len(tr_white_l)
    grey_cnt, white_cnt = 0, 0
    for i in range(max(len(tr_grey_l), len(tr_white_l))):
        if i < len(tr_grey_l):
            d_t = get_d(tr_grey_l[i])
            grey_cnt += 1
            if d_t != -1:
                course_l.append(d_t)
        if i < len(tr_white_l):
            d_t = get_d(tr_white_l[i])
            white_cnt += 1
            if d_t != -1:
                course_l.append(d_t)
    if term == 3:
        term = 1
        year += 1
        year_plus_1 += 1
    else:
        term += 1

with open(filepath, 'w', encoding='utf-8') as f:
    json.dump(course_l, f, indent=4, ensure_ascii=False)
