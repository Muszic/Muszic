#!/usr/bin/env python3
"""Build crisp vector brand/skill panels for the Ben 10 inspired profile.

The artwork uses recognizable project/company marks inside original glassy frames.
Brand marks are not redrawn by a generative model: their vector geometry is kept
separate from the fan-inspired UI treatment.
"""
from __future__ import annotations

from pathlib import Path
from html import escape

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
BRANDS = ASSETS / "brands"
ASSETS.mkdir(parents=True, exist_ok=True)
BRANDS.mkdir(parents=True, exist_ok=True)

INK = "#13282A"
INK2 = "#233A34"
MUTED = "#66736A"
GREEN = "#0A7A43"
LIME = "#82E35B"
PALE = "#EEF5E8"
PAPER = "#F8FAF4"
WHITE = "#FEFFF9"
LINE = "#D5E0D0"

# Visual Studio Code geometry from the VS Code icon distributed by Skill Icons.
VSCODE_PATHS = (
    ("#2489CA", "M33.7158 100.208C33.7158 100.208 28.9814 96.795 34.6627 92.2381L47.8994 80.402C47.8994 80.402 51.6869 76.4172 55.6915 79.8891L177.84 172.368V216.714C177.84 216.714 177.781 223.678 168.844 222.908L33.7158 100.208Z"),
    ("#1070B3", "M65.1997 128.792L33.7157 157.415C33.7157 157.415 30.4805 159.822 33.7157 164.123L48.3333 177.418C48.3333 177.418 51.8052 181.147 56.9341 176.905L90.3119 151.596L65.1997 128.792Z"),
    ("#0877B9", "M120.474 129.029L178.215 84.9391L177.84 40.83C177.84 40.83 175.374 31.2033 167.148 36.2139L90.312 106.145L120.474 129.029Z"),
    ("#3C99D4", "M168.844 222.968C172.198 226.4 176.262 225.276 176.262 225.276L221.259 203.103C227.019 199.177 226.21 194.305 226.21 194.305V61.8982C226.21 56.0788 220.252 54.0667 220.252 54.0667L181.253 35.267C172.731 30 167.148 36.2139 167.148 36.2139C167.148 36.2139 174.328 31.0455 177.84 40.83V215.905C177.84 217.109 177.583 218.292 177.071 219.358C176.045 221.429 173.816 223.362 168.47 222.553L168.844 222.968Z"),
)

# Standard four-colour Google G geometry (48 x 48).
GOOGLE_PATHS = (
    ("#FFC107", "M43.611 20.083H42V20H24v8h11.303C33.65 32.657 29.223 36 24 36c-6.627 0-12-5.373-12-12S17.373 12 24 12c3.059 0 5.842 1.154 7.961 3.039l5.657-5.657C34.046 6.053 29.268 4 24 4 12.955 4 4 12.955 4 24s8.955 20 20 20 20-8.955 20-20c0-1.341-.138-2.65-.389-3.917z"),
    ("#FF3D00", "M6.306 14.691l6.571 4.819C14.655 15.108 18.961 12 24 12c3.059 0 5.842 1.154 7.961 3.039l5.657-5.657C34.046 6.053 29.268 4 24 4 16.318 4 9.656 8.337 6.306 14.691z"),
    ("#4CAF50", "M24 44c5.166 0 9.86-1.977 13.409-5.192l-6.19-5.238C29.211 35.091 26.715 36 24 36c-5.202 0-9.619-3.317-11.283-7.946l-6.522 5.025C9.505 39.556 16.227 44 24 44z"),
    ("#1976D2", "M43.611 20.083H42V20H24v8h11.303c-.792 2.237-2.231 4.166-4.087 5.571l6.193 5.237C39.993 36.445 44 30.668 44 24c0-1.341-.138-2.65-.389-3.917z"),
)

