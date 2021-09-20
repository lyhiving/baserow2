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
          v-if="$v.values.formula.$dirty && $v.values.formula.$error"
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
import parseBaserowFormula from '@baserow/modules/database/formula/parser/parser'

export default {
  name: 'FieldFormulaSubForm',
  mixins: [form, fieldSubForm],
  props: {
    table: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      allowedValues: ['formula'],
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
  },
  methods: {
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
