<template>
  <div ref="cell" class="grid-view__cell active">
    <div class="grid-field grid-field-text">{{ value }}</div>
  </div>
</template>

<script>
import gridField from '@baserow/modules/database/mixins/gridField'

export default {
  name: 'GridViewFormulaField',
  mixins: [gridField],
}
</script>
