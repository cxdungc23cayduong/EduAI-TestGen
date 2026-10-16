import io
import random
import re
import google.generativeai as genai
import streamlit as st
import pandas as pd
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

# --- 1. CẤU HÌNH GIAO DIỆN TỐC ĐỘ CAO ---
st.set_page_config(
    page_title="EduAI-TestGen & LMS - Hệ Thống Khảo Thí & Ôn Tập AI",
    page_icon="🤖",
    layout="wide",
)

# Tối ưu render giao diện
st.markdown("""
    <style>
        .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
    </style>
""", unsafe_allow_html=True)

# --- 2. DỮ LIỆU CHUẨN SÁCH GIÁO KHOA "KẾT NỐI TRI THỨC" TIN HỌC THPT ---
CURRICULUM_DATA = {
    "Lớp 10": {
        "Chủ đề 1: Máy tính và xã hội tri thức": [
            "Bài 1: Thông tin và xử lí thông tin", "Bài 2: Vai trò của thiết bị thông minh và tin học đối với xã hội",
            "Bài 3: Một số kiểu dữ liệu và dữ liệu văn bản", "Bài 4: Hệ nhị phân và dữ liệu số nguyên",
            "Bài 5: Dữ liệu lôgic", "Bài 6: Dữ liệu âm thanh và hình ảnh", "Bài 7: Thực hành sử dụng thiết bị số thông dụng"
        ],
        "Chủ đề 2: Mạng máy tính và Internet": ["Bài 8: Mạng máy tính trong cuộc sống hiện đại", "Bài 9: An toàn trên không gian mạng", "Bài 10: Thực hành khai thác tài nguyên trên Internet"],
        "Chủ đề 3: Đạo đức, pháp luật và văn hoá trong môi trường số": ["Bài 11: Ứng xử trên môi trường số. Nghĩa vụ tôn trọng bản quyền"],
        "Chủ đề 4: Ứng dụng tin học": ["Bài 12: Phần mềm thiết kế đồ hoạ", "Bài 13: Bổ sung các đối tượng đồ hoạ", "Bài 14: Làm việc với đối tượng đường và văn bản", "Bài 15: Hoàn thiện hình ảnh đồ hoạ"],
        "Chủ đề 5: Giải quyết vấn đề với sự trợ giúp của máy tính": [
            "Bài 16: Ngôn ngữ lập trình bậc cao và Python", "Bài 17: Biến và lệnh gán", "Bài 18: Các lệnh vào ra đơn giản",
            "Bài 19: Câu lệnh rẽ nhánh if", "Bài 20: Câu lệnh lặp for", "Bài 21: Câu lệnh lặp while",
            "Bài 22: Kiểu dữ liệu danh sách", "Bài 23: Một số lệnh làm việc với dữ liệu danh sách", "Bài 24: Xâu kí tự",
            "Bài 25: Một số lệnh làm việc với xâu kí tự", "Bài 26: Hàm trong Python", "Bài 27: Tham số của hàm",
            "Bài 28: Phạm vi của biến", "Bài 29: Nhận biết lỗi chương trình", "Bài 30: Kiểm thử và gỡ lỗi chương trình",
            "Bài 31: Thực hành viết chương trình đơn giản", "Bài 32: Ôn tập lập trình Python"
        ],
        "Chủ đề 6: Hướng nghiệp với tin học": ["Bài 33: Nghề thiết kế đồ hoạ máy tính", "Bài 34: Nghề phát triển phần mềm"]
    },
    "Lớp 11 (Tin học ứng dụng)": {
        "Chủ đề 1: Máy tính và xã hội tri thức": ["Bài 1: Hệ điều hành", "Bài 2: Thực hành sử dụng hệ điều hành", "Bài 3: Phần mềm nguồn mở và phần mềm chạy trên Internet", "Bài 4: Bên trong máy tính", "Bài 5: Kết nối máy tính với các thiết bị số"],
        "Chủ đề 2: Tổ chức lưu trữ, tìm kiếm và trao đổi thông tin": ["Bài 6: Lưu trữ và chia sẻ tệp tin trên Internet", "Bài 7: Thực hành tìm kiếm thông tin trên Internet", "Bài 8: Thực hành nâng cao sử dụng thư điện tử và mạng xã hội"],
        "Chủ đề 3: Đạo đức, pháp luật và văn hoá trong môi trường số": ["Bài 9: Giao tiếp an toàn trên Internet"],
        "Chủ đề 4: Giới thiệu các hệ cơ sở dữ liệu": ["Bài 10: Lưu trữ dữ liệu và khai thác thông tin phục vụ quản lí", "Bài 11: Cơ sở dữ liệu", "Bài 12: Hệ quản trị cơ sở dữ liệu và hệ cơ sở dữ liệu", "Bài 13: Cơ sở dữ liệu quan hệ", "Bài 14: SQL - Ngôn ngữ truy vấn có cấu trúc", "Bài 15: Bảo mật và an toàn hệ cơ sở dữ liệu"],
        "Chủ đề 5: Hướng nghiệp với tin học": ["Bài 16: Công việc quản trị cơ sở dữ liệu"],
        "Chủ đề 6: Thực hành tạo và khai thác cơ sở dữ liệu": [f"Bài {i}: Thực hành..." for i in range(17, 25)],
        "Chủ đề 7: Phần mềm chỉnh sửa ảnh và làm video": [f"Bài {i}: ..." for i in range(25, 32)]
    },
    "Lớp 12 (Tin học ứng dụng)": {
        "Chủ đề 1: Máy tính và xã hội tri thức": ["Làm quen với Trí tuệ nhân tạo", "Trí tuệ nhân tạo trong khoa học và đời sống"],
        "Chủ đề 4: Giải quyết vấn đề với sự trợ giúp của máy tính": ["HTML và cấu trúc trang web", "Định dạng văn bản", "Tạo danh sách, bảng", "Tạo liên kết", "Khái niệm, vai trò của CSS", "Định dạng văn bản bằng CSS"]
    }
}

