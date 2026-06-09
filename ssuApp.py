import json
import os
import random
from flask import Flask, render_template_string, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = "ssuchelin_secret_key_2026_flask"

# ==========================================
# 로컬 JSON 데이터 (부대찌개 -> 한식 통합)
# ==========================================
DATA_FILE = "ssuchelin_data_v6.json"

# 더미 식당 생성기 (부대찌개 제거)
dummy_stores = []
categories = ["한식", "일식", "중식", "양식", "패스트푸드", "카페/디저트", "아시안", "멕시코 음식"]
locations = ["고민사거리", "중문", "정문", "후문", "숭실대입구역", "상도동"]
images = ["🍔", "🍜", "🍣", "🍛", "🍕", "🥩", "☕", "🍰", "🌮", "🍲", "🍱"]

for i in range(5, 35):
    cat = random.choice(categories)
    dist = random.randint(50, 2000)
    dummy_stores.append({
        "id": i,
        "name": f"맛있는 {cat} {i}호점",
        "location": random.choice(locations),
        "distance": f"중문에서 {dist}m",
        "distanceNum": dist,
        "category": cat,
        "priceRange": random.choice([5000, 7000, 10000, 15000, 20000]),
        "isTrending": random.choice([True, False]),
        "is_open": random.choice([True, False]),
        "businessHours": "11:00 - 21:00",
        "image": random.choice(images),
        "description": f"가성비 좋고 맛있는 {cat} 전문점입니다.",
        "menus": [
            {"name": "대표 메뉴", "price": random.choice([6000, 7000, 8000, 9000])},
            {"name": "세트 메뉴", "price": random.choice([10000, 12000, 15000])}
        ],
        "reviews": [
            {"id": i*10, "author": "익명", "major": "알수없음", "rating": random.randint(3, 5), "text": "괜찮은 식당이에요!"}
        ]
    })

default_data = {
    "users": [], 
    "stores": [
        {
            "id": 1, "name": "크라이치즈버거", "location": "고민사거리", "distance": "중문에서 100m", "distanceNum": 100,
            "category": "패스트푸드", "priceRange": 10000, "isTrending": True, "is_open": True,
            "businessHours": "11:00 - 20:30", "image": "🍔", "description": "12년째 치즈버거 한 길만 걸어온 한국 로컬 버거",
            "menus": [
                {"name": "크라이 치킨버거", "price": 7900},
                {"name": "트리플치즈버거세트", "price": 13500},
                {"name": "치즈버거세트", "price": 8900}
            ],
            "reviews": [
                {"id": 1, "author": "익명", "major": "경영학부", "rating": 5, "text": "맛있는 집입니다"},
                {"id": 2, "author": "익명", "major": "컴퓨터학부", "rating": 4, "text": "감자튀김이 맛있는 집"}
            ]
        },
        {
            "id": 2, "name": "BURRITO ZIP", "location": "고민사거리", "distance": "중문에서 130m", "distanceNum": 130,
            "category": "멕시코 음식", "priceRange": 4900, "isTrending": True, "is_open": True,
            "businessHours": "13:00 - 20:00", "image": "🌯", "description": "공강 시간에 빠르게 먹고 가기 좋은 부리또",
            "menus": [{"name": "단품부리또", "price": 4400}, {"name": "음료세트", "price": 5400}],
            "reviews": [{"id": 3, "author": "익명", "major": "전자정보공학부", "rating": 5, "text": "매운맛 추천."}]
        },
        {
            "id": 3, "name": "찌개대학 부대과", "location": "고민사거리", "distance": "중문에서 120m", "distanceNum": 120,
            "category": "한식", # 부대찌개 -> 한식으로 수정
            "priceRange": 7000, "isTrending": False, "is_open": False,
            "businessHours": "11:00 - 22:00", "image": "🍲", "description": "맛있는 부대찌개",
            "menus": [{"name": "홍부대찌개", "price": 7000}, {"name": "백부대찌개", "price": 7000}],
            "reviews": [{"id": 4, "author": "익명", "major": "건축학부", "rating": 5, "text": "밥이 무제한 리필"}]
        },
        {
            "id": 4, "name": "취향", "location": "고민사거리", "distance": "중문에서 150m", "distanceNum": 150,
            "category": "중식", "priceRange": 10000, "isTrending": True, "is_open": True,
            "businessHours": "11:30 - 21:00", "image": "🍜", "description": "탕수육이 맛있는 중식당",
            "menus": [{"name": "짜장면", "price": 6500}, {"name": "탕수육", "price": 10000}],
            "reviews": []
        }
    ] + dummy_stores,
    "partnerships": [
        {"partner": "전체 제휴 카페", "benefit": "모든 재학생 음료 사이즈업", "matchId": None, "target": "전체"},
        {"partner": "크라이치즈버거", "benefit": "IT대학 재학생 인증시 할인 및 치즈스틱", "matchId": 1, "target": "IT대학"},
        {"partner": "BURRITO ZIP", "benefit": "공과대학 재학생 세트 메뉴 10% 할인", "matchId": 2, "target": "공과대학"},
        {"partner": "취향", "benefit": "경영대학 재학생 군만두 서비스", "matchId": 4, "target": "경영대학"}
    ]
}