# Salesforce icon from Font Awesome's brands collection (640 x 512).
SALESFORCE_PATH = "M248.89 245.64h-26.35c.69-5.16 3.32-14.12 13.64-14.12 6.75 0 11.97 3.82 12.71 14.12zm136.66-13.88c-.47 0-14.11-1.77-14.11 20s13.63 20 14.11 20c13 0 14.11-13.54 14.11-20 0-21.76-13.66-20-14.11-20zm-243.22 23.76a8.63 8.63 0 0 0-3.29 7.29c0 4.78 2.08 6.05 3.29 7.05 4.7 3.7 15.07 2.12 20.93.95v-16.94c-5.32-1.07-16.73-1.96-20.93 1.65zM640 232c0 87.58-80 154.39-165.36 136.43-18.37 33-70.73 70.75-132.2 41.63-41.16 96.05-177.89 92.18-213.81-5.17C8.91 428.78-50.19 266.52 53.36 205.61 18.61 126.18 76 32 167.67 32a124.24 124.24 0 0 1 98.56 48.7c20.7-21.4 49.4-34.81 81.15-34.81 42.34 0 79 23.52 98.8 58.57C539 63.78 640 132.69 640 232zm-519.55 31.8c0-11.76-11.69-15.17-17.87-17.17-5.27-2.11-13.41-3.51-13.41-8.94 0-9.46 17-6.66 25.17-2.12 0 0 1.17.71 1.64-.47.24-.7 2.36-6.58 2.59-7.29a1.13 1.13 0 0 0-.7-1.41c-12.33-7.63-40.7-8.51-40.7 12.7 0 12.46 11.49 15.44 17.88 17.17 4.72 1.58 13.17 3 13.17 8.7 0 4-3.53 7.06-9.17 7.06a31.76 31.76 0 0 1-19-6.35c-.47-.23-1.42-.71-1.65.71l-2.4 7.47c-.47.94.23 1.18.23 1.41 1.75 1.4 10.3 6.59 22.82 6.59 13.17 0 21.4-7.06 21.4-18.11zm32-42.58c-10.13 0-18.66 3.17-21.4 5.18a1 1 0 0 0-.24 1.41l2.59 7.06a1 1 0 0 0 1.18.7c.65 0 6.8-4 16.93-4 4 0 7.06.71 9.18 2.36 3.6 2.8 3.06 8.29 3.06 10.58-4.79-.3-19.11-3.44-29.41 3.76a16.92 16.92 0 0 0-7.34 14.54c0 5.9 1.51 10.4 6.59 14.35 12.24 8.16 36.28 2 38.1 1.41 1.58-.32 3.53-.66 3.53-1.88v-33.88c.04-4.61.32-21.64-22.78-21.64zM199 200.24a1.11 1.11 0 0 0-1.18-1.18H188a1.11 1.11 0 0 0-1.17 1.18v79a1.11 1.11 0 0 0 1.17 1.18h9.88a1.11 1.11 0 0 0 1.18-1.18zm55.75 28.93c-2.1-2.31-6.79-7.53-17.65-7.53-3.51 0-14.16.23-20.7 8.94-6.35 7.63-6.58 18.11-6.58 21.41 0 3.12.15 14.26 7.06 21.17 2.64 2.91 9.06 8.23 22.81 8.23 10.82 0 16.47-2.35 18.58-3.76.47-.24.71-.71.24-1.88l-2.35-6.83a1.26 1.26 0 0 0-1.41-.7c-2.59.94-6.35 2.82-15.29 2.82-17.42 0-16.85-14.74-16.94-16.7h37.17a1.23 1.23 0 0 0 1.17-.94c-.29 0 2.07-14.7-6.09-24.23zm36.69 52.69c13.17 0 21.41-7.06 21.41-18.11 0-11.76-11.7-15.17-17.88-17.17-4.14-1.66-13.41-3.38-13.41-8.94 0-3.76 3.29-6.35 8.47-6.35a38.11 38.11 0 0 1 16.7 4.23s1.18.71 1.65-.47c.23-.7 2.35-6.58 2.58-7.29a1.13 1.13 0 0 0-.7-1.41c-7.91-4.9-16.74-4.94-20.23-4.94-12 0-20.46 7.29-20.46 17.64 0 12.46 11.48 15.44 17.87 17.17 6.11 2 13.17 3.26 13.17 8.7 0 4-3.52 7.06-9.17 7.06a31.8 31.8 0 0 1-19-6.35 1 1 0 0 0-1.65.71l-2.35 7.52c-.47.94.23 1.18.23 1.41 1.72 1.4 10.33 6.59 22.79 6.59zM357.09 224c0-.71-.24-1.18-1.18-1.18h-11.76c0-.14.94-8.94 4.47-12.47 4.16-4.15 11.76-1.64 12-1.64 1.17.47 1.41 0 1.64-.47l2.83-7.77c.7-.94 0-1.17-.24-1.41-5.09-2-17.35-2.87-24.46 4.24-5.48 5.48-7 13.92-8 19.52h-8.47a1.28 1.28 0 0 0-1.17 1.18l-1.42 7.76c0 .7.24 1.17 1.18 1.17h8.23c-8.51 47.9-8.75 50.21-10.35 55.52-1.08 3.62-3.29 6.9-5.88 7.76-.09 0-3.88 1.68-9.64-.24 0 0-.94-.47-1.41.71-.24.71-2.59 6.82-2.83 7.53s0 1.41.47 1.41c5.11 2 13 1.77 17.88 0 6.28-2.28 9.72-7.89 11.53-12.94 2.75-7.71 2.81-9.79 11.76-59.74h12.23a1.29 1.29 0 0 0 1.18-1.18zm53.39 16c-.56-1.68-5.1-18.11-25.17-18.11-15.25 0-23 10-25.16 18.11-1 3-3.18 14 0 23.52.09.3 4.41 18.12 25.16 18.12 14.95 0 22.9-9.61 25.17-18.12 3.21-9.61 1.01-20.52 0-23.52zm45.4-16.7c-5-1.65-16.62-1.9-22.11 5.41v-4.47a1.11 1.11 0 0 0-1.18-1.17h-9.4a1.11 1.11 0 0 0-1.18 1.17v55.28a1.12 1.12 0 0 0 1.18 1.18h9.64a1.12 1.12 0 0 0 1.18-1.18v-27.77c0-2.91.05-11.37 4.46-15.05 4.9-4.9 12-3.36 13.41-3.06a1.57 1.57 0 0 0 1.41-.94 74 74 0 0 0 3.06-8 1.16 1.16 0 0 0-.47-1.41zm46.81 54.1l-2.12-7.29c-.47-1.18-1.41-.71-1.41-.71-4.23 1.82-10.15 1.89-11.29 1.89-4.64 0-17.17-1.13-17.17-19.76 0-6.23 1.85-19.76 16.47-19.76a34.85 34.85 0 0 1 11.52 1.65s.94.47 1.18-.71c.94-2.59 1.64-4.47 2.59-7.53.23-.94-.47-1.17-.71-1.17-11.59-3.87-22.34-2.53-27.76 0-1.59.74-16.23 6.49-16.23 27.52 0 2.9-.58 30.11 28.94 30.11a44.45 44.45 0 0 0 15.52-2.83 1.3 1.3 0 0 0 .47-1.42zm53.87-39.52c-.8-3-5.37-16.23-22.35-16.23-16 0-23.52 10.11-25.64 18.59a38.58 38.58 0 0 0-1.65 11.76c0 25.87 18.84 29.4 29.88 29.4 10.82 0 16.46-2.35 18.58-3.76.47-.24.71-.71.24-1.88l-2.36-6.83a1.26 1.26 0 0 0-1.41-.7c-2.59.94-6.35 2.82-15.29 2.82-17.42 0-16.85-14.74-16.93-16.7h37.16a1.25 1.25 0 0 0 1.18-.94c-.24-.01.94-7.07-1.41-15.54zm-23.29-6.35c-10.33 0-13 9-13.64 14.12H546c-.88-11.92-7.62-14.13-12.73-14.13z"

