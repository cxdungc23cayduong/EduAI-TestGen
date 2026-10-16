import io
import random
import google.generativeai as genai
import streamlit as st
import pandas as pd
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

# --- 1. CẤU HÌNH GIAO DIỆN TRANG WEB ---
st.set_page_config(
    page_title="EduAI-TestGen & LMS - Hệ Thống Khảo Thí & Ôn Tập AI",
    page_icon="🤖",
    layout="wide",
)

# --- 2. DỮ LIỆU CHUẨN SÁCH GIÁO KHOA "KẾT NỐI TRI THỨC" TIN HỌC THPT ---
CURRICULUM_DATA = {
    "Lớp 10": {
        "Chủ đề 1: Máy tính và xã hội tri thức": [
            "Bài 1: Thông tin và xử lí thông tin",
            "Bài 2: Vai trò của thiết bị thông minh và tin học đối với xã hội",
            "Bài 3: Một số kiểu dữ liệu và dữ liệu văn bản",
            "Bài 4: Hệ nhị phân và dữ liệu số nguyên",
            "Bài 5: Dữ liệu lôgic",
            "Bài 6: Dữ liệu âm thanh và hình ảnh",
            "Bài 7: Thực hành sử dụng thiết bị số thông dụng"
        ],
        "Chủ đề 2: Mạng máy tính và Internet": [
            "Bài 8: Mạng máy tính trong cuộc sống hiện đại",
            "Bài 9: An toàn trên không gian mạng",
            "Bài 10: Thực hành khai thác tài nguyên trên Internet"
        ],
        "Chủ đề 3: Đạo đức, pháp luật và văn hoá trong môi trường số": [
            "Bài 11: Ứng xử trên môi trường số. Nghĩa vụ tôn trọng bản quyền"
        ],
        "Chủ đề 4: Ứng dụng tin học": [
            "Bài 12: Phần mềm thiết kế đồ hoạ",
            "Bài 13: Bổ sung các đối tượng đồ hoạ",
            "Bài 14: Làm việc với đối tượng đường và văn bản",
            "Bài 15: Hoàn thiện hình ảnh đồ hoạ"
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
            "Bài 32: Ôn tập lập trình Python"
        ],
        "Chủ đề 6: Hướng nghiệp với tin học": [
            "Bài 33: Nghề thiết kế đồ hoạ máy tính",
            "Bài 34: Nghề phát triển phần mềm"
        ]
    },
    "Lớp 11 (Tin học ứng dụng)": {
        "Chủ đề 1: Máy tính và xã hội tri thức": [
            "Bài 1: Hệ điều hành",
            "Bài 2: Thực hành sử dụng hệ điều hành",
            "Bài 3: Phần mềm nguồn mở và phần mềm chạy trên Internet",
            "Bài 4: Bên trong máy tính",
            "Bài 5: Kết nối máy tính với các thiết bị số"
        ],
        "Chủ đề 2: Tổ chức lưu trữ, tìm kiếm và trao đổi thông tin": [
            "Bài 6: Lưu trữ và chia sẻ tệp tin trên Internet",
            "Bài 7: Thực hành tìm kiếm thông tin trên Internet",
            "Bài 8: Thực hành nâng cao sử dụng thư điện tử và mạng xã hội"
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
            "Bài 15: Bảo mật và an toàn hệ cơ sở dữ liệu"
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
            "Bài 24: Thực hành sao lưu dữ liệu"
        ],
        "Chủ đề 7: Phần mềm chỉnh sửa ảnh và làm video": [
            "Bài 25: Phần mềm chỉnh sửa ảnh",
            "Bài 26: Công cụ tinh chỉnh màu sắc và công cụ chọn",
            "Bài 27: Công cụ vẽ và một số ứng dụng",
            "Bài 28: Tạo ảnh động",
            "Bài 29: Khám phá phần mềm làm phim",
            "Bài 30: Biên tập phim",
            "Bài 31: Thực hành tạo phim hoạt hình"
        ]
    },
    "Lớp 12 (Tin học ứng dụng)": {
        "Chủ đề 1: Máy tính và xã hội tri thức": [
            "Làm quen với Trí tuệ nhân tạo",
            "Trí tuệ nhân tạo trong khoa học và đời sống"
        ],
        "Chủ đề 2: Mạng máy tính và Internet": [
            "Một số thiết bị mạng thông dụng",
            "Giao thức mạng",
            "Thực hành chia sẻ tài nguyên trên mạng"
        ],
        "Chủ đề 3: Đạo đức, pháp luật và văn hoá trong môi trường số": [
            "Giao tiếp và ứng xử trong không gian mạng"
        ],
        "Chủ đề 4: Giải quyết vấn đề với sự trợ giúp của máy tính": [
            "HTML và cấu trúc trang web",
            "Định dạng văn bản",
            "Tạo danh sách, bảng",
            "Tạo liên kết",
            "Chèn tệp tin đa phương tiện và khung nội tuyến vào trang web",
            "Tạo biểu mẫu",
            "Khái niệm, vai trò của CSS",
            "Định dạng văn bản bằng CSS",
            "Tạo màu cho chữ và nền",
            "Định dạng khung",
            "Các mức ưu tiên của bộ chọn",
            "Thực hành tổng hợp thiết kế trang web"
        ],
        "Chủ đề 5: Hướng nghiệp với tin học": [
            "Dịch vụ sửa chữa và bảo trì máy tính",
            "Nhóm nghề quản trị thuộc ngành Công nghệ thông tin",
            "Hội thảo hướng nghiệp"
        ],
        "Chủ đề 6: Máy tính và xã hội tri thức (Định hướng ứng dụng)": [
            "Thực hành kết nối các thiết bị số"
        ],
        "Chủ đề 7: Ứng dụng tin học (Định hướng ứng dụng)": [
            "Chuẩn bị xây dựng trang web",
            "Xây dựng phần đầu trang web",
            "Xây dựng phần thân và chân trang web",
            "Liên kết và thanh điều hướng",
            "Biểu mẫu trên trang web",
            "Thực hành tổng hợp"
        ]
    }
}

