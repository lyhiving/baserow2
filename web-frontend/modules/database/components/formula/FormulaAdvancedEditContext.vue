<template>
  <Context ref="editContext">
    <div class="formula-field">
      <div class="formula-field__input">
        <AutoResizingTextarea
          ref="textAreaFormulaInput"
          v-model="formula"
          class="formula-field__input-formula"
          @click="recalcAutoComplete"
          @keyup="recalcAutoComplete"
          @tab="doAutoComplete"
        ></AutoResizingTextarea>
      </div>
      <div v-if="error" class="formula-field__input-error">{{ error }}</div>
      <div class="formula-field__body">
        <div class="formula-field__items">
          <FormulaFieldItemGroup
            :filtered-items="filteredFields"
            :unfiltered-items="fields"
            title="Fields"
            @select-item="selectItem"
          >
          </FormulaFieldItemGroup>
          <FormulaFieldItemGroup
            :filtered-items="filteredNormalFunctions"
            :unfiltered-items="unfilteredNormalFunctions"
            title="Functions"
            @select-item="selectItem"
          >
          </FormulaFieldItemGroup>
          <FormulaFieldItemGroup
            :filtered-items="filteredOperators"
            :unfiltered-items="unfilteredOperators"
            title="Operators"
            @select-item="selectItem"
          >
          </FormulaFieldItemGroup>
        </div>
        <FormulaFieldItemDescription :selected-item="selectedItem">
        </FormulaFieldItemDescription>
      </div>
    </div>
  </Context>
</template>

<script>
import context from '@baserow/modules/core/mixins/context'
import AutoResizingTextarea from '@baserow/modules/core/components/helpers/AutoResizingTextarea'
import {
  autocompleteFormula,
  calculateFilteredFunctionsAndFieldsBasedOnCursorLocation,
} from '@baserow/modules/database/formula/autocompleter/formulaAutocompleter'
import FormulaFieldItemGroup from '@baserow/modules/database/components/formula/FormulaFieldItemGroup'
import FormulaFieldItemDescription from '@baserow/modules/database/components/formula/FormulaFieldItemDescription'

export default {
  name: 'FormulaAdvancedEditContext',
  components: {
    FormulaFieldItemDescription,
    FormulaFieldItemGroup,
    AutoResizingTextarea,
  },
  mixins: [context],
  props: {
    table: {
      type: Object,
      required: true,
    },
    fields: {
      type: Array,
      required: true,
    },
    value: {
      type: String,
      required: true,
    },
    error: {
      type: Boolean,
      required: true,
    },
  },
  data() {
    const functions = this.getAndWrapFunctions()
    return {
      functions,
      selectedItem: functions[0],
      filteredFunctions: functions,
      filteredFields: [],
    }
  },
  computed: {
    formula: {
      get() {
        return this.value
      },
      set(value) {
        this.$emit('input', value)
      },
    },
    fieldItems() {
      return this.fields.map((f) =>
        this.wrapItem(
          f.name,
          f.id,
          this.getFieldIcon(f),
          `A ${f.type} field`,
          `concat(field('${f.name}'), ' extra text ')`,
          `field('${f.name}')`,
          f
        )
      )
    },
    unfilteredNormalFunctions() {
      return this.functions.filter((f) => !f.item.isOperator())
    },
    unfilteredOperators() {
      return this.functions.filter((f) => f.item.isOperator())
    },
    filteredNormalFunctions() {
      return this.filteredFunctions.filter((f) => !f.item.isOperator())
    },
    filteredOperators() {
      return this.filteredFunctions.filter((f) => f.item.isOperator())
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
    resetFilters() {
      this.filteredFunctions = this.functions
      this.filteredFields = this.fieldItems
    },
    selectItem(item, resetFilters = true) {
      this.selectedItem.isSelected = false
      this.selectedItem = false
      if (resetFilters) {
        this.resetFilters()
      }
      this.selectedItem = item
      item.isSelected = true
    },
    recalcAutoComplete() {
      const cursorLocation =
        this.$refs.textAreaFormulaInput.$refs.textarea.selectionStart

      const { filteredFields, filteredFunctions, filtered } =
        calculateFilteredFunctionsAndFieldsBasedOnCursorLocation(
          this.formula,
          cursorLocation,
          this.fieldItems,
          this.functions
        )

      this.filteredFunctions = filteredFunctions
      this.filteredFields = filteredFields

      if (filtered) {
        if (this.filteredFunctions.length > 0) {
          this.selectItem(filteredFunctions[0], false)
        } else if (this.filteredFields.length > 0) {
          this.selectItem(filteredFields[0], false)
        }
      }
    },
    doAutoComplete() {
      const startingCursorLocation =
        this.$refs.textAreaFormulaInput.$refs.textarea.selectionStart

      const { autocompletedFormula, newCursorPosition } = autocompleteFormula(
        this.formula,
        startingCursorLocation,
        this.filteredFunctions,
        this.filteredFields
      )
      this.formula = autocompletedFormula

      this.$nextTick(() => {
        this.$refs.textAreaFormulaInput.$refs.textarea.setSelectionRange(
          newCursorPosition,
          newCursorPosition
        )
        this.recalcAutoComplete()
      })
    },
    openContext(triggeringEl) {
      this.$refs.editContext.toggle(
        triggeringEl,
        'top',
        'left',
        -triggeringEl.scrollHeight - 3,
        -1
      )
      this.$nextTick(() => {
        this.$refs.textAreaFormulaInput.$refs.textarea.focus()
      })
    },
    wrapItem(value, key, icon, description, examples, syntaxUsage, item) {
      return {
        value,
        key,
        icon,
        isSelected: false,
        description,
        examples,
        syntaxUsage,
        item,
      }
    },
    getAndWrapFunctions() {
      return Object.values(this.$registry.getAll('formula_function')).map((f) =>
        this.wrapItem(
          f.isOperator() ? f.getOperator() : f.getType(),
          f.getType(),
          this.funcTypeToIconClass(f),
          f.getDescription(),
          f.getExamples(),
          f.getSyntaxUsage(),
          f
        )
      )
    },
  },
}
</script>
