# Mini AI Study Assistant — Modular AI Agents Lab

Một project nhỏ **bằng Python** để hiểu nội dung 3 module của khóa IBM **Fundamentals of Building AI Agents**. Mở trong **VS Code trên Windows**.

**Chạy được OFFLINE (không API key, không cài thêm thư viện)**. Khi đã hiểu phần lõi, bạn có thể thử LCEL và AI Agent thật với LangChain.

> **Quan trọng:** Offline mode dùng một bộ định tuyến bằng luật (`if/regex`) **mô phỏng** tool calling, KHÔNG phải LLM. Chỉ `--mode agent` dùng LLM thật để tự quyết định gọi công cụ. Dữ liệu điểm là giả lập.

## 1. Cấu trúc project

```text
ai_agent_course_lab/
├── main.py                      # CLI: điểm vào chương trình
├── START_HERE.bat               # Double-click để chạy demo trên Windows
├── course_lab/
│   ├── database.py              # SQLite + CSV: data layer
│   ├── tools.py                 # Calculator, SQL, Notes, Chart tools
│   ├── manual.py                # Tool schema + JSON validation + manual calling
│   ├── visualization.py         # Tạo biểu đồ SVG không dùng thư viện ngoài
│   ├── lcel_demo.py             # LCEL: RunnableLambda | RunnableLambda
│   ├── manual_llm.py            # LLM thật + app tự chạy tools (bind_tools)
│   └── langchain_agent.py       # Agent thật: create_agent + @tool + Memory
├── data/study_scores.csv        # 12 dòng dữ liệu minh họa
├── outputs/                     # Kết quả biểu đồ (tạo khi chạy)
├── tests/test_course_lab.py     # Unit tests
├── NOTION_NOTES.md              # Ghi chú tiếng Anh cho Notion
└── requirements-optional.txt    # Thư viện thêm cho LCEL / real LLM
```

## 2. Chạy ngay (chỉ cần Python)

Trong VS Code: `File -> Open Folder` chọn thư mục `ai_agent_course_lab`, mở Terminal (PowerShell). Hoặc **nhấp đúp `START_HERE.bat`** để chạy demo ngay trên Windows.

```powershell
python --version
python main.py --demo
```

Nếu máy Windows dùng Python Launcher, thay `python` bằng `py`.

**Kết quả demo**: toán `12*5 = 60`, SQL điểm trung bình `8.46`, bảng xếp hạng, tra cứu ghi chú, file biểu đồ `outputs/course_averages.svg`. Nhấp đúp file SVG để xem bằng trình duyệt.

Để tự nhập lệnh:

```powershell
python main.py --mode offline
```

Sau đó gõ lần lượt:

```text
calc 12 * 5
avg
top 3
grades
chart
notes tool calling
remember An
whoami
tools
exit
```

Lưu ý offline router hiểu các **lệnh cố định**, không hiểu mọi câu tiếng Việt tự nhiên.

## 3. Chạy LCEL (không cần API key)

Cài thư viện tùy chọn:

```powershell
python -m pip install -r requirements-optional.txt
python main.py --mode lcel
```

Gõ `calc 12 * 5`, `avg`, `top 3`, `chart`. Xem `course_lab/lcel_demo.py` để hiểu `RunnableLambda(parse) | RunnableLambda(execute) | RunnableLambda(format)`.

**LCEL ≠ AI Agent**: LCEL xác định chuỗi xử lý cố định; nó không tự suy luận chọn tool. (Có thể dùng LCEL cùng LLM, nhưng demo này tách riêng để dễ hiểu.)

## 4. Chạy Manual Tool Calling với LLM thật (cần API key)

Đây là bước **cầu nối** giữa mô phỏng ở phần đầu và LangChain Agent hoàn chỉnh. Ở chế độ này, **LLM thật chọn tool** bằng `bind_tools()` nhưng **chính Python tự gọi hàm** và trả `ToolMessage` cho LLM.

```powershell
$env:OPENAI_API_KEY="YOUR_API_KEY"
$env:OPENAI_MODEL="openai:gpt-4.1-mini"
python main.py --mode manual-llm
```

