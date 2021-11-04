import { Registerable } from '@/modules/core/registry'
import RowEditFieldText from '@/modules/database/components/row/RowEditFieldText'
import RowEditFieldNumber from '@/modules/database/components/row/RowEditFieldNumber'
import RowEditFieldDate from '@/modules/database/components/row/RowEditFieldDate'
import RowEditFieldBoolean from '@/modules/database/components/row/RowEditFieldBoolean'
import FunctionalGridViewFieldDate from '@baserow/modules/database/components/view/grid/fields/FunctionalGridViewFieldDate'
import FunctionalGridViewFieldBoolean from '@baserow/modules/database/components/view/grid/fields/FunctionalGridViewFieldBoolean'
import FunctionalGridViewFieldNumber from '@baserow/modules/database/components/view/grid/fields/FunctionalGridViewFieldNumber'
import FunctionalGridViewFieldText from '@baserow/modules/database/components/view/grid/fields/FunctionalGridViewFieldText'

export class BaserowFormulaTypeDefinition extends Registerable {
  getIconClass() {
    throw new Error(
      'Not implemented error. This method should return the types icon.'
    )
  }

  getRowEditFieldComponent() {
    throw new Error(
      'Not implemented error. This method should return the types row edit component.'
    )
  }

  getFunctionalGridViewFieldComponent() {
    throw new Error(
      'Not implemented error. This method should return the types functional grid' +
        ' view field component.'
    )
  }

  getFieldType() {
    throw new Error(
      'Not implemented error. This method should return the types corresponding' +
        ' Baserow field type that should be used for things like sort indicators etc.'
    )
  }
}

export class BaserowFormulaTextType extends BaserowFormulaTypeDefinition {
  getType() {
    return 'text'
  }

  getFieldType() {
    return 'text'
  }

  getIconClass() {
    return 'font'
  }

  getRowEditFieldComponent() {
    return RowEditFieldText
  }

  getFunctionalGridViewFieldComponent() {
    return FunctionalGridViewFieldText
  }
}

export class BaserowFormulaCharType extends BaserowFormulaTypeDefinition {
  getType() {
    return 'char'
  }

  getFieldType() {
    return 'text'
  }

  getIconClass() {
    return 'font'
  }

  getRowEditFieldComponent() {
    return RowEditFieldText
  }

  getFunctionalGridViewFieldComponent() {
    return FunctionalGridViewFieldText
  }
}

export class BaserowFormulaNumberType extends BaserowFormulaTypeDefinition {
  getType() {
    return 'number'
  }

  getFieldType() {
    return 'number'
  }

  getIconClass() {
    return 'hashtag'
  }

  getRowEditFieldComponent() {
    return RowEditFieldNumber
  }

  getFunctionalGridViewFieldComponent() {
    return FunctionalGridViewFieldNumber
  }
}

export class BaserowFormulaBooleanType extends BaserowFormulaTypeDefinition {
  getType() {
    return 'boolean'
  }

  getFieldType() {
    return 'boolean'
  }

  getIconClass() {
    return 'check-square'
  }

  getRowEditFieldComponent() {
    return RowEditFieldBoolean
  }

  getFunctionalGridViewFieldComponent() {
    return FunctionalGridViewFieldBoolean
  }
}

export class BaserowFormulaDateType extends BaserowFormulaTypeDefinition {
  getType() {
    return 'date'
  }

  getFieldType() {
    return 'date'
  }

  getIconClass() {
    return 'calendar-alt'
  }

  getRowEditFieldComponent() {
    return RowEditFieldDate
  }

  getFunctionalGridViewFieldComponent() {
    return FunctionalGridViewFieldDate
  }
}

export class BaserowFormulaDateIntervalType extends BaserowFormulaTypeDefinition {
  getType() {
    return 'date_interval'
  }

  getFieldType() {
    return 'date'
  }

  getIconClass() {
    return 'history'
  }

  getRowEditFieldComponent() {
    return RowEditFieldText
  }

  getFunctionalGridViewFieldComponent() {
    return FunctionalGridViewFieldText
  }
}

// This type only exists in the frontend and only is referenced by a few weird frontend
// function defs which we want to show as a 'special' type in the GUI.
export class BaserowFormulaSpecialType extends BaserowFormulaTypeDefinition {
  getType() {
    return 'special'
  }

  getFieldType() {
    return 'text'
  }

  getIconClass() {
    return 'square-root-alt'
  }

  getRowEditFieldComponent() {
    return RowEditFieldText
  }

  getFunctionalGridViewFieldComponent() {
    return FunctionalGridViewFieldText
  }
}

export class BaserowFormulaInvalidType extends BaserowFormulaTypeDefinition {
  getType() {
    return 'invalid'
  }

  getFieldType() {
    return 'text'
  }

  getIconClass() {
    return 'fa-exclamation-triangle'
  }

  getRowEditFieldComponent() {
    return RowEditFieldText
  }

  getFunctionalGridViewFieldComponent() {
    return FunctionalGridViewFieldText
  }
}

export class BaserowFormulaArrayType extends BaserowFormulaTypeDefinition {
  getType() {
    return 'array'
  }

  getFieldType() {
    return 'text'
  }

  getIconClass() {
    return 'list'
  }

  getRowEditFieldComponent() {
    return RowEditFieldText
  }

  getFunctionalGridViewFieldComponent() {
    return FunctionalGridViewFieldText
  }
}
