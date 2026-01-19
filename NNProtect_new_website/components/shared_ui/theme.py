'''Archivo que contiene los colores oficiales del tema personalizado de la página'''

class Custom_theme():
    def light_colors(self):
        return {
            "primary": "#0039F2",
            "secondary": "#5E79FF",
            "tertiary": "#FFFFFF",
            "background": "#F2F3F8",
            "traslucid-background": "rgba(255, 255, 255, 1)",
            "traslucid-background-blue": "rgba(0, 57, 242, 0.8)",
            "menu-background": "linear-gradient(180deg, rgba(0, 0, 0, 0.15) 10%, rgba(0, 0, 0, 0) 100%)",
            "text": "#000000",
            "border": "#0039F2",
            "box_shadow": "0px 0px 16px 3px #5E79FF10",
            "success": "#10B981",
            "success_light": "#D1FAE5",
            "warning": "#F59E0B",
            "warning_light": "#FEF3C7",
            "error": "#EF4444",
            "error_light": "#FEE2E2",
            "info": "#3B82F6",
            "info_light": "#DBEAFE",
        }
    
    def dark_colors(self):
        return {
            "primary": "#0039F2",
            "secondary": "#5E79FF",
            "tertiary": "#1C1C1E",
            "background": "#000000",
            "traslucid-background": "rgba(0, 0, 0, 0.6)",
            "menu-background": "linear-gradient(180deg, rgba(255, 255, 255, 0.1) 0%, rgba(0, 0, 0, 0) 100%)",
            "text": "#FFFFFF",
            "border": "#D8B4FE",
            "box_shadow": "0px 0px 16px 2px #1A155C90",
            "success": "#10B981",
            "success_light": "#D1FAE5",
            "warning": "#F59E0B",
            "warning_light": "#FEF3C7",
            "error": "#EF4444",
            "error_light": "#FEE2E2",
            "info": "#3B82F6",
            "info_light": "#DBEAFE",
        }