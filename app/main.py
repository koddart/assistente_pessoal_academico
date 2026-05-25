import sys
import os
from dotenv import load_dotenv
import json
from app.llm.client import client
from app.tools.orquestrador import executar_ferramenta


load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def executar_fluxo_jarvis(pergunta_usuario: str) -> str:
    prompt_analise = (
        "Você é o motor de rotas do JARVIS.\n"
        "Hoje é terça, 26 de maio de 2026.\n\n"
        "Sua única saída permitida é um objeto JSON com as chaves:\n"
        "- 'acao': string contendo 'listar_tarefas', 'adicionar_tarefa', 'concluir_tarefa', 'consultar_agenda', 'buscar_material_rag' ou 'conversar'.\n"
        "- 'params': objeto com os argumentos da função.\n\n"
        "Regra para buscar_material_rag: Use SEMPRE que o usuário fizer perguntas conceituais, dúvidas de matérias, pedir explicações ou resumos (ex: {'termo_busca': 'regressão linear'}).\n\n"
        "Exemplo de saída para listagem:\n"
        "Sempre que a ação for adicionar_tarefa, use as chaves titulo e data_prazo.\n"
        "{\"acao\": \"listar_tarefas\", \"params\": {}}\n\n"
        f"Pedido do usuário: {pergunta_usuario}\n"
        "Resposta JSON:"
    )

    try:
        resposta = client.chat.completions.create(
            model="google/gemma-3-12b-it",
            temperature=0.1,
            messages=[{"role": "user", "content": prompt_analise}]
        )
        
        conteudo = resposta.choices[0].message.content.strip()
        
        if "```" in conteudo:
            conteudo = conteudo.split("```")[1]
            if conteudo.startswith("json"):
                conteudo = conteudo[4:]
        conteudo = conteudo.strip()

        dados_intencao = json.loads(conteudo)
        acao = dados_intencao.get("acao", "conversar")
        params = dados_intencao.get("params", {})

        if acao == "conversar":
            return client.chat.completions.create(
                model="google/gemma-3-12b-it",
                messages=[{"role": "user", "content": pergunta_usuario}]
            ).choices[0].message.content

        print(f"\nJARVIS: Executando rota '{acao}'...")
        resultado_local = executar_ferramenta(acao, params)

        if acao in ["listar_tarefas", "consultar_agenda"]:
            return resultado_local

        if acao == "buscar_material_rag":
            prompt_resposta = (
                f"O estudante perguntou: '{pergunta_usuario}'\n\n"
                f"Responda de forma didática baseando-se estritamente nestes trechos do material dele:\n"
                f"{resultado_local}"
            )
            return client.chat.completions.create(
                model="google/gemma-3-12b-it",
                temperature=0.4,
                messages=[{"role": "user", "content": prompt_resposta}]
            ).choices[0].message.content

        resposta_confirmacao = client.chat.completions.create(
            model="google/gemma-3-12b-it",
            temperature=0.5,
            messages=[
                {"role": "system", "content": "Confirme o sucesso da operação de forma breve e amigável com base no resultado enviado."},
                {"role": "user", "content": f"Resultado: {resultado_local}"}
            ]
        )
        return resposta_confirmacao.choices[0].message.content

    except Exception as e:
        return f"Erro na orquestração central do Jarvis: {str(e)}"


def main():
    print("                                                      JARVIS ACADÊMICO - SISTEMA ESTÁVEL                                        ")
    while True:
        try:
            pergunta = input("\nVocê: ")
            if pergunta.strip().lower() in ["sair", "exit", "quit"]:
                break
            if not pergunta.strip():
                continue
            
            resposta_final = executar_fluxo_jarvis(pergunta)
            print(f"\nJARVIS:\n{resposta_final}")
            print("\n" + "_"*60)
        except KeyboardInterrupt:
            sys.exit(0)

if __name__ == "__main__":
    main()