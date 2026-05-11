from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base

class TestTable(Base):
    __tablename__ = "test_table"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
