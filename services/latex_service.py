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
        """Extrait les formules LaTeX et formate le texte pour une image en préservant les retours à la ligne"""
        print(f"[DEBUG] Texte original: {repr(text)}")
        
        # Remplacer les caractères Unicode problématiques
        text = text.replace('\u274c', 'X')  # ❌ -> X
        text = text.replace('\u2705', 'V')  # ✅ -> V
        text = text.replace('\u2713', 'V')  # ✓ -> V
        print(f"[DEBUG] Après remplacement Unicode: {repr(text)}")
        
        # Remplacer toutes les formules LaTeX par des versions compatibles
        # Convertir \( ... \) en $ ... $ (toutes les occurrences)
        text = re.sub(r'\\\((.*?)\\\)', r'$\1$', text, flags=re.DOTALL)
        print(f"[DEBUG] Après conversion \\(...\\): {repr(text)}")
        
        # Convertir \[ ... \] en $ ... $ (display math -> inline pour simplicité) 
        # Utilisation d'un pattern plus robuste
        text = re.sub(r'\\\[(.*?)\\\]', r'$$\1$$', text, flags=re.DOTALL)
        print(f"[DEBUG] Après conversion \\[...\\]: {repr(text)}")
        
        # Nettoyer les doubles $ qui peuvent apparaître (mais garder $$ pour display math)
        text = re.sub(r'\$\$\$+', r'$$', text)
        print(f"[DEBUG] Après nettoyage $$$: {repr(text)}")
        
        # Nettoyer les $ vides qui peuvent apparaître
        text = re.sub(r'\$\s*\$', r'', text)
        text = re.sub(r'\$\$\s*\$\$', r'', text)
        print(f"[DEBUG] Après nettoyage $ vides: {repr(text)}")
        
        # Ajouter des espaces autour des formules pour une meilleure lisibilité
        text = re.sub(r'\$([^$]+)\$', r' $\1$ ', text)
        text = re.sub(r'\$\$([^$]+)\$\$', r' $$\1$$ ', text)
        print(f"[DEBUG] Après ajout espaces: {repr(text)}")
        
        # Nettoyer les espaces multiples SAUF les retours à la ligne
        text = re.sub(r'[ \t]+', r' ', text)  # Remplacer espaces/tabs multiples par un seul espace
        text = re.sub(r' *\n *', r'\n', text)  # Nettoyer espaces autour des retours à la ligne
        print(f"[DEBUG] Après nettoyage espaces: {repr(text)}")
        
        result = text.strip()
        print(f"[DEBUG] Résultat final: {repr(result)}")
        return result
    
    @staticmethod
    def latex_to_image(texte: str, filename: str, width: int = 520, height: int = 600):
        """Convertit le texte contenant du LaTeX en image bien formatée avec largeur Discord"""
        fig = None
        try:
            # Extraire et formatter le texte LaTeX en préservant les retours à la ligne
            formatted_text = LatexService.extract_and_format_latex(texte)
            
            # Si le texte formaté est vide, on utilise le texte original
            if not formatted_text.strip():
                formatted_text = texte
            
            # Largeur fixe similaire à un message Discord (environ 520px)
            # Hauteur adaptative basée sur le nombre de lignes
            lines_count = formatted_text.count('\n') + 1
            
            # Ajuster la taille pour correspondre à Discord
            fig_width = 6.5  # Largeur fixe équivalent à un message Discord
            fig_height = max(2, lines_count * 0.4 + 1)  # Hauteur adaptative
            fontsize = 11  # Taille de police similaire à Discord
            
            # Créer une figure adaptée
            fig, ax = plt.subplots(figsize=(fig_width, fig_height))
            
            # Configurer l'affichage avec une gestion d'erreur pour LaTeX
            try:
                ax.text(0.05, 0.95, formatted_text, fontsize=fontsize, ha='left', va='top', 
                       transform=ax.transAxes, wrap=False, linespacing=1.2,
                       bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.8))
            except Exception as latex_error:
                print(f"[WARNING] Erreur LaTeX, utilisation du texte sans formatage: {latex_error}")
                # Fallback: utiliser le texte original sans LaTeX
                plain_text = re.sub(r'\\[a-zA-Z]+\{.*?\}', '', texte)  # Supprimer les commandes LaTeX
                plain_text = re.sub(r'[\$\\]', '', plain_text)  # Supprimer $ et \
                ax.text(0.05, 0.95, plain_text, fontsize=fontsize, ha='left', va='top', 
                       transform=ax.transAxes, wrap=False, linespacing=1.2,
                       bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.8))
            
            ax.axis('off')
            
            # Sauvegarder avec fond blanc
            plt.savefig(filename, bbox_inches='tight', dpi=150, facecolor='white', 
                       edgecolor='none', pad_inches=0.2)
            plt.close(fig)
            
            return True
            
        except Exception as e:
            print(f"Erreur lors de la génération LaTeX: {e}")
            if fig is not None:
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