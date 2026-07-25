import uuid
from backend.src.domain.entities.user import User
from backend.src.domain.entities.document import Document
from backend.src.domain.entities.conversation import Conversation


def test_user_entity_creation():
    user = User(
        email="test@example.com",
        hashed_password="hashed_secret",
        full_name="Test User",
        role="customer",
    )
    assert user.email == "test@example.com"
    assert user.role == "customer"
    assert user.is_active is True
    assert user.is_superuser is False


def test_document_entity_creation():
    user_id = str(uuid.uuid4())
    doc = Document(
        title="Knowledge Manual",
        filename="manual.pdf",
        file_path="uploads/raw/manual.pdf",
        file_type="pdf",
        file_size=1024,
        mime_type="application/pdf",
        user_id=user_id,
    )
    assert doc.title == "Knowledge Manual"
    assert doc.status == "pending"
    assert doc.user_id == user_id


def test_conversation_entity_creation():
    user_id = str(uuid.uuid4())
    conv = Conversation(
        title="Technical Query",
        user_id=user_id,
    )
    assert conv.title == "Technical Query"
    assert conv.status == "active"
