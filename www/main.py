from browser import document, window, html, timer
import json, re
import datetime

# --- 初期設定・定数 ---
storage = window.localStorage
saved_regions = []
current_lang = "ja"

real_eq_data = []      
real_tsunami_data = [] 
debug_eq_data = []     
debug_tsunami_data = []

# 通知・制御用
last_eq_id = None
is_debug_mode = False  
target_count = 10      
current_display_limit = 10 
is_initial_loaded = False

SCALE_CLASSES = {
    10: "scale-1", 20: "scale-2", 30: "scale-3", 40: "scale-4",
    45: "scale-5l", 50: "scale-5h", 55: "scale-6l", 60: "scale-6h", 70: "scale-7"
}

tsunami_areas = [
    "北海道太平洋沿岸東部","北海道太平洋沿岸中部","北海道太平洋沿岸西部","北海道日本海沿岸北部",
    "北海道日本海沿岸南部","オホーツク海沿岸","青森県太平洋沿岸","青森県日本海沿岸",
    "陸奥湾","岩手県沿岸北部","宮城県北部","宮城県中部","宮城県南部","秋田県沿岸北部","山形県庄内",
    "福島県浜通り","茨城県北部","茨城県南部","千葉県九十九里・外房","千葉県内房","東京湾内湾",
    "伊豆諸島","小笠原諸島","相模湾・三浦半島","新潟県上中下越","佐渡","富山県","石川県能登","石川県加賀",
    "福井県嶺北","福井県嶺南","静岡県各部","愛知県外海","伊勢湾・三河湾","大阪府沿岸","兵庫県瀬戸内海沿岸",
    "和歌山県沿岸","鳥取県沿岸","島根県沿岸","岡山県沿岸","広島県沿岸","山口県沿岸","徳島県沿岸",
    "香川県沿岸","愛媛県沿岸","高知県沿岸","福岡県沿岸","佐賀県沿岸","長崎県沿岸","熊本県沿岸",
    "大分県沿岸","宮崎県沿岸","鹿児島県沿岸","奄美群島・トカラ列島","沖縄本島地方","宮古島・八重山地方"
]

PREF_DICT = {
    "北海道": {"en": "Hokkaido", "ko": "홋카이도", "zh": "北海道", "zh-tw": "北海道"},
    "青森県": {"en": "Aomori", "ko": "아오모리", "zh": "青森", "zh-tw": "青森"},
    "岩手県": {"en": "Iwate", "ko": "이와테", "zh": "岩手", "zh-tw": "岩手"},
    "宮城県": {"en": "Miyagi", "ko": "미야기", "zh": "宫城", "zh-tw": "宮城"},
    "秋田県": {"en": "Akita", "ko": "아키타", "zh": "秋田", "zh-tw": "秋田"},
    "山形県": {"en": "Yamagata", "ko": "야마가타", "zh": "山形", "zh-tw": "山形"},
    "福島県": {"en": "Fukushima", "ko": "후쿠시마", "zh": "福岛", "zh-tw": "福島"},
    "茨城県": {"en": "Ibaraki", "ko": "이바라키", "zh": "茨城", "zh-tw": "茨城"},
    "栃木県": {"en": "Tochigi", "ko": "토치기", "zh": "栃木", "zh-tw": "栃木"},
    "群馬県": {"en": "Gunma", "ko": "군마", "zh": "群马", "zh-tw": "群馬"},
    "埼玉県": {"en": "Saitama", "ko": "사이타마", "zh": "埼玉", "zh-tw": "埼玉"},
    "千葉県": {"en": "Chiba", "ko": "지바", "zh": "千叶", "zh-tw": "千葉"},
    "東京都": {"en": "Tokyo", "ko": "도쿄", "zh": "东京", "zh-tw": "東京"},
    "神奈川県": {"en": "Kanagawa", "ko": "카나가와", "zh": "神奈川", "zh-tw": "神奈川"},
    "新潟県": {"en": "Niigata", "ko": "니이가타", "zh": "新潟", "zh-tw": "新潟"},
    "富山県": {"en": "Toyama", "ko": "도야마", "zh": "富山", "zh-tw": "富山"},
    "石川県": {"en": "Ishikawa", "ko": "이시카와", "zh": "石川", "zh-tw": "石川"},
    "福井県": {"en": "Fukui", "ko": "후쿠이", "zh": "福井", "zh-tw": "福井"},
    "山梨県": {"en": "Yamanashi", "ko": "야마나시", "zh": "山梨", "zh-tw": "山梨"},
    "長野県": {"en": "Nagano", "ko": "나가노", "zh": "长野", "zh-tw": "長野"},
    "岐阜県": {"en": "Gifu", "ko": "기후", "zh": "岐阜", "zh-tw": "岐阜"},
    "静岡県": {"en": "Shizuoka", "ko": "시즈오카", "zh": "静冈", "zh-tw": "靜岡"},
    "愛知県": {"en": "Aichi", "ko": "아이치", "zh": "爱知", "zh-tw": "愛知"},
    "三重県": {"en": "Mie", "ko": "미에", "zh": "三重", "zh-tw": "三重"},
    "滋賀県": {"en": "Shiga", "ko": "시가", "zh": "滋贺", "zh-tw": "滋賀"},
    "京都府": {"en": "Kyoto", "ko": "교토", "zh": "京都", "zh-tw": "京都"},
    "大阪府": {"en": "Osaka", "ko": "오사카", "zh": "大阪", "zh-tw": "大阪"},
    "兵庫県": {"en": "Hyogo", "ko": "효고", "zh": "兵库", "zh-tw": "兵庫"},
    "奈良県": {"en": "Nara", "ko": "나라", "zh": "奈良", "zh-tw": "奈良"},
    "和歌山県": {"en": "Wakayama", "ko": "와카야마", "zh": "和歌山", "zh-tw": "和歌山"},
    "鳥取県": {"en": "Tottori", "ko": "돗토리", "zh": "鸟取", "zh-tw": "鳥取"},
    "島根県": {"en": "Shimane", "ko": "시마네", "zh": "岛根", "zh-tw": "島根"},
    "岡山県": {"en": "Okayama", "ko": "오카야마", "zh": "冈山", "zh-tw": "岡山"},
    "広島県": {"en": "Hiroshima", "ko": "히로시마", "zh": "广岛", "zh-tw": "廣島"},
    "山口県": {"en": "Yamaguchi", "ko": "야마구치", "zh": "山口", "zh-tw": "山口"},
    "徳島県": {"en": "Tokushima", "ko": "도쿠시마", "zh": "德岛", "zh-tw": "德島"},
    "香川県": {"en": "Kagawa", "ko": "카가와", "zh": "香川", "zh-tw": "香川"},
    "愛媛県": {"en": "Ehime", "ko": "에히메", "zh": "爱媛", "zh-tw": "愛媛"},
    "高知県": {"en": "Kochi", "ko": "고치", "zh": "高知", "zh-tw": "高知"},
    "福岡県": {"en": "Fukuoka", "ko": "후쿠오카", "zh": "福冈", "zh-tw": "福岡"},
    "佐賀県": {"en": "Saga", "ko": "사가", "zh": "佐贺", "zh-tw": "佐賀"},
    "長崎県": {"en": "Nagasaki", "ko": "나가사키", "zh": "长崎", "zh-tw": "長崎"},
    "熊本県": {"en": "Kumamoto", "ko": "쿠마모토", "zh": "熊本", "zh-tw": "熊本"},
    "大分県": {"en": "Oita", "ko": "오이타", "zh": "大分", "zh-tw": "大分"},
    "宮崎県": {"en": "Miyazaki", "ko": "미야자키", "zh": "宫崎", "zh-tw": "宮崎"},
    "鹿児島県": {"en": "Kagoshima", "ko": "카고시마", "zh": "鹿儿岛", "zh-tw": "鹿兒島"},
    "沖縄県": {"en": "Okinawa", "ko": "오키나와", "zh": "冲绳", "zh-tw": "沖縄"}
}

