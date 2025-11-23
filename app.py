import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
import io
from dotenv import load_dotenv
import requests
import json
import base64

# Load environment variables (for local development)
load_dotenv()

# Get API key from Streamlit Secrets (for Streamlit Cloud) or environment variable (for local)
def get_api_key():
    # Try Streamlit Secrets first (for Streamlit Cloud)
    try:
        if hasattr(st, 'secrets') and 'GOOGLE_API_KEY' in st.secrets:
            return st.secrets['GOOGLE_API_KEY']
    except:
        pass
    # Fallback to environment variable (for local development)
    return os.getenv("GOOGLE_API_KEY", "")

# Configure page
st.set_page_config(
    page_title="Gift Image Creator",
    page_icon="🎁",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if "generated_image" not in st.session_state:
    st.session_state.generated_image = None
if "generated_image_data" not in st.session_state:
    st.session_state.generated_image_data = None
# We will use the widget key 'prompt_style_input' directly

# Custom CSS for sophisticated design
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Global font and colors */
    .stApp {
        background-color: #f8f9fa;
        font-family: 'Helvetica Neue', sans-serif;
        color: #333333;
    }
    
    /* Logo styling */
    .logo-container {
        display: flex;
        justify-content: center;
        margin-bottom: 1rem;
        padding-top: 1rem;
    }
    .logo-img {
        max-width: 200px;
        height: auto;
    }
    
    /* Title styling */
    .main-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1a1a1a;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    
    /* Section Header Styling */
    .section-header {
        font-size: 1.2rem;
        font-weight: 600;
        color: #000000; /* Black */
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #11C2A3;
        padding-left: 10px;
    }
    
    /* Sub-label styling */
    .sub-label {
        font-size: 0.95rem;
        font-weight: 600;
        color: #000000; /* Black */
        margin-bottom: 0.2rem;
        margin-top: 0.5rem;
    }

    /* Button styling */
    .stButton > button {
        width: 100%;
        font-weight: 700 !important;
        border: none !important;
        transition: all 0.3s ease !important;
    }

    /* Primary Button (Generate) - Gradient & Rounded */
    div[data-testid="stButton"] > button[kind="primary"] {
        border-radius: 50px !important;
        background: linear-gradient(90deg, #11C2A3 0%, #43C7E3 100%) !important;
        color: white !important;
        font-size: 1.1rem !important;
        padding: 0.8rem 2rem !important;
        box-shadow: 0 4px 15px rgba(17, 194, 163, 0.3) !important;
        white-space: nowrap !important; /* Prevent text wrapping */
    }
    div[data-testid="stButton"] > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(17, 194, 163, 0.4) !important;
        opacity: 0.95;
    }
    div[data-testid="stButton"] > button[kind="primary"]:active {
        transform: translateY(1px);
    }

    /* Secondary Button (Tags) - White, Border, Boxy */
    div[data-testid="stButton"] > button[kind="secondary"] {
        border-radius: 8px !important; /* Slightly rounded square */
        background-color: white !important;
        color: #11C2A3 !important; /* Brand color text */
        border: 2px solid #11C2A3 !important; /* Brand color border */
        font-size: 0.9rem !important;
        padding: 0.5rem 1rem !important;
    }
    div[data-testid="stButton"] > button[kind="secondary"]:hover {
        background-color: #f0fdfa !important; /* Very light teal */
        border-color: #0eb092 !important;
        color: #0eb092 !important;
    }
    
    /* Download Button Styling */
    div[data-testid="stDownloadButton"] > button {
        border-radius: 8px !important;
        background-color: white !important;
        color: #11C2A3 !important;
        border: 2px solid #11C2A3 !important;
        font-size: 0.9rem !important;
        padding: 0.5rem 1rem !important;
    }
    div[data-testid="stDownloadButton"] > button:hover {
        background-color: #f0fdfa !important;
        border-color: #0eb092 !important;
        color: #0eb092 !important;
    }
    
    /* Center download button */
    div[data-testid="stVerticalBlock"]:has(div[data-testid="stDownloadButton"]) {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }
    
    /* Card-like containers */
    .css-1r6slb0 {
        background-color: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 1.5rem;
    }

    /* File Uploader Styling */
    /* Hide the default "Drag and drop files here" text */
    [data-testid="stFileUploader"] section > div > div > span {
        display: none;
    }
    /* Add Japanese text */
    [data-testid="stFileUploader"] section > div > div::before {
        content: "ここにファイルをドラッグ＆ドロップ、またはクリックして選択";
        display: block;
        margin-bottom: 10px;
        color: #666;
        font-size: 1rem;
        text-align: center;
    }

    /* Style file list items */
    [data-testid="stFileUploader"] ul {
        background-color: #f8f9fa !important;
        border-radius: 8px !important;
        padding: 0.5rem !important;
    }
    
    .stFileUploaderFile {
        background-color: white !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 6px !important;
        padding: 0.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    .stFileUploaderFileName {
        color: #333 !important;
        font-weight: 500 !important;
    }
    
    /* Style delete button */
    [data-testid="stFileUploaderDeleteBtn"] button {
        color: #ff4b4b !important;
        transition: all 0.2s ease !important;
    }
    
    [data-testid="stFileUploaderDeleteBtn"] button:hover {
        background-color: #ffebee !important;
        color: #d32f2f !important;
    }
    
    /* Style and center pagination */
    [data-testid="stFileUploaderPagination"] {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        gap: 0.5rem !important;
        margin-top: 0.5rem !important;
        padding: 0.5rem !important;
    }
    
    [data-testid="stFileUploaderPagination"] button {
        color: #11C2A3 !important;
        transition: all 0.2s ease !important;
    }
    
    [data-testid="stFileUploaderPagination"] button:hover {
        background-color: #f0fdfa !important;
    }
    
    [data-testid="stFileUploaderPagination"] small {
        color: #666 !important;
        font-size: 0.85rem !important;
    }
    
    /* Fix for Delete Buttons and File List */
    [data-testid="stFileUploaderUploadedItem"] div[data-testid="stMarkdownContainer"] p {
        display: none;
    }
    
    /* Aspect Ratio Radio Buttons */
    /* Ensure labels are visible and high contrast */
    [data-testid="stRadio"] label p {
        font-size: 1rem !important;
        color: #000000 !important; /* Black */
        font-weight: 500 !important;
    }
    /* Force radio button text color specifically */
    div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p {
        color: #000000 !important;
    }
    
    /* Input labels */
    .stTextInput label, .stTextArea label {
        color: #000000 !important;
    }
    
    /* Custom Loader Animation */
    @keyframes pulse-blue {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(17, 194, 163, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(17, 194, 163, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(17, 194, 163, 0); }
    }
    .generating-loader {
        display: flex;
        justify-content: center;
        align-items: center;
        flex-direction: column;
        margin: 2rem 0;
    }
    .generating-circle {
        width: 50px;
        height: 50px;
        background-color: #11C2A3;
        border-radius: 50%;
        animation: pulse-blue 2s infinite;
        margin-bottom: 1rem;
    }
    .generating-text {
        font-size: 1.1rem;
        font-weight: 500;
        color: #11C2A3;
    }
   /* Tag Buttons */
    .tag-button {
        display: inline-block;
        padding: 5px 10px;
        margin: 5px;
        background-color: #e9ecef;
        border-radius: 20px;
        color: #495057;
        font-size: 0.9rem;
        cursor: pointer;
        border: 1px solid #ced4da;
    }
    .tag-button:hover {
        background-color: #dee2e6;
    }

    /* Template Selection Styling */
    .template-radio-btn {
        background-color: transparent !important;
        border: none !important;
        color: #333 !important;
        font-size: 1.5rem !important;
        padding: 0 !important;
        margin: 0 !important;
        line-height: 1 !important;
        box-shadow: none !important;
    }
    .template-radio-btn:hover {
        background-color: transparent !important;
        color: #11C2A3 !important;
        transform: none !important;
        box-shadow: none !important;
    }
    .template-radio-btn:active {
        background-color: transparent !important;
        transform: none !important;
    }
    
    /* Center the generate button */
    div[data-testid="stVerticalBlock"]:has(button[kind="primary"]) {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }
    
    /* Center logo image */
    div[data-testid="stImage"] {
        display: flex !important;
        justify-content: center !important;
    }
</style>
""", unsafe_allow_html=True)

# Header with Logo - centered
if os.path.exists("logo.png"):
    st.image("logo.png", width=150)
else:
    st.markdown('<h1 class="main-title">AnyGift</h1>', unsafe_allow_html=True)

st.markdown('<h1 class="main-title">選べるギフト画像Creator</h1>', unsafe_allow_html=True)

# Sidebar for settings
with st.sidebar:
    st.header("設定")
    default_api_key = get_api_key()
    api_key_input = st.text_input("Google API Key", type="password", value=default_api_key)
    model_name = st.text_input("Model ID", value="gemini-3-pro-image-preview")
    st.caption("デフォルト: gemini-3-pro-image-preview")

# Function to generate image
def generate_image(uploaded_files, main_text, sub_text, prompt_style, aspect_ratio, template_image_path=None, modification_instruction=""):
    if not uploaded_files:
        return None, "画像をアップロードしてください。"
    
    # Custom Animation Placeholder
    placeholder = st.empty()
    placeholder.markdown("""
        <div class="generating-loader">
            <div class="generating-circle"></div>
            <div class="generating-text">画像生成中です...</div>
        </div>
    """, unsafe_allow_html=True)
    
    try:
        # Prepare inputs for REST API
        
        # Construct the prompt
        base_prompt = f"""
        Create a high-quality, premium gift selection image.
        
        Input Images: Use these product images as the main subjects.
        
        Text Content:
        - Main Text: "{main_text}" (Make this prominent and elegant)
        - Sub Text: "{sub_text}" (Smaller, complementary text)
        
        Style/Atmosphere: {prompt_style}
        
        Requirements:
        - Professional product photography style.
        - If multiple images are provided, arrange them tastefully.
        - Add a "Choice" or "Gift" theme background.
        - Make it look like a high-end e-commerce banner.
        - Ensure text is legible and integrated into the design.
        """
        
        if template_image_path:
             base_prompt += "\n\nReference Design: Please use the provided reference image as a layout and style guide."
        
        if modification_instruction:
            base_prompt += f"\n\nMODIFICATION REQUEST: {modification_instruction}\nPlease regenerate the image applying these changes while keeping the original intent."

        contents_parts = [{"text": base_prompt}]
        
        # Add Template Image if selected (can be file path or UploadedFile object)
        if template_image_path:
            try:
                # Check if it's an UploadedFile object (custom reference) or a file path (template)
                if hasattr(template_image_path, 'read'):
                    # It's an UploadedFile object
                    template_image_path.seek(0)
                    template_bytes = template_image_path.getvalue()
                elif os.path.exists(template_image_path):
                    # It's a file path
                    with open(template_image_path, "rb") as f:
                        template_bytes = f.read()
                else:
                    template_bytes = None
                
                if template_bytes:
                    template_base64 = base64.b64encode(template_bytes).decode('utf-8')
                    
                    # Determine mime type
                    if hasattr(template_image_path, 'type'):
                        # UploadedFile has a type attribute
                        mime_type = template_image_path.type
                    else:
                        # File path - determine from extension
                        ext = os.path.splitext(template_image_path)[1].lower()
                        mime_type = "image/png" if ext == ".png" else "image/jpeg"
                    
                    contents_parts.append({
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": template_base64
                        }
                    })
            except Exception as e:
                print(f"Error loading template: {e}")

        for file in uploaded_files:
            # Reset file pointer
            file.seek(0)
            bytes_data = file.getvalue()
            base64_data = base64.b64encode(bytes_data).decode('utf-8')
            mime_type = file.type
            contents_parts.append({
                "inline_data": {
                    "mime_type": mime_type,
                    "data": base64_data
                }
            })

        # Construct payload
        payload = {
            "contents": [
                {
                    "parts": contents_parts
                }
            ],
            "generationConfig": {
                "responseModalities": ["IMAGE"],
                "imageConfig": {
                    "aspectRatio": aspect_ratio
                }
            }
        }

        # API Endpoint
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key_input}"
        
        headers = {
            "Content-Type": "application/json"
        }

        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        # Clear animation
        placeholder.empty()
        
        if response.status_code == 200:
            result = response.json()
            try:
                candidates = result.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    image_part = None
                    for part in parts:
                        if "inlineData" in part:
                            image_part = part["inlineData"]
                            break
                    
                    if image_part:
                        image_data = base64.b64decode(image_part["data"])
                        image = Image.open(io.BytesIO(image_data))
                        
                        # Save to session state
                        st.session_state.generated_image = image
                        
                        buf = io.BytesIO()
                        image.save(buf, format="PNG")
                        byte_im = buf.getvalue()
                        st.session_state.generated_image_data = byte_im
                        
                        return image, None
                    else:
                        return None, "画像が生成されませんでした。レスポンスに画像データが含まれていません。"
                else:
                    return None, "生成候補が見つかりませんでした。"
            except Exception as parse_error:
                return None, f"レスポンスの解析に失敗しました: {str(parse_error)}"
        else:
            if response.status_code == 429:
                return None, "APIエラー: 429 (利用枠超過)。サイドバーでモデルIDを変更してみてください。"
            return None, f"APIエラー: {response.status_code}\n{response.text}"

    except Exception as e:
        placeholder.empty()
        return None, f"エラーが発生しました: {str(e)}"


# Main Content
if not api_key_input:
    st.warning("APIキーが設定されていません。.envファイルを設定するか、サイドバーで入力してください。")
else:
    # Configure GenAI
    genai.configure(api_key=api_key_input)

    # Step 1: Image Upload
    st.markdown('<div class="section-header">商品画像アップロード</div>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader("商品画像をアップロードしてください", type=['png', 'jpg', 'jpeg', 'webp'], accept_multiple_files=True, label_visibility="collapsed")

    if uploaded_files:
        cols = st.columns(len(uploaded_files))
        for idx, file in enumerate(uploaded_files):
            with cols[idx]:
                st.image(file, use_container_width=True)

    st.markdown("---")

    # Step 2: Configuration
    st.markdown('<div class="section-header">デザイン設定</div>', unsafe_allow_html=True)
    
    # Template Selection
    st.markdown('<div class="sub-label">見本デザイン（任意）</div>', unsafe_allow_html=True)
    
    # Display template images in a row
    template_options = [
        {"name": "指定なし", "path": None, "image": None},
        {"name": "デザインA", "path": "templates/template_1.jpg", "image": "templates/template_1.jpg"},
        {"name": "デザインB", "path": "templates/template_2.jpg", "image": "templates/template_2.jpg"},
        {"name": "デザインC", "path": "templates/template_3.png", "image": "templates/template_3.png"},
        {"name": "デザインD", "path": "templates/template_4.jpg", "image": "templates/template_4.jpg"},
    ]
    
    # Display images in columns
    cols = st.columns(len(template_options))
    for i, option in enumerate(template_options):
        with cols[i]:
            if option["image"] and os.path.exists(option["image"]):
                st.image(option["image"], use_container_width=True)
            else:
                # Placeholder for "None" - Square aspect ratio
                st.markdown(
                    """
                    <div style="
                        width: 100%;
                        aspect-ratio: 1 / 1;
                        background-color: #f0f2f6; 
                        display: flex; 
                        align-items: center; 
                        justify-content: center; 
                        border-radius: 5px;
                        color: #666;
                        font-size: 0.8rem;
                        border: 1px dashed #ccc;
                        margin-bottom: 0.5rem;
                    ">
                        指定なし
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
    
    # Native radio buttons for selection
    template_names = [opt["name"] for opt in template_options]
    selected_template_name = st.radio(
        "見本デザインを選択",
        options=template_names,
        index=0,
        horizontal=True,
        label_visibility="collapsed"
    )
    
    # Get the selected template path
    selected_template_path = None
    for opt in template_options:
        if opt["name"] == selected_template_name:
            selected_template_path = opt["path"]
            break

    # Custom Reference Design Upload
    st.markdown('<div class="sub-label">参照デザイン(任意)</div>', unsafe_allow_html=True)
    st.caption("独自のデザインを参照したい場合は、画像をアップロードしてください")
    reference_design_file = st.file_uploader(
        "参照デザイン画像をアップロード",
        type=['png', 'jpg', 'jpeg', 'webp'],
        accept_multiple_files=False,
        label_visibility="collapsed",
        key="reference_design_uploader"
    )
    
    if reference_design_file:
        st.image(reference_design_file, caption="アップロードされた参照デザイン", width=200)
    
    # Determine which template to use (custom upload takes priority)
    final_template_path = None
    if reference_design_file:
        # Use the uploaded reference design
        final_template_path = reference_design_file
    elif selected_template_path:
        # Use the selected template
        final_template_path = selected_template_path

    # Aspect Ratio with visual icons
    st.markdown('<div class="sub-label">アスペクト比</div>', unsafe_allow_html=True)
    aspect_ratio_selection = st.radio(
        "アスペクト比を選択",
        options=["1:1 (正方形)", "16:9 (横長)", "9:16 (縦長)", "4:3 (標準)", "3:4 (縦標準)"],
        index=0,
        horizontal=True,
        label_visibility="collapsed"
    )
    # Map selection to API value
    aspect_ratio_map = {
        "1:1 (正方形)": "1:1",
        "16:9 (横長)": "16:9",
        "9:16 (縦長)": "9:16",
        "4:3 (標準)": "4:3",
        "3:4 (縦標準)": "3:4"
    }
    aspect_ratio = aspect_ratio_map[aspect_ratio_selection]
    
    st.markdown("---")
    
    # Text Inputs (Vertical Layout)
    st.markdown('<div class="section-header">入れたい文言</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="sub-label">メインテキスト</div>', unsafe_allow_html=True)
    main_text = st.text_input(
        "メインテキスト", 
        value="選べるカタログギフト",
        placeholder="例: Happy Birthday",
        label_visibility="collapsed"
    )
    
    st.markdown('<div class="sub-label">サブテキスト</div>', unsafe_allow_html=True)
    sub_text = st.text_input(
        "サブテキスト", 
        value="ギフトをもらった人が好きな商品を選べます",
        placeholder="例: 2025.11.21",
        label_visibility="collapsed"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown('<div class="section-header">AIへの指示</div>', unsafe_allow_html=True)
    
    # Tag Buttons
    tag_prompts = {
        "パステルカラー": "パステルカラーを基調とした、ふんわりと優しい雰囲気のデザイン。明るく柔らかい光の演出を加え、可愛らしさと幸福感を表現してください。",
        "高級感": "黒やゴールド、深い色合いを使用した、シックで高級感のあるデザイン。洗練されたフォントとレイアウトで、プレミアムなギフトであることを強調してください。",
        "シンプル": "余計な装飾を削ぎ落とした、ミニマルで洗練されたデザイン。余白を活かし、商品画像とテキストが際立つように清潔感のある構成にしてください。",
        "ポップ": "鮮やかな色使いと元気な印象を与えるポップなデザイン。動きのあるレイアウトや幾何学模様を取り入れ、楽しさとワクワク感を演出してください。",
        "和風": "和紙の質感や伝統的な和柄（麻の葉、青海波など）を取り入れた、落ち着きのある和風デザイン。上品で奥ゆかしい雰囲気を表現してください。",
        "季節感（冬）": "雪の結晶やキラキラとした光、寒色系のカラーパレットを使用した冬らしいデザイン。温かみのあるギフトとしての魅力を引き立てる、幻想的な雰囲気にしてください。"
    }
    
    # Helper to update prompt (Overwrite)
    def update_prompt(prompt_text):
        st.session_state.prompt_style_input = prompt_text

    # Display tags as small buttons
    st.markdown("ヒント: クリックで追加")
    tag_cols = st.columns(3) # Adjusted for longer text
    for i, (label, prompt_text) in enumerate(tag_prompts.items()):
        with tag_cols[i % 3]:
            # Use on_click callback to update state before rerun
            st.button(label, key=f"tag_{i}", use_container_width=True, on_click=update_prompt, args=(prompt_text,))

    prompt_style = st.text_area(
        "AIへの指示", 
        placeholder="例: パステルカラー、ふんわり、高級感、余白を活かしたデザイン...", 
        height=108,
        label_visibility="collapsed",
        key="prompt_style_input"
    )

    st.markdown("---")

    # Step 3: Generate
    # Header removed as requested
    
    # Button will be centered via CSS
    if st.button("画像を生成する", type="primary"):
        image, error = generate_image(uploaded_files, main_text, sub_text, prompt_style, aspect_ratio, final_template_path)
        if error:
            st.error(error)
        # Success is handled by session state update in function

    # Display Result (Persistence)
    if st.session_state.generated_image:
        st.image(st.session_state.generated_image, caption="生成された画像", use_container_width=True)
        
        # Download button will be centered via CSS
        st.download_button(
            label="画像をダウンロード",
            data=st.session_state.generated_image_data,
            file_name="generated_gift_image.png",
            mime="image/png"
        )
        
        st.markdown("---")
        st.markdown("#### 画像を微調整")
        st.caption("生成された画像を元に、さらに調整を加えることができます")
        modification_prompt = st.text_area(
            "変更したい点を入力してください", 
            placeholder="例: 文字色を青にして、背景をもっと明るく、文字サイズを大きく...",
            height=120,
            label_visibility="collapsed"
        )
        
        if st.button("再生成する", type="secondary"):
            if not modification_prompt:
                st.warning("変更内容を入力してください。")
            else:
                # Pass the generated image as reference for regeneration
                # Create a temporary file-like object from the generated image
                buf = io.BytesIO()
                st.session_state.generated_image.save(buf, format="PNG")
                buf.seek(0)
                
                # Create a mock UploadedFile-like object
                class MockUploadedFile:
                    def __init__(self, data, name="generated.png", type="image/png"):
                        self._data = data
                        self.name = name
                        self.type = type
                    
                    def seek(self, pos):
                        self._data.seek(pos)
                    
                    def getvalue(self):
                        return self._data.getvalue()
                    
                    def read(self):
                        return self._data.read()
                
                reference_image = MockUploadedFile(buf)
                
                # Combine original prompt with modification request
                combined_prompt = f"{prompt_style}\n\n【変更指示】\n{modification_prompt}"
                
                # Generate with the previous image as reference
                image, error = generate_image(uploaded_files, main_text, sub_text, combined_prompt, aspect_ratio, reference_image)
                if error:
                    st.error(error)
                else:
                    st.rerun()
