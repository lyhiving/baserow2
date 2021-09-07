<template>
  <div
    ref="cell"
    :class="{
      'cell-error': field.field_type === 'numeric' && value === 'NaN',
    }"
    class="grid-view__cell active"
  >
    <div class="grid-field grid-field-text">{{ field.error ? '' : value }}</div>
  </div>
</template>

<script>
import gridField from '@baserow/modules/database/mixins/gridField'

export default {
  name: 'GridViewFormulaField',
  mixins: [gridField],
}
</script>
