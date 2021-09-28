<template>
  <div>
    <div class="control">
      <div class="control__elements">
        <input
          ref="formulaInput"
          :value="formula"
          type="text"
          class="input"
          placeholder="Formula"
          @click="$emit('open-advanced-context', $refs.formulaInput)"
          @input="$emit('open-advanced-context', $refs.formulaInput)"
        />
      </div>
    </div>
    <div v-if="error" class="error grid-field-formula__error">
      {{ error }}
    </div>
    <div v-if="formulaChanged && !parsingError && defaultValues.id">
      <a href="#" @click="$emit('retype-formula')">Get new formula options</a>
    </div>
    <FieldFormulaNumberSubForm
      v-else-if="formulaType === 'number'"
      :default-values="defaultValues"
      :table="table"
    >
    </FieldFormulaNumberSubForm>
    <FieldDateSubForm
      v-else-if="formulaType === 'date'"
      :default-values="defaultValues"
      :table="table"
    >
    </FieldDateSubForm>
  </div>
</template>
<script>
import FieldFormulaNumberSubForm from '@baserow/modules/database/components/field/FieldFormulaNumberSubForm'
import FieldDateSubForm from '@baserow/modules/database/components/field/FieldDateSubForm'
import form from '@baserow/modules/core/mixins/form'
import fieldSubForm from '@baserow/modules/database/mixins/fieldSubForm'

export default {
  name: 'FieldFormulaInitialSubForm',
  components: {
    FieldDateSubForm,
    FieldFormulaNumberSubForm,
  },
  mixins: [form, fieldSubForm],
  props: {
    formula: {
      type: String,
      required: true,
    },
    initialFormula: {
      type: String,
      required: false,
      default: null,
    },
    formulaType: {
      type: String,
      required: false,
      default: null,
    },
    error: {
      type: String,
      required: false,
      default: null,
    },
    parsingError: {
      type: Error,
      required: false,
      default: null,
    },
  },
  data() {
    return {
      allowedValues: [],
      values: {},
    }
  },
  computed: {
    formulaChanged() {
      return (
        this.initialFormula !== null && this.formula !== this.initialFormula
      )
    },
  },
}
</script>