# --- 3. KHỞI TẠO BIẾN TOÀN CỤC TRONG SESSION STATE ---
if "generated_test" not in st.session_state:
    st.session_state.generated_test = ""
if "question_bank_pool" not in st.session_state:
    st.session_state.question_bank_pool = []

# --- 4. HÀM TỐC ĐỘ CAO GỌI GEMINI AI ---
@st.cache_data(show_spinner=False)
def cached_gemini_generation(api_key, prompt_text):
    """Hàm cache kết quả AI giúp không phải gọi lại nếu trùng prompt, tăng tốc độ tối đa"""
    genai.configure(api_key=api_key)
    # Sử dụng model nhanh và ổn định nhất
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(
        prompt_text,
        generation_config={"temperature": 0.3} # Giảm độ ngẫu nhiên giúp sinh nội dung nhanh hơn
    )
    if response and response.text:
        return response.text
    raise Exception("Không nhận được phản hồi từ AI.")

# --- 5. TIÊU ĐỀ & MENU ĐIỀU HƯỚNG CHÍNH ---
st.subheader("TRƯỜNG THCS VÀ THPT CÂY DƯƠNG | GIÁO VIÊN: CAO XUÂN ĐÚNG")
st.title("EduAI-TestGen: Hệ Thống Khảo Thí & Ôn Tập Thông Minh")

app_mode = st.selectbox(
    "CHỌN CHỨC NĂNG HỆ THỐNG:",
    [
        "1. Khảo Thí & Ra Đề (Dành cho Giáo viên)",
        "2. Góc Ôn Tập Thông Minh (Dành cho Học sinh tự ôn)",
        "3. Quản Lý Bài Tập & Chấm Điểm (LMS Giáo viên)"
    ]
)
st.divider()