def load_data():
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "users" not in data:
                    data["users"] = []
                    save_data(data)
                return data
        else:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(default_data, f, ensure_ascii=False, indent=4)
            return default_data
    except Exception:
        return default_data

def save_data(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"데이터 저장 에러: {e}")

def get_avg_rating(reviews):
    if not reviews: return 0.0
    return round(sum(r["rating"] for r in reviews) / len(reviews), 1)

# ==========================================
# Jinja2 HTML 템플릿 
# ==========================================
BASE_HTML = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SSU슐랭 가이드</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .no-scrollbar::-webkit-scrollbar { display: none; }
        .no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
        .pb-safe { padding-bottom: env(safe-area-inset-bottom, 20px); }
    </style>
</head>
<body class="bg-gray-100 font-sans text-gray-900 flex justify-center min-h-screen">
    <div class="w-full max-w-md bg-white min-h-screen flex flex-col relative shadow-xl overflow-hidden">
        
        <header class="bg-orange-500 text-white p-4 sticky top-0 z-20 flex justify-between items-center shadow-md">
            {% block header %}
            <div class="flex items-center gap-2">
                <span class="text-2xl">🍽️</span>
                <h1 class="text-xl font-bold tracking-tight">SSU슐랭 가이드</h1>
            </div>
            <a href="/profile" class="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center">👤</a>
            {% endblock %}
        </header>

        {% with messages = get_flashed_messages() %}
            {% if messages %}
            <div class="bg-red-50 text-red-600 p-3 text-sm flex items-center justify-center gap-2 font-bold border-b border-red-200">
                {% for message in messages %}<span>{{ message }}</span>{% endfor %}
            </div>
            {% endif %}
        {% endwith %}

        <main class="flex-1 overflow-y-auto pb-20">
            {% block content %}{% endblock %}
        </main>

        {% block bottom_nav %}
        <nav class="absolute bottom-0 w-full bg-white border-t border-gray-200 flex justify-around p-2 pb-safe z-20 shadow-[0_-2px_10px_rgba(0,0,0,0.05)]">
            <a href="/home" class="flex flex-col items-center p-2 min-w-[64px] transition-colors {% if active_tab == 'home' %}text-orange-500{% else %}text-gray-400{% endif %}">
                <span class="text-2xl">🏠</span><span class="text-[10px] font-medium mt-1">홈</span>
            </a>
            <a href="/search" class="flex flex-col items-center p-2 min-w-[64px] transition-colors {% if active_tab == 'search' %}text-orange-500{% else %}text-gray-400{% endif %}">
                <span class="text-2xl">🔍</span><span class="text-[10px] font-medium mt-1">검색</span>
            </a>
            <a href="/coupons" class="flex flex-col items-center p-2 min-w-[64px] transition-colors {% if active_tab == 'coupons' %}text-orange-500{% else %}text-gray-400{% endif %}">
                <span class="text-2xl">🎫</span><span class="text-[10px] font-medium mt-1">할인</span>
            </a>
            <a href="/profile" class="flex flex-col items-center p-2 min-w-[64px] transition-colors {% if active_tab == 'profile' %}text-orange-500{% else %}text-gray-400{% endif %}">
                <span class="text-2xl">👤</span><span class="text-[10px] font-medium mt-1">프로필</span>
            </a>
        </nav>
        {% endblock %}
    </div>
