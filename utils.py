import time
import uuid

def for_each(items, process_func, max_retries=1, retry_delay=5, item_name_func=None):
    processed_ids = set()
    
    for item in items:
        if not isinstance(item, dict):
            item = {"data": item, "id": str(uuid.uuid4())}
        elif 'id' not in item:
            item['id'] = str(uuid.uuid4())
        
        item_id = item['id']
        
        if item_name_func:
            item_name = item_name_func(item)
        elif isinstance(item, dict) and 'nome' in item:
            item_name = item['nome']
        elif isinstance(item, dict) and 'name' in item:
            item_name = item['name']
        else:
            item_name = str(item_id)[:8]
        
        if item_id in processed_ids:
            print(f"⏭️ Pulando item {item_name} - já processado nesta execução")
            continue
            
        processed_ids.add(item_id)
        
        attempts = 0

        while attempts <= max_retries:
            try:
                print(f"🔄 Tentativa {attempts + 1} para item: {item_name}")
                
                result = process_func(item, attempts == 0)
                
                if result == "Unfinish":
                    print(f"⏭️ Item {item_name} retornou 'Unfinish' - pulando para próximo")
                    break
                elif result == "Success":
                    print(f"✅ Item {item_name} processado com sucesso")
                    break
                else:
                    print(f"✅ Item {item_name} concluído")
                    break
                    
            except Exception as e:
                if str(e).startswith("Unfinish:"):
                    message = str(e).replace("Unfinish: ", "")
                    print(f"⏭️ {message} - pulando para próximo item")
                    break
                
                attempts += 1

                print(f"❌ Erro na tentativa {attempts} para item {item_name}: {e}")
                
                if attempts > max_retries:
                    print(f"❌ Esgotadas as tentativas para item {item_name} após {max_retries + 1} tentativas")
                    break
                else:
                    print(f"🔄 Tentando novamente em {retry_delay} segundos...")
                    time.sleep(retry_delay)