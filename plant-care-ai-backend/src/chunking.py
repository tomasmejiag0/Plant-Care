"""
Módulo de Chunking (Segmentación)
Divide documentos largos en chunks más pequeños para procesamiento
"""
from typing import List


class TextChunker:
    """Divide texto en chunks semánticos"""
    
    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        """
        Args:
            chunk_size: Tamaño aproximado de cada chunk en caracteres
            overlap: Cantidad de caracteres de overlap entre chunks
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_by_sentences(self, text: str) -> List[str]:
        """
        Divide texto en chunks respetando límites de oraciones
        
        Args:
            text: Texto a dividir
            
        Returns:
            Lista de chunks
        """
        # Dividir por oraciones (aproximado)
        sentences = text.replace('.\n', '.|').replace('. ', '.|').split('|')
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # Si agregar esta oración excede el tamaño, guardar chunk actual
            if len(current_chunk) + len(sentence) > self.chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                
                # Comenzar nuevo chunk con overlap
                words = current_chunk.split()
                overlap_text = ' '.join(words[-self.overlap:]) if len(words) > self.overlap else current_chunk
                current_chunk = overlap_text + " " + sentence
            else:
                current_chunk += " " + sentence
        
        # Agregar último chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def chunk_document(self, document: dict) -> List[dict]:
        """
        Divide un documento en chunks
        
        Args:
            document: Dict con 'filename' y 'content'
            
        Returns:
            Lista de chunks con metadata
        """
        text = document['content']
        chunks = self.chunk_by_sentences(text)
        
        result = []
        for i, chunk in enumerate(chunks):
            result.append({
                'chunk_id': f"{document['filename']}_chunk_{i}",
                'source_file': document['filename'],
                'chunk_index': i,
                'text': chunk,
                'char_count': len(chunk)
            })
        
        return result


if __name__ == "__main__":
    # Test
    chunker = TextChunker(chunk_size=300, overlap=30)
    
    test_doc = {
        'filename': 'test.txt',
        'content': """Las suculentas son plantas que almacenan agua en sus hojas. 
        Requieren riego moderado, aproximadamente cada 10-14 días. 
        Prefieren luz indirecta brillante. El exceso de riego causa pudrición de raíces. 
        Las hojas amarillas pueden indicar exceso de agua."""
    }
    
    chunks = chunker.chunk_document(test_doc)
    print(f"Chunks creados: {len(chunks)}")
    for chunk in chunks:
        print(f"\n{chunk['chunk_id']}: {chunk['char_count']} chars")
        print(chunk['text'][:100])
