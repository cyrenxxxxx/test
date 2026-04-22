from flask import Flask, request, render_template_string, jsonify
import yt_dlp
import random
from functools import lru_cache
import threading
import time
import socket

app = Flask(__name__)

RANDOM_KEYWORDS = ['kpop top', 'pop hits', 'rock classics', 'rnb vibes', 'chill lofi', 'dance edm', 'indie folk', 'jazz cafe', 'hip hop beats', 'alternative rock', 'kpop 2025', 'kpop 2026', 'bigbang', 'blackpink', 'bts', 'new jeans', 'twice', 'seventeen']

@lru_cache(maxsize=200)
def get_cached_stream_url(video_id):
    ydl_opts = {
        'format': 'bestaudio',
        'quiet': True,
        'no_warnings': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
        return info['url']

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no, viewport-fit=cover">
    <title>Web Music</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            -webkit-tap-highlight-color: transparent;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background: #000000;
            width: 100vw;
            height: 100vh;
            overflow: hidden;
            position: fixed;
            top: 0;
            left: 0;
        }

        .main-page {
            width: 100%;
            height: 100%;
            background: linear-gradient(180deg, #0a0a0a 0%, #000000 100%);
            position: relative;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .header {
            position: sticky;
            top: 0;
            left: 0;
            right: 0;
            padding: 12px 24px;
            background: none;
            backdrop-filter: blur(20px);
            z-index: 50;
            display: flex;
            justify-content: flex-end;
            align-items: center;
            flex-shrink: 0;
        }

        .library-title {
            color: white;
            font-size: 28px;
            font-weight: 700;
            letter-spacing: -0.5px;
            position: absolute;
            left: 24px;
        }

        .search-icon-btn {
            width: 44px;
            height: 44px;
            border-radius: 30px;
            background: rgba(255,255,255,0.1);
            border: none;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s ease;
        }

        .search-icon-btn:active {
            transform: scale(0.96);
            background: rgba(255,255,255,0.2);
        }

        .search-icon-btn svg {
            width: 22px;
            height: 22px;
            fill: white;
        }

        .song-list-container {
            flex: 1;
            overflow-y: auto;
            padding: 0 24px 140px 24px;
            scroll-behavior: smooth;
        }

        .song-list-container::-webkit-scrollbar {
            width: 4px;
        }

        .song-list-container::-webkit-scrollbar-track {
            background: rgba(255,255,255,0.05);
            border-radius: 10px;
        }

        .song-list-container::-webkit-scrollbar-thumb {
            background: #1DB954;
            border-radius: 10px;
        }

        .song-list {
            display: flex;
            flex-direction: column;
            gap: 16px;
        }

        .song-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid rgba(255,255,255,0.06);
            cursor: pointer;
            transition: all 0.2s;
        }

        .song-item:active {
            background: rgba(255,255,255,0.05);
            padding-left: 8px;
        }

        .song-info {
            flex: 1;
        }

        .song-name {
            color: white;
            font-size: 17px;
            font-weight: 500;
            margin-bottom: 4px;
        }

        .song-artist-name {
            color: rgba(255,255,255,0.5);
            font-size: 13px;
        }

        .song-duration {
            color: rgba(255,255,255,0.4);
            font-size: 13px;
            font-family: monospace;
        }

        .refresh-indicator {
            position: fixed;
            top: 60px;
            left: 50%;
            transform: translateX(-50%);
            background: none;
            backdrop-filter: blur(20px);
            padding: 8px 20px;
            border-radius: 30px;
            color: #1DB954;
            font-size: 13px;
            z-index: 150;
            opacity: 0;
            transition: opacity 0.2s;
            pointer-events: none;
            white-space: nowrap;
        }

        .search-popup {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.96);
            backdrop-filter: blur(30px);
            z-index: 200;
            transform: translateY(-100%);
            transition: transform 0.35s cubic-bezier(0.2, 0.9, 0.4, 1.1);
            display: flex;
            flex-direction: column;
            padding-top: 60px;
        }

        .search-popup.active {
            transform: translateY(0);
        }

        .search-popup-header {
            padding: 0 24px 20px 24px;
            display: flex;
            align-items: center;
            gap: 16px;
            flex-shrink: 0;
        }

        .search-popup-input {
            flex: 1;
            padding: 16px 20px;
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.12);
            border-radius: 40px;
            color: white;
            font-size: 16px;
            outline: none;
        }

        .search-popup-input:focus {
            border-color: #1DB954;
            background: rgba(255,255,255,0.12);
        }

        .close-popup-btn {
            width: 44px;
            height: 44px;
            border-radius: 30px;
            background: rgba(255,255,255,0.08);
            border: none;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .close-popup-btn:active {
            transform: scale(0.96);
        }

        .search-results-container {
            flex: 1;
            overflow-y: auto;
            padding: 0 24px 30px 24px;
        }

        .search-results-container::-webkit-scrollbar {
            width: 4px;
        }

        .search-results-container::-webkit-scrollbar-track {
            background: rgba(255,255,255,0.05);
            border-radius: 10px;
        }

        .search-results-container::-webkit-scrollbar-thumb {
            background: #1DB954;
            border-radius: 10px;
        }

        .search-suggestions {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        .search-suggestion-item {
            padding: 12px 16px;
            background: rgba(255,255,255,0.04);
            border-radius: 24px;
            cursor: pointer;
            transition: all 0.2s;
        }

        .search-suggestion-item:active {
            background: #1DB954;
            transform: translateX(4px);
        }

        .sugg-title {
            color: white;
            font-weight: 500;
            font-size: 15px;
        }

        .sugg-artist {
            color: rgba(255,255,255,0.5);
            font-size: 12px;
            margin-top: 4px;
        }

        .floating-player {
            position: fixed;
            bottom: 24px;
            left: 16px;
            right: 16px;
            background: rgba(18,18,18,0.98);
            backdrop-filter: blur(40px);
            border-radius: 60px;
            padding: 10px 16px;
            display: flex;
            align-items: center;
            gap: 12px;
            cursor: pointer;
            z-index: 100;
            border: 1px solid rgba(255,255,255,0.08);
            box-shadow: 0 8px 32px rgba(0,0,0,0.4);
            transform: translateY(200px);
            transition: transform 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55), opacity 0.4s ease-out;
            opacity: 1;
        }

        .floating-player.visible {
            transform: translateY(0);
        }

        .floating-player.fade-out {
            opacity: 0;
            transform: translateY(30px);
        }

        .floating-player.fade-in {
            opacity: 1;
            transform: translateY(0);
        }

        .floating-avatar {
            width: 48px;
            height: 48px;
            background: linear-gradient(135deg, #1DB954, #0d6e2f);
            border-radius: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .floating-avatar.rotating {
            animation: spinFloating 2s linear infinite;
        }

        @keyframes spinFloating {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }

        .floating-avatar svg {
            width: 24px;
            height: 24px;
            fill: white;
        }

        .floating-info {
            flex: 1;
        }

        .floating-title {
            color: white;
            font-weight: 600;
            font-size: 14px;
        }

        .floating-artist {
            color: rgba(255,255,255,0.5);
            font-size: 12px;
        }

        .floating-play-icon {
            width: 44px;
            height: 44px;
            background: #1DB954;
            border-radius: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            border: none;
            cursor: pointer;
        }

        .floating-play-icon:active {
            transform: scale(0.96);
        }

        .fullscreen-player {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: radial-gradient(circle at 40% 30%, #1a1a2e, #0a0a0a);
            z-index: 300;
            transform: translateY(100%);
            transition: transform 0.4s cubic-bezier(0.2, 0.9, 0.4, 1.1);
            display: flex;
            flex-direction: column;
        }

        .fullscreen-player.active {
            transform: translateY(0);
        }

        .player-header {
            padding: 20px 24px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-shrink: 0;
            position: relative;
        }

        /* DESKTOP BACK BUTTON - transparent with arrow pointing down */
        .desktop-back-btn {
            width: 44px;
            height: 44px;
            border-radius: 30px;
            background: rgba(255,255,255,0.1);
            border: none;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s ease;
            position: absolute;
            left: 24px;
            top: 20px;
        }

        .desktop-back-btn:hover {
            background: rgba(255,255,255,0.2);
            transform: scale(1.05);
        }

        .desktop-back-btn:active {
            transform: scale(0.96);
        }

        .desktop-back-btn svg {
            width: 24px;
            height: 24px;
            fill: white;
        }

        /* Hide desktop back button on mobile (touch devices) */
        @media (max-width: 768px) {
            .desktop-back-btn {
                display: none;
            }
        }

        /* NOW PLAYING floating badge with note icon */
        .now-playing-badge {
            position: absolute;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(29, 185, 84, 0.15);
            backdrop-filter: blur(10px);
            padding: 6px 16px;
            border-radius: 30px;
            border: 1px solid rgba(29, 185, 84, 0.3);
            pointer-events: none;
            z-index: 10;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .now-playing-badge span {
            color: #1DB954;
            font-size: 12px;
            font-weight: 500;
            letter-spacing: 0.5px;
        }

        .now-playing-badge svg {
            width: 14px;
            height: 14px;
            fill: #1DB954;
        }

        .drag-area {
            width: 100%;
            height: 40px;
            cursor: grab;
            opacity: 0;
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
        }
        
        .drag-area:active {
            cursor: grabbing;
        }

        /* Show drag area only on mobile */
        @media (min-width: 769px) {
            .drag-area {
                display: none;
            }
        }

        .player-content {
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 40px 24px;
        }

        .disc-container {
            width: 280px;
            height: 280px;
            margin-bottom: 48px;
            position: relative;
        }

        .rotating-disc {
            width: 100%;
            height: 100%;
            background: linear-gradient(145deg, #2a2a3e, #1a1a2a);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 30px 50px rgba(0,0,0,0.5);
            position: relative;
        }

        .rotating-disc.rotating {
            animation: spin 4s linear infinite;
        }

        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }

        .disc-inner {
            width: 120px;
            height: 120px;
            background: rgba(0,0,0,0.5);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .note-icon {
            width: 50px;
            height: 50px;
            fill: rgba(255,255,255,0.8);
        }

        .player-song-title {
            font-size: 28px;
            font-weight: 700;
            color: white;
            text-align: center;
            margin-bottom: 8px;
        }

        .player-song-artist {
            font-size: 18px;
            color: rgba(255,255,255,0.6);
            text-align: center;
            margin-bottom: 40px;
        }

        .player-progress {
            width: 100%;
            max-width: 400px;
            margin-bottom: 32px;
        }

        .progress-track {
            width: 100%;
            height: 6px;
            background: rgba(255,255,255,0.15);
            border-radius: 10px;
            cursor: pointer;
            position: relative;
        }

        .progress-fill-player {
            width: 0%;
            height: 100%;
            background: #1DB954;
            border-radius: 10px;
            position: relative;
            transition: width 0.05s linear;
        }

        .progress-fill-player::after {
            content: '';
            width: 12px;
            height: 12px;
            background: white;
            border-radius: 50%;
            position: absolute;
            right: -6px;
            top: -3px;
            box-shadow: 0 0 8px #1DB954;
        }

        .player-time {
            display: flex;
            justify-content: space-between;
            margin-top: 8px;
            color: rgba(255,255,255,0.5);
            font-size: 12px;
        }

        .player-controls {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 48px;
        }

        .skip-btn {
            background: transparent;
            border: none;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 12px;
            opacity: 0.7;
            transition: all 0.2s;
        }

        .skip-btn:active {
            opacity: 1;
            transform: scale(0.95);
        }

        .skip-btn svg {
            width: 28px;
            height: 28px;
            fill: white;
        }

        .player-play-btn {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            background: #1DB954;
            border: none;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s;
        }

        .player-play-btn:active {
            transform: scale(0.96);
        }

        .player-play-btn svg {
            width: 36px;
            height: 36px;
            fill: white;
        }
    </style>
</head>
<body>

<div class="main-page" id="mainPage">
    <div class="header">
        <div class="library-title">Your Library</div>
        <button class="search-icon-btn" id="mainSearchBtn">
            <svg viewBox="0 0 24 24"><path d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zM9.5 14C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg>
        </button>
    </div>
    <div class="refresh-indicator" id="refreshIndicator">↓ pull down to refresh</div>
    <div class="song-list-container" id="songListContainer">
        <div class="song-list" id="songList">
            <div style="color:rgba(255,255,255,0.5); text-align:center; padding:40px;">Loading 50 songs...</div>
        </div>
    </div>
</div>

<div class="search-popup" id="searchPopup">
    <div class="search-popup-header">
        <input type="text" class="search-popup-input" id="popupSearchInput" placeholder="Search songs, artists..." autocomplete="off">
        <button class="close-popup-btn" id="closePopupBtn">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="white"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>
        </button>
    </div>
    <div class="search-results-container" id="searchResultsContainer">
        <div class="search-suggestions" id="searchSuggestions"></div>
    </div>
</div>

<div class="floating-player" id="floatingPlayer">
    <div class="floating-avatar" id="floatingAvatar">
        <svg viewBox="0 0 24 24"><path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z"/></svg>
    </div>
    <div class="floating-info">
        <div class="floating-title" id="floatTitle">Select a song</div>
        <div class="floating-artist" id="floatArtist">-</div>
    </div>
    <button class="floating-play-icon" id="floatPlayBtn">
        <svg viewBox="0 0 24 24" width="20" height="20" fill="white"><path d="M8 5v14l11-7z"/></svg>
    </button>
</div>

<div class="fullscreen-player" id="fullscreenPlayer">
    <div class="player-header">
        <!-- DESKTOP BACK BUTTON - arrow pointing down -->
        <button class="desktop-back-btn" id="desktopBackBtn">
            <svg viewBox="0 0 24 24">
                <path d="M12 16l-6-6 1.41-1.41L12 13.17l4.59-4.58L18 10z"/>
            </svg>
        </button>
        
        <!-- NOW PLAYING floating badge with note icon -->
        <div class="now-playing-badge">
            <svg viewBox="0 0 24 24">
                <path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z"/>
            </svg>
            <span>NOW PLAYING</span>
        </div>
        
        <div class="drag-area" id="dragArea"></div>
    </div>
    <div class="player-content">
        <div class="disc-container">
            <div class="rotating-disc" id="rotatingDisc">
                <div class="disc-inner">
                    <svg class="note-icon" viewBox="0 0 24 24">
                        <path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z"/>
                    </svg>
                </div>
            </div>
        </div>
        <div class="player-song-title" id="fullTitle">Ready</div>
        <div class="player-song-artist" id="fullArtist">-</div>
        <div class="player-progress">
            <div class="progress-track" id="fullProgressTrack">
                <div class="progress-fill-player" id="fullProgressFill"></div>
            </div>
            <div class="player-time">
                <span id="fullCurrent">00:00</span>
                <span id="fullDuration">00:00</span>
            </div>
        </div>
        <div class="player-controls">
            <button class="skip-btn" id="skipBackBtn">
                <svg viewBox="0 0 24 24"><path d="M11.99 5V1l-5 5 5 5V7c3.31 0 6 2.69 6 6s-2.69 6-6 6-6-2.69-6-6h-2c0 4.42 3.58 8 8 8s8-3.58 8-8-3.58-8-8-8z"/><path d="M10 16l-4-4 4-4v8z"/></svg>
            </button>
            <button class="player-play-btn" id="fullPlayBtn">
                <svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
            </button>
            <button class="skip-btn" id="skipForwardBtn">
                <svg viewBox="0 0 24 24"><path d="M12.01 5V1l5 5-5 5V7c-3.31 0-6 2.69-6 6s2.69 6 6 6 6-2.69 6-6h2c0 4.42-3.58 8-8 8s-8-3.58-8-8 3.58-8 8-8z"/><path d="M13 16l4-4-4-4v8z"/></svg>
            </button>
        </div>
    </div>
</div>

<script>
    let audio = new Audio();
    let currentSong = null;
    let isPlayingGlobal = false;
    let progressInterval = null;
    let currentSongList = [];
    let lastScrollY = 0;
    let scrollTimeout = null;

    async function loadRandomLibrary() {
        const container = document.getElementById('songList');
        container.innerHTML = '<div style="color:rgba(255,255,255,0.5); text-align:center; padding:40px;">Loading 50 songs...</div>';
        try {
            let res = await fetch('/random-songs');
            let songs = await res.json();
            currentSongList = songs;
            renderSongList(songs);
        } catch(e) {
            container.innerHTML = '<div style="color:rgba(255,255,255,0.5); text-align:center; padding:40px;">Error loading. Pull to refresh.</div>';
        }
    }

    function renderSongList(songs) {
        const container = document.getElementById('songList');
        container.innerHTML = '';
        songs.forEach(song => {
            const div = document.createElement('div');
            div.className = 'song-item';
            div.innerHTML = `
                <div class="song-info">
                    <div class="song-name">${escapeHtml(song.title)}</div>
                    <div class="song-artist-name">${escapeHtml(song.artist)}</div>
                </div>
                <div class="song-duration">${song.duration || '03:00'}</div>
            `;
            div.onclick = () => playThisSong(song.id, song.title, song.artist);
            container.appendChild(div);
        });
    }

    function escapeHtml(str) { 
        if(!str) return '';
        return str.replace(/[&<>]/g, function(m){if(m==='&')return'&amp;';if(m==='<')return'&lt;';if(m==='>')return'&gt;';return m;}); 
    }

    function startFloatingRotation(play) {
        const floatingAvatar = document.getElementById('floatingAvatar');
        if (play) {
            floatingAvatar.classList.add('rotating');
        } else {
            floatingAvatar.classList.remove('rotating');
        }
    }

    async function playThisSong(id, title, artist) {
        if (progressInterval) clearInterval(progressInterval);
        
        audio.pause();
        audio.currentTime = 0;
        
        currentSong = { id, title, artist };
        document.getElementById('floatTitle').innerText = title;
        document.getElementById('floatArtist').innerText = artist;
        document.getElementById('fullTitle').innerText = title;
        document.getElementById('fullArtist').innerText = artist;
        
        const floatingPlayer = document.getElementById('floatingPlayer');
        floatingPlayer.classList.add('visible');
        floatingPlayer.classList.remove('fade-out');
        floatingPlayer.classList.add('fade-in');
        
        let streamRes = await fetch('/stream?id=' + encodeURIComponent(id));
        let streamUrl = await streamRes.text();
        audio.src = streamUrl;
        audio.play();
        isPlayingGlobal = true;
        updateAllPlayIcons(true);
        startRotation(true);
        startFloatingRotation(true);
        
        audio.addEventListener('loadedmetadata', () => {
            document.getElementById('fullDuration').innerText = formatTime(audio.duration);
        });
        progressInterval = setInterval(updateAllProgress, 300);
        audio.onended = () => {
            isPlayingGlobal = false;
            updateAllPlayIcons(false);
            startRotation(false);
            startFloatingRotation(false);
        };
    }

    function updateAllProgress() {
        if (!isDragging && audio.duration && !isNaN(audio.duration)) {
            let percent = (audio.currentTime / audio.duration) * 100;
            document.getElementById('fullProgressFill').style.width = percent + '%';
            document.getElementById('fullCurrent').innerText = formatTime(audio.currentTime);
        }
    }

    function formatTime(sec) { 
        if(isNaN(sec)) return '00:00'; 
        let m = Math.floor(sec/60); 
        let s = Math.floor(sec%60); 
        return m+':'+(s<10?'0':'')+s; 
    }

    function updateAllPlayIcons(playing) {
        const playIcon = `<svg viewBox="0 0 24 24" width="20" height="20" fill="white"><path d="M8 5v14l11-7z"/></svg>`;
        const pauseIcon = `<svg viewBox="0 0 24 24" width="20" height="20" fill="white"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg>`;
        const bigPlay = `<svg viewBox="0 0 24 24" width="36" height="36" fill="white"><path d="M8 5v14l11-7z"/></svg>`;
        const bigPause = `<svg viewBox="0 0 24 24" width="36" height="36" fill="white"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg>`;
        document.getElementById('floatPlayBtn').innerHTML = playing ? pauseIcon : playIcon;
        document.getElementById('fullPlayBtn').innerHTML = playing ? bigPause : bigPlay;
    }

    function startRotation(play) {
        const disc = document.getElementById('rotatingDisc');
        if (play) disc.classList.add('rotating');
        else disc.classList.remove('rotating');
    }

    function togglePlayPause() {
        if (!currentSong) return;
        if (isPlayingGlobal) { 
            audio.pause(); 
            isPlayingGlobal = false; 
            updateAllPlayIcons(false); 
            startRotation(false);
            startFloatingRotation(false);
        } else { 
            audio.play(); 
            isPlayingGlobal = true; 
            updateAllPlayIcons(true); 
            startRotation(true);
            startFloatingRotation(true);
        }
    }

    function skipBackward() {
        if (audio) audio.currentTime = Math.max(0, audio.currentTime - 10);
    }
    function skipForward() {
        if (audio && audio.duration) audio.currentTime = Math.min(audio.duration, audio.currentTime + 10);
    }

    // DESKTOP BACK BUTTON FUNCTIONALITY
    document.getElementById('desktopBackBtn').onclick = () => {
        document.getElementById('fullscreenPlayer').classList.remove('active');
    };

    document.getElementById('floatPlayBtn').onclick = (e) => { e.stopPropagation(); togglePlayPause(); };
    document.getElementById('fullPlayBtn').onclick = () => togglePlayPause();
    document.getElementById('skipBackBtn').onclick = () => skipBackward();
    document.getElementById('skipForwardBtn').onclick = () => skipForward();

    // 🔥 REAL-TIME DRAG/SLIDE SUPPORT 🔥
    const progressTrack = document.getElementById('fullProgressTrack');
    const progressFill = document.getElementById('fullProgressFill');
    const fullCurrent = document.getElementById('fullCurrent');
    let isDragging = false;

    function updateProgressUI(percent) {
        percent = Math.min(1, Math.max(0, percent));
        progressFill.style.width = (percent * 100) + '%';
        if (audio.duration && !isNaN(audio.duration)) {
            let newTime = percent * audio.duration;
            fullCurrent.innerText = formatTime(newTime);
        }
    }

    // Touch events for mobile - real time drag/slide
    progressTrack.addEventListener('touchstart', (e) => {
        isDragging = true;
        let rect = progressTrack.getBoundingClientRect();
        let percent = (e.touches[0].clientX - rect.left) / rect.width;
        updateProgressUI(percent);
        audio.currentTime = percent * audio.duration;
        e.preventDefault();
        e.stopPropagation();
    });

    progressTrack.addEventListener('touchmove', (e) => {
        if (!isDragging) return;
        let rect = progressTrack.getBoundingClientRect();
        let percent = (e.touches[0].clientX - rect.left) / rect.width;
        updateProgressUI(percent);
        audio.currentTime = percent * audio.duration;
        e.preventDefault();
        e.stopPropagation();
    });

    progressTrack.addEventListener('touchend', () => {
        isDragging = false;
        if (audio.duration) {
            let percent = audio.currentTime / audio.duration;
            updateProgressUI(percent);
        }
    });

    // Mouse events for desktop - real time drag/slide
    progressTrack.addEventListener('mousedown', (e) => {
        isDragging = true;
        let rect = progressTrack.getBoundingClientRect();
        let percent = (e.clientX - rect.left) / rect.width;
        updateProgressUI(percent);
        audio.currentTime = percent * audio.duration;
        e.preventDefault();
    });

    window.addEventListener('mousemove', (e) => {
        if (!isDragging) return;
        let rect = progressTrack.getBoundingClientRect();
        let percent = (e.clientX - rect.left) / rect.width;
        updateProgressUI(percent);
        audio.currentTime = percent * audio.duration;
    });

    window.addEventListener('mouseup', () => {
        isDragging = false;
        if (audio.duration) {
            let percent = audio.currentTime / audio.duration;
            updateProgressUI(percent);
        }
    });

    // Scroll to fade/bounce effect
    const songContainer = document.getElementById('songListContainer');
    const floatingPlayer = document.getElementById('floatingPlayer');
    
    songContainer.addEventListener('scroll', () => {
        const currentScrollY = songContainer.scrollTop;
        
        if (scrollTimeout) clearTimeout(scrollTimeout);
        
        if (currentScrollY > lastScrollY + 5 && currentScrollY > 60) {
            if (floatingPlayer.classList.contains('visible') && !floatingPlayer.classList.contains('fade-out')) {
                floatingPlayer.classList.add('fade-out');
                floatingPlayer.classList.remove('fade-in');
            }
        } else if (currentScrollY < lastScrollY - 5) {
            if (floatingPlayer.classList.contains('visible') && floatingPlayer.classList.contains('fade-out')) {
                floatingPlayer.classList.remove('fade-out');
                floatingPlayer.classList.add('fade-in');
                scrollTimeout = setTimeout(() => {
                    floatingPlayer.classList.remove('fade-in');
                }, 500);
            }
        }
        
        lastScrollY = currentScrollY;
    });

// Drag down to close fullscreen player - smooth 60fps drag (mobile only)
const fullscreenPlayer = document.getElementById('fullscreenPlayer');
let touchStartYFull = 0;
let touchStartXFull = 0;
let isDraggingProgressBar = false;
let isDraggingPlayer = false;
let shouldClose = false;
let screenHeight = window.innerHeight;
let closeThreshold = screenHeight * 0.3;
let rafId = null;
let currentDiffY = 0;

window.addEventListener('resize', () => {
    screenHeight = window.innerHeight;
    closeThreshold = screenHeight * 0.3;
});

progressTrack.addEventListener('touchstart', (e) => {
    isDraggingProgressBar = true;
});

progressTrack.addEventListener('touchend', () => {
    setTimeout(() => { isDraggingProgressBar = false; }, 100);
});

function updatePlayerPosition() {
    if (!isDraggingPlayer) return;
    
    let maxDrag = screenHeight * 0.8;
    let newTranslateY = Math.min(currentDiffY, maxDrag);
    fullscreenPlayer.style.transform = `translateY(${newTranslateY}px)`;
    
    if (currentDiffY > closeThreshold) {
        shouldClose = true;
    } else {
        shouldClose = false;
    }
    
    rafId = null;
}

fullscreenPlayer.addEventListener('touchstart', (e) => {
    if (e.target.closest('#fullProgressTrack')) {
        return;
    }
    isDraggingPlayer = true;
    touchStartYFull = e.touches[0].clientY;
    touchStartXFull = e.touches[0].clientX;
    shouldClose = false;
    currentDiffY = 0;
    
    fullscreenPlayer.style.transition = 'none';
    fullscreenPlayer.style.willChange = 'transform';
});

fullscreenPlayer.addEventListener('touchmove', (e) => {
    if (isDraggingProgressBar || e.target.closest('#fullProgressTrack')) {
        return;
    }
    if (!isDraggingPlayer) return;
    
    let diffY = e.touches[0].clientY - touchStartYFull;
    let diffX = Math.abs(e.touches[0].clientX - touchStartXFull);
    
    if (diffY > 0 && diffX < 50) {
        currentDiffY = diffY;
        
        // Use requestAnimationFrame for smooth 60fps
        if (rafId === null) {
            rafId = requestAnimationFrame(updatePlayerPosition);
        }
        e.preventDefault();
    }
});

fullscreenPlayer.addEventListener('touchend', () => {
    isDraggingPlayer = false;
    
    if (rafId) {
        cancelAnimationFrame(rafId);
        rafId = null;
    }
    
    fullscreenPlayer.style.willChange = '';
    
    if (shouldClose && fullscreenPlayer.classList.contains('active')) {
        fullscreenPlayer.style.transform = '';
        fullscreenPlayer.style.transition = '';
        fullscreenPlayer.classList.remove('active');
    } else {
        fullscreenPlayer.style.transition = 'transform 0.35s cubic-bezier(0.2, 0.9, 0.4, 1.1)';
        fullscreenPlayer.style.transform = '';
        setTimeout(() => {
            if (fullscreenPlayer.style.transition) {
                fullscreenPlayer.style.transition = '';
            }
        }, 350);
    }
    
    shouldClose = false;
    touchStartYFull = 0;
    touchStartXFull = 0;
    currentDiffY = 0;
});

const originalObserver = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
        if (mutation.attributeName === 'class') {
            if (fullscreenPlayer.classList.contains('active')) {
                fullscreenPlayer.style.transform = '';
                fullscreenPlayer.style.transition = '';
                fullscreenPlayer.style.willChange = '';
            }
        }
    });
});
originalObserver.observe(fullscreenPlayer, { attributes: true });

    document.getElementById('floatingPlayer').onclick = (e) => { 
        if(e.target.tagName !== 'BUTTON' && e.target.closest('.floating-play-icon') === null) 
            document.getElementById('fullscreenPlayer').classList.add('active'); 
    };

    const searchBtn = document.getElementById('mainSearchBtn');
    const popup = document.getElementById('searchPopup');
    const closePopup = document.getElementById('closePopupBtn');
    const searchInput = document.getElementById('popupSearchInput');
    const suggestionsDiv = document.getElementById('searchSuggestions');

    searchBtn.onclick = () => popup.classList.add('active');
    closePopup.onclick = () => { popup.classList.remove('active'); suggestionsDiv.innerHTML = ''; searchInput.value = ''; };
    
    let debounce;
    searchInput.oninput = () => {
        clearTimeout(debounce);
        let q = searchInput.value.trim();
        if (q.length < 2) { suggestionsDiv.innerHTML = ''; return; }
        debounce = setTimeout(() => fetchSuggestions(q), 400);
    };
    
    async function fetchSuggestions(q) {
        let res = await fetch('/suggest?q=' + encodeURIComponent(q));
        let songs = await res.json();
        suggestionsDiv.innerHTML = '';
        songs.forEach(s => {
            let div = document.createElement('div');
            div.className = 'search-suggestion-item';
            div.innerHTML = `<div class="sugg-title">${escapeHtml(s.title)}</div><div class="sugg-artist">${escapeHtml(s.artist)}</div>`;
            div.onclick = () => { 
                playThisSong(s.id, s.title, s.artist); 
                popup.classList.remove('active'); 
                suggestionsDiv.innerHTML = ''; 
                searchInput.value = ''; 
            };
            suggestionsDiv.appendChild(div);
        });
    }

    let touchStartYList = 0;
    let pullDistance = 0;
    let isRefreshing = false;
    
    songContainer.addEventListener('touchstart', (e) => {
        if (songContainer.scrollTop === 0 && !isRefreshing) {
            touchStartYList = e.touches[0].clientY;
            pullDistance = 0;
        }
    });
    
    songContainer.addEventListener('touchmove', (e) => {
        if (songContainer.scrollTop === 0 && touchStartYList > 0 && !isRefreshing) {
            let diff = e.touches[0].clientY - touchStartYList;
            if (diff > 0) {
                pullDistance = diff;
                let opacity = Math.min(diff / 80, 1);
                document.getElementById('refreshIndicator').style.opacity = opacity;
                document.getElementById('refreshIndicator').innerHTML = '↓ release to refresh';
                e.preventDefault();
            }
        }
    });
    
    songContainer.addEventListener('touchend', () => {
        if (pullDistance > 60 && !isRefreshing && songContainer.scrollTop === 0) {
            isRefreshing = true;
            document.getElementById('refreshIndicator').innerHTML = '⟳ refreshing...';
            document.getElementById('refreshIndicator').style.opacity = '1';
            loadRandomLibrary().then(() => {
                setTimeout(() => {
                    isRefreshing = false;
                    document.getElementById('refreshIndicator').style.opacity = '0';
                    document.getElementById('refreshIndicator').innerHTML = '';
                    pullDistance = 0;
                    touchStartYList = 0;
                }, 500);
            });
        } else {
            document.getElementById('refreshIndicator').style.opacity = '0';
            setTimeout(() => {
                document.getElementById('refreshIndicator').innerHTML = '';
            }, 200);
        }
        pullDistance = 0;
        touchStartYList = 0;
    });

    loadRandomLibrary();
</script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/random-songs')
def random_songs():
    keyword = random.choice(RANDOM_KEYWORDS)
    ydl_opts = {'quiet': True, 'extract_flat': True, 'playlistend': 50}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch50:{keyword}", download=False)
        results = []
        for entry in info['entries']:
            if entry:
                results.append({
                    'id': entry['id'],
                    'title': entry['title'][:60] if entry['title'] else 'Unknown',
                    'artist': entry.get('channel', 'Unknown Artist'),
                    'duration': entry.get('duration_string', '03:00')
                })
        return jsonify(results)

@app.route('/suggest')
def suggest():
    q = request.args.get('q')
    ydl_opts = {'quiet': True, 'extract_flat': True, 'playlistend': 10}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch10:{q}", download=False)
        results = [{'id': e['id'], 'title': e['title'], 'artist': e.get('channel', 'Unknown')} for e in info['entries'] if e]
        return jsonify(results)

@app.route('/stream')
def stream():
    vid = request.args.get('id')
    return get_cached_stream_url(vid)

# Auto-warmup function para kahit walang browser ay ready agad
def warmup_server():
    """Pre-initialize yt-dlp without needing browser"""
    time.sleep(3)
    try:
        import requests
        response = requests.get('http://localhost:5000/random-songs', timeout=10)
        if response.status_code == 200:
            print("✅ Server warmed up! Ready to stream music on any device!")
    except:
        print("✅ Server is running and ready!")

if __name__ == '__main__':
    print("=" * 50)
    print("🔥 SUPER SMOOTH MUSIC PLAYER")
    print("=" * 50)
    
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    print(f"📱 Phone Access: http://{local_ip}:5000")
    print(f"💻 PC Access: http://localhost:5000")
    print("✅ Server is ALWAYS active - no browser needed on PC!")
    print("=" * 50)
    
    # Start warmup in background (para ready agad)
    warmup_thread = threading.Thread(target=warmup_server, daemon=True)
    warmup_thread.start()
    
    # Run with debug=False at use_reloader=False
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True, use_reloader=False)