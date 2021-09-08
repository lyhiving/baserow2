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
          <template v-if="!$v.values.formula.required">
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
          <template v-else-if="values.error">
            {{ values.error }}
          </template>
        </div>
        <div v-if="!values.error">
          <FieldNumberSubForm
            v-if="values.field_type === 'numeric'"
            :default-values="defaultValues"
            :table="table"
          >
          </FieldNumberSubForm>
          <FieldTextSubForm
            v-else-if="values.field_type === 'text'"
            :default-values="defaultValues"
            :table="table"
          >
          </FieldTextSubForm>
          <FieldDateSubForm
            v-else-if="values.field_type === 'datetime'"
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
  replaceFieldWithFieldById,
} from '@/modules/database/formula/parser/parser'
import FieldNumberSubForm from '@/modules/database/components/field/FieldNumberSubForm'
import FieldTextSubForm from '@/modules/database/components/field/FieldTextSubForm'
import FieldDateSubForm from '@/modules/database/components/field/FieldDateSubForm'

export default {
  name: 'FieldFormulaSubForm',
  components: { FieldDateSubForm, FieldTextSubForm, FieldNumberSubForm },
  mixins: [form, fieldSubForm],
  props: {
    table: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      allowedValues: ['formula', 'error', 'field_type'],
      values: {
        formula: '',
      },
      internalFormulaValue: '',
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
    fieldIdToNameMap(newMap) {
      // A field name has changed so the current this.values.formula might now have
      // an invalid field('old name') reference. Instead lets re-update it from our
      // internal format where all references are in the form field_by_id(..)
      try {
        this.updateFormulaData(this.internalFormulaValue)
        this.error = ''
      } catch (e) {
        this.error = e
      }
    },
    'default-values'(newValue, oldValue) {
      if (!this.error) {
        try {
          this.updateFormulaData(newValue.formula)
          this.error = ''
        } catch (e) {
          this.error = e
        }
      }
    },
    'values.formula'(newValue, oldValue) {
      if (!this.error) {
        try {
          this.updateFormulaData(newValue)
          this.error = ''
        } catch (e) {
          this.error = e
        }
      }
    },
  },
  methods: {
    updateFormulaData(formula) {
      const result = replaceFieldWithFieldById(formula, this.fieldNameToIdMap)
      if (result !== false) {
        const { newFormula, errors } = result
        this.internalFormulaValue = newFormula
        this.values.formula = replaceFieldByIdWithFieldRef(
          this.internalFormulaValue,
          this.fieldIdToNameMap
        )
        if (errors.length > 0) {
          throw new Error(errors.join(', '))
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
        this.updateFormulaData(value)
        this.error = ''
        return true
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