</body>
</html>
"""

LOGIN_HTML = """
{% extends 'base' %}
{% block header %}{% endblock %}{% block bottom_nav %}{% endblock %}
{% block content %}
<div class="h-full flex flex-col justify-center px-8 py-10 bg-white">
    <div class="text-center mb-10">
        <div class="text-6xl mb-4">🍽️</div>
        <h2 class="text-3xl font-extrabold text-orange-600 mb-2">SSU슐랭 가이드</h2>
        <p class="text-gray-500 text-sm">대학가 맛집 평가 & 공유 서비스</p>
    </div>
    <form action="/login" method="POST" class="space-y-4">
        <div>
            <label class="block text-sm font-bold text-gray-700 mb-1">학번</label>
            <input type="text" name="username" class="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-orange-500" placeholder="학번을 입력하세요 (숫자)" required>
        </div>
        <div>
            <label class="block text-sm font-bold text-gray-700 mb-1">비밀번호</label>
            <input type="password" name="password" class="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-orange-500" placeholder="비밀번호를 입력하세요" required>
        </div>
        <button type="submit" class="w-full bg-orange-500 text-white font-bold py-3.5 rounded-xl mt-6 shadow-md hover:bg-orange-600">로그인</button>
    </form>
    
    <div class="mt-8 pt-6 border-t border-gray-100 text-center">
        <p class="text-sm text-gray-500 mb-3">아직 SSU슐랭 회원이 아니신가요?</p>
        <a href="/register" class="w-full block bg-gray-100 text-gray-800 font-bold py-3 rounded-xl hover:bg-gray-200 transition-colors">회원가입하기</a>
    </div>
</div>
{% endblock %}
"""

REGISTER_HTML = """
{% extends 'base' %}
{% block header %}{% endblock %}{% block bottom_nav %}{% endblock %}
{% block content %}
<div class="h-full flex flex-col justify-center px-8 py-10 bg-white">
    <div class="mb-8">
        <h2 class="text-2xl font-extrabold text-gray-900 mb-2">회원가입 📝</h2>
        <p class="text-gray-500 text-sm">단과대 혜택을 위해 정확히 입력해주세요.</p>
    </div>
    <form action="/register" method="POST" class="space-y-4">
        <div>
            <label class="block text-sm font-bold text-gray-700 mb-1">학번 (아이디)</label>
            <input type="text" name="username" class="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-orange-500" placeholder="예: 20260001" required>
        </div>
        <div>
            <label class="block text-sm font-bold text-gray-700 mb-1">비밀번호</label>
            <input type="password" name="password" class="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-orange-500" placeholder="비밀번호 입력" required>
        </div>
        <div>
            <label class="block text-sm font-bold text-gray-700 mb-1">이름 (닉네임)</label>
            <input type="text" name="name" class="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-orange-500" placeholder="예: 김슈냥" required>
        </div>
        <div>
            <label class="block text-sm font-bold text-gray-700 mb-1">소속 단과대학</label>
            <select name="college" class="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-orange-500" required>
                <option value="IT대학">IT대학</option>
                <option value="공과대학">공과대학</option>
                <option value="경영대학">경영대학</option>
                <option value="인문대학">인문대학</option>
                <option value="자연과학대학">자연과학대학</option>
                <option value="사회과학대학">사회과학대학</option>
                <option value="법과대학">법과대학</option>
                <option value="기타">기타</option>
            </select>
        </div>
        <button type="submit" class="w-full bg-gray-900 text-white font-bold py-3.5 rounded-xl mt-6 shadow-md hover:bg-gray-800">가입하기</button>
    </form>
    <div class="mt-6 text-center">
        <a href="/login" class="text-sm font-bold text-gray-500 hover:underline">← 로그인으로 돌아가기</a>
    </div>
