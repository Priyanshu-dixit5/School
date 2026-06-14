"""Static site content — uses only images from app/static/images/."""
from datetime import datetime
from types import SimpleNamespace


def _item(**kwargs):
    return SimpleNamespace(**kwargs)


HERO_IMAGES = [
    'images/welcome.jpeg',
    'images/full-school-poster.jpeg',
    'images/blue-bells-poster.jpeg',
    'images/love-to-learn-poster.jpeg',
]

GALLERY_ITEMS = [
    _item(title='Annual Function', image='images/annual-function.jpeg', category='events', featured=True),
    _item(title='Science Exhibition', image='images/science-exhibition.jpeg', category='academics', featured=True),
    _item(title='Sports Meet', image='images/sports-meet.jpeg', category='sports', featured=True),
    _item(title='Our Toppers', image='images/toppers.jpeg', category='achievements', featured=True),
    _item(title='Graduation 2024', image='images/graduate-2024.jpeg', category='achievements', featured=True),
    _item(title='Morning Prayer', image='images/ground-prayer.jpeg', category='campus', featured=False),
    _item(title='School Tour', image='images/school-tour.jpeg', category='campus', featured=False),
    _item(title='Campus View', image='images/school1.jpeg', category='campus', featured=False),
    _item(title='Girl Reading', image='images/girl-reading.jpeg', category='academics', featured=False),
    _item(title='Active Learning', image='images/student-raising-hand.jpeg', category='academics', featured=False),
    _item(title='Blue Bells Poster', image='images/blue-bells-poster.jpeg', category='campus', featured=False),
    _item(title='Love To Learn', image='images/love-to-learn-poster.jpeg', category='campus', featured=False),
]

NEWS_ITEMS = [
    _item(
        slug='annual-function-2026',
        title='Annual Function 2026 — A Grand Celebration',
        summary='Students showcased talent through dance, music, drama, and cultural performances at our Annual Function.',
        content='''Our Annual Function was a spectacular celebration of talent, creativity, and school spirit. Students from every class participated in cultural performances, award ceremonies, and special presentations that highlighted the values of Blue Bells Public School.

Parents and guests witnessed the dedication of our faculty and the confidence of our students on stage. The event reinforced our commitment to holistic education — balancing academics with arts, culture, and character building.''',
        image='images/annual-function.jpeg',
        published_at=datetime(2026, 2, 15),
    ),
    _item(
        slug='science-exhibition-winners',
        title='Science Exhibition — Young Innovators Shine',
        summary='Students presented innovative science projects at our inter-school science exhibition.',
        content='''Blue Bells Public School hosted a vibrant Science Exhibition where students demonstrated curiosity, research skills, and scientific thinking. Projects ranged from renewable energy models to environmental awareness displays.

Our young scientists received appreciation from judges and visitors alike. The exhibition reflects our emphasis on hands-on learning and STEM education from early grades through senior secondary.''',
        image='images/science-exhibition.jpeg',
        published_at=datetime(2026, 1, 20),
    ),
    _item(
        slug='sports-meet-2026',
        title='Sports Meet 2026 — Spirit of Champions',
        summary='Annual sports meet featuring athletics, team games, and house competitions.',
        content='''The Sports Meet brought together students, teachers, and parents for a day of athletic excellence and team spirit. Events included track and field, cricket, football, and fun races for younger students.

Sports are integral to life at Blue Bells Public School. We believe physical fitness builds discipline, resilience, and leadership — qualities that complement academic achievement.''',
        image='images/sports-meet.jpeg',
        published_at=datetime(2026, 1, 5),
    ),
    _item(
        slug='congratulations-graduates-2024',
        title='Congratulations Class of 2024',
        summary='Celebrating our graduating students and their outstanding board results.',
        content='''We proudly congratulate the Class of 2024 graduates of Blue Bells Public School. Their dedication, hard work, and the support of our faculty have led to excellent board results and bright futures ahead.

Our graduates are now pursuing higher education in diverse fields. We wish them every success and remind them that they will always be part of the Blue Bells family.''',
        image='images/graduate-2024.jpeg',
        published_at=datetime(2024, 5, 28),
    ),
    _item(
        slug='toppers-felicitated',
        title='Board Exam Toppers Felicitated',
        summary='Honouring students who achieved top ranks in CBSE board examinations.',
        content='''Blue Bells Public School felicitated our board exam toppers in a special ceremony attended by parents, faculty, and management. These students exemplify the academic excellence we strive for every day.

We celebrate not just marks, but the consistent effort, discipline, and guidance that made their success possible. Congratulations to all our achievers!''',
        image='images/toppers.jpeg',
        published_at=datetime(2025, 6, 10),
    ),
]

