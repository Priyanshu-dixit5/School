"""Download facility, campus, hero, gallery, news, and event images."""
import os
import urllib.request

BASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app', 'static', 'images')
os.makedirs(BASE, exist_ok=True)

IMAGES = {
    # Hero banner carousel
    'hero-1.jpg': 'https://images.pexels.com/photos/256490/pexels-photo-256490.jpeg?auto=compress&cs=tinysrgb&w=1920&h=1080&fit=crop',
    'hero-2.jpg': 'https://images.unsplash.com/photo-1562774053-701939374585?auto=format&fit=crop&w=1920&h=1080&q=85',
    'hero-3.jpg': 'https://images.pexels.com/photos/159490/yale-university-landscape-universities-schools-159490.jpeg?auto=compress&cs=tinysrgb&w=1920&h=1080&fit=crop',
    'hero-4.jpg': 'https://images.pexels.com/photos/207691/pexels-photo-207691.jpeg?auto=compress&cs=tinysrgb&w=1920&h=1080&fit=crop',
    'hero-5.jpg': 'https://images.unsplash.com/photo-1509062522246-3755977927d7?auto=format&fit=crop&w=1920&h=1080&q=85',
    'hero-poster.jpg': 'https://images.pexels.com/photos/256490/pexels-photo-256490.jpeg?auto=compress&cs=tinysrgb&w=1920&h=1080&fit=crop',
    'og-image.jpg': 'https://images.pexels.com/photos/256490/pexels-photo-256490.jpeg?auto=compress&cs=tinysrgb&w=1200&h=630&fit=crop',
    'about-campus.jpg': 'https://images.unsplash.com/photo-1562774053-701939374585?auto=format&fit=crop&w=900&h=650&q=85',
    'infrastructure-campus.jpg': 'https://images.pexels.com/photos/159490/yale-university-landscape-universities-schools-159490.jpeg?auto=compress&cs=tinysrgb&w=900&h=650&fit=crop',
    'principal.jpg': 'https://images.unsplash.com/photo-1560250097-0b93528c311a?auto=format&fit=crop&w=600&h=750&q=85',
    'chairman.jpg': 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?auto=format&fit=crop&w=600&h=750&q=85',
    'facility-smart.jpg': 'https://images.unsplash.com/photo-1580582932707-520aed937b7b?auto=format&fit=crop&w=800&h=550&q=85',
    'facility-lab.jpg': 'https://images.unsplash.com/photo-1532094349884-543bc11b234d?auto=format&fit=crop&w=800&h=550&q=85',
    'facility-computer.jpg': 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?auto=format&fit=crop&w=800&h=550&q=85',
    'facility-library.jpg': 'https://images.unsplash.com/photo-1521587760476-6c12a4b040da?auto=format&fit=crop&w=800&h=550&q=85',
    'facility-sports.jpg': 'https://images.pexels.com/photos/47730/pexels-photo-47730.jpeg?auto=compress&cs=tinysrgb&w=800&h=550&fit=crop',
    'facility-pool.jpg': 'https://images.pexels.com/photos/1263325/pexels-photo-1263325.jpeg?auto=compress&cs=tinysrgb&w=800&h=550&fit=crop',
    'facility-auditorium.jpg': 'https://images.pexels.com/photos/1099680/pexels-photo-1099680.jpeg?auto=compress&cs=tinysrgb&w=800&h=550&fit=crop',
    'facility-transport.jpg': 'https://images.pexels.com/photos/1592384/pexels-photo-1592384.jpeg?auto=compress&cs=tinysrgb&w=800&h=550&fit=crop',
    'facility-medical.jpg': 'https://images.pexels.com/photos/263402/pexels-photo-263402.jpeg?auto=compress&cs=tinysrgb&w=800&h=550&fit=crop',
    'gallery-1.jpg': 'https://images.unsplash.com/photo-1509062522246-3755977927d7?auto=format&fit=crop&w=700&h=500&q=85',
    'gallery-2.jpg': 'https://images.pexels.com/photos/159775/library-la-trobe-study-students-159775.jpeg?auto=compress&cs=tinysrgb&w=700&h=500&fit=crop',
    'gallery-3.jpg': 'https://images.unsplash.com/photo-1524178232363-1fb2b075b655?auto=format&fit=crop&w=700&h=500&q=85',
    'gallery-4.jpg': 'https://images.pexels.com/photos/207691/pexels-photo-207691.jpeg?auto=compress&cs=tinysrgb&w=700&h=500&fit=crop',
    'gallery-5.jpg': 'https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=700&h=500&q=85',
    'gallery-6.jpg': 'https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&w=700&h=500&q=85',
    'gallery-7.jpg': 'https://images.unsplash.com/photo-1498243691581-b145c3f54a5a?auto=format&fit=crop&w=700&h=500&q=85',
    'gallery-8.jpg': 'https://images.pexels.com/photos/267885/pexels-photo-267885.jpeg?auto=compress&cs=tinysrgb&w=700&h=500&fit=crop',
    'gallery-9.jpg': 'https://images.pexels.com/photos/8199562/pexels-photo-8199562.jpeg?auto=compress&cs=tinysrgb&w=700&h=500&fit=crop',
    'gallery-10.jpg': 'https://images.pexels.com/photos/8199562/pexels-photo-8199562.jpeg?auto=compress&cs=tinysrgb&w=700&h=500&fit=crop',
    'gallery-11.jpg': 'https://images.pexels.com/photos/267885/pexels-photo-267885.jpeg?auto=compress&cs=tinysrgb&w=700&h=500&fit=crop',
    'gallery-12.jpg': 'https://images.pexels.com/photos/5212345/pexels-photo-5212345.jpeg?auto=compress&cs=tinysrgb&w=700&h=500&fit=crop',
    'news-1.jpg': 'https://images.pexels.com/photos/7107432/pexels-photo-7107432.jpeg?auto=compress&cs=tinysrgb&w=800&h=500&fit=crop',
    'news-2.jpg': 'https://images.unsplash.com/photo-1532094349884-543bc11b234d?auto=format&fit=crop&w=800&h=500&q=85',
    'news-3.jpg': 'https://images.unsplash.com/photo-1580582932707-520aed937b7b?auto=format&fit=crop&w=800&h=500&q=85',
    'event-1.jpg': 'https://images.pexels.com/photos/7107432/pexels-photo-7107432.jpeg?auto=compress&cs=tinysrgb&w=800&h=500&fit=crop',
    'event-2.jpg': 'https://images.pexels.com/photos/47730/pexels-photo-47730.jpeg?auto=compress&cs=tinysrgb&w=800&h=500&fit=crop',
    'event-3.jpg': 'https://images.unsplash.com/photo-1524178232363-1fb2b075b655?auto=format&fit=crop&w=800&h=500&q=85',
    'news-placeholder.jpg': 'https://images.unsplash.com/photo-1503676260728-1c00da094a0b?auto=format&fit=crop&w=800&h=500&q=85',
}


def download():
    for name, url in IMAGES.items():
        path = os.path.join(BASE, name)
        if os.path.exists(path) and os.path.getsize(path) > 5000:
            print(f'Skip {name} (exists)')
            continue
        try:
            print(f'Downloading {name}...')
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=90) as resp:
                data = resp.read()
            if len(data) < 3000:
                print(f'  SKIP {name} — too small')
                continue
            with open(path, 'wb') as f:
                f.write(data)
            print(f'  OK ({len(data)} bytes)')
        except Exception as e:
            print(f'  FAIL {name}: {e}')


if __name__ == '__main__':
    download()
    print('Done.')
