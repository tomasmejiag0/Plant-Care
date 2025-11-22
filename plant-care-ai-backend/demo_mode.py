"""
Modo Demo - Sistema que funciona completamente sin Gemini
Útil para demostraciones cuando se ha agotado la quota o no hay API key
"""
import json
from typing import Dict, List

# Respuestas de ejemplo predefinidas para demostración
DEMO_RESPONSES = {
    "como cuido una suculenta": """Las suculentas son plantas fascinantes que almacenan agua en sus hojas y tallos, lo que las hace muy resistentes a la sequía. Son perfectas para principiantes porque requieren muy poco mantenimiento.

Para cuidarlas correctamente, aquí tienes lo más importante:

• Riego: Solo riega cuando la tierra esté completamente seca. En invierno puede ser cada 2-4 semanas, y en verano cada 1-2 semanas. El exceso de agua es el error más común que cometen las personas.

• Luz: Necesitan al menos 6 horas de luz solar directa al día. Si las tienes en interior, colócalas cerca de una ventana muy soleada orientada al sur.

• Suelo: Usa una mezcla especial para cactus o suculentas que tenga excelente drenaje. Puedes agregar perlita o arena gruesa para mejorarlo.

• Temperatura: La mayoría prefiere temperaturas entre 15-25°C. Evita exponerlas a temperaturas bajo 10°C.

• Propagación: Puedes propagarlas fácilmente cortando una hoja o tallo, dejándolo secar unos días, y luego plantándolo en tierra húmeda. En 4-12 semanas deberías ver raíces nuevas.

¿Te gustaría saber más sobre algún aspecto específico del cuidado de suculentas?""",

    "como cuido un cactus": """Los cactus son plantas increíblemente resistentes que pueden sobrevivir en condiciones extremas. Son ideales para personas que viajan mucho o tienen poco tiempo para el cuidado de plantas.

Aspectos clave del cuidado de cactus:

• Riego: Mucho menos frecuente que otras plantas. En verano, riega cada 2-3 semanas cuando la tierra esté completamente seca. En invierno, puede ser cada mes o incluso menos.

• Luz: Necesitan mucha luz solar directa. Colócalos en el lugar más soleado de tu casa, preferiblemente cerca de una ventana orientada al sur o oeste.

• Suelo: Requieren tierra muy bien drenada. Usa mezcla especial para cactus o agrega arena y perlita a la tierra normal.

• Maceta: Asegúrate de que tenga agujeros de drenaje. Los cactus odian el agua estancada.

• Temperatura: La mayoría tolera temperaturas entre 10-30°C. Algunos pueden sobrevivir hasta 5°C si están secos.

¿Te gustaría saber más sobre propagación o problemas comunes de cactus?""",

    "que plantas son buenas para interior": """Hay muchas plantas excelentes para interiores que son fáciles de cuidar. Aquí tienes algunas recomendaciones:

Plantas de interior populares:

• Pothos (Epipremnum aureum): Muy tolerante, crece rápido, perfecta para principiantes. Tolera poca luz y riego irregular.

• Sansevieria (Lengua de Suegra): Extremadamente resistente, puede sobrevivir semanas sin agua. Ideal para oficinas o personas ocupadas.

• Monstera Deliciosa: Muy popular por sus hojas grandes y decorativas. Necesita luz indirecta brillante y riego moderado.

• Helechos: Perfectos para baños o lugares con alta humedad. Necesitan tierra siempre húmeda pero no empapada.

• Suculentas: Requieren muy poco mantenimiento, perfectas para ventanas soleadas.

Todas estas plantas son relativamente fáciles de cuidar y pueden adaptarse bien a condiciones de interior. ¿Te gustaría saber más sobre alguna específica?""",

    "por que se ponen amarillas las hojas": """Las hojas amarillas pueden tener varias causas. Aquí te explico las más comunes:

Causas principales de hojas amarillas:

• Exceso de riego: La causa más común. Las raíces se ahogan y no pueden absorber nutrientes. Solución: Deja secar la tierra completamente antes de regar de nuevo.

• Falta de riego: Si la planta está muy seca, las hojas se ponen amarillas y se caen. Solución: Riega cuando los primeros centímetros de tierra estén secos.

• Falta de luz: Las plantas necesitan luz para hacer fotosíntesis. Sin suficiente luz, las hojas se vuelven amarillas. Solución: Mueve la planta a un lugar más iluminado.

• Falta de nutrientes: Si la planta no recibe suficientes nutrientes, las hojas pueden volverse amarillas. Solución: Fertiliza durante la temporada de crecimiento.

• Envejecimiento natural: Las hojas viejas se vuelven amarillas y se caen, esto es normal.

Para identificar la causa, observa si las hojas amarillas están en la parte inferior (normal) o superior (problema), y revisa la frecuencia de riego.

¿Tu planta tiene hojas amarillas? Describe más detalles y te ayudo a identificar la causa.""",

    "cada cuanto debo regar mis plantas": """La frecuencia de riego depende del tipo de planta, el tamaño de la maceta, la temperatura y la humedad. Aquí tienes una guía general:

Frecuencia de riego por tipo de planta:

• Suculentas y cactus: Cada 2-4 semanas en invierno, cada 1-2 semanas en verano. Siempre verifica que la tierra esté completamente seca.

• Plantas de interior comunes (Pothos, Monstera): Cada 5-10 días, cuando los primeros 2-3 cm de tierra estén secos.

• Plantas tropicales: Cada 3-7 días, mantén la tierra húmeda pero no empapada.

• Helechos: Cada 2-4 días, necesitan tierra siempre húmeda.

Regla general: Es mejor regar menos que más. La mayoría de plantas mueren por exceso de agua, no por falta de ella.

Método para verificar: Introduce el dedo 2-3 cm en la tierra. Si está seca, es momento de regar. Si está húmeda, espera unos días más.

¿Qué tipo de planta tienes? Puedo darte recomendaciones más específicas.""",

    "que pasa si arranco una hoja sin querer de mi suculenta": """No te preocupes, arrancar una hoja accidentalmente de tu suculenta no es el fin del mundo. De hecho, las suculentas son muy resistentes y pueden recuperarse fácilmente.

Lo que debes hacer:

• No te preocupes: Las suculentas pueden perder hojas y seguir creciendo perfectamente. Es parte de su ciclo natural.

• Deja que cicatrice: Si la hoja se desprendió completamente, déjala secar unos días antes de intentar propagarla (si quieres).

• Propaga la hoja (opcional): Si la hoja está completa, puedes usarla para crear una nueva planta. Colócala sobre tierra seca y espera a que desarrolle raíces (puede tomar 2-4 semanas).

• Cuida la planta original: La suculenta madre seguirá creciendo normalmente. Solo asegúrate de que la herida no se infecte manteniendo la tierra seca por unos días.

• Evita regar inmediatamente: Si hay una herida visible, espera 2-3 días antes de regar para que cicatrice.

Las suculentas son muy adaptables y perder una hoja accidentalmente no afectará su salud general. De hecho, muchas personas propagan suculentas intencionalmente arrancando hojas.

¿Te gustaría saber más sobre cómo propagar suculentas o cómo cuidar una suculenta después de perder hojas?""",

    "como trasplanto una planta": """Trasplantar una planta puede parecer intimidante, pero siguiendo estos pasos será sencillo:

Pasos para trasplantar:

1. Elige el momento adecuado: La mejor época es primavera o principios de verano, cuando la planta está en crecimiento activo.

2. Selecciona la maceta nueva: Debe ser solo 2-5 cm más grande que la actual. Demasiado grande puede causar problemas de drenaje.

3. Prepara la nueva maceta: Coloca una capa de drenaje (piedras o grava) en el fondo. Luego agrega tierra fresca.

4. Retira la planta: Riega ligeramente la planta el día anterior para facilitar el proceso. Saca la planta con cuidado, sosteniendo la base del tallo.

5. Inspecciona las raíces: Si están muy enrolladas (root-bound), suavemente desenreda algunas. Si hay raíces podridas, córtalas.

6. Planta en la nueva maceta: Coloca la planta en el centro y agrega tierra alrededor, presionando suavemente.

7. Riega moderadamente: Riega después de trasplantar, pero no en exceso. La planta necesita adaptarse.

8. Ubicación: Mantén la planta en un lugar con luz indirecta durante unos días para que se adapte.

¿Necesitas ayuda con algún paso específico o tipo de planta en particular?"""
}

