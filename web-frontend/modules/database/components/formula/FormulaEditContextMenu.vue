<template>
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
        <div class="formula-field__body">
          <div class="formula-field__items">
            <ul class="formula-field__item-group">
              <li class="formula-field__item-group-title">Fields</li>
              <li
                v-for="field in allFieldsWithoutThisField"
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
              <li class="formula-field__item-group-title">Functions</li>
              <li
                v-for="func in functions"
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
      },
      functions,
      selectedFunction: functions[0],
      selectedCategory: 'function',
      selectedField: false,
    }
  },
  computed: {
    ...mapGetters({
      fields: 'field/getAllWithPrimary',
    }),
    allFieldsWithoutThisField() {
      return this.fields.filter((f) => f.id !== this.values.id)
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
    selectFunction(func) {
      this.deselectAll()
      this.selectedFunction = func
      this.selectedCategory = 'function'
    },
    selectField(field) {
      this.deselectAll()
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
      console.log(cursorLocation)
      if (cursorLocation > 0) {
        console.log(
          getPrefixIfFuncOrFieldRef(this.values.formula, cursorLocation)
        )
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