PREF_CHINESE_DICT = {
    "北海道": {"zh": "北海道", "zh-tw": "北海道"},
    "青森県": {"zh": "青森", "zh-tw": "青森"},
    "岩手県": {"zh": "岩手", "zh-tw": "岩手"},
    "宮城県": {"zh": "宫城", "zh-tw": "宮城"},
    "秋田県": {"zh": "秋田", "zh-tw": "秋田"},
    "山形県": {"zh": "山形", "zh-tw": "山形"},
    "福島県": {"zh": "福岛", "zh-tw": "福島"},
    "茨城県": {"zh": "茨城", "zh-tw": "茨城"},
    "栃木県": {"zh": "栃木", "zh-tw": "栃木"},
    "群馬県": {"zh": "群马", "zh-tw": "群馬"},
    "埼玉県": {"zh": "埼玉", "zh-tw": "埼玉"},
    "千葉県": {"zh": "千叶", "zh-tw": "千葉"},
    "東京都": {"zh": "东京", "zh-tw": "東京"},
    "神奈川県": {"zh": "神奈川", "zh-tw": "神奈川"},
    "新潟県": {"zh": "新潟", "zh-tw": "新潟"},
    "富山県": {"zh": "富山", "zh-tw": "富山"},
    "石川県": {"zh": "石川", "zh-tw": "石川"},
    "福井県": {"zh": "福井", "zh-tw": "福井"},
    "山梨県": {"zh": "山梨", "zh-tw": "山梨"},
    "長野県": {"zh": "长野", "zh-tw": "長野"},
    "岐阜県": {"zh": "岐阜", "zh-tw": "岐阜"},
    "静岡県": {"zh": "静冈", "zh-tw": "靜岡"},
    "愛知県": {"zh": "爱知", "zh-tw": "愛知"},
    "三重県": {"zh": "三重", "zh-tw": "三重"},
    "滋賀県": {"zh": "滋贺", "zh-tw": "滋賀"},
    "京都府": {"zh": "京都", "zh-tw": "京都"},
    "大阪府": {"zh": "大阪", "zh-tw": "大阪"},
    "兵庫県": {"zh": "兵库", "zh-tw": "兵庫"},
    "奈良県": {"zh": "奈良", "zh-tw": "奈良"},
    "和歌山県": {"zh": "和歌山", "zh-tw": "和歌山"},
    "鳥取県": {"zh": "鸟取", "zh-tw": "鳥取"},
    "島根県": {"zh": "岛根", "zh-tw": "島根"},
    "岡山県": {"zh": "冈山", "zh-tw": "岡山"},
    "広島県": {"zh": "广岛", "zh-tw": "廣島"},
    "山口県": {"zh": "山口", "zh-tw": "山口"},
    "徳島県": {"zh": "德岛", "zh-tw": "德島"},
    "香川県": {"zh": "香川", "zh-tw": "香川"},
    "愛媛県": {"zh": "爱媛", "zh-tw": "愛媛"},
    "高知県": {"zh": "高知", "zh-tw": "高知"},
    "福岡県": {"zh": "福冈", "zh-tw": "福岡"},
    "佐賀県": {"zh": "佐贺", "zh-tw": "佐賀"},
    "長崎県": {"zh": "长崎", "zh-tw": "長崎"},
    "熊本県": {"zh": "熊本", "zh-tw": "熊本"},
    "大分県": {"zh": "大分", "zh-tw": "大分"},
    "宮崎県": {"zh": "宫崎", "zh-tw": "宮崎"},
    "鹿児島県": {"zh": "鹿儿岛", "zh-tw": "鹿兒島"},
    "沖縄県": {"zh": "冲绳", "zh-tw": "沖繩"}
}

