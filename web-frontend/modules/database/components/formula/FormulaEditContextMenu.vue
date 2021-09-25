<template>
  <div>
    <div>
      <div class="control">
        <div class="control__elements">
          <input
            ref="formulaInput"
            :value="values.formula"
            type="text"
            class="input"
            placeholder="Formula"
            @click="
              $refs.editContext.toggle(
                $refs.formulaInput,
                'top',
                'left',
                -$refs.formulaInput.scrollHeight - 3,
                -1
              )
              $refs.textAreaFormulaInput.focus()
            "
          />
        </div>
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
    <Context ref="editContext">
      <div class="formula-field">
        <div class="formula-field__input">
          <AutoResizingTextarea
            ref="textAreaFormulaInput"
            v-model="values.formula"
            class="formula-field__input-formula"
            @input="$v.values.formula.$touch()"
            @click="recalcAutoComplete"
            @keyup="recalcAutoComplete"
            @tab="doAutoComplete"
            @blur="$v.values.formula.$touch()"
          ></AutoResizingTextarea>
        </div>
        <div
          v-if="
            ($v.values.formula.$dirty && $v.values.formula.$error) ||
            values.error
          "
          class="formula-field__input-error"
        >
          <template v-if="values.error">
            {{ values.error }}
          </template>
          <template v-else-if="!$v.values.formula.required">
            Please enter a formula, press tab to autocomplete the selected field
            or function!
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
        <div class="formula-field__body">
          <div class="formula-field__items">
            <ul class="formula-field__item-group">
              <li class="formula-field__item-group-title">
                Fields
                {{
                  someFieldsFiltered ? `(${numFieldsFiltered} filtered)` : ''
                }}
              </li>
              <li
                v-for="field in filteredFields"
                :key="field.id"
                class="formula-field__item"
                :class="{
                  'formula-field__item-selected': fieldIsSelected(field),
                }"
              >
                <a
                  href="#"
                  class="formula-field__item-link"
                  @click="selectField(field)"
                >
                  <i
                    class="fas formula-field__item-icon"
                    :class="[getFieldIcon(field)]"
                  />
                  {{ field.name }}
                </a>
              </li>
            </ul>
            <ul class="formula-field__item-group">
              <li class="formula-field__item-group-title">
                Functions
                {{
                  someFunctionsFiltered
                    ? `(${numFunctionsFiltered} filtered)`
                    : ''
                }}
              </li>
              <li
                v-for="func in filteredFunctions"
                :key="func.getType()"
                class="formula-field__item"
                :class="{
                  'formula-field__item-selected': functionIsSelected(func),
                }"
              >
                <a
                  href="#"
                  class="formula-field__item-link"
                  @click="selectFunction(func)"
                >
                  <i
                    class="fas formula-field__item-icon"
                    :class="[funcTypeToIconClass(func)]"
                  />
                  {{ func.getType() }}
                </a>
              </li>
            </ul>
          </div>
          <div class="formula-field__description">
            <div class="formula-field__description-heading-1">
              <i
                class="fas formula-field__description-icon"
                :class="[descriptionIcon]"
              />
              {{ descriptionHeading }}
            </div>
            <div class="formula-field__description-text">
              {{ descriptionText }}
            </div>
            <div class="formula-field__description-heading-2">Syntax</div>
            <pre
              class="formula-field__description-example"
            ><code>{{ syntaxUsage }}</code></pre>
            <div class="formula-field__description-heading-2">Examples</div>
            <pre
              class="formula-field__description-example"
            ><code>{{ examples }}</code></pre>
          </div>
        </div>
      </div>
    </Context>
  </div>
</template>

<script>
import context from '@baserow/modules/core/mixins/context'
import AutoResizingTextarea from '@baserow/modules/core/components/helpers/AutoResizingTextarea'
import form from '@baserow/modules/core/mixins/form'
import { required } from 'vuelidate/lib/validators'
import parseBaserowFormula, {
  getPrefixIfFuncOrFieldRef,
  replaceFieldByIdWithFieldRef,
  updateFieldNames,
} from '@baserow/modules/database/formula/parser/parser'
import { mapGetters } from 'vuex'
import FieldFormulaNumberSubForm from '@baserow/modules/database/components/field/FieldFormulaNumberSubForm'
import FieldDateSubForm from '@baserow/modules/database/components/field/FieldDateSubForm'

