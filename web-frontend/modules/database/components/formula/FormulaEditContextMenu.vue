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
import FormulaFieldItemGroup from '@baserow/modules/database/components/formula/FormulaFieldItemGroup'
import FormulaFieldItemDescription from '@baserow/modules/database/components/formula/FormulaFieldItemDescription'

export default {
  name: 'FormulaEditContextMenu',
  components: {
    FormulaFieldItemDescription,
    FormulaFieldItemGroup,
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
    const functions = Object.values(
      this.$registry.getAll('formula_function')
    ).map((f) =>
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
    return {
      allowedValues: ['formula', 'formula_type', 'error', 'id'],
      values: {
        formula: '',
        formula_type: '',
        error: '',
        id: false,
      },
      functions,
      selectedItem: functions[0],
      filteredFunctions: functions,
      filteredFields: [],
    }
  },
  computed: {
    ...mapGetters({
      rawFields: 'field/getAllWithPrimary',
    }),
    fields() {
      return this.rawFields
        .filter((f) => {
          return f.id !== this.values.id
        })
        .map((f) =>
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
    fieldIdToNameMap() {
      return this.rawFields.reduce(function (map, obj) {
        map[obj.id] = obj.name
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
    resetFilters() {
      this.filteredFunctions = this.functions
      this.filteredFields = this.fields
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
          this.values.formula,
          cursorLocation,
          this.fields,
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
