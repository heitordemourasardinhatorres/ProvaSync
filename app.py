import streamlit as st
import os
from datetime import datetime
from extractor import parse_json_questoes
from forms_api import criar_form_google
import historico

st.set_page_config(page_title="ProvaSync", page_icon="📝", layout="wide")
st.title("ProvaSync - Sincronizador de Provas (via JSON)")

tab_nova, tab_historico = st.tabs(["Nova Prova", "Histórico"])

with tab_nova:
    st.header("Faça upload do arquivo JSON com as questões da prova")
    
    # Novo Input restrito a JSON
    arquivo_json = st.file_uploader("Selecione um arquivo .json", type=["json"])
    tipo_prova = st.radio("Esta prova é Objetiva ou Discursiva?", ["Objetiva", "Discursiva"])
    
    # Controle de estado
    if "questoes_detectadas" not in st.session_state:
        st.session_state.questoes_detectadas = None
        st.session_state.json_nome = ""
        st.session_state.tipo_atual = ""
        
    if st.button("Processar Arquivo JSON"):
        if arquivo_json is not None:
            # Armazena estado pro formulário e histórico
            st.session_state.json_nome = os.path.splitext(arquivo_json.name)[0]
            st.session_state.tipo_atual = tipo_prova
            try:
                # Decodificando texto json na memória e enviando para extractor
                conteudo = arquivo_json.getvalue().decode("utf-8")
                
                with st.spinner("Classificando e mapeando array do arquivo JSON..."):
                    questoes = parse_json_questoes(conteudo, tipo_prova)
                
                st.success(f"{len(questoes)} questões importadas com sucesso do JSON!")
                st.session_state.questoes_detectadas = questoes
            except Exception as e:
                st.error(str(e))
                st.session_state.questoes_detectadas = None
        else:
            st.warning("Por favor, selecione e faça upload de um arquivo contendo JSON válido na área acima primeiro.")

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
                "resumo": st.column_config.TextColumn("Resumo do Enunciado")
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
