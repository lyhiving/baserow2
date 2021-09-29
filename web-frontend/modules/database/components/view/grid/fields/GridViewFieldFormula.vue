<template>
  <div
    v-if="field.formula_type === 'number' && value === 'NaN'"
    class="grid-view__cell cell-error"
  >
    <div class="grid-field-number">Invalid Number</div>
  </div>
  <div v-else-if="field.error" ref="cell" class="grid-view__cell active"></div>
  <component
    :is="getComponent(field)"
    v-else-if="getComponent(field)"
    v-bind="$props"
  ></component>
  <div
    v-else-if="field.formula_type === 'invalid'"
    class="grid-view__cell"
  ></div>
  <div v-else ref="cell" class="grid-view__cell active">Unknown field type</div>
</template>

<script>
import FunctionalGridViewFieldDate from '@baserow/modules/database/components/view/grid/fields/FunctionalGridViewFieldDate'
import FunctionalGridViewFieldBoolean from '@baserow/modules/database/components/view/grid/fields/FunctionalGridViewFieldBoolean'
import FunctionalGridViewFieldNumber from '@baserow/modules/database/components/view/grid/fields/FunctionalGridViewFieldNumber'
import FunctionalGridViewFieldText from '@baserow/modules/database/components/view/grid/fields/FunctionalGridViewFieldText'
import gridField from '@baserow/modules/database/mixins/gridField'

export default {
  name: 'GridViewFormulaField',
  mixins: [gridField],
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
