#!/usr/bin/env python3
"""
Tự động sinh bài học tiếng Anh Audio Visual hàng ngày bằng Google Gemini AI.
Thiết kế chạy độc lập qua GitHub Actions hoặc chạy cục bộ (Local).
Không sử dụng thư viện ngoài, chỉ dùng Python standard library.
"""

import os
import sys
import json
import datetime
import urllib.request
import urllib.error

# Thiết lập UTF-8 cho terminal Windows để in tiếng Việt và emoji không bị lỗi
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

# Danh sách chủ đề xoay vòng theo các thứ trong tuần
THEMES_BY_WEEKDAY = {
    0: "Hệ Thống Âm Thanh & Cân Chỉnh Âm Học (Acoustic Tuning, DSP Limiter & Dante Latency)",
    1: "Hệ Thống Hiển Thị, Máy Chiếu & dvLED (AVIXA DISCAS, Pixel Pitch & Throw Ratio)",
    2: "Mạng Hạ Tầng AV, Switch PoE+ & Điều Khiển IP (VLAN Isolation, QoS & REST API)",
    3: "Phối Hợp Công Trường, Hạ Tầng Cáp & Bản Vẽ (RCP, Conduit Bend Radius & As-Built)",
    4: "Họp Dự Án, Đàm Phán Hãng & Báo Giá Kỹ Thuật (Lead Time, BOM & Client Kick-off)",
    5: "Nghiệm Thu T&C, Bàn Giao & Hướng Dẫn Sử Dụng (Commissioning, Touch Panel & Training)",
    6: "Giao Tiếp Văn Phòng & Xã Giao Đồng Nghiệp (Office Small Talk, Lunch & Project Review)"
}

