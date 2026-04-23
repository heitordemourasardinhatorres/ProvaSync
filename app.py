import streamlit as st
import os
from datetime import datetime
from src.extractor import parse_json_questoes
from src.forms_api import criar_form_google
import src.historico as historico

st.set_page_config(page_title="ProvaSync", page_icon="📝", layout="wide")
st.title("ProvaSync - Sincronizador de Provas (via JSON)")
st.write("Este aplicativo permite que você faça upload de um arquivo JSON (ou cole o texto) com as questões da prova e gere um formulário no Google Forms com as questões mapeadas.")

tab_nova, tab_historico = st.tabs(["Nova Prova", "Histórico"])

with tab_nova:
    st.header("Faça upload do arquivo JSON com as questões da prova")
    
    # Seleção do método de entrada
    metodo_input = st.radio("Como deseja enviar o JSON?", ["Upload de Arquivo", "Colar Texto"], horizontal=True)
    
    arquivo_json = None
    texto_json = ""
    json_nome_input = "Prova Colada Manualmente"
    
    if metodo_input == "Upload de Arquivo":
        arquivo_json = st.file_uploader("Selecione um arquivo .json", type=["json"])
        nome_sugerido = os.path.splitext(os.path.basename(arquivo_json.name))[0] if arquivo_json else "Prova do Arquivo"
    else:
        texto_json = st.text_area("Cole a estrutura JSON bruta aqui limitando pelas suas chaves:", height=250)
        nome_sugerido = "Prova Colada Manualmente"

    json_nome_input = st.text_input("Qual o nome desta prova? (Para o Histórico e título):", value=nome_sugerido)
    tipo_prova = st.radio("Esta prova é Objetiva ou Discursiva?", ["Objetiva", "Discursiva"], horizontal=True)
    
    # Controle de estado
    if "questoes_detectadas" not in st.session_state:
        st.session_state.questoes_detectadas = None
        st.session_state.json_nome = ""
        st.session_state.tipo_atual = ""
        
    if st.button("Processar JSON", type="primary"):
        conteudo = ""
        nome_prova = json_nome_input
        
        if metodo_input == "Upload de Arquivo" and arquivo_json is not None:
            conteudo = arquivo_json.getvalue().decode("utf-8")
        elif metodo_input == "Colar Texto" and texto_json.strip():
            conteudo = texto_json.strip()
            
        if conteudo:
            # Armazena estado pro formulário e histórico
            st.session_state.json_nome = nome_prova
            st.session_state.tipo_atual = tipo_prova
            try:
                # Verificação de segurança (Limite de 2MB)
                if len(conteudo.encode('utf-8')) > 2 * 1024 * 1024:
                    raise ValueError("Falha de Segurança: O arquivo ou texto inserido é excessivamente grande (Lim. 2 MB).")
                    
                with st.spinner("Classificando e mapeando array do arquivo JSON..."):
                    questoes = parse_json_questoes(conteudo, tipo_prova)
                
                st.success(f"{len(questoes)} questões importadas com sucesso!")
                st.session_state.questoes_detectadas = questoes
            except Exception as e:
                st.error(str(e))
                st.session_state.questoes_detectadas = None
        else:
            st.warning("Por favor, selecione e faça upload de um arquivo ou cole um JSON válido na área acima primeiro.")

    # Área de visualização em tabela interativa Streamlit.
    if st.session_state.questoes_detectadas is not None:
        st.write("---")
        st.markdown("### Questões Listadas")
        st.info("Estas questões estruturadas em JSON estão corretas? É possível editar, excluir ou adicionar novas linhas livremente nesta tabela prévia, depois siga para gerar no Google as checkboxes!")
        
        # Tabela frontend dinâmica de revisão final
        df_questoes = st.data_editor(
            st.session_state.questoes_detectadas,
            num_rows="dynamic",
            column_config={
                "id": st.column_config.TextColumn("Identificador (ex: 1, 1a)"),
                "materia": st.column_config.TextColumn("Matéria"),
                "submateria": st.column_config.TextColumn("Submatéria")
            },
            key="editor_questoes_frontend",
            width="stretch"
        )
        
        if st.button("Criar Form no Google", type="primary"):
            questoes_finais = df_questoes
            if not questoes_finais:
                st.warning("A lista final de questões está vazia, o que indica um erro. Preencha a tabela ou faça re-upload.")
            else:
                try:
                    with st.spinner("Aguardando contato com a API do Google Forms... Uma janela do navegador pode se abrir caso ainda não esteja autorizado pelo OAuth2."):
                        data_atual = datetime.now().strftime("%Y-%m-%d")
                        titulo_do_form = f"{st.session_state.json_nome} — {data_atual}"
                        form_id, form_link = criar_form_google(titulo_do_form, questoes_finais, st.session_state.tipo_atual)
                        
                        historico.salvar_historico(
                            nome=st.session_state.json_nome,
                            tipo=st.session_state.tipo_atual,
                            num_questoes=len(questoes_finais),
                            form_link=form_link,
                            form_id=form_id
                        )
                        
                    st.success("Google Form criado com sucesso na sua conta base!")
                    st.markdown(f"**Link Compartilhável:** [{form_link}]({form_link})")
                    st.code(form_link, language="text")
                except FileNotFoundError as e:
                    st.error(str(e))
                except Exception as e:
                    st.error(f"Ocorreu um erro no servidor web Google API. Ocorreu o erro: {str(e)}")

with tab_historico:
    st.header("Histórico de Formulários Mapeados")
    
    dados_logados = historico.carregar_historico()
    
    if not dados_logados:
        st.info("Nenhum formulário web foi sincronizado até agora por log. Faça upload de seu primeiro JSON!")
    else:
        st.dataframe(
            dados_logados,
            column_config={
                "nome": "Nome Capturado do JSON",
                "tipo": "Tipo",
                "questoes_detectadas": "Qnt. de Questões",
                "form_id": None,
                "criado_em": "Data da Sincronização",
                "form_link": st.column_config.LinkColumn("Link Ativo do Form")
            },
            width="stretch",
            hide_index=True
        )
