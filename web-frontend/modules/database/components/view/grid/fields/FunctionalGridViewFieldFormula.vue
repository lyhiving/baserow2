<template functional>
  <div
    v-if="props.field.field_type === 'NumberField' && props.value === 'NaN'"
    v-tooltip="'Divide by zero error'"
    class="grid-view__cell cell-error"
  ></div>
  <component
    :is="$options.methods.getComponent(props.field)"
    v-else-if="$options.methods.getComponent(props.field)"
    v-bind="props"
  ></component>
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
  props: {
    field: {
      type: Object,
      required: true,
    },
  },
  methods: {
    getComponent(field) {
      return {
        DateField: FunctionalGridViewFieldDate,
        TextField: FunctionalGridViewFieldText,
        BooleanField: FunctionalGridViewFieldBoolean,
        NumberField: FunctionalGridViewFieldNumber,
      }[field.field_type]
    },
  },
}
</script>