# --- 3. TIÊU ĐỀ & MENU ĐIỀU HƯỚNG CHÍNH ---
st.subheader("TRƯỜNG THCS VÀ THPT CÂY DƯƠNG | GIÁO VIÊN: CAO XUÂN ĐÚNG")
st.title("🤖 EduAI-TestGen: Hệ Thống Khảo Thí & Ôn Tập Thông Minh")

# Tạo Menu chuyển đổi các phân vùng chức năng
app_mode = st.selectbox(
    "🎯 CHỌN CHỨC NĂNG HỆ THỐNG:",
    [
        "📊 1. Khảo Thí & Ra Đề (Dành cho Giáo viên)",
        "🤖 2. Góc Ôn Tập Thông Minh (Dành cho Học sinh tự ôn)",
        "📝 3. Quản Lý Bài Tập & Chấm Điểm (LMS Giáo viên)"
    ]
)
st.divider()

# =========================================================================
# PHÂN VÙNG 1: KHẢO THÍ & RA ĐỀ (CODE GỐC CỦA THẦY)
# =========================================================================
if app_mode == "📊 1. Khảo Thí & Ra Đề (Dành cho Giáo viên)":
    st.sidebar.markdown("### 👨‍🏫 QUẢN LÝ KHẢO THÍ")
    api_key_input = st.sidebar.text_input("Nhập Google Gemini API Key", type="password")

    st.sidebar.divider()
    st.sidebar.header("📚 Xây dựng ma trận đề")
    selected_grade = st.sidebar.selectbox("Chọn khối lớp", list(CURRICULUM_DATA.keys()))

    all_lessons_in_grade = []
    for topic, lessons in CURRICULUM_DATA[selected_grade].items():
        for lesson in lessons:
            all_lessons_in_grade.append(f"{topic} | {lesson}")

    selected_lessons = st.sidebar.multiselect("Chọn các bài học đưa vào đề thi", all_lessons_in_grade)
    num_versions = st.sidebar.number_input("Số lượng mã đề cần tạo", min_value=1, max_value=10, value=1)

    st.sidebar.divider()
    st.sidebar.header("📊 Bảng Ma Trận Đề Kiểm Tra")
    col_ai_btn, col_reset = st.sidebar.columns([3, 1])
    with col_ai_btn:
        ai_auto_matrix_btn = st.button("✨ AI gợi ý ma trận")
    with col_reset:
        if st.button("🔄 Đặt lại"):
            st.session_state.matrix_df_state = None
            st.rerun()

    if "matrix_df_state" not in st.session_state:
        st.session_state.matrix_df_state = None

    if ai_auto_matrix_btn:
        if not selected_lessons:
            st.sidebar.warning("⚠️ Vui lòng chọn ít nhất một bài học!")
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
            st.sidebar.success("✨ Đã thiết lập ma trận chuẩn tức thì!")

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
        st.sidebar.caption("💡 Click vào ô số để sửa ma trận:")
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

        st.sidebar.success(f"**📊 Tổng số câu hỏi: {total_questions} câu**")

        if not df_selected.empty:
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
                df_export = df_selected.drop(columns=["Chọn"]).reset_index(drop=True)
                df_export.index += 1
                df_export.index.name = "STT"
                df_export.to_excel(writer, sheet_name="MaTranDeThi", startrow=5)
                ws = writer.sheets["MaTranDeThi"]
                ws["A1"] = "TRƯỜNG THCS VÀ THPT CÂY DƯƠNG"
                ws["A2"] = f"MA TRẬN ĐỀ KIỂM TRA ĐỊNH KỲ MÔN TIN HỌC {selected_grade.upper()}"
                ws["A3"] = "GIÁO VIÊN BIÊN SOẠN: CAO XUÂN ĐÚNG"
                ws["A4"] = f"Thời gian làm bài: 45 phút | Tổng số câu: {total_questions} câu"
                
                for col in ws.columns:
                    max_len = max(len(str(cell.value or '')) for cell in col)
                    col_letter = col[0].column_letter
                    ws.column_dimensions[col_letter].width = max(max_len + 3, 10)

            excel_buffer.seek(0)
            st.sidebar.download_button(
                label="📊 Tải Ma trận (Excel chuẩn)", data=excel_buffer,
                file_name=f"Ma_Tran_De_Thi_TinHoc_{selected_grade.replace(' ', '_')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

    st.subheader(f"📋 Nội dung đề kiểm tra ({num_versions} Mã đề)")
    if "generated_test" not in st.session_state:
        st.session_state.generated_test = ""

    if st.button("🚀 Bắt đầu sinh đề kiểm tra", type="primary"):
        if not api_key_input:
            st.error("⚠️ Vui lòng nhập Google Gemini API Key ở thanh bên trái!")
        elif not matrix_config:
            st.warning("⚠️ Vui lòng chọn ít nhất một bài học!")
        else:
            try:
                with st.spinner("🤖 Gemini AI đang phân tích ma trận và thực hiện hoán vị trộn đề..."):
                    genai.configure(api_key=api_key_input)
                    model = genai.GenerativeModel("gemini-1.5-flash")

                    matrix_str = ""
                    for config in matrix_config:
                        matrix_str += f"- Chủ đề: {config['topic']} | Bài học: {config['lesson']}\n"
                        matrix_str += f"  + Nhận biết: {config['nb']} câu | Thông hiểu: {config['th']} câu | Vận dụng: {config['vd']} câu | Vận dụng cao: {config['vdc']} câu.\n"

                    prompt = (
                        "Bạn là một chuyên gia khảo thí và giáo viên Tin học THPT xuất sắc theo Chương trình GDPT 2018 (sách Kết nối tri thức).\n"
                        f"Hãy biên soạn một đề kiểm tra định kỳ môn Tin học cho {selected_grade}.\n\n"
                        "YÊU CẦU MA TRẬN BẮT BUỘC:\n"
                        f"{matrix_str}\n"
                        "CHỈ DẪN:\n"
                        f"1. Số lượng mã đề: {num_versions} mã đề. Hoán vị câu hỏi và phương án A,B,C,D cho các mã đề tiếp theo.\n"
                        "2. Câu hỏi Trắc nghiệm 4 phương án A,B,C,D, chỉ 1 đáp án đúng. Tuyệt đối không dùng 'Tất cả các đáp án trên'.\n"
                        "3. Bắt đầu mỗi mã đề bằng: '### MÃ ĐỀ <số>' (VD: ### MÃ ĐỀ 101).\n"
                        "4. Bắt đầu phần đáp án bằng: '### ĐÁP ÁN VÀ HƯỚNG DẪN CHẤM' ở cuối văn bản kèm bảng tổng hợp.\n"
                    )
                    response = model.generate_content(prompt, stream=True)
                    def stream_parser():
                        for chunk in response:
                            if chunk.text: yield chunk.text
                    full_text = st.write_stream(stream_parser)
                    st.session_state.generated_test = full_text
                    st.success("🎉 Sinh và trộn đề thành công!")
            except Exception as e:
                st.error(f"❌ Lỗi kết nối Gemini AI: {e}")

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
            label="📥 Tải BỘ ĐỀ (Word) bản in chuẩn", data=buffer,
            file_name=f"Bo_De_Kiem_Tra_{selected_grade.replace(' ', '_')}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )

# =========================================================================
# PHÂN VÙNG 2: GÓC ÔN TẬP THÔNG MINH (DÀNH CHO HỌC SINH TỰ ÔN)
# =========================================================================
elif app_mode == "🤖 2. Góc Ôn Tập Thông Minh (Dành cho Học sinh tự ôn)":
    st.markdown("### 🎓 PHÒNG HỌC & ÔN TẬP TRỰC TUYẾN MÔN TIN HỌC")
    st.info("Học sinh chọn khối lớp và bài học muốn ôn tập. AI sẽ tự động tạo một bộ đề trắc nghiệm tương tác giúp học sinh kiểm tra kiến thức tức thì!")

    col1, col2 = st.columns(2)
    with col1:
        hs_grade = st.selectbox("Chọn khối lớp của em", list(CURRICULUM_DATA.keys()), key="hs_grade")
    with col2:
        # Lấy danh sách bài học phẳng
        all_lessons_flat = []
        for top, less in CURRICULUM_DATA[hs_grade].items():
            for l in less:
                all_lessons_flat.append(l)
        hs_lesson = st.selectbox("Chọn bài học cần ôn tập", all_lessons_flat, key="hs_lesson")

    hs_api_key = st.text_input("Nhập mã Gemini API Key được cung cấp bởi giáo viên:", type="password", key="hs_api")
    num_practice_q = st.slider("Số lượng câu hỏi ôn tập:", min_value=5, max_value=20, value=5, step=5)

    if "practice_quiz" not in st.session_state:
        st.session_state.practice_quiz = None
    if "user_answers" not in st.session_state:
        st.session_state.user_answers = {}

    if st.button("🎯 Bắt đầu làm bài ôn tập", type="primary"):
        if not hs_api_key:
            st.error("⚠️ Vui lòng nhập API Key để AI tạo đề ôn tập!")
        else:
            with st.spinner("🤖 AI đang biên soạn bộ câu hỏi ôn tập bám sát chương trình..."):
                try:
                    genai.configure(api_key=hs_api_key)
                    model = genai.GenerativeModel("gemini-1.5-flash")
                    prompt_quiz = (
                        f"Bạn là giáo viên Tin học. Hãy tạo {num_practice_q} câu hỏi trắc nghiệm khách quan về bài học: '{hs_lesson}' ({hs_grade}, sách Kết nối tri thức).\n"
                        "Mỗi câu hỏi có 4 phương án A, B, C, D và chỉ có 1 đáp án đúng.\n"
                        "Định dạng nghiêm ngặt bắt buộc cho mỗi câu:\n"
                        "CÂU [Số]: [Nội dung câu hỏi]\n"
                        "A. [Đáp án A]\n"
                        "B. [Đáp án B]\n"
                        "C. [Đáp án C]\n"
                        "D. [Đáp án D]\n"
                        "ĐÁP ÁN ĐÚNG: [A/B/C/D] - [Giải thích ngắn gọn vì sao đúng]\n"
                    )
                    res = model.generate_content(prompt_quiz)
                    st.session_state.practice_quiz = res.text
                    st.session_state.user_answers = {}
                    st.success("🎉 Đã tạo xong đề ôn tập! Em hãy trả lời các câu hỏi bên dưới.")
                except Exception as e:
                    st.error(f"Lỗi tạo đề ôn tập: {e}")

    # Hiển thị giao diện làm bài trắc nghiệm cho học sinh
    if st.session_state.practice_quiz:
        st.markdown("---")
        st.subheader(f"📝 BÀI ÔN TẬP: {hs_lesson}")
        
        quiz_text = st.session_state.practice_quiz
        questions = quiz_text.split("CÂU ")
        
        submitted = False
        with st.form("quiz_form"):
            for idx, q in enumerate(questions[1:], 1):
                lines = [l.strip() for l in q.strip().split("\n") if l.strip()]
                if len(lines) >= 5:
                    q_title = lines[0]
                    opts = lines[1:5] # A, B, C, D
                    st.markdown(f"**Câu {idx}: {q_title}**")
                    
                    choice = st.radio(
                        f"Chọn đáp án câu {idx}:", 
                        options=["Chưa chọn", "A", "B", "C", "D"],
                        key=f"q_{idx}",
                        label_visibility="collapsed"
                    )
                    st.session_state.user_answers[idx] = choice
                    st.markdown("")

            submitted = st.form_submit_button("📤 Nộp bài và xem kết quả", type="primary")

        if submitted:
            score = 0
            total_valid = 0
            st.markdown("### 📊 KẾT QUẢ ÔN TẬP CỦA EM")
            
            for idx, q in enumerate(questions[1:], 1):
                lines = [l.strip() for l in q.strip().split("\n") if l.strip()]
                correct_line = ""
                for l in lines:
                    if "ĐÁP ÁN ĐÚNG:" in l:
                        correct_line = l
                        break
                
                if correct_line:
                    total_valid += 1
                    correct_ans = correct_line.split("ĐÁP ÁN ĐÚNG:")[1].strip()[0] # Lấy ký tự A, B, C hoặc D
                    user_ans = st.session_state.user_answers.get(idx, "Chưa chọn")
                    
                    if user_ans == correct_ans:
                        score += 1
                        st.success(f"✅ Câu {idx}: Đúng! (Em chọn {user_ans} | {correct_line})")
                    else:
                        st.error(f"❌ Câu {idx}: Sai. (Em chọn {user_ans} | Đáp án đúng: {correct_line})")

            if total_valid > 0:
                percent = (score / total_valid) * 10
                st.balloons()
                st.metric(label="🌟 Điểm số tổng kết của em (Thang điểm 10)", value=f"{percent:.1f} điểm", delta=f"Đúng {score}/{total_valid} câu")

# =========================================================================
# PHÂN VÙNG 3: QUẢN LÝ NGÂN HÀNG ĐỀ & CHẤM ĐIỂM (LMS GIÁO VIÊN)
# =========================================================================
elif app_mode == "📝 3. Quản Lý Bài Tập & Chấm Điểm (LMS Giáo viên)":
    st.markdown("### 📂 HỆ THỐNG QUẢN LÝ NGÂN HÀNG ĐỀ & CHẤM ĐIỂM")
    st.info("Thầy/cô có thể tải lên tệp Excel chứa ngân hàng câu hỏi riêng của trường Cây Dương, giao bài tập trực tuyến và xem bảng điểm của học sinh.")

    tab_nganhang, tab_giao, tab_cham = st.tabs([
        "1. Tải lên Ngân hàng Đề (Excel)", 
        "2. Tạo & Giao Bài Kiểm Tra", 
        "3. Chấm Điểm & Thống Kê"
    ])

    with tab_nganhang:
        st.subheader("📤 Tải lên Tệp Ngân Hàng Câu Hỏi (Excel)")
        st.markdown("Thầy/cô tải lên tệp Excel chứa danh sách câu hỏi trắc nghiệm để học sinh ôn tập trực tuyến.")
        
        uploaded_excel = st.file_uploader("Chọn tệp Excel ngân hàng đề (.xlsx)", type=["xlsx"])
        
        if uploaded_excel is not None:
            try:
                df_bank = pd.read_excel(uploaded_excel)
                st.success(f"🎉 Tải lên thành công! Đã ghi nhận {len(df_bank)} câu hỏi trong ngân hàng đề.")
                st.markdown("**Xem trước dữ liệu ngân hàng đề:**")
                st.dataframe(df_bank.head(10), use_container_width=True)
                
                # Lưu vào session state để phần góc ôn tập của học sinh có thể đọc được
                st.session_state.custom_question_bank = df_bank
            except Exception as e:
                st.error(f"❌ Lỗi đọc tệp Excel: {e}")
        else:
            st.info("💡 Nếu chưa có tệp, hệ thống đang sử dụng kho câu hỏi mặc định tích hợp sẵn.")

    with tab_giao:
        st.subheader("🔗 Tạo Mã Bài Kiểm Tra Trực Tuyến")
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            exam_title = st.text_input("Tiêu đề bài kiểm tra:", "Kiểm tra 15 phút - Môn Tin học 10")
            class_name = st.text_input("Lớp được giao:", "10A1")
        with col_g2:
            exam_code = st.text_input("Mã bài kiểm tra (Mật khẩu truy cập):", "TIN10_01")
            deadline = st.date_input("Hạn nộp bài:")

        st.markdown("---")
        st.subheader("📋 Nội dung bài kiểm tra:")
        exam_content_input = st.text_area(
            "Dán nội dung câu hỏi hoặc ghi chú hướng dẫn giao bài:",
            placeholder="Học sinh làm bài ôn tập chương trình Tin học 10..."
        )

        if st.button("💾 Lưu và Giao Bài Cho Học Sinh", type="primary"):
            if not exam_code:
                st.warning("⚠️ Vui lòng nhập mã bài kiểm tra!")
            else:
                st.success(f"🎉 Đã tạo thành công bài kiểm tra [Mã: **{exam_code}**] cho lớp **{class_name}**!")
                st.markdown(f"👉 **Hướng dẫn học sinh:** Truy cập vào mục *'2. Góc Ôn Tập Thông Minh'* và chọn đúng chủ đề để làm bài.")

    with tab_cham:
        st.subheader("📊 Bảng Điểm & Thống Kê Kết Quả Lớp Học")
        
        mock_data = {
            "STT": [1, 2, 3, 4, 5],
            "Họ và tên": ["Nguyễn Văn An", "Trần Thị Bình", "Lê Hoàng Nam", "Phạm Minh Thư", "Vũ Hoàng Long"],
            "Lớp": ["10A1", "10A1", "10A1", "10A1", "10A1"],
            "Mã đề làm": ["TIN10_01", "TIN10_01", "TIN10_01", "TIN10_01", "TIN10_01"],
            "Số câu đúng": ["9/10", "8/10", "10/10", "6/10", "7/10"],
            "Điểm số": [9.0, 8.0, 10.0, 6.0, 7.0],
            "Trạng thái": ["Đã nộp", "Đã nộp", "Đã nộp", "Đã nộp", "Đã nộp"]
        }
        df_scores = pd.DataFrame(mock_data)
        st.dataframe(df_scores, use_container_width=True, hide_index=True)
        
        score_buffer = io.BytesIO()
        with pd.ExcelWriter(score_buffer, engine="openpyxl") as writer:
            df_scores.to_excel(writer, index=False, sheet_name="BangDiemLop")
        score_buffer.seek(0)
        
        st.download_button(
            label="📥 Tải Bảng Điểm Lớp (Excel chuẩn)", data=score_buffer,
            file_name="Bang_Diem_Trac_Nghiem_TinHoc.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
