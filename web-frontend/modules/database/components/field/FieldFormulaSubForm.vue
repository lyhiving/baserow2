<template>
  <div>
    <div class="control">
      <div class="control__elements">
        <div v-if="$v.values.formula.$error" class="error">
          This field is required and must be valid.
        </div>
        <input
          ref="formula"
          v-model="values.formula"
          type="text"
          class="input"
          placeholder="Formula"
          @input="$v.values.formula.$touch()"
          @blur="$v.values.formula.$touch()"
        />
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
    }
  },
  computed: {
    ...mapGetters({
      fields: 'field/getAllWithPrimary',
    }),
  },
  validations: {
    values: {
      formula: {
        required,
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
                const message = `${offendingSymbol} line ${line}, col ${column}: ${msg}`
                console.error(message)
                throw new Error(message)
              },
            })
            parser.buildParseTrees = true
            return true
          } catch (e) {
            return false
          }
        },
      },
    },
  },
}
</script>
