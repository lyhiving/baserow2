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
            @click="openContext"
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
                {{ getFilterIndicator(fields, filteredFields) }}
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
                  getFilterIndicator(
                    unfilteredNormalFunctions,
                    filteredNormalFunctions
                  )
                }}
              </li>
              <li
                v-for="func in filteredNormalFunctions"
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
            <ul class="formula-field__item-group">
              <li class="formula-field__item-group-title">
                Operators
                {{ getFilterIndicator(unfilteredOperators, filteredOperators) }}
              </li>
              <li
                v-for="func in filteredOperators"
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
                  {{ func.getOperator() }}
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
              {{ makeHeader(descriptionHeading) }}
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
import parseBaserowFormula from '@baserow/modules/database/formula/parser/parser'
import { mapGetters } from 'vuex'
import FieldFormulaNumberSubForm from '@baserow/modules/database/components/field/FieldFormulaNumberSubForm'
import FieldDateSubForm from '@baserow/modules/database/components/field/FieldDateSubForm'
import { updateFieldNames } from '@baserow/modules/database/formula/parser/updateFieldNames'
import { replaceFieldByIdWithField } from '@baserow/modules/database/formula/parser/replaceFieldByIdWithField'
import {
  autocompleteFormula,
  calculateFilteredFunctionsAndFieldsBasedOnCursorLocation,
} from '@baserow/modules/database/formula/autocompleter/formulaAutocompleter'

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
      filteredFunctions: functions,
      filteredFields: [],
    }
  },
  computed: {
    ...mapGetters({
      rawFields: 'field/getAllWithPrimary',
    }),
    fields() {
      return this.rawFields.filter((f) => {
        return f.id !== this.values.id
      })
    },
    unfilteredNormalFunctions() {
      return this.functions.filter((f) => !f.isOperator())
    },
    unfilteredOperators() {
      return this.functions.filter((f) => f.isOperator())
    },
    filteredNormalFunctions() {
      return this.filteredFunctions.filter((f) => !f.isOperator())
    },
    filteredOperators() {
      return this.filteredFunctions.filter((f) => f.isOperator())
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
  mounted() {
    this.recalcAutoComplete()
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
        this.convertServerSideFormulaToClient(value)
        return true
      } catch (e) {
        this.error = e
        return false
      }
    },
    convertServerSideFormulaToClient(formula) {
      this.values.formula = replaceFieldByIdWithField(
        formula,
        this.fieldIdToNameMap
      )
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
      this.filteredFunctions = this.functions
      this.filteredFields = this.fields
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

      const { filteredFields, filteredFunctions, filtered } =
        calculateFilteredFunctionsAndFieldsBasedOnCursorLocation(
          this.values.formula,
          cursorLocation,
          this.fields,
          this.functions
        )
      this.filteredFunctions = filteredFunctions
      this.filteredFields = filteredFields
      if (filtered) {
        if (this.filteredFunctions.length > 0) {
          this.selectFunction(filteredFunctions[0], false)
        } else if (this.filteredFields.length > 0) {
          this.selectField(filteredFields[0], false)
        }
      }
    },
    doAutoComplete() {
      const startingCursorLocation =
        this.$refs.textAreaFormulaInput.$refs.textarea.selectionStart
      const { autocompletedFormula, newCursorPosition } = autocompleteFormula(
        this.values.formula,
        startingCursorLocation,
        this.filteredFunctions,
        this.filteredFields
      )
      this.values.formula = autocompletedFormula
      this.$nextTick(() => {
        this.$refs.textAreaFormulaInput.$refs.textarea.setSelectionRange(
          newCursorPosition,
          newCursorPosition
        )
        this.recalcAutoComplete()
      })
    },
    openContext() {
      this.$refs.editContext.toggle(
        this.$refs.formulaInput,
        'top',
        'left',
        -this.$refs.formulaInput.scrollHeight - 3,
        -1
      )
      this.$nextTick(() => {
        this.$refs.textAreaFormulaInput.$refs.textarea.focus()
      })
    },
    makeHeader(header) {
      return header.replaceAll('_', ' ')
    },
    getFilterIndicator(unfilteredList, filteredList) {
      const numFiltered = unfilteredList.length - filteredList.length
      return numFiltered === 0 ? '' : `(${numFiltered} filtered)`
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
