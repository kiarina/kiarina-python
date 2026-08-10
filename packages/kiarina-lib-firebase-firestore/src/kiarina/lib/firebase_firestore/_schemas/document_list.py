from dataclasses import dataclass

from .document_snapshot import DocumentSnapshot


@dataclass
class DocumentList:
    """A page of documents listed from a Cloud Firestore collection."""

    documents: list[DocumentSnapshot]
    next_page_token: str | None