# Python, Docker, Git and GitHub paths from Font Awesome brands.
PYTHON_PATH = "M439.8 200.5c-7.7-30.9-22.3-54.2-53.4-54.2h-40.1v47.4c0 36.8-31.2 67.8-66.8 67.8H172.7c-29.2 0-53.4 25-53.4 54.3v101.8c0 29 25.2 46 53.4 54.3 33.8 9.9 66.3 11.7 106.8 0 26.9-7.8 53.4-23.5 53.4-54.3v-40.7H226.2v-13.6h160.2c31.1 0 42.6-21.7 53.4-54.2 11.2-33.5 10.7-65.7 0-108.6zM286.2 404c11.1 0 20.1 9.1 20.1 20.3 0 11.3-9 20.4-20.1 20.4-11 0-20.1-9.2-20.1-20.4.1-11.3 9.1-20.3 20.1-20.3zM167.8 248.1h106.8c29.7 0 53.4-24.5 53.4-54.3V91.9c0-29-24.4-50.7-53.4-55.6-35.8-5.9-74.7-5.6-106.8.1-45.2 8-53.4 24.7-53.4 55.6v40.7h106.9v13.6h-147c-31.1 0-58.3 18.7-66.8 54.2-9.8 40.7-10.2 66.1 0 108.6 7.6 31.6 25.7 54.2 56.8 54.2H101v-48.8c0-35.3 30.5-66.4 66.8-66.4zm-6.7-142.6c-11.1 0-20.1-9.1-20.1-20.3.1-11.3 9-20.4 20.1-20.4 11 0 20.1 9.2 20.1 20.4s-9 20.3-20.1 20.3z"
DOCKER_PATH = "M349.9 236.3h-66.1v-59.4h66.1v59.4zm0-204.3h-66.1v60.7h66.1V32zm78.2 144.8H362v59.4h66.1v-59.4zm-156.3-72.1h-66.1v60.1h66.1v-60.1zm78.1 0h-66.1v60.1h66.1v-60.1zm276.8 100c-14.4-9.7-47.6-13.2-73.1-8.4-3.3-24-16.7-44.9-41.1-63.7l-14-9.3-9.3 14c-18.4 27.8-23.4 73.6-3.7 103.8-8.7 4.7-25.8 11.1-48.4 10.7H2.4c-8.7 50.8 5.8 116.8 44 162.1 37.1 43.9 92.7 66.2 165.4 66.2 157.4 0 273.9-72.5 328.4-204.2 21.4.4 67.6.1 91.3-45.2 1.5-2.5 6.6-13.2 8.5-17.1l-13.3-8.9zm-511.1-27.9h-66v59.4h66.1v-59.4zm78.1 0h-66.1v59.4h66.1v-59.4zm78.1 0h-66.1v59.4h66.1v-59.4zm-78.1-72.1h-66.1v60.1h66.1v-60.1z"
GIT_PATH = "M439.55 236.05L244 40.45a28.87 28.87 0 0 0-40.81 0l-40.66 40.63 51.52 51.52c27.06-9.14 52.68 16.77 43.39 43.68l49.66 49.66c34.23-11.8 61.18 31 35.47 56.69-26.49 26.49-70.21-2.87-56-37.34L240.22 199v121.85c25.3 12.54 22.26 41.85 9.08 55a34.34 34.34 0 0 1-48.55 0c-17.57-17.6-11.07-46.91 11.25-56v-123c-20.8-8.51-24.6-30.74-18.64-45L142.57 101 8.45 235.14a28.86 28.86 0 0 0 0 40.81l195.61 195.6a28.86 28.86 0 0 0 40.8 0l194.69-194.69a28.86 28.86 0 0 0 0-40.81z"
GITHUB_PATH = "M165.9 397.4c0 2-2.3 3.6-5.2 3.6-3.3.3-5.6-1.3-5.6-3.6 0-2 2.3-3.6 5.2-3.6 3-.3 5.6 1.3 5.6 3.6zm-31.1-4.5c-.7 2 1.3 4.3 4.3 4.9 2.6 1 5.6 0 6.2-2s-1.3-4.3-4.3-5.2c-2.6-.7-5.5.3-6.2 2.3zm44.2-1.7c-2.9.7-4.9 2.6-4.6 4.9.3 2 2.9 3.3 5.9 2.6 2.9-.7 4.9-2.6 4.6-4.6-.3-1.9-3-3.2-5.9-2.9zM244.8 8C106.1 8 0 113.3 0 252c0 110.9 69.8 205.8 169.5 239.2 12.8 2.3 17.3-5.6 17.3-12.1 0-6.2-.3-40.4-.3-61.4 0 0-70 15-84.7-29.8 0 0-11.4-29.1-27.8-36.6 0 0-22.9-15.7 1.6-15.4 0 0 24.9 2 38.6 25.8 21.9 38.6 58.6 27.5 72.9 20.9 2.3-16 8.8-27.1 16-33.7-55.9-6.2-112.3-14.3-112.3-110.5 0-27.5 7.6-41.3 23.6-58.9-2.6-6.5-11.1-33.3 2.6-67.9 20.9-6.5 69 27 69 27 20-5.6 41.5-8.5 62.8-8.5s42.8 2.9 62.8 8.5c0 0 48.1-33.6 69-27 13.7 34.7 5.2 61.4 2.6 67.9 16 17.7 25.8 31.5 25.8 58.9 0 96.5-58.9 104.2-114.8 110.5 9.2 7.9 17 22.9 17 46.4 0 33.7-.3 75.4-.3 83.6 0 6.5 4.6 14.4 17.3 12.1C428.2 457.8 496 362.9 496 252 496 113.3 383.5 8 244.8 8zM97.2 352.9c-1.3 1-1 3.3.7 5.2 1.6 1.6 3.9 2.3 5.2 1 1.3-1 1-3.3-.7-5.2-1.6-1.6-3.9-2.3-5.2-1zm-10.8-8.1c-.7 1.3.3 2.9 2.3 3.9 1.6 1 3.6.7 4.3-.7.7-1.3-.3-2.9-2.3-3.9-2-.6-3.6-.3-4.3.7zm32.4 35.6c-1.6 1.3-1 4.3 1.3 6.2 2.3 2.3 5.2 2.6 6.5 1 1.3-1.3.7-4.3-1.3-6.2-2.2-2.3-5.2-2.6-6.5-1zm-11.4-14.7c-1.6 1-1.6 3.6 0 5.9 1.6 2.3 4.3 3.3 5.6 2.3 1.6-1.3 1.6-3.9 0-6.2-1.4-2.3-4-3.3-5.6-2z"


