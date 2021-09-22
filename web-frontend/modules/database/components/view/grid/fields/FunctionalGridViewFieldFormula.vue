<template functional>
  <div
    v-if="props.field.formula_type === 'number' && props.value === 'NaN'"
    v-tooltip="'Invalid number'"
    class="grid-view__cell cell-error"
  ></div>
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
import FunctionalGridViewFieldDate from '@baserow/modules/database/components/view/grid/fields/FunctionalGridViewFieldDate'
import FunctionalGridViewFieldText from '@baserow/modules/database/components/view/grid/fields/FunctionalGridViewFieldText'
import FunctionalGridViewFieldBoolean from '@baserow/modules/database/components/view/grid/fields/FunctionalGridViewFieldBoolean'
import FunctionalGridViewFieldNumber from '@baserow/modules/database/components/view/grid/fields/FunctionalGridViewFieldNumber'

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
