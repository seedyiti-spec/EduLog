import html as _html
import json
import os
import re
import tempfile
import time
import uuid
from datetime import date, datetime

from google import genai
from google.genai import types
import streamlit as st
from notion_client import Client as NotionClient

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="EduLog",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS — Magazine B style ─────────────────────────────────────────────
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,300;1,9..40,400&family=DM+Serif+Display:ital@0;1&display=swap" rel="stylesheet">

<style>
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: #1A1A1A;
}
.stApp { background-color: #FAF9F6; }

#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding-top: 3rem;
    padding-bottom: 4rem;
    max-width: 1100px;
}

[data-testid="stSidebar"] {
    background-color: #F2F0EB;
    border-right: 1px solid #E0DDD6;
}
[data-testid="stSidebar"] * {
    font-family: 'DM Sans', sans-serif;
    color: #1A1A1A;
}

.stButton > button {
    background-color: transparent !important;
    color: #1A1A1A !important;
    border: 1px solid #1A1A1A !important;
    border-radius: 0px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    padding: 0.45rem 1.2rem !important;
    transition: background-color 0.15s ease, color 0.15s ease !important;
}
.stButton > button:hover {
    background-color: #1A1A1A !important;
    color: #FAF9F6 !important;
}
.stButton > button[kind="primary"] {
    background-color: #1A1A1A !important;
    color: #FAF9F6 !important;
}
.stButton > button[kind="primary"]:hover { background-color: #3d3d3d !important; }
.stButton > button:disabled {
    border-color: #C8C5BE !important;
    color: #C8C5BE !important;
}

.stFormSubmitButton > button {
    background-color: transparent !important;
    color: #1A1A1A !important;
    border: 1px solid #1A1A1A !important;
    border-radius: 0px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    padding: 0.45rem 1.2rem !important;
    transition: background-color 0.15s ease, color 0.15s ease !important;
}
.stFormSubmitButton > button:hover {
    background-color: #1A1A1A !important;
    color: #FAF9F6 !important;
}

.stTextInput > div > div > input,
.stSelectbox > div > div,
.stDateInput > div > div > input {
    background-color: #FAF9F6 !important;
    border: 1px solid #D0CCC4 !important;
    border-radius: 0px !important;
    font-family: 'DM Sans', sans-serif !important;
    color: #1A1A1A !important;
}
.stTextInput > div > div > input:focus {
    border-color: #1A1A1A !important;
    box-shadow: none !important;
}
[data-baseweb="select"] > div {
    border-radius: 0px !important;
    border-color: #D0CCC4 !important;
    background-color: #FAF9F6 !important;
}

[data-testid="stFileUploader"] {
    border: 1px dashed #C0BCB4 !important;
    border-radius: 0px !important;
    background: #F5F3EE !important;
    padding: 1rem !important;
}

.stTabs [data-baseweb="tab-list"] {
    background: transparent;
    border-bottom: 1px solid #1A1A1A;
    gap: 0;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    border: none;
    border-bottom: 2px solid transparent;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.78rem;
    font-weight: 500;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: #888 !important;
    padding: 0.6rem 1.4rem;
    margin-bottom: -1px;
}
.stTabs [aria-selected="true"] {
    color: #1A1A1A !important;
    border-bottom: 2px solid #1A1A1A !important;
    background: transparent !important;
}

[data-testid="stExpander"] {
    border: 1px solid #E0DDD6 !important;
    border-radius: 0px !important;
    background: #FAF9F6 !important;
}
[data-testid="stExpander"] summary {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.85rem;
    font-weight: 500;
    letter-spacing: 0.03em;
    color: #1A1A1A;
}

hr { border-color: #E0DDD6 !important; margin: 2rem 0 !important; }

.stAlert {
    border-radius: 0px !important;
    border-left-width: 3px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.85rem !important;
}
.stSpinner > div { border-top-color: #1A1A1A !important; }

.stTextArea > div > div > textarea {
    background-color: #F5F3EE !important;
    border: 1px solid #D0CCC4 !important;
    border-radius: 0px !important;
    font-family: 'DM Sans', sans-serif !important;
    color: #1A1A1A !important;
    font-size: 0.88rem !important;
    font-weight: 300 !important;
    line-height: 1.8 !important;
    resize: vertical !important;
}
.stTextArea > div > div > textarea:focus {
    border-color: #1A1A1A !important;
    box-shadow: none !important;
}
.stTextArea > div > div > textarea::placeholder {
    color: #AAAAAA !important;
    font-style: italic !important;
}
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
DATA_DIR = "data"
CLASSES_FILE = os.path.join(DATA_DIR, "classes.json")

GEMINI_MODEL = "gemini-2.5-flash"

MIME_MAP = {
    ".mp3": "audio/mpeg", ".mp4": "audio/mp4", ".m4a": "audio/mp4",
    ".wav": "audio/wav", ".webm": "audio/webm", ".ogg": "audio/ogg",
    ".flac": "audio/flac", ".aac": "audio/aac",
}


# ── Key access via st.secrets ─────────────────────────────────────────────────
def get_keys() -> dict:
    return {
        "GEMINI_API_KEY":    st.secrets.get("GEMINI_API_KEY", ""),
        "NOTION_TOKEN":      st.secrets.get("NOTION_TOKEN", ""),
        "NOTION_DATABASE_ID": st.secrets.get("NOTION_DATABASE_ID", ""),
    }


# ── Session state initialisation ──────────────────────────────────────────────
def _init_session_state():
    if "classes" not in st.session_state:
        try:
            if os.path.exists(CLASSES_FILE):
                with open(CLASSES_FILE, "r", encoding="utf-8") as f:
                    st.session_state.classes = json.load(f)
            else:
                st.session_state.classes = {}
        except Exception:
            st.session_state.classes = {}

    if "class_data" not in st.session_state:
        st.session_state.class_data = {}

    if "current_class" not in st.session_state:
        st.session_state.current_class = None


# ── Data helpers (session_state-backed, file I/O as best-effort) ──────────────
def load_classes() -> dict:
    return st.session_state.get("classes", {})


def save_classes(classes: dict):
    st.session_state.classes = classes
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(CLASSES_FILE, "w", encoding="utf-8") as f:
            json.dump(classes, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def class_data_path(class_id: str) -> str:
    return os.path.join(DATA_DIR, f"class_{class_id}.json")


def load_class_data(class_id: str) -> dict:
    class_data_store = st.session_state.get("class_data", {})
    if class_id in class_data_store:
        return class_data_store[class_id]
    # Fallback: read from file (local dev or initial cloud load)
    try:
        path = class_data_path(class_id)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            st.session_state.class_data[class_id] = data
            return data
    except Exception:
        pass
    default = {"children": [], "journals": []}
    st.session_state.class_data[class_id] = default
    return default


def save_class_data(class_id: str, data: dict):
    if "class_data" not in st.session_state:
        st.session_state.class_data = {}
    st.session_state.class_data[class_id] = data
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(class_data_path(class_id), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


# ── Sidebar ───────────────────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="padding:1.5rem 0 0.5rem 0;">
            <div style="font-size:0.65rem; font-weight:600; letter-spacing:0.18em;
                        text-transform:uppercase; color:#888; margin-bottom:0.4rem;">System</div>
            <div style="font-family:'DM Serif Display',serif; font-size:1.6rem;
                        font-weight:400; color:#1A1A1A; line-height:1.1;">EduLog</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<hr style='margin:1rem 0; border-color:#C8C5BE;'>", unsafe_allow_html=True)

        # Connection status dots
        keys = get_keys()
        statuses = [
            ("Gemini",  bool(keys["GEMINI_API_KEY"])),
            ("Notion",  bool(keys["NOTION_TOKEN"] and keys["NOTION_DATABASE_ID"])),
        ]
        for name, ok in statuses:
            dot   = "#2D6A4F" if ok else "#C8C5BE"
            color = "#1A1A1A" if ok else "#999"
            st.markdown(f"""
            <div style="display:flex; align-items:center; gap:0.5rem;
                        margin-bottom:0.35rem; font-size:0.75rem; color:{color};">
                <div style="width:6px; height:6px; border-radius:50%;
                            background:{dot}; flex-shrink:0;"></div>
                {name}
            </div>""", unsafe_allow_html=True)


# ── Gemini: speaker diarisation + class-wide analysis ─────────────────────────
def _build_class_prompt(class_name: str, obs_date: str, num_students: int) -> str:
    letters = [chr(ord('A') + i) for i in range(num_students)]
    labels = [f"학생 {l}" for l in letters]
    last_letter = letters[-1]
    label_list = ", ".join(f"'{lb}'" for lb in labels)

    first_entry = (
        f'  {{\n    "speaker": "{labels[0]}",\n'
        f'    "key_observations": "주요 발화 및 관찰 내용",\n'
        f'    "writing_summary": "아이가 쓴 글의 내용 요약",\n'
        f'    "teacher_feedback": "선생님의 피드백 내용"\n  }}'
    )
    other_entries = [
        f'  {{\n    "speaker": "{lb}",\n'
        f'    "key_observations": "...",\n'
        f'    "writing_summary": "...",\n'
        f'    "teacher_feedback": "..."\n  }}'
        for lb in labels[1:]
    ]
    json_template = "[\n" + ",\n".join([first_entry] + other_entries) + "\n]"

    return (
        f"당신은 어린이 글쓰기 수업 전문 관찰 일지 작성 AI입니다.\n"
        f"첨부된 음성 파일은 '{class_name}' 수업의 {obs_date} 녹음입니다.\n\n"
        f"⚠️ 중요: 이 녹음본에는 교사(디렉터) 1명과 정확히 {num_students}명의 학생만 등장합니다. "
        f"배경 소음이나 톤 변화에 속지 말고, 학생을 정확히 '학생 A'부터 '학생 {last_letter}'까지만 "
        f"엄격하게 분류하여 JSON으로 반환하세요.\n\n"
        f"임무:\n"
        f"1. 목소리 특성(음색, 억양, 말투, 어휘 등)에 근거하여 {num_students}명의 학생을 {label_list}로 엄격히 분리하세요.\n"
        f"   - 반드시 정확히 {num_students}명만 구분하세요. 더 많거나 더 적게 분리하지 마세요.\n"
        f"   - 디렉터(교사)의 목소리는 별도로 인식하되, 결과 JSON에는 포함하지 마세요.\n"
        f"2. 각 학생별로 아래 3가지 항목의 관찰 일지를 작성하세요.\n"
        f"   각 항목은 핵심만 간결하게 요약하세요. 불필요한 수식이나 반복 없이 정갈하게 서술하세요.\n\n"
        f"항목 설명:\n"
        f"- key_observations: 아이의 목소리와 맥락 추적. 수업 중 아이가 한 핵심 발화를 직접 인용하고, 대화 흐름과 반응 맥락을 서술하세요.\n"
        f"- writing_summary: 아이가 발표하거나 대화 중에 언급한 자신의 글의 핵심 내용을 요약하세요. 글의 소재, 전개, 표현의 특징을 포함하세요.\n"
        f"- teacher_feedback: 디렉터(교사)가 해당 학생의 글에 대해 건넨 코멘트나 조언을 정확히 추출하세요. 디렉터의 발화에서만 가져오세요.\n"
        f"  ⚠️ 수업 초반의 결과물 피드백뿐만 아니라, 수업 중후반부에 아이들이 자신의 글을 읽고 난 직후에 디렉터(교사)가 건네는 피드백과 조언을 절대 누락하지 마세요.\n"
        f"  ⚠️ 90분 전체의 오디오 타임라인을 끝까지 집중해서 추적하고, 초반-중반-후반에 등장하는 모든 피드백을 시간 흐름에 따라 빠짐없이 기록하세요.\n\n"
        f"반드시 아래 JSON 배열 형식으로만 응답하세요. 다른 텍스트는 절대 포함하지 마세요.\n"
        f"배열 내 항목 수는 정확히 {num_students}개여야 합니다.\n\n"
        f"{json_template}"
    )


def analyze_class_with_gemini(
    audio_file, api_key: str, class_name: str, obs_date: str, num_students: int = 4
) -> list:
    client = genai.Client(api_key=api_key)

    suffix = os.path.splitext(audio_file.name)[-1].lower() or ".m4a"
    mime_type = MIME_MAP.get(suffix, "audio/mpeg")

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(audio_file.read())
        tmp_path = tmp.name

    uploaded = None
    try:
        uploaded = client.files.upload(
            file=tmp_path,
            config=types.UploadFileConfig(mime_type=mime_type),
        )

        max_wait_sec = 600
        waited = 0
        while uploaded.state.name not in ("ACTIVE", "FAILED"):
            time.sleep(5)
            waited += 5
            if waited >= max_wait_sec:
                raise TimeoutError(
                    f"파일 처리 대기 시간이 초과되었습니다 ({max_wait_sec}초). "
                    "파일 크기를 줄이거나 잠시 후 다시 시도해 주세요."
                )
            uploaded = client.files.get(name=uploaded.name)

        if uploaded.state.name == "FAILED":
            raise ValueError(f"Gemini 파일 처리 실패 (state={uploaded.state.name})")

        prompt = _build_class_prompt(class_name, obs_date, num_students)
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[uploaded, prompt],
            config=types.GenerateContentConfig(response_mime_type="application/json"),
        )
        text = response.text
        m = re.search(r"\[.*\]", text, re.DOTALL)
        return json.loads(m.group() if m else text)

    finally:
        os.unlink(tmp_path)
        if uploaded:
            try:
                client.files.delete(name=uploaded.name)
            except Exception:
                pass


# ── Notion integration ────────────────────────────────────────────────────────
def _rt(text: str) -> list:
    return [{"text": {"content": text[i: i + 1999]}} for i in range(0, max(len(text), 1), 1999)]


def send_to_notion(journal: dict, token: str, database_id: str, class_name_override: str = ""):
    nc = NotionClient(auth=token)
    a = journal["analysis"]
    director_memo = journal.get("director_realtime_memo", "")

    # 5단계 폴백: 인자 → journal dict → current_class → nav_class_name → classes 조회
    resolved_class = (
        class_name_override.strip()
        or journal.get("class_name", "").strip()
        or (st.session_state.get("current_class") or {}).get("name", "").strip()
        or st.session_state.get("nav_class_name", "").strip()
        or load_classes().get(journal.get("class_id", ""), {}).get("name", "").strip()
        or "미분류"
    )

    properties = {
        "이름": {"title": _rt(journal["child_name"])},
        "날짜": {"date": {"start": journal["date"]}},
        "클래스": {"select": {"name": resolved_class}},
        "주요 발화 및 관찰 내용": {"rich_text": _rt(a.get("key_observations", ""))},
        "아이가 쓴 글의 내용 요약": {"rich_text": _rt(a.get("writing_summary", ""))},
        "선생님의 피드백 내용": {"rich_text": _rt(a.get("teacher_feedback", ""))},
        "디렉터 메모": {"rich_text": _rt(director_memo)},
    }
    transcript = journal.get("transcript", "")
    blocks = [{"object": "block", "type": "heading_2",
               "heading_2": {"rich_text": [{"text": {"content": "녹음 전사 내용"}}]}}]
    for i in range(0, len(transcript), 1999):
        blocks.append({"object": "block", "type": "paragraph",
                       "paragraph": {"rich_text": [{"text": {"content": transcript[i: i + 1999]}}]}})
    nc.pages.create(parent={"database_id": database_id}, properties=properties, children=blocks)


# ── Typography helpers ────────────────────────────────────────────────────────
def mag_label(text: str):
    st.markdown(f"""
    <div style="font-size:0.62rem; font-weight:600; letter-spacing:0.18em;
                text-transform:uppercase; color:#888; margin-bottom:0.3rem;">
        {text}
    </div>""", unsafe_allow_html=True)


def mag_section_title(text: str):
    st.markdown(f"""
    <div style="font-size:0.62rem; font-weight:600; letter-spacing:0.18em;
                text-transform:uppercase; color:#888; margin:2.5rem 0 1rem 0;
                padding-bottom:0.5rem; border-bottom:1px solid #E0DDD6;">
        {text}
    </div>""", unsafe_allow_html=True)


def mag_analysis_block(index: int, label: str, content: str):
    st.markdown(f"""
    <div style="padding:1.8rem 0; border-bottom:1px solid #E8E5DF;">
        <div style="display:flex; align-items:baseline; gap:1rem; margin-bottom:0.8rem;">
            <span style="font-size:0.6rem; font-weight:600; letter-spacing:0.2em;
                         text-transform:uppercase; color:#AAAAAA; min-width:1.2rem;">0{index}</span>
            <span style="font-size:0.72rem; font-weight:600; letter-spacing:0.12em;
                         text-transform:uppercase; color:#555;">{label}</span>
        </div>
        <div style="font-size:0.95rem; font-weight:300; line-height:1.9;
                    color:#1A1A1A; padding-left:2.2rem;">{content}</div>
    </div>
    """, unsafe_allow_html=True)


_ANALYSIS_FIELDS = [
    ("주요 발화 및 관찰 내용",  "key_observations"),
    ("아이가 쓴 글의 내용 요약", "writing_summary"),
    ("선생님의 피드백 내용",    "teacher_feedback"),
]


def render_analysis_card(analysis: dict):
    for i, (label, key) in enumerate(_ANALYSIS_FIELDS, 1):
        mag_analysis_block(i, label, analysis.get(key, "—"))


# ── Tab 1: Upload & Analysis ──────────────────────────────────────────────────
def render_upload_tab(class_id: str, class_name: str, keys: dict):
    mag_section_title("Record & Analyse")

    cdata = load_class_data(class_id)
    children = cdata.get("children", [])
    child_options = ["미지정"] + [c["name"] for c in children]

    col1, col2 = st.columns(2)
    with col1:
        mag_label("수업 날짜")
        obs_date = st.date_input("수업 날짜", value=date.today(), label_visibility="collapsed")
    with col2:
        mag_label("참여 학생 수")
        num_students = st.number_input(
            "참여 학생 수",
            min_value=1, max_value=10, value=4, step=1,
            label_visibility="collapsed",
            help="실제 수업에 참여한 학생 수를 입력하세요 (1~10명). AI가 이 숫자에 맞게 화자를 분리합니다.",
        )

    st.markdown("<div style='margin-top:1.5rem;'>", unsafe_allow_html=True)
    mag_label("음성 파일 업로드 — mp3 / m4a / wav / mp4 / webm / ogg / flac")
    audio_file = st.file_uploader(
        "음성 파일", type=["mp3", "m4a", "wav", "mp4", "webm", "ogg", "flac", "aac"],
        label_visibility="collapsed",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    if audio_file:
        st.audio(audio_file)
        st.markdown("<div style='margin-top:1rem;'>", unsafe_allow_html=True)
        if st.button("Analyse →", type="primary"):
            if not keys["GEMINI_API_KEY"]:
                st.error("Streamlit Secrets에 GEMINI_API_KEY가 설정되지 않았습니다.")
            else:
                with st.status("Gemini 분석 중…", expanded=True) as status:
                    try:
                        st.write("— 음성 파일을 Gemini에 업로드 중")
                        audio_file.seek(0)
                        st.write("— 화자 분리 및 관찰 일지 생성 중 (파일 크기에 따라 수 분 소요될 수 있습니다)")
                        speakers = analyze_class_with_gemini(
                            audio_file, keys["GEMINI_API_KEY"],
                            class_name, str(obs_date),
                            int(num_students),
                        )
                        status.update(label="완료", state="complete")
                        st.session_state["_class_result"] = {
                            "speakers": speakers,
                            "class_id": class_id,
                            "class_name": class_name,
                            "date": str(obs_date),
                        }
                    except Exception as exc:
                        status.update(label="오류", state="error")
                        st.error(f"오류 상세 내용: {exc}")
        st.markdown("</div>", unsafe_allow_html=True)

    result = st.session_state.get("_class_result")
    if not (result and result.get("class_id") == class_id):
        return

    speakers = result["speakers"]

    st.markdown(f"""
    <div style="margin-top:3rem; padding-top:2rem; border-top:2px solid #1A1A1A;">
        <div style="font-size:0.62rem; font-weight:600; letter-spacing:0.18em;
                    text-transform:uppercase; color:#888; margin-bottom:0.6rem;">
            Speaker Diarisation Result
        </div>
        <div style="display:flex; align-items:baseline; gap:1.5rem;">
            <span style="font-family:'DM Serif Display',serif; font-size:2rem;
                         font-weight:400; color:#1A1A1A;">{len(speakers)}명 분리 완료</span>
            <span style="font-size:0.85rem; color:#888; font-weight:300;">{result['date']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Name mapping ─────────────────────────────────────────────────────────
    mag_section_title("화자 매핑 — 학생 이름 지정")
    st.markdown("""
    <div style="font-size:0.82rem; color:#888; font-weight:300; margin-bottom:1.5rem; line-height:1.7;">
        Gemini가 목소리 특성으로 구분한 학생 A–F에 실제 이름을 지정하세요.<br>
        '미지정' 항목은 저장에서 제외됩니다.
    </div>
    """, unsafe_allow_html=True)

    map_cols = st.columns(3)
    for i, sp in enumerate(speakers):
        label = sp["speaker"]
        map_key = f"_map_{class_id}_{label.replace(' ', '_')}"
        with map_cols[i % 3]:
            mag_label(label)
            st.selectbox(label, child_options, key=map_key, label_visibility="collapsed")

    # ── Analysis cards ────────────────────────────────────────────────────────
    mag_section_title("분석 결과")
    for sp in speakers:
        label = sp["speaker"]
        map_key = f"_map_{class_id}_{label.replace(' ', '_')}"
        mapped = st.session_state.get(map_key, "미지정")
        display = f"{label}  ·  {mapped}" if mapped != "미지정" else label
        analysis = {k: v for k, v in sp.items() if k != "speaker"}
        memo_key = f"_memo_{class_id}_{label.replace(' ', '_')}"
        with st.expander(display):
            render_analysis_card(analysis)
            st.markdown("""
            <div style="border-top:1px solid #E8E5DF; margin-top:0.5rem; padding-top:1.6rem;
                        padding-bottom:0.4rem;">
                <div style="font-size:0.62rem; font-weight:600; letter-spacing:0.18em;
                            text-transform:uppercase; color:#888; margin-bottom:0.5rem;">
                    디렉터 실시간 메모
                </div>
                <div style="font-size:0.78rem; font-weight:300; color:#AAA; margin-bottom:0.8rem;
                            line-height:1.6;">
                    수업 직후 느낀 점, 다음 수업 아이디어, 특별히 기억해 둘 관찰 내용을 자유롭게 기록하세요.
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.text_area(
                "디렉터 실시간 메모",
                placeholder="예) 오늘 유독 집중력이 좋았고, '사과가 빨간 건 부끄러워서'라는 표현이 인상적이었음. 다음 시간에 색깔의 감정 연결하는 활동 제안해볼 것.",
                key=memo_key,
                label_visibility="collapsed",
                height=130,
            )

    # ── Batch save / send ─────────────────────────────────────────────────────
    st.markdown("<div style='margin-top:2rem;'>", unsafe_allow_html=True)
    notion_ready = bool(keys["NOTION_TOKEN"] and keys["NOTION_DATABASE_ID"])
    sc1, sc2 = st.columns(2)

    if sc1.button("일괄 저장", use_container_width=True):
        cdata_fresh = load_class_data(class_id)
        saved = []
        for sp in speakers:
            label = sp["speaker"]
            map_key = f"_map_{class_id}_{label.replace(' ', '_')}"
            child_name = st.session_state.get(map_key, "미지정")
            if child_name == "미지정":
                continue
            analysis = {k: v for k, v in sp.items() if k != "speaker"}
            memo_key = f"_memo_{class_id}_{label.replace(' ', '_')}"
            director_memo = st.session_state.get(memo_key, "")
            journal = {
                "id": str(uuid.uuid4()),
                "child_name": child_name,
                "class_id": class_id,
                "class_name": class_name,
                "date": result["date"],
                "transcript": "",
                "analysis": analysis,
                "director_realtime_memo": director_memo,
                "created_at": datetime.now().isoformat(),
                "sent_to_notion": False,
            }
            cdata_fresh["journals"].append(journal)
            saved.append(child_name)
        if saved:
            save_class_data(class_id, cdata_fresh)
            st.success(f"저장 완료: {', '.join(saved)}")
        else:
            st.warning("저장할 항목이 없습니다. 이름을 지정해 주세요.")

    if sc2.button(
        "Notion 일괄 전송", use_container_width=True, disabled=not notion_ready,
        help="Streamlit Secrets에 NOTION_TOKEN / NOTION_DATABASE_ID를 설정해 주세요." if not notion_ready else "",
    ):
        # class_name 강제 확정 — 함수 파라미터가 1순위, 세션/조회가 폴백
        active_class_name = (
            class_name.strip()
            or (st.session_state.get("current_class") or {}).get("name", "").strip()
            or st.session_state.get("nav_class_name", "").strip()
            or load_classes().get(class_id, {}).get("name", "").strip()
            or "미분류"
        )

        cdata_fresh = load_class_data(class_id)
        sent = []
        errors = []
        for sp in speakers:
            label = sp["speaker"]
            map_key = f"_map_{class_id}_{label.replace(' ', '_')}"
            child_name = st.session_state.get(map_key, "미지정")
            if child_name == "미지정":
                continue
            analysis = {k: v for k, v in sp.items() if k != "speaker"}
            memo_key = f"_memo_{class_id}_{label.replace(' ', '_')}"
            director_memo = st.session_state.get(memo_key, "")
            journal = {
                "id": str(uuid.uuid4()),
                "child_name": child_name,
                "class_id": class_id,
                "class_name": active_class_name,
                "date": result["date"],
                "transcript": "",
                "analysis": analysis,
                "director_realtime_memo": director_memo,
                "created_at": datetime.now().isoformat(),
                "sent_to_notion": True,
            }
            try:
                with st.spinner(f"{child_name} 전송 중…"):
                    send_to_notion(
                        journal,
                        keys["NOTION_TOKEN"],
                        keys["NOTION_DATABASE_ID"],
                        class_name_override=active_class_name,
                    )
                cdata_fresh["journals"].append(journal)
                sent.append(child_name)
            except Exception as exc:
                errors.append(f"{child_name}: {exc}")
        if sent:
            save_class_data(class_id, cdata_fresh)
            st.success(f"Notion 전송 완료: {', '.join(sent)}")
        for e in errors:
            st.error(e)
        if not sent and not errors:
            st.warning("전송할 항목이 없습니다. 이름을 지정해 주세요.")
    st.markdown("</div>", unsafe_allow_html=True)


# ── Tab 2: Child Management ───────────────────────────────────────────────────
def render_children_tab(class_id: str):
    mag_section_title("Children")

    with st.form("form_add_child", clear_on_submit=True):
        ci1, ci2 = st.columns([4, 1])
        mag_label("이름")
        new_name = ci1.text_input("이름", placeholder="홍길동", label_visibility="collapsed")
        ci2.markdown("<div style='margin-top:1.45rem;'>", unsafe_allow_html=True)
        submitted = ci2.form_submit_button("추가", use_container_width=True)
        ci2.markdown("</div>", unsafe_allow_html=True)
        if submitted:
            name = new_name.strip()
            if not name:
                st.error("이름을 입력해 주세요.")
            else:
                cdata = load_class_data(class_id)
                if name in {c["name"] for c in cdata["children"]}:
                    st.error("이미 등록된 이름입니다.")
                else:
                    cdata["children"].append({
                        "id": str(uuid.uuid4()),
                        "name": name,
                        "added_at": datetime.now().isoformat(),
                    })
                    save_class_data(class_id, cdata)
                    st.rerun()

    cdata = load_class_data(class_id)
    children = cdata.get("children", [])

    if not children:
        st.markdown("""
        <div style="padding:2rem; border:1px dashed #C8C5BE; text-align:center;
                    font-size:0.85rem; color:#888;">
            등록된 아이가 없습니다.
        </div>""", unsafe_allow_html=True)
        return

    st.markdown(f"""
    <div style="font-size:0.72rem; color:#888; letter-spacing:0.06em; margin:1.5rem 0 1rem 0;">
        총 {len(children)}명 등록됨
    </div>""", unsafe_allow_html=True)

    for child in children:
        cc1, cc2 = st.columns([5, 1])
        cc1.markdown(f"""
        <div style="padding:0.8rem 0; border-bottom:1px solid #F0EDE8;">
            <span style="font-size:0.95rem; font-weight:500; color:#1A1A1A;">{child['name']}</span>
            <span style="font-size:0.72rem; color:#AAA; margin-left:1rem;">{child['added_at'][:10]}</span>
        </div>""", unsafe_allow_html=True)
        if cc2.button("삭제", key=f"del_ch_{child['id']}", use_container_width=True):
            st.session_state["_confirm_del_child"] = child["id"]

        if st.session_state.get("_confirm_del_child") == child["id"]:
            st.warning(f"'{child['name']}' 아이를 삭제하시겠습니까?")
            dc1, dc2 = st.columns(2)
            if dc1.button("삭제 확인", key=f"conf_dc_{child['id']}"):
                cdata = load_class_data(class_id)
                cdata["children"] = [c for c in cdata["children"] if c["id"] != child["id"]]
                save_class_data(class_id, cdata)
                st.session_state.pop("_confirm_del_child", None)
                st.rerun()
            if dc2.button("취소", key=f"canc_dc_{child['id']}"):
                st.session_state.pop("_confirm_del_child", None)
                st.rerun()


# ── Tab 3: Journal List ───────────────────────────────────────────────────────
def render_journals_tab(class_id: str, keys: dict):
    mag_section_title("Journal Archive")

    cdata = load_class_data(class_id)
    journals = cdata.get("journals", [])

    if not journals:
        st.markdown("""
        <div style="padding:2rem; border:1px dashed #C8C5BE; text-align:center;
                    font-size:0.85rem; color:#888;">
            저장된 관찰 일지가 없습니다.
        </div>""", unsafe_allow_html=True)
        return

    child_names = sorted({j["child_name"] for j in journals})
    fc1, fc2 = st.columns(2)
    with fc1:
        mag_label("아이 필터")
        filter_child = st.selectbox("아이 필터", ["전체"] + child_names, label_visibility="collapsed")
    with fc2:
        mag_label("전송 상태")
        filter_notion = st.selectbox("전송 상태", ["전체", "전송됨", "미전송"], label_visibility="collapsed")

    filtered = journals
    if filter_child != "전체":
        filtered = [j for j in filtered if j["child_name"] == filter_child]
    if filter_notion == "전송됨":
        filtered = [j for j in filtered if j.get("sent_to_notion")]
    elif filter_notion == "미전송":
        filtered = [j for j in filtered if not j.get("sent_to_notion")]
    filtered = sorted(filtered, key=lambda x: x["date"], reverse=True)

    st.markdown(f"""
    <div style="font-size:0.72rem; color:#888; letter-spacing:0.06em; margin:1.5rem 0 1rem 0;">
        {len(filtered)}개 일지
    </div>""", unsafe_allow_html=True)

    notion_ready = bool(keys["NOTION_TOKEN"] and keys["NOTION_DATABASE_ID"])

    for jn in filtered:
        sent = jn.get("sent_to_notion")
        badge_color = "#2D6A4F" if sent else "#BBBBBB"
        badge_text  = "전송됨" if sent else "미전송"

        with st.expander(f"{jn['child_name']}  ·  {jn['date']}"):
            st.markdown(f"""
            <div style="display:inline-block; font-size:0.6rem; font-weight:600;
                        letter-spacing:0.14em; text-transform:uppercase;
                        color:{badge_color}; border:1px solid {badge_color};
                        padding:0.15rem 0.5rem; margin-bottom:1rem;">
                {badge_text}
            </div>""", unsafe_allow_html=True)

            render_analysis_card(jn["analysis"])

            director_memo = jn.get("director_realtime_memo", "")
            if director_memo:
                st.markdown(f"""
                <div style="margin-top:1rem; padding:1.4rem 1.6rem 1.2rem 1.6rem;
                            background:#F5F3EE; border-left:2px solid #1A1A1A;">
                    <div style="font-size:0.62rem; font-weight:600; letter-spacing:0.18em;
                                text-transform:uppercase; color:#888; margin-bottom:0.7rem;">
                        디렉터 실시간 메모
                    </div>
                    <div style="font-size:0.9rem; font-weight:300; line-height:1.9; color:#1A1A1A;
                                white-space:pre-wrap;">{director_memo}</div>
                </div>
                """, unsafe_allow_html=True)

            with st.expander("전사 원문"):
                st.markdown(f"""
                <div style="font-size:0.83rem; font-weight:300; line-height:1.9; color:#555;">
                    {jn.get('transcript', '')}
                </div>""", unsafe_allow_html=True)

            st.markdown("<div style='margin-top:1.5rem;'>", unsafe_allow_html=True)
            jc1, jc2 = st.columns([3, 1])
            if not sent:
                if jc1.button(
                    "Notion으로 전송", key=f"notion_{jn['id']}",
                    disabled=not notion_ready, use_container_width=True,
                ):
                    try:
                        # 저장된 일지의 class_name이 비어 있을 경우를 대비한 강제 폴백
                        effective_class = (
                            jn.get("class_name", "").strip()
                            or (st.session_state.get("current_class") or {}).get("name", "").strip()
                            or st.session_state.get("nav_class_name", "").strip()
                            or load_classes().get(class_id, {}).get("name", "").strip()
                            or "미분류"
                        )
                        with st.spinner("전송 중…"):
                            send_to_notion(
                                jn,
                                keys["NOTION_TOKEN"],
                                keys["NOTION_DATABASE_ID"],
                                class_name_override=effective_class,
                            )
                        for j in cdata["journals"]:
                            if j["id"] == jn["id"]:
                                j["sent_to_notion"] = True
                        save_class_data(class_id, cdata)
                        st.success("전송되었습니다.")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"오류 상세 내용: {exc}")
            else:
                jc1.markdown("""
                <div style="font-size:0.75rem; color:#2D6A4F; padding:0.4rem 0;">
                    ✓ Notion 전송 완료
                </div>""", unsafe_allow_html=True)

            if jc2.button("삭제", key=f"del_jn_{jn['id']}", use_container_width=True):
                cdata["journals"] = [j for j in cdata["journals"] if j["id"] != jn["id"]]
                save_class_data(class_id, cdata)
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)


# ── Home page ─────────────────────────────────────────────────────────────────
def render_home():
    st.markdown("""
    <div style="border-bottom:2px solid #1A1A1A; padding-bottom:1.5rem; margin-bottom:3rem;">
        <div style="font-size:0.62rem; font-weight:600; letter-spacing:0.22em;
                    text-transform:uppercase; color:#888; margin-bottom:0.8rem;">
            Observation Journal System
        </div>
        <div style="font-family:'DM Serif Display',serif; font-size:3.2rem;
                    font-weight:400; color:#1A1A1A; line-height:1.05; letter-spacing:-0.01em;">
            EduLog
        </div>
        <div style="font-size:0.85rem; font-weight:300; color:#777;
                    margin-top:0.6rem; letter-spacing:0.02em;">
            어린이 글쓰기 수업 관찰 일지
        </div>
    </div>
    """, unsafe_allow_html=True)

    classes = load_classes()
    col_h, col_btn = st.columns([4, 1])
    col_h.markdown("""
    <div style="font-size:0.62rem; font-weight:600; letter-spacing:0.18em;
                text-transform:uppercase; color:#888; padding-top:0.4rem;">
        Classes
    </div>""", unsafe_allow_html=True)
    if col_btn.button("+ 새 클래스", use_container_width=True):
        st.session_state["_show_add_class"] = True

    if st.session_state.get("_show_add_class"):
        st.markdown("<div style='margin-top:1.5rem; padding:1.5rem; background:#F2F0EB; border:1px solid #E0DDD6;'>", unsafe_allow_html=True)
        with st.form("form_add_class", clear_on_submit=True):
            mag_label("클래스 이름")
            name_input = st.text_input("클래스 이름", placeholder="목요일 오후 글쓰기반", label_visibility="collapsed")
            mag_label("설명 (선택)")
            desc_input = st.text_input("설명", placeholder="초등 2-3학년 / 오후 4시", label_visibility="collapsed")
            fc1, fc2 = st.columns(2)
            if fc1.form_submit_button("추가", use_container_width=True):
                name = name_input.strip()
                if name:
                    cid = str(uuid.uuid4())[:8]
                    new_class = {
                        "id": cid, "name": name,
                        "description": desc_input.strip(),
                        "created_at": datetime.now().isoformat(),
                    }
                    classes[cid] = new_class
                    save_classes(classes)
                    # Pre-populate empty class data in session_state
                    st.session_state.class_data[cid] = {"children": [], "journals": []}
                    st.session_state.pop("_show_add_class", None)
                    st.rerun()
                else:
                    st.error("클래스 이름을 입력해 주세요.")
            if fc2.form_submit_button("취소", use_container_width=True):
                st.session_state.pop("_show_add_class", None)
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:1.5rem;'>", unsafe_allow_html=True)

    if not classes:
        st.markdown("""
        <div style="padding:3rem 2rem; border:1px dashed #C8C5BE; text-align:center;
                    font-size:0.85rem; color:#888;">
            클래스가 없습니다. '+ 새 클래스' 버튼으로 추가해 주세요.
        </div>""", unsafe_allow_html=True)
        return

    cols = st.columns(min(3, len(classes)))
    for idx, (cid, cls) in enumerate(classes.items()):
        with cols[idx % 3]:
            cdata = load_class_data(cid)
            n_ch = len(cdata["children"])
            n_jo = len(cdata["journals"])
            _name = _html.escape(cls['name'])
            _raw_desc = cls.get('description', '')
            _desc = _html.escape(_raw_desc) if _raw_desc else '&nbsp;'
            st.markdown(
                f'<div style="border:1px solid #E0DDD6; padding:1.8rem 1.6rem 1.2rem 1.6rem;'
                f'background:#FAF9F6; margin-bottom:1rem;">'
                f'<div style="font-size:0.6rem; font-weight:600; letter-spacing:0.16em;'
                f'text-transform:uppercase; color:#AAAAAA; margin-bottom:0.6rem;">Class</div>'
                f'<div style="font-family:\'DM Serif Display\',serif; font-size:1.4rem;'
                f'font-weight:400; color:#1A1A1A; margin-bottom:0.3rem; line-height:1.2;">'
                f'{_name}</div>'
                f'<div style="font-size:0.75rem; color:#999; font-weight:300; margin-bottom:1rem;">'
                f'{_desc}</div>'
                f'<div style="font-size:0.72rem; color:#777; margin-bottom:1.2rem; letter-spacing:0.03em;">'
                f'{n_ch}명 &nbsp;·&nbsp; {n_jo}개 일지</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            c_open, c_del = st.columns([3, 1])
            if c_open.button("열기", key=f"open_{cid}", use_container_width=True):
                st.session_state["nav_class_id"] = cid
                st.session_state["nav_class_name"] = cls["name"]
                st.session_state["current_class"] = {"id": cid, "name": cls["name"]}
                st.rerun()
            if c_del.button("삭제", key=f"del_cls_{cid}", use_container_width=True):
                st.session_state["_confirm_del_class"] = cid

    st.markdown("</div>", unsafe_allow_html=True)

    if "_confirm_del_class" in st.session_state:
        cid = st.session_state["_confirm_del_class"]
        cname = classes.get(cid, {}).get("name", "")
        st.warning(f"'{cname}' 클래스를 삭제하시겠습니까? 모든 일지 데이터가 삭제됩니다.")
        cc1, cc2 = st.columns(2)
        if cc1.button("삭제 확인"):
            classes.pop(cid, None)
            save_classes(classes)
            st.session_state.class_data.pop(cid, None)
            try:
                fp = class_data_path(cid)
                if os.path.exists(fp):
                    os.remove(fp)
            except Exception:
                pass
            st.session_state.pop("_confirm_del_class", None)
            st.rerun()
        if cc2.button("취소"):
            st.session_state.pop("_confirm_del_class", None)
            st.rerun()


# ── Class detail ──────────────────────────────────────────────────────────────
def render_class_detail(class_id: str, class_name: str):
    st.session_state.current_class = {"id": class_id, "name": class_name}
    keys = get_keys()

    if st.button("← Back"):
        for k in ("nav_class_id", "nav_class_name", "_class_result", "current_class"):
            st.session_state.pop(k, None)
        st.rerun()

    st.markdown(f"""
    <div style="border-bottom:2px solid #1A1A1A; padding-bottom:1.2rem;
                margin-bottom:2rem; margin-top:0.5rem;">
        <div style="font-size:0.6rem; font-weight:600; letter-spacing:0.18em;
                    text-transform:uppercase; color:#888; margin-bottom:0.5rem;">Class</div>
        <div style="font-family:'DM Serif Display',serif; font-size:2.4rem;
                    font-weight:400; color:#1A1A1A; line-height:1.05;">{class_name}</div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["Record & Analyse", "Children", "Journal Archive"])
    with tab1:
        render_upload_tab(class_id, class_name, keys)
    with tab2:
        render_children_tab(class_id)
    with tab3:
        render_journals_tab(class_id, keys)


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    _init_session_state()
    render_sidebar()

    if "nav_class_id" in st.session_state:
        render_class_detail(
            st.session_state["nav_class_id"],
            st.session_state["nav_class_name"],
        )
    else:
        render_home()


if __name__ == "__main__":
    main()
