@echo off
REM 画像用自動モザイクスクリプト
python mosaic-image.py
if exist mosaic-auto.bat del mosaic-auto.bat
