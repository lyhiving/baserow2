<template>
  <div class="control__elements">
    <div>
      {{ value }}
    </div>
  </div>
</template>

<script>
import rowEditField from '@baserow/modules/database/mixins/rowEditField'

export default {
  name: 'RowEditFieldFormula',
  mixins: [rowEditField],
}
</script>