EVENTS = [
    _item(
        title='Annual Function',
        description='Cultural performances, awards, and celebrations with students and parents.',
        event_date=datetime(2026, 2, 15),
        location='School Auditorium',
        image='images/annual-function.jpeg',
        is_upcoming=False,
    ),
    _item(
        title='Science Exhibition',
        description='Student-led science projects and innovation showcase.',
        event_date=datetime(2026, 1, 20),
        location='Science Block',
        image='images/science-exhibition.jpeg',
        is_upcoming=False,
    ),
    _item(
        title='Sports Meet',
        description='Annual athletics and team sports competition for all classes.',
        event_date=datetime(2026, 1, 5),
        location='Sports Ground',
        image='images/sports-meet.jpeg',
        is_upcoming=False,
    ),
    _item(
        title='Scholarship Guidance Session',
        description='Expert guidance on scholarships and higher education opportunities.',
        event_date=datetime(2026, 7, 15),
        location='Conference Hall',
        image='images/scholarship-guidance.jpeg',
        is_upcoming=True,
    ),
    _item(
        title='New Event — Coming Soon',
        description='Stay tuned for exciting upcoming programs and activities.',
        event_date=datetime(2026, 8, 1),
        location='Blue Bells Campus',
        image='images/coming-soon.jpeg',
        is_upcoming=True,
    ),
]

TEACHERS = [
    _item(name='Senior Faculty', subject='Mathematics', image='images/teacher1.jpeg'),
    _item(name='Senior Faculty', subject='English', image='images/teacher2.jpeg'),
    _item(name='Senior Faculty', subject='Science', image='images/teacher3.jpeg'),
    _item(name='Senior Faculty', subject='Social Studies', image='images/teacher4.jpeg'),
    _item(name='Senior Faculty', subject='Hindi', image='images/teacher5.jpeg'),
    _item(name='Senior Faculty', subject='Computer Science', image='images/teacher6.jpeg'),
]

FACILITIES = [
    _item(name='Science Laboratories', description='Hands-on experiments and STEM learning in well-equipped labs.', icon='bi-flask', image='images/science-exhibition.jpeg'),
    _item(name='Library & Reading', description='A quiet space fostering reading habits and independent study.', icon='bi-book', image='images/girl-reading.jpeg'),
    _item(name='Sports Complex', description='Cricket, athletics, and team sports with professional coaching.', icon='bi-trophy', image='images/sports-meet.jpeg'),
    _item(name='Auditorium & Events', description='Spacious hall for assemblies, performances, and celebrations.', icon='bi-mic', image='images/annual-function.jpeg'),
    _item(name='School Tour', description='Explore our campus, classrooms, and learning spaces on a guided school tour.', icon='bi-signpost-2', image='images/school-tour.jpeg'),
    _item(name='Morning Assembly', description='Daily prayer and values education building character and discipline.', icon='bi-sun', image='images/ground-prayer.jpeg'),
]

TESTIMONIALS = [
    _item(name='Parent Community', role='parent', content='Blue Bells Public School has given our children a nurturing environment with caring teachers and excellent facilities.', rating=5),
    _item(name='Alumni', role='student', content='The values and education I received at Blue Bells prepared me well for higher studies and life ahead.', rating=5),
    _item(name='Parent Community', role='parent', content='We appreciate the balance of academics, sports, and cultural activities. Our child loves coming to school every day.', rating=5),
]

CAREERS = [
    _item(title='Trained Graduate Teacher', department='Academics', description='Passionate educators for CBSE curriculum across subjects.', requirements='Graduate with B.Ed, relevant teaching experience preferred', location='On Campus', employment_type='full-time'),
    _item(title='Sports Coach', department='Sports', description='Qualified coach for cricket, athletics, and team sports.', requirements='Sports certification and coaching experience', location='On Campus', employment_type='full-time'),
]


def get_news_by_slug(slug):
    return next((n for n in NEWS_ITEMS if n.slug == slug), None)
