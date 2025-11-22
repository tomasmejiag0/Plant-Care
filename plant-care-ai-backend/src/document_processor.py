"""
Procesador Inteligente de Documentos
Analiza documentos encontrados y genera respuestas contextuales sin LLM
"""
import re
from typing import List, Dict


class DocumentProcessor:
    """Procesa documentos encontrados y genera respuestas contextuales"""
    
    def __init__(self):
        self.question_keywords = {
            'que pasa si': ['consecuencia', 'resultado', 'efecto', 'solución', 'hacer'],
            'como': ['paso', 'método', 'proceso', 'instrucción', 'procedimiento'],
            'por que': ['causa', 'razón', 'motivo', 'explicación'],
            'cada cuanto': ['frecuencia', 'periodo', 'intervalo', 'tiempo'],
            'que': ['definición', 'tipo', 'clase', 'característica'],
            'cuando': ['momento', 'época', 'tiempo', 'condición']
        }
    
    def extract_relevant_info(self, query: str, documents: List[Dict]) -> str:
        """
        Extrae información relevante de documentos basándose en la pregunta
        
        Args:
            query: Pregunta del usuario
            documents: Lista de documentos encontrados con relevancia
            
        Returns:
            Respuesta estructurada basada en los documentos
        """
        if not documents:
            return None
        
        query_lower = query.lower().strip()
        
        # Limpiar y combinar documentos
        cleaned_docs = []
        for doc in documents[:5]:  # Top 5 documentos
            doc_text = self._clean_document(doc['text'])
            if doc_text:
                cleaned_docs.append({
                    'text': doc_text,
                    'score': doc['relevance_score'],
                    'source': doc.get('source', 'desconocido')
                })
        
        if not cleaned_docs:
            return None
        
        # Analizar tipo de pregunta
        question_type = self._identify_question_type(query_lower)
        
        # Extraer información según el tipo de pregunta
        if question_type == 'que_pasa_si':
            return self._answer_what_happens_if(query_lower, cleaned_docs)
        elif question_type == 'como':
            return self._answer_how_to(query_lower, cleaned_docs)
        elif question_type == 'por_que':
            return self._answer_why(query_lower, cleaned_docs)
        elif question_type == 'cada_cuanto':
            return self._answer_frequency(query_lower, cleaned_docs)
        elif question_type == 'que':
            return self._answer_what(query_lower, cleaned_docs)
        else:
            return self._answer_general(query_lower, cleaned_docs)
    
    def _clean_document(self, text: str) -> str:
        """Limpia el texto del documento"""
        # Eliminar markdown
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'#{1,6}\s+', '', text)
        text = re.sub(r'\.\.\.+', '', text)
        
        # Eliminar líneas muy cortas o solo números
        lines = [l.strip() for l in text.split('\n') 
                if l.strip() and len(l.strip()) > 10 
                and not re.match(r'^[\d\.\-\•\*]+$', l.strip())]
        
        return ' '.join(lines)
    
    def _identify_question_type(self, query: str) -> str:
        """Identifica el tipo de pregunta"""
        if 'que pasa si' in query or 'que pasa cuando' in query:
            return 'que_pasa_si'
        elif query.startswith('como'):
            return 'como'
        elif query.startswith('por que') or query.startswith('porque'):
            return 'por_que'
        elif 'cada cuanto' in query or 'cada cuánto' in query:
            return 'cada_cuanto'
        elif query.startswith('que') or query.startswith('qué'):
            return 'que'
        else:
            return 'general'
    
    def _answer_what_happens_if(self, query: str, docs: List[Dict]) -> str:
        """Responde preguntas tipo 'que pasa si'"""
        # Buscar palabras clave relacionadas con la pregunta
        query_words = set(query.split())
        
        # Buscar información sobre consecuencias, soluciones, efectos
        relevant_sentences = []
        for doc in docs:
            doc_text = doc['text'].lower()
            sentences = doc['text'].split('.')
            
            for sentence in sentences:
                sentence_lower = sentence.lower().strip()
                # Buscar oraciones que mencionen palabras de la pregunta
                if any(word in sentence_lower for word in query_words if len(word) > 3):
                    # Buscar palabras relacionadas con consecuencias
                    if any(kw in sentence_lower for kw in ['pasa', 'ocurre', 'resultado', 'efecto', 
                                                           'solución', 'hacer', 'debe', 'puede', 
                                                           'debería', 'recomienda', 'importante']):
                        if 30 < len(sentence.strip()) < 300:
                            relevant_sentences.append(sentence.strip())
        
        if relevant_sentences:
            # Combinar las más relevantes
            response = ' '.join(relevant_sentences[:4])
            response = re.sub(r'\s+', ' ', response)
            if len(response) > 800:
                response = response[:800] + '...'
            return response
        
        return None
    
    def _answer_how_to(self, query: str, docs: List[Dict]) -> str:
        """Responde preguntas tipo 'como'"""
        query_words = set(query.split())
        relevant_sentences = []
        context_sentences = []
        
        # Identificar el tema principal (suculenta, cactus, etc.)
        plant_type = None
        for word in ['suculenta', 'cactus', 'planta', 'orquidea', 'helecho', 'bonsai']:
            if word in query.lower():
                plant_type = word
                break
        
        for doc in docs:
            doc_text = doc['text']
            doc_lower = doc_text.lower()
            sentences = doc_text.split('.')
            
            # Buscar oraciones relevantes con contexto
            for i, sentence in enumerate(sentences):
                sentence_lower = sentence.lower().strip()
                sentence_stripped = sentence.strip()
                
                # Filtrar oraciones muy cortas o fragmentos técnicos
                if len(sentence_stripped) < 20:
                    continue
                
                # Filtrar fragmentos técnicos aislados
                if any(fragment in sentence_stripped for fragment in ['Corte limpio horizontal ambos', 
                                                                      'Sacar de maceta cuidadosamente']):
                    # Solo incluir si tiene contexto adicional
                    if len(sentence_stripped) < 50:
                        continue
                
                # Buscar oraciones que mencionen palabras clave de la pregunta
                has_query_words = any(word in sentence_lower for word in query_words if len(word) > 3)
                
                # Buscar oraciones con palabras clave de instrucciones
                has_instruction_keywords = any(kw in sentence_lower for kw in [
                    'paso', 'método', 'proceso', 'instrucción', 'debe', 'debería', 
                    'necesita', 'requiere', 'importante', 'recomienda', 'cuidar',
                    'riego', 'luz', 'suelo', 'agua', 'maceta', 'trasplante'
                ])
                
                # Si es sobre el tipo de planta específico, darle más prioridad
                has_plant_type = plant_type and plant_type in sentence_lower
                
                if has_query_words and (has_instruction_keywords or has_plant_type):
                    if 30 < len(sentence_stripped) < 400:
                        relevant_sentences.append({
                            'text': sentence_stripped,
                            'has_plant': has_plant_type,
                            'score': doc['score']
                        })
                
                # También capturar oraciones de contexto (antes y después)
                if has_query_words and i > 0:
                    prev_sentence = sentences[i-1].strip()
                    if 30 < len(prev_sentence) < 200 and prev_sentence not in relevant_sentences:
                        context_sentences.append(prev_sentence)
        
        # Ordenar por relevancia (plant type primero, luego por score del documento)
        relevant_sentences.sort(key=lambda x: (not x['has_plant'], -x['score']))
        
        if relevant_sentences:
            # Construir respuesta con contexto
            response_parts = []
            
            # Agregar introducción si es sobre un tipo específico de planta
            if plant_type:
                plant_name = plant_type.capitalize()
                if plant_type == 'cactus':
                    response_parts.append(f"Los cactus son plantas muy resistentes que requieren cuidados específicos.")
                elif plant_type == 'suculenta':
                    response_parts.append(f"Las suculentas son plantas que almacenan agua y son perfectas para principiantes.")
            
            # Agregar oraciones relevantes
            for sent_info in relevant_sentences[:6]:
                sent_text = sent_info['text']
                # Evitar duplicados
                if sent_text not in ' '.join(response_parts):
                    response_parts.append(sent_text)
            
            # Agregar contexto adicional si la respuesta es muy corta
            if len(' '.join(response_parts)) < 200 and context_sentences:
                for ctx in context_sentences[:2]:
                    if ctx not in ' '.join(response_parts):
                        response_parts.append(ctx)
            
            response = ' '.join(response_parts)
            response = re.sub(r'\s+', ' ', response)
            
            # Asegurar que la respuesta tenga suficiente contenido
            if len(response) < 100:
                # Si es muy corta, intentar agregar más contexto del documento más relevante
                if docs:
                    best_doc = docs[0]['text']
                    # Extraer párrafos más largos
                    paragraphs = [p.strip() for p in best_doc.split('\n\n') if len(p.strip()) > 100]
                    if paragraphs:
                        response += ' ' + paragraphs[0][:300]
                        response = re.sub(r'\s+', ' ', response)
            
            if len(response) > 1200:
                response = response[:1200] + '...'
            
            return response
        
        return None
    
    def _answer_why(self, query: str, docs: List[Dict]) -> str:
        """Responde preguntas tipo 'por que'"""
        query_words = set(query.split())
        relevant_sentences = []
        
        for doc in docs:
            sentences = doc['text'].split('.')
            for sentence in sentences:
                sentence_lower = sentence.lower().strip()
                if any(word in sentence_lower for word in query_words if len(word) > 3):
                    if any(kw in sentence_lower for kw in ['causa', 'razón', 'motivo', 'porque',
                                                          'debido', 'provoca', 'ocasiona']):
                        if 30 < len(sentence.strip()) < 300:
                            relevant_sentences.append(sentence.strip())
        
        if relevant_sentences:
            response = ' '.join(relevant_sentences[:4])
            response = re.sub(r'\s+', ' ', response)
            if len(response) > 800:
                response = response[:800] + '...'
            return response
        
        return None
    
    def _answer_frequency(self, query: str, docs: List[Dict]) -> str:
        """Responde preguntas sobre frecuencia"""
        relevant_sentences = []
        
        for doc in docs:
            sentences = doc['text'].split('.')
            for sentence in sentences:
                sentence_lower = sentence.lower().strip()
                if any(kw in sentence_lower for kw in ['cada', 'semana', 'día', 'días', 'vez',
                                                       'frecuencia', 'periodo', 'intervalo']):
                    if 30 < len(sentence.strip()) < 300:
                        relevant_sentences.append(sentence.strip())
        
        if relevant_sentences:
            response = ' '.join(relevant_sentences[:4])
            response = re.sub(r'\s+', ' ', response)
            if len(response) > 800:
                response = response[:800] + '...'
            return response
        
        return None
    
    def _answer_what(self, query: str, docs: List[Dict]) -> str:
        """Responde preguntas tipo 'que'"""
        query_words = set(query.split())
        relevant_sentences = []
        
        for doc in docs:
            sentences = doc['text'].split('.')
            for sentence in sentences:
                sentence_lower = sentence.lower().strip()
                if any(word in sentence_lower for word in query_words if len(word) > 3):
                    if 30 < len(sentence.strip()) < 300:
                        relevant_sentences.append(sentence.strip())
        
        if relevant_sentences:
            response = ' '.join(relevant_sentences[:5])
            response = re.sub(r'\s+', ' ', response)
            if len(response) > 1000:
                response = response[:1000] + '...'
            return response
        
        return None
    
    def _answer_general(self, query: str, docs: List[Dict]) -> str:
        """Responde preguntas generales"""
        query_words = set(query.split())
        relevant_sentences = []
        
        for doc in docs:
            sentences = doc['text'].split('.')
            for sentence in sentences:
                sentence_lower = sentence.lower().strip()
                # Buscar oraciones que contengan palabras de la pregunta
                matches = sum(1 for word in query_words if word in sentence_lower and len(word) > 3)
                if matches >= 1 and 30 < len(sentence.strip()) < 300:
                    relevant_sentences.append((sentence.strip(), matches))
        
        # Ordenar por relevancia (más matches = más relevante)
        relevant_sentences.sort(key=lambda x: x[1], reverse=True)
        
        if relevant_sentences:
            response = ' '.join([s[0] for s in relevant_sentences[:5]])
            response = re.sub(r'\s+', ' ', response)
            if len(response) > 1000:
                response = response[:1000] + '...'
            return response
        
        return None

