<template>
  <div>
    <div class="control">
      <div class="control__elements">
        <input
          ref="formulaInput"
          :value="formula"
          type="text"
          class="input input--monospace"
          @click.="$emit('open-advanced-context', $refs.formulaInput)"
          @input.stop="$emit('open-advanced-context', $refs.formulaInput)"
          @focus.stop="$emit('open-advanced-context', $refs.formulaInput)"
        />
      </div>
    </div>
    <div
      v-if="loading || formulaTypeRefreshNeeded || error"
      class="formula-field__type-refresher"
    >
      <div v-if="loading" class="loading"></div>
      <template v-else>
        <div v-if="error" class="error formula-field__error">
          {{ error }}
        </div>
        <a
          v-if="formulaTypeRefreshNeeded"
          href="#"
          class="formula-field__refresh"
          @click.stop="$emit('refresh-formula-type')"
        >
          <i class="fas fa-sync-alt"></i>
          Refresh formula options
        </a>
      </template>
    </div>
    <template v-else>
      <FieldFormulaNumberSubForm
        v-if="formulaType === 'number'"
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
    </template>
  </div>
</template>
<script>
import form from '@baserow/modules/core/mixins/form'

import fieldSubForm from '@baserow/modules/database/mixins/fieldSubForm'
import FieldFormulaNumberSubForm from '@baserow/modules/database/components/field/FieldFormulaNumberSubForm'
import FieldDateSubForm from '@baserow/modules/database/components/field/FieldDateSubForm'

export default {
  name: 'FieldFormulaInitialSubForm',
  components: {
    FieldDateSubForm,
    FieldFormulaNumberSubForm,
  },
  mixins: [form, fieldSubForm],
  props: {
    loading: {
      type: Boolean,
      required: true,
    },
    formula: {
      type: String,
      required: true,
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
    formulaTypeRefreshNeeded: {
      type: Boolean,
      required: true,
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
