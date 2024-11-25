import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os


class SysMLv2APIClient:
    """
    Klasse zur Interaktion mit der SysMLv2 API.
    Verbindet sich mit dem lokalen Server, führt CRUD-Operationen aus
    und speichert die Ergebnisse.

    Attributes:
        base_url (str): Basis-URL der API.
    """
    def __init__(self, base_url: str):
        """
        Initialisiert den API-Client mit der angegebenen Basis-URL.

        Args:
            base_url (str): Die Basis-URL des lokalen SysMLv2 Servers.
        """
        self.base_url = base_url

    def get_model(self, model_id: str) -> dict:
        """
        Ruft ein SysMLv2-Modell mit der angegebenen ID ab.

        Args:
            model_id (str): Die ID des gewünschten Modells.

        Returns:
            dict: Das Modell als JSON-Daten, wenn der Abruf erfolgreich ist.
        """
        try:
            response = requests.get(f"{self.base_url}/models/{model_id}")
            response.raise_for_status()  # Fehler auslösen, wenn der Statuscode nicht 200 ist
            return response.json()
        except requests.RequestException as e:
            raise ConnectionError(f"Fehler beim Abrufen des Modells: {e}") from e

    def save_response(self, data: dict, file_path: str):
        """
        Speichert die API-Antwort in einer JSON-Datei.

        Args:
            data (dict): Die JSON-Daten, die gespeichert werden sollen.
            file_path (str): Der Speicherort der Datei.
        """
        try:
            with open(file_path, "w") as file:
                json.dump(data, file, indent=4)
        except IOError as e:
            raise IOError(f"Fehler beim Speichern der Datei: {e}") from e


class SysMLv2App:
    """
    Hauptanwendung für die GUI, welche die Benutzerinteraktion steuert.
    Verwendet Tkinter für die Benutzeroberfläche.
    """
    def __init__(self, root):
        """
        Initialisiert die Tkinter-GUI.

        Args:
            root: Das Hauptfenster der Anwendung.
        """
        self.root = root
        self.root.title("SysMLv2 API Client")

        # API-Client initialisieren
        self.api_client = SysMLv2APIClient(base_url="http://localhost:8080")

        # GUI-Elemente
        self.create_widgets()

    def create_widgets(self):
        """Erstellt die GUI-Elemente."""
        # Eingabe für Model-ID
        ttk.Label(self.root, text="Modell-ID:").grid(row=0, column=0, padx=5, pady=5)
        self.model_id_entry = ttk.Entry(self.root, width=30)
        self.model_id_entry.grid(row=0, column=1, padx=5, pady=5)

        # Button zum Abrufen des Modells
        fetch_button = ttk.Button(self.root, text="Modell abrufen", command=self.fetch_model)
        fetch_button.grid(row=1, column=0, columnspan=2, pady=10)

    def fetch_model(self):
        """Ruft ein Modell ab und speichert die Antwort."""
        model_id = self.model_id_entry.get()

        if not model_id:
            messagebox.showwarning("Warnung", "Bitte geben Sie eine Modell-ID ein.")
            return

        try:
            # Modell abrufen
            data = self.api_client.get_model(model_id)
            messagebox.showinfo("Erfolg", f"Modell {model_id} erfolgreich abgerufen!")

            # Antwort speichern
            save_path = os.path.join(os.getcwd(), f"{model_id}_model.json")
            self.api_client.save_response(data, save_path)
            messagebox.showinfo("Gespeichert", f"Modell wurde gespeichert unter:\n{save_path}")
        except ConnectionError as e:
            messagebox.showerror("Verbindungsfehler", str(e))
        except IOError as e:
            messagebox.showerror("Speicherfehler", str(e))


class MetadataManager:
    """
    Klasse zur Verwaltung von Metadaten zwischen Domänenmodellen und SysMLv2.
    """
    def __init__(self, domain_files: list):
        """
        Initialisiert den Metadaten-Manager.

        Args:
            domain_files (list): Liste der standardisierten Dateipfade aus Domänen.
        """
        self.domain_files = domain_files

    def map_metadata(self, sysml_data: dict, domain_data: dict) -> dict:
        """
        Verknüpft Metadaten aus Domänenmodellen mit SysMLv2-Daten.

        Args:
            sysml_data (dict): SysMLv2-Daten als JSON.
            domain_data (dict): Domänenmodell-Daten als JSON.

        Returns:
            dict: Verknüpfte Metadaten.
        """
        # Beispielhafte Logik: Kombinieren der Daten
        combined_data = {
            "sysml": sysml_data,
            "domain": domain_data
        }
        return combined_data


if __name__ == "__main__":
    # Tkinter-App starten
    root = tk.Tk()
    app = SysMLv2App(root)
    root.mainloop()
