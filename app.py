import io
import json
import random
import re
from datetime import date
from typing import Dict, List, Any

import google.generativeai as genai
import pandas as pd
import streamlit as st
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt

# =========================================================================
# 1. CẤU HÌNH HỆ THỐNG & GIAO DIỆN
# =========================================================================
st.set_page_config(
    page_title="EduAI-TestGen & LMS - Hệ Thống Khảo Thí & Ôn Tập AI",
    page_icon="🤖",
    layout="wide",
)

st.markdown(
    """
    <style>
        .block-container { padding-top: 1.2rem; padding-bottom: 2rem; }
        div[data-testid="stMetricValue"] { font-size: 1.8rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================================
# 2. DỮ LIỆU CHƯƠNG TRÌNH SGK "KẾT NỐI TRI THỨC" TIN HỌC THPT
# =========================================================================
CURRICULUM_DATA: Dict[str, Dict[str, List[str]]] = {
    "Lớp 10": {
        "Chủ đề 1: Máy tính và xã hội tri thức": [
            "Bài 1: Thông tin và xử lí thông tin",
            "Bài 2: Vai trò của thiết bị thông minh và tin học đối với xã hội",
            "Bài 3: Một số kiểu dữ liệu và dữ liệu văn bản",
            "Bài 4: Hệ nhị phân và dữ liệu số nguyên",
            "Bài 5: Dữ liệu lôgic",
            "Bài 6: Dữ liệu âm thanh và hình ảnh",
            "Bài 7: Thực hành sử dụng thiết bị số thông dụng",
        ],
        "Chủ đề 2: Mạng máy tính và Internet": [
            "Bài 8: Mạng máy tính trong cuộc sống hiện đại",
            "Bài 9: An toàn trên không gian mạng",
            "Bài 10: Thực hành khai thác tài nguyên trên Internet",
        ],
        "Chủ đề 3: Đạo đức, pháp luật và văn hoá trong môi trường số": [
            "Bài 11: Ứng xử trên môi trường số. Nghĩa vụ tôn trọng bản quyền"
        ],
        "Chủ đề 4: Ứng dụng tin học": [
            "Bài 12: Phần mềm thiết kế đồ hoạ",
            "Bài 13: Bổ sung các đối tượng đồ hoạ",
            "Bài 14: Làm việc với đối tượng đường và văn bản",
            "Bài 15: Hoàn thiện hình ảnh đồ hoạ",
        ],
        "Chủ đề 5: Giải quyết vấn đề với sự trợ giúp của máy tính": [
            "Bài 16: Ngôn ngữ lập trình bậc cao và Python",
            "Bài 17: Biến và lệnh gán",
            "Bài 18: Các lệnh vào ra đơn giản",
            "Bài 19: Câu lệnh rẽ nhánh if",
            "Bài 20: Câu lệnh lặp for",
            "Bài 21: Câu lệnh lặp while",
            "Bài 22: Kiểu dữ liệu danh sách",
            "Bài 23: Một số lệnh làm việc với dữ liệu danh sách",
            "Bài 24: Xâu kí tự",
            "Bài 25: Một số lệnh làm việc với xâu kí tự",
            "Bài 26: Hàm trong Python",
            "Bài 27: Tham số của hàm",
            "Bài 28: Phạm vi của biến",
            "Bài 29: Nhận biết lỗi chương trình",
            "Bài 30: Kiểm thử và gỡ lỗi chương trình",
            "Bài 31: Thực hành viết chương trình đơn giản",
            "Bài 32: Ôn tập lập trình Python",
        ],
        "Chủ đề 6: Hướng nghiệp với tin học": [
            "Bài 33: Nghề thiết kế đồ hoạ máy tính",
            "Bài 34: Nghề phát triển phần mềm",
        ],
    },
    "Lớp 11 (Tin học ứng dụng)": {
        "Chủ đề 1: Máy tính và xã hội tri thức": [
            "Bài 1: Hệ điều hành",
            "Bài 2: Thực hành sử dụng hệ điều hành",
            "Bài 3: Phần mềm nguồn mở và phần mềm chạy trên Internet",
            "Bài 4: Bên trong máy tính",
            "Bài 5: Kết nối máy tính với các thiết bị số",
        ],
        "Chủ đề 2: Tổ chức lưu trữ, tìm kiếm và trao đổi thông tin": [
            "Bài 6: Lưu trữ và chia sẻ tệp tin trên Internet",
            "Bài 7: Thực hành tìm kiếm thông tin trên Internet",
            "Bài 8: Thực hành nâng cao sử dụng thư điện tử và mạng xã hội",
        ],
        "Chủ đề 3: Đạo đức, pháp luật và văn hoá trong môi trường số": [
            "Bài 9: Giao tiếp an toàn trên Internet"
        ],
        "Chủ đề 4: Giới thiệu các hệ cơ sở dữ liệu": [
            "Bài 10: Lưu trữ dữ liệu và khai thác thông tin phục vụ quản lí",
            "Bài 11: Cơ sở dữ liệu",
            "Bài 12: Hệ quản trị cơ sở dữ liệu và hệ cơ sở dữ liệu",
            "Bài 13: Cơ sở dữ liệu quan hệ",
            "Bài 14: SQL - Ngôn ngữ truy vấn có cấu trúc",
            "Bài 15: Bảo mật và an toàn hệ cơ sở dữ liệu",
        ],
        "Chủ đề 5: Hướng nghiệp với tin học": [
            "Bài 16: Công việc quản trị cơ sở dữ liệu"
        ],
        "Chủ đề 6: Thực hành tạo và khai thác cơ sở dữ liệu": [
            "Bài 17: Quản trị cơ sở dữ liệu trên máy tính",
            "Bài 18: Thực hành xác định cấu trúc bảng và các trường khoá",
            "Bài 19: Thực hành tạo lập cơ sở dữ liệu và các bảng",
            "Bài 20: Thực hành tạo lập các bảng có khoá ngoài",
            "Bài 21: Thực hành cập nhật và truy xuất dữ liệu các bảng",
            "Bài 22: Thực hành cập nhật bảng dữ liệu có tham chiếu",
            "Bài 23: Thực hành truy xuất dữ liệu qua liên kết các bảng",
            "Bài 24: Thực hành sao lưu dữ liệu",
        ],
        "Chủ đề 7: Phần mềm chỉnh sửa ảnh và làm video": [
            "Bài 25: Phần mềm chỉnh sửa ảnh",
            "Bài 26: Công cụ tinh chỉnh màu sắc và công cụ chọn",
            "Bài 27: Công cụ vẽ và một số ứng dụng",
            "Bài 28: Tạo ảnh động",
            "Bài 29: Khám phá phần mềm làm phim",
            "Bài 30: Biên tập phim",
            "Bài 31: Thực hành tạo phim hoạt hình",
        ],
    },
    "Lớp 12 (Tin học ứng dụng)": {
        "Chủ đề 1: Máy tính và xã hội tri thức": [
            "Bài 1: Làm quen với Trí tuệ nhân tạo",
            "Bài 2: Trí tuệ nhân tạo trong khoa học và đời sống",
        ],
        "Chủ đề 2: Mạng máy tính và Internet": [
            "Bài 3: Một số thiết bị mạng thông dụng",
            "Bài 4: Giao thức mạng",
            "Bài 5: Thực hành chia sẻ tài nguyên trên mạng",
        ],
        "Chủ đề 3: Đạo đức, pháp luật và văn hoá trong môi trường số": [
            "Bài 6: Giao tiếp và ứng xử trong không gian mạng"
        ],
        "Chủ đề 4: Giải quyết vấn đề với sự trợ giúp của máy tính": [
            "Bài 7: HTML và cấu trúc trang web",
            "Bài 8: Định dạng văn bản",
            "Bài 9: Tạo danh sách, bảng",
            "Bài 10: Tạo liên kết",
            "Bài 11: Chèn tệp tin đa phương tiện và khung nội tuyến vào trang web",
            "Bài 12: Tạo biểu mẫu",
            "Bài 13: Khái niệm, vai trò của CSS",
            "Bài 14: Định dạng văn bản bằng CSS",
            "Bài 15: Tạo màu và định dạng phông chữ bằng CSS",
            "Bài 16: Định dạng khung",
            "Bài 17: Các mức ưu tiên của bộ chọn",
            "Bài 18: Thực hành tổng hợp thiết kế trang web",
        ],
    },
}

# =========================================================================
# 3. KHỞI TẠO SESSION STATE AN TOÀN
# =========================================================================
def init_session_state() -> None:
    defaults = {
        "exam_versions": [],          # Danh sách các mã đề đã trộn
        "question_bank_pool": [],     # Ngân hàng câu hỏi chuẩn hóa
        "matrix_df_state": None,      # Bảng ma trận hiện tại
        "last_selected_lessons": [],  # Theo dõi thay đổi lựa chọn bài học
        "quiz_session": None,         # Đề thi thử hiện tại của học sinh
        "published_exams": [],        # Danh sách mã bài kiểm tra đã phát hành
        "score_records": [            # Bảng điểm LMS (kết hợp mẫu + thực tế)
            {"STT": 1, "Họ và tên": "Nguyễn Văn An", "Lớp": "10A1", "Mã bài": "TIN_CAYDUONG_01", "Điểm số": 9.0, "Trạng thái": "Đã nộp bài"},
            {"STT": 2, "Họ và tên": "Trần Thị Bình", "Lớp": "10A1", "Mã bài": "TIN_CAYDUONG_01", "Điểm số": 8.5, "Trạng thái": "Đã nộp bài"},
            {"STT": 3, "Họ và tên": "Lê Hoàng Nam", "Lớp": "10A1", "Mã bài": "TIN_CAYDUONG_01", "Điểm số": 10.0, "Trạng thái": "Đã nộp bài"},
            {"STT": 4, "Họ và tên": "Phạm Minh Thư", "Lớp": "10A1", "Mã bài": "TIN_CAYDUONG_01", "Điểm số": 7.5, "Trạng thái": "Đã nộp bài"},
        ],
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_session_state()

# =========================================================================
# 4. CÁC HÀM LÕI: GỌI GEMINI AI, TRỘN ĐỀ & XUẤT FILE WORD
# =========================================================================
@st.cache_data(show_spinner=False)
def generate_questions_from_ai(api_key: str, grade: str, matrix_json: str) -> List[Dict[str, Any]]:
    """
    Gọi Gemini AI sinh bộ câu hỏi gốc dưới dạng JSON chuẩn.
    Nhờ trả về JSON và trộn đề bằng Python, tốc độ nhanh gấp nhiều lần và không bao giờ lệch đáp án.
    """
    genai.configure(api_key=api_key)
    matrix_config = json.loads(matrix_json)

    matrix_lines = []
    for item in matrix_config:
        matrix_lines.append(
            f"- {item['topic']} | {item['lesson']}: "
            f"Nhận biết ({item['nb']}), Thông hiểu ({item['th']}), "
            f"Vận dụng ({item['vd']}), Vận dụng cao ({item['vdc']})"
        )
    matrix_str = "\n".join(matrix_lines)

    prompt = f"""
Bạn là chuyên gia khảo thí môn Tin học THPT (Chương trình GDPT 2018 - Sách Kết nối tri thức với cuộc sống).
Hãy biên soạn bộ câu hỏi trắc nghiệm khách quan 4 lựa chọn cho khối {grade} bám sát ma trận sau:

{matrix_str}

YÊU CẦU BẮT BUỘC:
1. Tổng số câu hỏi phải khớp chính xác với tổng số câu trong ma trận.
2. Mỗi câu hỏi có 4 phương án lựa chọn (không ghi tiền tố A., B., C., D. vào trong nội dung phương án) và chỉ có duy nhất 1 phương án đúng.
3. Trả về KẾT QUẢ DUY NHẤT dưới dạng mảng JSON (JSON Array) theo đúng cấu trúc sau, không kèm văn bản giải thích bên ngoài:
[
  {{
    "lesson": "Tên bài học",
    "level": "Nhận biết | Thông hiểu | Vận dụng | Vận dụng cao",
    "question": "Nội dung câu hỏi...",
    "options": ["Nội dung phương án 1", "Nội dung phương án 2", "Nội dung phương án 3", "Nội dung phương án 4"],
    "correct_index": 0,
    "explanation": "Giải thích ngắn gọn vì sao đáp án này đúng"
  }}
]
(Lưu ý: correct_index là chỉ số 0, 1, 2 hoặc 3 tương ứng với phương án đúng trong mảng options).
"""
    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(
        prompt,
        generation_config={
            "temperature": 0.3,
            "response_mime_type": "application/json",
        },
    )

    if not response or not response.text:
        raise ValueError("Không nhận được phản hồi từ Gemini AI.")

    raw_text = response.text.strip()
    # Làm sạch trường hợp AI bọc markdown ```json ... ```
    raw_text = re.sub(r"^```(?:json)?\s*", "", raw_text)
    raw_text = re.sub(r"\s*```$", "", raw_text)

    questions = json.loads(raw_text)
    cleaned_questions = []
    for q in questions:
        opts = [re.sub(r"^[A-Da-d][\.\:\)]\s*", "", str(opt).strip()) for opt in q.get("options", [])]
        while len(opts) < 4:
            opts.append(f"Phương án bổ sung {len(opts) + 1}")
        opts = opts[:4]
        c_idx = int(q.get("correct_index", 0))
        if c_idx not in (0, 1, 2, 3):
            c_idx = 0

        cleaned_questions.append({
            "lesson": q.get("lesson", ""),
            "level": q.get("level", "Nhận biết"),
            "question": re.sub(r"^Câu\s*\d+[\.\:\s]*", "", str(q.get("question", "")).strip(), flags=re.IGNORECASE),
            "options": opts,
            "correct_index": c_idx,
            "explanation": q.get("explanation", ""),
        })
    return cleaned_questions


def generate_shuffled_versions(base_questions: List[Dict[str, Any]], num_versions: int) -> List[Dict[str, Any]]:
    """Hoán vị câu hỏi và phương án A, B, C, D tự động cho từng mã đề."""
    versions = []
    labels = ["A", "B", "C", "D"]

    for v_idx in range(num_versions):
        exam_code = f"{101 + v_idx}"
        shuffled_qs = random.sample(base_questions, len(base_questions))
        version_questions = []

        for q_idx, q in enumerate(shuffled_qs, start=1):
            correct_text = q["options"][q["correct_index"]]
            shuffled_opts = random.sample(q["options"], len(q["options"]))
            new_correct_idx = shuffled_opts.index(correct_text)
            answer_letter = labels[new_correct_idx]

            version_questions.append({
                "number": q_idx,
                "level": q["level"],
                "question": q["question"],
                "options": [f"{labels[i]}. {shuffled_opts[i]}" for i in range(4)],
                "raw_options": shuffled_opts,
                "answer": answer_letter,
                "explanation": q.get("explanation", ""),
            })

        versions.append({
            "exam_code": exam_code,
            "questions": version_questions,
        })
    return versions


def create_word_document(exam_versions: List[Dict[str, Any]], grade: str) -> bytes:
    """Xuất bộ đề kiểm tra và bảng đáp án chuẩn thể thức ra file Word (.docx)."""
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(12)

    for idx, version in enumerate(exam_versions):
        if idx > 0:
            doc.add_page_break()

        # Quốc hiệu / Tiêu đề đề thi
        hp = doc.add_paragraph()
        hp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        hp.add_run("TRƯỜNG THCS VÀ THPT CÂY DƯƠNG\n").bold = True
        hp.add_run(f"ĐỀ KIỂM TRA ĐỊNH KỲ - MÔN TIN HỌC {grade.upper()}\n").bold = True
        hp.add_run(f"MÃ ĐỀ: {version['exam_code']}\n").bold = True
        hp.add_run("Thời gian làm bài: 45 phút (Không kể thời gian phát đề)\n").italic = True

        doc.add_paragraph("Họ và tên thí sinh: ................................................................... Lớp: ...................")
        sep = doc.add_paragraph("_" * 65)
        sep.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Nội dung từng câu hỏi
        for q in version["questions"]:
            p_q = doc.add_paragraph()
            run_num = p_q.add_run(f"Câu {q['number']}: ")
            run_num.bold = True
            p_q.add_run(q["question"])

            for opt_str in q["options"]:
                p_opt = doc.add_paragraph(opt_str)
                p_opt.paragraph_format.left_indent = Pt(18)
                p_opt.paragraph_format.space_after = Pt(2)

    # Trang Đáp án và Hướng dẫn chấm ở cuối tài liệu
    doc.add_page_break()
    ans_heading = doc.add_paragraph()
    ans_heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_h = ans_heading.add_run("ĐÁP ÁN VÀ HƯỚNG DẪN CHẤM")
    run_h.bold = True
    run_h.font.size = Pt(14)

    for version in exam_versions:
        p_code = doc.add_paragraph()
        p_code.add_run(f"\nMã đề: {version['exam_code']}").bold = True

        num_q = len(version["questions"])
        table = doc.add_table(rows=2, cols=num_q)
        table.style = "Table Grid"
        for i, q in enumerate(version["questions"]):
            table.cell(0, i).text = f"Câu {q['number']}"
            table.cell(1, i).text = q["answer"]

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()


def build_default_matrix(lessons: List[str], ai_suggest: bool = False) -> pd.DataFrame:
    """Tạo DataFrame ma trận mặc định hoặc gợi ý tự động phân bổ theo chuẩn."""
    rows = []
    n = len(lessons)
    for idx, item in enumerate(lessons):
        topic_name, lesson_name = item.split(" | ", 1)
        if ai_suggest and n > 0:
            nb = max(1, round(8 / n))
            th = max(1, round(6 / n))
            vd = 1 if (idx % 2 == 0 or n <= 4) else 0
            vdc = 1 if (idx == n - 1) else 0
        else:
            nb, th, vd, vdc = 1, 1, 0, 0

        rows.append({
            "Chọn": True,
            "Chủ đề": topic_name,
            "Bài học": lesson_name,
            "Nhận biết": nb,
            "Thông hiểu": th,
            "Vận dụng": vd,
            "Vận dụng cao": vdc,
        })
    return pd.DataFrame(rows)

# =========================================================================
# 5. TIÊU ĐỀ & THANH ĐIỀU HƯỚNG CHÍNH
# =========================================================================
st.subheader("TRƯỜNG THCS VÀ THPT CÂY DƯƠNG | GIÁO VIÊN: CAO XUÂN ĐÚNG")
st.title("EduAI-TestGen: Hệ Thống Khảo Thí & Ôn Tập Thông Minh")

app_mode = st.selectbox(
    "CHỌN PHÂN HỆ LÀM VIỆC:",
    [
        "1. Khảo Thí & Ra Đề (Dành cho Giáo viên)",
        "2. Góc Ôn Tập Thông Minh (Dành cho Học sinh tự ôn)",
        "3. Quản Lý Bài Tập & Chấm Điểm (LMS Giáo viên)",
    ],
)
st.divider()

# =========================================================================
# PHÂN VÙNG 1: KHẢO THÍ & RA ĐỀ (GIÁO VIÊN)
# =========================================================================
if app_mode == "1. Khảo Thí & Ra Đề (Dành cho Giáo viên)":
    with st.sidebar:
        st.markdown("### ⚙️ CẤU HÌNH KHẢO THÍ")
        api_key_input = st.text_input("Nhập Google Gemini API Key", type="password")
        st.divider()

        st.header("1. Chọn phạm vi kiến thức")
        selected_grade = st.selectbox("Chọn khối lớp", list(CURRICULUM_DATA.keys()))

        all_lessons_in_grade = [
            f"{topic} | {lesson}"
            for topic, lessons in CURRICULUM_DATA[selected_grade].items()
            for lesson in lessons
        ]
        selected_lessons = st.multiselect("Chọn các bài học đưa vào đề thi", all_lessons_in_grade)
        num_versions = st.number_input("Số lượng mã đề cần trộn", min_value=1, max_value=10, value=2)

        st.divider()
        st.header("2. Bảng Ma Trận Đề Kiểm Tra")

        # Tự động đồng bộ bảng ma trận khi giáo viên thêm/bớt bài học
        if selected_lessons != st.session_state.last_selected_lessons:
            st.session_state.last_selected_lessons = selected_lessons
            st.session_state.matrix_df_state = (
                build_default_matrix(selected_lessons, ai_suggest=False) if selected_lessons else None
            )

        col_ai_btn, col_reset = st.columns([2, 1])
        with col_ai_btn:
            if st.button("✨ AI gợi ý ma trận", use_container_width=True):
                if not selected_lessons:
                    st.warning("Vui lòng chọn ít nhất một bài học!")
                else:
                    st.session_state.matrix_df_state = build_default_matrix(selected_lessons, ai_suggest=True)
                    st.toast("Đã phân bổ ma trận chuẩn!", icon="✅")
        with col_reset:
            if st.button("Đặt lại", use_container_width=True):
                st.session_state.matrix_df_state = (
                    build_default_matrix(selected_lessons, ai_suggest=False) if selected_lessons else None
                )
                st.rerun()

        matrix_config = []
        total_questions = 0

        if selected_lessons and st.session_state.matrix_df_state is not None:
            edited_df = st.data_editor(
                st.session_state.matrix_df_state,
                hide_index=True,
                column_config={
                    "Chọn": st.column_config.CheckboxColumn("Chọn", width="small"),
                    "Chủ đề": st.column_config.TextColumn("Chủ đề", disabled=True),
                    "Bài học": st.column_config.TextColumn("Bài học", disabled=True),
                    "Nhận biết": st.column_config.NumberColumn("NB", min_value=0, max_value=20, step=1, width="small"),
                    "Thông hiểu": st.column_config.NumberColumn("TH", min_value=0, max_value=20, step=1, width="small"),
                    "Vận dụng": st.column_config.NumberColumn("VD", min_value=0, max_value=20, step=1, width="small"),
                    "Vận dụng cao": st.column_config.NumberColumn("VDC", min_value=0, max_value=20, step=1, width="small"),
                },
                use_container_width=True,
            )

            df_selected = edited_df[edited_df["Chọn"] == True].copy()
            level_cols = ["Nhận biết", "Thông hiểu", "Vận dụng", "Vận dụng cao"]
            df_selected[level_cols] = df_selected[level_cols].fillna(0).astype(int)
            df_selected["Tổng số câu"] = df_selected[level_cols].sum(axis=1)
            total_questions = int(df_selected["Tổng số câu"].sum())

            for _, row in df_selected.iterrows():
                if row["Tổng số câu"] > 0:
                    matrix_config.append({
                        "topic": row["Chủ đề"],
                        "lesson": row["Bài học"],
                        "nb": int(row["Nhận biết"]),
                        "th": int(row["Thông hiểu"]),
                        "vd": int(row["Vận dụng"]),
                        "vdc": int(row["Vận dụng cao"]),
                    })

            st.info(f"**Tổng số câu hỏi:** {total_questions} câu")

    # Khu vực màn hình chính của Phân vùng 1
    st.subheader(f"Khởi tạo & Quản lý Đề kiểm tra ({num_versions} Mã đề)")

    if st.button("🚀 Bắt đầu sinh đề kiểm tra", type="primary"):
        if not api_key_input:
            st.error("Vui lòng nhập Google Gemini API Key ở thanh công cụ bên trái!")
        elif not matrix_config:
            st.warning("Vui lòng chọn bài học và thiết lập số lượng câu hỏi lớn hơn 0!")
        else:
            try:
                with st.spinner("Gemini AI đang biên soạn câu hỏi và trộn các mã đề..."):
                    matrix_json = json.dumps(matrix_config, ensure_ascii=False)
                    base_questions = generate_questions_from_ai(api_key_input, selected_grade, matrix_json)

                    # Trộn thành N mã đề bằng thuật toán Python
                    st.session_state.exam_versions = generate_shuffled_versions(base_questions, int(num_versions))

                    # Đưa câu hỏi gốc (không trùng lặp) vào Ngân hàng ôn tập cho học sinh
                    existing_q_texts = {q["question"] for q in st.session_state.question_bank_pool}
                    added_count = 0
                    for q in base_questions:
                        if q["question"] not in existing_q_texts:
                            st.session_state.question_bank_pool.append(q)
                            existing_q_texts.add(q["question"])
                            added_count += 1

                    st.success(
                        f"Đã tạo thành công {num_versions} mã đề ({len(base_questions)} câu/đề) "
                        f"và bổ sung {added_count} câu hỏi mới vào Ngân hàng ôn tập!"
                    )
            except Exception as e:
                st.error(f"Lỗi khi sinh đề từ Gemini AI: {e}")

    # Hiển thị bản xem trước và nút tải Word
    if st.session_state.exam_versions:
        word_bytes = create_word_document(st.session_state.exam_versions, selected_grade)
        st.download_button(
            label="📥 Tải BỘ ĐỀ & ĐÁP ÁN (File Word chuẩn in ấn)",
            data=word_bytes,
            file_name=f"Bo_De_Tin_Hoc_{selected_grade.replace(' ', '_')}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            type="primary",
        )

        st.markdown("#### 📄 Xem trước các mã đề và đáp án")
        tabs = st.tabs([f"Mã đề {v['exam_code']}" for v in st.session_state.exam_versions] + ["🔑 Bảng Đáp Án"])

        for idx, version in enumerate(st.session_state.exam_versions):
            with tabs[idx]:
                for q in version["questions"]:
                    st.markdown(f"**Câu {q['number']}** *({q['level']})*: {q['question']}")
                    for opt in q["options"]:
                        st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;{opt}")
                    st.write("")

        with tabs[-1]:
            for version in st.session_state.exam_versions:
                st.markdown(f"**Mã đề {version['exam_code']}**")
                ans_df = pd.DataFrame(
                    [[q["answer"] for q in version["questions"]]],
                    columns=[f"Câu {q['number']}" for q in version["questions"]],
                )
                st.dataframe(ans_df, use_container_width=True, hide_index=True)

# =========================================================================
# PHÂN VÙNG 2: GÓC ÔN TẬP THÔNG MINH (HỌC SINH)
# =========================================================================
elif app_mode == "2. Góc Ôn Tập Thông Minh (Dành cho Học sinh tự ôn)":
    st.markdown("### 📝 PHÒNG ÔN TẬP TRỰC TUYẾN TỪ NGÂN HÀNG ĐỀ")
    pool_size = len(st.session_state.question_bank_pool)

    if pool_size == 0:
        st.warning(
            "Kho ngân hàng câu hỏi đang trống! Giáo viên vui lòng vào mục "
            "**'1. Khảo Thí & Ra Đề'** để sinh ít nhất một đề kiểm tra trước."
        )
    else:
        st.success(f"Kho ôn tập hiện có **{pool_size}** câu hỏi sẵn sàng.")

        col_info1, col_info2, col_info3 = st.columns(3)
        with col_info1:
            student_name = st.text_input("Họ và tên học sinh:", placeholder="Nguyễn Văn A")
        with col_info2:
            student_class = st.text_input("Lớp:", value="10A1")
        with col_info3:
            max_q = min(20, pool_size)
            min_q = 1 if pool_size < 3 else 3
            default_q = min(5, max_q)
            if min_q == max_q:
                num_to_quiz = max_q
                st.info(f"Số câu hỏi làm bài: {num_to_quiz} câu")
            else:
                num_to_quiz = st.slider(
                    "Số lượng câu hỏi muốn luyện tập:",
                    min_value=min_q,
                    max_value=max_q,
                    value=default_q,
                )

        if st.button("🎯 Bắt đầu làm bài ôn tập mới", type="primary"):
            sampled = random.sample(st.session_state.question_bank_pool, num_to_quiz)
            quiz_items = []
            labels = ["A", "B", "C", "D"]
            for q in sampled:
                correct_text = q["options"][q["correct_index"]]
                shuffled_opts = random.sample(q["options"], 4)
                correct_letter = labels[shuffled_opts.index(correct_text)]
                quiz_items.append({
                    "question": q["question"],
                    "level": q.get("level", ""),
                    "formatted_options": [f"{labels[i]}. {shuffled_opts[i]}" for i in range(4)],
                    "answer": correct_letter,
                    "explanation": q.get("explanation", ""),
                })
            st.session_state.quiz_session = quiz_items

        if st.session_state.quiz_session:
            st.markdown("---")
            with st.form("student_quiz_form"):
                user_answers = {}
                for idx, q_item in enumerate(st.session_state.quiz_session, start=1):
                    st.markdown(f"**Câu {idx}:** {q_item['question']}")
                    selected_opt = st.radio(
                        f"Chọn đáp án câu {idx}:",
                        options=q_item["formatted_options"],
                        index=None,
                        key=f"quiz_q_{idx}",
                        label_visibility="collapsed",
                    )
                    user_answers[idx] = selected_opt[0] if selected_opt else "Chưa chọn"
                    st.write("")

                submitted_quiz = st.form_submit_button("✅ Nộp bài và Xem kết quả", type="primary")

            if submitted_quiz:
                score_cnt = 0
                total_q = len(st.session_state.quiz_session)
                st.markdown("### 📊 KẾT QUẢ BÀI LÀM CHI TIẾT")

                for idx, q_item in enumerate(st.session_state.quiz_session, start=1):
                    u_ans = user_answers.get(idx, "Chưa chọn")
                    c_ans = q_item["answer"]
                    if u_ans == c_ans:
                        score_cnt += 1
                        st.success(f"**Câu {idx}: Chính xác!** (Em chọn **{u_ans}**)")
                    else:
                        st.error(
                            f"**Câu {idx}: Chưa đúng.** (Em chọn: **{u_ans}** | Đáp án đúng: **{c_ans}**)"
                        )
                    if q_item.get("explanation"):
                        st.caption(f"💡 *Giải thích:* {q_item['explanation']}")

                final_score = round((score_cnt / total_q) * 10, 1)
                st.metric(
                    label="Điểm số đạt được",
                    value=f"{final_score} / 10 điểm",
                    delta=f"Đúng {score_cnt}/{total_q} câu",
                )

                if final_score >= 8.0:
                    st.balloons()

                # Tự động lưu điểm vào hệ thống LMS (Phân vùng 3) nếu học sinh có nhập tên
                if student_name.strip():
                    st.session_state.score_records.append({
                        "STT": len(st.session_state.score_records) + 1,
                        "Họ và tên": student_name.strip(),
                        "Lớp": student_class.strip() or "Tự chọn",
                        "Mã bài": "ON_TAP_AI",
                        "Điểm số": final_score,
                        "Trạng thái": "Đã nộp bài",
                    })
                    st.info(f"Đã tự động lưu kết quả của **{student_name}** vào Bảng điểm LMS!")

# =========================================================================
# PHÂN VÙNG 3: QUẢN LÝ BÀI TẬP & CHẤM ĐIỂM (LMS GIÁO VIÊN)
# =========================================================================
elif app_mode == "3. Quản Lý Bài Tập & Chấm Điểm (LMS Giáo viên)":
    st.markdown("### 📈 QUẢN LÝ TIẾN ĐỘ & BẢNG ĐIỂM HỌC SINH")
    st.info(
        f"Ngân hàng đề hiện có **{len(st.session_state.question_bank_pool)}** câu hỏi | "
        f"Tổng số lượt nộp bài đã ghi nhận:
