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
            r'\$.*?\$',  # Math inline: $...$
            r'\\\[.*?\\\]',  # Math display: \[...\]
            r'\\\(.*?\\\)',  # Math inline: \(...\)
            r'\\begin\{.*?\}',  # Environnements: \begin{...}
            r'\\[a-zA-Z]+',  # Commandes LaTeX: \command
            r'\\frac\{.*?\}\{.*?\}',  # Fractions
            r'\^[{]?.*?[}]?',  # Exposants
            r'_[{]?.*?[}]?',  # Indices
        ]

        for pattern in latex_patterns:
            if re.search(pattern, text, re.DOTALL):
                return True
        return False

    @staticmethod
    def ensure_math_mode(text):
        # Utiliser une expression régulière pour trouver les commandes \mathbb non entourées de $
        pattern = r'(?<!\\)\\(mathbb)\{[^$\}]*\}(?!\$)'
        # Ajouter des $ autour des commandes \mathbb non entourées
        return re.sub(pattern, r'$\1$', text)

    @staticmethod
    def extract_and_clean_latex(text):
        # Convertir \( ... \) et \[ ... \] en $ ... $
        text = re.sub(r'\\\((.*?)\\\)', r'$\1$', text, flags=re.DOTALL)
        text = re.sub(r'\\\[(.*?)\\\]', r'$\1$', text, flags=re.DOTALL)
        # Nettoyer espaces multiples sauf retours à la ligne
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r' *\n *', '\n', text)
        # Supprimer lignes contenant uniquement un $
        lines = text.split('\n')
        lines = [line for line in lines if line.strip() != '$']
        text = '\n'.join(lines)
        # Supprimer les $ $ inutiles ou vides
        text = re.sub(r'\$\s*\$', '', text)
        # Convertir $$ ... $$ en $ ... $ (inline)
        text = re.sub(r'\$\$(.*?)\$\$', r'$\1$', text, flags=re.DOTALL)
        # Corriger triples ou plus de $ : $$$...$$$ → $...$
        text = re.sub(r'\${3,}(.*?)\${3,}', r'$\1$', text, flags=re.DOTALL)
        # Équilibrer $ si impair
        if text.count('$') % 2 != 0:
            if text.endswith('$'):
                text = text[:-1]
            elif text.startswith('$'):
                text = text[1:]
        # Fusionner les mathématiques éclatées : ex. $ ... $ \frac{...} $$
        pattern = re.compile(
            r'(\$[^\$]*?\$)\s*(\\\\?[a-zA-Z]+\{.*?\})\s*(\${1,})',
            flags=re.DOTALL
        )

        def fusion_math(match):
            math1 = match.group(1)[1:-1].strip()  # contenu sans $
            cmd = match.group(2).strip()  # commande LaTeX comme \frac{...}
            # On remet tout dans un seul inline math
            return f"${math1} {cmd}$"

        text = pattern.sub(fusion_math, text)
        return text.strip()

    @staticmethod
    def auto_math_wrap_lines(text):
        """
        N'ajoute des $...$ qu'autour des vraies expressions mathématiques,
        sans inclure les parties en texte avec accents.
        """
        def safe_wrap_math(match):
            content = match.group(0)
            # On ne wrappe que les parties avec des formules, pas le texte normal
            return f"${content}$"

        # Exemple : transformer uniquement les fractions ou intégrales hors math mode
        math_expr = r'(\\(frac|int|sum|lim|sqrt|to|mathbb)[^$]*)'
        return re.sub(math_expr, safe_wrap_math, text)

    @staticmethod
    def latex_to_image(texte: str, filename: str, width: int = 460, height: int = 600):
        """Convertit le texte contenant du LaTeX en image bien formatée avec largeur Discord"""
        fig = None
        try:
            # Extraire et formatter le texte LaTeX en préservant les retours à la ligne
            formatted_text = LatexService.extract_and_clean_latex(texte)
            formatted_text = LatexService.auto_math_wrap_lines(formatted_text)
            formatted_text = LatexService.ensure_math_mode(formatted_text)
            # Si le texte formaté est vide, on utilise le texte original
            if not formatted_text.strip():
                formatted_text = texte

            # Largeur optimisée pour Discord (460px ~ largeur message Discord standard)
            # Hauteur adaptative basée sur le nombre de lignes
            lines_count = formatted_text.count('\n') + 1

            # Dimensions optimisées pour correspondre exactement à Discord
            # Discord utilise environ 460px de largeur pour les messages
            fig_width_pixels = width  # Utiliser la largeur passée en paramètre (460px par défaut)
            fig_width_inches = fig_width_pixels / 100  # Conversion approximative px vers pouces
            fig_height = max(1.5, lines_count * 0.35 + 0.8)  # Hauteur adaptative plus compacte
            fontsize = 12  # Taille de police ajustée pour Discord

            plt.rcParams['text.latex.preamble'] = r'\usepackage[utf8]{inputenc}\usepackage{amsmath}\usepackage{amssymb}'
            plt.rcParams['text.usetex'] = True  # utilise le moteur latex
            # Créer une figure adaptée avec les dimensions
            fig, ax = plt.subplots(figsize=(fig_width_inches, fig_height))

            # Configurer l'affichage avec une gestion d'erreur pour LaTeX
            try:
                print("[DEBUG] TEXTE FINAL :", repr(formatted_text))
                ax.text(0.05, 0.95, formatted_text, fontsize=fontsize, ha='left', va='top',
                        transform=ax.transAxes, wrap=True, linespacing=1.3,
                        bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.8))
            except Exception as latex_error:
                print(f"[WARNING] Erreur LaTeX, utilisation du texte sans formatage: {latex_error}")
                # Fallback: utiliser le texte original sans LaTeX
                plain_text = re.sub(r'\\[a-zA-Z]+\{.*?\}', '', texte)  # Supprimer les commandes LaTeX
                plain_text = re.sub(r'[\$\\]', '', plain_text)  # Supprimer $ et \
                ax.text(0.05, 0.95, plain_text, fontsize=fontsize, ha='left', va='top',
                        transform=ax.transAxes, wrap=True, linespacing=1.3,
                        bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.8))

            ax.axis('off')

            # Sauvegarder avec paramètres optimisés pour Discord
            # DPI réduit pour équilibrer qualité/taille, dimensions exactes pour Discord
            plt.savefig(filename, bbox_inches='tight', dpi=120, facecolor='white',
                        edgecolor='none', pad_inches=0.15)
            plt.close(fig)

            return True

        except Exception as e:
            print(f"Erreur lors de la génération LaTeX: {e}")
            if fig is not None:
                plt.close(fig)
            return False

latex_service = LatexService()
