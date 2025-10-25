import enum

from datetime import date

from sqlalchemy import Text, String, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import List, TYPE_CHECKING

from app.db import Base
from app.db.models.base import TimestampMixin
from app.db.types import uid_pk, str_16, str_24, str_32, str_64, str_128, fk_country, fk_designer, fk_design_bureau, \
    fk_article

if TYPE_CHECKING:
    from app.db.models import Articles, AircraftDesignersAssociation, Countries, Designers


class AircraftTypes(str, enum.Enum):
    """
    Типы воздушных судов
    """

    airplane = "самолёт"
    airship = "дирижабль"
    helicopter = "вертолёт"
    rocket = "ракета"
    glider = "планёр"
    ornithopter = "орнитоптер"
    autogiro = "автожир"
    gyrodyne = "винтокрыл"
    wige = "экраноплан"
    balloon = "воздушный шар"
    uav = "беспилотник"


class EngineTypes(str, enum.Enum):
    """
    Типы двигателей
    """

    piston = "поршневой"
    turbojet = "турбореактивный"
    turboprop = "турбовинтовой"
    turbofan = "турбовентиляторный"
    ramjet = "воздушно-реактивный"
    rocket = "ракетный"
    electric = "электрический"


class AircraftStatus(str, enum.Enum):
    """
    Статус воздушного судна
    """

    in_production = "в производстве"
    discontinued = "снят с производства"
    in_operation = "в эксплуатации"


class AircraftPurpose(str, enum.Enum):
    """
    Назначение воздушного судна
    """

    civilian = "гражданский"
    transport = "транспортный"
    cargo = "грузовой"
    training = "учебный"
    medical = "медицинский"
    research = "исследовательский"
    military = "военный"
    special = "специального назначения"
    fighter = "истребитель"
    bomber = "бомбардировщик"
    tanker = "танкер"
    awacs = "awacs"


class Aircraft(Base, TimestampMixin):
    """
    Воздушные суда
    """

    __tablename__ = "aircraft"
    __table_args__ = {"schema": "articles"}

    id: Mapped[uid_pk]
    article_id: Mapped[fk_article | None]  # id статьи
    country_id: Mapped[fk_country]  # двухбуквенный ISO-код страны

    name: Mapped[str_32] = mapped_column(unique=True)  # название воздушного судна
    original_name: Mapped[str_32 | None] = mapped_column(unique=True)  # название на оригинальном языке
    aircraft_type: Mapped[str_16 | None] = mapped_column(Enum(AircraftTypes, native_enum=False, length=16))  # тип ВС
    image_url: Mapped[str_128 | None]  # основное изображение воздушного судна
    image_description: Mapped[str_128 | None]  # описание изображения воздушного судна
    image_license: Mapped[str_32 | None]  # лицензия изображения
    image_source: Mapped[str_128 | None]  # источник изображения
    image_author: Mapped[str_64 | None]  # автор изображения
    image_author_url: Mapped[str_128 | None]  # ссылка на автора изображения
    first_flight: Mapped[date | None]  # первый полёт
    wingspan: Mapped[float | None]  # размах крыльев в метрах
    length: Mapped[float | None]  # длина воздушного судна в метрах
    height: Mapped[float | None]  # высота воздушного судна в метрах
    max_takeoff_weight: Mapped[float | None]  # максимальный взлетный вес в килограммах
    engine_type: Mapped[str_32 | None] = mapped_column(Enum(EngineTypes, native_enum=False, length=32))  # тип двигателя
    number_of_engines: Mapped[int | None]  # количество двигателей
    max_speed: Mapped[int | None]  # максимальная скорость в км/ч
    cruise_speed: Mapped[int | None]  # крейсерская скорость в км/ч
    range: Mapped[int | None]  # дальность полета в км
    service_ceiling: Mapped[int | None]  # практический потолок в метрах
    crew: Mapped[int | None]  # экипаж (количество человек)
    # capacity: Mapped[str | None] = mapped_column(Text)  # вместимость (количество пассажиров или полезной нагрузки)
    icao_designator: Mapped[str | None] = mapped_column(String(4))  # четырёхбуквенный код ИКАО
    iata_designator: Mapped[str | None] = mapped_column(String(3))  # двух-трёхбуквенный код ИАТА
    status: Mapped[str_24 | None] = mapped_column(Enum(AircraftStatus, native_enum=False, length=24))  # статус самолета
    # variants: Mapped[str | None] = mapped_column(Text)  # описание модификаций и вариантов самолета
    year_of_manufacture: Mapped[int | None]  # дата начала производства
    first_used: Mapped[date | None]  # дата начала эксплуатации
    last_used: Mapped[date | None]  # дата окончания эксплуатации

    article: Mapped["Articles"] = relationship(back_populates="aircraft")
    country: Mapped["Countries"] = relationship(back_populates="aircraft")
    designers_association: Mapped[List["AircraftDesignersAssociation"]] = relationship(
        back_populates="aircraft"
    )
    designers: Mapped[List["Designers"]] = relationship(
        secondary="articles.aircraft_designers_as",
        back_populates="aircraft",
        viewonly=True,  # для предотвращения прямого добавления дизайнеров через aircraft.designers
    )


class DesignBureaus(Base, TimestampMixin):
    """
    Конструкторское бюро
    """

    __tablename__ = "design_bureaus"
    __table_args__ = {"schema": "articles"}

    id: Mapped[uid_pk]
    country_id: Mapped[fk_country]  # двухбуквенный ISO-код страны

    name: Mapped[str_32] = mapped_column(unique=True)  # название конструкторского бюро
    original_name: Mapped[str_32 | None] = mapped_column(unique=True)  # название на оригинальном языке
    description: Mapped[str] = mapped_column(Text)  # описание конструкторского бюро
    # image_url: Mapped[str_128 | None]
    # location: Mapped[str_128 | None]

    country: Mapped["Countries"] = relationship(back_populates="design_bureaus")
    designers_association: Mapped[List["DesignersBureausAssociation"]] = relationship(
        back_populates="design_bureau"
    )
    designers: Mapped[List["Designers"]] = relationship(
        secondary="articles.designers_bureaus_as",
        back_populates="design_bureaus",
        viewonly=True,
    )


class DesignersBureausAssociation(Base):
    """
    Ассоциативная таблица для связи конструкторов и конструкторских бюро
    """

    __tablename__ = "designers_bureaus_as"
    __table_args__ = {"schema": "articles"}

    designer_id: Mapped[fk_designer] = mapped_column(primary_key=True)
    design_bureau_id: Mapped[fk_design_bureau] = mapped_column(primary_key=True)
    role: Mapped[str_64 | None]  # роль конструктора в бюро ("руководитель отдела", ...)

    designer: Mapped["Designers"] = relationship(back_populates="bureau_association")
    design_bureau: Mapped["DesignBureaus"] = relationship(back_populates="designers_association")
