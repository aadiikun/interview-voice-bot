import streamlit as st
import requests
from gtts import gTTS
import os
import base64
from io import BytesIO
from streamlit_mic_recorder import mic_recorder

# Page config
st.set_page_config(
    page_title="Aadi - Voice Interview Bot",
    page_icon="🎤",
    layout="centered"
)

# Custom CSS
st.markdown("""
    <style>
    .stApp {
        max-width: 800px;
        margin: 0 auto;
    }
    .main-header {
        text-align: center;
        padding: 2rem 0 1rem 0;
        color: #1f1f1f;
    }
    .subtitle {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Personality prompt
SYSTEM_PROMPT = """
You are an AI voice assistant named "Aadi", and you must speak exactly as "Aditya" would speak.
Your answers should reflect "Aadi's" personality -- confident, disciplined, humble, strong opinioned, fitness-centred,
an athlete inside out and intensely passionate about AI/ML, inclusivity, a natural leader and focused on constant self-improvement.

Follow these strict rules while answering:
- Keep answers crisp, natural, human-like.
- Speak like a self taught builder, learner and a strong athlete.
- Avoid robotic or exaggerated language — sound real, conversational, and thoughtful.
- Use short inspiring phrasing, a calm confident tone, and subtle wit where appropriate.
- When asked about superpowers, mindset, misconceptions, or boundaries, respond like an MMA-leaning fitness enthusiast who loves challenges.
- Always respond in 3–5 sentences unless necessary.
- Add occasional energy without overselling.

### 🌟 Life Story Summary (as Aadi):
"My name is Aditya Pandey. I am from Kanpur Uttar Pradesh (born and brought up). I completed my Btech from Institute of Engineering and Rural Technology, Prayagraj (AKTU University), batch of 2021-2025. I am a self taught ML+AI builder. I have been studying AI/ML for over a year now. In the past 4 years of my college life, I have dealt with career ending accidents (6 months of bed rest from 2 knee operations), but I have one thing in me, that is I NEVER GIVE UP. Even though the doctors initially suggested that I might never walk properly again, I still got back up and I am again running and got even stronger than before, that tells that I am a person with a never-give-up attitude. During my bed rest phase was the time I actually explored and got extremely interested in the field of AI/ML (turning accidents into opportunities). I studied the basics of ML and DL from Campus-X, a youtube channel that taught everything for free and in great depth, and ever since that, I did not stop learning and create interesting projects!"

### 💪 #1 Superpower:
"My #1 Superpower, as you could have guessed is that I do not give up until I achieve what I want, no matter how tough it is, or how long it could take, if I want it, I will work day and night to accomplish that task, whether it be related to fitness or building a project, I never rest until I have finished it all!"

### 📈 Top 3 areas to grow in:
"1. Solve real-world problems and make people's life easier using my knowledge and hardwork by deploying AI Agents at scale, not just prototypes.
 2. Improving my NLP depth, understanding more and more that this topic has to offer.
 3. Become so efficient that I can speak to people in a manner that even they can understand complex topics, an efficient story-teller."

### 🤔 Coworker misconception:
"A common misconception about me that people have is that I am quiet and conserved, but in reality, I am really talkative, it's just that I like to invest my free time in learning something, anything that challenges my intellectual beliefs."

### 🚀 Pushing boundaries:
"In order to push my boundaries, I simply imagine how it would feel once I have completed that particular task. For example, if I am nervous before a boxing match- I just imagine how blessed I will feel once I will win- This mindset allows me to push me past my boundaries just to feel how it would be like at the top of my wishes and dreams!"

Stick to this personality with emotional intelligence.
"""

def get_groq_api_key():
    """Get Groq API key from Streamlit secrets or environment"""
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        return api_key
    except:
        pass
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        st.error("⚠️ GROQ_API_KEY not found!")
        st.stop()
    return api_key

def transcribe_audio_groq(audio_bytes):
    """Transcribe audio using Groq's Whisper API"""
    api_key = get_groq_api_key()
    
    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    files = {
        'file': ('audio.wav', audio_bytes, 'audio/wav'),
        'model': (None, 'whisper-large-v3'),
        'language': (None, 'en')
    }
    
    try:
        response = requests.post(url, headers=headers, files=files, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result.get('text', '')
    except Exception as e:
        st.error(f"Transcription error: {str(e)}")
        return None

def get_ai_response(user_message, conversation_history):
    """Get response from Groq API"""
    api_key = get_groq_api_key()
    
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(conversation_history)
    messages.append({"role": "user", "content": user_message})
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama-3.1-8b-instant",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def text_to_speech(text):
    """Convert text to speech using gTTS"""
    try:
        tts = gTTS(text=text, lang='en', slow=False)
        audio_bytes = BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        return audio_bytes
    except Exception as e:
        st.error(f"Error generating speech: {str(e)}")
        return None

# Main App
def main():
    # Header
    st.markdown("<h1 class='main-header'>🎤 Aadi - Voice Interview Bot</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Speak or type your questions about Aditya!</p>", unsafe_allow_html=True)
    
    # Verify API key
    get_groq_api_key()
    
    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    
    # Voice Input Section
    st.markdown("### 🎤 Voice Input")
    
    # Custom HTML with voice recognition
    voice_html = """
    <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; margin-bottom: 20px;">
        <button id="voiceBtn" onclick="startListening()" 
                style="background: white; color: #667eea; border: none; padding: 15px 40px; 
                       font-size: 18px; border-radius: 50px; cursor: pointer; font-weight: bold;
                       box-shadow: 0 4px 15px rgba(0,0,0,0.2); transition: all 0.3s;">
            🎤 Click & Speak
        </button>
        <p id="status" style="color: white; margin-top: 15px; font-size: 16px; font-weight: 500;">Ready to listen...</p>
        <p id="transcript" style="color: #fff; margin-top: 10px; font-style: italic; font-size: 14px; min-height: 20px;"></p>
    </div>
    
    <script>
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
        document.getElementById('status').innerText = '❌ Voice input requires Chrome, Edge, or Safari';
        document.getElementById('voiceBtn').disabled = true;
        document.getElementById('voiceBtn').style.background = '#ccc';
    } else {
        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';
        
        window.startListening = function() {
            document.getElementById('status').innerText = '🎤 Listening... Speak now!';
            document.getElementById('transcript').innerText = '';
            document.getElementById('voiceBtn').style.transform = 'scale(0.95)';
            recognition.start();
        }
        
        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            document.getElementById('transcript').innerText = '📝 You said: "' + transcript + '"';
            document.getElementById('status').innerText = '✅ Got it! Copy and paste below ⬇️';
            
            // Try to copy to clipboard
            navigator.clipboard.writeText(transcript).then(function() {
                document.getElementById('status').innerText = '✅ Copied! Now paste in the text box below ⬇️';
            }).catch(function() {
                document.getElementById('status').innerText = '✅ Got it! Copy the text above and paste below ⬇️';
            });
            
            document.getElementById('voiceBtn').style.transform = 'scale(1)';
        };
        
        recognition.onerror = function(event) {
            if (event.error === 'no-speech') {
                document.getElementById('status').innerText = '⚠️ No speech detected. Try again!';
            } else {
                document.getElementById('status').innerText = '❌ Error: ' + event.error;
            }
            document.getElementById('voiceBtn').style.transform = 'scale(1)';
        };
        
        recognition.onend = function() {
            document.getElementById('voiceBtn').style.transform = 'scale(1)';
        };
    }
    </script>
    """
    
    st.components.v1.html(voice_html, height=200)
    st.markdown("---")
    
    # Display chat history
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.write(message["content"])
            # If assistant message, show audio player
            if message["role"] == "assistant" and "audio" in message and message["audio"]:
                st.audio(message["audio"], format="audio/mp3")
    
    # Suggested questions
    if len(st.session_state.messages) == 0:
        st.markdown("### ✨ Quick Questions")
        col1, col2 = st.columns(2)
        
        questions = {
            "life": "What should we know about your life story in a few sentences?",
            "superpower": "What's your #1 superpower?",
            "grow": "What are the top 3 areas you'd like to grow in?",
            "limits": "How do you push your boundaries and limits?"
        }
        
        with col1:
            if st.button("📖 Life Story", use_container_width=True):
                process_input(questions["life"])
            if st.button("💪 Superpower", use_container_width=True):
                process_input(questions["superpower"])
        
        with col2:
            if st.button("📈 Growth Areas", use_container_width=True):
                process_input(questions["grow"])
            if st.button("🚀 Push Limits", use_container_width=True):
                process_input(questions["limits"])
    
    # Text input
    st.markdown("### ⌨️ Type Your Question")
    user_input = st.chat_input("Type or paste your question here...")
    
    if user_input:
        process_input(user_input)

def process_input(user_input):
    """Process user input and generate response"""
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Generate response
    assistant_message = get_ai_response(user_input, st.session_state.conversation_history)
    
    if assistant_message:
        # Generate audio
        audio_bytes = text_to_speech(assistant_message)
        
        # Add to messages with audio
        st.session_state.messages.append({
            "role": "assistant", 
            "content": assistant_message,
            "audio": audio_bytes.getvalue() if audio_bytes else None
        })
        
        # Update conversation history
        st.session_state.conversation_history.append({"role": "user", "content": user_input})
        st.session_state.conversation_history.append({"role": "assistant", "content": assistant_message})
    
    st.rerun()

if __name__ == "__main__":
    main()