export default {
  name: 'FormulaEditContextMenu',
  components: {
    AutoResizingTextarea,
    FieldDateSubForm,
    FieldFormulaNumberSubForm,
  },
  mixins: [context, form],
  props: {
    table: {
      type: Object,
      required: true,
    },
  },
  data() {
    const functions = Object.values(this.$registry.getAll('formula_function'))
    return {
      allowedValues: ['formula', 'formula_type', 'error', 'id'],
      values: {
        formula: '',
        formula_type: '',
        error: '',
        id: false,
      },
      functions,
      selectedFunction: functions[0],
      selectedCategory: 'function',
      selectedField: false,
      functionFilter: false,
      fieldFilter: false,
    }
  },
  computed: {
    ...mapGetters({
      fields: 'field/getAllWithPrimary',
    }),

    allFieldsWithoutThisField() {
      return this.fields.filter((f) => {
        return f.id !== this.values.id
      })
    },
    filteredFields() {
      if (
        this.functionFilter !== false &&
        !'field'.startsWith(this.functionFilter)
      ) {
        return []
      } else {
        return this.allFieldsWithoutThisField.filter((f) => {
          return (
            !this.fieldFilter ||
            f.name.toLowerCase().startsWith(this.fieldFilter.toLowerCase())
          )
        })
      }
    },
    numFieldsFiltered() {
      return this.allFieldsWithoutThisField.length - this.filteredFields.length
    },
    someFieldsFiltered() {
      return this.numFieldsFiltered > 0
    },
    filteredFunctions() {
      if (this.fieldFilter !== false) {
        return []
      } else {
        return this.functions.filter(
          (f) =>
            !this.functionFilter ||
            f
              .getType()
              .toLowerCase()
              .startsWith(this.functionFilter.toLowerCase())
        )
      }
    },
    numFunctionsFiltered() {
      return this.functions.length - this.filteredFunctions.length
    },
    someFunctionsFiltered() {
      return this.numFunctionsFiltered > 0
    },
    fieldIdToNameMap() {
      return this.fields.reduce(function (map, obj) {
        map[obj.id] = obj.name
        return map
      }, {})
    },
    descriptionHeading() {
      switch (this.selectedCategory) {
        case 'function':
          return this.selectedFunction.getType()
        case 'field':
          return this.selectedField.name
        default:
          return ''
      }
    },
    descriptionText() {
      switch (this.selectedCategory) {
        case 'function':
          return this.selectedFunction.getDescription()
        case 'field':
          return `A ${this.selectedField.type} field`
        default:
          return ''
      }
    },
    descriptionIcon() {
      switch (this.selectedCategory) {
        case 'function':
          return this.funcTypeToIconClass(this.selectedFunction)
        case 'field':
          return this.getFieldIcon(this.selectedField)
        default:
          return ''
      }
    },
    syntaxUsage() {
      let result = ''
      switch (this.selectedCategory) {
        case 'function':
          result = this.selectedFunction.getSyntaxUsage()
          break
        case 'field':
          result = `field('${this.selectedField.name}')`
          break
      }
      return this.wrapInListIfNotAlready(result).join('\n')
    },
    examples() {
      let result = ''
      switch (this.selectedCategory) {
        case 'function':
          result = this.selectedFunction.getExamples()
          break
        case 'field':
          result = `concat(field('${this.selectedField.name}'), ' extra text ')`
          break
      }
      return this.wrapInListIfNotAlready(result).join('\n')
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
    getFieldIcon(field) {
      const fieldType = this.$registry.get('field', field.type)
      return `fa-${fieldType.getIconClass()}`
    },
    funcTypeToIconClass(func) {
      const formulaType = func.getFormulaType()
      return {
        text: 'fa-font',
        char: 'fa-font',
        number: 'fa-hashtag',
        boolean: 'fa-check-square',
        date: 'fa-calendar-alt',
        special: 'fa-square-root-alt',
      }[formulaType]
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
    wrapInListIfNotAlready(item) {
      if (Array.isArray(item)) {
        return item
      } else {
        return [item]
      }
    },
    deselectAll() {
      this.selectedFunction = false
      this.selectedField = false
    },
    resetFilters() {
      this.fieldFilter = false
      this.functionFilter = false
    },
    selectFunction(func, resetFilters = true) {
      this.deselectAll()
      if (resetFilters) {
        this.resetFilters()
      }
      this.selectedFunction = func
      this.selectedCategory = 'function'
    },
    selectField(field, resetFilters = true) {
      this.deselectAll()
      if (resetFilters) {
        this.resetFilters()
      }
      this.selectedField = field
      this.selectedCategory = 'field'
    },
    functionIsSelected(func) {
      return (
        this.selectedCategory === 'function' &&
        this.selectedFunction.getType() === func.getType()
      )
    },
    fieldIsSelected(field) {
      return (
        this.selectedCategory === 'field' && this.selectedField.id === field.id
      )
    },
    recalcAutoComplete() {
      const cursorLocation =
        this.$refs.textAreaFormulaInput.$refs.textarea.selectionStart
      if (cursorLocation >= 0) {
        const { type, tokenTextUptoCursor } = getPrefixIfFuncOrFieldRef(
          this.values.formula,
          cursorLocation
        )
        console.log('type', type, 'token', tokenTextUptoCursor)
        this.resetFilters()
        if (type === 'field_inner_partial') {
          // Get rid of any quote in the front
          const withoutFrontQuote = tokenTextUptoCursor.slice(1)
          if (
            withoutFrontQuote.endsWith("'") ||
            withoutFrontQuote.endsWith('"')
          ) {
            this.fieldFilter = withoutFrontQuote.slice(
              0,
              withoutFrontQuote.length - 1
            )
          } else {
            this.fieldFilter = withoutFrontQuote
          }
          if (this.filteredFields.length > 0) {
            this.selectField(this.filteredFields[0], false)
          }
        } else if (type === 'identifier') {
          this.functionFilter = tokenTextUptoCursor
          if (this.filteredFunctions.length > 0) {
            this.selectFunction(this.filteredFunctions[0], false)
          }
        }
      }
    },
    doAutoComplete() {
      const startingCursorLocation =
        this.$refs.textAreaFormulaInput.$refs.textarea.selectionStart
      if (startingCursorLocation >= 0) {
        const {
          type,
          tokenTextUptoCursor,
          cursorAtEndOfToken,
          closingParenIsNextNormalToken,
          cursorLocation,
        } = getPrefixIfFuncOrFieldRef(
          this.values.formula,
          startingCursorLocation
        )
        let chosen = false
        let quoteIt = false
        let optionalClosingParen = ''
        let resultingCursorOffset = 0
        if (type === 'field_inner_partial') {
          if (!cursorAtEndOfToken) {
            return
          }
          if (this.filteredFields.length > 0) {
            quoteIt = true
            chosen = this.filteredFields[0].name
            optionalClosingParen = closingParenIsNextNormalToken ? ')' : ''
            resultingCursorOffset = 1
          }
        } else if (type === 'identifier') {
          if (this.filteredFunctions.length > 0) {
            const funcType = this.filteredFunctions[0].getType()
            const startingArg = funcType === 'field' ? "''" : ''
            if (funcType === 'field') {
              resultingCursorOffset = -1
            }
            chosen = funcType + '(' + startingArg
            if (cursorAtEndOfToken) {
              optionalClosingParen = ')'
            }
          }
        }
        if (chosen) {
          const startWithoutToken = this.values.formula.slice(
            0,
            cursorLocation - tokenTextUptoCursor.length
          )
          const afterToken = this.values.formula.slice(cursorLocation)
          const doubleQuote = tokenTextUptoCursor.startsWith('"')
          let replacement
          if (quoteIt) {
            replacement = doubleQuote
              ? `"${chosen.replace('"', '\\"')}"`
              : `'${chosen.replace("'", "\\'")}'`
          } else {
            replacement = chosen
          }

          this.values.formula =
            startWithoutToken + replacement + optionalClosingParen + afterToken
          const beforeClosingBracketPos =
            startWithoutToken.length +
            replacement.length +
            resultingCursorOffset
          this.$nextTick(() => {
            this.$refs.textAreaFormulaInput.$refs.textarea.setSelectionRange(
              beforeClosingBracketPos,
              beforeClosingBracketPos
            )
            this.recalcAutoComplete()
          })
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