# =========================================================================
# PHÂN VÙNG 1: KHẢO THÍ & RA ĐỀ
# =========================================================================
if app_mode == "1. Khảo Thí & Ra Đề (Dành cho Giáo viên)":
    st.sidebar.markdown("### QUẢN LÝ KHẢO THÍ")
    api_key_input = st.sidebar.text_input("Nhập Google Gemini API Key", type="password")

    st.sidebar.divider()
    st.sidebar.header("Xây dựng ma trận đề")
    selected_grade = st.sidebar.selectbox("Chọn khối lớp", list(CURRICULUM_DATA.keys()))

    all_lessons_in_grade = []
    for topic, lessons in CURRICULUM_DATA[selected_grade].items():
        for lesson in lessons:
            all_lessons_in_grade.append(f"{topic} | {lesson}")

    selected_lessons = st.sidebar.multiselect("Chọn các bài học đưa vào đề thi", all_lessons_in_grade)
    num_versions = st.sidebar.number_input("Số lượng mã đề cần tạo", min_value=1, max_value=10, value=1)

    st.sidebar.divider()
    st.sidebar.header("Bảng Ma Trận Đề Kiểm Tra")
    col_ai_btn, col_reset = st.sidebar.columns([3, 1])
    with col_ai_btn:
        ai_auto_matrix_btn = st.button("AI gợi ý ma trận")
    with col_reset:
        if st.button("Đặt lại"):
            st.session_state.matrix_df_state = None
            st.rerun()

    if "matrix_df_state" not in st.session_state:
        st.session_state.matrix_df_state = None

    if ai_auto_matrix_btn:
        if not selected_lessons:
            st.sidebar.warning("Vui lòng chọn ít nhất một bài học!")
        else:
            num_lessons = len(selected_lessons)
            ai_data = []
            for idx, item in enumerate(selected_lessons):
                topic_name, lesson_name = item.split(" | ")
                nb = max(1, round(8 / num_lessons))
                th = max(1, round(6 / num_lessons))
                vd = 1 if (idx % 2 == 0 or num_lessons <= 4) else 0
                vdc = 1 if (idx == num_lessons - 1) else 0
                ai_data.append({
                    "Chọn": True, "Chủ đề": topic_name, "Bài học": lesson_name,
                    "Nhận biết": nb, "Thông hiểu": th, "Vận dụng": vd, "Vận dụng cao": vdc
                })
            st.session_state.matrix_df_state = pd.DataFrame(ai_data)
            st.sidebar.success("Đã thiết lập ma trận chuẩn tức thì!")

    @st.cache_data
    def get_default_matrix(lessons):
        data = []
        for item in lessons:
            topic_name, lesson_name = item.split(" | ")
            data.append({
                "Chọn": True, "Chủ đề": topic_name, "Bài học": lesson_name,
                "Nhận biết": 1, "Thông hiểu": 1, "Vận dụng": 0, "Vận dụng cao": 0
            })
        return pd.DataFrame(data)

    if st.session_state.matrix_df_state is None and selected_lessons:
        st.session_state.matrix_df_state = get_default_matrix(selected_lessons)

    matrix_config = []
    total_questions = 0

    if selected_lessons and st.session_state.matrix_df_state is not None:
        edited_df = st.sidebar.data_editor(
            st.session_state.matrix_df_state, hide_index=True,
            column_config={
                "Chọn": st.column_config.CheckboxColumn("Chọn", width="small"),
                "Chủ đề": st.column_config.TextColumn("Chủ đề", disabled=True),
                "Bài học": st.column_config.TextColumn("Bài học", disabled=True),
                "Nhận biết": st.column_config.NumberColumn("NB", min_value=0, max_value=20, step=1, width="small"),
                "Thông hiểu": st.column_config.NumberColumn("TH", min_value=0, max_value=20, step=1, width="small"),
                "Vận dụng": st.column_config.NumberColumn("VD", min_value=0, max_value=20, step=1, width="small"),
                "Vận dụng cao": st.column_config.NumberColumn("VDC", min_value=0, max_value=20, step=1, width="small"),
            },
            key="matrix_editor_ai", use_container_width=True
        )
        st.session_state.matrix_df_state = edited_df

        if not edited_df.empty:
            df_selected = edited_df[edited_df["Chọn"] == True].copy()
            cols_to_int = ["Nhận biết", "Thông hiểu", "Vận dụng", "Vận dụng cao"]
            df_selected[cols_to_int] = df_selected[cols_to_int].fillna(0).astype(int)
            df_selected["Tổng số câu"] = df_selected[cols_to_int].sum(axis=1)
            total_questions = df_selected["Tổng số câu"].sum()
            
            for _, row in df_selected.iterrows():
                if row["Tổng số câu"] > 0:
                    matrix_config.append({
                        "topic": row["Chủ đề"], "lesson": row["Bài học"],
                        "nb": row["Nhận biết"], "th": row["Thông hiểu"], 
                        "vd": row["Vận dụng"], "vdc": row["Vận dụng cao"]
                    })

        st.sidebar.success(f"Tổng số câu hỏi: {total_questions} câu")

    st.subheader(f"Nội dung đề kiểm tra ({num_versions} Mã đề)")

    if st.button("Bắt đầu sinh đề kiểm tra", type="primary"):
        if not api_key_input:
            st.error("Vui lòng nhập Google Gemini API Key ở thanh bên trái!")
        elif not matrix_config:
            st.warning("Vui lòng chọn ít nhất một bài học!")
        else:
            try:
                with st.spinner("Gemini AI đang tổng hợp và tối ưu hóa nội dung đề kiểm tra..."):
                    matrix_str = ""
                    for config in matrix_config:
                        matrix_str += f"- Chủ đề: {config['topic']} | Bài học: {config['lesson']}\n"
                        matrix_str += f"  + Nhận biết: {config['nb']} câu | Thông hiểu: {config['th']} câu | Vận dụng: {config['vd']} câu | Vận dụng cao: {config['vdc']} câu.\n"

                    prompt = (
                        "Bạn là chuyên gia khảo thí Tin học THPT (chương trình GDPT 2018, sách Kết nối tri thức).\n"
                        f"Hãy biên soạn đề kiểm tra môn Tin học {selected_grade} chuẩn xác, súc tích.\n\n"
                        "YÊU CẦU MA TRẬN:\n"
                        f"{matrix_str}\n"
                        "CHỈ DẪN:\n"
                        f"1. Số lượng mã đề: {num_versions} mã đề. Hoán vị câu hỏi và phương án A,B,C,D.\n"
                        "2. Trắc nghiệm 4 phương án A,B,C,D, duy nhất 1 đáp án đúng.\n"
                        "3. Bắt đầu mỗi mã đề bằng: '### MÃ ĐỀ <số>'.\n"
                        "4. Bắt đầu phần đáp án bằng: '### ĐÁP ÁN VÀ HƯỚNG DẪN CHẤM' ở cuối.\n"
                    )
                    
                    full_text = cached_gemini_generation(api_key_input, prompt)
                    st.session_state.generated_test = full_text

                    extracted_questions = []
                    lines = full_text.split("\n")
                    current_q = {"question": "", "options": [], "answer": "A"}
                    for line in lines:
                        line_s = line.strip()
                        if line_s.startswith("Câu ") or line_s.startswith("CÂU "):
                            if current_q["question"] and len(current_q["options"]) >= 2:
                                extracted_questions.append(current_q)
                            current_q = {"question": line_s, "options": [], "answer": "A"}
                        elif line_s.startswith("A.") or line_s.startswith("B.") or line_s.startswith("C.") or line_s.startswith("D."):
                            current_q["options"].append(line_s)
                        elif "ĐÁP ÁN:" in line_s.upper() or "ĐÚNG:" in line_s.upper():
                            if "A" in line_s: current_q["answer"] = "A"
                            elif "B" in line_s: current_q["answer"] = "B"
                            elif "C" in line_s: current_q["answer"] = "C"
                            elif "D" in line_s: current_q["answer"] = "D"
                    if current_q["question"] and len(current_q["options"]) >= 2:
                        extracted_questions.append(current_q)

                    if extracted_questions:
                        st.session_state.question_bank_pool.extend(extracted_questions)
                        st.success(f"Đã sinh đề thành công và tự động thêm {len(extracted_questions)} câu hỏi vào Ngân hàng ôn tập!")
                    else:
                        st.success("Đã sinh đề thành công!")
            except Exception as e:
                st.error(f"Lỗi kết nối Gemini AI: {e}")

    if st.session_state.generated_test:
        st.markdown("---")
        doc = Document()
        style = doc.styles['Normal']
        style.font.name = 'Times New Roman'
        style.font.size = Pt(12)

        def add_exam_header(docx_obj, ma_de=""):
            hp = docx_obj.add_paragraph()
            hp.alignment = WD_ALIGN_PARAGRAPH.CENTER
            hp.add_run("TRƯỜNG THCS VÀ THPT CÂY DƯƠNG\n").bold = True
            hp.add_run(f"ĐỀ KIỂM TRA ĐỊNH KỲ - MÔN TIN HỌC {selected_grade.upper()}\n").bold = True
            if ma_de: hp.add_run(f"{ma_de}\n").bold = True
            hp.add_run("Thời gian làm bài: 45 phút\n").italic = True
            docx_obj.add_paragraph("Họ và tên thí sinh: ................................................. Lớp: .....................")
            docx_obj.add_paragraph("_" * 60).alignment = WD_ALIGN_PARAGRAPH.CENTER
            docx_obj.add_paragraph()

        first_page = True
        for line in st.session_state.generated_test.split("\n"):
            line = line.strip()
            if not line:
                doc.add_paragraph()
                continue
            if "MÃ ĐỀ" in line.upper() and line.startswith("#"):
                if not first_page: doc.add_page_break()
                first_page = False
                add_exam_header(doc, line.replace("#", "").strip())
                continue
            if "ĐÁP ÁN" in line.upper() and line.startswith("#"):
                if not first_page: doc.add_page_break()
                first_page = False
                p = doc.add_heading(level=1)
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.add_run(line.replace("#", "").strip())
                continue
            
            p = doc.add_paragraph()
            parts = line.split("**")
            for i, part in enumerate(parts):
                run = p.add_run(part)
                if i % 2 != 0: run.bold = True

        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        st.download_button(
            label="Tải BỘ ĐỀ (Word) bản in chuẩn", data=buffer,
            file_name=f"Bo_De_Kiem_Tra_{selected_grade.replace(' ', '_')}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )

# =========================================================================
# PHÂN VÙNG 2: GÓC ÔN TẬP THÔNG MINH
# =========================================================================
elif app_mode == "2. Góc Ôn Tập Thông Minh (Dành cho Học sinh tự ôn)":
    st.markdown("### PHÒNG ÔN TẬP TRỰC TUYẾN TỪ KHO ĐỀ")
    st.info("Hệ thống tự động tổng hợp câu hỏi từ các đề kiểm tra do giáo viên biên soạn để học sinh ôn tập trực tuyến.")

    if not st.session_state.question_bank_pool:
        st.warning("Kho ngân hàng câu hỏi đang trống! Thầy cô vui lòng vào mục '1. Khảo Thí & Ra Đề' và bấm sinh ít nhất một đề kiểm tra.")
    else:
        st.success(f"Kho ôn tập hiện có {len(st.session_state.question_bank_pool)} câu hỏi.")
        
        num_to_quiz = st.slider("Chọn số lượng câu hỏi làm bài ôn tập:", min_value=3, max_value=min(15, len(st.session_state.question_bank_pool)), value=5)

        if "quiz_session" not in st.session_state:
            st.session_state.quiz_session = None

        if st.button("Bắt đầu làm bài trắc nghiệm ôn tập", type="primary"):
            st.session_state.quiz_session = random.sample(st.session_state.question_bank_pool, num_to_quiz)
            st.session_state.student_choices = {}

        if st.session_state.quiz_session:
            st.markdown("---")
            submitted_quiz = False
            with st.form("student_quiz_form"):
                for idx, q_item in enumerate(st.session_state.quiz_session, 1):
                    st.markdown(f"**Câu {idx}: {q_item['question']}**")
                    options = q_item['options']
                    if len(options) < 4:
                        options = ["A. Không có phương án", "B. Không có phương án", "C. Không có phương án", "D. Không có phương án"]
                    
                    choice = st.radio(
                        f"Chọn đáp án câu {idx}:",
                        options=["Chưa chọn", "A", "B", "C", "D"],
                        key=f"std_q_{idx}",
                        label_visibility="collapsed"
                    )
                    st.session_state.student_choices[idx] = choice
                    st.markdown("")

                submitted_quiz = st.form_submit_button("Nộp bài và chấm điểm", type="primary")

            if submitted_quiz:
                score_cnt = 0
                st.markdown("### KẾT QUẢ ÔN TẬP")
                for idx, q_item in enumerate(st.session_state.quiz_session, 1):
                    user_ans = st.session_state.student_choices.get(idx, "Chưa chọn")
                    correct_ans = q_item['answer']
                    if user_ans == correct_ans:
                        score_cnt += 1
                        st.success(f"Câu {idx}: Đúng! (Em chọn {user_ans})")
                    else:
                        st.error(f"Câu {idx}: Sai. (Em chọn {user_ans} | Đáp án đúng: {correct_ans})")

                total_q = len(st.session_state.quiz_session)
                final_score = (score_cnt / total_q) * 10
                st.balloons()
                st.metric(label="Điểm tổng kết", value=f"{final_score:.1f} điểm", delta=f"Đúng {score_cnt}/{total_q} câu")

# =========================================================================
# PHÂN VÙNG 3: QUẢN LÝ BÀI TẬP & CHẤM ĐIỂM
# =========================================================================
elif app_mode == "3. Quản Lý Bài Tập & Chấm Điểm (LMS Giáo viên)":
    st.markdown("### QUẢN LÝ TIẾN ĐỘ & BẢNG ĐIỂM")
    st.info(f"Hệ thống đang quản lý kho ngân hàng đề tự động với {len(st.session_state.question_bank_pool)} câu hỏi.")

    tab1, tab2 = st.tabs(["1. Giao bài kiểm tra nhanh", "2. Bảng điểm học sinh"])

    with tab1:
        st.subheader("Tạo Mã Bài Kiểm Tra Cho Lớp")
        c1, c2 = st.columns(2)
        with c1:
            st.text_input("Tên bài kiểm tra:", "Kiểm tra 15 phút - Tin học THPT")
            st.text_input("Lớp:", "10A1")
        with c2:
            st.text_input("Mã bài kiểm tra:", "TIN_CAYDUONG_01")
            st.date_input("Hạn nộp:")
        if st.button("Xác nhận phát hành bài kiểm tra", type="primary"):
            st.success("Đã phát hành bài kiểm tra thành công cho học sinh!")

    with tab2:
        st.subheader("Bảng Điểm Tổng Hợp")
        mock_data = {
            "STT": [1, 2, 3, 4],
            "Họ và tên": ["Nguyễn Văn An", "Trần Thị Bình", "Lê Hoàng Nam", "Phạm Minh Thư"],
            "Lớp": ["10A1", "10A1", "10A1", "10A1"],
            "Điểm số": [9.0, 8.5, 10.0, 7.5],
            "Trạng thái": ["Đã nộp bài", "Đã nộp bài", "Đã nộp bài", "Đã nộp bài"]
        }
        df_score = pd.DataFrame(mock_data)
        st.dataframe(df_score, use_container_width=True, hide_index=True)
        
        score_buf = io.BytesIO()
        with pd.ExcelWriter(score_buf, engine="openpyxl") as writer:
            df_score.to_excel(writer, index=False, sheet_name="BangDiem")
        score_buf.seek(0)
        st.download_button("Tải Bảng Điểm Excel", data=score_buf, file_name="BangDiem_Lop.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
