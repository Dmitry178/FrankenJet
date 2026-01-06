import uuid

from datetime import datetime, date
from sqlalchemy import UUID, text, ForeignKey, Integer, BigInteger, String, Boolean, true, false, literal, \
    DateTime, Date
from sqlalchemy.orm import mapped_column
from typing import Annotated

# строковые аннотированные типы
str_16 = Annotated[str, 16]
str_24 = Annotated[str, 24]
str_32 = Annotated[str, 32]
str_64 = Annotated[str, 64]
str_128 = Annotated[str, 128]
str_256 = Annotated[str, 256]
str_512 = Annotated[str, 512]
str_1024 = Annotated[str, 1024]
str_2048 = Annotated[str, 2048]

# числовые аннотированные типы
int_0 = Annotated[int, mapped_column(Integer, default=0, server_default=literal(0))]
int64 = Annotated[int, mapped_column(BigInteger)]

# бинарные аннотированные типы
bool_null = Annotated[bool | None, mapped_column(Boolean, nullable=True)]
bool_true = Annotated[bool, mapped_column(Boolean, default=True, server_default=true())]
bool_false = Annotated[bool, mapped_column(Boolean, default=False, server_default=false())]

# типы даты/времени
date_now = Annotated[date, mapped_column(Date, server_default=text("CURRENT_DATE"))]
datetime_now = Annotated[datetime, mapped_column(DateTime, server_default=text("now()"))]

# UUID аннотированные типы
uid = Annotated[
    uuid.UUID,
    mapped_column(
        UUID(as_uuid=True),
        server_default=text("uuid_generate_v4()")
    )
]

uid_pk = Annotated[
    uuid.UUID,
    mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("uuid_generate_v4()")
    )
]

# foreign keys
fk_user = Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), ForeignKey("users.users.id"))]
fk_user_cascade = \
    Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), ForeignKey("users.users.id", ondelete="CASCADE"))]
fk_role = Annotated[str, mapped_column(String(16), ForeignKey("users.roles.role"))]
fk_aircraft = Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), ForeignKey("articles.aircraft.id"))]
fk_article = Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), ForeignKey("articles.articles.id"))]
fk_country = Annotated[str, mapped_column(String(2), ForeignKey("articles.countries.id"))]
fk_tag = Annotated[str, mapped_column(String(32), ForeignKey("articles.tags.tag_id"))]
fk_tag_category = Annotated[str, mapped_column(String(32), ForeignKey("articles.tags_categories.category_id"))]

# раскомментировать при использовании этих моделей в проекте
# fk_design_bureau = Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), ForeignKey("articles.design_bureaus.id"))]
# fk_designer = Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), ForeignKey("articles.designers.id"))]
# fk_manufacturer = Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), ForeignKey("articles.manufacturers.id"))]

# карта аннотированных типов
annotation_map = {
    str_16: String(16),
    str_24: String(24),
    str_32: String(32),
    str_64: String(64),
    str_128: String(128),
    str_256: String(256),
    str_512: String(512),
    str_1024: String(1024),
    str_2048: String(2048),

    int_0: Integer,
    int64: BigInteger,

    bool_null: Boolean,
    bool_true: Boolean,
    bool_false: Boolean,

    uid: UUID(as_uuid=True),
    uid_pk: UUID(as_uuid=True),

    datetime_now: DateTime,

    fk_user: Integer,
    fk_user_cascade: Integer,
    fk_aircraft: UUID(as_uuid=True),
    fk_article: UUID(as_uuid=True),
    fk_country: UUID(as_uuid=True),
    fk_tag: String(32),

    # раскомментировать при использовании этих моделей в проекте
    # fk_design_bureau: UUID(as_uuid=True),
    # fk_designer: UUID(as_uuid=True),
    # fk_manufacturer: UUID(as_uuid=True),
}