</div>
{% endblock %}
"""

HOME_HTML = """
{% extends 'base' %}
{% block content %}
<div class="p-4 space-y-6">
    <div class="bg-orange-50 rounded-2xl p-5 border border-orange-100">
        <h2 class="text-xl font-extrabold text-orange-900 mb-2">{{ session.get('user_name', '학우') }}님, 오늘 뭐 먹지? 🤔</h2>
        <p class="text-sm text-orange-700 mb-4">조건에 딱 맞는 맛집을 1초 만에 찾아보세요!</p>
        <a href="/search" class="w-full bg-white text-orange-500 font-semibold py-3 rounded-xl shadow-sm flex items-center justify-center gap-2 border border-orange-200">
            🔍 필터링 검색하러 가기
        </a>
    </div>

    <div>
        <h3 class="text-lg font-bold flex items-center gap-2 mb-3">
            <span class="text-red-500 animate-pulse">🔥</span> 실시간 트렌딩 맛집
        </h3>
        <!-- 변경됨: 가로 1행 스크롤에서 전체화면 2열 그리드(세로 드래그)로 변경 -->
        <div class="grid grid-cols-2 gap-3 pb-4">
            {% for store in trending_stores[:10] %} <!-- 트렌딩 상위 10개만 홈에 표시 -->
            <a href="/store/{{ store.id }}" class="bg-white rounded-xl shadow-sm border border-gray-100 p-3 flex flex-col hover:bg-gray-50 transition-colors">
                <div class="w-full h-24 bg-gray-50 rounded-lg flex items-center justify-center text-4xl mb-2 relative">
                    {{ store.image }}
                    {% if not store.is_open %}
                        <div class="absolute inset-0 bg-black/60 rounded-lg flex items-center justify-center text-white text-[10px] font-bold">영업종료</div>
                    {% endif %}
                </div>
                <div class="flex flex-col flex-1">
                    <div class="flex justify-between items-start mb-1 gap-1">
                        <h4 class="font-bold text-sm text-gray-900 truncate">{{ store.name }}</h4>
                        <div class="flex items-center text-[10px] font-bold text-orange-600 bg-orange-50 border border-orange-100 px-1 py-0.5 rounded whitespace-nowrap">
                            ★ {{ store.avg_rating }}
                        </div>
                    </div>
                    <p class="text-[10px] text-gray-500 mb-1 truncate">{{ store.category }} · {{ store.distance }}</p>
                </div>
            </a>
            {% endfor %}
        </div>
    </div>
