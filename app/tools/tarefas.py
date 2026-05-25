import json
from pathlib import Path
import os 

TAREFAS_PATH = Path("app/memory/tarefas.json")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def adicionar_tarefa(titulo=None, data_prazo="undefined", nome_tarefa=None, tarefa=None, prazo=None, data=None, dia=None, **kwargs):
    tarefas = []

    if TAREFAS_PATH.exists():
        try:
            with TAREFAS_PATH.open("r", encoding="utf-8") as f:
                tarefas = json.load(f)
        except Exception:
            tarefas = []

    titulo = titulo or nome_tarefa or tarefa
    if not titulo or not str(titulo).strip():
        return "Não foi possível adicionar a tarefa: título não informado."

    data_prazo = prazo or data or dia or data_prazo

    novo_id = max([t.get("id", 0) for t in tarefas], default=0) + 1

    nova_tarefa = {
        "id": novo_id,
        "titulo": str(titulo).strip(),
        "status": "Pendente",
        "data_prazo": str(data_prazo).strip(),
    }

    tarefas.append(nova_tarefa)

    TAREFAS_PATH.parent.mkdir(parents=True, exist_ok=True)

    with TAREFAS_PATH.open("w", encoding="utf-8") as f:
        json.dump(tarefas, f, indent=2, ensure_ascii=False)

    prazo_str = f" com prazo para {data_prazo}" if data_prazo != "undefined" else ""
    return f"Tarefa '[{novo_id}] {titulo}' adicionada com sucesso{prazo_str}."

def listar_tarefas() -> str:
    if not os.path.exists(TAREFAS_PATH):
        return "Sua Lista de Tarefas está vazia."

    try:
        with open(TAREFAS_PATH, "r", encoding="utf-8") as f:
            conteudo = f.read().strip()
            if not conteudo:
                return "Sua Lista de Tarefas está vazia."
            tarefas = json.loads(conteudo)
    except Exception as e:
        return f"Erro interno ao decodificar o JSON: {str(e)}"

    if not tarefas:
        return "Sua Lista de Tarefas está vazia."

    resultado = "Sua Lista de Tarefas:\n"
    for t in tarefas:
        prazo = f" (Prazo: {t['data_prazo']})" if t.get("data_prazo") != "undefined" else ""
        resultado += f"- [{t['id']}] {t['titulo']}{prazo} - {t['status']}\n"
    
    return resultado

def concluir_tarefa(id_tarefa=None, tarefa_id=None, tarefa=None, titulo=None, nome=None, **kwargs):

    tarefas = []

    if TAREFAS_PATH.exists():
        with TAREFAS_PATH.open("r", encoding="utf-8") as f:
            tarefas = json.load(f)

    identificador = id_tarefa or tarefa_id or tarefa or titulo or nome

    if identificador is None:
        return "Nenhuma tarefa foi informada."

    tarefa_encontrada = None

    for item in tarefas:

        if str(item.get("id")) == str(identificador):
            tarefa_encontrada = item
            break

        if item.get("titulo", "").lower() == str(identificador).lower():
            tarefa_encontrada = item
            break

    if tarefa_encontrada is None:
        return "Tarefa não encontrada."

    tarefa_encontrada["status"] = "Concluída"

    with TAREFAS_PATH.open("w", encoding="utf-8") as f:
        json.dump(tarefas, f, indent=2, ensure_ascii=False)

    return f"Tarefa '{tarefa_encontrada['titulo']}' concluída com sucesso."