UI_DICT = {
    "ja": {
        "title": "地震・津波情報アプリ", "region_h3": "マイ地域設定", "pref_op": "都道府県を選択",
        "add": "追加", "refresh": "最新情報に更新", "more": "さらに読み込む", "close": "閉じる",
        "tsunami_none": "🌊津波情報（発表なし：タップで詳細表示）", "tsunami_hint": "🌊津波警報・注意報（詳細表示）",
        "tsunami_title": "津波情報", "now_time": "現在時刻", "tsunami_empty": "現在、発表されている津波警報・注意報はありません。",
        "detail_title": "震源詳細", "hypo": "震源地", "max_scale": "最大震度", "depth": "深さ", "mag": "マグニチュード", "loading": "読み込み中...",
        "noti_on": "通知を有効にする", "new_eq": "新しい地震",
        "noti_granted": "通知が許可されました！", "noti_denied": "通知が拒否されています。",
        "tab_shindo": "各地の震度", "tab_lpgm": "長周期地震動", "approx": "約", "unknown": "不明", 
        "no_lp_info": "この地震による長周期地震動の情報はありません。", 
        "notify_req_body": "通知を許可しますか？",
        "notify_enabled": "通知を有効にしました", 
        "my_area_label": "マイ地域"
    },
    "en": {
        "title": "Earthquake Info", "region_h3": "Region Settings", "pref_op": "Select Prefecture",
        "add": "Add", "refresh": "Refresh", "more": "Load More", "close": "Close",
        "tsunami_none": "🌊Tsunami Info (None: Tap for Details)", "tsunami_hint": "🌊Tsunami Warning (Details)",
        "tsunami_title": "Tsunami Information", "now_time": "Current Time", "tsunami_empty": "No tsunami warnings in effect.",
        "detail_title": "Seismic Detail", "hypo": "Epicenter", "max_scale": "Max Intensity", "depth": "Depth", "mag": "Magnitude", "loading": "Loading...",
        "noti_on": "Enable Notifications", "new_eq": "New Earthquake",
        "noti_granted": "Notifications enabled!", "noti_denied": "Notifications are denied.",
        "tab_shindo": "Seismic Intensity", "tab_lpgm": "LPGM Class", "approx": "Approx. ", "unknown": "Unknown", 
        "no_lp_info": "No long-period ground motion information for this earthquake.", 
        "notify_req_body": "Allow notifications?",
        "notify_enabled": "Notifications enabled", 
        "my_area_label": "My Region"
    },
    "ko": {
        "title": "지진·쓰나미 정보", "region_h3": "지역 설정", "pref_op": "도도부현 선택",
        "add": "추가", "refresh": "최신 정보", "more": "더 보기", "close": "닫기",
        "tsunami_none": "🌊쓰나미 정보 (없음: 상세 보기)", "tsunami_hint": "🌊쓰나미 경보 (상세 보기)",
        "tsunami_title": "쓰나미 정보", "now_time": "현재 시각", "tsunami_empty": "현재 발표된 쓰나미 경보가 없습니다.",
        "detail_title": "지진 상세", "hypo": "진원지", "max_scale": "최대 진도", "depth": "깊이", "mag": "규모", "loading": "로딩 중...",
        "noti_on": "알림 활성화", "new_eq": "새로운 지진",
        "noti_granted": "알림이 허용되었습니다!", "noti_denied": "알림이 거부되었습니다.",
        "tab_shindo": "지역별 진도", "tab_lpgm": "장주기 지진동", "approx": "약 ", "unknown": "미상", 
        "no_lp_info": "이 지진에 의한 장주기 지진동 정보는 없습니다.", 
        "notify_req_body": "알림을 허용하시겠습니까?",
        "notify_enabled": "알림이 활성화되었습니다", 
        "my_area_label": "내 지역"
    },
    "zh": {
        "title": "地震·海啸信息", "region_h3": "我的地区设置", "pref_op": "选择都道府县",
        "add": "添加", "refresh": "更新信息", "more": "加载更多", "close": "关闭",
        "tsunami_none": "🌊海啸信息（未发布：点击查看详情）", "tsunami_hint": "🌊海啸警报（查看详情）",
        "tsunami_title": "海啸信息", "now_time": "当前时间", "tsunami_empty": "目前没有发布的海啸警報。",
        "detail_title": "震源详情", "hypo": "震中", "max_scale": "最大震度", "depth": "深度", "mag": "震级", "loading": "加载中...",
        "noti_on": "启用通知", "new_eq": "新地震",
        "noti_granted": "通知已启用！", "noti_denied": "通知已被拒绝。",
        "tab_shindo": "各地震度", "tab_lpgm": "长周期地震动", "approx": "约", "unknown": "未知", 
        "no_lp_info": "本次地震无长周期地震动相关信息。", 
        "notify_req_body": "允许通知吗？",
        "notify_enabled": "已启用通知", 
        "my_area_label": "我的地区"
    },
    "zh-tw": {
        "title": "地震·海嘯資訊", "region_h3": "我的地區設定", "pref_op": "選擇都道府縣",
        "add": "新增", "refresh": "更新資訊", "more": "加載更多", "close": "關閉",
        "tsunami_none": "🌊海嘯資訊（未發布：點擊查看詳情）", "tsunami_hint": "🌊海嘯警報（加載詳情）",
        "tsunami_title": "海嘯資訊", "now_time": "當前時間", "tsunami_empty": "目前沒有發布的海嘯警報。",
        "detail_title": "震央詳情", "hypo": "震央", "max_scale": "最大震度", "depth": "深度", "mag": "震級", "loading": "載入中...",
        "noti_on": "啟用通知", "new_eq": "新地震",
        "noti_granted": "通知已啟用！", "noti_denied": "通知已被拒絶。",
        "tab_shindo": "各地震度", "tab_lpgm": "長周期地震動", "approx": "約", "unknown": "未知", 
        "no_lp_info": "本次地震無長周期地震動相關資訊。", 
        "notify_req_body": "允許通知嗎？",
        "notify_enabled": "已啟用通知", 
        "my_area_label": "我的地區"
    }
}

# --- 翻訳・ユーティリティ関数 ---

def translate_lp_term(text):
    return text

def scale_to_text(scale):
    m = {10:"1", 20:"2", 30:"3", 40:"4", 45:"5弱", 50:"5強", 55:"6弱", 60:"6強", 70:"7"}
    res = m.get(scale, "不明" if current_lang == "ja" else "Unknown")
    if current_lang != "ja":
        res = res.replace("弱", "-").replace("強", "+")
    return res

def lp_scale_to_text(lp_scale):
    if lp_scale <= 0: return ""
    return f"階級{lp_scale}" if current_lang == "ja" else f"Class {lp_scale}"

def get_scale_class(scale):
    return SCALE_CLASSES.get(scale, "")

