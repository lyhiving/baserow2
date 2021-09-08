<template>
  <div
    ref="cell"
    v-tooltip="
      field.field_type === 'numeric' && value === 'NaN'
        ? 'Divide by zero error'
        : false
    "
    :class="{
      'cell-error': field.field_type === 'numeric' && value === 'NaN',
    }"
    class="grid-view__cell active"
  >
    <div class="grid-field grid-field-text-selectable">
      {{ field.error ? '' : value }}
    </div>
  </div>
</template>

<script>
import gridField from '@baserow/modules/database/mixins/gridField'

export default {
  name: 'GridViewFormulaField',
  mixins: [gridField],
}
</script>
