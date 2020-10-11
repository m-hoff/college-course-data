import re
import time

from bs4 import BeautifulSoup
import pandas as pd
import requests

def get_programs(
    url='https://bulletins.psu.edu/university-course-descriptions/undergraduate/', 
    excluded_programs=['EDAB']
):
    # Returns a dictionary of the unique program prefixes and titles and their
    # associated URLs, e.g.,
    # {'IE':
    #     'title': 'Industrial Engineering',
    #     'url': https://bulletins.psu.edu/university-course-descriptions/undergraduate/ie/'
    # }
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    programs = {}
    for program in soup.find(id='cl-menu').find_all('a'):
        prefix = re.findall(r'\(([A-Z\w ]+)\)', program.text)
        title = re.findall(r'(^[\w ]*\w)', program.text)
        
        programs[prefix[0]] = {
            'title': title[0],
            'url': 'https://bulletins.psu.edu' + program.get('href')
        }
        
    for excluded in excluded_programs:
        # Remove specified program prefixes from the directory
        del(programs[excluded])

    return programs

def get_courses(programs, verbose=True):
    # Gathers course information from the passed dictionary of courses, cleans the data,
    # and returns a data frame of the result.
    start = time.time()
    courses = pd.DataFrame(
        columns=[
            'prefix', 'number', 'suffix', 'title', 'description', 'credits', 'other'
        ]
    )

    for i, program_code in enumerate(programs.keys()):
        url = programs[program_code]['url']
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')

        for course in soup.find_all(class_='courseblock'):
            prefix = program_code
            
            # Occasionally course numbers will have an alphabet character suffix to 
            # indicate some attribute of the course. For example, IE 480W indicates a
            # writing intensive course. 
            raw_number = course.find(class_='course_code').text.split('\n')[-1]
            number = ''
            suffix = ''
            for c in raw_number:
                if c.isnumeric():
                    number += c
                elif c.isalpha():
                    suffix += c
            
            title = course.find_all(class_='course_codetitle')[-1].text
            
            credits = course.find(class_='course_credits').text
            
            description = course.find(class_='courseblockdesc')
            if description is not None:
                description = description.text
            
            other = course.find(class_='noindent courseblockextra')
            if other is not None:
                other = other.text

            new_course = pd.DataFrame(
                [[prefix, number, suffix, title, description, credits, other]], 
                columns=courses.columns
            )
            courses = courses.append(new_course, ignore_index=True)

    # Create a unique course key for every course record
    courses['key'] = courses['prefix'] + ' ' + courses['number'] + courses['suffix']
    courses['number'] = courses['number'].astype(int)

    # Some courses offer a range of credits, so the max and min of this range are found
    courses['minimum credits'] = courses['credits'].apply(minimum_credits)
    courses['maximum credits'] = courses['credits'].apply(maximum_credits)

    courses['description'] = courses['description'].apply(remove_escape_characters)
    courses['other'] = courses['other'].apply(remove_escape_characters)

    stop = time.time()
    if verbose:
        print(f'Found {len(courses):,} courses in {stop-start:.2f}s')

    return courses[
        [
            'key', 
            'prefix', 
            'number', 
            'suffix', 
            'title', 
            'description', 
            'minimum credits', 
            'maximum credits', 
            'other'
        ]
    ]

def minimum_credits(credits):
    numeric_credits = re.findall(r'(\d+)-(\d+)|(\d+) C', credits)[0]
    min_credits = int(numeric_credits[0] or numeric_credits[2])
    return min_credits

def maximum_credits(credits):
    numeric_credits = re.findall(r'(\d+)-(\d+)|(\d+) C', credits)[0]
    max_credits = int(numeric_credits[1] or numeric_credits[2])
    return max_credits

def remove_escape_characters(text):
    if text is None:
        return
    escape_characters = [chr(c) for c in range(1, 32)]
    return ''.join([c for c in text if c not in escape_characters])

def main():
    programs = get_programs()
    courses = get_courses(programs)
    courses.to_csv('courses.csv', encoding='utf-8')

if __name__ == '__main__':
    main()
