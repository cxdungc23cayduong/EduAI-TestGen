import io
import json
import random
import re
from datetime import date
from typing import Any, Dict, List

import google.generativeai as genai
import pandas as pd
import streamlit as st
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt

# --- 1. CẤU HÌNH HỆ THỐNG & GIAO DIỆN ---
st.set_page_config(
    page_title="EduAI-TestGen & LMS",
    page_icon="🤖",
    layout="wide",
)

st.markdown(
    "<style>.block-container { padding-top: 1.2rem; padding-bottom: 2rem; }</style>",
    unsafe_allow_html=True,
)

# --- 2. DỮ LIỆU CHƯƠNG TRÌNH SGK TIN HỌC THPT ---
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
            f"Bài {i}: Thực hành cơ sở dữ liệu" for i in range(17, 25)
        ],
        "Chủ đề 7: Phần mềm chỉnh sửa ảnh và làm video": [
            f"Bài {i}: Chỉnh sửa ảnh và làm video" for i in range(25, 32)
        ],
    },
    "Lớp 12 (Tin học ứng dụng)": {
        "Chủ đề 1: Máy tính và xã hội tri thức": [
            "Bài 1: Làm quen với Trí tuệ nhân tạo",
            "Bài 2: Trí tuệ nhân tạo trong khoa học và đời sống",
        ],
        "Chủ đề 4: Giải quyết vấn đề với sự trợ giúp của máy tính": [
            "Bài 7: HTML và cấu trúc trang web",
            "Bài 8: Định dạng văn bản",
            "Bài 9: Tạo danh sách, bảng",
            "Bài 10: Tạo liên kết",
            "Bài 13: Khái niệm, vai trò của CSS",
            "Bài 14: Định dạng văn bản bằng CSS",
        ],
    },
}