def defs() -> str:
    return f'''<defs>
  <linearGradient id="panel" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#FFFFFF"/><stop offset="1" stop-color="#EDF5E8"/></linearGradient>
  <linearGradient id="glass" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#FFFFFF" stop-opacity=".98"/><stop offset=".58" stop-color="#FCFFF9" stop-opacity=".92"/><stop offset="1" stop-color="#E9F2E4" stop-opacity=".90"/></linearGradient>
  <linearGradient id="metal" x1=".15" y1=".05" x2=".85" y2=".95"><stop stop-color="#FFFFFF"/><stop offset=".22" stop-color="#E7EFE3"/><stop offset=".56" stop-color="#AEBDB0"/><stop offset=".78" stop-color="#F8FFF3"/><stop offset="1" stop-color="#718276"/></linearGradient>
  <linearGradient id="pythonGradient" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#3776AB"/><stop offset=".55" stop-color="#3776AB"/><stop offset=".56" stop-color="#FFD343"/><stop offset="1" stop-color="#FFD343"/></linearGradient>
  <radialGradient id="greenGlow"><stop stop-color="#82E35B" stop-opacity=".58"/><stop offset="1" stop-color="#82E35B" stop-opacity="0"/></radialGradient>
  <filter id="shadow" x="-25%" y="-25%" width="150%" height="170%"><feDropShadow dx="0" dy="12" stdDeviation="15" flood-color="#1F4C31" flood-opacity=".16"/></filter>
  <filter id="softShadow" x="-25%" y="-25%" width="150%" height="170%"><feDropShadow dx="0" dy="7" stdDeviation="9" flood-color="#1F4C31" flood-opacity=".13"/></filter>
  <filter id="logoGlow" x="-60%" y="-60%" width="220%" height="220%"><feDropShadow dx="0" dy="5" stdDeviation="8" flood-color="#6FDB5F" flood-opacity=".35"/></filter>
</defs>'''


def style() -> str:
    return '''<style>
text{font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif}.title{font-size:36px;font-weight:780;letter-spacing:-1.4px;fill:#13282A}.eyebrow{font-size:13px;font-weight:780;letter-spacing:1.7px;fill:#0A7A43}.company{font-size:30px;font-weight:780;letter-spacing:-.8px;fill:#13282A}.role{font-size:17px;font-weight:720;fill:#233A34}.body{font-size:15px;fill:#66736A}.small{font-size:11px;font-weight:720;letter-spacing:1px;fill:#0A7A43}.tileLabel{font-size:13px;font-weight:720;fill:#233A34}.tileGroup{font-size:11px;font-weight:760;letter-spacing:1.2px;fill:#0A7A43}.prTitle{font-size:25px;font-weight:780;letter-spacing:-.6px;fill:#13282A}.prBody{font-size:16px;fill:#536259}
</style>'''


def svg_root(width: int, height: int, title: str, body: str) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title">
<title id="title">{escape(title)}</title>
{defs()}
{style()}
<rect width="{width}" height="{height}" rx="30" fill="url(#panel)"/>
<ellipse cx="{int(width*.72)}" cy="32" rx="340" ry="220" fill="url(#greenGlow)" opacity=".22"/>
{body}
</svg>'''


def orb(cx: float, cy: float, r: float, icon: str, inner: str = "#FFFFFF", glow: str = "#82E35B") -> str:
    return f'''<g transform="translate({cx} {cy})" filter="url(#logoGlow)">
