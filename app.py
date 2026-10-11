import io
import google.generativeai as genai
import streamlit as st
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

# --- 1. CẤU HÌNH GIAO DIỆN TRANG WEB ---
st.set_page_config(
    page_title="EduAI-TestGen - Hệ Thống Sinh Đề Tổng Hợp",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 EduAI-TestGen: Hệ Thống Sinh Đề Kiểm Tra Giữa Kì / Cuối Kì")
st.markdown(
    "Ứng dụng hỗ trợ giáo viên Tin học xây dựng ma trận và tạo đề kiểm tra tổng hợp "
    "nhiều bài học bám sát Chương trình GDPT 2018 (Sách Kết nối tri thức)."
)
st.divider()

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

# --- 3. THANH BÊN (SIDEBAR): CẤU HÌNH API & MA TRẬN ĐA BÀI HỌC ---
st.sidebar.header("⚙️ Cấu hình hệ thống & AI")

api_key_input = st.sidebar.text_input(
    "Nhập Google Gemini API Key của thầy/cô",
    type="password",
    help="Dán mã API Key lấy từ Google AI Studio vào đây",
)

st.sidebar.divider()
st.sidebar.header("📚 Xây dựng ma trận đề kiểm tra")

# Chọn khối lớp
selected_grade = st.sidebar.selectbox("Chọn khối lớp", list(CURRICULUM_DATA.keys()))

# Tạo danh sách tất cả các bài học của khối lớp đó để chọn nhiều bài
all_lessons_in_grade = []
for topic, lessons in CURRICULUM_DATA[selected_grade].items():
    for lesson in lessons:
        all_lessons_in_grade.append(f"{topic} | {lesson}")

selected_lessons = st.sidebar.multiselect(
    "Chọn các bài học đưa vào đề thi (Có thể chọn nhiều bài)", 
    all_lessons_in_grade,
    help="Ví dụ: Chọn 5 bài học để tạo đề kiểm tra Giữa kì"
)

# Lặp qua các bài học đã chọn để thiết lập ma trận chi tiết cho từng bài
matrix_config = []
total_questions = 0

if selected_lessons:
    st.sidebar.markdown("### 📊 Chi tiết ma trận từng bài học")
    for item in selected_lessons:
        topic_name, lesson_name = item.split(" | ")
        
        with st.sidebar.expander(f"Cấu hình: {lesson_name}", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                nb = st.number_input("Nhận biết", min_value=0, max_value=20, value=1, key=f"nb_{item}")
                vd = st.number_input("Vận dụng", min_value=0, max_value=20, value=0, key=f"vd_{item}")
            with col2:
                th = st.number_input("Thông hiểu", min_value=0, max_value=20, value=1, key=f"th_{item}")
                vdc = st.number_input("Vận dụng cao", min_value=0, max_value=20, value=0, key=f"vdc_{item}")
            
            matrix_config.append({
                "topic": topic_name,
                "lesson": lesson_name,
                "nb": nb, "th": th, "vd": vd, "vdc": vdc
            })
            total_questions += (nb + th + vd + vdc)

    st.sidebar.success(f"**Tổng số câu hỏi trong đề: {total_questions} câu**")

# --- 4. KHU VỰC CHÍNH: GỌI GEMINI AI SINH ĐỀ ---
st.subheader("📋 Nội dung đề kiểm tra tổng hợp")

if "generated_test" not in st.session_state:
    st.session_state.generated_test = ""

if st.button("🚀 Bắt đầu sinh đề kiểm tra bám sát Ma trận", type="primary"):
    if not api_key_input:
        st.error("⚠️ Thầy/cô vui lòng nhập Google Gemini API Key ở thanh bên trái!")
    elif not matrix_config:
        st.warning("⚠️ Thầy/cô vui lòng chọn ít nhất một bài học để đưa vào đề thi!")
    else:
        try:
            with st.spinner("🤖 Gemini AI đang phân tích ma trận và biên soạn đề..."):
                genai.configure(api_key=api_key_input)
                model = genai.GenerativeModel("gemini-3.8-flash")

                matrix_str = ""
                for config in matrix_config:
                    matrix_str += f"- Chủ đề: {config['topic']} | Bài học: {config['lesson']}\n"
                    matrix_str += f"  + Nhận biết: {config['nb']} câu | Thông hiểu: {config['th']} câu | Vận dụng: {config['vd']} câu | Vận dụng cao: {config['vdc']} câu.\n"

                prompt = f"""
                Bạn là một chuyên gia khảo thí và giáo viên Tin học THPT xuất sắc theo Chương trình GDPT 2018 (sách Kết nối tri thức).
                Hãy biên soạn một đề kiểm tra định kỳ môn Tin học cho {selected_grade}.
                
                YÊU CẦU MA TRẬN BẮT BUỘC (TUÂN THỦ TUYỆT ĐỐI SỐ LƯỢNG NÀY):
                {matrix_str}

                CHỈ DẪN BIÊN SOẠN:
                1. Nội dung câu hỏi phải bám sát chính xác ngữ cảnh và yêu cầu cần đạt của từng bài học tương ứng trong sách Kết nối tri thức.
                2. Câu hỏi Trắc nghiệm (Nhận biết, Thông hiểu): Phải có 4 phương án A, B, C, D. Chỉ có duy nhất 1 đáp án đúng. Các phương án nhiễu phải hợp lý, không mơ hồ. Tuyệt đối KHÔNG lạm dụng phương án "Tất cả các đáp án trên".
                3. Câu hỏi Lập trình/Thực hành (Vận dụng, Vận dụng cao): Ưu tiên sử dụng ngôn ngữ Python/C++. Phải mô tả rõ yêu cầu bài toán, dữ liệu vào (Input), dữ liệu ra (Output) và có test-case mẫu.
                4. KHÔNG tiết lộ đáp án ngay bên cạnh câu hỏi trong phần đề thi dành cho học sinh.
                5. PHẦN ĐÁP ÁN VÀ HƯỚNG DẪN CHẤM: Phải được tách riêng và đặt ở cuối cùng của văn bản. Lời giải lập trình phải đúng cú pháp, tối ưu về thuật toán (thời gian, bộ nhớ).

                Trình bày kết quả chuyên nghiệp bằng định dạng Markdown.
                """

                # Gọi API với chế độ STREAM (Trực tiếp)
                response = model.generate_content(prompt, stream=True)
                
                # Sử dụng bộ xử lý luồng gốc của Streamlit siêu mượt
                def stream_parser():
                    for chunk in response:
                        if chunk.text:
                            yield chunk.text
                            
                # In trực tiếp ra màn hình với tốc độ tối đa
                full_text = st.write_stream(stream_parser)
                st.session_state.generated_test = full_text
                
                st.success("🎉 Gemini AI đã sinh thành công đề kiểm tra tổng hợp!")

        except Exception as e:
            st.error(f"❌ Lỗi kết nối với Gemini AI: {e}")

# --- 5. TẠO FILE WORD CHUẨN FORM GIÁO DỤC ---
if st.session_state.generated_test:
    st.markdown("---")
    
    doc = Document()
    
    # Thiết lập Font chữ mặc định toàn văn bản là Times New Roman, cỡ 12
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(12)

    # 1. Phần Tiêu đề Trường / Đề thi (Căn giữa)
    header_p = doc.add_paragraph()
    header_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    run_truong = header_p.add_run("TRƯỜNG THPT ................................\n")
    run_truong.bold = True
    run_truong.font.size = Pt(13)
    
    run_de = header_p.add_run(f"ĐỀ KIỂM TRA ĐỊNH KỲ - MÔN TIN HỌC {selected_grade.upper()}\n")
    run_de.bold = True
    run_de.font.size = Pt(14)
    
    run_tg = header_p.add_run("Thời gian làm bài: 45 phút (Không kể thời gian phát đề)\n")
    run_tg.italic = True
    run_tg.font.size = Pt(12)

    # 2. Phần Thông tin Thí sinh
    doc.add_paragraph("Họ và tên thí sinh: ................................................................. Lớp: .....................")
    doc.add_paragraph("Số báo danh: ..........................................................................................................")
    
    # Đường kẻ ngang phân cách
    doc.add_paragraph("_" * 60).alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph() # Dòng trống tạo khoảng cách
    
    # 3. Xử lý nội dung Markdown từ AI sang Word
    for line in st.session_state.generated_test.split("\n"):
        line = line.strip()
        if not line:
            doc.add_paragraph()
            continue
            
        if line.startswith("# "):
            p = doc.add_heading(level=1)
            run = p.add_run(line.replace("# ", ""))
            run.font.name = 'Times New Roman'
        elif line.startswith("## "):
            p = doc.add_heading(level=2)
            run = p.add_run(line.replace("## ", ""))
            run.font.name = 'Times New Roman'
        elif line.startswith("### "):
            p = doc.add_heading(level=3)
            run = p.add_run(line.replace("### ", ""))
            run.font.name = 'Times New Roman'
        else:
            p = doc.add_paragraph()
            # Bóc tách để giữ được chữ in đậm
            parts = line.split("**")
            for i, part in enumerate(parts):
                run = p.add_run(part)
                run.font.name = 'Times New Roman'
                if i % 2 != 0: 
                    run.bold = True

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    st.download_button(
        label="📥 Tải đề kiểm tra định dạng Word (Bản in chuẩn)",
        data=buffer,
        file_name=f"De_Kiem_Tra_{selected_grade.replace(' ', '_')}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
