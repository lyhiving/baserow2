<template>
  <div ref="cell" class="grid-view__cell active">
    {{ value }}
  </div>
</template>

<script>
import gridField from '@baserow/modules/database/mixins/gridField'

export default {
  name: 'GridViewFormulaField',
  mixins: [gridField],
}
</script>
