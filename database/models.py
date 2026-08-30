from sqlalchemy import Float, Integer, String, Boolean, Date
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import date


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    fuel_consumption: Mapped[float | None] = mapped_column(Float, nullable=True)

class MileageSetting(Base):
    __tablename__ = "mileage_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    workplace: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    mileage: Mapped[float] = mapped_column(Float, nullable=False)

class DailyReport(Base):
    __tablename__ = "daily_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    user_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    report_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    workplace: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    mileage: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    refueled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    fuel_liters: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    fuel_amount: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    work_description: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    work_completed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    is_out_of_town: Mapped[bool] = mapped_column(
    Boolean,
    nullable=False,
)