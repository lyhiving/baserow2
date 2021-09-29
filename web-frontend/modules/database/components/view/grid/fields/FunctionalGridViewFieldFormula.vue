<template functional>
  <div
    v-if="props.field.formula_type === 'number' && props.value === 'NaN'"
    class="grid-view__cell cell-error"
  >
    <div class="grid-field-number">Invalid Number</div>
  </div>
  <component
    :is="$options.methods.getComponent(props.field)"
    v-else-if="$options.methods.getComponent(props.field)"
    :field="props.field"
    :value="props.value"
  ></component>
  <div
    v-else-if="props.field.formula_type === 'invalid'"
    class="grid-view__cell"
  ></div>
  <div v-else class="grid-view__cell cell-error">Unknown Field Type</div>
</template>
<script>
import FunctionalGridViewFieldBoolean from '@baserow/modules/database/components/view/grid/fields/FunctionalGridViewFieldBoolean'
import FunctionalGridViewFieldDate from '@baserow/modules/database/components/view/grid/fields/FunctionalGridViewFieldDate'
import FunctionalGridViewFieldNumber from '@baserow/modules/database/components/view/grid/fields/FunctionalGridViewFieldNumber'
import FunctionalGridViewFieldText from '@baserow/modules/database/components/view/grid/fields/FunctionalGridViewFieldText'

export default {
  name: 'FunctionalGridViewFieldFormula',
  components: {
    FunctionalGridViewFieldDate,
    FunctionalGridViewFieldText,
    FunctionalGridViewFieldBoolean,
    FunctionalGridViewFieldNumber,
  },
  methods: {
    getComponent(field) {
      return {
        date: FunctionalGridViewFieldDate,
        text: FunctionalGridViewFieldText,
        boolean: FunctionalGridViewFieldBoolean,
        number: FunctionalGridViewFieldNumber,
      }[field.formula_type]
    },
  },
}
</script>