<circle r="{r*1.28:.1f}" fill="{glow}" opacity=".12"/>
<circle cy="{r*.10:.1f}" r="{r:.1f}" fill="#163A28" opacity=".18"/>
<circle r="{r:.1f}" fill="url(#metal)" stroke="#315E43" stroke-width="2"/>
<circle r="{r*.77:.1f}" fill="{inner}" stroke="#D8E3D4" stroke-width="1.4"/>
<path d="M{-r*.56:.1f} {-r*.57:.1f}A{r*.76:.1f} {r*.76:.1f} 0 0 1 {r*.48:.1f} {-r*.61:.1f}" fill="none" stroke="#FFFFFF" stroke-opacity=".86" stroke-width="{max(2,r*.07):.1f}" stroke-linecap="round"/>
{icon}
</g>'''


def vscode_icon(size: float) -> str:
    scale = size / 256
    parts = ''.join(f'<path fill="{color}" d="{path}"/>' for color, path in VSCODE_PATHS)
    return f'<g transform="translate({-size/2:.2f} {-size/2:.2f}) scale({scale:.6f})">{parts}</g>'


def google_icon(size: float) -> str:
    scale = size / 48
    parts = ''.join(f'<path fill="{color}" d="{path}"/>' for color, path in GOOGLE_PATHS)
    return f'<g transform="translate({-size/2:.2f} {-size/2:.2f}) scale({scale:.6f})">{parts}</g>'


def salesforce_icon(size: float) -> str:
    scale = size / 640
    # Center the 640x512 mark inside a square.
    return f'<g transform="translate({-size/2:.2f} {-size*0.40:.2f}) scale({scale:.6f})"><path fill="#00A1E0" d="{SALESFORCE_PATH}"/></g>'


def tenstorrent_icon(size: float) -> str:
    scale = size / 85
    return f'''<g transform="translate({-size/2:.2f} {-size/2:.2f}) scale({scale:.6f})">
<path d="M21.4062 48.0411V72.0137L42.524 84L63.6417 72.0137V48.0411L42.524 60.0274L21.4062 48.0411Z" fill="#786BB0"/>
<path d="M21.4063 48.0411V24.4041L42.5241 36.3904L63.6418 24.4041L42.5241 11.9863L21.4063 0L0 12.0822V36.0548L21.4063 48.0411Z" fill="#FFD10A"/>
<path d="M85.0001 12.0821L63.6418 .0479V24.404V47.9931L85.0001 36.0547V12.0821Z" fill="#F04F5E"/>
</g>'''


def microsoft_icon(size: float) -> str:
    s = size * .42
    gap = size * .07
    x = -s-gap/2
    y = -s-gap/2
    return f'''<g>
<rect x="{x:.2f}" y="{y:.2f}" width="{s-gap:.2f}" height="{s-gap:.2f}" fill="#F25022"/>
<rect x="{gap/2:.2f}" y="{y:.2f}" width="{s-gap:.2f}" height="{s-gap:.2f}" fill="#7FBA00"/>
<rect x="{x:.2f}" y="{gap/2:.2f}" width="{s-gap:.2f}" height="{s-gap:.2f}" fill="#00A4EF"/>
<rect x="{gap/2:.2f}" y="{gap/2:.2f}" width="{s-gap:.2f}" height="{s-gap:.2f}" fill="#FFB900"/>
</g>'''


def omnitrix_mark(cx: int, cy: int, r: int) -> str:
    q = r * .50
    return f'''<g transform="translate({cx} {cy})" filter="url(#softShadow)"><circle r="{r}" fill="url(#metal)" stroke="#1D5E3A" stroke-width="2"/><circle r="{r*.75}" fill="#13282A" stroke="#B8F29E"/><path d="M{-q} {-q}H{q}L{q*.28} 0L{q} {q}H{-q}L{-q*.28} 0Z" fill="#82E35B"/><path d="M{-r*.54} {-r*.55}A{r*.72} {r*.72} 0 0 1 {r*.47} {-r*.60}" fill="none" stroke="#FFF" stroke-opacity=".72" stroke-width="3" stroke-linecap="round"/></g>'''


def build_brand_files() -> None:
    samples = {
        "vscode.svg": (vscode_icon(170), "#F6FBFF"),
        "google-g.svg": (google_icon(170), "#FFFFFF"),
        "salesforce.svg": (salesforce_icon(178), "#FFFFFF"),
        "tenstorrent.svg": (tenstorrent_icon(164), "#15191C"),
        "microsoft.svg": (microsoft_icon(165), "#FFFFFF"),
    }
    for name, (icon, inner) in samples.items():
        body = orb(128, 128, 104, icon, inner=inner)
        BRANDS.joinpath(name).write_text(svg_root(256, 256, name[:-4], body), encoding="utf-8")


def build_experience(mobile: bool = False) -> str:
    width = 600 if mobile else 1200
    entries = [
        ("NOW", "Salesforce", "Associate Member of Technical Staff", ["Enterprise software", "Salesforce Platform"], "Bengaluru, India", salesforce_icon, "#F9FDFF", "#66C7F0"),
        ("PREVIOUSLY", "Tenstorrent", "AI Intern", ["AI acceleration", "TT-Metalium"], "Engineering systems", tenstorrent_icon, "#171B1D", "#FFD10A"),
        ("MAY — JUL 2025", "Microsoft", "Software Engineer Intern", ["SharePoint Embedded", "Office Document Services & Platforms"], "Hyderabad, India", microsoft_icon, "#FFFFFF", "#61BDF1"),
    ]
    body = []
    if mobile:
        body.append('<text x="34" y="45" class="eyebrow">FIELD LOG / EXPERIENCE</text>')
        body.append('<text x="32" y="86" class="title">Three teams. One engineering path.</text>')
        body.append('<text x="34" y="113" class="body">Enterprise platforms, AI acceleration, and developer-facing products.</text>')
        body.append(omnitrix_mark(546, 48, 28))
        for i, (period, company, role, focus, foot, icon_fn, inner, glow) in enumerate(entries):
            y = 142 + i * 292
            body.append(f'''<g transform="translate(20 {y})" filter="url(#shadow)">
