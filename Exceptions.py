class SyntaxeInvalide(Exception):
    def __init__(self):
        super().__init__("❌ **Syntaxe incorrecte !**\n\n"
            "**Utilisation :** `!quizz <difficulté> <spécialité>`\n"
            "• **Difficulté :** 1 (facile), 2 (moyen), 3 (difficile)\n"
            "• **Spécialités :** Maths, NSI, Physique-Chimie, SVT, SES, HGGSP, random\n\n"
            "**Exemples :**\n"
            "`!quizz 2 Maths` - Question de difficulté moyenne en Maths\n"
            "`!quizz 1 random` - Question facile dans une spécialité aléatoire")
        
class DifficulteInvalide(Exception):
    def __init__(self):
        super().__init__("❌ **Difficulté invalide !**\n\n"
                "La difficulté doit être :\n"
                "• **1** pour facile\n"
                "• **2** pour moyen\n"
                "• **3** pour difficile\n\n"
                "**Exemple :** `!quizz 2 Maths`")
        



class SpecialiteInvalide(Exception):
    def __init__(self):
        super().__init__("❌ **Spécialité invalide !**\n\n"
                "**Spécialités disponibles :**\n"
                "• Maths\n"
                "• NSI\n"
                "• Physique-Chimie\n"
                "• SVT\n"
                "• SES\n"
                "• HGGSP\n"
                "• random (spécialité aléatoire)\n\n"
                "**Syntaxe :** `!quizz <difficulté> <spécialité>`\n"
                "**Exemple :** `!quizz 2 NSI`")
        

