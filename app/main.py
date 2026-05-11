import sys
from pathlib import Path

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.logger import log_rag_interaction
from app.rag_engine import ask_rag
from app.ollama_client import is_ollama_available, get_ollama_model


st.set_page_config(
    page_title="Assistant IA RAG ISO",
    page_icon="📚",
    layout="wide",
)


def display_confidence(label: str, score: float) -> None:
    """
    Affiche le niveau de confiance avec un message métier.
    """

    st.metric(
        label="Niveau de confiance",
        value=f"{label} ({score:.2f})",
    )

    if label == "Élevé":
        st.success("Les sources retrouvées semblent solides, mais une validation humaine reste nécessaire.")
    elif label == "Moyen":
        st.warning("Les sources sont utiles, mais la réponse doit être vérifiée.")
    elif label == "Faible":
        st.warning("La réponse repose sur des sources limitées, fragiles ou à vérifier.")
    else:
        st.error("Les documents disponibles ne permettent pas de répondre de manière fiable.")


def display_sources(sources: list[dict]) -> None:
    """
    Affiche les sources documentaires utilisées.
    """

    if not sources:
        st.info("Aucune source suffisamment pertinente.")
        return

    for source in sources:
        with st.expander(
            f"{source['reference']} - {source['titre']} | {source['statut']}",
            expanded=False,
        ):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.write(f"**Référence :** {source['reference']}")
                st.write(f"**Version :** {source['version']}")
                st.write(f"**Statut :** {source['statut']}")

            with col2:
                st.write(f"**Type :** {source['type_document']}")
                st.write(f"**Processus :** {source['processus']}")
                st.write(f"**Propriétaire :** {source['proprietaire']}")

            with col3:
                st.write(f"**Date validation :** {source['date_validation']}")
                st.write(f"**Fichier :** `{source['source_file']}`")
                st.write(f"**Score max :** {source['best_similarity_score']:.3f}")


def display_extracts(extracts: list[dict]) -> None:
    """
    Affiche les extraits pertinents retrouvés par ChromaDB.
    """

    if not extracts:
        st.info("Aucun extrait suffisamment pertinent.")
        return

    for index, extract in enumerate(extracts, start=1):
        adjusted_score = extract.get("adjusted_score", extract["similarity_score"])
        intent_bonus = extract.get("intent_bonus", 0.0)

        with st.expander(
            f"Extrait {index} | {extract['reference']} "
            f"| score {extract['similarity_score']:.3f} "
            f"| ajusté {adjusted_score:.3f}",
            expanded=False,
        ):
            st.caption(
                f"Chunk : {extract['chunk_id']} | "
                f"Bonus intention : {intent_bonus:.3f}"
            )
            st.write(extract["text"])


def main() -> None:
    st.title("📚 Assistant IA RAG ISO")
    st.caption("PoC local : documentation ISO fictive, ChromaDB, Streamlit et Ollama.")

    with st.sidebar:
        st.header("Configuration")

        generation_mode = st.radio(
            "Mode de génération",
            options=[
                "Sans LLM",
                "Ollama local",
            ],
            index=1,
        )

        st.divider()

        st.subheader("État Ollama")

        if is_ollama_available():
            st.success("Ollama disponible")
            st.write(f"Modèle : `{get_ollama_model()}`")
        else:
            st.error("Ollama indisponible")
            st.write("Lance Ollama avant d'utiliser le mode local.")

        st.divider()

        enable_logging = st.checkbox(
            "Journaliser les interactions",
            value=True,
        )

        st.divider()

        st.subheader("Questions de démonstration")

        demo_questions = [
            "Quels documents prouvent qu'un audit interne a été réalisé ?",
            "Cette procédure de gestion des risques est-elle encore valide ?",
            "Quelle est la procédure de gestion des non-conformités ?",
            "Prépare une checklist d'audit pour le processus achats.",
            "Quelle est la politique de cybersécurité de l'entreprise ?",
        ]

        selected_demo_question = st.selectbox(
            "Choisir une question",
            options=[""] + demo_questions,
        )

        st.divider()

        st.info(
            "Ce PoC utilise une documentation fictive. "
            "Les réponses doivent être validées par un humain."
        )

    default_question = selected_demo_question if selected_demo_question else ""

    question = st.text_area(
        "Question",
        value=default_question,
        placeholder="Pose une question sur la documentation qualité fictive...",
        height=100,
    )

    col_run, col_clear = st.columns([1, 1])

    with col_run:
        run_button = st.button("Interroger l'assistant", type="primary")

    with col_clear:
        clear_button = st.button("Effacer")

    if clear_button:
        st.rerun()

    if run_button:
        if not question.strip():
            st.warning("Saisis une question avant de lancer la recherche.")
            return

        use_ollama = generation_mode == "Ollama local"

        with st.spinner("Recherche des sources et génération de la réponse..."):
            response = ask_rag(
                question=question.strip(),
                use_ollama=use_ollama,
            )

            log_path = None
            if enable_logging:
                log_path = log_rag_interaction(response)

        st.divider()

        st.subheader("Réponse")

        if response.generation_mode == "ollama":
            st.badge("Réponse générée avec Ollama local")
        else:
            st.badge("Réponse générée sans LLM")

        st.markdown(response.answer)

        st.info(
            f"Intention détectée : {response.detected_intent_label} "
            f"(`{response.detected_intent}`)"
        )

        if log_path:
            st.caption(f"Interaction journalisée dans : `{log_path}`")

        st.divider()

        col_confidence, col_alerts = st.columns([1, 2])

        with col_confidence:
            display_confidence(
                label=response.confidence_label,
                score=response.confidence_score,
            )

        with col_alerts:
            st.subheader("Alertes")

            if response.alerts:
                for alert in response.alerts:
                    st.warning(alert)
            else:
                st.success("Aucune alerte documentaire détectée.")

        st.divider()

        tab_sources, tab_extracts, tab_context, tab_limits = st.tabs(
            [
                "Sources utilisées",
                "Extraits pertinents",
                "Extraits envoyés au LLM",
                "Limites",
            ]
        )

        with tab_sources:
            display_sources(response.sources)

        with tab_extracts:
            display_extracts(response.relevant_extracts)

        with tab_context:
            st.caption(
                "Ces extraits sont ceux réellement transmis au générateur "
                "LLM/Ollama. Les autres extraits pertinents restent affichés "
                "pour transparence."
            )
            display_extracts(response.context_extracts)

        with tab_limits:
            for limitation in response.limitations:
                st.write(f"- {limitation}")


if __name__ == "__main__":
    main()
