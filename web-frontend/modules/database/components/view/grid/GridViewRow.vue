<template>
  <div
    class="grid-view-row"
    :class="{ 'grid-view-row-loading': row._.loading }"
  >
    <GridViewField
      v-for="field in fields"
      :key="field.id"
      :field="field"
      :row="row"
      :table="table"
    ></GridViewField>
  </div>
</template>

<script>
import GridViewField from '@baserow/modules/database/components/view/grid/GridViewField'

export default {
  name: 'GridViewRow',
  components: { GridViewField },
  props: {
    table: {
      type: Object,
      required: true
    },
    fields: {
      type: Array,
      required: true
    },
    row: {
      type: Object,
      required: true
    }
  }
}
</script>
