import enum

from datetime import date

from sqlalchemy import Date, Text, String, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import List, TYPE_CHECKING

from app.db import Base
from app.db.models.base import TimestampMixin
from app.db.types import uid_pk, str_32, str_64, str_128, fk_manufacturer, fk_country, fk_designer, fk_aircraft, \
    fk_design_bureau, fk_article

if TYPE_CHECKING:
    from app.db.models import Articles


class AircraftTypes(str, enum.Enum):
    """
    Типы воздушных судов
    """

    airplane = "самолёт"
    airship = "дирижабль"
    helicopter = "вертолёт"
    rocket = "ракета"
    glider = "планер"
    ornithopter = "орнитоптер"
    autogiro = "автожир"
    gyrodyne = "винтокрыл"
    wige = "экраноплан"
    balloon = "воздушный шар"
    blimp = "дирижабль"


class EngineTypes(str, enum.Enum):
    """
    Типы двигателей
    """

    piston = "поршневой"
    turbojet = "турбореактивный"
    turboprop = "турбовинтовой"
    turbofan = "турбовентиляторный"
    ramjet = "прямоточный воздушно-реактивный"
    rocket = "ракетный"
    electric = "электрический"


class AircraftStatus(str, enum.Enum):
    """
    Статус воздушного судна
    """

    in_production = "в производстве"
    discontinued = "снят с производства"
    in_operation = "в эксплуатации"


class Aircraft(Base, TimestampMixin):
    """
    Воздушные суда
    """

    __tablename__ = "aircraft"
    __table_args__ = {"schema": "articles"}

    id: Mapped[uid_pk]
    article_id: Mapped[fk_article | None]  # id статьи
    country_id: Mapped[fk_country]  # двухбуквенный ISO-код страны
    manufacturer_id: Mapped[fk_manufacturer | None]  # id производителя

    slug: Mapped[str_64] = mapped_column(unique=True)  # строковый идентификатор
    name: Mapped[str_32] = mapped_column(unique=True)  # название воздушного судна
    aircraft_type: Mapped[str | None] = mapped_column(Enum(AircraftTypes, native_enum=False))  # тип воздушного судна
    first_flight: Mapped[date | None]  # первый полёт
    wingspan: Mapped[float | None]  # размах крыльев в метрах
    length: Mapped[float | None]  # длина воздушного судна в метрах
    height: Mapped[float | None]  # высота воздушного судна в метрах
    max_takeoff_weight: Mapped[float | None]  # максимальный взлетный вес в килограммах
    engine_type: Mapped[str | None] = mapped_column(Enum(EngineTypes, native_enum=False))  # тип двигателя
    number_of_engines: Mapped[int | None]  # количество двигателей
    max_speed: Mapped[int | None]  # максимальная скорость в км/ч
    cruise_speed: Mapped[int | None]  # крейсерская скорость в км/ч
    range: Mapped[int | None]  # дальность полета в км
    service_ceiling: Mapped[int | None]  # практический потолок в метрах
    crew: Mapped[int | None]  # экипаж (количество человек)
    # capacity: Mapped[str | None] = mapped_column(Text)  # вместимость (количество пассажиров или полезной нагрузки)
    icao_designator: Mapped[str | None] = mapped_column(String(4))  # четырёхбуквенный код ИКАО
    iata_designator: Mapped[str | None] = mapped_column(String(3))  # двух-трёхбуквенный код ИАТА
    status: Mapped[str | None] = mapped_column(Enum(AircraftStatus, native_enum=False))  # статус самолета
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
    manufacturer_association: Mapped[List["AircraftManufacturersAssociation"]] = relationship(
        back_populates="aircraft"
    )
    manufacturers: Mapped[List["Manufacturers"]] = relationship(
        secondary="articles.aircraft_manufacturers_as",
        back_populates="aircraft",
        viewonly=True,
    )


class Countries(Base):
    """
    Страны
    """

    __tablename__ = "countries"
    __table_args__ = {"schema": "articles"}

    id: Mapped[str] = mapped_column(String(2), primary_key=True)  # двухбуквенный ISO-код страны

    name: Mapped[str_32] = mapped_column(unique=True)  # название страны
    iso_code: Mapped[str | None] = mapped_column(String(3), unique=True, nullable=True)  # трёхбуквенный ISO-код страны
    flag_image_url: Mapped[str_128 | None]  # URL изображения флага страны

    aircraft: Mapped[List["Aircraft"]] = relationship(back_populates="country")
    design_bureaus: Mapped[List["DesignBureaus"]] = relationship(back_populates="country")
    designers: Mapped[List["Designers"]] = relationship(back_populates="country")
    manufacturers: Mapped[List["Manufacturers"]] = relationship(back_populates="country")