def get_demo_response(query: str) -> str:
    """
    Obtiene una respuesta de demostración basada en la consulta
    Si no encuentra una respuesta exacta, busca palabras clave relacionadas
    """
    query_lower = query.lower().strip()
    
    # Buscar respuesta exacta o parcial
    for key, response in DEMO_RESPONSES.items():
        if key in query_lower or query_lower in key:
            return response
    
    # Buscar por palabras clave relacionadas
    keywords_mapping = {
        'arrancar': 'que pasa si arranco una hoja sin querer de mi suculenta',
        'hoja caida': 'que pasa si arranco una hoja sin querer de mi suculenta',
        'perder hoja': 'que pasa si arranco una hoja sin querer de mi suculenta',
        'hoja rota': 'que pasa si arranco una hoja sin querer de mi suculenta',
        'suculenta': 'como cuido una suculenta',
        'cactus': 'como cuido un cactus',
        'interior': 'que plantas son buenas para interior',
        'amarilla': 'por que se ponen amarillas las hojas',
        'amarillas': 'por que se ponen amarillas las hojas',
        'regar': 'cada cuanto debo regar mis plantas',
        'riego': 'cada cuanto debo regar mis plantas',
        'trasplantar': 'como trasplanto una planta',
        'trasplante': 'como trasplanto una planta',
        'propagar': 'como cuido una suculenta',  # Menciona propagación
    }
    
    # Buscar palabras clave en la consulta
    for keyword, response_key in keywords_mapping.items():
        if keyword in query_lower:
            if response_key in DEMO_RESPONSES:
                return DEMO_RESPONSES[response_key]
    
    # Respuesta genérica mejorada si no encuentra match
    return """Encontré información relevante sobre tu pregunta en mi base de conocimiento. 

Puedo ayudarte con temas como:
• Cuidado de suculentas o cactus
• Problemas comunes de plantas (hojas amarillas, plagas, hojas caídas, etc.)
• Frecuencia de riego
• Trasplante y propagación
• Plantas de interior recomendadas
• Qué hacer si se cae o se rompe una hoja

¿Te gustaría que te explique alguno de estos temas en detalle? Por ejemplo, puedes preguntar:
- "Como cuido una suculenta"
- "Por que se ponen amarillas las hojas"
- "Cada cuanto debo regar mis plantas"
"""

if __name__ == "__main__":
    # Test
    print("Modo Demo - Respuestas predefinidas")
    print("=" * 60)
    
    test_queries = [
        "como cuido una suculenta",
        "por que se ponen amarillas las hojas",
        "cada cuanto debo regar"
    ]
    
    for query in test_queries:
        print(f"\nPregunta: {query}")
        print(f"Respuesta: {get_demo_response(query)[:100]}...")

