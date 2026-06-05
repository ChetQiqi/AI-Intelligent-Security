#!/usr/bin/env python3
import base64
import json
import sys
import time
from pathlib import Path

import streamlit as st

script_dir = Path(__file__).parent.absolute()
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from apps.recognition_system.ui import ApiClient, ApiClientError


st.set_page_config(page_title="人脸识别系统", layout="wide")


SVG_ICONS = {
    "home": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>',
    "users": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
    "user": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
    "image": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>',
    "video": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2" ry="2"/></svg>',
    "camera": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg>',
    "cpu": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2" ry="2"/><rect x="9" y="9" width="6" height="6"/><line x1="9" y1="1" x2="9" y2="4"/><line x1="15" y1="1" x2="15" y2="4"/><line x1="9" y1="20" x2="9" y2="23"/><line x1="15" y1="20" x2="15" y2="23"/><line x1="20" y1="9" x2="23" y2="9"/><line x1="20" y1="14" x2="23" y2="14"/><line x1="1" y1="9" x2="4" y2="9"/><line x1="1" y1="14" x2="4" y2="14"/></svg>',
    "settings": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>',
    "activity": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>',
    "wand": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/><line x1="2" y1="22" x2="22" y2="22"/><path d="M5.5 18.5l4-4"/></svg>',
}


