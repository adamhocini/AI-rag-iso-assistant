from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple


REQUIRED_METADATA_FIELDS = [
    "titre",
    "reference",
    "version",
    "statut",
    "date_validation",
    "proprietaire",
    "processus",
    "type_document",
]


@dataclass
class QualityDocument:
    """
    Représente un document qualité chargé depuis le corpus.

    metadata : informations structurées du document
    content  : contenu textuel du document, sans les métadonnées
    source_path : chemin du fichier source
    """

    metadata: Dict[str, str]
    content: str
    source_path: str


def split_front_matter(raw_text: str) -> Tuple[str, str]:
    """
    Sépare les métadonnées YAML simplifiées du contenu Markdown.

    Le format attendu est :

    ---
    titre: "..."
    reference: "..."
    ---

    # Contenu du document
    """

    if not raw_text.startswith("---"):
        raise ValueError("Le document ne commence pas par un bloc de métadonnées '---'.")

    parts = raw_text.split("---", 2)

    if len(parts) < 3:
        raise ValueError("Le bloc de métadonnées est incomplet ou mal fermé.")

    front_matter = parts[1].strip()
    content = parts[2].strip()

    return front_matter, content


def parse_metadata(front_matter: str) -> Dict[str, str]:
    """
    Parse un bloc de métadonnées très simple au format clé: valeur.

    Exemple :
    titre: "Procédure de gestion documentaire"
    reference: "PROC-DOC-001"
    """

    metadata = {}

    for line in front_matter.splitlines():
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        if ":" not in line:
            continue

        key, value = line.split(":", 1)

        clean_key = key.strip()
        clean_value = value.strip().strip('"').strip("'")

        metadata[clean_key] = clean_value

    return metadata


def validate_metadata(metadata: Dict[str, str], file_path: Path) -> None:
    """
    Vérifie que toutes les métadonnées obligatoires sont présentes.
    """

    missing_fields = [
        field for field in REQUIRED_METADATA_FIELDS
        if field not in metadata or not metadata[field]
    ]

    if missing_fields:
        raise ValueError(
            f"Le fichier '{file_path.name}' est incomplet. "
            f"Métadonnées manquantes : {', '.join(missing_fields)}"
        )


def load_markdown_document(file_path: Path) -> QualityDocument:
    """
    Charge un document Markdown unique.
    """

    raw_text = file_path.read_text(encoding="utf-8")

    front_matter, content = split_front_matter(raw_text)
    metadata = parse_metadata(front_matter)

    validate_metadata(metadata, file_path)

    metadata["source_file"] = file_path.name

    return QualityDocument(
        metadata=metadata,
        content=content,
        source_path=str(file_path),
    )


def load_documents(documents_dir: str | Path) -> List[QualityDocument]:
    """
    Charge tous les fichiers Markdown d'un dossier.
    """

    documents_path = Path(documents_dir)

    if not documents_path.exists():
        raise FileNotFoundError(f"Le dossier '{documents_path}' n'existe pas.")

    markdown_files = sorted(documents_path.glob("*.md"))

    if not markdown_files:
        raise FileNotFoundError(f"Aucun fichier Markdown trouvé dans '{documents_path}'.")

    documents = []

    for file_path in markdown_files:
        document = load_markdown_document(file_path)
        documents.append(document)

    return documents
