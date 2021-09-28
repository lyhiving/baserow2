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
        />
      </div>
    </div>
    <div v-if="error" class="error grid-field-formula__error">{{ error }}</div>
    <FieldFormulaNumberSubForm
      v-else-if="defaultValues.formula_type === 'number'"
      :default-values="defaultValues"
      :table="table"
    >
    </FieldFormulaNumberSubForm>
    <FieldDateSubForm
      v-else-if="defaultValues.formula_type === 'date'"
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
    error: {
      type: String,
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
}
</script>
