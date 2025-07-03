#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Système de Surveillance d'Examen
Module Principal - exam_monitor.py
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import datetime
import json
import os
import sys
import logging
from pathlib import Path

# Imports pour la surveillance système
import psutil
import pyautogui
import win32gui
import win32process
import win32clipboard

import subprocess
import winreg
from PIL import Image, ImageTk

# Configuration des logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('exam_monitor.log'),
        logging.StreamHandler()
    ]
)

class ExamMonitor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Surveillant d'Examen - Version Étudiant")
        self.root.geometry("800x600")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Variables de contrôle
        self.monitoring = False
        self.exam_started = False
        self.student_name = ""
        self.exam_id = ""
        self.exam_start_time = None
        
        # Configuration de surveillance
        self.config = {
            "forbidden_keywords": [
                "chatgpt", "stackoverflow", "discord", "whatsapp",
                "facebook", "youtube", "instagram", "gmail", "outlook",
                "claude", "bard", "copilot", "github"
            ],
            "forbidden_processes": [
                "discord.exe", "whatsapp.exe", "telegram.exe", "slack.exe",
                "teams.exe", "zoom.exe", "notepad++.exe"
            ],
            "check_interval": 5,  # secondes
            "screenshot_on_violation": True,
            "block_clipboard": True,
            "monitor_usb": True
        }
        
        # Données de surveillance
        self.violations = []
        self.last_clipboard = ""
        self.usb_devices = set()
        self.last_violation_time = {}
        self.violation_cooldown = 30  # secondes
        
        # Créer les dossiers nécessaires
        self.setup_directories()
        
        # Interface utilisateur
        self.setup_ui()
        
        # Initialiser la surveillance USB
        self.init_usb_monitoring()

    def setup_directories(self):
        """Créer les dossiers pour les logs et captures d'écran"""
        os.makedirs("logs", exist_ok=True)
        os.makedirs("screenshots", exist_ok=True)
        os.makedirs("reports", exist_ok=True)

    def setup_ui(self):
        """Configurer l'interface utilisateur"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configuration de l'examen
        config_frame = ttk.LabelFrame(main_frame, text="Configuration de l'Examen", padding="10")
        config_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(config_frame, text="Nom de l'étudiant:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.student_entry = ttk.Entry(config_frame, width=30)
        self.student_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        ttk.Label(config_frame, text="ID de l'examen:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        self.exam_entry = ttk.Entry(config_frame, width=30)
        self.exam_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Boutons de contrôle
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=1, column=0, columnspan=2, pady=(0, 10))
        
        self.start_btn = ttk.Button(control_frame, text="Démarrer l'Examen", 
                                   command=self.start_exam)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_btn = ttk.Button(control_frame, text="Arrêter l'Examen", 
                                  command=self.stop_exam, state="disabled")
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.config_btn = ttk.Button(control_frame, text="Configuration", 
                                    command=self.open_config)
        self.config_btn.pack(side=tk.LEFT)
        
        # Status
        self.status_var = tk.StringVar(value="Prêt à démarrer")
        status_frame = ttk.LabelFrame(main_frame, text="Statut", padding="10")
        status_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var)
        self.status_label.pack()
        
        # Zone de logs
        log_frame = ttk.LabelFrame(main_frame, text="Journal de Surveillance", padding="10")
        log_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Statistiques
        stats_frame = ttk.LabelFrame(main_frame, text="Statistiques", padding="10")
        stats_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        self.stats_violations = ttk.Label(stats_frame, text="Violations détectées: 0")
        self.stats_violations.pack(side=tk.LEFT, padx=(0, 20))
        
        self.stats_time = ttk.Label(stats_frame, text="Temps d'examen: 00:00:00")
        self.stats_time.pack(side=tk.LEFT)
        
        # Configuration du redimensionnement
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)

    def start_exam(self):
        """Démarrer la surveillance d'examen"""
        # Validation des champs
        student_name = self.student_entry.get().strip()
        exam_id = self.exam_entry.get().strip()
        
        if not student_name or not exam_id:
            messagebox.showerror("Erreur", "Veuillez renseigner le nom de l'étudiant et l'ID de l'examen")
            return
        
        self.student_name = student_name
        self.exam_id = exam_id
        
        # Confirmation de démarrage
        if not messagebox.askyesno("Confirmation", 
                                   f"Démarrer l'examen pour {student_name}?\n\n"
                                   "Une fois démarré, toutes vos actions seront surveillées."):
            return
        
        # Démarrer la surveillance
        self.exam_started = True
        self.monitoring = True
        self.exam_start_time = datetime.datetime.now()
        
        # Mise à jour de l'interface
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.student_entry.config(state="disabled")
        self.exam_entry.config(state="disabled")
        self.status_var.set("Surveillance ACTIVE - Examen en cours")
        
        # Démarrer le thread de surveillance
        self.monitoring_thread = threading.Thread(target=self.monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        # Démarrer le timer
        self.timer_thread = threading.Thread(target=self.update_timer, daemon=True)
        self.timer_thread.start()
        
        self.log_event("INFO", f"Examen démarré pour {student_name} (ID: {exam_id})")

    def stop_exam(self):
        """Arrêter la surveillance d'examen"""
        if messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir arrêter l'examen?"):
            self.monitoring = False
            self.exam_started = False
            
            # Mise à jour de l'interface
            self.start_btn.config(state="normal")
            self.stop_btn.config(state="disabled")
            self.student_entry.config(state="normal")
            self.exam_entry.config(state="normal")
            self.status_var.set("Examen terminé")
            
            # Générer le rapport final
            self.generate_report()
            
            self.log_event("INFO", "Examen terminé")

    def monitoring_loop(self):
        """Boucle principale de surveillance"""
        while self.monitoring:
            try:
                # Vérifier les processus actifs
                self.check_active_processes()
                
                # Vérifier les fenêtres de navigateur
                self.check_browser_windows()
                
                # Vérifier le presse-papiers
                if self.config["block_clipboard"]:
                    self.check_clipboard()
                
                # Vérifier les périphériques USB
                if self.config["monitor_usb"]:
                    self.check_usb_devices()
                
                # Attendre avant la prochaine vérification
                time.sleep(self.config["check_interval"])
                
            except Exception as e:
                self.log_event("ERROR", f"Erreur dans la surveillance: {str(e)}")

    def check_active_processes(self):
        """Vérifier les processus actifs"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    proc_name = proc.info['name'].lower()
                    
                    # Vérifier si le processus est interdit
                    if proc_name in self.config["forbidden_processes"]:
                        self.report_violation("PROCESSUS_INTERDIT", 
                                            f"Processus interdit détecté: {proc_name}")
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
        except Exception as e:
            self.log_event("ERROR", f"Erreur lors de la vérification des processus: {str(e)}")

    def check_browser_windows(self):
        """Vérifier les fenêtres de navigateur et leurs titres"""
        try:
            def enum_window_callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    window_title = win32gui.GetWindowText(hwnd).lower()
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    
                    try:
                        process = psutil.Process(pid)
                        process_name = process.name().lower()
                        
                        # Vérifier si c'est un navigateur
                        browser_names = ['chrome.exe', 'firefox.exe', 'msedge.exe', 'opera.exe', 'brave.exe']
                        if process_name in browser_names:
                            # Vérifier les mots-clés interdits dans le titre
                            for keyword in self.config["forbidden_keywords"]:
                                if keyword in window_title:
                                    self.report_violation("SITE_INTERDIT",
                                                        f"Site interdit détecté: {keyword} dans '{window_title}'")
                                    
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                        
                return True
            
            win32gui.EnumWindows(enum_window_callback, [])
            
        except Exception as e:
            self.log_event("ERROR", f"Erreur lors de la vérification des navigateurs: {str(e)}")

    def check_clipboard(self):
        """Vérifier l'utilisation du presse-papiers"""
        try:
            win32clipboard.OpenClipboard()
            try:
                current_clipboard = win32clipboard.GetClipboardData()
                if current_clipboard != self.last_clipboard:
                    if self.last_clipboard:  # Pas la première fois
                        self.report_violation("COPIER_COLLER",
                                            f"Utilisation du presse-papiers détectée")
                    self.last_clipboard = current_clipboard
            except:
                pass
            finally:
                win32clipboard.CloseClipboard()
                
        except Exception as e:
            self.log_event("ERROR", f"Erreur lors de la vérification du presse-papiers: {str(e)}")

    def check_usb_devices(self):
        """Vérifier les connexions USB"""
        try:
            current_devices = set()
            
            # Lister les périphériques de stockage
            for partition in psutil.disk_partitions():
                if 'removable' in partition.opts:
                    current_devices.add(partition.device)
            
            # Détecter les nouveaux périphériques
            new_devices = current_devices - self.usb_devices
            if new_devices:
                for device in new_devices:
                    self.report_violation("USB_DETECTE",
                                        f"Nouveau périphérique USB détecté: {device}")
                    
            self.usb_devices = current_devices
            
        except Exception as e:
            self.log_event("ERROR", f"Erreur lors de la vérification USB: {str(e)}")

    def init_usb_monitoring(self):
        """Initialiser la surveillance USB"""
        try:
            # Enregistrer l'état initial des périphériques USB
            for partition in psutil.disk_partitions():
                if 'removable' in partition.opts:
                    self.usb_devices.add(partition.device)
        except Exception as e:
            self.log_event("ERROR", f"Erreur lors de l'initialisation USB: {str(e)}")

    def report_violation(self, violation_type, description):
        """Signaler une violation"""
        timestamp = datetime.datetime.now()
        violation = {
            "timestamp": timestamp.isoformat(),
            "type": violation_type,
            "description": description,
            "student": self.student_name,
            "exam_id": self.exam_id
        }

        # Anti-spam : éviter de répéter la même alerte trop souvent
        now = time.time()
        last_time = self.last_violation_time.get(description, 0)
        if now - last_time < self.violation_cooldown:
            return  # Trop tôt pour répéter cette alerte

        self.last_violation_time[description] = now
        self.violations.append(violation)

        # Capture écran
        screenshot_path = None
        if self.config["screenshot_on_violation"]:
            screenshot_path = self.take_screenshot(violation_type)
            violation["screenshot"] = screenshot_path

        # Alerte & log
        self.show_violation_alert(violation_type, description)
        self.log_event("VIOLATION", f"{violation_type}: {description}")
        self.update_stats()

    def take_screenshot(self, violation_type):
        """Prendre une capture d'écran"""
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshots/{self.exam_id}_{timestamp}_{violation_type}.png"
            
            screenshot = pyautogui.screenshot()
            screenshot.save(filename)
            
            return filename
            
        except Exception as e:
            self.log_event("ERROR", f"Erreur lors de la capture d'écran: {str(e)}")
            return None

    def show_violation_alert(self, violation_type, description):
        """Afficher une alerte de violation"""
        # Créer une fenêtre d'alerte
        alert_window = tk.Toplevel(self.root)
        alert_window.title("⚠️ VIOLATION DÉTECTÉE")
        alert_window.geometry("400x200")
        alert_window.configure(bg='red')
        alert_window.attributes('-topmost', True)
        
        # Centrer la fenêtre
        alert_window.transient(self.root)
        alert_window.grab_set()
        
        # Contenu de l'alerte
        frame = ttk.Frame(alert_window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        title_label = ttk.Label(frame, text="⚠️ TENTATIVE DE TRICHE DÉTECTÉE",
                               font=("Arial", 14, "bold"), foreground="red")
        title_label.pack(pady=(0, 10))
        
        desc_label = ttk.Label(frame, text=description, font=("Arial", 10),
                              wraplength=350)
        desc_label.pack(pady=(0, 20))
        
        ttk.Button(frame, text="J'ai compris", 
                  command=alert_window.destroy).pack()
        
        # Fermer automatiquement après 10 secondes
        alert_window.after(10000, alert_window.destroy)

    def log_event(self, level, message):
        """Logger un événement"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {level}: {message}\n"
        
        # Ajouter au widget de log
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)
        
        # Logger dans le fichier
        if level == "ERROR":
            logging.error(message)
        elif level == "VIOLATION":
            logging.warning(message)
        else:
            logging.info(message)

    def update_stats(self):
        """Mettre à jour les statistiques"""
        violation_count = len(self.violations)
        self.stats_violations.config(text=f"Violations détectées: {violation_count}")

    def update_timer(self):
        """Mettre à jour le timer d'examen"""
        while self.exam_started:
            if self.exam_start_time:
                elapsed = datetime.datetime.now() - self.exam_start_time
                elapsed_str = str(elapsed).split('.')[0]  # Enlever les microsecondes
                self.stats_time.config(text=f"Temps d'examen: {elapsed_str}")
            
            time.sleep(1)

    def generate_report(self):
        """Générer le rapport final d'examen"""
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            report_filename = f"reports/rapport_{self.exam_id}_{timestamp}.json"
            
            if self.exam_start_time:
                exam_duration = datetime.datetime.now() - self.exam_start_time
            else:
                exam_duration = datetime.timedelta(0)
            
            report = {
                "student_name": self.student_name,
                "exam_id": self.exam_id,
                "start_time": self.exam_start_time.isoformat() if self.exam_start_time else None,
                "end_time": datetime.datetime.now().isoformat(),
                "duration": str(exam_duration),
                "violations": self.violations,
                "total_violations": len(self.violations),
                "config": self.config
            }
            
            with open(report_filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("Rapport généré", 
                               f"Rapport d'examen sauvegardé: {report_filename}")
            
        except Exception as e:
            self.log_event("ERROR", f"Erreur lors de la génération du rapport: {str(e)}")

    def open_config(self):
        """Ouvrir la fenêtre de configuration"""
        config_window = ConfigWindow(self.root, self.config, self.on_config_updated)

    def on_config_updated(self, new_config):
        """Callback quand la configuration est mise à jour"""
        self.config.update(new_config)
        self.log_event("INFO", "Configuration mise à jour")

    def on_closing(self):
        """Gérer la fermeture de l'application"""
        if self.exam_started:
            if messagebox.askyesno("Confirmation", 
                                   "Un examen est en cours. Êtes-vous sûr de vouloir quitter?"):
                self.monitoring = False
                self.root.destroy()
        else:
            self.root.destroy()

    def run(self):
        """Lancer l'application"""
        self.root.mainloop()


class ConfigWindow:
    """Fenêtre de configuration"""
    
    def __init__(self, parent, config, callback):
        self.parent = parent
        self.config = config.copy()
        self.callback = callback
        
        self.window = tk.Toplevel(parent)
        self.window.title("Configuration de Surveillance")
        self.window.geometry("600x500")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.setup_ui()

    def setup_ui(self):
        """Configurer l'interface de configuration"""
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Onglet Général
        general_frame = ttk.Frame(notebook, padding="10")
        notebook.add(general_frame, text="Général")
        
        ttk.Label(general_frame, text="Intervalle de vérification (secondes):").grid(row=0, column=0, sticky=tk.W)
        self.interval_var = tk.StringVar(value=str(self.config["check_interval"]))
        ttk.Entry(general_frame, textvariable=self.interval_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        self.screenshot_var = tk.BooleanVar(value=self.config["screenshot_on_violation"])
        ttk.Checkbutton(general_frame, text="Prendre des captures d'écran lors des violations",
                       variable=self.screenshot_var).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
        
        self.clipboard_var = tk.BooleanVar(value=self.config["block_clipboard"])
        ttk.Checkbutton(general_frame, text="Surveiller le presse-papiers",
                       variable=self.clipboard_var).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        self.usb_var = tk.BooleanVar(value=self.config["monitor_usb"])
        ttk.Checkbutton(general_frame, text="Surveiller les périphériques USB",
                       variable=self.usb_var).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        # Onglet Mots-clés interdits
        keywords_frame = ttk.Frame(notebook, padding="10")
        notebook.add(keywords_frame, text="Mots-clés interdits")
        
        ttk.Label(keywords_frame, text="Mots-clés interdits (un par ligne):").pack(anchor=tk.W)
        self.keywords_text = scrolledtext.ScrolledText(keywords_frame, height=15, width=50)
        self.keywords_text.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        self.keywords_text.insert(tk.END, '\n'.join(self.config["forbidden_keywords"]))
        
        # Onglet Processus interdits
        processes_frame = ttk.Frame(notebook, padding="10")
        notebook.add(processes_frame, text="Processus interdits")
        
        ttk.Label(processes_frame, text="Processus interdits (un par ligne):").pack(anchor=tk.W)
        self.processes_text = scrolledtext.ScrolledText(processes_frame, height=15, width=50)
        self.processes_text.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        self.processes_text.insert(tk.END, '\n'.join(self.config["forbidden_processes"]))
        
        # Boutons
        button_frame = ttk.Frame(self.window)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Button(button_frame, text="Annuler", 
                  command=self.window.destroy).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="Sauvegarder", 
                  command=self.save_config).pack(side=tk.RIGHT)

    def save_config(self):
        """Sauvegarder la configuration"""
        try:
            # Mettre à jour la configuration
            self.config["check_interval"] = int(self.interval_var.get())
            self.config["screenshot_on_violation"] = self.screenshot_var.get()
            self.config["block_clipboard"] = self.clipboard_var.get()
            self.config["monitor_usb"] = self.usb_var.get()
            
            # Mots-clés interdits
            keywords_text = self.keywords_text.get(1.0, tk.END).strip()
            self.config["forbidden_keywords"] = [kw.strip().lower() for kw in keywords_text.split('\n') if kw.strip()]
            
            # Processus interdits
            processes_text = self.processes_text.get(1.0, tk.END).strip()
            self.config["forbidden_processes"] = [proc.strip().lower() for proc in processes_text.split('\n') if proc.strip()]
            
            # Sauvegarder dans un fichier
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            # Callback
            self.callback(self.config)
            
            messagebox.showinfo("Configuration", "Configuration sauvegardée avec succès!")
            self.window.destroy()
            
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer un nombre valide pour l'intervalle")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde: {str(e)}")


if __name__ == "__main__":
    try:
        # Vérifier les dépendances
        required_modules = ['psutil', 'pyautogui', 'win32gui', 'PIL']
        missing_modules = []
        
        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                missing_modules.append(module)
        
        if missing_modules:
            print("Modules manquants détectés. Installation en cours...")
            print("Modules manquants:", ', '.join(missing_modules))
            print("\nPour installer les dépendances, exécutez:")
            print("pip install psutil pyautogui pywin32 pillow")
            sys.exit(1)
        
        # Lancer l'application
        app = ExamMonitor()
        app.run()
        
    except Exception as e:
        print(f"Erreur lors du lancement: {str(e)}")
        input("Appuyez sur Entrée pour quitter...")