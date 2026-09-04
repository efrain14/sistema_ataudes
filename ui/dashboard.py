import customtkinter as ctk
from database.daos import AtaudDAO
from config import UMBRAL_USOS_CRITICO

class DashboardView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill="both", expand=True, padx=20, pady=20)
        self.grid_columnconfigure((0, 1, 2, 3), weight=1)

        ctk.CTkLabel(self, text="📊 Dashboard", font=ctk.CTkFont(size=26, weight="bold")).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 20))

        self.tarjetas = {}
        metricas = AtaudDAO.metricas()
        configs = [
            ("Total", metricas["total"], "#3498db"),
            ("Disponibles", metricas["disponibles"], "#27ae60"),
            ("En Uso", metricas["en_uso"], "#e67e22"),
            ("En Restauración", metricas["restauracion"], "#9b59b6"),
            ("Dados de Baja", metricas["baja"], "#7f8c8d"),
            ("⚠️ Críticos (≥20 usos)", metricas["criticos"], "#c0392b"),
        ]
        for i, (titulo, valor, color) in enumerate(configs):
            fila, col = divmod(i, 3)
            card = ctk.CTkFrame(self, corner_radius=12, fg_color=color)
            card.grid(row=fila + 1, column=col, padx=10, pady=10, sticky="nsew")
            ctk.CTkLabel(card, text=titulo, font=ctk.CTkFont(size=14)).pack(pady=(15, 5))
            lbl = ctk.CTkLabel(card, text=str(valor), font=ctk.CTkFont(size=38, weight="bold"))
            lbl.pack(pady=(0, 15))
            self.tarjetas[titulo] = lbl

        # Ataúdes críticos
        ctk.CTkLabel(self, text="⚠️ Ataúdes con usos críticos (≥20)", font=ctk.CTkFont(size=16, weight="bold")).grid(row=4, column=0, columnspan=4, sticky="w", pady=(20, 5))

        criticos = [a for a in AtaudDAO.listar() if a["contador_usos"] >= UMBRAL_USOS_CRITICO and a["estado"] != "Dado de Baja"]
        if criticos:
            frame = ctk.CTkFrame(self, fg_color="#4a1a1a")
            frame.grid(row=5, column=0, columnspan=4, sticky="nsew", pady=5)
            for a in criticos[:10]:
                ctk.CTkLabel(frame, text=f"• {a['codigo_qr']} — {a['tipo']} — {a['contador_usos']} usos", text_color="#ff6b6b").pack(anchor="w", padx=15, pady=2)
        else:
            ctk.CTkLabel(self, text="✅ Sin alertas críticas", text_color="green").grid(row=5, column=0, columnspan=4)

        self.btn_refrescar = ctk.CTkButton(self, text="🔄 Refrescar", command=self.refrescar)
        self.btn_refrescar.grid(row=6, column=0, pady=20)

    def refrescar(self):
        for w in self.winfo_children():
            w.destroy()
        self.__init__(self.master)