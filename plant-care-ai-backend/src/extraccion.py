"""
Módulo de Extracción de Datos
Extrae información de documentos de texto sobre cuidado de plantas
"""
import os
from typing import List
from pathlib import Path


class DataExtractor:
    """Extrae texto de archivos de documentación sobre plantas"""
    
    def __init__(self, data_dir: str = "data/plantas"):
        self.data_dir = Path(data_dir)
        
    def extract_from_file(self, filepath: str) -> str:
        """
        Extrae texto de un archivo
        
        Args:
            filepath: Ruta al archivo
            
        Returns:
            Contenido del archivo como string
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except Exception as e:
            print(f"Error al leer {filepath}: {e}")
            return ""
    
    def extract_all_documents(self) -> List[dict]:
        """
        Extrae todos los documentos del directorio de datos
        
        Returns:
            Lista de diccionarios con 'filename' y 'content'
        """
        documents = []
        
        if not self.data_dir.exists():
            print(f"Directorio {self.data_dir} no existe")
            return documents
        
        # Buscar archivos .txt y .md
        for ext in ['*.txt', '*.md']:
            for filepath in self.data_dir.rglob(ext):
                content = self.extract_from_file(filepath)
                if content:
                    documents.append({
                        'filename': filepath.name,
                        'filepath': str(filepath),
                        'content': content
                    })
                    print(f"✓ Extraído: {filepath.name}")
        
        print(f"\nTotal documentos extraídos: {len(documents)}")
        return documents


if __name__ == "__main__":
    # Test
    extractor = DataExtractor()
    docs = extractor.extract_all_documents()
    for doc in docs[:2]:
        print(f"\n{doc['filename']}: {len(doc['content'])} caracteres")