</div>
{% endblock %}
"""

SEARCH_HTML = """
{% extends 'base' %}
{% block content %}
<div class="h-full flex flex-col bg-gray-50">
    <details class="bg-white p-4 shadow-sm border-b border-gray-100 sticky top-0 z-10 text-sm group" open>
        <summary class="flex justify-between items-center font-bold text-gray-800 cursor-pointer list-none outline-none">
            <span class="flex items-center gap-1 text-base">🔍 상세 필터링</span>
            <span class="text-orange-500 text-xs font-normal group-open:hidden border border-orange-200 px-2 py-1 rounded bg-orange-50">조건 열기 ▼</span>
            <span class="text-gray-500 text-xs font-normal hidden group-open:inline border border-gray-200 px-2 py-1 rounded">접기 ▲</span>
        </summary>
        
        <form action="/search" method="GET" class="mt-4 border-t border-gray-100 pt-4 space-y-4">
            
            <div class="flex gap-4">
                <div class="flex-1">
                    <label class="block text-xs font-semibold text-gray-500 mb-1">음식 종류</label>
                    <select name="category" class="w-full bg-gray-50 border border-gray-200 rounded p-2 focus:ring-2 focus:ring-orange-500 outline-none">
                        <option value="">전체보기</option>
                        <option value="한식" {% if filters.category == '한식' %}selected{% endif %}>한식</option>
                        <option value="패스트푸드" {% if filters.category == '패스트푸드' %}selected{% endif %}>패스트푸드</option>
                        <option value="중식" {% if filters.category == '중식' %}selected{% endif %}>중식</option>
                        <option value="일식" {% if filters.category == '일식' %}selected{% endif %}>일식</option>
                        <option value="양식" {% if filters.category == '양식' %}selected{% endif %}>양식</option>
                        <option value="멕시코 음식" {% if filters.category == '멕시코 음식' %}selected{% endif %}>멕시코 음식</option>
                        <!-- 부대찌개 옵션 삭제됨 -->
                    </select>
                </div>
                <div class="flex-1">
                    <label class="block text-xs font-semibold text-gray-500 mb-1">최대 거리</label>
                    <select name="max_distance" class="w-full bg-gray-50 border border-gray-200 rounded p-2 focus:ring-2 focus:ring-orange-500 outline-none">
                        <option value="2000" {% if filters.max_distance == '2000' %}selected{% endif %}>상관없음</option>
                        <option value="100" {% if filters.max_distance == '100' %}selected{% endif %}>100m 이내 (코앞)</option>
                        <option value="300" {% if filters.max_distance == '300' %}selected{% endif %}>300m 이내</option>
                        <option value="500" {% if filters.max_distance == '500' %}selected{% endif %}>500m 이내</option>
                    </select>
                </div>
            </div>

            <div>
                <label class="block text-xs font-semibold text-gray-500 mb-1 flex justify-between">
                    <span>최대 예산 (1인)</span>
                    <span class="text-orange-500 font-bold" id="price-display">{{ "{:,}".format(filters.max_price|int) }}원 이하</span>
                </label>
                <input type="range" name="max_price" min="5000" max="20000" step="1000" value="{{ filters.max_price }}" 
                       oninput="document.getElementById('price-display').innerText = Number(this.value).toLocaleString() + '원 이하'" 
                       class="w-full accent-orange-500 mt-1">
            </div>

            <div class="flex justify-between items-center bg-gray-50 p-2 rounded border border-gray-100">
                <label class="flex items-center gap-2 text-xs font-bold text-gray-700 cursor-pointer">
                    <input type="checkbox" name="is_open" value="true" class="w-4 h-4 accent-orange-500" {% if filters.is_open %}checked{% endif %}>
                    현재 영업 중인 식당만 보기
                </label>
            </div>
            
            <div class="flex items-center gap-2 pt-2">
                <label class="text-xs font-bold text-gray-700 whitespace-nowrap">정렬 방식:</label>
                <select name="sort" class="flex-1 bg-white border border-gray-200 rounded py-1.5 px-2 text-xs focus:ring-2 focus:ring-orange-500 outline-none">
                    <option value="rating" {% if filters.sort == 'rating' %}selected{% endif %}>★ 별점 높은 순</option>
                    <option value="distance" {% if filters.sort == 'distance' %}selected{% endif %}>📍 거리 가까운 순</option>
                </select>
            </div>

            <div class="flex gap-2 mt-2">
                <a href="/search" class="w-1/3 bg-gray-200 text-gray-700 font-bold py-2 rounded-lg text-center hover:bg-gray-300 transition-colors">
                    조건 초기화
                </a>
                <button type="submit" class="w-2/3 bg-orange-500 text-white font-bold py-2 rounded-lg shadow-sm hover:bg-orange-600 transition-colors">
                    결과 보기
                </button>
            </div>
        </form>
    </details>

    <div class="p-4 flex-1 overflow-y-auto">
        <div class="text-sm font-bold text-gray-800 mb-3">
            조건에 맞는 식당 <span class="text-orange-500">{{ stores|length }}</span>곳
        </div>
        
        {% if stores %}
            <!-- 변경됨: 세로 리스트에서 2열 그리드로 변경 -->
            <div class="grid grid-cols-2 gap-3">
                {% for store in stores %}
                <a href="/store/{{ store.id }}" class="bg-white p-3 rounded-xl shadow-sm border border-gray-100 flex flex-col hover:bg-orange-50 transition-colors">
                    <div class="w-full h-24 bg-gray-50 rounded-lg flex items-center justify-center text-4xl mb-2 relative">
                        {{ store.image }}
                        {% if not store.is_open %}
                            <div class="absolute inset-0 bg-black/60 rounded-lg flex items-center justify-center text-white text-[10px] font-bold">영업종료</div>
                        {% endif %}
                    </div>
                    <div class="flex flex-col flex-1">
                        <div class="flex justify-between items-start mb-1 gap-1">
                            <h3 class="font-bold text-sm text-gray-900 truncate">{{ store.name }}</h3>
                            <div class="flex items-center text-[10px] font-bold text-orange-600 bg-orange-50 border border-orange-100 px-1 py-0.5 rounded whitespace-nowrap">
                                ★ {{ store.avg_rating }}
                            </div>
                        </div>
                        <p class="text-[10px] text-gray-500 mb-1 truncate">{{ store.category }} · {{ store.distance }}</p>
                        <div class="flex gap-1 mt-auto pt-1">
                            <span class="text-[9px] px-1.5 py-0.5 rounded bg-gray-100 text-gray-600 truncate">💸 {{ "{:,}".format(store.priceRange) }}원~</span>
                            {% if store.is_open %}
                                <span class="text-[9px] px-1.5 py-0.5 rounded bg-green-50 text-green-600 border border-green-200 whitespace-nowrap">영업중</span>
                            {% endif %}
                        </div>
                    </div>
                </a>
                {% endfor %}
            </div>
        {% else %}
            <div class="text-center py-12 text-gray-500">
                <div class="text-4xl mb-3">🥲</div>
                조건에 맞는 식당이 없습니다.<br/><span class="text-xs">필터를 조정해 보세요.</span>
            </div>
        {% endif %}
    </div>
