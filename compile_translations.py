"""
Script para compilar archivos .po a .mo sin necesidad de gettext
"""
import polib
from pathlib import Path

def compile_messages():
    locale_path = Path(__file__).parent / 'locale'
    
    for po_file in locale_path.rglob('*.po'):
        mo_file = po_file.with_suffix('.mo')
        print(f"Compilando {po_file} -> {mo_file}")
        
        try:
            po = polib.pofile(str(po_file))
            po.save_as_mofile(str(mo_file))
            print(f"✓ Compilado exitosamente")
        except Exception as e:
            print(f"✗ Error: {e}")

if __name__ == '__main__':
    compile_messages()
    print("\n¡Compilación completada!")