def format_address(addr):
    if not addr: return ""
    pattern = re.compile('^.+?[市区町村]')
    m = pattern.search(str(addr))
    if m: return m.group(0)
    return ""

def translate_place_chinese(text):
    if not text: return text
    l_key = current_lang.lower()
    for jp_pref, trans_dict in PREF_CHINESE_DICT.items():
        if jp_pref in text:
            translated = trans_dict.get(l_key, jp_pref)
            return text.replace(jp_pref, translated)
    if text[-1] in ["都", "府", "県"]:
        text = text[:-1]
    return text

def translate_place(text):
    if not text or current_lang == "ja": 
        return text
    if current_lang in ["zh", "zh-tw"]:
        return translate_place_chinese(text)
    l_key = current_lang.lower()
    for jp_pref, trans_dict in PREF_DICT.items():
        if jp_pref in text:
            translated = trans_dict.get(l_key)
            if translated:
                return text.replace(jp_pref, translated)
    return text

def setup_notification_with_translation(ev):
    ui = UI_DICT[current_lang]
    if not window.confirm(ui["notify_req_body"]):
        return

    def on_permission(permission):
        if permission == "granted":
            window.localStorage.setItem("notification_enabled", "1")
        # ★ここに追加: 結果に応じてボタンを書き換える
        update_notify_button()

    try:
        window.Notification.requestPermission().then(on_permission)
    except:
        window.Notification.requestPermission(on_permission)

def check_notification(data):
    if not data: return
    latest_eq = data[0]
    eq_id = latest_eq.get("id")
    try:
        last_id = storage.getItem("last_notified_id")
        if last_id is not None and str(last_id) == str(eq_id):
            return
    except:
        pass 
    
    ui = UI_DICT[current_lang]
    earth = latest_eq.get("earthquake", {})
    hypo = earth.get("hypocenter", {})
    max_scale = earth.get("maxScale", 0)
    
    translated_hypo = translate_place(hypo.get("name", "不明"))
    scale_text = scale_to_text(max_scale)
    
    title = f"{ui['new_eq']}: {translated_hypo}"
    body = f"{ui['max_scale']}: {scale_text}"
    
    if hasattr(window, "Notification") and window.Notification.permission == "granted":
        window.Notification.new(title, {"body": body})

    storage.setItem("last_notified_id", str(eq_id))

def get_max_scale_pref(eq_item):
    e = eq_item.get("earthquake", {})
    max_scale = e.get("maxScale", 0)
    points = eq_item.get("points", [])
    if not points or max_scale <= 0:
        return e.get("hypocenter", {}).get("name", "Unknown")
    max_prefs = list(dict.fromkeys([
        p.get("pref") for p in points 
        if p.get("scale") == max_scale and p.get("pref")
    ]))
    return max_prefs[0] if max_prefs else e.get("hypocenter", {}).get("name", "Unknown")

# --- 詳細表示ロジック (修正対象) ---