# --- 3. KHỞI TẠO SESSION STATE ---
def init_session_state() -> None:
    defaults = {
        "exam_versions": [],
        "question_bank_pool": [],
        "matrix_df_state": None,
        "last_selected_lessons": [],
        "quiz_session": None,
        "published_exams": [],
        "score_records": [
            {"STT": 1, "Họ và tên": "Nguyễn Văn An", "Lớp": "10A1", "Mã bài": "TIN_01", "Điểm số": 9.0, "Trạng thái": "Đã nộp bài"},
            {"STT": 2, "Họ và tên": "Trần Thị Bình", "Lớp": "10A1", "Mã bài": "TIN_01", "Điểm số": 8.5, "Trạng thái": "Đã nộp bài"},
            {"STT": 3, "Họ và tên": "Lê Hoàng Nam", "Lớp": "10A1", "Mã bài": "TIN_01", "Điểm số": 10.0, "Trạng thái": "Đã nộp bài"},
            {"STT": 4, "Họ và tên": "Phạm Minh Thư", "Lớp": "10A1", "Mã bài": "TIN_01", "Điểm số": 7.5, "Trạng thái": "Đã nộp bài"},
        ],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session_state()

# --- 4. CÁC HÀM XỬ LÝ LÕI ---
@st.cache_data(show_spinner=False)
def generate_questions_from_ai(api_key: str, grade: str, matrix_json: str) -> List[Dict[str, Any]]:
    genai.configure(api_key=api_key)
    matrix_config = json.loads(matrix_json)

    lines = []
    for item in matrix_config:
        row_str = (
            f"- {item['topic']} | {item['lesson']}: "
            f"NB({item['nb']}), TH({item['th']}), VD({item['vd']}), VDC({item['vdc']})"
        )
        lines.append(row_str)
    matrix_str = "\n".join(lines)

    prompt_parts = [
        f"Bạn là chuyên gia khảo thí Tin học THPT (GDPT 2018 - Kết nối tri thức) khối {grade}.",
        "Hãy biên soạn bộ câu hỏi trắc nghiệm 4 lựa chọn bám sát ma trận sau:",
        matrix_str,
        "YÊU CẦU BẮT BUỘC:",
        "1. Tổng số câu hỏi khớp chính xác với ma trận.",
        "2. Mỗi câu có 4 phương án trong mảng options (không ghi A., B., C., D. ở đầu).",
        "3. Chỉ trả về JSON Array theo cấu trúc:",
        '[{"lesson": "...", "level": "Nhận biết", "question": "...", "options": ["...", "...", "...", "..."], "correct_index": 0, "explanation": "..."}]',
    ]
    prompt = "\n".join(prompt_parts)

    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(
        prompt,
        generation_config={"temperature": 0.3, "response_mime_type": "application/json"},
    )

    if not response or not response.text:
        raise ValueError("Không nhận được phản hồi từ Gemini AI.")

    raw_text = response.text.strip()
    raw_text = re.sub(r"^```(?:json)?\s*", "", raw_text)
    raw_text = re.sub(r"\s*```$", "", raw_text)

    questions = json.loads(raw_text)
    cleaned = []
    for q in questions:
        opts = [re.sub(r"^[A-Da-d][\.\:\)]\s*", "", str(o).strip()) for o in q.get("options", [])]
        while len(opts) < 4:
            opts.append(f"Phương án {len(opts) + 1}")
        opts = opts[:4]
        c_idx = int(q.get("correct_index", 0))
        if c_idx not in (0, 1, 2, 3):
            c_idx = 0

        q_text = re.sub(r"^Câu\s*\d+[\.\:\s]*", "", str(q.get("question", "")).strip(), flags=re.IGNORECASE)
        cleaned.append({
            "lesson": q.get("lesson", ""),
            "level": q.get("level", "Nhận biết"),
            "question": q_text,
            "options": opts,
            "correct_index": c_idx,
            "explanation": q.get("explanation", ""),
        })
    return cleaned


def generate_shuffled_versions(base_questions: List[Dict[str, Any]], num_versions: int) -> List[Dict[str, Any]]:
    versions = []
    labels = ["A", "B", "C", "D"]
    for v_idx in range(num_versions):
        exam_code = str(101 + v_idx)
        shuffled_qs = random.sample(base_questions, len(base_questions))
        v_questions = []
        for q_idx, q in enumerate(shuffled_qs, start=1):
            correct_text = q["options"][q["correct_index"]]
            shuffled_opts = random.sample(q["options"], 4)
            ans_letter = labels[shuffled_opts.index(correct_text)]
            v_questions.append({
                "number": q_idx,
                "level": q["level"],
                "question": q["question"],
                "options": [f"{labels[i]}. {shuffled_opts[i]}" for i in range(4)],
                "answer": ans_letter,
                "explanation": q.get("explanation", ""),
            })
        versions.append({"exam_code": exam_code, "questions": v_questions})
    return versions


def create_word_document(exam_versions: List[Dict[str, Any]], grade: str) -> bytes:
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(12)

    for idx, version in enumerate(exam_versions):
        if idx > 0:
            doc.add_page_break()
        hp = doc.add_paragraph()
        hp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        hp.add_run("TRƯỜNG THCS VÀ THPT CÂY DƯƠNG\n").bold = True
        hp.add_run(f"ĐỀ KIỂM TRA ĐỊNH KỲ - MÔN TIN HỌC {grade.upper()}\n").bold = True
        hp.add_run(f"MÃ ĐỀ: {version['exam_code']}\n").bold = True
        hp.add_run("Thời gian làm bài: 45 phút\n").italic = True

        doc.add_paragraph("Họ và tên thí sinh: .................................................... Lớp: .............")
        sep = doc.add_paragraph("_" * 60)
        sep.alignment = WD_ALIGN_PARAGRAPH.CENTER

        for q in version["questions"]:
            p_q = doc.add_paragraph()
            p_q.add_run(f"Câu {q['number']}: ").bold = True
            p_q.add_run(q["question"])
            for opt_str in q["options"]:
                p_opt = doc.add_paragraph(opt_str)
                p_opt.paragraph_format.left_indent = Pt(18)
                p_opt.paragraph_format.space_after = Pt(2)

    doc.add_page_break()
    ans_h = doc.add_paragraph()
    ans_h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_h = ans_h.add_run("ĐÁP ÁN VÀ HƯỚNG DẪN CHẤM")
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

    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf.getvalue()


def build_default_matrix(lessons: List[str], ai_suggest: bool = False) -> pd.DataFrame:
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

# --- 5. GIAO DIỆN CHÍNH ---
st.subheader("TRƯỜNG THCS VÀ THPT CÂY DƯƠNG | GIÁO VIÊN: CAO XUÂN ĐÚNG")
st.title("EduAI-TestGen: Hệ Thống Khảo Thí & Ôn Tập Thông Minh")

MODE_1 = "1. Khảo Thí & Ra Đề (Dành cho Giáo viên)"
MODE_2 = "2. Góc Ôn Tập Thông Minh (Dành cho Học sinh tự ôn)"
MODE_3 = "3. Quản Lý Bài Tập & Chấm Điểm (LMS Giáo viên)"

app_mode = st.selectbox("CHỌN CHỨC NĂNG HỆ THỐNG:", [MODE_1, MODE_2, MODE_3])
st.divider()

# =========================================================================
# PHÂN VÙNG 1: KHẢO THÍ & RA ĐỀ
# =========================================================================
if app_mode == MODE_1:
    with st.sidebar:
        st.markdown("### QUẢN LÝ KHẢO THÍ")
        api_key_input = st.text_input("Nhập Google Gemini API Key", type="password")
        st.divider()

        st.header("1. Chọn bài học")
        selected_grade = st.selectbox("Chọn khối lớp", list(CURRICULUM_DATA.keys()))
        all_lessons = [
            f"{t} | {l}"
            for t, lessons in CURRICULUM_DATA[selected_grade].items()
            for l in lessons
        ]
        selected_lessons = st.multiselect("Chọn các bài học", all_lessons)
        num_versions = st.number_input("Số lượng mã đề", min_value=1, max_value=10, value=2)

        st.divider()
        st.header("2. Ma Trận Đề Kiểm Tra")

        if selected_lessons != st.session_state.last_selected_lessons:
            st.session_state.last_selected_lessons = selected_lessons
            st.session_state.matrix_df_state = (
                build_default_matrix(selected_lessons, False) if selected_lessons else None
            )

        c_ai, c_rst = st.columns([2, 1])
        with c_ai:
            if st.button("AI gợi ý ma trận", use_container_width=True):
                if not selected_lessons:
                    st.warning("Vui lòng chọn bài học!")
                else:
                    st.session_state.matrix_df_state = build_default_matrix(selected_lessons, True)
        with c_rst:
            if st.button("Đặt lại", use_container_width=True):
                st.session_state.matrix_df_state = (
                    build_default_matrix(selected_lessons, False) if selected_lessons else None
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

            df_sel = edited_df[edited_df["Chọn"] == True].copy()
            lvl_cols = ["Nhận biết", "Thông hiểu", "Vận dụng", "Vận dụng cao"]
            df_sel[lvl_cols] = df_sel[lvl_cols].fillna(0).astype(int)
            df_sel["Tổng"] = df_sel[lvl_cols].sum(axis=1)
            total_questions = int(df_sel["Tổng"].sum())

            for _, r in df_sel.iterrows():
                if r["Tổng"] > 0:
                    matrix_config.append({
                        "topic": r["Chủ đề"],
                        "lesson": r["Bài học"],
                        "nb": int(r["Nhận biết"]),
                        "th": int(r["Thông hiểu"]),
                        "vd": int(r["Vận dụng"]),
                        "vdc": int(r["Vận dụng cao"]),
                    })
            st.success(f"Tổng số câu hỏi: {total_questions} câu")

    st.subheader(f"Nội dung đề kiểm tra ({num_versions} Mã đề)")

    if st.button("Bắt đầu sinh đề kiểm tra", type="primary"):
        if not api_key_input:
            st.error("Vui lòng nhập Google Gemini API Key ở thanh bên trái!")
        elif not matrix_config:
            st.warning("Vui lòng chọn ít nhất một bài học!")
        else:
            try:
                with st.spinner("Gemini AI đang biên soạn và trộn mã đề..."):
                    m_json = json.dumps(matrix_config, ensure_ascii=False)
                    base_qs = generate_questions_from_ai(api_key_input, selected_grade, m_json)
                    st.session_state.exam_versions = generate_shuffled_versions(base_qs, int(num_versions))

                    existing = {q["question"] for q in st.session_state.question_bank_pool}
                    added = 0
                    for q in base_qs:
                        if q["question"] not in existing:
                            st.session_state.question_bank_pool.append(q)
                            existing.add(q["question"])
                            added += 1

                    msg = f"Đã tạo {num_versions} mã đề và thêm {added} câu hỏi vào Ngân hàng ôn tập!"
                    st.success(msg)
            except Exception as e:
                st.error(f"Lỗi kết nối Gemini AI: {e}")

    if st.session_state.exam_versions:
        docx_bytes = create_word_document(st.session_state.exam_versions, selected_grade)
        st.download_button(
            label="📥 Tải BỘ ĐỀ & ĐÁP ÁN (File Word chuẩn)",
            data=docx_bytes,
            file_name=f"Bo_De_{selected_grade.replace(' ', '_')}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            type="primary",
        )

        tab_names = [f"Mã đề {v['exam_code']}" for v in st.session_state.exam_versions] + ["Bảng Đáp Án"]
        tabs = st.tabs(tab_names)
        for i, v in enumerate(st.session_state.exam_versions):
            with tabs[i]:
                for q in v["questions"]:
                    st.markdown(f"**Câu {q['number']}** *({q['level']})*: {q['question']}")
                    for opt in q["options"]:
                        st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;{opt}")
                    st.write("")
        with tabs[-1]:
            for v in st.session_state.exam_versions:
                st.markdown(f"**Mã đề {v['exam_code']}**")
                ans_df = pd.DataFrame(
                    [[q["answer"] for q in v["questions"]]],
                    columns=[f"Câu {q['number']}" for q in v["questions"]],
                )
                st.dataframe(ans_df, use_container_width=True, hide_index=True)

# =========================================================================
# PHÂN VÙNG 2: GÓC ÔN TẬP THÔNG MINH
# =========================================================================
elif app_mode == MODE_2:
    st.markdown("### PHÒNG ÔN TẬP TRỰC TUYẾN TỪ KHO ĐỀ")
    pool_size = len(st.session_state.question_bank_pool)

    if pool_size == 0:
        st.warning("Kho câu hỏi đang trống! Vui lòng vào mục 1 để sinh đề kiểm tra trước.")
    else:
        st.success(f"Kho ôn tập hiện có {pool_size} câu hỏi.")
        c1, c2, c3 = st.columns(3)
        with c1:
            student_name = st.text_input("Họ và tên học sinh:", placeholder="Nguyễn Văn A")
        with c2:
            student_class = st.text_input("Lớp:", value="10A1")
        with c3:
            max_q = min(20, pool_size)
            min_q = 1 if pool_size < 3 else 3
            def_q = min(5, max_q)
            if min_q == max_q:
                num_to_quiz = max_q
            else:
                num_to_quiz = st.slider("Số câu ôn tập:", min_value=min_q, max_value=max_q, value=def_q)

        if st.button("Bắt đầu làm bài trắc nghiệm", type="primary"):
            sampled = random.sample(st.session_state.question_bank_pool, num_to_quiz)
            quiz_items = []
            labels = ["A", "B", "C", "D"]
            for q in sampled:
                c_text = q["options"][q["correct_index"]]
                s_opts = random.sample(q["options"], 4)
                c_letter = labels[s_opts.index(c_text)]
                quiz_items.append({
                    "question": q["question"],
                    "formatted_options": [f"{labels[i]}. {s_opts[i]}" for i in range(4)],
                    "answer": c_letter,
                    "explanation": q.get("explanation", ""),
                })
            st.session_state.quiz_session = quiz_items

        if st.session_state.quiz_session:
            st.markdown("---")
            with st.form("student_quiz_form"):
                user_answers = {}
                for idx, q_item in enumerate(st.session_state.quiz_session, start=1):
                    st.markdown(f"**Câu {idx}:** {q_item['question']}")
                    sel = st.radio(
                        f"Câu {idx}",
                        options=q_item["formatted_options"],
                        index=None,
                        key=f"quiz_q_{idx}",
                        label_visibility="collapsed",
                    )
                    user_answers[idx] = sel[0] if sel else "Chưa chọn"
                    st.write("")
                submitted_quiz = st.form_submit_button("Nộp bài và chấm điểm", type="primary")

            if submitted_quiz:
                score_cnt = 0
                total_q = len(st.session_state.quiz_session)
                st.markdown("### KẾT QUẢ ÔN TẬP")
                for idx, q_item in enumerate(st.session_state.quiz_session, start=1):
                    u_ans = user_answers.get(idx, "Chưa chọn")
                    c_ans = q_item["answer"]
                    if u_ans == c_ans:
                        score_cnt += 1
                        st.success(f"Câu {idx}: Đúng! (Em chọn {u_ans})")
                    else:
                        st.error(f"Câu {idx}: Sai. (Em chọn {u_ans} | Đáp án đúng: {c_ans})")
                    if q_item.get("explanation"):
                        st.caption(f"Giải thích: {q_item['explanation']}")

                final_score = round((score_cnt / total_q) * 10, 1)
                st.metric("Điểm tổng kết", f"{final_score} điểm", f"Đúng {score_cnt}/{total_q} câu")
                if final_score >= 8.0:
                    st.balloons()

                if student_name.strip():
                    st.session_state.score_records.append({
                        "STT": len(st.session_state.score_records) + 1,
                        "Họ và tên": student_name.strip(),
                        "Lớp": student_class.strip() or "10A1",
                        "Mã bài": "ON_TAP_AI",
                        "Điểm số": final_score,
                        "Trạng thái": "Đã nộp bài",
                    })
                    st.info("Đã lưu điểm vào hệ thống LMS!")

# =========================================================================
# PHÂN VÙNG 3: QUẢN LÝ BÀI TẬP & CHẤM ĐIỂM
# =========================================================================
elif app_mode == MODE_3:
    st.markdown("### QUẢN LÝ TIẾN ĐỘ & BẢNG ĐIỂM")
    num_bank = len(st.session_state.question_bank_pool)
    num_scores = len(st.session_state.score_records)
    st.info(f"Ngân hàng đề: **{num_bank}** câu hỏi | Đã ghi nhận: **{num_scores}** lượt nộp bài.")

    tab1, tab2 = st.tabs(["1. Giao bài kiểm tra nhanh", "2. Bảng điểm học sinh"])

    with tab1:
        st.subheader("Tạo Mã Bài Kiểm Tra Cho Lớp")
        c1, c2 = st.columns(2)
        with c1:
            ex_title = st.text_input("Tên bài kiểm tra:", "Kiểm tra 15 phút - Tin học THPT")
            ex_class = st.text_input("Lớp:", "10A1")
        with c2:
            ex_code = st.text_input("Mã bài kiểm tra:", "TIN_CAYDUONG_01")
            ex_date = st.date_input("Hạn nộp:", value=date.today())

        if st.button("Xác nhận phát hành bài kiểm tra", type="primary"):
            st.session_state.published_exams.append({
                "Mã bài": ex_code,
                "Tên bài": ex_title,
                "Lớp": ex_class,
                "Hạn nộp": ex_date.strftime("%d/%m/%Y"),
            })
            st.success(f"Đã phát hành mã bài {ex_code} thành công!")

        if st.session_state.published_exams:
            st.dataframe(pd.DataFrame(st.session_state.published_exams), use_container_width=True, hide_index=True)

    with tab2:
        st.subheader("Bảng Điểm Tổng Hợp")
        df_score = pd.DataFrame(st.session_state.score_records)
        st.dataframe(df_score, use_container_width=True, hide_index=True)

        score_buf = io.BytesIO()
        with pd.ExcelWriter(score_buf, engine="openpyxl") as writer:
            df_score.to_excel(writer, index=False, sheet_name="BangDiem")
        score_buf.seek(0)
        st.download_button(
            label="📥 Tải Bảng Điểm Excel",
            data=score_buf,
            file_name="BangDiem_Lop.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
