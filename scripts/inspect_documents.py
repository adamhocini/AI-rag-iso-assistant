import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.document_loader import load_documents


def main() -> None:
    documents_dir = PROJECT_ROOT / "data" / "documents"

    documents = load_documents(documents_dir)

    print(f"Nombre de documents chargés : {len(documents)}")
    print()

    for document in documents:
        metadata = document.metadata

        print(
            f"- {metadata['reference']} | "
            f"v{metadata['version']} | "
            f"{metadata['statut']} | "
            f"{metadata['type_document']} | "
            f"{metadata['titre']}"
        )

    print()
    print("Exemple de document chargé :")
    print("---------------------------")

    first_document = documents[0]

    print(f"Titre       : {first_document.metadata['titre']}")
    print(f"Référence   : {first_document.metadata['reference']}")
    print(f"Statut      : {first_document.metadata['statut']}")
    print(f"Processus   : {first_document.metadata['processus']}")
    print(f"Fichier     : {first_document.metadata['source_file']}")
    print()

    excerpt = first_document.content[:500].replace("\n", " ")
    print("Extrait du contenu :")
    print(excerpt)


if __name__ == "__main__":
    main()