def show_detail_by_idx(idx, current_list):
    ui = UI_DICT[current_lang]
    eq = current_list[idx]
    earth = eq.get("earthquake", {})
    hypo = earth.get("hypocenter", {})
    lp_data = earth.get("longPeriod", {})
    max_lp = lp_data.get("maxClass", 0)
    
    mag_raw = hypo.get("magnitude")
    mag = mag_raw if mag_raw is not None else -1
    dep_raw = hypo.get("depth")
    dep = dep_raw if dep_raw is not None else -1
    lat = hypo.get("latitude", 0) or 0
    lng = hypo.get("longitude", 0) or 0
    points = eq.get("points", [])
    
    unknown_text = ui["unknown"]
    approx_text = ui["approx"]

    content = document["detail_content"]
    content.innerHTML = ""

    h = html.DIV()
    max_pref = get_max_scale_pref(eq)
    max_pref_translated = translate_place(max_pref)

    h <= html.H2(f"{ui['detail_title']} - {max_pref_translated}", 
                 style={'borderBottom':'2px solid #333', 'paddingBottom':'5px', 'margin':'0 0 10px 0'})

    mag_text = f"M{mag}" if mag >= 0 else unknown_text
    dep_text = f"{approx_text}{dep}km" if dep >= 0 else unknown_text

    summary = html.DIV(
        style='padding:10px; background:#f8f9fa; border-radius:8px; font-weight:bold; font-size:0.9em; border-left:5px solid #333;'
    )
    summary.innerHTML = f"{ui['hypo']}: {translate_place(hypo.get('name','不明'))}<br>{ui['max_scale']}: {scale_to_text(earth.get('maxScale', 0))} / {mag_text} / {ui['depth']}: {dep_text}"
    h <= summary
    content <= h

    tab_container = html.DIV(style={'display':'flex', 'margin-top':'15px', 'border-bottom':'2px solid #eee'})
    btn_shindo = html.BUTTON(ui["tab_shindo"], style={'flex':1, 'padding':'10px', 'border':'none', 'background':'#007bff', 'color':'white', 'cursor':'pointer', 'fontWeight':'bold'})
    btn_lp = html.BUTTON(ui["tab_lpgm"], style={'flex':1, 'padding':'10px', 'border':'none', 'background':'#eee', 'color':'#666', 'cursor':'pointer'})
    
    tab_container <= btn_shindo
    tab_container <= btn_lp
    content <= tab_container

    view_shindo = html.DIV(style={'display':'block', 'overflow-y':'auto', 'max-height':'40vh', 'padding-top':'10px'})
    view_lp = html.DIV(style={'display':'none', 'overflow-y':'auto', 'max-height':'40vh', 'padding-top':'10px'})
    
    # --- 修正: 都道府県（pr）だけを判定して強調するロジック ---
    if points:
        city_max_scale = {}
        for p in points:
            sc = p.get("scale", 0)
            city = format_address(p.get("addr", ""))
            if city not in city_max_scale or sc > city_max_scale[city]:
                city_max_scale[city] = sc
        scale_map = {}
        for p in points:
            city = format_address(p.get("addr", ""))
            sc = city_max_scale[city]
            pr = p.get("pref", "Unknown")
            if sc not in scale_map: scale_map[sc] = {}
            if pr not in scale_map[sc]: scale_map[sc][pr] = []
            if city not in scale_map[sc][pr]:
                scale_map[sc][pr].append(city)

        for sc in sorted(scale_map.keys(), reverse=True):
            # 震度アイコン
            view_shindo <= html.DIV(f"震度 {scale_to_text(sc)}", Class=get_scale_class(sc), style='color:white; padding:5px 10px; margin-top:10px; border-radius:4px; font-weight:bold;')
            
            for pr in sorted(scale_map[sc].keys()):
                # 都道府県が保存リストに含まれているか判定
                is_my_pref = pr in saved_regions
                
                # スタイル分岐
                if is_my_pref:
                    # 強調スタイル（背景ピンク、太字、★付き）
                    pref_style = {'fontWeight':'bold', 'marginTop':'12px', 'fontSize':'1.0em', 'color':'#d63384', 'background':'#fff0f6', 'padding':'6px', 'borderRadius':'6px', 'borderLeft':'4px solid #d63384'}
                    pref_text = f"★ {translate_place(pr)}"
                else:
                    # 通常スタイル
                    pref_style = {'fontWeight':'bold', 'marginTop':'8px', 'fontSize':'0.9em', 'padding':'2px 0'}
                    pref_text = f"【{translate_place(pr)}】"

                view_shindo <= html.DIV(pref_text, style=pref_style)
                
                # 市町村はシンプルに羅列（個別強調なし）
                cities_str = " ・".join(scale_map[sc][pr])
                view_shindo <= html.DIV(cities_str, style='padding:2px 5px; font-size:0.85em; color:#555; lineHeight:1.5;')
    # ---------------------------------------------------

    if max_lp > 0 or is_debug_mode: 
        display_lp_max = max_lp if max_lp > 0 else 1
        view_lp <= html.DIV(f"{ui['max_scale']} {lp_scale_to_text(display_lp_max)}", 
                             style={'font-size':'1.2em', 'font-weight':'bold', 'color':'#d32f2f', 
                                    'padding':'10px', 'text-align':'center', 'background':'#fff0f0', 'border-radius':'8px'})
        lp_map = {}
        has_lp_points = False
        for p in points:
            l_sc = p.get("lpgmScore", 0) 
            if l_sc > 0:
                has_lp_points = True
                pr = p.get("pref", "Unknown")
                city = format_address(p.get("addr", ""))
                if l_sc not in lp_map: lp_map[l_sc] = {}
                if pr not in lp_map[l_sc]: lp_map[l_sc][pr] = []
                if city not in lp_map[l_sc][pr]:
                    lp_map[l_sc][pr].append(city)
        if not has_lp_points:
            view_lp <= html.DIV("観測地点の詳細は発表されていません。", style={'padding':'20px', 'text-align':'center', 'color':'#666'})
        else:
            for l_sc in sorted(lp_map.keys(), reverse=True):
                view_lp <= html.DIV(f"{lp_scale_to_text(l_sc)} 観測地域", 
                                     style={'background':'#d32f2f', 'color':'white', 'padding':'5px 10px', 'margin-top':'10px', 'border-radius':'4px', 'font-weight':'bold', 'font-size':'0.9em'})
                for pr in sorted(lp_map[l_sc].keys()):
                    view_lp <= html.DIV(f"【{translate_place(pr)}】", style={'fontWeight':'bold', 'marginTop':'8px', 'fontSize':'0.9em'})
                    view_lp <= html.DIV(" ・".join(lp_map[l_sc][pr]), style='padding:2px 5px; font-size:0.85em; color:#555;')
    else:
        view_lp <= html.DIV(ui.get("no_lp_info", "---"), style={'padding':'40px 20px', 'text-align':'center', 'color':'#999'})

    content <= view_shindo
    content <= view_lp

    def switch_to_shindo(ev):
        view_shindo.style.display = "block"
        view_lp.style.display = "none"
        btn_shindo.style.background = "#007bff"; btn_shindo.style.color = "white"
        btn_lp.style.background = "#eee"; btn_lp.style.color = "#666"

    def switch_to_lp(ev):
        view_shindo.style.display = "none"
        view_lp.style.display = "block"
        btn_shindo.style.background = "#eee"; btn_shindo.style.color = "#666"
        btn_lp.style.background = "#d32f2f"; btn_lp.style.color = "white"

    btn_shindo.bind("click", switch_to_shindo)
    btn_lp.bind("click", switch_to_lp)

    document["map"].style.display = "block"
    document["content_detail"].style.display = "block"
    
    if hasattr(window, "updateMap") and lat != 0 and lng != 0:
        window.updateMap(lat, lng)

def render_tsunami_colors():
    if not hasattr(window, 'coastalRegionsGeoJSON'): return
    pass

def show_tsunami_detail(tsunami_list):
    ui = UI_DICT[current_lang]
    h_container = html.DIV()
    title_row = html.DIV(style={"display":"flex", "justifyContent":"space-between", "alignItems":"center", "borderBottom":"2px solid #333", "paddingBottom":"8px", "marginTop":"0"})
    title_row <= html.H2(ui["tsunami_title"], style={"margin":"0"})
    time_div = html.DIV(style={"fontSize":"0.85em", "color":"#666"})
    title_row <= time_div
    h_container <= title_row
    update_current_time(time_div)
    timer.set_interval(lambda: update_current_time(time_div), 1000)

    if tsunami_list:
        table = html.TABLE(style='width:100%; border-collapse:collapse; margin-top:10px; background:white;')
        header = html.TR(style='background:#f0f0f0; border-bottom:2px solid #ccc;')
        header <= html.TH(ui.get("hypo", "地域"), style='padding:10px; text-align:left; font-size:0.9em;')
        header <= html.TH("到達予想 / 高さ", style='padding:10px; text-align:right; font-size:0.9em;')
        table <= header
        for t in tsunami_list:
            grade = t.get("grade", "")
            color = "#d32f2f" if grade in ["majorWarning", "warning"] else "#333"
            row = html.TR(style='border-bottom:1px solid #eee;')
            row <= html.TD(translate_place(t.get('name','')), style=f'padding:12px 10px; font-weight:bold; color:{color};')
            time_h = t.get('firstHeight', {}).get('arrivalTime', '---')
            max_h = t.get('maxHeight', {}).get('description', '---')
            display_time = format_arrival_time(time_h)
            info_td = html.TD(style='padding:12px 10px; text-align:right; font-size:0.95em;')
            info_td.innerHTML = f"{display_time} / <span style='font-weight:bold; font-size:1.1em;'>{max_h}</span>"
            row <= info_td
            table <= row
        h_container <= table
    else:
        h_container <= html.DIV(ui["tsunami_empty"], style={"padding":"40px 20px", "textAlign":"center", "color":"#666"})

    document["detail_content"].innerHTML = "" 
    document["detail_content"] <= h_container
    document["map"].style.display = "none"
    document["content_detail"].style.display = "block"