<rect width="560" height="264" rx="28" fill="url(#glass)" stroke="#D1DFCC"/>
<rect x="18" y="18" width="7" height="228" rx="4" fill="#65DA57"/>
<rect x="403" y="19" width="137" height="31" rx="15" fill="#ECF7E6" stroke="#CFE5C6"/>
<text x="471" y="40" class="small" text-anchor="middle">{escape(period)}</text>
{orb(96, 86, 56, icon_fn(82), inner=inner, glow=glow)}
<text x="169" y="79" class="company">{escape(company)}</text>
<text x="169" y="109" class="role">{escape(role)}</text>
<text x="49" y="163" class="body">{escape(focus[0])}</text>
<text x="49" y="188" class="body">{escape(focus[1])}</text>
<path d="M49 211H514" stroke="#D8E1D4"/>
<circle cx="53" cy="233" r="4" fill="#0A7A43"/><text x="65" y="238" class="body">{escape(foot)}</text>
<text x="516" y="238" class="small" text-anchor="end">MODE 0{i+1}</text>
</g>''')
        return svg_root(width, 1030, "Experience at Salesforce, Tenstorrent, and Microsoft with authentic brand marks", ''.join(body))

    body.append('<text x="38" y="44" class="eyebrow">FIELD LOG / EXPERIENCE</text>')
    body.append('<text x="36" y="90" class="title">Three teams. One engineering path.</text>')
    body.append('<text x="38" y="119" class="body">Enterprise platforms, AI acceleration, and developer-facing products.</text>')
    body.append(omnitrix_mark(1138, 52, 30))
    for i, (period, company, role, focus, foot, icon_fn, inner, glow) in enumerate(entries):
        x = 28 + i * 390
        body.append(f'''<g transform="translate({x} 151)" filter="url(#shadow)">
<rect width="364" height="295" rx="29" fill="url(#glass)" stroke="#D1DFCC"/>
<rect x="17" y="17" width="7" height="261" rx="4" fill="#65DA57"/>
<rect x="211" y="18" width="134" height="31" rx="15" fill="#ECF7E6" stroke="#CFE5C6"/>
<text x="278" y="39" class="small" text-anchor="middle">{escape(period)}</text>
{orb(92, 86, 58, icon_fn(84), inner=inner, glow=glow)}
<text x="40" y="167" class="company">{escape(company)}</text>
<text x="40" y="197" class="role">{escape(role)}</text>
<text x="40" y="228" class="body">{escape(focus[0])}</text>
<text x="40" y="251" class="body">{escape(focus[1])}</text>
<circle cx="44" cy="273" r="4" fill="#0A7A43"/><text x="56" y="278" class="body">{escape(foot)}</text>
<text x="330" y="278" class="small" text-anchor="end">MODE 0{i+1}</text>
</g>''')
    return svg_root(width, 480, "Experience at Salesforce, Tenstorrent, and Microsoft with authentic brand marks", ''.join(body))


def build_selected(mobile: bool = False) -> str:
    width = 600 if mobile else 1200
    entries = [
        ("VISUAL STUDIO CODE", "ArrayQueue correctness", ["Fixed symmetrical boundary errors when consuming", "a queue from both ends.", "Regression tests for interleaved operations."], "PR #301119", vscode_icon, "#F6FBFF", "#30A7E5"),
        ("GOOGLE / GOOGLETEST", "UTF-8 JSON output", ["Preserved UTF-8 bytes across signed- and", "unsigned-character platforms.", "End-to-end regression coverage."], "PR #5082", google_icon, "#FFFFFF", "#64C57A"),
    ]
    body: list[str] = []
    body.append('<text x="36" y="42" class="eyebrow">MERGED MISSIONS / VERIFIED</text>')
    body.append('<text x="34" y="84" class="title">Small fixes. Durable impact.</text>')
    body.append(omnitrix_mark(width-56, 48, 28))
    if mobile:
        for i, (tag, title, lines, pr, icon_fn, inner, glow) in enumerate(entries):
            y = 116 + i * 312
            body.append(f'''<g transform="translate(20 {y})" filter="url(#shadow)">
<rect width="560" height="286" rx="28" fill="url(#glass)" stroke="#D1DFCC"/>
{orb(87, 82, 54, icon_fn(80), inner=inner, glow=glow)}
<rect x="426" y="22" width="110" height="30" rx="15" fill="#E5F6DE" stroke="#C4E4B9"/><text x="481" y="42" class="small" text-anchor="middle">MERGED</text>
<text x="158" y="69" class="eyebrow">{escape(tag)}</text>
<text x="158" y="103" class="prTitle">{escape(title)}</text>
<text x="38" y="159" class="prBody">{escape(lines[0])}</text><text x="38" y="184" class="prBody">{escape(lines[1])}</text><text x="38" y="217" class="body">{escape(lines[2])}</text>
<path d="M38 240H522" stroke="#D8E1D4"/><text x="38" y="269" class="small">{escape(pr)}</text><text x="522" y="269" class="small" text-anchor="end">READ THE CHANGE ↗</text>
</g>''')
        return svg_root(width, 752, "Selected merged work in Visual Studio Code and GoogleTest with authentic marks", ''.join(body))

    for i, (tag, title, lines, pr, icon_fn, inner, glow) in enumerate(entries):
        x = 28 + i * 586
        body.append(f'''<g transform="translate({x} 115)" filter="url(#shadow)">
