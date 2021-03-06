import psycopg2 as pg
from pprint import pprint

def drop_dp():
    with pg.connect('dbname=adpy2.3 user=adpyuser') as conn:
        with conn.cursor() as cur:
            cur.execute('''drop table student cascade''')
            cur.execute('''drop table  course cascade ''')
            cur.execute('''drop table student_course cascade''')

def create_db():
    with pg.connect('dbname=adpy2.3 user=adpyuser') as conn:
        with conn.cursor() as cur:
            cur.execute("""
                create table if not exists student (
                    id serial PRIMARY KEY,
                    name varchar(100) not null,
                    gpa numeric(10,2),
                    birth timestamp with time zone
                    );
                    """)
            cur.execute("""
                create table if not exists course (
                    id serial PRIMARY KEY,
                    name varchar(100) not null
                    );
                    """)
            cur.execute("""
                create table if not exists student_course (
                    id serial PRIMARY KEY,
                    student_id INTEGER REFERENCES student(id)
                    on delete cascade,
                    course_id INTEGER REFERENCES course(id)
                    on delete cascade
                    );
                    """)


def add_course(*courses):
    sql_query_list = list()
    for course in courses:
        course_data = tuple([course])
        sql_query_list.append(course_data)
    with pg.connect('dbname=adpy2.3 user=adpyuser') as conn:
        with conn.cursor() as cur:
            cur.executemany("""
                insert into course (name) values (%s);
                    """, sql_query_list)


def check_if_exists(course_id):
    with pg.connect('dbname=adpy2.3 user=adpyuser') as conn:
        with conn.cursor() as cur:
            cur.execute("""
                select exists (select true
                from course where id = %s);
                    """, (course_id,))
            result = cur.fetchone()[0]
        return result


def add_student(student):
    with pg.connect('dbname=adpy2.3 user=adpyuser') as conn:
        with conn.cursor() as cur:
            cur.execute("""
                insert into student (name, gpa, birth) values (%s, %s, %s)
                returning id;
                    """, (student['name'], student['gpa'], student['birth']))
            result = cur.fetchone()[0]
        return result


def add_students(course_id, *students):
    if check_if_exists(course_id) is False:
        pass
    else:
        for student in students:
            id_value = add_student(student)
            with pg.connect('dbname=adpy2.3 user=adpyuser') as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        insert into student_course (student_id, course_id)
                        values (%s, %s);
                            """, (id_value, course_id))


def get_students(course_id):
    with pg.connect('dbname=adpy2.3 user=adpyuser') as conn:
        with conn.cursor() as cur:
            cur.execute("""
                select s.id, s.name, c.name from student_course sc
                join student s on s.id = sc.student_id
                join course c on c.id = sc.course_id
                where sc.course_id = %s;
                    """, (course_id,))
            result = cur.fetchall()
        return result


def get_student(student_id):
    with pg.connect('dbname=adpy2.3 user=adpyuser') as conn:
        with conn.cursor() as cur:
            cur.execute("""
                select * from student where id = %s
                    """, (student_id,))
            result = cur.fetchone()
        return result


if __name__ == '__main__':
    create_db()
    add_student({'name': 'Игорь Сергеев', 'gpa': 3.9, 'birth': '1987-01-13'})
    add_course('Экономическая теория', 'Философия', 'Логика')
    add_students(14, {'name': 'Иван Виноградов', 'gpa': 3.6, 'birth': '1986-11-09'},
                    {'name': 'Наталья Степанова', 'gpa': 4.0, 'birth': '1984-06-15'},
                    {'name': 'Анастасия Глаголева', 'gpa': 1.0, 'birth': '1985-05-31'})
    pprint(get_students(14))
    pprint(get_student(50))

# drop_dp()