# --- 後半部分: リスト表示・API取得 ---

def create_tsunami_card(tsunami_data):
    ui = UI_DICT[current_lang]
    if not tsunami_data:
        card = html.DIV(ui["tsunami_none"], style={"background":"#e3f2fd","color":"#0d47a1","padding":"15px","borderRadius":"10px","textAlign":"center","cursor":"pointer","border":"1px solid #bbdefb","fontWeight":"bold","margin":"15px 0"})
        card.bind("click", lambda e: show_tsunami_detail(tsunami_data))
        return card
    container = html.DIV()
    hint = html.DIV(ui["tsunami_hint"], style={"textAlign":"center","fontSize":"0.9em","color":"#333","fontWeight":"bold","marginBottom":"10px","cursor":"pointer"})
    hint.bind("click", lambda e: show_tsunami_detail(tsunami_data))
    container <= hint
    labels_dict = {
        "ja": {"majorWarning": "大津波警報", "warning": "津波警報", "watch": "津波注意報"},
        "en": {"majorWarning": "Major Tsunami Warning", "warning": "Tsunami Warning", "watch": "Tsunami Advisory"},
        "ko": {"majorWarning": "대쓰나미 경보", "warning": "쓰나미 경보", "watch": "쓰나미 주의보"},
        "zh": {"majorWarning": "大海啸警报", "warning": "海啸警报", "watch": "海啸注意报"},
        "zh-tw": {"majorWarning": "大海嘯警報", "warning": "海嘯警報", "watch": "海嘯注意報"}
    }
    current_labels = labels_dict.get(current_lang, labels_dict["ja"])
    for it in tsunami_data[:3]:
        g = it.get("grade")
        bg = "#800080" if g=="majorWarning" else "#ff0000" if g=="warning" else "#fdd835"
        txt_color = "#fff" if g!="watch" else "#333"
        card = html.DIV(style={"background":bg,"color":txt_color,"padding":"15px","borderRadius":"10px","marginBottom":"12px","display":"flex","justifyContent":"space-between","cursor":"pointer","boxShadow":"0 4px 10px rgba(0,0,0,0.15)"})
        L, R = html.DIV(), html.DIV(style={"textAlign":"right"})
        L <= html.DIV(current_labels.get(g, ""), style={"fontSize":"0.7em","opacity":"0.8"})
        L <= html.DIV(translate_place(it.get("name","")), style={"fontWeight":"bold"})
        time_div = html.DIV(style={"fontSize":"0.8em"})
        time_div.innerHTML = format_arrival_time(it.get("firstHeight", {}).get("arrivalTime", ""))
        R <= time_div
        R <= html.DIV(it.get("maxHeight", {}).get("description", ""), style={"fontWeight":"bold","fontSize":"1.2em"})
        card <= L + R
        card.bind("click", lambda e, data=tsunami_data: show_tsunami_detail(data))
        container <= card
    return container

def render_list(eq_data, tsunami_data):
    if "result" not in document: return
    ui = UI_DICT[current_lang]
    container = document["result"]
    container.innerHTML = ""
    container <= create_tsunami_card(tsunami_data)
    
    for i, eq in enumerate(eq_data):
        e = eq.get("earthquake", {})
        max_scale = e.get("maxScale", 0)
        if max_scale <= 0: continue
        
        lp_data = e.get("longPeriod", {})
        max_lp = lp_data.get("maxClass", 0)
        hypo_name = e.get("hypocenter", {}).get("name", "Unknown")
        display_place = hypo_name if current_lang == "ja" else translate_place(get_max_scale_pref(eq))
        tm = str(e.get("time", ""))[5:16].replace("T", " ")
        
        # --- マイ地域の最大震度を計算 ---
        hit = False
        my_max_scale = 0
        
        if any(reg in hypo_name for reg in saved_regions if reg):
            hit = True
        
        points = eq.get("points", [])
        if saved_regions:
            for p in points:
                addr = p.get("addr", "")
                pref = p.get("pref", "")
                p_scale = p.get("scale", 0)
                
                is_match = False
                for reg in saved_regions:
                    if reg and (reg in addr or reg in pref):
                        is_match = True
                        break
                
                if is_match:
                    hit = True
                    if p_scale > my_max_scale:
                        my_max_scale = p_scale
        # --------------------------------
        
        item = html.DIV(Class="earthquake-item", id=f"eq_{i}")
        item.style.borderRadius = "10px"; item.style.overflow = "hidden"; item.style.marginBottom = "10px"
        item.style.border = "1px solid #eee"; item.style.display = "flex"; item.style.alignItems = "stretch" 
        
        # 左端：全体の最大震度
        item <= html.DIV(scale_to_text(max_scale), Class=f"col col-intensity {get_scale_class(max_scale)}")
        
        if hit:
            item.style.borderLeft = "6px solid #ff0000"; item.style.background = "#fff0f0"; item.style.fontWeight = "bold"
        
        # 中央：時間と場所
        center_div = html.DIV(style={"flex": "1", "padding": "10px", "display": "flex", "flexDirection": "column", "justifyContent": "center"})
        
        time_row = html.DIV(tm, style={"fontSize": "0.85em", "color": "#666"})
        if max_lp > 0:
            lp_label = "長周期階級" if current_lang == "ja" else "LPGM Class"
            lp_span = html.SPAN(f" {lp_label} {max_lp}", style={"fontSize": "0.8em", "color": "#d32f2f", "marginLeft": "5px", "fontWeight": "bold"})
            time_row <= lp_span
        center_div <= time_row
        center_div <= html.DIV(display_place, style={"fontSize": "1em", "fontWeight": "bold", "whiteSpace": "nowrap", "overflow": "hidden", "textOverflow": "ellipsis"})
        item <= center_div

        # --- 右端：マイ地域情報エリア ---
        
        # ベースとなるスタイル
        my_reg_style = {
            "display": "flex", 
            "flexDirection": "column", 
            "alignItems": "center", 
            "justifyContent": "center", 
            "minWidth": "75px",
            "padding": "0 5px",
            "margin": "4px",        # 周囲に余白を作る
            "borderRadius": "6px",  # 角を丸くする
            "boxShadow": "0 1px 2px rgba(0,0,0,0.1)" 
        }
        
        if my_max_scale > 0:
            # 揺れがある場合: 震度クラスを適用しつつ、文字色を白で上書き
            my_scale_class = get_scale_class(my_max_scale)
            my_reg_style["border"] = "none"
            my_reg_style["color"] = "white" # ← 文字色を白に指定
        else:
            # 揺れがない場合
            my_scale_class = ""
            my_reg_style["background"] = "#f9f9f9"
            my_reg_style["color"] = "#aaaaaa"
            my_reg_style["border"] = "1px solid #eee"
        
        my_reg_div = html.DIV(Class=my_scale_class, style=my_reg_style)
        
        # 上段：ラベル
        lbl_text = ui.get("my_area_label", "マイ地域")
        # 背景色があるので、少し透明度を下げて馴染ませる（白文字ベース）
        lbl_opacity = "0.9" if my_max_scale > 0 else "1.0"
        my_reg_div <= html.DIV(lbl_text, style={"fontSize": "0.6em", "marginBottom": "2px", "opacity": lbl_opacity})
        
        # 下段：震度
        val_text = scale_to_text(my_max_scale) if my_max_scale > 0 else "-"
        my_reg_div <= html.DIV(val_text, style={"fontWeight": "bold", "fontSize": "1.3em"})
        
        item <= my_reg_div
        # --------------------------------

        item.bind("click", lambda e, idx=i, data=eq_data: show_detail_by_idx(idx, data))
        container <= item