class Designers(Base, TimestampMixin):
    """
    Конструкторы
    """

    __tablename__ = "designers"
    __table_args__ = {"schema": "articles"}

    id: Mapped[uid_pk]
    country_id: Mapped[fk_country]

    slug: Mapped[str_64] = mapped_column(unique=True)  # строковый идентификатор
    name: Mapped[str_32] = mapped_column(unique=True)  # имя конструктора
    birth_date: Mapped[date | None] = mapped_column(Date)
    death_date: Mapped[date | None] = mapped_column(Date)
    known_for: Mapped[str | None] = mapped_column(Text)  # чем знаменит конструктор
    biography: Mapped[str] = mapped_column(Text)  # биография
    image_url: Mapped[str_128 | None]  # URL основного изображения

    country: Mapped["Countries"] = relationship(back_populates="designers")
    aircraft_association: Mapped[List["AircraftDesignersAssociation"]] = relationship(
        back_populates="designer"
    )
    aircraft: Mapped[List["Aircraft"]] = relationship(
        secondary="articles.aircraft_designers_as",
        back_populates="designers",
        viewonly=True,  # для предотвращения прямого добавления самолетов через designer.aircraft
    )
    bureau_association: Mapped[List["DesignersBureausAssociation"]] = relationship(
        back_populates="designer"
    )
    design_bureaus: Mapped[List["DesignBureaus"]] = relationship(
        secondary="articles.designers_bureaus_as",
        back_populates="designers",
        viewonly=True,  # для предотвращения прямого добавления КБ через конструктора
    )


class AircraftDesignersAssociation(Base):
    """
    Ассоциативная таблица для связи самолётов и конструкторов
    """

    __tablename__ = "aircraft_designers_as"
    __table_args__ = {"schema": "articles"}

    aircraft_id: Mapped[fk_aircraft] = mapped_column(primary_key=True)
    designer_id: Mapped[fk_designer] = mapped_column(primary_key=True)
    role: Mapped[str_64 | None]  # роли ("главный конструктор", "ведущий инженер", ...)

    aircraft: Mapped["Aircraft"] = relationship(back_populates="designers_association")
    designer: Mapped["Designers"] = relationship(back_populates="aircraft_association")


class Manufacturers(Base, TimestampMixin):
    """
    Производители воздушных судов
    """

    __tablename__ = "manufacturers"
    __table_args__ = {"schema": "articles"}

    id: Mapped[uid_pk]
    country_id: Mapped[fk_country]  # двухбуквенный ISO-код страны

    slug: Mapped[str_64] = mapped_column(unique=True)  # строковый идентификатор
    name: Mapped[str_32] = mapped_column(unique=True)  # название производителя
    description: Mapped[str] = mapped_column(Text)  # описание производителя

    country: Mapped["Countries"] = relationship(back_populates="manufacturers")
    aircraft_association: Mapped[List["AircraftManufacturersAssociation"]] = relationship(
        back_populates="manufacturer"
    )
    aircraft: Mapped[List["Aircraft"]] = relationship(
        secondary="articles.aircraft_manufacturers_as",
        back_populates="manufacturers",
        viewonly=True,
    )


class AircraftManufacturersAssociation(Base):
    """
    Ассоциативная таблица для связи самолетов и производителей
    """

    __tablename__ = "aircraft_manufacturers_as"
    __table_args__ = {"schema": "articles"}

    aircraft_id: Mapped[fk_aircraft] = mapped_column(primary_key=True)
    manufacturer_id: Mapped[fk_manufacturer] = mapped_column(primary_key=True)
    start_production: Mapped[date | None]  # дата начала производства на данном предприятии
    end_production: Mapped[date | None]  # дата окончания производства на данном предприятии

    aircraft: Mapped["Aircraft"] = relationship(back_populates="manufacturer_association")
    manufacturer: Mapped["Manufacturers"] = relationship(back_populates="aircraft_association")


class DesignBureaus(Base, TimestampMixin):
    """
    Конструкторское бюро
    """

    __tablename__ = "design_bureaus"
    __table_args__ = {"schema": "articles"}

    id: Mapped[uid_pk]
    country_id: Mapped[fk_country]  # двухбуквенный ISO-код страны

    slug: Mapped[str_64] = mapped_column(unique=True)  # строковый идентификатор
    name: Mapped[str_32] = mapped_column(unique=True)  # название конструкторского бюро
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