def get_system_prompt(today_str, weekday_name, theme_suggestion):
    return f"""
Bạn là Senior AV Consultant và Gia sư Tiếng Anh Kỹ thuật cao cấp theo phương pháp ENGLISH_COACH (A1 to Pro).
Hôm nay là {weekday_name}, ngày {today_str}.
Chủ đề trọng tâm của ngày hôm nay: "{theme_suggestion}".

Nhiệm vụ của bạn: Hãy biên soạn một gói bài học tiếng Anh Audio Visual & Giao tiếp công trường hoàn chỉnh cho ngày hôm nay.
QUY TẮC BẮT BUỘC:
1. Đảm bảo triết lý ENGLISH_COACH: Song ngữ Anh - Việt, khung câu ngắn dễ lắp ghép (Sentence Frame), sửa lỗi 4 mục.
2. Thuật ngữ Audio Visual phải chính xác 100% theo tiêu chuẩn ngành (SPL, Dante, DISCAS, EDID, Headroom, PoE, RCP, As-built...).
3. Câu cơ bản (Basic): Chuẩn ngữ pháp, ngắn gọn cho người mới bắt đầu (A1-A2).
4. Câu nâng cấp (Pro): Văn phong tự nhiên, chuyên nghiệp của kỹ sư AV quốc tế hoặc người bản xứ.
5. Cung cấp phiên âm IPA chuẩn cho từ vựng và câu cơ bản.

BẮT BUỘC CHỈ XUẤT RA DUY NHẤT 1 ĐOẠN MÃ JSON THUẦN (KHÔNG CÓ GIẢI THÍCH, KHÔNG BỌC TRONG MARKDOWN, KHÔNG ```json).
Cấu trúc JSON bắt buộc phải chính xác như sau:
{{
  "updatedAt": "{today_str}T06:00:00Z",
  "date": "{today_str}",
  "dayNumber": 1,
  "theme": "{theme_suggestion}",
  "source": "Google Gemini AI (Automated Daily Feed)",
  "corePattern": {{
    "frame": "Khung câu mẫu có chứa [Dấu ngoặc vuông thay thế]",
    "vn": "Dịch nghĩa tiếng Việt của khung câu mẫu",
    "exampleEn": "Câu ví dụ tiếng Anh hoàn chỉnh sử dụng khung câu",
    "exampleVn": "Dịch nghĩa tiếng Việt của câu ví dụ",
    "substitutions": [
      "cụm từ thay thế 1 / cụm từ thay thế 2",
      "cụm từ thay thế 3 / cụm từ thay thế 4"
    ]
  }},
  "vocabulary": [
    {{
      "term": "Thuật ngữ tiếng Anh",
      "category": "audio | video | control | site | daily",
      "ipa": "/phiên âm IPA/",
      "meaning": "Giải nghĩa tiếng Việt chi tiết bản chất kỹ thuật",
      "exampleEn": "Câu ví dụ tiếng Anh thực tế trong dự án",
      "exampleVn": "Dịch nghĩa tiếng Việt của câu ví dụ"
    }},
    {{
      "term": "Thuật ngữ tiếng Anh 2",
      "category": "audio | video | control | site | daily",
      "ipa": "/phiên âm IPA/",
      "meaning": "Giải nghĩa tiếng Việt",
      "exampleEn": "Câu ví dụ tiếng Anh",
      "exampleVn": "Dịch nghĩa tiếng Việt"
    }},
    {{
      "term": "Thuật ngữ tiếng Anh 3",
      "category": "audio | video | control | site | daily",
      "ipa": "/phiên âm IPA/",
      "meaning": "Giải nghĩa tiếng Việt",
      "exampleEn": "Câu ví dụ tiếng Anh",
      "exampleVn": "Dịch nghĩa tiếng Việt"
    }}
  ],
  "reflexDrill": [
    {{
      "id": 1,
      "category": "av | daily",
      "categoryLabel": "NHÃN CHỦ ĐỀ NGẮN",
      "vn": "Câu tiếng Việt tình huống cần phản xạ nói sang tiếng Anh",
      "context": "Ngữ cảnh: Mô tả tình huống thực tế trên công trường hoặc văn phòng.",
      "basicEn": "Câu tiếng Anh chuẩn cơ bản (ngắn, dễ nhớ A1-A2)",
      "basicIpa": "/phiên âm IPA của câu cơ bản/",
      "proEn": "Câu tiếng Anh nâng cấp tự nhiên (Pro Native Engineer)",
      "proNote": "Giải thích chi tiết từ vựng và sắc thái câu bản ngữ bằng tiếng Việt",
      "frame": "Khung câu lắp ghép dạng [Placeholder]"
    }},
    {{
      "id": 2,
      "category": "av | daily",
      "categoryLabel": "NHÃN CHỦ ĐỀ NGẮN",
      "vn": "Câu tiếng Việt tình huống phản xạ thứ hai",
      "context": "Ngữ cảnh: Mô tả tình huống thực tế.",
      "basicEn": "Câu tiếng Anh cơ bản",
      "basicIpa": "/phiên âm IPA/",
      "proEn": "Câu tiếng Anh nâng cấp tự nhiên",
      "proNote": "Giải thích chi tiết",
      "frame": "Khung câu dạng [Placeholder]"
    }}
  ],
  "microDialogue": {{
    "id": 1,
    "title": "Tiêu đề kịch bản đối thoại thực chiến",
    "desc": "Tóm tắt ngữ cảnh cuộc đối thoại ngắn giữa 2 người",
    "messages": [
      {{
        "speaker": "Site Manager / Client / Architect",
        "side": "left",
        "en": "Câu hỏi hoặc ý kiến của đối tác",
        "vn": "Dịch nghĩa tiếng Việt"
      }},
      {{
        "speaker": "AV Engineer (You)",
        "side": "right",
        "en": "Câu phản hồi kỹ thuật tự tin và chuyên nghiệp của bạn",
        "vn": "Dịch nghĩa tiếng Việt"
      }},
      {{
        "speaker": "Site Manager / Client / Architect",
        "side": "left",
        "en": "Câu phản hồi tiếp theo của đối tác",
        "vn": "Dịch nghĩa tiếng Việt"
      }},
      {{
        "speaker": "AV Engineer (You)",
        "side": "right",
        "en": "Câu kết luận hoặc giải pháp tối ưu của bạn",
        "vn": "Dịch nghĩa tiếng Việt"
      }}
    ]
  }},
  "sentenceBuilder": [
    {{
      "id": 1,
      "vn": "Câu tiếng Việt cần sắp xếp từ vựng",
      "words": ["Mảng", "các", "từ", "rời", "rạc", "tiếng", "Anh."],
      "fullSentence": "Câu tiếng Anh hoàn chỉnh sau khi ghép đúng thứ tự.",
      "grammarNote": "Phân tích cấu trúc ngữ pháp ngắn gọn, dễ nhớ."
    }}
  ]
}}
"""