<rect width="558" height="275" rx="28" fill="url(#glass)" stroke="#D1DFCC"/>
{orb(82, 80, 56, icon_fn(82), inner=inner, glow=glow)}
<rect x="425" y="22" width="110" height="30" rx="15" fill="#E5F6DE" stroke="#C4E4B9"/><text x="480" y="42" class="small" text-anchor="middle">MERGED</text>
<text x="158" y="67" class="eyebrow">{escape(tag)}</text>
<text x="158" y="103" class="prTitle">{escape(title)}</text>
<text x="40" y="157" class="prBody">{escape(lines[0])}</text><text x="40" y="182" class="prBody">{escape(lines[1])}</text><text x="40" y="214" class="body">{escape(lines[2])}</text>
<path d="M40 232H518" stroke="#D8E1D4"/><text x="40" y="259" class="small">{escape(pr)}</text><text x="518" y="259" class="small" text-anchor="end">READ THE CHANGE ↗</text>
</g>''')
    return svg_root(width, 420, "Selected merged work in Visual Studio Code and GoogleTest with authentic marks", ''.join(body))


def tech_icon(kind: str, cx: float, cy: float, size: float) -> str:
    # Icons are intentionally crisp vectors and recognizable brand/product marks.
    if kind == "cpp":
        pts = " ".join(f"{cx + size*.48*dx:.1f},{cy + size*.48*dy:.1f}" for dx,dy in [(0,-1),(.866,-.5),(.866,.5),(0,1),(-.866,.5),(-.866,-.5)])
        return f'<polygon points="{pts}" fill="#00599C"/><text x="{cx}" y="{cy+size*.14}" text-anchor="middle" font-size="{size*.34}" font-weight="800" fill="#FFF">C++</text>'
    if kind == "cs":
        pts = " ".join(f"{cx + size*.48*dx:.1f},{cy + size*.48*dy:.1f}" for dx,dy in [(0,-1),(.866,-.5),(.866,.5),(0,1),(-.866,.5),(-.866,-.5)])
        return f'<polygon points="{pts}" fill="#68217A"/><text x="{cx}" y="{cy+size*.14}" text-anchor="middle" font-size="{size*.38}" font-weight="800" fill="#FFF">C#</text>'
    if kind == "dotnet":
        return f'<circle cx="{cx}" cy="{cy}" r="{size*.48}" fill="#512BD4"/><text x="{cx}" y="{cy+size*.11}" text-anchor="middle" font-size="{size*.28}" font-weight="800" fill="#FFF">.NET</text>'
    if kind == "python":
        s=size/512
        return f'<g transform="translate({cx-size*.44} {cy-size*.5}) scale({s})"><path fill="url(#pythonGradient)" d="{PYTHON_PATH}"/></g>'
    if kind == "ts":
        return f'<rect x="{cx-size*.48}" y="{cy-size*.48}" width="{size*.96}" height="{size*.96}" rx="{size*.10}" fill="#3178C6"/><text x="{cx+size*.04}" y="{cy+size*.21}" text-anchor="middle" font-size="{size*.52}" font-weight="800" fill="#FFF">TS</text>'
    if kind == "pytorch":
        return f'<path d="M{cx+size*.1} {cy-size*.42}A{size*.40} {size*.40} 0 1 0 {cx+size*.34} {cy-size*.12}" fill="none" stroke="#EE4C2C" stroke-width="{size*.12}" stroke-linecap="round"/><circle cx="{cx+size*.22}" cy="{cy-size*.34}" r="{size*.07}" fill="#EE4C2C"/>'
    if kind == "tensorflow":
        return f'<g fill="#FF8F00"><path d="M{cx-size*.44} {cy-size*.32}L{cx} {cy-size*.49}L{cx} {cy+size*.42}L{cx-size*.18} {cy+size*.34}V{cy-size*.10}L{cx-size*.44} {cy}Z"/><path d="M{cx+size*.06} {cy-size*.49}L{cx+size*.44} {cy-size*.32}V{cy}L{cx+size*.18} {cy-size*.10}V{cy+size*.34}L{cx+size*.06} {cy+size*.42}Z"/></g>'
    if kind == "opencv":
        r=size*.24; sw=size*.095
        return f'<g fill="none" stroke-width="{sw}"><circle cx="{cx}" cy="{cy-size*.19}" r="{r}" stroke="#F44336"/><circle cx="{cx-size*.22}" cy="{cy+size*.20}" r="{r}" stroke="#4CAF50"/><circle cx="{cx+size*.22}" cy="{cy+size*.20}" r="{r}" stroke="#2196F3"/></g>'
    if kind == "sklearn":
        return f'<g transform="translate({cx} {cy})"><ellipse cx="{-size*.12}" cy="0" rx="{size*.32}" ry="{size*.18}" transform="rotate(-32)" fill="#F7931E"/><ellipse cx="{size*.18}" cy="0" rx="{size*.30}" ry="{size*.17}" transform="rotate(32)" fill="#29ABE2"/><text x="0" y="{size*.08}" text-anchor="middle" font-size="{size*.19}" font-weight="800" fill="#FFF">sk</text></g>'
    if kind == "azure":
        return f'<path d="M{cx-size*.42} {cy+size*.42}L{cx-size*.05} {cy-size*.47}H{cx+size*.18}L{cx-size*.03} {cy+size*.07}L{cx+size*.47} {cy+size*.42}H{cx+size*.15}L{cx-size*.08} {cy+size*.23}L{cx-size*.17} {cy+size*.42}Z" fill="#0089D6"/>'
    if kind == "docker":
        s=size/640
        return f'<g transform="translate({cx-size*.5} {cy-size*.40}) scale({s})"><path fill="#2496ED" d="{DOCKER_PATH}"/></g>'
    if kind == "git":
        s=size/512
        return f'<g transform="translate({cx-size*.44} {cy-size*.5}) scale({s})"><path fill="#F05032" d="{GIT_PATH}"/></g>'
    if kind == "github":
        s=size/512
        return f'<g transform="translate({cx-size*.47} {cy-size*.5}) scale({s})"><path fill="#181717" d="{GITHUB_PATH}"/></g>'
    if kind == "actions":
        return f'<g fill="none" stroke="#2088FF" stroke-width="{size*.09}" stroke-linecap="round" stroke-linejoin="round"><circle cx="{cx-size*.24}" cy="{cy-size*.22}" r="{size*.10}"/><circle cx="{cx+size*.25}" cy="{cy-size*.14}" r="{size*.10}"/><circle cx="{cx}" cy="{cy+size*.28}" r="{size*.10}"/><path d="M{cx-size*.14} {cy-size*.20}L{cx+size*.15} {cy-size*.15}M{cx+size*.20} {cy-size*.05}L{cx+size*.05} {cy+size*.19}M{cx-size*.18} {cy-size*.13}L{cx-size*.04} {cy+size*.19}"/></g>'
    raise ValueError(kind)


def build_tech(mobile: bool = False) -> str:
    items = [
        ("cpp","C++","SYSTEMS"),("cs","C#","SYSTEMS"),("dotnet",".NET","SYSTEMS"),("python","Python","AI / ML"),("ts","TypeScript","SYSTEMS"),
        ("pytorch","PyTorch","AI / ML"),("tensorflow","TensorFlow","AI / ML"),("opencv","OpenCV","AI / ML"),("sklearn","scikit-learn","AI / ML"),
        ("azure","Azure","BUILDER"),("docker","Docker","BUILDER"),("git","Git","BUILDER"),("github","GitHub","BUILDER"),("actions","Actions","BUILDER"),
    ]
    width = 600 if mobile else 1200
    body: list[str] = []
    body.append('<text x="36" y="42" class="eyebrow">TECH ARSENAL / VECTOR LOADOUT</text>')
    body.append('<text x="34" y="83" class="title">Tools I trust in real systems.</text>')
    body.append('<text x="36" y="109" class="body">Crisp vector marks — no blurred screenshot icons.</text>')
    body.append(omnitrix_mark(width-55, 50, 28))
    if mobile:
        cols=3; tile_w=172; tile_h=132; x0=23; gap=18; y0=142
        for i,(kind,label,group) in enumerate(items):
            x=x0+(i%cols)*(tile_w+gap); y=y0+(i//cols)*(tile_h+16)
            body.append(f'''<g transform="translate({x} {y})" filter="url(#softShadow)"><rect width="{tile_w}" height="{tile_h}" rx="22" fill="url(#glass)" stroke="#D4E0D0"/>{tech_icon(kind,tile_w/2,52,66)}<text x="{tile_w/2}" y="101" class="tileLabel" text-anchor="middle">{escape(label)}</text><text x="{tile_w/2}" y="120" class="tileGroup" text-anchor="middle">{escape(group)}</text></g>''')
        return svg_root(width, 908, "Technology arsenal with crisp vector product and language marks", ''.join(body))
    cols=7; tile_w=148; tile_h=142; gap=18; x0=28; y0=143
    for i,(kind,label,group) in enumerate(items):
        x=x0+(i%cols)*(tile_w+gap); y=y0+(i//cols)*(tile_h+18)
        body.append(f'''<g transform="translate({x} {y})" filter="url(#softShadow)"><rect width="{tile_w}" height="{tile_h}" rx="23" fill="url(#glass)" stroke="#D4E0D0"/>{tech_icon(kind,tile_w/2,56,72)}<text x="{tile_w/2}" y="110" class="tileLabel" text-anchor="middle">{escape(label)}</text><text x="{tile_w/2}" y="130" class="tileGroup" text-anchor="middle">{escape(group)}</text></g>''')
    return svg_root(width, 470, "Technology arsenal with crisp vector product and language marks", ''.join(body))


def main() -> None:
    build_brand_files()
    ASSETS.joinpath("experience-console.svg").write_text(build_experience(False), encoding="utf-8")
    ASSETS.joinpath("experience-console-mobile.svg").write_text(build_experience(True), encoding="utf-8")
    ASSETS.joinpath("selected-work.svg").write_text(build_selected(False), encoding="utf-8")
    ASSETS.joinpath("selected-work-mobile.svg").write_text(build_selected(True), encoding="utf-8")
    ASSETS.joinpath("tech-console.svg").write_text(build_tech(False), encoding="utf-8")
    ASSETS.joinpath("tech-console-mobile.svg").write_text(build_tech(True), encoding="utf-8")
    print("built brand-accurate SVG panels")


if __name__ == "__main__":
    main()