Ví dụ: `What is the overall average score?`, `Calculate 12 times 5.`

Hãy đọc `course_lab/manual_llm.py` để hiểu `ai_message.tool_calls` → `execute_tool_call()` → `ToolMessage()`.

## 5. Chạy LangChain Agent thật (cần API key riêng)

Đảm bảo đã cài `requirements-optional.txt`. Trong **PowerShell**:

```powershell
$env:OPENAI_API_KEY="YOUR_API_KEY"
$env:OPENAI_MODEL="openai:gpt-4.1-mini"
python main.py --mode agent
```

Hỏi tự nhiên, ví dụ:

```text
What is 12 multiplied by 5?
Which student has the highest average score?
Please create a bar chart of course averages.
Find notes on tool calling.
My favorite course is AI. What is my favorite course?
```

Agent có thể gọi **nhiều tool trong một yêu cầu**, hoặc chỉ trả lời trực tiếp khi không cần tool. Cùng `thread_id` lưu lịch sử cho tới khi tắt chương trình (`InMemorySaver`).

- Dữ liệu SQL chỉ được truy cập qua các hàm đọc an toàn; không thực thi SQL tự do do LLM sinh.
- Chương trình không đòi API key ở chế độ offline và LCEL.
- **OpenAI API trả phí riêng, không bao gồm trong gói ChatGPT Plus.** Không chia sẻ key hay đưa vào GitHub.
- Tên model có thể thay đổi theo quyền truy cập API; điều chỉnh `$env:OPENAI_MODEL` nếu model không khả dụng.

## 6. Tương ứng với nội dung Coursera

| Phần học IBM | Code nên đọc / chạy |
|---|---|
| Why AI Needs Tools | `tools.py` (calculator, SQL, chart) |
| Traditional Tool Calling | `manual.py` (mock), `manual_llm.py` (LLM thật) |
| Structured Outputs and Validation | `manual.py`: `validate_tool_call()` |
| Build Custom Tools | `tools.py` và `langchain_agent.py` với `@tool` |
| Embedded Tool Calling | `langchain_agent.py` với `create_agent()` |
| LCEL and Chaining | `lcel_demo.py` (`|` chain) |
| Interactive Agents and Memory | `langchain_agent.py` + `InMemorySaver` |
| Natural Language Data Visualization | `plot_scores()`; real agent chọn tool tạo SVG |
| Conversational SQL / Data Access | `database.py` + `top_students()` + real agent |
| Agent Orchestration | Vòng lặp tools trong `create_agent()` |

Khóa học có thể đề cập nhiều built-in tools và tích hợp khác: project này minh họa **nguyên lý chung**, không thay thế tất cả bài lab của khóa.

## 7. Tự kiểm tra

```powershell
python -m unittest discover -s tests -v
```

Kỳ vọng: tất cả 8 tests `OK`.

## 8. Bài tập nâng cấp

1. Viết thêm tool `lowest_student()` và gọi ở offline mode.
2. Thêm tool `course_average(course)` truy vấn SQL có điều kiện.
3. Dùng LCEL tạo chuỗi `parse → validate → execute → format` (tách validate thành bước riêng).
4. Viết test kiểm tra lỗi chia cho 0 và tham số âm / không hợp lệ.
5. Dùng agent thật yêu cầu tính trung bình và lưu chart trong cùng một lượt hỏi.

## 9. Ghi nhớ

- **Tool definition**: name + description + parameters.
- **Tool calling**: model đề xuất gọi tool; **Python** thực thi.
- **LCEL**: ghép các bước theo luồng xác định.
- **LangChain Agent**: LLM tự chọn tools và có thể lặp.
- **SQL/Chart**: tools có tác dụng thật ngoài việc tạo văn bản.
- **Memory**: thông tin giữa các câu hỏi có thể được lưu theo một thread.

Tham khảo: https://docs.langchain.com/oss/python/langchain/agents và https://docs.langchain.com/oss/python/langchain/tools
