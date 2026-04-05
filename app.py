#!/usr/bin/env python3
"""
GPU Password Cracker - Modern GUI Application
Professional password cracking demonstration with real-time performance visualization.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import time
from pathlib import Path
from src.cpu_sequential import CPUSequentialCracker
from src.cpu_parallel import CPUParallelCracker
from src.gpu_cuda import GPUCracker
from src.hash_functions import hash_md5
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from collections import deque


class ModernPasswordCrackerGUI:
    """Modern GUI Application for password cracking with real-time metrics."""

    def __init__(self, root):
        self.root = root
        self.root.title("GPU Password Cracker Pro - RTX 3060")
        self.root.geometry("1400x900")
        self.root.resizable(True, True)

        # Modern color scheme
        self.colors = {
            'bg': '#1e1e1e',
            'fg': '#ffffff',
            'accent': '#007acc',
            'success': '#4ec9b0',
            'error': '#f48771',
            'warning': '#dcdcaa'
        }

        # Configure style
        self.setup_styles()

        # Variables
        self.target_hash = tk.StringVar()
        self.hash_algorithm = tk.StringVar(value="md5")
        self.attack_mode = tk.StringVar(value="dictionary")
        self.wordlist_path = tk.StringVar(value="data/wordlists/rockyou.txt")
        self.implementation = tk.StringVar(value="gpu")
        self.num_workers = tk.IntVar(value=8)
        self.charset = tk.StringVar(value="abcdefghijklmnopqrstuvwxyz0123456789")
        self.max_length = tk.IntVar(value=4)
        self.comparison_size = tk.IntVar(value=100000)  # Number of passwords for comparison

        # Performance data
        self.performance_history = {
            'time': deque(maxlen=100),
            'cpu_seq': deque(maxlen=100),
            'cpu_par': deque(maxlen=100),
            'gpu': deque(maxlen=100)
        }
        self.current_metrics = {
            'rate': 0,
            'time': 0,
            'attempts': 0
        }

        # Status
        self.is_running = False
        self.cracker_thread = None
        self.comparison_results = []

        self.create_widgets()
        self.setup_plots()

    def setup_styles(self):
        """Setup modern ttk styles."""
        style = ttk.Style()
        style.theme_use('clam')

        # Configure colors
        style.configure('TFrame', background=self.colors['bg'])
        style.configure('TLabel', background=self.colors['bg'], foreground=self.colors['fg'])
        style.configure('TLabelframe', background=self.colors['bg'], foreground=self.colors['fg'])
        style.configure('TLabelframe.Label', background=self.colors['bg'], foreground=self.colors['accent'],
                       font=('Arial', 11, 'bold'))
        style.configure('TButton', background=self.colors['accent'], foreground=self.colors['fg'])
        style.configure('Accent.TButton', background=self.colors['success'], foreground='black',
                       font=('Arial', 10, 'bold'))
        style.configure('TRadiobutton', background=self.colors['bg'], foreground=self.colors['fg'])
        style.configure('TEntry', fieldbackground='#2d2d2d', foreground=self.colors['fg'])

    def create_widgets(self):
        """Create all GUI widgets with modern design."""
        self.root.configure(bg=self.colors['bg'])

        # Main container with two columns
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left panel (Controls)
        left_panel = ttk.Frame(main_container)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 5))

        # Right panel (Visualization)
        right_panel = ttk.Frame(main_container)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        self.create_left_panel(left_panel)
        self.create_right_panel(right_panel)

    def create_left_panel(self, parent):
        """Create left control panel."""
        # Header
        header = ttk.Frame(parent)
        header.pack(fill=tk.X, pady=(0, 10))

        title = ttk.Label(header, text="🔐 GPU Password Cracker Pro",
                         font=('Arial', 18, 'bold'), foreground=self.colors['accent'])
        title.pack()

        subtitle = ttk.Label(header, text="NVIDIA RTX 3060 • CUDA 12.4 • 3584 Cores",
                            font=('Arial', 9), foreground='#888888')
        subtitle.pack()

        # Target Hash
        hash_frame = ttk.LabelFrame(parent, text="🎯 Target Hash", padding=10)
        hash_frame.pack(fill=tk.X, pady=5)

        ttk.Label(hash_frame, text="Hash:").pack(anchor=tk.W)
        hash_entry = ttk.Entry(hash_frame, textvariable=self.target_hash, font=('Consolas', 10))
        hash_entry.pack(fill=tk.X, pady=5)

        ttk.Label(hash_frame, text="Algorithm:").pack(anchor=tk.W, pady=(5, 0))
        algo_frame = ttk.Frame(hash_frame)
        algo_frame.pack(fill=tk.X)
        ttk.Radiobutton(algo_frame, text="MD5", variable=self.hash_algorithm, value="md5").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(algo_frame, text="SHA-1", variable=self.hash_algorithm, value="sha1").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(algo_frame, text="SHA-256", variable=self.hash_algorithm, value="sha256").pack(side=tk.LEFT)

        # Attack Configuration
        attack_frame = ttk.LabelFrame(parent, text="⚔️ Attack Configuration", padding=10)
        attack_frame.pack(fill=tk.X, pady=5)

        ttk.Radiobutton(attack_frame, text="Dictionary Attack", variable=self.attack_mode,
                       value="dictionary", command=self.update_attack_mode).pack(anchor=tk.W)
        ttk.Radiobutton(attack_frame, text="Brute Force", variable=self.attack_mode,
                       value="brute_force", command=self.update_attack_mode).pack(anchor=tk.W)

        # Dictionary options
        self.dict_frame = ttk.Frame(attack_frame)
        self.dict_frame.pack(fill=tk.X, pady=5)

        ttk.Label(self.dict_frame, text="Wordlist:").pack(anchor=tk.W)
        wordlist_row = ttk.Frame(self.dict_frame)
        wordlist_row.pack(fill=tk.X)
        ttk.Entry(wordlist_row, textvariable=self.wordlist_path, font=('Consolas', 9)).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(wordlist_row, text="Browse", command=self.browse_wordlist, width=8).pack(side=tk.RIGHT)

        # Brute force options
        self.brute_frame = ttk.Frame(attack_frame)

        ttk.Label(self.brute_frame, text="Character Set:").pack(anchor=tk.W)
        ttk.Entry(self.brute_frame, textvariable=self.charset).pack(fill=tk.X, pady=2)

        ttk.Label(self.brute_frame, text="Max Length:").pack(anchor=tk.W, pady=(5, 0))
        ttk.Spinbox(self.brute_frame, from_=1, to=8, textvariable=self.max_length, width=10).pack(anchor=tk.W)

        # Implementation
        impl_frame = ttk.LabelFrame(parent, text="⚡ Implementation", padding=10)
        impl_frame.pack(fill=tk.X, pady=5)

        ttk.Radiobutton(impl_frame, text="🚀 GPU CUDA (Fastest)", variable=self.implementation,
                       value="gpu").pack(anchor=tk.W)
        ttk.Radiobutton(impl_frame, text="💻 CPU Parallel", variable=self.implementation,
                       value="cpu_parallel").pack(anchor=tk.W)
        ttk.Radiobutton(impl_frame, text="🐌 CPU Sequential (Baseline)", variable=self.implementation,
                       value="cpu_sequential").pack(anchor=tk.W)

        worker_frame = ttk.Frame(impl_frame)
        worker_frame.pack(fill=tk.X, pady=5)
        ttk.Label(worker_frame, text="CPU Workers:").pack(side=tk.LEFT)
        ttk.Spinbox(worker_frame, from_=1, to=16, textvariable=self.num_workers, width=8).pack(side=tk.LEFT, padx=5)

        # Control buttons
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=10)

        self.start_button = ttk.Button(button_frame, text="▶ Start Cracking",
                                       command=self.start_cracking, style='Accent.TButton')
        self.start_button.pack(fill=tk.X, pady=2)

        self.stop_button = ttk.Button(button_frame, text="⏹ Stop",
                                      command=self.stop_cracking, state=tk.DISABLED)
        self.stop_button.pack(fill=tk.X, pady=2)

        # Comparison size slider
        comp_frame = ttk.LabelFrame(button_frame, text="⚖️ Comparison Dataset Size", padding=5)
        comp_frame.pack(fill=tk.X, pady=5)

        self.comp_size_label = ttk.Label(comp_frame, text="100,000 passwords",
                                         font=('Arial', 9, 'bold'),
                                         foreground=self.colors['accent'])
        self.comp_size_label.pack()

        comp_slider = tk.Scale(comp_frame, from_=10000, to=14344380,
                              variable=self.comparison_size,
                              orient=tk.HORIZONTAL,
                              resolution=10000,
                              showvalue=0,
                              command=self.update_comparison_label,
                              bg=self.colors['bg'],
                              fg=self.colors['fg'],
                              highlightthickness=0,
                              troughcolor='#2d2d2d',
                              activebackground=self.colors['accent'])
        comp_slider.pack(fill=tk.X, pady=2)

        # Quick preset buttons
        preset_frame = ttk.Frame(comp_frame)
        preset_frame.pack(fill=tk.X)
        ttk.Button(preset_frame, text="10k", width=6,
                  command=lambda: self.comparison_size.set(10000)).pack(side=tk.LEFT, padx=1)
        ttk.Button(preset_frame, text="100k", width=6,
                  command=lambda: self.comparison_size.set(100000)).pack(side=tk.LEFT, padx=1)
        ttk.Button(preset_frame, text="1M", width=6,
                  command=lambda: self.comparison_size.set(1000000)).pack(side=tk.LEFT, padx=1)
        ttk.Button(preset_frame, text="Full", width=6,
                  command=lambda: self.comparison_size.set(14344380)).pack(side=tk.LEFT, padx=1)

        ttk.Button(button_frame, text="🔄 Run Comparison",
                  command=self.run_comparison).pack(fill=tk.X, pady=2)

        ttk.Button(button_frame, text="Clear Output",
                  command=self.clear_output).pack(fill=tk.X, pady=2)

        # Status
        status_frame = ttk.LabelFrame(parent, text="📊 Status", padding=10)
        status_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.status_label = ttk.Label(status_frame, text="Ready", font=('Arial', 11, 'bold'),
                                      foreground=self.colors['success'])
        self.status_label.pack(pady=5)

        # Metrics
        metrics_grid = ttk.Frame(status_frame)
        metrics_grid.pack(fill=tk.X, pady=5)

        self.metric_labels = {}
        metrics = [
            ("⏱️ Time", "time", "0.00s"),
            ("⚡ Rate", "rate", "0 h/s"),
            ("🔢 Attempts", "attempts", "0")
        ]

        for idx, (label, key, default) in enumerate(metrics):
            ttk.Label(metrics_grid, text=label, font=('Arial', 9)).grid(
                row=idx, column=0, sticky=tk.W, pady=2)
            self.metric_labels[key] = ttk.Label(metrics_grid, text=default,
                                               font=('Arial', 10, 'bold'),
                                               foreground=self.colors['accent'])
            self.metric_labels[key].grid(row=idx, column=1, sticky=tk.E, pady=2)

        metrics_grid.columnconfigure(1, weight=1)

        self.update_attack_mode()

    def create_right_panel(self, parent):
        """Create right visualization panel."""
        # Output log
        log_frame = ttk.LabelFrame(parent, text="📝 Output Log", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        self.output_text = scrolledtext.ScrolledText(
            log_frame, height=12, wrap=tk.WORD,
            bg='#1e1e1e', fg=self.colors['fg'],
            font=('Consolas', 9), insertbackground='white'
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)

        # Configure tags
        self.output_text.tag_config("success", foreground=self.colors['success'], font=('Consolas', 10, 'bold'))
        self.output_text.tag_config("error", foreground=self.colors['error'], font=('Consolas', 10, 'bold'))
        self.output_text.tag_config("info", foreground=self.colors['accent'])
        self.output_text.tag_config("warning", foreground=self.colors['warning'])

        # Detailed statistics panel with charts
        stats_frame = ttk.LabelFrame(parent, text="📊 Detailed Performance Analysis", padding=5)
        stats_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        self.stats_container = stats_frame

    def setup_plots(self):
        """Setup matplotlib plots."""
        # Create figure with dark theme
        plt.style.use('dark_background')

        # Detailed analysis figure - 2x2 subplots
        self.detail_fig = Figure(figsize=(10, 7), facecolor='#1e1e1e')
        self.detail_axes = self.detail_fig.subplots(2, 2)

        for ax_row in self.detail_axes:
            for ax in ax_row:
                ax.set_facecolor('#1e1e1e')
                ax.tick_params(colors='white', labelsize=8)
                ax.grid(True, alpha=0.2)

        self.detail_canvas = FigureCanvasTkAgg(self.detail_fig, master=self.stats_container)
        self.detail_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def update_attack_mode(self):
        """Update UI based on attack mode."""
        if self.attack_mode.get() == "dictionary":
            self.dict_frame.pack(fill=tk.X, pady=5)
            self.brute_frame.pack_forget()
        else:
            self.dict_frame.pack_forget()
            self.brute_frame.pack(fill=tk.X, pady=5)

    def update_comparison_label(self, _value=None):
        """Update comparison size label when slider changes."""
        size = self.comparison_size.get()
        if size >= 1000000:
            label = f"{size/1000000:.1f}M passwords"
        elif size >= 1000:
            label = f"{size/1000:.0f}k passwords"
        else:
            label = f"{size:,} passwords"
        self.comp_size_label.config(text=label)

    def browse_wordlist(self):
        """Browse for wordlist file."""
        filename = filedialog.askopenfilename(
            title="Select Wordlist",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialdir="data/wordlists"
        )
        if filename:
            self.wordlist_path.set(filename)

    def log(self, message, tag="info"):
        """Log message to output."""
        self.output_text.insert(tk.END, message + "\n", tag)
        self.output_text.see(tk.END)

    def clear_output(self):
        """Clear output log."""
        self.output_text.delete(1.0, tk.END)

    def update_metrics(self, time_elapsed, rate, attempts):
        """Update metric displays."""
        self.metric_labels['time'].config(text=f"{time_elapsed:.2f}s")
        self.metric_labels['rate'].config(text=f"{rate:,.0f} h/s")
        self.metric_labels['attempts'].config(text=f"{attempts:,}")

    def start_cracking(self):
        """Start cracking."""
        target = self.target_hash.get().strip()
        if not target:
            messagebox.showerror("Error", "Please enter a target hash")
            return

        if self.attack_mode.get() == "dictionary":
            if not Path(self.wordlist_path.get()).exists():
                messagebox.showerror("Error", "Wordlist not found")
                return

        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        self.cracker_thread = threading.Thread(target=self.run_cracking, daemon=True)
        self.cracker_thread.start()

    def stop_cracking(self):
        """Stop cracking."""
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="Stopped", foreground=self.colors['warning'])
        self.log("⚠️ Stopped by user", "warning")

    def run_cracking(self):
        """Run cracking operation."""
        try:
            target_hash = self.target_hash.get().strip()
            impl = self.implementation.get()
            algo = self.hash_algorithm.get()

            self.log("="*60, "info")
            self.log(f"🚀 Starting {self.attack_mode.get()} attack", "info")
            self.log(f"🎯 Target: {target_hash}", "info")
            self.log(f"🔐 Algorithm: {algo.upper()}", "info")
            self.log(f"⚡ Mode: {impl.upper()}", "info")
            self.log("="*60, "info")

            # Initialize
            self.status_label.config(text="Initializing...", foreground=self.colors['accent'])

            if impl == "gpu":
                if algo != "md5":
                    messagebox.showwarning("Limited Support",
                        f"GPU implementation currently only supports MD5.\nFalling back to CPU for {algo.upper()}.")
                    cracker = CPUParallelCracker(hash_algorithm=algo, num_workers=8)
                else:
                    cracker = GPUCracker(hash_algorithm=algo, batch_size=100000)
            elif impl == "cpu_parallel":
                cracker = CPUParallelCracker(hash_algorithm=algo, num_workers=self.num_workers.get())
            else:
                cracker = CPUSequentialCracker(hash_algorithm=algo)

            # Run attack
            self.status_label.config(text="Cracking...", foreground=self.colors['warning'])

            if self.attack_mode.get() == "dictionary":
                self.log(f"📚 Loading wordlist...", "info")
                with open(self.wordlist_path.get(), 'r', encoding='latin-1', errors='ignore') as f:
                    wordlist = []
                    for line in f:
                        # Filter out non-printable control characters
                        pwd = ''.join(c for c in line if c.isprintable()).strip()
                        if pwd:
                            # Try to fix UTF-8 encoded characters that were read as latin-1
                            try:
                                pwd = pwd.encode('latin-1').decode('utf-8')
                            except (UnicodeDecodeError, UnicodeEncodeError):
                                pass  # Keep original if conversion fails
                            wordlist.append(pwd)
                self.log(f"📚 Loaded {len(wordlist):,} passwords", "info")

                found, stats = cracker.dictionary_attack(target_hash, wordlist)
            else:
                found, stats = cracker.brute_force(target_hash, self.charset.get(), self.max_length.get())

            # Results
            if found:
                self.log("="*60, "success")
                self.log(f"✅ PASSWORD FOUND: {found}", "success")
                self.log("="*60, "success")
                messagebox.showinfo("Success!", f"Password cracked: {found}")
                self.status_label.config(text="Success!", foreground=self.colors['success'])
            else:
                self.log("="*60, "error")
                self.log("❌ Password not found", "error")
                self.log("="*60, "error")
                self.status_label.config(text="Not Found", foreground=self.colors['error'])

            self.log(f"\n📊 Statistics:", "info")
            self.log(f"  ⏱️  Time: {stats['time']:.4f}s", "info")
            self.log(f"  🔢 Attempts: {stats['attempts']:,}", "info")
            self.log(f"  ⚡ Rate: {stats['rate']:,.0f} h/s", "info")

            self.update_metrics(stats['time'], stats['rate'], stats['attempts'])

        except Exception as e:
            self.log(f"❌ Error: {str(e)}", "error")
            messagebox.showerror("Error", str(e))
        finally:
            self.is_running = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

    def run_comparison(self):
        """Run performance comparison."""
        target = self.target_hash.get().strip()
        if not target:
            messagebox.showerror("Error", "Please enter a target hash")
            return

        self.log("\n" + "="*60, "info")
        self.log("🏁 Running Performance Comparison", "info")
        self.log("="*60, "info")

        threading.Thread(target=self._comparison_thread, args=(target,), daemon=True).start()

    def _comparison_thread(self, target_hash):
        """Run comparison in thread."""
        try:
            algo = self.hash_algorithm.get()

            # Load wordlist
            if self.attack_mode.get() == "dictionary":
                with open(self.wordlist_path.get(), 'r', encoding='latin-1', errors='ignore') as f:
                    wordlist = []
                    for line in f:
                        # Filter out non-printable control characters
                        pwd = ''.join(c for c in line if c.isprintable()).strip()
                        if pwd:
                            # Try to fix UTF-8 encoded characters that were read as latin-1
                            try:
                                pwd = pwd.encode('latin-1').decode('utf-8')
                            except (UnicodeDecodeError, UnicodeEncodeError):
                                pass  # Keep original if conversion fails
                            wordlist.append(pwd)
                    # Use slider value for comparison size
                    comparison_size = self.comparison_size.get()
                    wordlist = wordlist[:comparison_size]
                self.log(f"📚 Using {len(wordlist):,} passwords for comparison", "info")
            else:
                wordlist = None

            result = {'implementations': {}, 'algorithm': algo}

            # CPU Sequential
            self.log(f"\n🐌 Testing CPU Sequential ({algo.upper()})...", "info")
            cracker = CPUSequentialCracker(hash_algorithm=algo)
            if wordlist:
                _, stats = cracker.dictionary_attack(target_hash, wordlist)
            else:
                _, stats = cracker.brute_force(target_hash, self.charset.get(), self.max_length.get())
            result['implementations']['CPU Sequential'] = stats
            self.log(f"  ⏱️  {stats['time']:.4f}s | ⚡ {stats['rate']:,.0f} h/s", "info")

            # CPU Parallel
            self.log(f"\n💻 Testing CPU Parallel ({algo.upper()})...", "info")
            cracker = CPUParallelCracker(hash_algorithm=algo, num_workers=8)
            if wordlist:
                _, stats = cracker.dictionary_attack(target_hash, wordlist)
            else:
                _, stats = cracker.brute_force(target_hash, self.charset.get(), self.max_length.get())
            result['implementations']['CPU Parallel'] = stats
            self.log(f"  ⏱️  {stats['time']:.4f}s | ⚡ {stats['rate']:,.0f} h/s", "info")

            # GPU (only for MD5)
            if algo == "md5":
                self.log(f"\n🚀 Testing GPU CUDA ({algo.upper()})...", "info")
                cracker = GPUCracker(hash_algorithm=algo, batch_size=100000)
                if wordlist:
                    _, stats = cracker.dictionary_attack(target_hash, wordlist)
                else:
                    _, stats = cracker.brute_force(target_hash, self.charset.get(), self.max_length.get())
                result['implementations']['GPU CUDA'] = stats
                self.log(f"  ⏱️  {stats['time']:.4f}s | ⚡ {stats['rate']:,.0f} h/s", "info")

                # Note about GPU performance characteristics
                if wordlist and len(wordlist) < 50000:
                    self.log(f"  ℹ️  Note: GPU has startup overhead. Advantage increases with larger datasets.", "info")
            else:
                self.log(f"\n⚠️  GPU CUDA: Not supported for {algo.upper()} (MD5 only)", "warning")

            # Calculate speedup
            cpu_time = result['implementations']['CPU Sequential']['time']

            if 'GPU CUDA' in result['implementations']:
                gpu_time = result['implementations']['GPU CUDA']['time']
                speedup = cpu_time / gpu_time

                self.log("\n" + "="*60, "success")
                self.log(f"🏆 GPU SPEEDUP: {speedup:.2f}x FASTER", "success")
                self.log("="*60, "success")
            else:
                cpu_par_time = result['implementations']['CPU Parallel']['time']
                speedup = cpu_time / cpu_par_time

                self.log("\n" + "="*60, "info")
                self.log(f"💻 CPU Parallel Speedup: {speedup:.2f}x vs Sequential", "info")
                self.log("="*60, "info")

            self.comparison_results.append(result)
            self.update_detailed_stats(result)

        except Exception as e:
            self.log(f"❌ Comparison error: {str(e)}", "error")

    def update_detailed_stats(self, result):
        """Update the detailed statistics panel with 4-panel analysis charts."""
        # Clear all subplots
        for ax_row in self.detail_axes:
            for ax in ax_row:
                ax.clear()
                ax.set_facecolor('#1e1e1e')
                ax.tick_params(colors='white', labelsize=8)
                ax.grid(True, alpha=0.2, axis='y')

        # Get implementations in order
        impl_order = ['CPU Sequential', 'CPU Parallel', 'GPU CUDA']
        implementations = {k: result['implementations'][k] for k in impl_order if k in result['implementations']}
        impl_names = list(implementations.keys())

        times = [implementations[name]['time'] for name in impl_names]
        rates = [implementations[name]['rate'] for name in impl_names]

        colors = ['#f48771', '#dcdcaa', '#4ec9b0'][:len(impl_names)]

        # Chart 1: Execution Time Comparison (top-left)
        ax1 = self.detail_axes[0, 0]
        bars1 = ax1.bar(impl_names, times, color=colors, alpha=0.8, edgecolor='white', linewidth=1.5)
        for bar, time in zip(bars1, times):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{time:.3f}s', ha='center', va='bottom', color='white', fontsize=9, fontweight='bold')
        ax1.set_ylabel('Time (seconds)', color='white', fontsize=9, fontweight='bold')
        ax1.set_title('Execution Time by Implementation', color='white', fontsize=10, fontweight='bold')
        ax1.set_xticklabels(impl_names, rotation=15, ha='right', fontsize=8)

        # Chart 2: Hash Rate Comparison (top-right)
        ax2 = self.detail_axes[0, 1]
        bars2 = ax2.bar(impl_names, rates, color=colors, alpha=0.8, edgecolor='white', linewidth=1.5)
        for bar, rate in zip(bars2, rates):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{rate/1e6:.2f}M', ha='center', va='bottom', color='white', fontsize=9, fontweight='bold')
        ax2.set_ylabel('Hash Rate (hashes/sec)', color='white', fontsize=9, fontweight='bold')
        ax2.set_title('Hash Rate Comparison', color='white', fontsize=10, fontweight='bold')
        ax2.set_xticklabels(impl_names, rotation=15, ha='right', fontsize=8)
        ax2.ticklabel_format(axis='y', style='scientific', scilimits=(0,0))

        # Chart 3: Speedup vs CPU Sequential (bottom-left)
        ax3 = self.detail_axes[1, 0]
        if 'CPU Sequential' in implementations:
            baseline_time = implementations['CPU Sequential']['time']
            speedups = [baseline_time / implementations[name]['time'] for name in impl_names]

            bars3 = ax3.bar(impl_names, speedups, color=colors, alpha=0.8, edgecolor='white', linewidth=1.5)
            for bar, speedup in zip(bars3, speedups):
                height = bar.get_height()
                ax3.text(bar.get_x() + bar.get_width()/2., height,
                        f'{speedup:.2f}x', ha='center', va='bottom', color='white', fontsize=9, fontweight='bold')

            ax3.axhline(y=1, color='red', linestyle='--', alpha=0.5, linewidth=1.5, label='Baseline')
            ax3.set_ylabel('Speedup (x times faster)', color='white', fontsize=9, fontweight='bold')
            ax3.set_title('Speedup vs CPU Sequential', color='white', fontsize=10, fontweight='bold')
            ax3.set_xticklabels(impl_names, rotation=15, ha='right', fontsize=8)
            ax3.legend(loc='upper left', fontsize=8)

        # Chart 4: Detailed Statistics Table (bottom-right)
        ax4 = self.detail_axes[1, 1]
        ax4.axis('off')  # Hide axes for table

        # Create table data
        table_data = []
        table_data.append(['Implementation', 'Time (s)', 'Rate (M h/s)', 'Speedup'])

        if 'CPU Sequential' in implementations:
            baseline_time = implementations['CPU Sequential']['time']
            for name in impl_names:
                stats = implementations[name]
                speedup = baseline_time / stats['time']
                table_data.append([
                    name.replace(' ', '\n'),
                    f"{stats['time']:.3f}",
                    f"{stats['rate']/1e6:.2f}",
                    f"{speedup:.2f}x"
                ])

        # Create table
        table = ax4.table(cellText=table_data, cellLoc='center', loc='center',
                         colWidths=[0.35, 0.2, 0.25, 0.2])
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1, 2)

        # Style table
        for i, cell in enumerate(table.get_celld().values()):
            if i < len(impl_names) + 1:  # Header row
                cell.set_facecolor('#2d2d2d')
                cell.set_text_props(weight='bold', color='white')
            else:
                cell.set_facecolor('#1e1e1e')
                cell.set_text_props(color='white')
            cell.set_edgecolor('white')

        # Add title
        ax4.text(0.5, 0.95, 'Performance Summary', ha='center', va='top',
                transform=ax4.transAxes, color='white', fontsize=10, fontweight='bold')

        self.detail_fig.tight_layout()
        self.detail_canvas.draw()


def main():
    """Main entry point."""
    root = tk.Tk()
    app = ModernPasswordCrackerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
