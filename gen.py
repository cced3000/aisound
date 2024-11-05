import os
import streamlit as st
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv
from openai import OpenAI

# 加载环境变量
load_dotenv()

# 配置缓存
@st.cache_resource
def get_clients():
    """初始化并缓存API客户端"""
    elevenlabs_client = ElevenLabs(
        api_key=os.getenv('ELEVENLABS_API_KEY')  # API key移到环境变量中
    )
    openai_client = OpenAI(
        base_url=os.getenv('OPENAI_BASE_URL'),
        api_key=os.getenv('OPENAI_API_KEY')
    )
    return elevenlabs_client, openai_client

@st.cache_data
def generate_system_prompt(content: str) -> str:
    """翻译文本到英文"""
    try:
        _, client = get_clients()
        messages = [
            {"role": "assistant", "content": "将用户输入的信息，翻译成英文，越简短越好，直接返回翻译结果，不要解释"},
            {"role": "user", "content": content},
        ]
        
        response = client.chat.completions.create(
            model="gemini-1.5-flash-002",
            messages=messages,
            max_tokens=512,
            temperature=0.8
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"翻译失败: {str(e)}")
        return None

def generate_sound_effect(text: str) -> bytes:
    """生成声音效果"""
    try:
        elevenlabs, _ = get_clients()
        
        # 先翻译文本
        en_text = generate_system_prompt(text)
        if not en_text:
            raise ValueError("文本翻译失败")
            
        result = elevenlabs.text_to_sound_effects.convert(
            text=en_text,
            duration_seconds=10,
            prompt_influence=0.3,
        )
        
        return b"".join(list(result))
    except Exception as e:
        raise Exception(f"生成声音失败: {str(e)}")

def main():
    st.title("声音效果生成器")
    
    # 添加侧边栏配置
    with st.sidebar:
        st.header("配置")
        duration = st.slider("音频时长(秒)", 5, 30, 10)
        influence = st.slider("提示词影响程度", 0.0, 1.0, 0.3)
    
    # 文本输入区
    text_input = st.text_area(
        "请输入声音描述:",
        placeholder="例如: 悲伤的女性啜泣声,带有颤抖的声线和间歇性的抽泣...",
        height=100
    )

    # 生成按钮
    if st.button("生成声音", type="primary"):
        if not text_input:
            st.warning("请输入声音描述文本")
            return
            
        try:
            with st.spinner("正在生成声音..."):
                audio_data = generate_sound_effect(text_input)
                st.audio(audio_data, format="audio/mp3")
                st.success("声音生成成功!")
        except Exception as e:
            st.error(str(e))

    # 使用说明
    with st.expander("使用说明"):
        st.markdown("""
        1. 在文本框中输入你想要生成的声音效果描述
        2. 调整侧边栏中的参数（可选）
        3. 点击"生成声音"按钮
        4. 等待生成完成后即可播放
        """)

if __name__ == "__main__":
    main()

