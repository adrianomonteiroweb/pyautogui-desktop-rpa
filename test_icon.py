import pyautogui as pay
import time
import os
from main import DesktopIconAutomation, AutomationConfig

def test_icon_detection():
    """Testa a detecção do ícone sem clicar"""
    
    config = AutomationConfig(
        confidence=0.9,
        double_click_interval=0.1,
        startup_delay=2,
        images_folder="images"
    )
    
    automation = DesktopIconAutomation(config)
    image_path = automation._get_image_path("icon.png")
    
    print("=== TESTE DE DETECÇÃO DO ÍCONE ===")
    print(f"Procurando pela imagem: {image_path}")
    
    if not os.path.exists(image_path):
        print("❌ Arquivo icon.png não encontrado!")
        return
    
    print("Aguardando 2 segundos...")
    time.sleep(2)
    
    # Encontra todas as ocorrências
    locations = automation._find_all_image_locations(image_path)
    
    if not locations:
        print("❌ Ícone não encontrado na tela")
        print("Dicas:")
        print("- Certifique-se que o ícone está visível")
        print("- Verifique se a imagem icon.png corresponde ao ícone atual")
        print("- Tente diminuir a confiança (confidence)")
    else:
        print(f"✅ Encontradas {len(locations)} ocorrência(s):")
        for i, location in enumerate(locations, 1):
            center = pay.center(location)
            print(f"  {i}. Posição: {center}")
            print(f"     Área: {location}")
        
        # Destaca a primeira ocorrência sem clicar
        if locations:
            center = pay.center(locations[0])
            print(f"\n🎯 Primeira ocorrência será clicada em: {center}")

if __name__ == "__main__":
    test_icon_detection()