def remove_region(ev):
    val = ev.target.getAttribute("data-val")
    if val in saved_regions:
        saved_regions.remove(val)
        storage.setItem("my_earthquake_regions", json.dumps(saved_regions))
        render_region_list()
        refresh_view()

def format_arrival_time(text):
    if text == "直ちに到達":
        label = "すぐ来る" if current_lang == "ja" else "Soon"
        style = "border:2px solid #ff0000; background:#ffffff; color:#ff0000; padding:1px 7px; border-radius:4px; font-weight:bold; display:inline-block;"
        return f'<span style="{style}">{label}</span>'
    return text

def update_current_time(div):
    now = datetime.datetime.now()
    div.text = f"現在時刻: {now.strftime('%Y/%m/%d %H:%M:%S')}"

def refresh_view():
    render_list(debug_eq_data if is_debug_mode else real_eq_data, debug_tsunami_data if is_debug_mode else real_tsunami_data)

# --- 通知チェック関数（正しい震源地名を表示する版） ---
def check_notification(data):
    if not data: return
    latest_eq = data[0]
    eq_id = latest_eq.get("id")
    
    # 以前通知したIDと同じなら通知しない
    try:
        last_id = storage.getItem("last_notified_id")
        if last_id is not None and str(last_id) == str(eq_id):
            return
    except:
        pass 
    
    ui = UI_DICT[current_lang]
    earth = latest_eq.get("earthquake", {})
    hypo = earth.get("hypocenter", {})
    max_scale = earth.get("maxScale", 0)
    
    # 震源地名を翻訳して取得
    translated_hypo = translate_place(hypo.get("name", "不明"))
    scale_text = scale_to_text(max_scale)
    
    title = f"{ui['new_eq']}: {translated_hypo}"
    body = f"{ui['max_scale']}: {scale_text}"
    
    # 通知の実行
    if hasattr(window, "Notification") and window.Notification.permission == "granted":
        window.Notification.new(title, {"body": body})

    # 通知済みIDを保存
    storage.setItem("last_notified_id", str(eq_id))


# --- API取得関数 ---
def fetch_api(limit, trigger_id="get_btn"):
    global real_eq_data, real_tsunami_data, current_display_limit
    
    # ボタン押下時は表示件数をリセットしない等の制御
    if trigger_id == "get_btn": 
        limit = current_display_limit
    else: 
        current_display_limit = limit

    # ロード中表示
    if trigger_id in document:
        document[trigger_id].text = UI_DICT[current_lang]["loading"]
        document[trigger_id].disabled = True

    def on_error(err):
        print(f"API Fetch Error: {err}")
        if trigger_id in document:
            document[trigger_id].disabled = False
            document[trigger_id].text = "Error (Retry)"

    # 地震情報の処理
    def on_eq_loaded(text):
        global real_eq_data
        try:
            if text:
                raw_json = json.loads(text)
                if isinstance(raw_json, list):
                    # 震度情報の無いデータを除外
                    valid_data = [
                        eq for eq in raw_json 
                        if eq.get("earthquake") and 
                           eq["earthquake"].get("maxScale", 0) > 0
                    ]
                    real_eq_data = valid_data[:limit]
                    
                    # ★ここで通知チェックを実行
                    check_notification(real_eq_data)
                    
                    # 画面描画
                    refresh_view()
        except Exception as e:
            print(f"JSON Parse Error: {e}")
        finally:
            if trigger_id in document:
                label_key = "refresh" if trigger_id == "get_btn" else "more"
                document[trigger_id].text = UI_DICT[current_lang][label_key]
                document[trigger_id].disabled = False

    # 津波情報の処理
    def on_tsunami_loaded(text):
        global real_tsunami_data
        try:
            data = json.loads(text)
            # 津波予報区が含まれているか確認
            real_tsunami_data = data[0]["areas"] if data and len(data) > 0 and "areas" in data[0] else []
        except: 
            real_tsunami_data = []
        
        # 津波取得完了後に地震情報を取得（連鎖）
        # limit+20 はフィルタリングで減る分を見越して多めに取得
        window.fetch(f"https://api.p2pquake.net/v2/history?codes=551&limit={limit+20}").then(lambda r: r.text()).then(on_eq_loaded).catch(on_error)

    # 処理開始：まずは津波情報(code=552)から
    window.fetch("https://api.p2pquake.net/v2/history?codes=552&limit=1").then(lambda r: r.text()).then(on_tsunami_loaded).catch(on_error)


