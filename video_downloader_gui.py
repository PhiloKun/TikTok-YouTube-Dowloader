#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import yt_dlp
import platform
import json
import traceback
import webbrowser # Import webbrowser module

def create_download_directory(directory):
    """创建下载目录"""
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory

def detect_platform(url):
    """检测URL所属的平台"""
    if "tiktok.com" in url:
        return "tiktok"
    elif "youtube.com" in url or "youtu.be" in url:
        return "youtube"
    else:
        return None

class VideoDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("视频下载器 - TikTok & YouTube")
        self.root.geometry("600x450") 
        self.root.resizable(False, False)
        
        # --- Set Window Icon (Optional) ---
        # Uncomment the line below and replace 'icon.ico' with the path to your icon file (Windows only)
        # try:
        #     self.root.iconbitmap('icon.ico') 
        # except tk.TclError:
        #     print("提示: 未找到icon.ico文件，将使用默认图标。")
        # For cross-platform PNG icons (requires Pillow potentially):
        # try:
        #     icon_image = tk.PhotoImage(file='icon.png') # Replace with your PNG path
        #     self.root.iconphoto(True, icon_image)
        # except Exception as e:
        #     print(f"提示: 加载图标失败 - {e}")
            

        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, relief="flat", background="#3498db")
        self.style.configure("TLabel", padding=6)
        self.style.configure("TEntry", padding=6)
        
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # --- UI Elements (Row numbers adjusted) ---
        # Row 0: URL Label
        ttk.Label(self.main_frame, text="请输入视频URL:").grid(column=0, row=0, sticky=tk.W, pady=2)
        # Row 1: URL Entry
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(self.main_frame, width=50, textvariable=self.url_var)
        self.url_entry.grid(column=0, row=1, sticky=(tk.W, tk.E), pady=2, padx=5)
        # Row 2: Platform Label
        self.platform_var = tk.StringVar(value="等待URL...")
        self.platform_label = ttk.Label(self.main_frame, textvariable=self.platform_var)
        self.platform_label.grid(column=0, row=2, sticky=tk.W, pady=2)
        self.url_entry.bind("<KeyRelease>", self.on_url_change)
        # Row 3: Output Dir Label
        ttk.Label(self.main_frame, text="下载目录:").grid(column=0, row=3, sticky=tk.W, pady=2)
        # Row 4: Output Dir Entry + Browse Button
        self.dir_frame = ttk.Frame(self.main_frame)
        self.dir_frame.grid(column=0, row=4, sticky=(tk.W, tk.E), pady=2)
        self.dir_var = tk.StringVar(value=os.path.join(os.getcwd(), "downloads"))
        self.dir_entry = ttk.Entry(self.dir_frame, width=40, textvariable=self.dir_var)
        self.dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        # Add folder icon to Browse button text
        self.browse_btn = ttk.Button(self.dir_frame, text="浏览... 📂", command=self.browse_directory)
        self.browse_btn.pack(side=tk.RIGHT, padx=5)
        
        # Row 5: Download Button (Moved up)
        # Add download icon to Download button text
        self.download_btn = ttk.Button(self.main_frame, text="⬇️ 下载视频", command=self.start_download)
        self.download_btn.grid(column=0, row=5, sticky=(tk.W, tk.E), pady=10, padx=5)
        # Row 6: Progress Bar (Moved up)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(column=0, row=6, sticky=(tk.W, tk.E), pady=5, padx=5)
        # Row 7: Status Label (Moved up)
        self.status_var = tk.StringVar(value="等待下载...")
        self.status_label = ttk.Label(self.main_frame, textvariable=self.status_var, anchor=tk.W)
        self.status_label.grid(column=0, row=7, sticky=(tk.W, tk.E), pady=5)
        
        # Row 8: Separator (Optional, for better visual separation)
        separator = ttk.Separator(self.main_frame, orient='horizontal')
        separator.grid(column=0, row=8, sticky='ew', pady=10)

        # Row 9: Author Info using Text widget for clickable links
        default_bg = root.cget('bg') 
        # Revert to word wrapping and height 2 to ensure full text visibility
        self.author_text = tk.Text(self.main_frame, height=2, borderwidth=0, 
                                   relief="flat", background=default_bg, 
                                   wrap="word", font=("Segoe UI", 9), cursor="arrow") # Set wrap back to "word"
        self.author_text.grid(column=0, row=9, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Insert text segments and apply tags - Re-verified inclusion of website
        self.author_text.insert(tk.END, "作者：PhiloKun  |  GItHub: ")
        github_url = "https://github.com/PhiloKun"
        self.author_text.insert(tk.END, github_url, ("link_github",))
        self.author_text.insert(tk.END, "  | 作者网站: ")
        website_url = "http://www.zhangkunzhe.cn" # Ensure http:// or https://
        # Ensure website URL is inserted with the correct tag
        self.author_text.insert(tk.END, website_url, ("link_website",)) 

        # Configure link tags
        self.author_text.tag_configure("link_github", foreground="blue", underline=True)
        self.author_text.tag_configure("link_website", foreground="blue", underline=True)

        # Bind events to tags - Re-verified bindings for website
        self.author_text.tag_bind("link_github", "<Enter>", self._show_hand_cursor)
        self.author_text.tag_bind("link_github", "<Leave>", self._show_arrow_cursor)
        self.author_text.tag_bind("link_github", "<Button-1>", lambda e: self._open_url(github_url))
        
        self.author_text.tag_bind("link_website", "<Enter>", self._show_hand_cursor)
        self.author_text.tag_bind("link_website", "<Leave>", self._show_arrow_cursor)
        self.author_text.tag_bind("link_website", "<Button-1>", lambda e: self._open_url(website_url))

        # Make the Text widget read-only
        self.author_text.config(state=tk.DISABLED)
        
        # Adjust padding for all elements
        for child in self.main_frame.winfo_children():
             child.grid_configure(padx=5)
             
        # Configure the main frame's column to expand horizontally
        self.main_frame.columnconfigure(0, weight=1)

    def on_url_change(self, event):
        """当URL输入改变时，尝试识别平台"""
        url = self.url_var.get().strip()
        if url:
            platform = detect_platform(url)
            if platform == "tiktok":
                self.platform_var.set("平台: TikTok")
            elif platform == "youtube":
                self.platform_var.set("平台: YouTube")
            else:
                self.platform_var.set("平台: 未知 (仅支持TikTok和YouTube)")
        else:
            self.platform_var.set("等待URL...")
    
    def browse_directory(self):
        """浏览文件夹对话框"""
        directory = filedialog.askdirectory(initialdir=self.dir_var.get())
        if directory:
            self.dir_var.set(directory)
    
    def update_progress(self, percentage, status):
        """更新进度条和状态"""
        self.progress_var.set(percentage)
        self.status_var.set(status)
        self.root.update_idletasks()  # 强制更新UI
    
    def download_complete(self, success, filename=None):
        """下载完成时的回调"""
        if success and filename:
            abs_filename = os.path.abspath(filename)
            self.update_progress(100, f"下载完成: {os.path.basename(abs_filename)}")
            messagebox.showinfo("下载完成", f"视频已成功下载到:\n{abs_filename}")
        else:
            error_message = self.status_var.get()
            if not error_message or "下载失败" in error_message or "等待下载" in error_message:
                 error_message = "无法下载视频，请检查URL和网络连接" 
            self.update_progress(0, "下载失败")
            messagebox.showerror("下载失败", error_message)
        
        self.download_btn.config(state=tk.NORMAL)

    def _open_url(self, url):
        try:
            webbrowser.open_new_tab(url)
        except Exception as e:
            print(f"无法打开URL {url}: {e}")
            messagebox.showerror("链接错误", f"无法在浏览器中打开链接:\n{url}")

    def _show_hand_cursor(self, event):
        self.author_text.config(cursor="hand2")

    def _show_arrow_cursor(self, event):
        self.author_text.config(cursor="arrow")

    def download_tiktok(self, url, output_dir):
        """下载TikTok视频（无水印）"""
        ydl_opts = {
            'format': 'best[ext=mp4]/best', 
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
            },
            'extractor_args': {
                'tiktok': {
                    'prefer_no_watermark': True, 
                    'embed_metadata': True,
                    'add_metadata': True,
                }
            },
             'postprocessors': [], 
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.update_progress(10, "获取视频信息...")
                info = ydl.extract_info(url, download=False)
                filename_template = ydl.prepare_filename(info) 
                
                self.update_progress(20, f"开始下载: {info.get('title', 'Unknown Title')}")
                
                def progress_hook(d):
                    if not isinstance(d, dict):
                        return

                    status = d.get('status') 
                    if status == 'downloading':
                        total_bytes_estimate = d.get('total_bytes') or d.get('total_bytes_estimate')
                        downloaded_bytes = d.get('downloaded_bytes')

                        if total_bytes_estimate and downloaded_bytes is not None:
                            percent = (downloaded_bytes / total_bytes_estimate) * 100
                            scaled_percent = min(20 + percent * 0.75, 95) # Keep scaling for progress bar
                            # Get formatted percentage string from yt-dlp, default to calculated one
                            percent_str = d.get('_percent_str', f'{percent:.1f}%').strip()
                            # Update status label to primarily show percentage
                            status_display = f"下载中: {percent_str}"
                            # Optionally add speed/ETA back if needed, but keep it concise
                            # speed_str = d.get('_speed_str')
                            # if speed_str:
                            #    status_display += f" @ {speed_str}"
                            self.update_progress(scaled_percent, status_display)
                        elif downloaded_bytes is not None:
                            self.update_progress(min(self.progress_var.get() + 0.5, 95), "下载中 (无进度信息)..." )
                    elif status == 'finished':
                        self.update_progress(95, "下载完成，正在处理...")
                    elif status == 'error':
                         err_msg = d.get('fragment_error') or d.get('msg', '未知错误')
                         self.update_progress(0, f"下载错误: {err_msg}")


                ydl_opts['progress_hooks'] = [progress_hook]
                ydl.download([url])

                final_filename = filename_template 
                if os.path.exists(final_filename):
                    self.download_complete(True, final_filename)
                    return True
                else:
                    try:
                         dir_files = [f for f in os.listdir(output_dir) if os.path.isfile(os.path.join(output_dir, f)) and f.lower().endswith('.mp4')]
                         if dir_files:
                              dir_files.sort(key=lambda x: os.path.getmtime(os.path.join(output_dir, x)), reverse=True)
                              potential_file = os.path.join(output_dir, dir_files[0])
                              if os.path.exists(potential_file):
                                   self.download_complete(True, potential_file)
                                   return True
                    except Exception:
                         pass
                    self.status_var.set(f"下载失败: 无法找到文件 {os.path.basename(final_filename)}")
                    self.download_complete(False)
                    return False
        except Exception as e:
            print("--- TRACEBACK START ---")
            traceback.print_exc()
            print("--- TRACEBACK END ---")
            error_msg = f"意外错误 (详情请查看控制台): {type(e).__name__}"
            self.update_progress(0, error_msg)
            self.download_complete(False)
            return False

    def download_youtube(self, url, output_dir):
        """下载YouTube视频, 强制下载预合并格式"""

        # Format selector prioritizing pre-merged files (video + audio)
        # Excludes video-only or audio-only streams. Might result in lower quality if high-res pre-merged isn't available.
        format_option = 'best[vcodec!=none][acodec!=none][ext=mp4]/best[vcodec!=none][acodec!=none]/best'
        
        ydl_opts = {
            'format': format_option,
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': False, 
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
            },
            'postprocessors': [], 
            'ignoreerrors': True, 
            'abort_on_error': False, 
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.update_progress(10, "获取视频信息...")
                info = ydl.extract_info(url, download=False)
                filename_template = ydl.prepare_filename(info)

                self.update_progress(20, f"开始下载: {info.get('title', 'Unknown Title')}")

                def progress_hook(d):
                    if not isinstance(d, dict):
                        return
                    
                    status = d.get('status') 
                    if status == 'downloading':
                        total_bytes_estimate = d.get('total_bytes') or d.get('total_bytes_estimate')
                        downloaded_bytes = d.get('downloaded_bytes')

                        if total_bytes_estimate and downloaded_bytes is not None:
                            percent = (downloaded_bytes / total_bytes_estimate) * 100
                            scaled_percent = min(20 + percent * 0.75, 95) # Keep scaling for progress bar
                            # Get formatted percentage string from yt-dlp, default to calculated one
                            percent_str = d.get('_percent_str', f'{percent:.1f}%').strip()
                            # Update status label to primarily show percentage
                            status_display = f"下载中: {percent_str}"
                            # Optionally add speed/ETA back if needed, but keep it concise
                            # speed_str = d.get('_speed_str')
                            # if speed_str:
                            #    status_display += f" @ {speed_str}"
                            self.update_progress(scaled_percent, status_display)
                        elif downloaded_bytes is not None:
                            self.update_progress(min(self.progress_var.get() + 0.5, 95), "下载中 (无进度信息)...")
                    elif status == 'finished':
                         self.update_progress(95, "下载完成，正在处理...")
                    elif status == 'error':
                         err_msg = d.get('fragment_error') or d.get('msg', '未知下载错误')
                         self.update_progress(0, f"下载错误: {err_msg}")

                ydl_opts['progress_hooks'] = [progress_hook]

                ydl.download([url])

                final_filename = filename_template 
                if os.path.exists(final_filename):
                    self.download_complete(True, final_filename)
                    return True
                else:
                    try:
                         dir_files = [f for f in os.listdir(output_dir) if os.path.isfile(os.path.join(output_dir, f)) and (f.lower().endswith('.mp4') or f.lower().endswith('.mkv') or f.lower().endswith('.webm'))]
                         if dir_files:
                              dir_files.sort(key=lambda x: os.path.getmtime(os.path.join(output_dir, x)), reverse=True)
                              potential_file = os.path.join(output_dir, dir_files[0])
                              if os.path.exists(potential_file):
                                   self.download_complete(True, potential_file)
                                   return True
                    except Exception:
                         pass
                    self.status_var.set(f"下载失败: 无法找到文件 {os.path.basename(final_filename)}")
                    self.download_complete(False)
                    return False

        except yt_dlp.utils.DownloadError as e:
            print("--- TRACEBACK START (DownloadError) ---")
            traceback.print_exc()
            print("--- TRACEBACK END ---")
            error_message = str(e)
            if "requested format is not available" in error_message.lower():
                 final_error = "错误: 请求的最佳视频/音频格式不可用。"
            else:
                 final_error = f"下载错误 (详情请查看控制台): {error_message}"
            self.update_progress(0, final_error)
            self.download_complete(False)
            return False
        except Exception as e:
            print("--- TRACEBACK START (General Exception) ---")
            traceback.print_exc()
            print("--- TRACEBACK END ---")
            error_msg = f"意外错误 (详情请查看控制台): {type(e).__name__}"
            self.update_progress(0, error_msg)
            self.download_complete(False)
            return False

    def start_download(self):
        """开始下载流程"""
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("错误", "请输入有效的视频URL")
            return

        platform_detected = detect_platform(url)
        if not platform_detected:
            messagebox.showerror("不支持的URL", "仅支持TikTok和YouTube视频")
            return

        output_dir = self.dir_var.get()
        try:
            create_download_directory(output_dir)
        except Exception as e:
            messagebox.showerror("错误", f"无法创建下载目录: {str(e)}")
            return

        self.download_btn.config(state=tk.DISABLED)
        self.progress_var.set(0)
        self.status_var.set("准备下载...")

        if platform_detected == "tiktok":
            thread = threading.Thread(target=self.download_tiktok, args=(url, output_dir), daemon=True)
        elif platform_detected == "youtube":
            thread = threading.Thread(target=self.download_youtube, args=(url, output_dir), daemon=True)
        
        thread.start()


if __name__ == "__main__":
    root = tk.Tk()
    app = VideoDownloaderApp(root)
    root.mainloop() 