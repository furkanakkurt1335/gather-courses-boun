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

filepath = 'course_d.json'
if os.path.exists(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        course_d = json.load(f)
else:
    course_d = dict()

while year < 2023:
    r = requests.get(url.format(year=year, year_plus_1=year_plus_1, short_name=short_name, term=term, dept=dept_url))
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
    tr_l = soup.find_all('tr', {'class': 'schtd2'})
    for tr in tr_l:
        td_l = tr.find_all('td')
        course_code = td_l[code_index].text.replace(' ', '').strip()
        course_name = td_l[name_index].text.strip()
        instructor = td_l[instructor_index].text.strip()
        print(course_code, course_name, instructor, dept, f'{year}/{year_plus_1}-{term}')
        key_t = f'{course_code} - {year} - {term}'
        if key_t in course_d.keys():
            print('Already exists', key_t)
        elif course_code == '':
            print('No course code')
        else:
            course_d[f'{course_code} - {year} - {term}'] = {'course_code': course_code, 'course_name': course_name, 'instructor': instructor, 'dept': dept, 'semester': f'{year}/{year_plus_1}-{term}'}
    if term == 3:
        term = 1
        year += 1
        year_plus_1 += 1
    else:
        term += 1

with open('course_d.json', 'w', encoding='utf-8') as f:
    json.dump(course_d, f, indent=4, ensure_ascii=False)