# --- 自動更新処理 ---
def auto_refresh():
    # 自動更新時はボタンIDを識別用に渡す
    fetch_api(current_display_limit, "auto_poll")
    # 次回のタイマーセット（60秒後）
    timer.set_timeout(auto_refresh, 60000)

# --- 地域追加などのUI操作 ---
def add_region_action(ev=None):
    global is_debug_mode, debug_eq_data, debug_tsunami_data, saved_regions
    p, c = document["pref_select"].value, document["my_region"].value.strip()

    # デバッグ: 通知テスト
    if c == "debugnotify":
        test_data = [{"id": "dbg_n_" + str(window.Date.new().getTime()),"earthquake": {"time": "2026-01-01T00:00:00+09:00","maxScale": 70,"hypocenter": {"name": "石川県能登地方", "magnitude": 7.6}}}]
        check_notification(test_data)
        window.alert("通知テストを実行しました。")
        document["my_region"].value = ""
        return

    # デバッグ: 全画面表示テスト
    if c == "all5m":
        is_debug_mode = True
        debug_eq_data = [{"id": "dbg_5m","earthquake": {"time": "2026-01-01T00:00:00+09:00","maxScale": 70,"hypocenter": {"name": "全国"}},"points": [{"pref": "全国", "addr": "全域", "scale": 70}]}]
        debug_tsunami_data = []
        for area in tsunami_areas:
            debug_tsunami_data.append({"grade": "majorWarning","name": area,"firstHeight": {"arrivalTime": "直ちに到達"},"maxHeight": {"description": "5m"}})
        refresh_view()
        return

    target = (p + c) if (p and c) else (p or c)
    if target and target not in saved_regions:
        saved_regions.append(target)
        storage.setItem("my_earthquake_regions", json.dumps(saved_regions))
        render_region_list()
        refresh_view()
    document["my_region"].value = ""

# --- 以下、既存のUIヘルパー関数 ---

def translate_select_box():
    if "pref_select" not in document: return
    ui = UI_DICT[current_lang]
    options = document["pref_select"].options
    for opt in options:
        val = opt.value
        if val == "": opt.text = ui.get("pref_op", "Select")
        else: opt.text = translate_place(val)

def update_notify_button():
    if "notify_btn" not in document: return
    ui = UI_DICT[current_lang]
    
    if hasattr(window, "Notification"):
        perm = window.Notification.permission
        btn = document["notify_btn"]
        
        if perm == "granted":
            # 許可済みの場合：ボタンを無効化し「許可されました」と表示
            btn.text = ui.get("noti_granted", "Notifications enabled!")
            btn.disabled = True
            btn.style.opacity = "0.6"
            btn.style.cursor = "default"
        elif perm == "denied":
            # 拒否されている場合
            btn.text = ui.get("noti_denied", "Notifications denied.")
            btn.disabled = True
            btn.style.opacity = "0.6"
        else:
            # 未設定（default）の場合：ボタンを有効化
            btn.text = ui.get("noti_on", "Enable Notifications")
            btn.disabled = False
            btn.style.opacity = "1.0"
            btn.style.cursor = "pointer"

def change_language_simple(ev):
    global current_lang
    current_lang = document["lang_select"].value
    ui = UI_DICT[current_lang]
    
    if "label_myregion" in document: document["label_myregion"].text = ui.get("region_h3", "")
    if "set_reg_btn" in document: document["set_reg_btn"].text = ui.get("add", "")
    if "get_btn" in document: document["get_btn"].text = ui.get("refresh", "")
    if "more_btn" in document: document["more_btn"].text = ui.get("more", "")
    
    # 修正: 単純なテキスト代入ではなく、状態判定関数を呼ぶ
    update_notify_button()
    
    translate_select_box()
    render_region_list()
    refresh_view()

def render_region_list():
    if "region_list" not in document: return
    container = document["region_list"]
    container.innerHTML = ""
    for r in saved_regions:
        display_name = translate_place(r)
        span = html.SPAN(style={'background':'#007bff', 'color': 'white','padding':'5px 12px','borderRadius':'20px','fontSize':'0.9em','display':'flex','alignItems':'center','marginBottom': '5px'})
        span <= html.SPAN(display_name)
        close = html.SPAN("×", style={'marginLeft':'8px','cursor':'pointer','fontWeight':'bold','color':'#fff','opacity': '0.8'})
        close.setAttribute("data-val", r)
        close.bind("click", remove_region)
        span <= close
        container <= span

def bind_events():
    global is_initial_loaded
    if is_initial_loaded: return
    if "lang_select" in document: document["lang_select"].bind("change", change_language_simple)
    if "set_reg_btn" in document: document["set_reg_btn"].bind("click", add_region_action)
    if "get_btn" in document: document["get_btn"].bind("click", lambda e: fetch_api(10, "get_btn"))
    if "more_btn" in document: document["more_btn"].bind("click", lambda e: fetch_api(current_display_limit + 10, "more_btn"))
    if "close_btn" in document: document["close_btn"].bind("click", lambda e: setattr(document["content_detail"].style, "display", "none"))
    if "notify_btn" in document: document["notify_btn"].bind("click", setup_notification_with_translation)

    is_initial_loaded = True
    update_notify_button()
    
    # 初回データ取得
    fetch_api(10)
    
    # ★自動更新タイマーを開始（コメントアウト解除）
    timer.set_timeout(auto_refresh, 60000)

def setup():
    global saved_regions
    try:
        raw = storage.getItem("my_earthquake_regions")
        if raw: saved_regions = json.loads(raw); render_region_list()
    except: pass
    timer.set_timeout(bind_events, 500)

setup()