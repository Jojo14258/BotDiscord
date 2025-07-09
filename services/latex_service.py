from IPython.display import Image
import matplotlib.pyplot as plt
import re
import io
from contextlib import redirect_stderr




class LatexService:
    """Service pour la gestion des équations LaTeX"""
    
    @staticmethod
    def contains_latex(text: str) -> bool:
        """Vérifie si le texte contient du code LaTeX"""
        latex_patterns = [
            r'\$.*?\$',           # Math inline: $...$
            r'\\\[.*?\\\]',       # Math display: \[...\]
            r'\\\(.*?\\\)',       # Math inline: \(...\)
            r'\\begin\{.*?\}',    # Environnements: \begin{...}
            r'\\[a-zA-Z]+',       # Commandes LaTeX: \command
            r'\\frac\{.*?\}\{.*?\}',  # Fractions
            r'\^[{]?.*?[}]?',     # Exposants
            r'_[{]?.*?[}]?',      # Indices
        ]
        
        for pattern in latex_patterns:
            if re.search(pattern, text, re.DOTALL):
                return True
        return False
  
  
    @staticmethod
    def extract_and_format_latex(text: str) -> str:
        """Extrait les formules LaTeX et formate le texte pour une image"""
        print(f"[DEBUG] Texte original: {repr(text)}")
        
        # Remplacer toutes les formules LaTeX par des versions compatibles
        # Convertir \( ... \) en $ ... $ (toutes les occurrences)
        text = re.sub(r'\\\((.*?)\\\)', r'$\1$', text)
        print(f"[DEBUG] Après conversion \\(...\\): {repr(text)}")
        
        # Convertir \[ ... \] en $ ... $ (display math -> inline pour simplicité)
        text = re.sub(r'\\\[(.*?)\\\]', r'$\1$', text)
        print(f"[DEBUG] Après conversion \\[...\\]: {repr(text)}")
        
        # Nettoyer les doubles $ qui peuvent apparaître ($$ -> $)
        text = re.sub(r'\$\$+', r'$', text)
        print(f"[DEBUG] Après nettoyage $$: {repr(text)}")
        
        # Nettoyer les $ vides qui peuvent apparaître
        text = re.sub(r'\$\s*\$', r'', text)
        print(f"[DEBUG] Après nettoyage $ vides: {repr(text)}")
        
        # Ajouter des espaces autour des formules pour une meilleure lisibilité
        text = re.sub(r'\$([^$]+)\$', r' $\1$ ', text)
        print(f"[DEBUG] Après ajout espaces: {repr(text)}")
        
        # Nettoyer les espaces multiples
        text = re.sub(r'\s+', r' ', text)
        print(f"[DEBUG] Après nettoyage espaces: {repr(text)}")
        
        result = text.strip()
        print(f"[DEBUG] Résultat final: {repr(result)}")
        return result
    
    @staticmethod
    def latex_to_image(texte: str, filename: str, width: int = 1000, height: int = 600):
        """Convertit le texte contenant du LaTeX en image bien formatée"""
        try:
            # Extraire et formatter le texte LaTeX
            formatted_text = LatexService.extract_and_format_latex(texte)
            
            # Ajuster la taille en fonction de la longueur du texte
            text_length = len(formatted_text)
            if text_length > 200:
                fig_width, fig_height = width/80, height/80  # Plus grand pour long texte
                fontsize = 12
            elif text_length > 100:
                fig_width, fig_height = width/90, height/90
                fontsize = 13
            else:
                fig_width, fig_height = width/100, height/100
                fontsize = 14
            
            # Créer une figure adaptée
            fig, ax = plt.subplots(figsize=(fig_width, fig_height))
            
            # Configurer l'affichage
            ax.text(0.5, 0.5, formatted_text, fontsize=fontsize, ha='center', va='center', 
                   transform=ax.transAxes, wrap=True, 
                   bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.8))
            ax.axis('off')
            
            # Sauvegarder avec fond blanc
            plt.savefig(filename, bbox_inches='tight', dpi=300, facecolor='white', 
                       edgecolor='none', pad_inches=0.2)
            plt.close(fig)
            
            return True
            
        except Exception as e:
            print(f"Erreur lors de la génération LaTeX: {e}")
            if 'fig' in locals():
                plt.close(fig)
            return False



#dot_product_equation_algebraic = r"Le produit de machin par machin est : $\mathbf{a} \cdot \mathbf{b} = \sum_{i=1}^n a_i b_i$"

#fig, ax = plt.subplots(figsize=(6,3))
#ax.text(0.5,0.5,dot_product_equation_algebraic, fontsize=50,ha='center',va='center')
#ax.axis('off')

#plt.savefig('dot_product_equation_algebraic.png', bbox_inches='tight', dpi=300)
#plt.close(fig)

#Image('dot_product_equation_algebraic.png', width=600, height=300)

# Instance globale
latex_service = LatexService()