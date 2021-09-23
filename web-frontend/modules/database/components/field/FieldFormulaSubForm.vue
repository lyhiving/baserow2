<template>
  <div>
    <div class="control">
      <div class="control__elements">
        <input
          ref="formula"
          v-model="values.formula"
          type="text"
          class="input"
          placeholder="Formula"
          @input="$v.values.formula.$touch()"
          @blur="$v.values.formula.$touch()"
        />
        <div
          v-if="
            ($v.values.formula.$dirty && $v.values.formula.$error) ||
            values.error
          "
          class="error formula-error"
        >
          <template v-if="values.error">
            {{ values.error }}
          </template>
          <template v-else-if="!$v.values.formula.required">
            This field is required.
          </template>
          <template v-else-if="!$v.values.formula.parseFormula">
            <strong
              >Error in the formula on line {{ error.line }} starting at letter
              {{ error.character }}</strong
            >
            <br />
            {{ toHumanReadableErrorMessage(error) }}
          </template>
        </div>
        <div v-if="!values.error">
          <FieldFormulaNumberSubForm
            v-if="values.formula_type === 'number'"
            :default-values="defaultValues"
            :table="table"
          >
          </FieldFormulaNumberSubForm>
          <FieldDateSubForm
            v-else-if="values.formula_type === 'date'"
            :default-values="defaultValues"
            :table="table"
          >
          </FieldDateSubForm>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import form from '@baserow/modules/core/mixins/form'

import fieldSubForm from '@baserow/modules/database/mixins/fieldSubForm'
import { required } from 'vuelidate/lib/validators'
import { mapGetters } from 'vuex'
import parseBaserowFormula, {
  replaceFieldByIdWithFieldRef,
  updateFieldNames,
} from '@baserow/modules/database/formula/parser/parser'
import FieldFormulaNumberSubForm from '@baserow/modules/database/components/field/FieldFormulaNumberSubForm'
import FieldDateSubForm from '@baserow/modules/database/components/field/FieldDateSubForm'

export default {
  name: 'FieldFormulaSubForm',
  components: { FieldDateSubForm, FieldFormulaNumberSubForm },
  mixins: [form, fieldSubForm],
  props: {
    table: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      allowedValues: ['formula', 'error', 'formula_type'],
      values: {
        formula: '',
      },
      error: '',
    }
  },
  computed: {
    ...mapGetters({
      fields: 'field/getAllWithPrimary',
    }),
    fieldIdToNameMap() {
      return this.fields.reduce(function (map, obj) {
        map[obj.id] = obj.name
        return map
      }, {})
    },
    fieldNameToIdMap() {
      return this.fields.reduce(function (map, obj) {
        map[obj.name] = obj.id
        return map
      }, {})
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
    },
    'values.formula'(newValue, oldValue) {
      this.convertServerSideFormulaToClient(newValue)
    },
  },
  methods: {
    convertServerSideFormulaToClient(formula) {
      const result = replaceFieldByIdWithFieldRef(
        formula,
        this.fieldIdToNameMap
      )
      if (result !== false) {
        const { newFormula, errors } = result
        this.values.formula = newFormula
        if (errors.length > 0) {
          this.error = errors.join(', ')
        } else {
          return true
        }
      }
      return false
    },
    fieldNameChanged(oldNameToNewNameMap) {
      const formula = this.values.formula
      if (this.convertServerSideFormulaToClient(formula)) {
        const result = updateFieldNames(
          this.values.formula,
          oldNameToNewNameMap
        )
        if (result !== false) {
          const { newFormula, errors } = result
          this.values.formula = newFormula
          if (errors.length > 0) {
            this.error = errors.join(', ')
          }
        }
      }
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
    parseFormula(value) {
      if (!value.trim()) {
        return false
      }
      try {
        parseBaserowFormula(value)
        return this.convertServerSideFormulaToClient(value)
      } catch (e) {
        this.error = e
        return false
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