def call_gemini_api(api_key, prompt, model="gemini-2.5-flash"):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.3,
            "topP": 0.95,
            "responseMimeType": "application/json"
        }
    }

    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            candidate = data.get("candidates", [{}])[0]
            text = candidate.get("content", {}).get("parts", [{}])[0].get("text", "")
            return text
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8")
        # Thử fallback sang gemini-1.5-flash nếu 2.5 không khả dụng
        if model != "gemini-1.5-flash":
            print(f"[*] Thử fallback sang model gemini-1.5-flash do: {e.code}")
            return call_gemini_api(api_key, prompt, model="gemini-1.5-flash")
        raise RuntimeError(f"HTTP Error {e.code}: {err_msg}")

def clean_json_output(raw_text):
    text = raw_text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()

def main():
    print("=" * 60)
    print("🚀 BẮT ĐẦU TỰ ĐỘNG SINH BÀI HỌC TIẾNG ANH AUDIO VISUAL")
    print("=" * 60)

    # Xác định đường dẫn file đầu ra
    script_dir = os.path.dirname(os.path.abspath(__file__))
    learn_dir = os.path.abspath(os.path.join(script_dir, ".."))
    output_path = os.path.join(learn_dir, "daily_feed.json")

    now = datetime.datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    weekday_idx = now.weekday()
    weekday_names = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]
    theme = THEMES_BY_WEEKDAY.get(weekday_idx, "Giao tiếp Kỹ thuật Audio Visual")

    print(f"📅 Ngày thực thi: {today_str} ({weekday_names[weekday_idx]})")
    print(f"🎯 Chủ đề: {theme}")
    print(f"📁 Tệp xuất: {output_path}")

    api_key = os.environ.get("GEMINI_API_KEY", "").strip()

    if not api_key:
        print("\n⚠️ CẢNH BÁO: Chưa tìm thấy biến môi trường 'GEMINI_API_KEY'.")
        print("  - Để sinh bài từ AI thật: Hãy cung cấp GEMINI_API_KEY trong GitHub Secrets hoặc đặt biến môi trường.")
        print("  - Script sẽ kiểm tra xem file daily_feed.json đã tồn tại hay chưa...")

        if os.path.exists(output_path):
            print(f"✅ Tệp {output_path} đã tồn tại. Giữ nguyên dữ liệu hiện tại.")
            sys.exit(0)
        else:
            print("❌ Tệp chưa tồn tại. Vui lòng cung cấp GEMINI_API_KEY để khởi tạo!")
            sys.exit(1)

    prompt = get_system_prompt(today_str, weekday_names[weekday_idx], theme)
    print("\n🌐 Đang kết nối tới Google Gemini API...")
    
    try:
        raw_output = call_gemini_api(api_key, prompt)
        cleaned_json = clean_json_output(raw_output)
        
        # Kiểm tra tính hợp lệ của JSON
        parsed_data = json.loads(cleaned_json)
        
        # Đảm bảo các khóa cốt lõi tồn tại
        required_keys = ["theme", "corePattern", "vocabulary", "reflexDrill", "microDialogue", "sentenceBuilder"]
        for key in required_keys:
            if key not in parsed_data:
                raise ValueError(f"Thiếu khóa bắt buộc trong JSON: {key}")

        parsed_data["date"] = today_str
        parsed_data["updatedAt"] = now.isoformat()

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(parsed_data, f, ensure_ascii=False, indent=2)

        print(f"\n🎉 THÀNH CÔNG! Đã cập nhật bài học mới ngày {today_str} vào:")
        print(f"   👉 {output_path}")
        print(f"   📌 Chủ đề: {parsed_data.get('theme')}")
        print(f"   📚 Số từ vựng mới: {len(parsed_data.get('vocabulary', []))}")
        print(f"   ⚡ Số câu phản xạ: {len(parsed_data.get('reflexDrill', []))}")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ LỖI TRONG QUÁ TRÌNH SINH BÀI: {e}")
        # Không xóa file cũ nếu gặp lỗi để đảm bảo app luôn có dữ liệu hoạt động
        if os.path.exists(output_path):
            print("⚠️ Giữ nguyên tệp daily_feed.json hiện có để không làm gián đoạn ứng dụng.")
            sys.exit(0)
        sys.exit(1)

if __name__ == "__main__":
    main()
