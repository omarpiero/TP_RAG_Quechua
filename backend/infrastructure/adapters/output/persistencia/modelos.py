from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class FuenteORM(Base):
    __tablename__ = "fuentes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    titulo: Mapped[str] = mapped_column(String(300), nullable=False)
    entidad_publicadora: Mapped[str] = mapped_column(String(200), nullable=False)
    licenciamiento: Mapped[str] = mapped_column(String(300), nullable=False)
    fecha_extraccion: Mapped[date] = mapped_column(Date, nullable=False)
    nombre_archivo: Mapped[str] = mapped_column(String(300), nullable=False)
    paginas_totales: Mapped[int] = mapped_column(Integer, default=0)
    paginas_con_texto: Mapped[int] = mapped_column(Integer, default=0)
    derivado_ocr: Mapped[bool] = mapped_column(Boolean, default=False)


class ConsultaORM(Base):
    __tablename__ = "consultas"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    texto: Mapped[str] = mapped_column(Text, nullable=False)
    idioma: Mapped[str] = mapped_column(String(2), nullable=False)
    texto_traducido: Mapped[str | None] = mapped_column(Text, nullable=True)
    momento: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    respuesta_texto: Mapped[str] = mapped_column(Text, nullable=False)
    abstenida: Mapped[bool] = mapped_column(Boolean, nullable=False, index=True)
    similitud_maxima: Mapped[float] = mapped_column(Float, nullable=False)

    respaldos: Mapped[list["RespaldoORM"]] = relationship(
        back_populates="consulta", cascade="all, delete-orphan", lazy="selectin"
    )


class RespaldoORM(Base):
    """Trazabilidad persistida: sin documento y pagina no hay forma de verificar una
    respuesta en la fuente original (RNF-08)."""

    __tablename__ = "respaldos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    consulta_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("consultas.id", ondelete="CASCADE"), nullable=False
    )
    fragmento_id: Mapped[str] = mapped_column(String(64), nullable=False)
    documento: Mapped[str] = mapped_column(String(300), nullable=False)
    pagina: Mapped[int] = mapped_column(Integer, nullable=False)
    texto: Mapped[str] = mapped_column(Text, nullable=False)
    puntuacion: Mapped[float] = mapped_column(Float, nullable=False)
    derivado_ocr: Mapped[bool] = mapped_column(Boolean, default=False)

    consulta: Mapped[ConsultaORM] = relationship(back_populates="respaldos")
