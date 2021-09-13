from typing import Union, Optional

from baserow.contrib.database.fields.models import Field

UnTyped = type(None)

InvalidType = str
ValidType = Field
Typed = Union[InvalidType, ValidType]
