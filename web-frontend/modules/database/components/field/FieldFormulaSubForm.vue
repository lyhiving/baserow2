<template>
  <div>
    <FieldFormulaInitialSubForm
      :default-values="mergedTypeOptions"
      :formula="values.formula"
      :error="localOrServerError"
      :formula-type="localOrServerFormulaType"
      :initial-formula="initialFormula"
      :parsing-error="parsingError"
      :table="table"
      @open-advanced-context="
        $refs.advancedFormulaEditContext.openContext($event)
      "
      @retype-formula="retypeFormula"
    >
    </FieldFormulaInitialSubForm>
    <FormulaAdvancedEditContext
      ref="advancedFormulaEditContext"
      v-model="values.formula"
      :table="table"
      :fields="fieldsWithoutThisField"
      :error="localOrServerError"
    >
    </FormulaAdvancedEditContext>
  </div>
</template>

<script>
import { required } from 'vuelidate/lib/validators'
import { mapGetters } from 'vuex'

import form from '@baserow/modules/core/mixins/form'
import { notifyIf } from '@baserow/modules/core/utils/error'

import fieldSubForm from '@baserow/modules/database/mixins/fieldSubForm'
import FieldFormulaInitialSubForm from '@baserow/modules/database/components/formula/FieldFormulaInitialSubForm'
import FormulaAdvancedEditContext from '@baserow/modules/database/components/formula/FormulaAdvancedEditContext'
import FormulaService from '@baserow/modules/database/services/formula'
import parseBaserowFormula from '@baserow/modules/database/formula/parser/parser'
import { replaceFieldByIdWithField } from '@baserow/modules/database/formula/parser/replaceFieldByIdWithField'
import { updateFieldNames } from '@baserow/modules/database/formula/parser/updateFieldNames'

export default {
  name: 'FieldFormulaSubForm',
  components: {
    FieldFormulaInitialSubForm,
    FormulaAdvancedEditContext,
  },
  mixins: [form, fieldSubForm],
  data() {
    return {
      allowedValues: ['formula'],
      values: {
        formula: '',
      },
      typeOptions: {},
      mergedTypeOptions: Object.assign({}, this.defaultValues),
      parsingError: null,
      errorFromServer: null,
      localFormulaType: null,
      initialFormula: null,
    }
  },
  computed: {
    ...mapGetters({
      rawFields: 'field/getAllWithPrimary',
    }),
    localOrServerFormulaType() {
      return this.localFormulaType
        ? this.localFormulaType
        : this.defaultValues.formula_type
    },
    fieldsWithoutThisField() {
      return this.rawFields.filter((f) => {
        return f.id !== this.defaultValues.id
      })
    },
    fieldIdToNameMap() {
      return this.rawFields.reduce(function (map, obj) {
        map[obj.id] = obj.name
        return map
      }, {})
    },
    localOrServerError() {
      if (!this.$v.values.formula.required) {
        return 'Please enter a formula'
      } else if (!this.$v.values.formula.parseFormula) {
        return (
          `Error in the formula on line ${this.parsingError.line} starting at
        letter ${this.parsingError.character}` +
          '\n' +
          this.toHumanReadableErrorMessage(this.parsingError)
        )
      } else if (this.errorFromServer) {
        return this.errorFromServer
      } else if (this.defaultValues.error) {
        return this.defaultValues.error
      } else {
        return null
      }
    },
  },
  watch: {
    fieldIdToNameMap(idToNewNames, idToOldNames) {
      const oldToNewNameMapBuilder = function (map, key) {
        map[idToOldNames[key]] = idToNewNames[key]
        return map
      }
      const oldKnownFieldIds = Object.keys(idToOldNames)
      const oldFieldNameToNewFieldName = oldKnownFieldIds.reduce(
        oldToNewNameMapBuilder,
        {}
      )
      this.fieldNameChanged(oldFieldNameToNewFieldName)
    },
    defaultValues(newValue, oldValue) {
      this.convertServerSideFormulaToClient(newValue.formula)
      this.mergedTypeOptions = Object.assign({}, newValue)
    },
    'values.formula'(newValue, oldValue) {
      this.$v.values.formula.$touch()
    },
  },
  methods: {
    parseFormula(value) {
      if (!value.trim()) {
        return false
      }
      try {
        parseBaserowFormula(value)
        this.convertServerSideFormulaToClient(value)
        this.parsingError = null
        return true
      } catch (e) {
        this.parsingError = e
        return false
      }
    },
    convertServerSideFormulaToClient(formula) {
      this.values.formula = replaceFieldByIdWithField(
        formula,
        this.fieldIdToNameMap
      )
      if (!this.initialFormula) {
        this.initialFormula = this.values.formula
      }
    },
    fieldNameChanged(oldNameToNewNameMap) {
      this.convertServerSideFormulaToClient(this.values.formula)
      this.values.formula = updateFieldNames(
        this.values.formula,
        oldNameToNewNameMap
      )
    },
    toHumanReadableErrorMessage(error) {
      const s = error.message
        .replace('extraneous', 'Invalid')
        .replace('input', 'letters')
        .replace(' expecting', ', was instead expecting ')
        .replace("'<EOF>'", 'the end of the formula')
        .replace('<EOF>', 'the end of the formula')
        .replace('mismatched letters', 'Unexpected')
        .replace('Unexpected the', 'Unexpected')
        .replace('SINGLEQ_STRING_LITERAL', 'a single quoted string')
        .replace('DOUBLEQ_STRING_LITERAL', 'a double quoted string')
        .replace('IDENTIFIER', 'a function')
        .replace('IDENTIFIER_UNICODE', '')
        .replace('{', '')
        .replace('}', '')
      return s + '.'
    },
    handleError(error) {
      if (error.handler.code === 'ERROR_WITH_FORMULA') {
        this.errorFromServer = error.handler.detail
        return true
      } else {
        return false
      }
    },
    reset() {
      form.methods.reset.call(this)
      this.errorFromServer = null
      this.initialFormula = null
    },
    async retypeFormula() {
      try {
        const { data } = await FormulaService(this.$client).type(
          this.defaultValues.id,
          this.values.formula
        )
        // eslint-disable-next-line camelcase
        const { formula_type, error, ...otherTypeOptions } = data

        this.mergedTypeOptions = Object.assign(
          {},
          this.mergedTypeOptions,
          otherTypeOptions
        )
        this.errorFromServer = error
        // eslint-disable-next-line camelcase
        this.localFormulaType = formula_type
        this.initialFormula = this.values.formula
      } catch (e) {
        if (!this.handleError(e)) {
          notifyIf(e, 'field')
        }
      }
    },
  },
  validations() {
    return {
      values: {
        formula: {
          required,
          parseFormula: this.parseFormula,
        },
      },
    }
  },
}
</script>