</div>
{% endblock %}
"""

COUPONS_HTML = """
{% extends 'base' %}
{% block content %}
<div class="p-4 bg-gray-50 min-h-full">
    <h2 class="text-xl font-bold mb-1 text-center mt-2">
        <span class="text-orange-600">{{ session.get('college', '대학') }}</span><br/>학생 제휴 혜택 안내 🤝
    </h2>
    <div class="space-y-3 mt-6">
        {% if partnerships %}
            {% for p in partnerships %}
            <div class="bg-white p-4 rounded-xl shadow-sm border-l-4 border-l-orange-500 border-y border-r border-gray-100">
                <div class="flex justify-between items-start mb-2">
                    <h3 class="font-bold text-gray-800">{{ p.partner }}</h3>
                    <span class="text-[10px] bg-gray-100 text-gray-600 px-2 py-1 rounded font-bold">{{ p.target }} 대상</span>
                </div>
                <p class="text-sm font-medium text-orange-800 bg-orange-50 p-2 rounded">혜택: <strong>{{ p.benefit }}</strong></p>
                {% if p.matchId %}
                <a href="/store/{{ p.matchId }}" class="block w-full text-center mt-3 py-2 bg-gray-50 text-gray-600 text-xs font-bold rounded hover:bg-gray-100">가게 정보 보기</a>
                {% endif %}
            </div>
            {% endfor %}
        {% else %}
            <div class="text-center py-10 text-gray-500">
                현재 소속 단과대학에 등록된 제휴 혜택이 없습니다.
            </div>
        {% endif %}
    </div>
</div>
{% endblock %}
"""

PROFILE_HTML = """
{% extends 'base' %}
{% block content %}
<div class="p-4">
    <div class="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 flex flex-col items-center mb-4">
        <div class="w-20 h-20 bg-orange-100 text-orange-500 rounded-full flex items-center justify-center mb-3 text-4xl">👤</div>
        <h2 class="text-xl font-bold">{{ session.get('user_name') }} <span class="text-sm font-normal text-gray-500">({{ session.get('user_id') }})</span></h2>
        <p class="text-sm text-gray-500 bg-gray-100 px-3 py-1 rounded-full mt-2 font-medium">{{ session.get('college') }} 재학생</p>
    </div>
    <a href="/logout" class="block text-center w-full bg-white border border-gray-200 text-red-500 font-bold py-3 rounded-xl shadow-sm hover:bg-gray-50">로그아웃</a>
</div>
{% endblock %}
"""

DETAIL_HTML = """
{% extends 'base' %}
{% block header %}
<a href="javascript:history.back()" class="flex items-center gap-2 text-white">
    <span class="text-2xl">←</span><h1 class="text-lg font-bold truncate">{{ store.name }}</h1>
</a>
<div></div>
{% endblock %}
{% block bottom_nav %}{% endblock %}

