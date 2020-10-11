# course-data

### Overview

A simple web scraper to gather information on undergraduate courses offered at Penn State University. All course data is obtained through the University Bulletins at https://bulletins.psu.edu/. The complete list of included programs can be found at https://bulletins.psu.edu/university-course-descriptions/undergraduate/.

Running `python course_scraper.py` will re-scrape the data and create a fresh copy of `courses.csv`.

The version of `courses.csv` included in this repository was created with information retrieved on October 10, 2010.

### Course Attributes

The attributes for each course include

- `key`: A unique key for each course combining the course prefix and number, for example "ECON 102".
- `prefix`: The code for each course subject, such as "PHYS" for courses in Physics.
- `suffix`: Some course numbers include a suffix character to denote certain course attributes. For example, "H" to indicate an honors course, or "S" to indicate a seminar course. 
- `title`: The full title of the course. 
- `description`: A brief text description of the course content. Some courses do not have a description.
- `minimum/maximum credits`: The number of credits a course is worth. In some cases a course may have a variable number of credits. 
- `other`: Other course information listed in the course bulletin. This can include prerequisites, cross-listed courses, and other information. 

A more thorough description of course attributes can be found at https://bulletins.psu.edu/university-course-descriptions/. 