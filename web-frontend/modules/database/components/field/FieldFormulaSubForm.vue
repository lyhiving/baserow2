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
          <template v-else-if="!$v.values.formula.check">
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
import antlr4 from 'antlr4'
import { BaserowFormulaLexer } from '@baserow/modules/database/formula/parser/generated/BaserowFormulaLexer'
import { BaserowFormula } from '@baserow/modules/database/formula/parser/generated/BaserowFormula'
import { mapGetters } from 'vuex'
import BaserowFormulaParserError from '@/modules/database/formula/parser/errors'

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
    check(value) {
      if (!value.trim()) {
        return false
      }
      try {
        const chars = new antlr4.InputStream(value)
        const lexer = new BaserowFormulaLexer(chars)
        const tokens = new antlr4.CommonTokenStream(lexer)
        const parser = new BaserowFormula(tokens)
        parser.removeErrorListeners()
        parser.addErrorListener({
          syntaxError: (
            recognizer,
            offendingSymbol,
            line,
            column,
            msg,
            err
          ) => {
            throw new BaserowFormulaParserError(
              offendingSymbol,
              line,
              column,
              msg
            )
          },
        })
        parser.buildParseTrees = true
        parser.root()
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
          check: this.check,
        },
      },
    }
  },
}
</script>
