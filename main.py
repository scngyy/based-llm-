"""
主程序 - PDF预处理页面
选择PDF文件并调用utils中的处理函数
"""

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import threading
from utils.pdf_processor import process_pdf_file

class PDFProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF预处理器")
        self.root.geometry("800x600")
        self.create_widgets()
    
    def create_widgets(self):
        # 标题
        tk.Label(self.root, text="PDF预处理器", font=("Arial", 16, "bold")).pack(pady=10)
        
        # 文件选择
        file_frame = tk.Frame(self.root)
        file_frame.pack(pady=10, padx=20, fill="x")
        
        tk.Label(file_frame, text="选择PDF文件:").pack(side="left")
        
        self.file_path_var = tk.StringVar()
        tk.Entry(file_frame, textvariable=self.file_path_var, width=50).pack(side="left", padx=10, fill="x", expand=True)
        
        tk.Button(file_frame, text="浏览", command=self.browse_file).pack(side="left")
        
        # 处理按钮
        tk.Button(self.root, text="开始处理", command=self.process_pdf, 
                 bg="#4CAF50", fg="white", font=("Arial", 12)).pack(pady=20)
        
        # 结果显示
        tk.Label(self.root, text="处理结果:", font=("Arial", 12, "bold")).pack(pady=10)
        
        self.result_text = scrolledtext.ScrolledText(self.root, height=15, width=80)
        self.result_text.pack(pady=10, padx=20, fill="both", expand=True)
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        tk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W).pack(side="bottom", fill="x")
    
    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="选择PDF文件",
            filetypes=[("PDF文件", "*.pdf"), ("所有文件", "*.*")]
        )
        if file_path:
            self.file_path_var.set(file_path)
    
    def process_pdf(self):
        file_path = self.file_path_var.get()
        if not file_path:
            messagebox.showerror("错误", "请选择PDF文件")
            return
        
        if not file_path.endswith('.pdf'):
            messagebox.showerror("错误", "请选择PDF文件")
            return
        
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "正在处理PDF文件，请稍候...\n\n")
        self.status_var.set("处理中...")
        self.root.update()
        
        thread = threading.Thread(target=self._process_thread, args=(file_path,))
        thread.daemon = True
        thread.start()
    
    def _process_thread(self, file_path):
        try:
            result = process_pdf_file(file_path)
            self.root.after(0, self._update_result, result)
        except Exception as e:
            error_result = {"success": False, "message": f"处理异常: {str(e)}"}
            self.root.after(0, self._update_result, error_result)
    
    def _update_result(self, result):
        self.result_text.delete(1.0, tk.END)
        
        if result["success"]:
            data = result["data"]
            self.result_text.insert(tk.END, "✅ 处理成功！\n\n")
            self.result_text.insert(tk.END, f"📝 消息: {result['message']}\n\n")
            
            self.result_text.insert(tk.END, "📊 处理统计:\n")
            self.result_text.insert(tk.END, f"   - Markdown长度: {len(data.get('markdown_content', ''))} 字符\n")
            self.result_text.insert(tk.END, f"   - 分块数量: {len(data.get('chunks', []))} 个\n")
            self.result_text.insert(tk.END, f"   - Prompt数量: {len(data.get('prompts', []))} 个\n")
            self.result_text.insert(tk.END, f"   - 处理时间: {data.get('processing_time', 0):.2f} 秒\n\n")
            
            if data.get('pdf_url'):
                self.result_text.insert(tk.END, f"🌐 PDF URL: {data['pdf_url']}\n\n")
            
            self.status_var.set("处理完成")
        else:
            self.result_text.insert(tk.END, "❌ 处理失败！\n\n")
            self.result_text.insert(tk.END, f"📝 错误信息: {result['message']}\n")
            self.status_var.set("处理失败")
        
        self.result_text.see(tk.END)

def main():
    root = tk.Tk()
    app = PDFProcessorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()