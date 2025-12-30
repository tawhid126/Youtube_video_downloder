#!/usr/bin/env python3
"""
YouTube Video Downloader - Streamlit App
Web interface for downloading YouTube videos
"""

import streamlit as st
import subprocess
import sys
import os
import yt_dlp
from pathlib import Path

# Set page config
st.set_page_config(
    page_title="YouTube Downloader",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #ff0000, #cc0000);
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 10px;
        padding: 15px;
        font-size: 16px;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #ff3333, #ff0000);
        box-shadow: 0 4px 15px rgba(255, 0, 0, 0.3);
    }
    .success-box {
        padding: 20px;
        background: #00c853;
        color: white;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
    }
    .error-box {
        padding: 20px;
        background: #ff5252;
        color: white;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Default download folder
DOWNLOAD_FOLDER = os.path.expanduser("~/Downloads/YouTube")

def get_quality_format(quality):
    """Get the format string for the desired quality"""
    quality_formats = {
        "2160": "bestvideo[height<=2160][ext=mp4]+bestaudio[ext=m4a]/best[height<=2160][ext=mp4]/best",
        "1080": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best",
        "720": "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best",
        "480": "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]/best",
    }
    return quality_formats.get(quality, quality_formats["1080"])

def get_video_info(url):
    """Get video information without downloading"""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            return {
                'success': True,
                'title': info.get('title', 'Unknown'),
                'channel': info.get('channel', 'Unknown'),
                'duration': info.get('duration', 0),
                'thumbnail': info.get('thumbnail', ''),
                'views': info.get('view_count', 0),
                'description': info.get('description', '')[:200] + '...',
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def format_duration(seconds):
    """Format duration in seconds to HH:MM:SS"""
    if not seconds:
        return "Unknown"
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"

def download_video(url, quality, output_path):
    """Download a YouTube video"""
    os.makedirs(output_path, exist_ok=True)
    
    ydl_opts = {
        'format': get_quality_format(quality),
        'outtmpl': f'{output_path}/%(title)s_%(height)sp.%(ext)s',
        'merge_output_format': 'mp4',
        'quiet': False,
        'no_warnings': False,
        'noplaylist': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return {
                'success': True,
                'title': info.get('title', 'Unknown'),
                'filename': f"{output_path}/{info.get('title', 'Unknown')}_{info.get('height', quality)}p.mp4"
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

# Main App
st.title("🎬 YouTube Video Downloader")
st.markdown("### Download YouTube videos in high quality")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Output folder
    output_folder = st.text_input(
        "📁 Download Folder",
        value=DOWNLOAD_FOLDER,
        help="Videos will be saved here"
    )
    
    st.markdown("---")
    st.markdown("### 📊 Statistics")
    if os.path.exists(output_folder):
        files = list(Path(output_folder).glob("*.mp4"))
        st.metric("Downloaded Videos", len(files))
        
        if files:
            total_size = sum(f.stat().st_size for f in files) / (1024**3)
            st.metric("Total Size", f"{total_size:.2f} GB")
    
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.info("""
    **YouTube Downloader**
    
    Download videos in:
    - 4K (2160p)
    - 1080p Full HD
    - 720p HD
    - 480p SD
    
    Files are saved as MP4
    """)

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    url = st.text_input(
        "🔗 Enter YouTube URL",
        placeholder="https://www.youtube.com/watch?v=..."
    )

with col2:
    quality = st.selectbox(
        "📊 Quality",
        options=["2160", "1080", "720", "480"],
        format_func=lambda x: {
            "2160": "4K (2160p)",
            "1080": "1080p Full HD",
            "720": "720p HD",
            "480": "480p SD"
        }[x],
        index=1
    )

# Get video info button
if url:
    if st.button("🔍 Get Video Info"):
        with st.spinner("Fetching video information..."):
            info = get_video_info(url)
            
            if info['success']:
                st.success("✅ Video found!")
                
                # Display video info
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    if info['thumbnail']:
                        st.image(info['thumbnail'], use_container_width=True)
                
                with col2:
                    st.markdown(f"### {info['title']}")
                    st.markdown(f"**📺 Channel:** {info['channel']}")
                    st.markdown(f"**⏱️ Duration:** {format_duration(info['duration'])}")
                    st.markdown(f"**👁️ Views:** {info['views']:,}")
                    
                    with st.expander("📝 Description"):
                        st.write(info['description'])
                
                st.session_state['video_info'] = info
            else:
                st.error(f"❌ Error: {info['error']}")

# Download button
st.markdown("---")

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    if st.button("⬇️ Download Video", type="primary", disabled=not url):
        if url:
            with st.spinner(f"Downloading in {quality}p quality..."):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                status_text.text("🚀 Starting download...")
                progress_bar.progress(20)
                
                result = download_video(url, quality, output_folder)
                
                progress_bar.progress(100)
                
                if result['success']:
                    st.markdown(f"""
                    <div class="success-box">
                        <h2>✅ Download Complete!</h2>
                        <p>📁 Saved to: {result['filename']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.balloons()
                else:
                    st.markdown(f"""
                    <div class="error-box">
                        <h2>❌ Download Failed</h2>
                        <p>{result['error']}</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ Please enter a YouTube URL first!")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Made with ❤️ using Streamlit | For personal use only</p>
</div>
""", unsafe_allow_html=True)