def inject_global_styles():
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Fira+Sans:wght@300;400;500;600;700&family=Fira+Code:wght@400;500;600&display=swap');

            /* ========== 全局与布局 ========== */
            html, body, [class*="st-"] {
                font-family: 'Fira Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            }
            code, pre, .stCodeBlock, [data-testid="stCode"] {
                font-family: 'Fira Code', 'Cascadia Code', 'JetBrains Mono', monospace;
            }
            .block-container {
                padding-top: 2rem;
                padding-bottom: 3rem;
            }
            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #0F172A 0%, rgba(59,130,246,0.04) 100%);
                border-right: 1px solid rgba(148, 163, 184, 0.12);
            }

            /* ========== 侧边栏导航 (Radio → 现代菜单) ========== */
            [data-testid="stSidebar"] .stRadio > div[role="radiogroup"] {
                gap: 0.35rem;
            }
            [data-testid="stSidebar"] .stRadio [role="radio"] {
                padding: 0.6rem 0.9rem;
                border-radius: 10px;
                background: transparent;
                border: 1px solid transparent;
                transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
                margin: 0;
                cursor: pointer;
            }
            [data-testid="stSidebar"] .stRadio [role="radio"]:hover {
                background: rgba(59, 130, 246, 0.08);
                transform: translateX(4px);
            }
            [data-testid="stSidebar"] .stRadio [role="radio"]:focus-visible {
                outline: 2px solid #3b82f6;
                outline-offset: 2px;
                border-radius: 10px;
            }
            [data-testid="stSidebar"] .stRadio [role="radio"][aria-checked="true"] {
                background: linear-gradient(135deg, rgba(59, 130, 246, 0.18) 0%, rgba(37, 99, 235, 0.06) 100%);
                border: 1px solid rgba(59, 130, 246, 0.35);
                box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
            }
            [data-testid="stSidebar"] .stRadio [role="radio"][aria-checked="true"] p {
                color: #60a5fa !important;
                font-weight: 700;
            }
            [data-testid="stSidebar"] .stRadio [role="radio"] div:first-child {
                display: none;
            }
            [data-testid="stSidebar"] .stRadio [role="radio"] p {
                font-size: 0.95rem;
                margin: 0;
                letter-spacing: -0.01em;
            }

            /* ========== 侧边栏 expander ========== */
            [data-testid="stSidebar"] .stExpander {
                border: 1px solid rgba(148, 163, 184, 0.12) !important;
                border-radius: 10px !important;
                margin-bottom: 0.35rem;
            }
            [data-testid="stSidebar"] .stExpander > summary {
                font-size: 0.85rem;
                padding: 0.5rem 0.7rem;
                background: rgba(30, 41, 59, 0.25);
            }

            /* ========== 按钮 ========== */
            .stButton > button,
            .stDownloadButton > button {
                font-weight: 600;
                border-radius: 10px;
                transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
                border: 1px solid rgba(148, 163, 184, 0.2);
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
                cursor: pointer;
            }
            .stButton > button:hover,
            .stDownloadButton > button:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
                border-color: rgba(59, 130, 246, 0.5);
                color: #60a5fa !important;
            }
            .stButton > button:active,
            .stDownloadButton > button:active {
                transform: translateY(1px);
                box-shadow: 0 1px 2px rgba(59, 130, 246, 0.2);
            }
            .stButton > button:focus-visible,
            .stDownloadButton > button:focus-visible {
                outline: 2px solid #3b82f6;
                outline-offset: 2px;
            }
            button[kind="primary"] {
                background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
                color: #fff !important;
                border: none !important;
                box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important;
            }
            button[kind="primary"]:hover {
                background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%) !important;
                box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4) !important;
                transform: translateY(-2px);
            }
            button[kind="primary"] p {
                color: #fff !important;
            }

            /* ========== 侧边栏表单卡片 ========== */
            [data-testid="stSidebar"] form {
                background: rgba(30, 41, 59, 0.5);
                border-radius: 14px;
                padding: 1rem;
                border: 1px solid rgba(148, 163, 184, 0.15);
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
                margin-bottom: 0.75rem;
            }
            [data-testid="stSidebar"] form:last-of-type {
                margin-bottom: 0;
            }

            /* ========== 输入框 ========== */
            [data-testid="stTextInput"] div[data-baseweb="base-input"],
            [data-testid="stNumberInput"] div[data-baseweb="base-input"] {
                border: 1px solid rgba(148, 163, 184, 0.3) !important;
                background-color: #1E293B !important;
                border-radius: 8px !important;
                transition: all 0.2s ease;
            }
            [data-testid="stTextInput"] div[data-baseweb="base-input"]:focus-within,
            [data-testid="stNumberInput"] div[data-baseweb="base-input"]:focus-within {
                border-color: #3b82f6 !important;
                box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.3) !important;
            }
            [data-testid="stTextInput"] input,
            [data-testid="stNumberInput"] input {
                color: #F8FAFC !important;
            }

            /* ========== 指标卡片 (st.metric) ========== */
            [data-testid="stMetric"] {
                background: #1E293B;
                border: 1px solid rgba(148, 163, 184, 0.15);
                border-radius: 14px;
                padding: 1rem 1.2rem;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
                min-height: 100px;
                display: flex;
                flex-direction: column;
                justify-content: center;
            }
            [data-testid="stMetric"]:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(59, 130, 246, 0.15);
                border-color: rgba(59, 130, 246, 0.3);
            }

            /* ========== Expander ========== */
            .stExpander {
                border: 1px solid rgba(148, 163, 184, 0.15) !important;
                border-radius: 12px !important;
                overflow: hidden;
                box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            }
            .stExpander > summary {
                background: rgba(30, 41, 59, 0.4);
            }

            /* ========== Tabs 导航 ========== */
            [data-testid="stTabs"] [role="tablist"] {
                gap: 0.25rem;
                overflow-x: auto;
                flex-wrap: nowrap;
                white-space: nowrap;
                -webkit-overflow-scrolling: touch;
                scrollbar-width: thin;
            }
            [data-testid="stTabs"] button[role="tab"] {
                border-radius: 8px 8px 0 0;
                transition: all 0.2s ease;
                cursor: pointer;
            }
            [data-testid="stTabs"] button[role="tab"]:focus-visible {
                outline: 2px solid #3b82f6;
                outline-offset: -2px;
            }

            /* ========== Hero 卡片 ========== */
            .app-hero {
                background:
                    radial-gradient(circle at 20% 20%, rgba(37, 99, 235, 0.18), transparent 28%),
                    #1E293B;
                border: 1px solid rgba(148, 163, 184, 0.18);
                border-radius: 20px;
                padding: 2.5rem;
                margin-bottom: 1.5rem;
                transition: all 0.3s ease;
            }
            .app-hero:hover {
                box-shadow: 0 12px 40px rgba(37, 99, 235, 0.12);
                border-color: rgba(59, 130, 246, 0.35);
            }
            .app-hero h1 {
                font-size: 2.6rem;
                line-height: 1.2;
                margin: 0 0 0.5rem 0;
                letter-spacing: -0.02em;
                font-weight: 700;
            }
            .app-hero p {
                color: #94A3B8;
                font-size: 1.05rem;
                margin: 0;
                line-height: 1.6;
            }
            .hero-tag {
                display: inline-flex;
                align-items: center;
                gap: 0.45rem;
                border: 1px solid rgba(59, 130, 246, 0.35);
                border-radius: 999px;
                color: #60a5fa;
                padding: 0.3rem 0.8rem;
                font-size: 0.8rem;
                font-weight: 600;
                margin-bottom: 1.2rem;
                background: rgba(59,130,246,0.08);
                letter-spacing: 0.02em;
            }
            .hero-actions {
                margin-top: 1rem;
                color: #94A3B8;
                font-size: 0.95rem;
                line-height: 1.6;
            }

            /* ========== 页面标题 ========== */
            .page-title {
                border-bottom: 1px solid rgba(148, 163, 184, 0.2);
                margin-bottom: 1.5rem;
                padding-bottom: 0.75rem;
            }
            .page-title h2 {
                margin: 0;
                font-size: 1.75rem;
                letter-spacing: -0.02em;
                font-weight: 700;
            }
            .page-title p {
                margin: 0.35rem 0 0 0;
                color: #94A3B8;
                font-size: 0.95rem;
            }

            /* ========== Feature 卡片 ========== */
            .feature-card {
                background:
                    linear-gradient(180deg, rgba(59, 130, 246, 0.06), transparent 70%),
                    #1E293B;
                border: 1px solid rgba(148, 163, 184, 0.15);
                border-radius: 16px;
                padding: 1.5rem;
                min-height: 220px;
                display: flex;
                flex-direction: column;
                transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
                cursor: default;
                position: relative;
                overflow: hidden;
            }
            .feature-card::before {
                content: '';
                position: absolute;
                top: 0; left: 0; right: 0; height: 3px;
                background: linear-gradient(90deg, #3b82f6, #8b5cf6);
                opacity: 0;
                transition: opacity 0.25s ease;
            }
            .feature-card:hover {
                transform: translateY(-6px);
                box-shadow: 0 12px 30px rgba(59, 130, 246, 0.18);
                border-color: rgba(59, 130, 246, 0.4);
            }
            .feature-card:hover::before {
                opacity: 1;
            }
            .feature-card .icon {
                width: 2.6rem;
                height: 2.6rem;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 10px;
                background: rgba(59, 130, 246, 0.15);
                margin-bottom: 1rem;
                color: #60a5fa;
                transition: transform 0.25s ease, background 0.25s ease;
            }
            .feature-card:hover .icon {
                transform: scale(1.12);
                background: rgba(59, 130, 246, 0.25);
            }
            .feature-card h3 {
                margin: 0 0 0.5rem 0;
                font-size: 1.1rem;
                font-weight: 600;
            }
            .feature-card p {
                color: #94A3B8;
                font-size: 0.9rem;
                line-height: 1.6;
                margin: 0;
            }

            /* ========== 人员行 ========== */
            .person-row {
                display: flex;
                justify-content: space-between;
                align-items: center;
                flex-wrap: wrap;
                gap: 0.5rem;
                border: 1px solid rgba(148, 163, 184, 0.15);
                border-radius: 10px;
                padding: 0.9rem 1.15rem;
                margin-bottom: 0.5rem;
                background: #1E293B;
                transition: all 0.2s ease;
                cursor: default;
            }
            .person-row:hover {
                transform: translateX(6px);
                border-color: rgba(59, 130, 246, 0.35);
                background: rgba(59, 130, 246, 0.06);
                box-shadow: 0 4px 12px rgba(59, 130, 246, 0.08);
            }
            .person-row .name {
                font-weight: 600;
                font-size: 0.95rem;
            }
            .person-row .meta {
                color: #94A3B8;
                font-size: 0.85rem;
                background: rgba(148,163,184,0.08);
                padding: 0.2rem 0.55rem;
                border-radius: 999px;
            }

            /* ========== 匹配结果卡片 ========== */
            .match-pair-row {
                display: flex;
                gap: 1rem;
                flex-wrap: wrap;
                overflow-x: auto;
                margin-bottom: 1rem;
            }
            .match-pair-card {
                min-width: 280px;
                width: 320px;
                max-width: 100%;
            }
            .match-pair-card img {
                width: 100%;
                max-width: 320px;
                height: auto;
                aspect-ratio: 1;
                object-fit: contain;
                border-radius: 10px;
                border: 1px solid rgba(148, 163, 184, 0.2);
                background: #0F172A;
            }
            .match-pair-card p {
                margin: 0.4rem 0 0 0;
                font-size: 0.85rem;
                color: #94A3B8;
            }

            /* ========== Callout 信息框 ========== */
            [data-testid="stInfo"] {
                background: rgba(59, 130, 246, 0.08);
                border: 1px solid rgba(59, 130, 246, 0.25);
                border-radius: 10px;
            }
            [data-testid="stWarning"] {
                background: rgba(245, 158, 11, 0.08);
                border: 1px solid rgba(245, 158, 11, 0.25);
                border-radius: 10px;
            }
            [data-testid="stError"] {
                background: rgba(239, 68, 68, 0.08);
                border: 1px solid rgba(239, 68, 68, 0.25);
                border-radius: 10px;
            }
            [data-testid="stSuccess"] {
                background: rgba(34, 197, 94, 0.08);
                border: 1px solid rgba(34, 197, 94, 0.25);
                border-radius: 10px;
            }

            /* ========== 列内按钮全宽 ========== */
            [data-testid="column"] .stButton > button {
                width: 100%;
            }

            /* ========== 全局 focus-visible ========== */
            *:focus-visible {
                outline: 2px solid #3b82f6 !important;
                outline-offset: 2px;
            }

            /* ========== prefers-reduced-motion ========== */
            @media (prefers-reduced-motion: reduce) {
                *, *::before, *::after {
                    animation-duration: 0.01ms !important;
                    animation-iteration-count: 1 !important;
                    transition-duration: 0.01ms !important;
                }
            }

            /* ========== 侧边栏分隔线 ========== */
            [data-testid="stSidebar"] hr {
                border-color: rgba(148, 163, 184, 0.12);
                margin: 0.6rem 0;
            }

            /* ========== 滚动条美化 ========== */
            ::-webkit-scrollbar {
                width: 6px;
                height: 6px;
            }
            ::-webkit-scrollbar-track {
                background: transparent;
            }
            ::-webkit-scrollbar-thumb {
                background: rgba(148, 163, 184, 0.25);
                border-radius: 3px;
            }
            ::-webkit-scrollbar-thumb:hover {
                background: rgba(148, 163, 184, 0.4);
            }

            /* ========== Logo 区域 ========== */
            .sidebar-logo {
                display: flex;
                align-items: center;
                gap: 0.6rem;
                padding: 0.5rem 0 1.5rem 0;
                justify-content: center;
            }
            .sidebar-logo svg {
                color: #60a5fa;
                flex-shrink: 0;
            }
            .sidebar-logo h1 {
                margin: 0;
                font-size: 1.4rem;
                font-weight: 700;
                background: linear-gradient(135deg, #60a5fa, #a78bfa);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                letter-spacing: -0.02em;
            }
            .sidebar-logo p {
                margin: 0.1rem 0 0 0;
                color: #64748b;
                font-size: 0.78rem;
                font-weight: 500;
            }

            /* ========== 侧边栏 section 标题 ========== */
            .sidebar-section-title {
                display: flex;
                align-items: center;
                gap: 0.4rem;
                font-size: 0.85rem;
                font-weight: 600;
                color: #94A3B8;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                margin-bottom: 0.5rem;
            }
            .sidebar-section-title svg {
                color: #64748b;
                flex-shrink: 0;
            }

            /* ========== 侧边栏间距优化 ========== */
            [data-testid="stSidebar"] > div > div > div {
                margin-bottom: 0.25rem;
            }

            /* ========== 人物资料卡 ========== */
            .person-cards-grid {
                display: flex;
                flex-wrap: wrap;
                gap: 1rem;
                margin: 1rem 0;
            }
            .person-card {
                display: flex;
                gap: 1rem;
                background: linear-gradient(135deg, #1E293B 0%, #1a2332 100%);
                border: 1px solid rgba(148, 163, 184, 0.18);
                border-radius: 14px;
                padding: 1.15rem;
                min-width: 300px;
                max-width: 380px;
                flex: 1 1 320px;
                transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            }
            .person-card:hover {
                transform: translateY(-3px);
                box-shadow: 0 8px 24px rgba(59, 130, 246, 0.15);
                border-color: rgba(59, 130, 246, 0.35);
            }
            .person-card.accepted {
                border-left: 3px solid #22C55E;
            }
            .person-card.rejected {
                border-left: 3px solid #F59E0B;
            }
            .person-card-avatar {
                flex-shrink: 0;
                width: 80px;
                height: 80px;
                border-radius: 12px;
                overflow: hidden;
                background: #0F172A;
                border: 2px solid rgba(148, 163, 184, 0.25);
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .person-card-avatar img {
                width: 100%;
                height: 100%;
                object-fit: cover;
            }
            .person-card-avatar .no-photo {
                color: #64748B;
                font-size: 0.7rem;
                text-align: center;
                padding: 0.3rem;
                line-height: 1.3;
            }
            .person-card-info {
                flex: 1;
                min-width: 0;
                display: flex;
                flex-direction: column;
                gap: 0.25rem;
            }
            .person-card-info .card-name {
                font-size: 1.05rem;
                font-weight: 700;
                color: #F1F5F9;
                margin: 0;
                line-height: 1.2;
            }
            .person-card-info .card-score {
                font-size: 0.85rem;
                font-weight: 600;
                margin: 0;
            }
            .person-card-info .card-score.high {
                color: #22C55E;
            }
            .person-card-info .card-score.medium {
                color: #F59E0B;
            }
            .person-card-info .card-score.low {
                color: #EF4444;
            }
            .person-card-info .card-meta {
                display: flex;
                flex-wrap: wrap;
                gap: 0.35rem;
                margin-top: 0.15rem;
            }
            .person-card-info .card-meta span {
                font-size: 0.75rem;
                color: #94A3B8;
                background: rgba(148, 163, 184, 0.08);
                padding: 0.15rem 0.5rem;
                border-radius: 999px;
                white-space: nowrap;
            }
            .person-card-info .card-meta span.gender-male {
                color: #60a5fa;
                background: rgba(59, 130, 246, 0.12);
            }
            .person-card-info .card-meta span.gender-female {
                color: #f472b6;
                background: rgba(244, 114, 182, 0.12);
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str = ""):
    st.markdown(
        f"""
        <div class="page-title">
            <h2>{title}</h2>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_person_cards(person_cards: list):
    """渲染人物资料卡网格。"""
    if not person_cards:
        return

    gender_labels = {"male": "男", "female": "女", "unspecified": "未指定"}
    cards_html = '<div class="person-cards-grid">'

    for card in person_cards:
        name = card.get("name", "Unknown")
        score = card.get("score", 0.0)
        accepted = card.get("accepted", False)
        gender = card.get("gender", "unspecified")
        birth_date = card.get("birth_date", "")
        embedding_count = card.get("embedding_count", 0)
        avatar_b64 = card.get("gallery_face_base64")

        status_class = "accepted" if accepted else "rejected"
        if score >= 0.7:
            score_class = "high"
        elif score >= 0.4:
            score_class = "medium"
        else:
            score_class = "low"

        if avatar_b64:
            avatar_html = f'<img src="data:image/jpeg;base64,{avatar_b64}" alt="{name}" />'
        else:
            avatar_html = '<div class="no-photo">暂无<br>照片</div>'

        meta_parts = []
        g = gender or "unspecified"
        gender_label = gender_labels.get(g, g)
        gender_class = f"gender-{g}" if g in ("male", "female") else ""
        meta_parts.append(f'<span class="{gender_class}">{gender_label}</span>')
        if birth_date:
            meta_parts.append(f"<span>{birth_date}</span>")
        meta_parts.append(f"<span>{embedding_count} 样本</span>")

        cards_html += f"""
        <div class="person-card {status_class}">
            <div class="person-card-avatar">{avatar_html}</div>
            <div class="person-card-info">
                <p class="card-name">{name}</p>
                <p class="card-score {score_class}">相似度 {score * 100:.1f}%</p>
                <div class="card-meta">{''.join(meta_parts)}</div>
            </div>
        </div>"""

    cards_html += "</div>"
    st.markdown(cards_html, unsafe_allow_html=True)


def init_session_state():
    if "api_base_url" not in st.session_state:
        st.session_state.api_base_url = "http://127.0.0.1:8000"
    if "auth_token" not in st.session_state:
        st.session_state.auth_token = ""
    if "current_user" not in st.session_state:
        st.session_state.current_user = None


def get_client() -> ApiClient:
    return ApiClient(st.session_state.api_base_url, token=st.session_state.auth_token or None)


def call_api(action, fallback=None):
    try:
        return action()
    except ApiClientError as exc:
        st.error(f"API 调用失败: {exc}")
    except Exception as exc:
        st.error(f"请求处理失败: {exc}")
    return fallback


def get_persons():
    payload = call_api(lambda: get_client().list_identities(), {"persons": []})
    return payload.get("persons", []) if payload else []


def is_logged_in() -> bool:
    return bool(st.session_state.auth_token and st.session_state.current_user)


def current_role() -> str:
    if not is_logged_in():
        return ""
    return str(st.session_state.current_user.get("role", ""))


def local_weights_files():
    weights_dir = project_root / "weights"
    if not weights_dir.exists():
        return []
    exts = {".pt", ".pth", ".ckpt", ".bin", ".onnx"}
    files = []
    for file_path in sorted(weights_dir.iterdir()):
        if file_path.is_file() and file_path.suffix.lower() in exts:
            files.append({"name": file_path.name, "path": str(file_path.resolve())})
    return files


def _get_weights_options(client) -> list:
    """返回可用权重文件的完整路径列表，优先从 API 获取，失败时读本地 weights 目录。"""
    try:
        payload = client.list_model_weights()
        items = payload.get("files", []) if payload else []
        return [item["path"] for item in items if item.get("path")]
    except Exception:
        local = local_weights_files()
        return [item["path"] for item in local]


def show_sidebar_controls():
    with st.sidebar:
        st.markdown("---")
        st.markdown(f'<div class="sidebar-section-title">{SVG_ICONS["settings"]} 控制面板</div>', unsafe_allow_html=True)
        st.session_state.api_base_url = st.text_input("API 地址", st.session_state.api_base_url)
        st.markdown(f'<div class="sidebar-section-title">{SVG_ICONS["user"]} 账号</div>', unsafe_allow_html=True)

        if not is_logged_in():
            st.caption("登录仅校验用户名和密码，角色以后端账号记录为准。")
            with st.form("login_form", clear_on_submit=False):
                login_username = st.text_input("登录用户名", key="login_username")
                login_password = st.text_input("登录密码", type="password", key="login_password")
                submit_login = st.form_submit_button("登录", use_container_width=True)
            if submit_login:
                payload = call_api(lambda: get_client().login(login_username, login_password))
                if payload:
                    st.session_state.auth_token = payload["access_token"]
                    me_info = call_api(lambda: get_client().me(), None)
                    st.session_state.current_user = me_info
                    st.rerun()

            st.markdown("---")
            st.caption("新用户注册（默认 viewer 角色，developer/admin 需由管理员创建）")
            with st.form("register_form", clear_on_submit=True):
                register_username = st.text_input("注册用户名", key="register_username")
                register_password = st.text_input("注册密码", type="password", key="register_password")
                submit_register = st.form_submit_button("注册账号", use_container_width=True)
            if submit_register:
                created = call_api(
                    lambda: get_client().register(
                        username=register_username,
                        password=register_password,
                        role="viewer",
                    )
                )
                if created:
                    st.success("注册成功，请使用新账号登录。")
                else:
                    st.info("注册失败，请检查用户名是否已存在。")
        else:
            user = st.session_state.current_user
            st.success(f"已登录：{user['username']} ({user['role']})")
            if st.button("刷新我的信息", use_container_width=True):
                st.session_state.current_user = call_api(lambda: get_client().me(), user)
                st.rerun()

            if user.get("role") == "admin":
                st.markdown("---")
                st.caption("管理员：创建新账号")
                with st.form("admin_create_user_form", clear_on_submit=True):
                    new_username = st.text_input("新用户用户名", key="admin_new_username")
                    new_password = st.text_input("新用户密码", type="password", key="admin_new_password")
                    new_role = st.selectbox("新用户角色", ["viewer", "developer", "admin"], index=0, key="admin_new_role")
                    new_email = st.text_input("邮箱（可选）", key="admin_new_email")
                    submit_admin_create = st.form_submit_button("创建用户", use_container_width=True)
                if submit_admin_create:
                    created = call_api(
                        lambda: get_client().register(
                            username=new_username,
                            password=new_password,
                            role=new_role,
                            email=new_email or None,
                        )
                    )
                    if created:
                        st.success(f"已创建用户：{created['username']} ({created['role']})")

            if st.button("退出登录", use_container_width=True):
                st.session_state.auth_token = ""
                st.session_state.current_user = None
                st.rerun()

        st.markdown("---")
        st.markdown(f'<div class="sidebar-section-title">{SVG_ICONS["activity"]} 系统状态</div>', unsafe_allow_html=True)
        health = call_api(lambda: get_client().health(), None)
        role = current_role()
        can_manage_model = is_logged_in() and role in ("admin", "developer")
        if health:
            st.success("API 已连接")
            if health.get("model_loaded"):
                st.success("模型已加载")
            else:
                st.warning("模型未加载")

            if can_manage_model:
                with st.expander("模型管理（admin / developer）", expanded=False):
                    runtime = call_api(lambda: get_client().model_runtime(), None)
                    if runtime:
                        st.caption(
                            f"当前模型: {runtime.get('model_name')} | 权重: {Path(runtime.get('weights_path', '')).name}"
                        )

                    weights_payload = call_api(lambda: get_client().list_model_weights(), {"files": []}) or {"files": []}
                    weight_items = weights_payload.get("files", [])
                    if not weight_items:
                        weight_items = local_weights_files()
                    model_name = st.selectbox(
                        "模型架构",
                        ["iresnet18", "iresnet34", "iresnet50", "iresnet100"],
                        index=2,
                        key="model_arch_selector",
                    )
                    if weight_items:
                        weight_name_to_path = {item["name"]: item["path"] for item in weight_items}
                        selected_weight_name = st.selectbox(
                            "权重文件（weights 目录）",
                            list(weight_name_to_path.keys()),
                            key="weights_file_selector",
                        )
                        selected_weight_path = weight_name_to_path[selected_weight_name]
                    else:
                        selected_weight_path = None
                        st.caption("未发现可用权重文件（.pt/.pth/.ckpt/.bin）。")

                    if st.button("加载/切换模型", use_container_width=True, key="switch_model_btn"):
                        with st.spinner("正在加载模型..."):
                            if selected_weight_path:
                                call_api(
                                    lambda: get_client().switch_model(
                                        model_name=model_name,
                                        weights_path=selected_weight_path,
                                    )
                                )
                            else:
                                call_api(lambda: get_client().load_model())
                        st.rerun()
            elif not is_logged_in():
                st.caption("请先登录 admin/developer 账号后管理模型。")
            else:
                st.caption("当前角色无模型管理权限。")

            # 所有已登录角色都可以查看当前推理模型信息（viewer 也可见）
            if is_logged_in():
                runtime_info = call_api(lambda: get_client().model_runtime(), None)
                if runtime_info:
                    model_name = runtime_info.get("model_name", "unknown")
                    model_path = Path(runtime_info.get("weights_path", "")).name
                    framework = str(runtime_info.get("framework", "")).upper() or "PT"
                    st.caption(f"当前推理模型: {model_name} | {model_path} | {framework}")
        else:
            st.warning("API 未连接")
            st.caption("启动后端：python run.py api")

        stats = {"person_count": 0, "embedding_count": 0}
        if is_logged_in():
            stats = call_api(lambda: get_client().stats(), {"person_count": 0, "embedding_count": 0}) or stats
        if stats and is_logged_in():
            col1, col2 = st.columns(2)
            col1.metric("注册人数", stats.get("person_count", 0))
            col2.metric("特征数量", stats.get("embedding_count", 0))


def page_home():
    hero_path = Path(r"C:\Users\ROG\.cursor\projects\e-RecognitionSystem\assets\recognition-hero.png")
    hero_left, hero_right = st.columns([1.05, 1], vertical_alignment="center")
    with hero_left:
        st.markdown(
            """
            <div class="app-hero">
                <div class="hero-tag">AI Recognition Platform</div>
                <h1>人脸识别系统</h1>
                <p>面向工程化部署的识别平台：前端展示、API 接入、Service 编排、SQLite 特征库。</p>
                <div class="hero-actions">启动后端后即可进行人员管理、图片识别、视频识别和摄像头实时识别。</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with hero_right:
        if hero_path.exists():
            st.image(str(hero_path), use_container_width=True)
        else:
            st.markdown(
                """
                <div style="background:linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
                            border:1px solid rgba(148,163,184,0.18);
                            border-radius:16px;
                            padding:2rem;
                            text-align:center;
                            color:#64748B;">
                    <p style="font-size:0.95rem;margin:0;">上传一张展示图片以完善首页</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    stats = {"person_count": 0, "embedding_count": 0}
    if is_logged_in():
        stats = call_api(lambda: get_client().stats(), {"person_count": 0, "embedding_count": 0}) or stats
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("注册人员", stats.get("person_count", 0))
    col2.metric("特征数量", stats.get("embedding_count", 0))
    col3.metric("API 状态", "在线")
    col4.metric("架构模式", "API + Service")

    st.markdown(
        "<div style='height: 0.75rem;'></div>",
        unsafe_allow_html=True,
    )
    st.markdown("### 核心功能")
    card_cols = st.columns(4)
    cards = [
        (SVG_ICONS["users"], "人员管理", "注册、查询、删除和修改人员信息。"),
        (SVG_ICONS["image"], "图片识别", "上传图片并调用后端识别人脸。"),
        (SVG_ICONS["video"], "视频识别", "上传视频并生成识别结果视频。"),
        (SVG_ICONS["camera"], "摄像头识别", "通过 API 控制实时摄像头识别。"),
    ]
    for col, (icon_svg, title, desc) in zip(card_cols, cards):
        with col:
            st.markdown(
                f"""
                <div class="feature-card">
                    <div class="icon">{icon_svg}</div>
                    <h3>{title}</h3>
                    <p>{desc}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    if is_logged_in():
        st.info("当前 UI 只负责展示和交互，数据库、模型加载、识别推理都在 FastAPI 后端完成。")
    else:
        st.warning("请先在左侧登录后再调用受保护的 API 接口。")


def page_person_management():
    page_header("人员管理", "通过 API 完成人员注册、列表查询、删除和编辑。")
    client = get_client()
    role = current_role()
    if role == "viewer":
        st.info("当前账号为 viewer，仅可录入人脸信息。")
        tab_add = st.tabs(["录入人脸"])[0]
        tab_list = tab_delete = tab_edit = None
    else:
        tab_add, tab_list, tab_delete, tab_edit = st.tabs(["注册新人", "人员列表", "删除人员", "编辑人员"])

    with tab_add:
        person_id = st.text_input("人员 ID", placeholder="例如: Alice")
        col1, col2 = st.columns(2)
        with col1:
            gender = st.selectbox("性别", ["unspecified", "male", "female"], format_func=lambda v: {"unspecified": "未指定", "male": "男", "female": "女"}[v])
        with col2:
            birth_date = st.text_input("出生日期", placeholder="YYYY-MM")
        uploaded_files = st.file_uploader("上传人脸照片（可多选）", type=["jpg", "jpeg", "png", "bmp"], accept_multiple_files=True)
        if st.button("注册", type="primary", use_container_width=True):
            if not person_id:
                st.error("请输入人员 ID")
            elif not uploaded_files:
                st.error("请上传至少一张照片")
            else:
                files = [(file.name, file.getvalue(), file.type or "application/octet-stream") for file in uploaded_files]
                with st.spinner("正在通过 API 注册人员..."):
                    result = call_api(lambda: client.add_identity(person_id, files, gender=gender, birth_date=birth_date))
                if result:
                    st.success(f"成功注册 {result['success_count']} 张照片")
                    for item in result["failed_files"]:
                        st.warning(f"{item['filename']}: {item['reason']}")

    if tab_list is not None:
        with tab_list:
            persons = get_persons()
            search_query = st.text_input("搜索人员", placeholder="输入人员 ID 或姓名...")
            if search_query:
                persons = [p for p in persons if search_query.lower() in p["name"].lower()]
            if not persons:
                st.info("暂无注册人员")
            else:
                gender_labels = {"male": "男", "female": "女", "unspecified": "未指定"}
                st.markdown(f"共 {len(persons)} 人")
                for item in persons:
                    g = item.get("gender", "unspecified")
                    bd = item.get("birth_date", "")
                    meta_parts = [f"{item['embedding_count']} 张特征"]
                    if g != "unspecified":
                        meta_parts.append(gender_labels.get(g, g))
                    if bd:
                        meta_parts.append(bd)
                    meta_str = " · ".join(meta_parts)
                    st.markdown(
                        f"""
                        <div class="person-row">
                            <span class="name">{item['name']}</span>
                            <span class="meta">{meta_str}</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

    if tab_delete is not None:
        with tab_delete:
            persons = get_persons()
            if not persons:
                st.info("暂无注册人员")
            else:
                person_to_delete = st.selectbox("选择要删除的人员", [item["name"] for item in persons])
                st.warning(f"确认删除 {person_to_delete}？此操作不可恢复。")
                if st.button("确认删除", type="primary", use_container_width=True):
                    result = call_api(lambda: client.delete_identity(person_to_delete))
                    if result and result.get("deleted"):
                        st.success(f"已删除 {person_to_delete}")
                        time.sleep(0.5)
                        st.rerun()

    if tab_edit is not None:
        with tab_edit:
            persons = get_persons()
            if not persons:
                st.info("暂无注册人员")
            else:
                person_names = [item["name"] for item in persons]
                selected = st.selectbox("选择要编辑的人员", person_names)
                detail = call_api(lambda: client.get_identity_detail(selected))
                current_gender = (detail or {}).get("gender", "unspecified") if detail else "unspecified"
                current_birth = (detail or {}).get("birth_date", "") if detail else ""

                new_name = st.text_input("新名字（留空则不修改）", placeholder="留空则不修改")
                col1, col2 = st.columns(2)
                with col1:
                    gender_idx = {"unspecified": 0, "male": 1, "female": 2}.get(current_gender, 0)
                    new_gender = st.selectbox("性别", ["unspecified", "male", "female"],
                                              index=gender_idx,
                                              format_func=lambda v: {"unspecified": "未指定", "male": "男", "female": "女"}[v])
                with col2:
                    new_birth = st.text_input("出生日期", value=current_birth, placeholder="YYYY-MM")
                if st.button("保存修改", type="primary", use_container_width=True):
                    result = call_api(lambda: client.update_identity(
                        selected,
                        new_name=new_name.strip(),
                        gender=new_gender,
                        birth_date=new_birth.strip(),
                    ))
                    if result and result.get("updated"):
                        st.success(f"已更新 {selected}")
                        time.sleep(0.5)
                        st.rerun()


def page_face_enrollment():
    page_header("人脸录入", "viewer 模式下仅开放人脸录入能力。")
    client = get_client()
    person_id = st.text_input("人员 ID", placeholder="例如: Alice")
    uploaded_files = st.file_uploader(
        "上传人脸照片（可多选）",
        type=["jpg", "jpeg", "png", "bmp"],
        accept_multiple_files=True,
    )
    if st.button("提交录入", type="primary", use_container_width=True):
        if not person_id:
            st.error("请输入人员 ID")
        elif not uploaded_files:
            st.error("请上传至少一张照片")
        else:
            files = [(file.name, file.getvalue(), file.type or "application/octet-stream") for file in uploaded_files]
            with st.spinner("正在通过 API 录入人脸..."):
                result = call_api(lambda: client.add_identity(person_id, files))
            if result:
                st.success(f"成功录入 {result['success_count']} 张照片")
                for item in result["failed_files"]:
                    st.warning(f"{item['filename']}: {item['reason']}")


def _build_result_csv(result: dict, job_type: str) -> str:
    """根据 job_type 构建 CSV 字符串。"""
    import io

    buf = io.StringIO()
    if job_type in ("lfw_verification", "ijb_evaluation"):
        datasets = result.get("datasets", {})
        tpr_values = result.get("tpr_values", {})
        buf.write(f"mean_accuracy,{result.get('mean_accuracy', '')}\n")
        buf.write(f"roc_auc,{result.get('roc_auc', '')}\n\n")
        buf.write("dataset,accuracy,threshold,pairs\n")
        for name, info in datasets.items():
            buf.write(f"{name},{info.get('acc', '')},{info.get('threshold', '')},{info.get('num_pairs', '')}\n")
        buf.write("\nfar_level,tar\n")
        for far_key, tar_val in tpr_values.items():
            buf.write(f"{far_key},{tar_val}\n")
    elif job_type == "threshold_sweep":
        summary = result.get("summary", [])
        columns = ["threshold", "rank1_accuracy", "far", "frr", "tar_at_far_1e3", "f1_score", "auc_score", "num_samples"]
        buf.write(",".join(columns) + "\n")
        for row in summary:
            buf.write(",".join(str(row.get(c, "")) for c in columns) + "\n")
    else:
        buf.write("No tabular data for this job type.\n")
    return buf.getvalue()


def _render_eval_job_result(job: dict) -> None:
    """渲染评估任务结果，包含图表。"""
    import io as _io

    result = job.get("result") or {}
    job_type = job.get("job_type", "")

    st.caption(
        f"job_id: `{job['job_id']}` | 用时: {job.get('elapsed_seconds', 0):.1f}s | "
        f"模型: {job.get('model_name')} | 权重: {Path(job.get('weights_path', '')).name}"
    )

    # ── Export buttons ──
    json_str = json.dumps(result, ensure_ascii=False, indent=2, default=str)
    csv_content = _build_result_csv(result, job_type)

    col_json, col_csv = st.columns(2)
    with col_json:
        st.download_button(
            label="📥 导出 JSON",
            data=json_str,
            file_name=f"eval_{job_type}_{job['job_id']}.json",
            mime="application/json",
            use_container_width=True,
        )
    with col_csv:
        st.download_button(
            label="📊 导出 CSV",
            data=csv_content,
            file_name=f"eval_{job_type}_{job['job_id']}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    if job_type == "lfw_verification":
        datasets_result = result.get("datasets", {})
        mean_acc = result.get("mean_accuracy")
        embedding_size = result.get("embedding_size", "")
        device = result.get("device", "")

        # 顶部汇总
        c1, c2, c3 = st.columns(3)
        c1.metric("平均准确率", f"{mean_acc * 100:.2f}%" if mean_acc else "—")
        c2.metric("Embedding 维度", str(embedding_size) if embedding_size else "—")
        c3.metric("设备", str(device) if device else "—")

        st.markdown("---")

        # 每个数据集大卡片（3列）
        valid_ds = {k: v for k, v in datasets_result.items() if v.get("acc") is not None}
        error_ds = {k: v for k, v in datasets_result.items() if v.get("acc") is None}

        if valid_ds:
            cols = st.columns(3)
            for i, (ds_name, ds_data) in enumerate(valid_ds.items()):
                acc = ds_data["acc"]
                th = ds_data.get("threshold", 0)
                pairs = ds_data.get("num_pairs", 0)
                color = "normal" if acc >= 0.98 else "inverse"
                with cols[i % 3]:
                    st.metric(
                        label=f"**{ds_name.upper()}**",
                        value=f"{acc * 100:.2f}%",
                        delta=f"threshold {th:.4f}  ·  {pairs} pairs",
                        delta_color="off",
                    )

        if error_ds:
            st.markdown("**以下数据集评估失败**")
            for ds_name, ds_data in error_ds.items():
                st.error(f"{ds_name}: {ds_data.get('error', '未知错误')}")

        st.markdown("---")

        # 柱状图
        chart_labels = [k for k, v in valid_ds.items()]
        chart_accs = [round(v["acc"] * 100, 2) for v in valid_ds.values()]
        if chart_labels:
            try:
                import matplotlib.pyplot as plt
                import io

                fig, ax = plt.subplots(figsize=(max(8, len(chart_labels) * 1.4), 5))
                colors = ["#4CAF50" if a >= 98 else "#FF9800" if a >= 95 else "#F44336" for a in chart_accs]
                bars = ax.bar(chart_labels, chart_accs, color=colors, width=0.6, edgecolor="white", linewidth=1.2)
                ax.set_ylim([max(0, min(chart_accs) - 3), 100.5])
                ax.set_ylabel("Accuracy (%)", fontsize=12)
                ax.set_title("LFW-style Verification Accuracy", fontsize=14, fontweight="bold")
                ax.tick_params(axis="x", labelsize=11)
                ax.grid(axis="y", linestyle="--", alpha=0.4)
                ax.spines["top"].set_visible(False)
                ax.spines["right"].set_visible(False)
                for bar, val in zip(bars, chart_accs):
                    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05,
                            f"{val:.2f}%", ha="center", va="bottom", fontsize=11, fontweight="bold")
                plt.tight_layout()
                buf = io.BytesIO()
                fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
                plt.close(fig)
                st.image(buf.getvalue(), use_container_width=True)
            except Exception:
                st.bar_chart(dict(zip(chart_labels, chart_accs)))

    elif job_type == "ijb_evaluation":
        target = result.get("target", "IJB")
        roc_auc = result.get("roc_auc")
        tpr_values = result.get("tpr_values", {})

        # 顶部大指标
        if roc_auc is not None:
            st.metric(f"{target} ROC AUC", f"{roc_auc:.4f}%")

        st.markdown("---")

        # TAR@FAR 大卡片
        if tpr_values:
            st.markdown("### TAR @ FAR")
            items = list(tpr_values.items())
            cols = st.columns(min(len(items), 3))
            for i, (far_str, tar_val) in enumerate(items):
                # 格式化 FAR 显示
                try:
                    import math
                    far_f = float(far_str)
                    if far_f < 0.001:
                        far_label = f"FAR=1e{int(round(math.log10(far_f)))}"
                    else:
                        far_label = f"FAR={far_f:.0e}"
                except Exception:
                    far_label = f"FAR={far_str}"
                with cols[i % 3]:
                    st.metric(label=far_label, value=f"{tar_val:.2f}%")

        st.markdown("---")

        # ROC 曲线（大图）
        fpr_pts = result.get("fpr", [])
        tpr_pts = result.get("tpr", [])
        if fpr_pts and tpr_pts:
            try:
                import matplotlib.pyplot as plt
                import io

                fig, ax = plt.subplots(figsize=(9, 6))
                ax.plot(fpr_pts, tpr_pts, lw=2, color="#4CAF50",
                        label=f"{result.get('weights', '')}  (AUC={roc_auc:.4f}%)")
                ax.set_xlim([1e-6, 0.1])
                ax.set_ylim([0.3, 1.0])
                ax.set_xscale("log")
                ax.set_xlabel("False Positive Rate", fontsize=12)
                ax.set_ylabel("True Positive Rate", fontsize=12)
                ax.set_title(f"ROC Curve — {target}", fontsize=14, fontweight="bold")
                ax.legend(loc="lower right", fontsize=10)
                ax.grid(linestyle="--", alpha=0.4)
                ax.spines["top"].set_visible(False)
                ax.spines["right"].set_visible(False)
                plt.tight_layout()
                buf = io.BytesIO()
                fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
                plt.close(fig)
                st.image(buf.getvalue(), use_container_width=True)
            except Exception:
                pass

        stdout_tail = result.get("stdout_tail", [])
        if stdout_tail:
            with st.expander("Runner 输出（末尾20行）"):
                st.code("\n".join(stdout_tail), language="text")

    elif job_type == "threshold_sweep":
        chart_data = result.get("chart_data", {})
        summary = result.get("summary", [])

        thresholds = chart_data.get("thresholds", [])
        if thresholds:
            try:
                import matplotlib.pyplot as plt
                import io

                fig, axes = plt.subplots(1, 2, figsize=(12, 4))

                # 左图：Rank-1 Accuracy & TAR@FAR
                ax1 = axes[0]
                if chart_data.get("rank1_accuracy"):
                    ax1.plot(thresholds, [v * 100 for v in chart_data["rank1_accuracy"]],
                             marker="o", label="Rank-1 Acc (%)", color="#4f8ef7")
                if chart_data.get("tar_at_far_1e3"):
                    ax1.plot(thresholds, [v * 100 for v in chart_data["tar_at_far_1e3"]],
                             marker="s", label="TAR@FAR=1e-3 (%)", color="#f7a64f")
                if chart_data.get("f1_score"):
                    ax1.plot(thresholds, [v * 100 for v in chart_data["f1_score"]],
                             marker="^", label="F1-Score (%)", color="#5fcf7a")
                ax1.set_xlabel("Threshold")
                ax1.set_ylabel("Score (%)")
                ax1.set_title("Recognition Metrics vs Threshold")
                ax1.legend(fontsize=8)
                ax1.grid(linestyle="--", alpha=0.5)

                # 右图：FAR & FRR
                ax2 = axes[1]
                if chart_data.get("far"):
                    ax2.plot(thresholds, chart_data["far"], marker="o", label="FAR", color="#f75f5f")
                if chart_data.get("frr"):
                    ax2.plot(thresholds, chart_data["frr"], marker="s", label="FRR", color="#a64ff7")
                ax2.set_xlabel("Threshold")
                ax2.set_ylabel("Rate")
                ax2.set_title("FAR / FRR vs Threshold")
                ax2.legend(fontsize=8)
                ax2.grid(linestyle="--", alpha=0.5)

                plt.tight_layout()
                buf = io.BytesIO()
                fig.savefig(buf, format="png", dpi=150)
                plt.close(fig)
                st.image(buf.getvalue(), use_container_width=True)
            except Exception:
                st.line_chart({
                    "Rank-1 Acc": chart_data.get("rank1_accuracy", []),
                    "F1": chart_data.get("f1_score", []),
                })

        # 汇总表
        if summary:
            display_cols = [
                "threshold", "rank1_accuracy", "far", "frr",
                "tar_at_far_1e3", "f1_score", "auc_score", "num_samples",
            ]
            filtered = [{k: row.get(k, "") for k in display_cols if k in row} for row in summary]
            st.dataframe(filtered, use_container_width=True)
    else:
        st.json(result)


def _poll_eval_job(client, job_id: str, placeholder):
    """单次轮询评估任务状态，更新占位符，返回最新 job dict。"""
    try:
        job = client.eval_job_status(job_id)
    except Exception as e:
        placeholder.error(f"轮询出错: {e}")
        return None

    status = job.get("status", "unknown")
    progress = float(job.get("progress", 0.0))
    msg = job.get("progress_msg", "")
    pdata = job.get("progress_data") or {}
    elapsed = job.get("elapsed_seconds", 0)

    with placeholder.container():
        if status in ("running", "pending"):
            # ── 总进度条 + 停止按钮 ──
            col_bar, col_btn = st.columns([5, 1])
            with col_bar:
                bar_pct = max(1, min(int(progress), 100))
                bar_label = f"{msg}  ({progress:.0f}%)" if msg else f"{progress:.0f}%"
                st.progress(bar_pct, text=bar_label)
                if elapsed:
                    st.caption(f"已运行 {elapsed:.0f}s")
            with col_btn:
                if st.button("Stop 停止", key=f"cancel_{job_id}", type="secondary", use_container_width=True):
                    try:
                        client.eval_cancel_job(job_id)
                        st.rerun()
                    except Exception as ex:
                        st.error(f"停止失败: {ex}")

            # ── LFW：已完成的数据集实时展示结果 ──
            if pdata.get("type") == "lfw":
                current = pdata.get("current", "")
                finished: dict = pdata.get("datasets", {})
                all_ds: list = job.get("params", {}).get("datasets") or []

                if finished:
                    st.markdown("### 已完成数据集")
                    cols = st.columns(min(len(finished), 3))
                    for i, (ds, res) in enumerate(finished.items()):
                        acc = res.get("acc")
                        th = res.get("threshold")
                        with cols[i % 3]:
                            st.metric(
                                label=ds.upper(),
                                value=f"{acc*100:.2f}%" if acc is not None else "—",
                                delta=f"threshold: {th:.4f}" if th is not None else None,
                                delta_color="off",
                            )

                # 当前正在跑的数据集
                if current:
                    st.info(f"Evaluating 正在评估 **{current}** ...")

                # 还未开始的数据集
                remaining = [d for d in all_ds if d not in finished and d != current]
                if remaining:
                    st.caption("等待中: " + "  ·  ".join(remaining))

            # ── IJB：显示阶段 ──
            elif pdata.get("type") == "ijb":
                phase_labels = {
                    "init": "初始化",
                    "extract_features": "提取特征",
                    "aggregate": "聚合模板",
                    "score": "计算相似度",
                    "roc": "计算 ROC",
                    "done": "完成",
                }
                phases_order = ["init", "extract_features", "aggregate", "score", "roc", "done"]
                current_phase = pdata.get("current_phase", "")
                phases_done = set(pdata.get("phases_done") or [])
                st.markdown("**评估阶段**")
                cols = st.columns(len(phases_order))
                for i, ph in enumerate(phases_order):
                    label = phase_labels.get(ph, ph)
                    if ph in phases_done:
                        cols[i].markdown(f"<span style='color:#22C55E;font-weight:600;'>Done</span> {label}", unsafe_allow_html=True)
                    elif ph == current_phase:
                        cols[i].markdown(f"<span style='color:#3B82F6;font-weight:600;'>&#x25B6;</span> **{label}**", unsafe_allow_html=True)
                    else:
                        cols[i].markdown(f"<span style='color:#475569;'>&#x25CB;</span> {label}", unsafe_allow_html=True)

        elif status == "done":
            st.success(f"评估完成！用时 {elapsed:.1f}s")
            _render_eval_job_result(job)
        elif status == "error":
            err_msg = job.get("error", "未知错误")
            if err_msg == "用户手动停止":
                st.warning(f"评估已手动停止（运行了 {elapsed:.1f}s）")
            else:
                st.error("评估出错")
                st.code(err_msg, language="text")
    return job


def page_developer_console():
    page_header("开发者工作台", "模型评估、Benchmark 查看与模型管理（admin/developer 专属）。")
    role = current_role()
    if role not in ("admin", "developer"):
        st.warning("当前账号无开发者权限。")
        return

    client = get_client()
    tab_eval_lfw = tab_eval_ijb = tab_eval_sweep = tab_jobs = tab_benchmark = tab_models = None
    _tabs = st.tabs([
        "LFW",
        "IJB",
        "阈值扫描",
        "评估历史",
        "Benchmark",
        "模型管理",
    ])
    (
        tab_eval_lfw, tab_eval_ijb, tab_eval_sweep,
        tab_jobs, tab_benchmark, tab_models,
    ) = _tabs

    # ----------------------------------------------------------------
    # Tab 1: LFW 验证评估
    # ----------------------------------------------------------------
    with tab_eval_lfw:
        st.markdown(
            "评估模型在 LFW / CALFW / CPLFW / AgeDB-30 / CFP-FP / VGG2-FP 等标准数据集上的验证准确率。"
        )
        with st.expander("数据集格式说明（点击展开）"):
            st.markdown(
                """
系统支持两种数据格式，**优先检测 bcolz，找不到时自动使用 numpy**：

**格式 A — bcolz**（原版 `verification.py` 格式，需安装 `bcolz` 库）
```
<data_root>/
    lfw/                ← bcolz 目录
    lfw_list.npy        ← 标签
    calfw/
    calfw_list.npy
    ...
```

**格式 B — numpy**（推荐，无需 bcolz，在训练服务器一次性转换）
```
<data_root>/
    lfw.npy             ← 图像数组，shape=[N, 3, 112, 112], uint8
    lfw_list.npy        ← 标签数组，shape=[N/2], bool
    calfw.npy
    calfw_list.npy
    ...
```

> 在训练服务器（有 bcolz 的环境）运行转换脚本：
> ```bash
> python tools/convert_lfw_to_npy.py --data_root /path/to/datasets --out_root /path/to/output
> ```
> 然后将 `output/` 目录复制到本机即可。
"""
            )
        st.markdown("---")

        # 获取当前可用权重列表
        weights_options = _get_weights_options(client)

        col1, col2 = st.columns(2)
        with col1:
            lfw_weights = st.selectbox(
                "选择权重文件",
                weights_options,
                key="lfw_weights_select",
            )
            lfw_backbone = st.selectbox(
                "Backbone 架构",
                ["iresnet18", "iresnet34", "iresnet50", "iresnet100",
                 "iresnet50_attention", "iresnet50_DCM", "iresnet50_att"],
                index=2,
                key="lfw_backbone_select",
            )
        with col2:
            lfw_data_root = st.text_input(
                "数据集根目录（bcolz 格式）",
                placeholder=r"E:\datasets\faces",
                key="lfw_data_root",
            )
            lfw_batch_size = st.number_input(
                "Batch Size", min_value=16, max_value=2048, value=512, step=16, key="lfw_batch_size"
            )

        available_datasets = ["lfw", "calfw", "cplfw", "agedb_30", "cfp_fp", "vgg2_fp"]
        lfw_datasets = st.multiselect(
            "评估数据集",
            available_datasets,
            default=available_datasets,
            key="lfw_datasets_select",
        )

        if st.button("提交 LFW 评估任务", key="lfw_submit_btn", type="primary", use_container_width=True):
            if not lfw_weights:
                st.error("请先选择权重文件")
            elif not lfw_data_root.strip():
                st.error("请输入数据集根目录")
            elif not lfw_datasets:
                st.error("请至少选择一个数据集")
            else:
                result = call_api(
                    lambda: client.eval_submit_lfw(
                        weights_path=lfw_weights,
                        backbone=lfw_backbone,
                        data_root=lfw_data_root.strip(),
                        datasets=lfw_datasets,
                        batch_size=int(lfw_batch_size),
                    ),
                    None,
                )
                if result:
                    job_id = result.get("job_id", "")
                    st.success(f"任务已提交：{result.get('message', '')}")
                    st.session_state["lfw_tracking_job_id"] = job_id

        # 轮询展示
        tracking_id = st.session_state.get("lfw_tracking_job_id", "")
        if tracking_id:
            st.markdown(f"**正在追踪任务 `{tracking_id}`**")
            placeholder = st.empty()
            job = _poll_eval_job(client, tracking_id, placeholder)
            if job and job.get("status") in ("running", "pending"):
                time.sleep(2)
                st.rerun()

    # ----------------------------------------------------------------
    # Tab 2: IJB 评估
    # ----------------------------------------------------------------
    with tab_eval_ijb:
        st.markdown(
            "在 IJB-B / IJB-C 数据集上评估模型的 TAR@FAR 和 ROC AUC。  \n"
            "数据集目录需包含 `loose_crop/` 和 `meta/` 子目录（标准 IJB release 结构）。"
        )
        st.markdown("---")

        weights_options_ijb = _get_weights_options(client)
        col1, col2 = st.columns(2)
        with col1:
            ijb_weights = st.selectbox("选择权重文件", weights_options_ijb, key="ijb_weights_select")
            ijb_backbone = st.selectbox(
                "Backbone 架构",
                ["iresnet18", "iresnet34", "iresnet50", "iresnet100",
                 "iresnet50_attention", "iresnet50_DCM", "iresnet50_att"],
                index=2,
                key="ijb_backbone_select",
            )
            ijb_target = st.selectbox("评估目标", ["IJBB", "IJBC"], key="ijb_target")
            ijb_batch_size = st.number_input(
                "Batch Size", min_value=16, max_value=2048, value=512, step=16, key="ijb_batch_size"
            )
        with col2:
            ijb_image_path = st.text_input(
                "数据集目录（含 loose_crop/ 和 meta/）",
                placeholder=r"E:\datasets\IJB_release\IJBB",
                key="ijb_image_path",
            )
            ijb_result_dir = st.text_input(
                "结果保存目录（可选）",
                placeholder=r"E:\eval_results",
                key="ijb_result_dir",
            )

        col_a, col_b, col_c = st.columns(3)
        ijb_use_norm = col_a.checkbox("use_norm_score", value=True, key="ijb_norm")
        ijb_use_det = col_b.checkbox("use_detector_score", value=True, key="ijb_det")
        ijb_use_flip = col_c.checkbox("use_flip_test", value=True, key="ijb_flip")

        if st.button("提交 IJB 评估任务", key="ijb_submit_btn", type="primary", use_container_width=True):
            if not ijb_weights:
                st.error("请先选择权重文件")
            elif not ijb_image_path.strip():
                st.error("请输入数据集目录")
            else:
                result = call_api(
                    lambda: client.eval_submit_ijb(
                        weights_path=ijb_weights,
                        backbone=ijb_backbone,
                        image_path=ijb_image_path.strip(),
                        target=ijb_target,
                        batch_size=int(ijb_batch_size),
                        use_norm_score=ijb_use_norm,
                        use_detector_score=ijb_use_det,
                        use_flip_test=ijb_use_flip,
                        result_dir=ijb_result_dir.strip(),
                    ),
                    None,
                )
                if result:
                    job_id = result.get("job_id", "")
                    st.success(f"任务已提交：{result.get('message', '')}")
                    st.session_state["ijb_tracking_job_id"] = job_id

        ijb_tracking_id = st.session_state.get("ijb_tracking_job_id", "")
        if ijb_tracking_id:
            st.markdown(f"**正在追踪任务 `{ijb_tracking_id}`**")
            placeholder_ijb = st.empty()
            job_ijb = _poll_eval_job(client, ijb_tracking_id, placeholder_ijb)
            if job_ijb and job_ijb.get("status") in ("running", "pending"):
                time.sleep(2)
                st.rerun()

    with tab_eval_sweep:
        st.markdown(
            "在本地测试图片目录上扫描多个识别阈值，输出 Rank-1 Accuracy / FAR / FRR / F1 等指标曲线。  \n"
            "测试目录结构：`<image_dir>/<person_name>/<image.jpg>`"
        )
        st.markdown("---")

        weights_options2 = _get_weights_options(client)

        col1, col2 = st.columns(2)
        with col1:
            sweep_weights = st.selectbox(
                "选择权重文件",
                weights_options2,
                key="sweep_weights_select",
            )
            sweep_backbone = st.selectbox(
                "Backbone 架构",
                ["iresnet18", "iresnet34", "iresnet50", "iresnet100"],
                index=2,
                key="sweep_backbone_select",
            )
            sweep_device = st.selectbox(
                "运行设备", ["auto", "cpu", "cuda"], index=0, key="sweep_device"
            )
        with col2:
            sweep_image_dir = st.text_input(
                "测试图片目录",
                placeholder=r"E:\test_images",
                key="sweep_image_dir",
            )
            sweep_db_path = st.text_input(
                "特征数据库路径（.db）",
                placeholder=r"E:\RecognitionSystem\data\features.db",
                key="sweep_db_path",
            )

        sweep_thresholds = st.text_input(
            "阈值列表（逗号分隔）",
            value="0.30,0.35,0.40,0.45,0.50,0.55,0.60",
            key="sweep_thresholds",
        )

        if st.button("提交阈值扫描任务", key="sweep_submit_btn", type="primary", use_container_width=True):
            if not sweep_weights:
                st.error("请先选择权重文件")
            elif not sweep_image_dir.strip():
                st.error("请输入测试图片目录")
            elif not sweep_db_path.strip():
                st.error("请输入特征数据库路径")
            else:
                result = call_api(
                    lambda: client.eval_submit_threshold_sweep(
                        weights_path=sweep_weights,
                        backbone=sweep_backbone,
                        image_dir=sweep_image_dir.strip(),
                        db_path=sweep_db_path.strip(),
                        thresholds=sweep_thresholds.strip(),
                        device=sweep_device,
                    ),
                    None,
                )
                if result:
                    job_id = result.get("job_id", "")
                    st.success(f"任务已提交：{result.get('message', '')}")
                    st.session_state["sweep_tracking_job_id"] = job_id

        # 轮询展示
        sweep_tracking_id = st.session_state.get("sweep_tracking_job_id", "")
        if sweep_tracking_id:
            st.markdown(f"**正在追踪任务 `{sweep_tracking_id}`**")
            placeholder2 = st.empty()
            job2 = _poll_eval_job(client, sweep_tracking_id, placeholder2)
            if job2 and job2.get("status") in ("running", "pending"):
                time.sleep(2)
                st.rerun()

    # ----------------------------------------------------------------
    # Tab 3: 评估历史
    # ----------------------------------------------------------------
    with tab_jobs:
        if st.button("刷新历史", key="eval_jobs_refresh", use_container_width=True):
            pass  # 点击即触发 rerun
        jobs_payload = call_api(lambda: client.eval_list_jobs(), {"jobs": []}) or {"jobs": []}
        jobs_list = jobs_payload.get("jobs", [])
        if not jobs_list:
            st.info("暂无评估记录。")
        else:
            for job in jobs_list:
                status_badge_colors = {"done": "#22C55E", "running": "#3B82F6", "pending": "#64748B", "error": "#EF4444"}
                status_labels = {"done": "Done", "running": "Running", "pending": "Pending", "error": "Error"}
                status = job["status"]
                badge_color = status_badge_colors.get(status, "#64748B")
                badge_text = status_labels.get(status, "?")
                label = (
                    f"<span style='display:inline-block;width:8px;height:8px;border-radius:50%;"
                    f"background:{badge_color};margin-right:6px;'></span>"
                    f"<span style='color:{badge_color};font-weight:600;font-size:0.8rem;'>{badge_text}</span> "
                    f"[{job['job_type']}] job_id=`{job['job_id']}` | "
                    f"{job.get('model_name')} | {Path(job.get('weights_path', '')).name}"
                )
                with st.expander(label, expanded=(job["status"] == "done")):
                    if job["status"] == "done":
                        _render_eval_job_result(job)
                    elif job["status"] == "error":
                        st.error("评估失败")
                        st.code(job.get("error", ""), language="text")
                    else:
                        st.info(f"状态: {job['status']} — {job.get('progress_msg', '')}")

    # ----------------------------------------------------------------
    # Tab 4: Benchmark（原有功能保留）
    # ----------------------------------------------------------------
    with tab_benchmark:
        if st.button("刷新 Benchmark", key="dev_refresh_benchmark", use_container_width=True):
            pass
        benchmark = call_api(lambda: client.developer_benchmark(), None)
        if benchmark:
            col1, col2 = st.columns(2)
            col1.metric("人员总数", benchmark.get("person_count", 0))
            col2.metric("特征总数", benchmark.get("embedding_count", 0))
            st.caption(f"数据库: {benchmark.get('database_path', '')}")
            st.markdown("#### 数据库类别分布（Top 10）")
            top_persons = benchmark.get("top_persons", [])
            if top_persons:
                names = [p["name"] for p in top_persons]
                counts = [p["embedding_count"] for p in top_persons]
                try:
                    import matplotlib.pyplot as plt
                    import io

                    fig, ax = plt.subplots(figsize=(8, 3))
                    ax.barh(names[::-1], counts[::-1], color="#4f8ef7")
                    ax.set_xlabel("Embedding 数量")
                    ax.set_title("人员 Embedding 分布")
                    ax.grid(axis="x", linestyle="--", alpha=0.4)
                    plt.tight_layout()
                    buf = io.BytesIO()
                    fig.savefig(buf, format="png", dpi=130)
                    plt.close(fig)
                    st.image(buf.getvalue(), use_container_width=True)
                except Exception:
                    for n, c in zip(names, counts):
                        st.write(f"- {n}: {c}")

            topn = st.slider("Gallery 分析 TopN", 3, 30, 10, key="dev_eval_topn")
            if st.button("分析当前 Gallery 分布", key="dev_eval_btn", type="primary", use_container_width=True):
                result = call_api(lambda: client.developer_model_eval(topn=topn), None)
                if result:
                    runtime = result.get("runtime", {})
                    st.success(
                        f"当前模型: **{runtime.get('model_name')}** | "
                        f"文件: `{Path(runtime.get('weights_path', '')).name}` | "
                        f"Gallery: {result.get('gallery_size', 0)} 条"
                    )
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown("**样本最多的身份**")
                        for item in result.get("class_balance_top", []):
                            st.write(f"- {item['name']}: {item['embedding_count']}")
                    with c2:
                        st.markdown("**样本最少的身份**")
                        for item in result.get("class_balance_bottom", []):
                            st.write(f"- {item['name']}: {item['embedding_count']}")
                    st.info(result.get("recommendation", ""))

    # ----------------------------------------------------------------
    # Tab 5: 模型管理（原有功能保留）
    # ----------------------------------------------------------------
    with tab_models:
        st.markdown("#### 上传模型")
        upload_file = st.file_uploader(
            "选择模型文件（.pt / .onnx）",
            type=["pt", "onnx"],
            key="dev_model_upload_file",
        )
        col1, col2 = st.columns(2)
        model_name_input = col1.text_input("模型名称", key="dev_model_name")
        backbone_input = col2.selectbox(
            "Backbone",
            ["iresnet18", "iresnet34", "iresnet50", "iresnet100"],
            index=2,
            key="dev_model_backbone",
        )
        embedding_size_input = st.number_input(
            "Embedding Size", min_value=64, max_value=2048, value=512, step=64
        )
        if st.button("上传模型", key="dev_upload_model_btn", type="primary", use_container_width=True):
            if upload_file is None:
                st.error("请先选择模型文件")
            elif not model_name_input.strip():
                st.error("请输入模型名称")
            else:
                uploaded = call_api(
                    lambda: client.upload_model(
                        file_name=upload_file.name,
                        content=upload_file.getvalue(),
                        name=model_name_input.strip(),
                        backbone=backbone_input,
                        embedding_size=int(embedding_size_input),
                    ),
                    None,
                )
                if uploaded:
                    st.success(f"模型上传成功：{uploaded.get('name')}")

        st.markdown("---")
        st.markdown("#### 已注册模型")
        models_payload = call_api(lambda: client.list_models(), {"models": []}) or {"models": []}
        models = models_payload.get("models", [])
        if not models:
            st.info("暂无模型记录")
        else:
            for item in models:
                if item.get("is_active"):
                    status_badge = '<span style="display:inline-flex;align-items:center;gap:4px;color:#22C55E;font-size:0.8rem;font-weight:600;"><span style="width:6px;height:6px;border-radius:50%;background:#22C55E;display:inline-block;"></span> Active 激活中</span>'
                else:
                    status_badge = '<span style="display:inline-flex;align-items:center;gap:4px;color:#64748B;font-size:0.8rem;font-weight:600;"><span style="width:6px;height:6px;border-radius:50%;background:#64748B;display:inline-block;"></span> Inactive 未激活</span>'
                st.markdown(
                    f"**{item['id']} | {item['name']}** {status_badge}  \n"
                    f"`{Path(item['path']).name}` | {item['framework']} | {item['backbone']} | "
                    f"dim={item.get('embedding_size', '?')}",
                    unsafe_allow_html=True,
                )
                col_act, col_del = st.columns(2)
                with col_act:
                    if st.button("激活", key=f"dev_activate_model_{item['id']}", use_container_width=True):
                        activated = call_api(lambda: client.activate_model(int(item["id"])), None)
                        if activated:
                            st.success(f"已激活：{activated.get('name')}")
                            st.rerun()
                with col_del:
                    if st.button("删除", key=f"dev_delete_model_{item['id']}", use_container_width=True):
                        deleted = call_api(lambda: client.delete_model(int(item["id"])), None)
                        if deleted and deleted.get("deleted"):
                            st.success("模型已删除")
                            st.rerun()
                        elif deleted and not deleted.get("deleted"):
                            st.warning(deleted.get("reason", "删除失败"))


def page_image_recognition():
    page_header("图片识别", "上传图片后调用后端推理服务返回检测框和识别结果。")
    threshold = st.slider("识别阈值", 0.0, 1.0, 0.45, 0.05)
    uploaded_file = st.file_uploader("上传图片", type=["jpg", "jpeg", "png", "bmp"])

    col_btn, col_clear = st.columns([3, 1])
    with col_btn:
        do_recognize = st.button("开始识别", type="primary", use_container_width=True)
    with col_clear:
        do_clear = st.button("清空结果", use_container_width=True,
                             disabled="image_result" not in st.session_state or st.session_state.get("image_result") is None)

    if do_clear:
        st.session_state.image_result = None
        st.rerun()

    if do_recognize and uploaded_file is not None:
        with st.spinner("正在通过 API 识别..."):
            result = call_api(lambda: get_client().recognize_image(uploaded_file.name, uploaded_file.getvalue(), threshold=threshold))
        if result:
            st.session_state.image_result = result
            st.rerun()
    elif do_recognize:
        st.error("请先上传图片")

    result = st.session_state.get("image_result")
    if not result:
        return

    st.markdown("#### 识别详情")
    for item in result.get("results", []):
        text = f"{item['display_name']} ({item['score'] * 100:.1f}%)"
        if item.get("accepted"):
            st.success(text)
        else:
            st.warning(text)
    if not result.get("results"):
        st.info("未检测到人脸")

    person_cards = result.get("person_cards", [])
    if person_cards:
        st.markdown("#### 人物资料卡")
        render_person_cards(person_cards)

    matched_pairs = result.get("matched_pairs", [])
    if matched_pairs:
        st.markdown("#### 图库图 vs 被识别图")
        annotated_img = result.get("annotated_image_base64")
        for idx, pair in enumerate(matched_pairs, start=1):
            gallery_img = pair.get("gallery_face_base64")
            query_img = pair.get("query_image_base64") or annotated_img or pair.get("query_face_base64")
            if not query_img:
                continue
            st.caption(f"匹配结果 {idx}: {pair.get('name', 'Unknown')}")
            if not gallery_img:
                st.warning(pair.get("gallery_error", "该匹配未找到图库参考图"))
                continue
            st.markdown(
                f"""
                <div class="match-pair-row">
                    <div class="match-pair-card">
                        <img src="data:image/jpeg;base64,{gallery_img}" alt="图库参考图" />
                        <p>图库参考图</p>
                    </div>
                    <div class="match-pair-card">
                        <img src="data:image/jpeg;base64,{query_img}" alt="被识别原图（含识别框）" />
                        <p>被识别原图（含识别框）</p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def page_video_recognition():
    page_header("视频识别", "上传视频文件，由后端完成逐帧识别、跟踪平滑和结果视频生成。")
    role = current_role()
    mode_options = ["视频中找人"] if role == "viewer" else ["视频中找人", "验证ID"]
    mode = st.radio("选择功能", mode_options, horizontal=True)
    verify_target = None
    if mode == "验证ID":
        persons = get_persons()
        if not persons:
            st.error("特征库为空，请先注册人员")
            return
        verify_target = st.selectbox("选择要验证的 ID", [item["name"] for item in persons])

    uploaded_file = st.file_uploader("上传视频", type=["mp4", "avi", "mov", "mkv"])
    col1, col2, col3 = st.columns(3)
    default_skip = 2 if role == "viewer" else 5
    default_threshold = 0.40 if role == "viewer" else 0.45
    default_stable = 2 if role == "viewer" else 3
    skip_frames = col1.slider("跳帧数", 1, 10, default_skip)
    threshold = col2.slider("识别阈值", 0.0, 1.0, default_threshold, 0.05)
    stable_frames = col3.slider("稳定帧数", 2, 10, default_stable)

    col_btn, col_clear = st.columns([3, 1])
    with col_btn:
        do_recognize = st.button("开始识别处理", type="primary", use_container_width=True)
    with col_clear:
        do_clear = st.button("清空结果", use_container_width=True,
                             disabled="video_result" not in st.session_state or st.session_state.get("video_result") is None)

    if do_clear:
        st.session_state.video_result = None
        st.rerun()

    if do_recognize and uploaded_file is not None:
        with st.spinner("后端正在处理视频，时间取决于视频长度..."):
            result = call_api(lambda: get_client().recognize_video(uploaded_file.name, uploaded_file.getvalue(), skip_frames, threshold, stable_frames, mode, verify_target))
        if result:
            st.session_state.video_result = result
            st.rerun()
    elif do_recognize:
        st.error("请先上传视频")

    if uploaded_file is not None:
        st.success(f"视频已上传: {uploaded_file.name}")

    result = st.session_state.get("video_result")
    if not result:
        return

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("总帧数", result["total_frames"])
    col2.metric("写入帧数", result["written_frames"])
    col3.metric("识别帧数", result["processed_frames"])
    col4.metric("识别人数", len(result["person_counts"]))
    if mode == "验证ID" and result.get("verify_result"):
        verify = result["verify_result"]
        if verify["passed"]:
            st.success(f"{verify['target']} 验证通过")
        else:
            st.error(f"{verify['target']} 验证失败，出现 {verify['frames']} 帧")
    elif result["person_counts"]:
        st.markdown("### 识别到的人员")
        for name, count in sorted(result["person_counts"].items()):
            st.write(f"**{name}**: {count} 次")
    else:
        st.info("视频中未识别到已注册人员")

    person_cards = result.get("person_cards", [])
    if person_cards:
        st.markdown("### 人物资料卡")
        render_person_cards(person_cards)

    st.markdown("### 识别结果视频")
    video_bytes = base64.b64decode(result["video_base64"])

    _, col_vid, _ = st.columns([1, 4, 1])
    with col_vid:
        st.video(video_bytes)

    st.download_button("下载识别后的视频", data=video_bytes, file_name=result["output_filename"], mime="video/mp4", use_container_width=True)


def page_camera():
    page_header("摄像头实时识别", "通过 API 启停摄像头任务，并在前端查看实时统计。停止摄像头后结果保留，点击清空按钮清除。")
    role = current_role()
    mode_options = ["视频中找人"] if role == "viewer" else ["视频中找人", "验证ID"]
    mode = st.radio("选择功能", mode_options, horizontal=True, key="camera_mode")
    verify_target = None
    if mode == "验证ID":
        persons = get_persons()
        if not persons:
            st.error("特征库为空，请先注册人员")
            return
        verify_target = st.selectbox("选择要验证的 ID", [item["name"] for item in persons])

    col1, col2, col3, col4 = st.columns(4)
    camera_id = col1.number_input("摄像头 ID", 0, 10, 0)
    default_skip = 2 if role == "viewer" else 3
    default_threshold = 0.40 if role == "viewer" else 0.45
    default_stable = 2 if role == "viewer" else 3
    skip_frames = col2.slider("跳帧数", 1, 10, default_skip)
    threshold = col3.slider("识别阈值", 0.0, 1.0, default_threshold, 0.05)
    stable_frames = col4.slider("稳定帧数", 2, 10, default_stable)
    client = get_client()

    # 初始化 session state
    if "camera_accumulated_stats" not in st.session_state:
        st.session_state.camera_accumulated_stats = {}
    if "camera_accumulated_frames" not in st.session_state:
        st.session_state.camera_accumulated_frames = 0
    if "camera_accumulated_processed" not in st.session_state:
        st.session_state.camera_accumulated_processed = 0

    col_start, col_stop, col_refresh, col_clear = st.columns(4)
    if col_start.button("启动摄像头", type="primary", use_container_width=True):
        # 启动前先清空后端旧数据
        call_api(lambda: client.clear_camera())
        st.session_state.camera_accumulated_stats = {}
        st.session_state.camera_accumulated_frames = 0
        st.session_state.camera_accumulated_processed = 0
        call_api(lambda: client.start_camera(camera_id, skip_frames, threshold, stable_frames, mode, verify_target))
        st.rerun()
    if col_stop.button("停止摄像头", use_container_width=True):
        call_api(lambda: client.stop_camera())
        st.rerun()
    if col_refresh.button("刷新状态", use_container_width=True):
        st.rerun()
    if col_clear.button("清空结果", use_container_width=True):
        call_api(lambda: client.clear_camera())
        st.session_state.camera_accumulated_stats = {}
        st.session_state.camera_accumulated_frames = 0
        st.session_state.camera_accumulated_processed = 0
        st.rerun()

    status = call_api(lambda: client.camera_status(), None)
    if not status:
        return

    # 合并本页面积累的统计数据（用于停止后仍保留历史记录）
    if status["running"] or status.get("total_frames", 0) > 0:
        backend_stats = status.get("stats", {})
        merged_stats = dict(st.session_state.camera_accumulated_stats)
        for name, count in backend_stats.items():
            merged_stats[name] = max(merged_stats.get(name, 0), count)
        st.session_state.camera_accumulated_stats = merged_stats
        st.session_state.camera_accumulated_frames = max(
            st.session_state.camera_accumulated_frames,
            status.get("total_frames", 0),
        )
        st.session_state.camera_accumulated_processed = max(
            st.session_state.camera_accumulated_processed,
            status.get("processed_frames", 0),
        )

    if status["running"]:
        st.success("摄像头运行中，识别画面由后端 OpenCV 窗口显示")
    else:
        st.info("摄像头未启动")

    col1, col2, col3 = st.columns(3)
    col1.metric("总帧数", st.session_state.camera_accumulated_frames)
    col2.metric("已识别帧", st.session_state.camera_accumulated_processed)
    col3.metric("FPS", f"{status['fps']:.1f}")

    for item in status.get("results", []):
        text = f"{item['display_name']} ({item['score'] * 100:.1f}%)"
        if item["accepted"]:
            st.success(text)
        else:
            st.warning(text)

    person_cards = status.get("person_cards", [])
    if person_cards:
        st.markdown("### 当前识别资料卡")
        render_person_cards(person_cards)

    if st.session_state.camera_accumulated_stats:
        st.markdown("### 累计已识别人员")
        for name, count in sorted(st.session_state.camera_accumulated_stats.items()):
            st.write(f"**{name}**: {count} 次")


def page_ai_portrait():
    """AI 肖像生成页面 - 基于 PhotoMaker V2 + SDXL 的 AI 肖像风格转换。"""
    import base64
    import io
    from PIL import Image

    page_header("AI 肖像生成", "基于 PhotoMaker V2 + Stable Diffusion XL，将人物照片转换为多种风格的AI肖像")

    if not is_logged_in():
        st.warning("请先在左侧登录后再使用 AI 肖像生成功能。")
        return

    client = get_client()

    # ── 步骤1: 获取已注册人员列表 ──
    st.markdown("### 1️⃣ 选择人员")

    try:
        persons_data = client.portrait_persons()
        persons = persons_data.get("persons", [])
    except ApiClientError as exc:
        st.error(f"无法获取人员列表: {exc}")
        return

    # 过滤有照片的人员
    persons_with_photos = [p for p in persons if p.get("image_paths") and len(p["image_paths"]) > 0]

    if not persons_with_photos:
        st.info("暂无已注册且有照片的人员。请先在「人员管理」中注册人员并上传照片。")
        return

    # 人员选择
    person_names = [p["name"] for p in persons_with_photos]
    selected_person = st.selectbox(
        "选择已注册人员",
        person_names,
        help="从数据库中已注册且有原始照片的人员中选择",
    )

    if not selected_person:
        return

    # ── 步骤2: 显示原始照片 ──
    st.markdown("### 2️⃣ 原始照片")

    # 获取选中人员的照片路径
    selected_data = next((p for p in persons_with_photos if p["name"] == selected_person), None)
    if selected_data is None:
        st.error("人员数据异常")
        return

    image_paths = selected_data["image_paths"]
    # 获取最新照片的 base64
    try:
        image_data = client.portrait_person_image(selected_person)
        original_b64 = image_data.get("image_base64", "")
        server_image_path = image_data.get("image_path", "")
    except ApiClientError as exc:
        st.error(f"无法获取人员照片: {exc}")
        return

    col_img, col_info = st.columns([1, 1])
    with col_img:
        if original_b64:
            st.image(
                base64.b64decode(original_b64),
                caption=f"{selected_person} 原始照片",
                use_container_width=True,
            )
        else:
            st.warning("无照片")

    with col_info:
        st.markdown(f"**人员名称:** {selected_person}")
        st.markdown(f"**照片数量:** {len(image_paths)} 张")
        st.markdown(f"**服务器路径:** `{server_image_path}`")
        if len(image_paths) > 1:
            st.markdown("**所有照片路径:**")
            for p in image_paths:
                st.markdown(f"- `{p}`")

    # ── 步骤3: 选择风格 ──
    st.markdown("### 3️⃣ 选择生成风格")

    # 获取风格列表
    try:
        styles_data = client.portrait_styles()
        styles = styles_data.get("styles", [])
    except ApiClientError:
        # 降级：使用本地硬编码的风格列表
        styles = [
            {"key": "business", "label": "💼 商务照"},
            {"key": "id_photo", "label": "🪪 证件照"},
            {"key": "ancient_chinese", "label": "🏮 古风写真"},
            {"key": "anime", "label": "🎨 动漫风格"},
            {"key": "cyberpunk", "label": "🤖 赛博朋克"},
            {"key": "professional", "label": "👔 职业形象照"},
        ]

    style_keys = [s["key"] for s in styles]
    style_labels = [s["label"] for s in styles]

    # 风格预览卡片
    style_cols = st.columns(len(styles))
    selected_style_idx = 0

    for i, (col, style) in enumerate(zip(style_cols, styles)):
        with col:
            style_desc = {
                "business": "正式商务形象",
                "id_photo": "标准证件照片",
                "ancient_chinese": "中国传统古风",
                "anime": "日系动漫风格",
                "cyberpunk": "未来科幻风格",
                "professional": "职场专业形象",
            }
            desc = style_desc.get(style["key"], "")
            st.markdown(
                f"""
                <div style="background:#1E293B; border:1px solid rgba(148,163,184,0.2);
                            border-radius:12px; padding:0.75rem; text-align:center; font-size:0.85rem;">
                    <div style="font-size:1.5rem; margin-bottom:0.25rem;">{style['label'][:2]}</div>
                    <div style="font-weight:600; color:#F8FAFC;">{style['label'][2:]}</div>
                    <div style="color:#94A3B8; font-size:0.75rem;">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    selected_style_label = st.selectbox(
        "风格选择",
        style_labels,
        help="选择要生成的 AI 肖像风格",
    )
    selected_style = styles[style_labels.index(selected_style_label)]["key"]

    st.markdown("---")

    # ── 步骤4: 高级选项 ──
    with st.expander("⚙️ 高级生成选项"):
        col_adv1, col_adv2, col_adv3 = st.columns(3)
        with col_adv1:
            seed = st.number_input(
                "随机种子 (Seed)",
                value=-1,
                step=1,
                help="相同种子产生相同结果。-1 表示随机种子。",
            )
        with col_adv2:
            num_steps = st.slider(
                "推理步数",
                min_value=20,
                max_value=100,
                value=50,
                step=5,
                help="步数越多质量越高，但生成更慢。推荐 30-50。",
            )
        with col_adv3:
            guidance = st.slider(
                "引导强度 (CFG)",
                min_value=1.0,
                max_value=15.0,
                value=5.0,
                step=0.5,
                help="控制对提示词的遵循程度。推荐 5.0。",
            )

        merge_step = st.slider(
            "ID 注入起始步 (Start Merge Step)",
            min_value=0,
            max_value=30,
            value=10,
            step=1,
            help="从第几步开始注入人物身份信息。值越小越像原图，但可能影响画质。推荐 10。",
        )

    # ── 步骤5: 生成按钮 ──
    st.markdown("### 4️⃣ 生成肖像")

    gen_col1, gen_col2, gen_col3 = st.columns([2, 1, 2])
    with gen_col2:
        generate_clicked = st.button(
            "🚀 生成 AI 肖像",
            type="primary",
            use_container_width=True,
            disabled=not is_logged_in(),
        )

    # 显示当前加载状态
    try:
        ps = client.portrait_status()
        model_loaded = ps.get("loaded", False)
        if model_loaded:
            st.success("✅ PhotoMaker 模型已加载，随时可以生成")
        else:
            st.info("💡 首次生成时将自动加载模型（需要 30-60 秒），请耐心等待")
    except Exception:
        pass

    if generate_clicked:
        if not server_image_path:
            st.error("无法确定参考图像路径，请重新选择人员")
            return

        seed_value = None if seed <= 0 else seed
        with st.spinner(f"🎨 正在为您生成 {selected_style_label} 风格的 AI 肖像...\n\n"
                        f"⏱️ 首次生成需要加载模型（约 30-60 秒），后续生成约 20-40 秒\n"
                        f"🖥️ 请勿刷新页面，耐心等待..."):
            try:
                result = client.portrait_generate(
                    person_name=selected_person,
                    image_path=server_image_path,
                    style=selected_style,
                    seed=seed_value,
                    num_inference_steps=num_steps,
                    guidance_scale=guidance,
                    start_merge_step=merge_step,
                )
            except ApiClientError as exc:
                st.error(f"❌ 生成失败: {exc}")
                return
            except Exception as exc:
                st.error(f"❌ 未知错误: {exc}")
                return

        # ── 步骤6: 显示结果 ──
        st.markdown("### 5️⃣ 生成结果")

        result_b64 = result.get("result_image_base64", "")
        output_path = result.get("output_path", "")
        elapsed = result.get("generation_time_seconds", 0)
        gen_seed = result.get("seed", 0)
        gen_prompt = result.get("prompt_used", "")

        col_res, col_meta = st.columns([2, 1])

        with col_res:
            if result_b64:
                result_img = Image.open(io.BytesIO(base64.b64decode(result_b64)))
                st.image(
                    result_img,
                    caption=f"{selected_person} - {selected_style_label} (seed={gen_seed})",
                    use_container_width=True,
                )

                # 下载按钮
                buf = io.BytesIO()
                result_img.save(buf, format="PNG")
                st.download_button(
                    label="📥 下载生成结果 (PNG)",
                    data=buf.getvalue(),
                    file_name=f"{selected_person}_{selected_style}_{gen_seed}.png",
                    mime="image/png",
                    type="primary",
                )
            else:
                st.warning("生成结果为空，请重试")

        with col_meta:
            st.markdown("**📋 生成详情**")
            st.markdown(f"- 风格: {result.get('style_label', selected_style)}")
            st.markdown(f"- 种子: {gen_seed}")
            st.markdown(f"- 耗时: {elapsed:.1f} 秒")
            st.markdown(f"- 尺寸: {result.get('width', 0)} × {result.get('height', 0)}")
            st.markdown(f"- 推理步数: {num_steps}")
            st.markdown(f"- 引导强度: {guidance:.1f}")
            st.markdown("")
            st.markdown(f"**📁 保存路径:**")
            st.code(output_path, language=None)
            st.markdown("")
            st.markdown("**💬 提示词:**")
            with st.expander("查看完整 Prompt"):
                st.text_area("Positive Prompt", gen_prompt, height=100, key="pos_prompt")
                st.text_area(
                    "Negative Prompt",
                    "(nsfw, worst quality, low quality, blurry, distorted face, bad anatomy, cartoon, painting)",
                    height=60,
                    key="neg_prompt",
                )

        st.success(f"✅ {result.get('message', '生成完成!')}")

        # 卸载模型按钮（释放显存）
        st.markdown("---")
        if st.button("🗑️ 卸载模型（释放 GPU 显存）", help="卸载 PhotoMaker 管线以释放显存给其他任务使用"):
            try:
                client.portrait_unload()
                st.success("模型已卸载，GPU 显存已释放")
                st.info("下次生成时将重新加载模型")
            except ApiClientError as exc:
                st.error(f"卸载失败: {exc}")


def main():
    init_session_state()
    inject_global_styles()

    with st.sidebar:
        st.markdown(
            f"""
            <div class="sidebar-logo">
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
                    <line x1="8" y1="21" x2="16" y2="21"/>
                    <line x1="12" y1="17" x2="12" y2="21"/>
                    <circle cx="12" cy="10" r="3"/>
                    <path d="M12 7v1" style="display:none"/>
                </svg>
                <div style="text-align:left;">
                    <h1>E-Recognition</h1>
                    <p>AI 视觉识别平台</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    role = current_role()
    if role == "viewer":
        nav_pages = ["Home 主页", "Face 人脸录入", "AI 肖像生成", "Camera 摄像头识别", "Image 图片识别", "Video 视频识别"]
    elif role in ("admin", "developer"):
        nav_pages = ["Home 主页", "People 人员管理", "Dev 开发者工作台", "AI 肖像生成", "Camera 摄像头识别", "Image 图片识别", "Video 视频识别"]
    else:
        nav_pages = ["Home 主页", "People 人员管理", "AI 肖像生成", "Camera 摄像头识别", "Image 图片识别", "Video 视频识别"]

    page = st.sidebar.radio("导航", nav_pages, label_visibility="collapsed")
    
    show_sidebar_controls()

    if "Home" in page:
        page_home()
    elif "Face" in page:
        page_face_enrollment()
    elif "People" in page:
        page_person_management()
    elif "Dev" in page:
        page_developer_console()
    elif "AI" in page or "肖像" in page:
        page_ai_portrait()
    elif "Camera" in page:
        page_camera()
    elif "Image" in page:
        page_image_recognition()
    elif "Video" in page:
        page_video_recognition()


if __name__ == "__main__":
    main()
