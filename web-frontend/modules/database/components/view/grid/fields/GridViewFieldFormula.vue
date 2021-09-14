<template>
  <div
    v-if="field.field_type === 'numeric' && value === 'NaN'"
    ref="cell"
    v-tooltip="'Divide by zero error'"
    class="grid-view__cell active cell-error"
  ></div>
  <div v-else-if="field.error" ref="cell" class="grid-view__cell active"></div>
  <component
    :is="getComponent(field)"
    v-else-if="getComponent(field)"
    v-bind="$props"
  ></component>
  <div v-else ref="cell" class="grid-view__cell active">Unknown field type</div>
</template>

<script>
import gridField from '@baserow/modules/database/mixins/gridField'
import GridViewFieldDate from '@baserow/modules/database/components/view/grid/fields/GridViewFieldDate'
import GridViewFieldNumber from '@baserow/modules/database/components/view/grid/fields/GridViewFieldNumber'
import GridViewFieldBoolean from '@baserow/modules/database/components/view/grid/fields/GridViewFieldBoolean'
import GridViewFieldText from '@baserow/modules/database/components/view/grid/fields/GridViewFieldText'

export default {
  name: 'GridViewFormulaField',
  mixins: [gridField],
  methods: {
    getComponent(field) {
      return {
        DateField: GridViewFieldDate,
        TextField: GridViewFieldText,
        BooleanField: GridViewFieldBoolean,
        NumberField: GridViewFieldNumber,
      }[field.field_type]
    },
  },
}
</script>
