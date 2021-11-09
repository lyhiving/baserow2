from typing import Union, Tuple, Optional, Set

ThroughFieldName = str
TargetFieldName = str
FieldName = str
ThroughFieldDependency = Tuple[ThroughFieldName, TargetFieldName]
FieldDependencies = Set[Union[FieldName, ThroughFieldDependency]]
OptionalFieldDependencies = Optional[FieldDependencies]
