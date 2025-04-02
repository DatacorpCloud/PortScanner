"""
Port Scanner Application

Author: [Alessio Orpellini]
Mail: [alessio.orpellini@gmail.com]

This script creates a graphical application for scanning the ports of multiple hosts. Users can select a file containing hosts and ports to be scanned. The application uses the `tkinter` library to create a simple graphical interface, allowing the user to select a file, start the port scan, and view the results.

Functionality:
1. The user selects a text file containing a list of hosts and their corresponding ports to scan.
2. Each line in the file should be in the format: `host,port,port,port,...`.
3. The application starts scanning the ports for each host in parallel using threads.
4. The scan results (success or failure for each port) are displayed in the interface and saved to a log file.

Requirements:
- Python 3.x
- Modules: os, sys, socket, threading, queue, tkinter, concurrent.futures

Detailed Operation:
- The `check_port` function attempts to connect to a specific port on a host and returns `True` if the connection succeeds, otherwise `False`.
- The graphical interface (`tkinter`) allows the user to select the host file and start the scan.
- The port scanning is handled using threading to allow parallel execution and improve performance.
- A progress bar shows the status of the scan, and the results are displayed in real-time in the text box.
- At the end of the scan, a log file is created with the results of all the connection tests.
"""


import os
import sys
import socket
import threading
import queue
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import concurrent.futures

def check_port(host, port, timeout=3):
    """Prova a connettersi a host e porta; ritorna True se raggiungibile."""
    try:
        port = int(port)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            return result == 0
    except Exception:
        return False

class PortScannerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Port Scanner")
        self.geometry("600x400")
        self.resizable(False, False)  # Dimensione fissa

        # Configura la griglia
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Frame per la selezione del file (riga 0)
        file_frame = tk.Frame(self)
        file_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        self.file_label = tk.Label(file_frame, text="Nessun file selezionato", anchor="w")
        self.file_label.pack(side="left", expand=True, fill="x", padx=(0,5))
        
        browse_button = tk.Button(file_frame, text="Sfoglia File", command=self.browse_file)
        browse_button.pack(side="right")

        # Widget per mostrare i messaggi di stato (riga 1)
        self.text = tk.Text(self, wrap="word")
        self.text.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # Barra di avanzamento (riga 2)
        self.progress = ttk.Progressbar(self, mode="determinate")
        self.progress.grid(row=2, column=0, sticky="ew", padx=5, pady=(0,5))

        # Bottone per avviare la scansione (riga 3)
        self.start_button = tk.Button(self, text="Avvia Scansione", command=self.start_scan, state="disabled")
        self.start_button.grid(row=3, column=0, sticky="ew", padx=5, pady=5)

        # Coda per la comunicazione tra thread
        self.queue = queue.Queue()

        # Variabili per il progresso
        self.total_tasks = 0
        self.completed_tasks = 0

        # Percorso del file degli host (inizialmente None)
        self.hosts_file = None

    def browse_file(self):
        file_path = filedialog.askopenfilename(title="Seleziona il file degli host", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            # Verifica preliminare del file: deve contenere almeno una riga valida
            valid = False
            try:
                with open(file_path, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line and "," in line:
                            parts = [x.strip() for x in line.split(",")]
                            if len(parts) >= 2:
                                valid = True
                                break
                if valid:
                    self.hosts_file = file_path
                    self.file_label.config(text=f"File selezionato: {os.path.basename(file_path)}")
                    self.start_button.config(state="normal")
                    self.text.insert(tk.END, f"File valido selezionato: {file_path}\n")
                else:
                    messagebox.showerror("Errore file", "Il file non risulta nel formato corretto.\nFormato atteso: host,porta,porta,...")
                    self.file_label.config(text="Nessun file selezionato")
                    self.start_button.config(state="disabled")
            except Exception as e:
                messagebox.showerror("Errore", f"Errore durante l'apertura del file: {e}")
                self.file_label.config(text="Nessun file selezionato")
                self.start_button.config(state="disabled")

    def start_scan(self):
        if not self.hosts_file:
            messagebox.showerror("Errore", "Seleziona un file valido prima di avviare la scansione.")
            return

        self.start_button.config(state="disabled")
        self.text.delete("1.0", tk.END)
        self.progress["value"] = 0
        self.completed_tasks = 0
        # Avvia il thread per la scansione
        threading.Thread(target=self.scan_ports, daemon=True).start()
        # Avvia il polling della coda per aggiornare l'interfaccia
        self.after(100, self.process_queue)

    def scan_ports(self):
        # Se l'applicazione è frozen, usa la directory dell'eseguibile; altrimenti usa __file__
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        log_file = os.path.join(base_dir, "log.txt")
        
        tasks = []
        results_list = []

        try:
            with open(self.hosts_file, "r") as f:
                lines = f.readlines()
        except Exception as e:
            self.queue.put(f"Errore nella lettura del file: {e}\n")
            self.queue.put("DONE")
            return

        for line in lines:
            line = line.strip()
            if not line:
                continue
            # La riga deve essere nel formato: host,porta,porta,porta,...
            parts = [x.strip() for x in line.split(",")]
            if len(parts) < 2:
                self.queue.put(f"Formato non valido: {line}\n")
                continue
            host = parts[0]
            ports = parts[1:]
            for port in ports:
                tasks.append((host, port))

        self.total_tasks = len(tasks)
        self.queue.put(f"Task totali: {self.total_tasks}\n")

        # Esecuzione parallela con ThreadPoolExecutor
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_task = {executor.submit(check_port, host, port): (host, port) for host, port in tasks}
            for future in concurrent.futures.as_completed(future_to_task):
                host, port = future_to_task[future]
                try:
                    success = future.result()
                    if success:
                        result_line = f"{host} {port} success\n"
                    else:
                        result_line = f"{host} {port} fail\n"
                    results_list.append(result_line)
                    self.queue.put(result_line)
                except Exception as e:
                    result_line = f"{host} {port} exception: {e}\n"
                    results_list.append(result_line)
                    self.queue.put(result_line)
                self.completed_tasks += 1
                self.queue.put("PROGRESS")

        # Scrive il file di log al termine della scansione
        try:
            with open(log_file, "w") as f:
                f.writelines(results_list)
            self.queue.put(f"\nLog file creato: {log_file}\n")
        except Exception as e:
            self.queue.put(f"\nErrore nella scrittura del log: {e}\n")

        self.queue.put("DONE")

    def process_queue(self):
        try:
            while True:
                msg = self.queue.get_nowait()
                if msg == "PROGRESS":
                    self.progress["value"] = self.completed_tasks
                    self.progress["maximum"] = self.total_tasks
                elif msg == "DONE":
                    self.start_button.config(state="normal")
                else:
                    self.text.insert(tk.END, msg)
                    self.text.see(tk.END)
        except queue.Empty:
            pass
        if self.start_button["state"] == "disabled":
            self.after(100, self.process_queue)

if __name__ == "__main__":
    app = PortScannerApp()
    app.mainloop()