{% block content %}
<div class="bg-gray-50 min-h-full pb-6">
    <div class="bg-white p-5 shadow-sm mb-2 border-b border-gray-100">
        <div class="flex justify-between items-start mb-2">
            <h2 class="text-2xl font-extrabold text-gray-900">{{ store.name }}</h2>
            <div class="bg-orange-50 text-orange-500 font-bold px-3 py-1 rounded-full flex items-center gap-1">★ {{ store.avg_rating }}</div>
        </div>
        <p class="text-sm text-gray-500 mb-3">{{ store.description }}</p>
        <div class="flex items-center text-xs text-gray-600 gap-2 mb-1">
            📍 위치: {{ store.location }} | {{ store.distance }}
        </div>
        <div class="flex items-center text-xs text-gray-600 gap-2">
            🕒 영업시간: {{ store.businessHours }} 
            {% if store.is_open %}<span class="text-green-500 font-bold">(영업중)</span>{% else %}<span class="text-red-500 font-bold">(영업종료)</span>{% endif %}
        </div>
    </div>

    <div class="flex border-b border-gray-200 bg-white sticky top-0 z-10">
        <button onclick="showTab('review')" id="btn-review" class="flex-1 py-3 text-sm font-bold border-b-2 border-orange-500 text-orange-500">생생 후기 ({{ store.reviews|length }})</button>
        <button onclick="showTab('menu')" id="btn-menu" class="flex-1 py-3 text-sm font-bold border-b-2 border-transparent text-gray-500">메뉴판</button>
    </div>

    <div class="p-4 space-y-4">
        <div id="tab-review">
            <div class="bg-white rounded-xl shadow-sm border border-orange-100 p-4 mb-4">
                <h4 class="text-sm font-bold text-gray-800 mb-3">✍️ 새로운 후기 남기기</h4>
                <form action="/store/{{ store.id }}/review" method="POST">
                    <input type="text" name="comment" class="w-full bg-gray-50 border border-gray-200 rounded-lg px-3 py-2 text-sm mb-3 focus:outline-none focus:ring-2 focus:ring-orange-500" placeholder="후기를 남겨주세요" required>
                    <div class="flex gap-2">
                        <select name="rating" class="flex-1 bg-gray-50 border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none">
                            <option value="5">★★★★★ (5점)</option>
                            <option value="4">★★★★☆ (4점)</option>
                            <option value="3">★★★☆☆ (3점)</option>
                            <option value="2">★★☆☆☆ (2점)</option>
                            <option value="1">★☆☆☆☆ (1점)</option>
                        </select>
                        <button type="submit" class="bg-orange-500 text-white font-bold py-2 px-4 rounded-lg text-sm">후기 등록</button>
                    </div>
                </form>
            </div>
            <div class="space-y-3">
                {% for review in store.reviews|reverse %}
                <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
                    <div class="flex text-orange-400 mb-1 text-xs">
                        {% for _ in range(review.rating) %}★{% endfor %}
                    </div>
                    <div class="flex items-center gap-2 mb-2">
                        <span class="font-bold text-xs text-gray-800">{{ review.author }}</span>
                        <span class="bg-blue-50 text-blue-600 text-[10px] px-1.5 py-0.5 rounded font-medium">{{ review.major }}</span>
                    </div>
                    <p class="text-sm text-gray-700">{{ review.text }}</p>
                </div>
                {% endfor %}
            </div>
        </div>

        <div id="tab-menu" class="hidden">
            <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
                <h3 class="font-bold text-gray-800 mb-3">🍴 주요 메뉴</h3>
                <div class="divide-y divide-gray-100">
                    {% for menu in store.menus %}
                    <div class="py-3 flex justify-between">
                        <span class="text-sm font-medium">{{ menu.name }}</span>
                        <span class="text-sm font-bold">{{ "{:,}".format(menu.price) }}원</span>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>
    </div>
</div>
<script>
    function showTab(t) {
        document.getElementById('tab-review').classList.add('hidden');
        document.getElementById('tab-menu').classList.add('hidden');
        document.getElementById('btn-review').className = 'flex-1 py-3 text-sm font-bold border-b-2 border-transparent text-gray-500';
        document.getElementById('btn-menu').className = 'flex-1 py-3 text-sm font-bold border-b-2 border-transparent text-gray-500';
        document.getElementById('tab-' + t).classList.remove('hidden');
        document.getElementById('btn-' + t).className = 'flex-1 py-3 text-sm font-bold border-b-2 border-orange-500 text-orange-500';
    }
</script>
{% endblock %}
"""

# ==========================================
# 템플릿 상속 모방 및 렌더러
# ==========================================
def render_page(template, **kwargs):
    from jinja2 import Environment, DictLoader
    env = Environment(loader=DictLoader({'base': BASE_HTML, 'page': template}))
    from flask import get_flashed_messages
    return env.get_template('page').render(get_flashed_messages=get_flashed_messages, session=session, **kwargs)

# ==========================================
# 라우팅
# ==========================================
@app.before_request
def require_login():
    if request.endpoint not in ['login', 'register', 'static'] and 'user_id' not in session:
        return redirect(url_for('login'))

@app.route("/")
def index():
    return redirect(url_for('home'))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        name = request.form.get("name", "").strip()
        college = request.form.get("college", "기타")

        data = load_data()
        
        if any(user["user_id"] == username for user in data.get("users", [])):
            flash("이미 가입된 학번입니다.")
            return redirect(url_for("register"))
            
        data["users"].append({
            "user_id": username,
            "password": password,
            "name": name,
            "college": college
        })
        save_data(data)
        
        flash("회원가입이 완료되었습니다. 로그인해주세요!")
        return redirect(url_for("login"))
        
    return render_page(REGISTER_HTML)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        
        data = load_data()
        
        user = next((u for u in data.get("users", []) if u["user_id"] == username and u["password"] == password), None)
        
        if user:
            session['user_id'] = user['user_id']
            session['user_name'] = user['name']
            session['college'] = user['college']
            return redirect(url_for("home"))
        else:
            flash("학번이나 비밀번호가 일치하지 않습니다.")
            return redirect(url_for("login"))
            
    return render_page(LOGIN_HTML)

@app.route("/home")
def home():
    data = load_data()
    for store in data["stores"]: store["avg_rating"] = get_avg_rating(store["reviews"])
    trending = sorted([s for s in data["stores"] if s["isTrending"]], key=lambda x: x["avg_rating"], reverse=True)
    return render_page(HOME_HTML, active_tab="home", trending_stores=trending)

@app.route("/search")
def search():
    data = load_data()
    
    category = request.args.get("category", "")
    max_price = request.args.get("max_price", "20000")
    max_distance = request.args.get("max_distance", "2000")
    is_open = request.args.get("is_open", "")
    sort_type = request.args.get("sort", "rating")
    
    filters = {
        "category": category,
        "max_price": max_price,
        "max_distance": max_distance,
        "is_open": is_open == "true",
        "sort": sort_type
    }
    
    filtered_stores = []
    for store in data["stores"]:
        store["avg_rating"] = get_avg_rating(store["reviews"])
        
        if filters["category"] and store.get("category") != filters["category"]: continue
        if store.get("priceRange", 0) > int(filters["max_price"]): continue
        if store.get("distanceNum", 9999) > int(filters["max_distance"]): continue
        if filters["is_open"] and not store.get("is_open", True): continue
            
        filtered_stores.append(store)
        
    if sort_type == "rating":
        filtered_stores.sort(key=lambda x: x["avg_rating"], reverse=True)
    elif sort_type == "distance":
        filtered_stores.sort(key=lambda x: x.get("distanceNum", 9999))
        
    return render_page(SEARCH_HTML, active_tab="search", stores=filtered_stores, filters=filters)

@app.route("/store/<int:store_id>")
def store_detail(store_id):
    data = load_data()
    store = next((s for s in data["stores"] if s["id"] == store_id), None)
    if not store:
        flash("존재하지 않는 음식점입니다.")
        return redirect(url_for("home"))
    store["avg_rating"] = get_avg_rating(store["reviews"])
    return render_page(DETAIL_HTML, active_tab="none", store=store)

@app.route("/store/<int:store_id>/review", methods=["POST"])
def add_review(store_id):
    comment = request.form.get("comment", "").strip()
    try: rating = int(request.form.get("rating", "5"))
    except ValueError: rating = 5
    if comment:
        data = load_data()
        for s in data["stores"]:
            if s["id"] == store_id:
                s["reviews"].append({
                    "id": len(s["reviews"]) + 1, 
                    "author": session.get('user_name', '익명'),
                    "major": session.get('college', 'SSU 재학생'), 
                    "rating": rating, 
                    "text": comment
                })
                save_data(data)
                break
    return redirect(url_for("store_detail", store_id=store_id))

@app.route("/coupons")
def coupons():
    data = load_data()
    user_college = session.get('college', '기타')
    
    filtered_partnerships = [
        p for p in data.get("partnerships", []) 
        if p.get("target") == "전체" or p.get("target") == user_college
    ]
    return render_page(COUPONS_HTML, active_tab="coupons", partnerships=filtered_partnerships)

@app.route("/profile")
def profile():
    return render_page(PROFILE_HTML, active_tab="profile")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
